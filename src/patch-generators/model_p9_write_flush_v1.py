"""Actual P9 writer/flush/error-policy instruction model with explicitly fake I/O.

Synthetic modeled seek/write outcomes are not hardware fault injection. Kernel
wrappers, formatting, warning internals and prompt answer are explicit mocks.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from model_p9_setup_failure_v1 import CPU as BaseCPU, MASK, signed
from pinned_binary import PinnedElf, ROOT


class Abort(Exception):
    pass


class CPU(BaseCPU):
    def __init__(self, elf, bases):
        super().__init__(elf, bases)
        self.regions.append((0x06000000, 0x06040000))
        self.code = {i.address: i for lo, hi in ((0x14888, 0x14aec), (0x1558c, 0x1572c))
                     for i in elf.instructions(lo, hi)}
        self.seeks, self.writes, self.messages = [], [], []
        self.seek_results, self.write_results = [], []
        self.cursor = 123456
        self.prompt_answer = 1
        self.invalid_buffer_returns_error = False
        self.g[1], self.lr = 0x70000000, 0x76543210
        self.store(self.slot(-0x7b08), 512, 4)
        self.store(self.slot(-0x7b38), 42, 4)
        self.store(self.slot(-0x7b2c), 1, 1)
        self.store(self.slot(-0x7b00), 0, 4)
        self.store(self.slot(-0x7b10), 0, 4)
        self.store(self.slot(-0x7ba4), 1, 1)

    def load(self, address, count):
        self.access(address, count)
        value = bytearray()
        for at in range(address, address + count):
            if at in self.memory:
                value.append(self.memory[at])
            else:
                original = next((h[3] + at - self.bases[index] for index, h in enumerate(self.elf.loads)
                                 if self.bases[index] <= at < self.bases[index] + h[5]), None)
                value.extend(self.elf.bytes_at(original, 1) if original is not None else b'\0')
        return int.from_bytes(value, 'big')

    def external(self, address):
        if address == 0xf7e8:
            result = self.seek_results.pop(0) if self.seek_results else signed(self.g[4], 64)
            row = {'fd': signed(self.g[3], 32), 'requested_byte_offset': self.g[4],
                   'result': result, 'cursor_before': self.cursor}
            if result >= 0:
                self.cursor = result
            row['cursor_after'] = self.cursor
            self.seeks.append(row)
            self.clobber(result)
        elif address == 0xf3a8:
            pointer, count = self.g[4], self.g[5]
            valid = any(lo <= pointer and pointer + count <= hi for lo, hi in self.regions)
            if not valid and not self.invalid_buffer_returns_error:
                raise AssertionError('Modeled write received invalid buffer')
            result = self.write_results.pop(0) if self.write_results else count
            if not valid:
                result = -1
            self.writes.append({'fd': signed(self.g[3], 32), 'pointer': pointer, 'count': count,
                                'byte_offset': self.cursor, 'result': result, 'buffer_valid': valid})
            if result > 0:
                self.cursor += result
            self.clobber(result)
        elif address in (0x15344, 0x20b04):
            self.messages.append({'callee': hex(address), 'format_pointer': self.g[3]})
            self.clobber(0)
        elif address == 0x14618:
            self.clobber(self.prompt_answer)
        elif address == 0xee98:
            raise Abort('Modeled nonlocal exit ' + str(self.g[3]))
        else:
            raise AssertionError('Unexpected external ' + hex(address))

    def run(self, pc):
        sentinel = self.lr
        for step in range(30000):
            if pc == sentinel:
                return {'returned': True, 'steps': step}
            if pc not in self.code:
                self.external(pc)
                pc = self.lr
                continue
            i = self.code[pc]
            self.trace.append(hex(pc))
            mnemonic = i.mnemonic.rstrip('+-')
            args = i.op_str.split(', ') if i.op_str else []
            nxt = pc + 4
            reg = lambda text: int(text[1:])
            imm = lambda text: int(text, 0)

            def ea(text):
                delta, base = text[:-1].split('(')
                return (self.g[reg(base)] + imm(delta)) & MASK

            if mnemonic in ('li', 'lis'):
                self.g[reg(args[0])] = imm(args[1]) * (65536 if mnemonic == 'lis' else 1) & MASK
            elif mnemonic in ('lbz', 'lwz', 'ld', 'stb', 'stw', 'std', 'stdu'):
                address = ea(args[1])
                count = 1 if mnemonic in ('lbz', 'stb') else 8 if mnemonic in ('ld', 'std', 'stdu') else 4
                if mnemonic in ('lbz', 'lwz', 'ld'):
                    self.g[reg(args[0])] = self.load(address, count)
                else:
                    self.store(address, self.g[reg(args[0])], count)
                if mnemonic == 'stdu':
                    self.g[1] = address
            elif mnemonic == 'mr': self.g[reg(args[0])] = self.g[reg(args[1])]
            elif mnemonic == 'extsw': self.g[reg(args[0])] = signed(self.g[reg(args[1])], 32) & MASK
            elif mnemonic == 'clrldi': self.g[reg(args[0])] = self.g[reg(args[1])] & ((1 << (64 - imm(args[2]))) - 1)
            elif mnemonic in ('addi', 'add'):
                rhs = imm(args[2]) if mnemonic == 'addi' else self.g[reg(args[2])]
                self.g[reg(args[0])] = (self.g[reg(args[1])] + rhs) & MASK
            elif mnemonic == 'subf': self.g[reg(args[0])] = (self.g[reg(args[2])] - self.g[reg(args[1])]) & MASK
            elif mnemonic in ('mulld', 'mullw'):
                bits = 64 if mnemonic == 'mulld' else 32
                self.g[reg(args[0])] = signed(self.g[reg(args[1])] * self.g[reg(args[2])], bits) & MASK
            elif mnemonic == 'divw':
                left, right = signed(self.g[reg(args[1])], 32), signed(self.g[reg(args[2])], 32)
                assert right and not (left == -0x80000000 and right == -1)
                result = abs(left) // abs(right) * (-1 if (left < 0) != (right < 0) else 1)
                self.g[reg(args[0])] = result & MASK
            elif mnemonic == 'sld': self.g[reg(args[0])] = (self.g[reg(args[1])] << (self.g[reg(args[2])] & 127)) & MASK
            elif mnemonic in ('cmpwi', 'cmpdi', 'cmpw', 'cmpd'):
                field, left, right = args if len(args) == 3 else ('cr0', *args)
                bits = 64 if mnemonic in ('cmpdi', 'cmpd') else 32
                a = signed(self.g[reg(left)], bits)
                b = imm(right) if mnemonic.endswith('i') else signed(self.g[reg(right)], bits)
                self.cr[int(field[2:])] = (a > b) - (a < b)
            elif mnemonic in ('beq', 'bne', 'bge', 'bgt', 'ble', 'blt'):
                field, target = args if len(args) == 2 else ('cr0', args[0])
                value = self.cr[int(field[2:])]
                if {'beq': value == 0, 'bne': value != 0, 'bge': value >= 0,
                    'bgt': value > 0, 'ble': value <= 0, 'blt': value < 0}[mnemonic]:
                    nxt = imm(target)
            elif mnemonic == 'b': nxt = imm(args[0])
            elif mnemonic == 'bl':
                self.lr = pc + 4
                target = imm(args[0])
                if target in self.code:
                    nxt = target
                else:
                    self.external(target)
            elif mnemonic == 'mflr': self.g[reg(args[0])] = self.lr
            elif mnemonic == 'mtlr': self.lr = self.g[reg(args[0])]
            elif mnemonic == 'blr': nxt = self.lr
            elif mnemonic != 'nop': raise AssertionError((hex(pc), mnemonic, args))
            pc = nxt
        raise AssertionError('Bounded instruction step limit')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', choices=('v1', 'v2', 'v3'), default='v1')
    args = parser.parse_args()
    output = ROOT / ('analysis/dev006/p9-write-flush-model-' + args.revision)
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    try:
        elf = PinnedElf('analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf',
            '1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2')
        cases = []
        for bases in ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000)):
            for name, fd, seeks, writes, answer in (
                ('successful-write', 42, [], [], 1), ('negative-FD', -1, [], [], 1),
                ('short-bulk-retry-success', 42, [], [512], 1),
                ('failed-bulk-and-sector-continue', 42, [], [-1, -1], 1),
                ('initial-seek-failed-then-reseek-success', 42, [-1], [], 1),
                ('both-seeks-failed-continue', 42, [-1, -1], [], 1),
                ('retry-seek-failed-after-short-write', 42, [2048000, -1], [512], 1),
                ('initial-seek-failed-abort', 42, [-1], [], 0)):
                cpu = CPU(elf, bases)
                cpu.g[3:7] = [fd & MASK, 0x06010000, 4000, 4096]
                cpu.seek_results, cpu.write_results, cpu.prompt_answer = list(seeks), list(writes), answer
                saved = {reg: cpu.g[reg] for reg in range(14, 32)}
                aborted = False
                try:
                    state = cpu.run(0x14918)
                except Abort:
                    aborted = True
                    state = {'returned': False}
                if not aborted:
                    assert cpu.g[1] == 0x70000000 and cpu.lr == 0x76543210
                    assert all(cpu.g[reg] == value for reg, value in saved.items())
                if name == 'successful-write':
                    assert len(cpu.writes) == 1 and cpu.writes[0]['byte_offset'] == 2048000
                    assert cpu.load(cpu.slot(-0x7b00), 4) == 1
                elif name == 'negative-FD': assert not cpu.writes and not cpu.seeks
                elif name == 'short-bulk-retry-success':
                    assert len(cpu.writes) == 9 and cpu.writes[1]['byte_offset'] == 2048000
                    assert cpu.load(cpu.slot(-0x7b2c), 1) == 0
                elif name == 'failed-bulk-and-sector-continue':
                    assert len(cpu.writes) == 9 and cpu.load(cpu.slot(-0x7b2c), 1) == 0
                elif name == 'both-seeks-failed-continue':
                    assert cpu.writes[0]['byte_offset'] == 123456 != 2048000
                elif name == 'retry-seek-failed-after-short-write':
                    assert cpu.writes[1]['byte_offset'] == 2048512 != 2048000
                elif name == 'initial-seek-failed-abort': assert aborted and not cpu.writes
                cases.append({'case': name, 'segment_bases': [hex(x) for x in bases], 'passed': True,
                              'aborted': aborted, 'seeks': cpu.seeks, 'writes': cpu.writes,
                              'all_IO_success_candidate_byte': cpu.load(cpu.slot(-0x7b2c), 1)})
            for drive, location in (('PNY', 'observations/HW002W/private/native-pny-capture-v1'),
                                    ('Lexar', 'observations/HW002Z/private/native-lexar-capture-v1')):
                sb_raw = (ROOT / location / 'primary-superblock.decoded.bin').read_bytes()
                for dirty, summary_present in ((0, True), (1, True), (0, False), (1, False)):
                    cpu = CPU(elf, bases)
                    header = cpu.slot(-0x7b88)
                    for n, byte in enumerate(sb_raw): cpu.store(0x06001000 + n, byte, 1)
                    cpu.store(header + 8, 160, 8)
                    cpu.store(header + 0x10, 8192, 4)
                    cpu.store(header + 0x14, 0, 4)
                    cpu.store(header + 0x1c, 0x06001000, 4)
                    cpu.store(header + 0x20, dirty, 1)
                    cpu.store(0x06001000 + 0x34c, 0x06010000 if summary_present else 0, 4)
                    cpu.g[3:5] = [42, header]
                    cpu.invalid_buffer_returns_error = True
                    saved = {reg: cpu.g[reg] for reg in range(14, 32)}
                    cpu.run(0x1558c)
                    assert cpu.g[1] == 0x70000000 and cpu.lr == 0x76543210
                    assert all(cpu.g[reg] == value for reg, value in saved.items())
                    assert cpu.load(header + 0x20, 1) == 0
                    if not dirty: assert not cpu.writes and not cpu.seeks
                    elif summary_present:
                        summary_bytes = struct.unpack_from('>i', sb_raw, 0x9c)[0]
                        assert len(cpu.writes) == 1 + (summary_bytes + 16383) // 16384
                        assert sum(w['count'] for w in cpu.writes[1:]) == summary_bytes
                        assert all(w['buffer_valid'] for w in cpu.writes)
                    else:
                        assert any(not w['buffer_valid'] for w in cpu.writes)
                        assert cpu.load(cpu.slot(-0x7b2c), 1) == 0
                    cases.append({'case': 'flush-' + drive, 'segment_bases': [hex(x) for x in bases],
                                  'dirty': dirty, 'summary_present': summary_present, 'passed': True,
                                  'write_count': len(cpu.writes), 'invalid_buffer_write_calls': sum(not w['buffer_valid'] for w in cpu.writes),
                                  'buffer_dirty_byte_at_return': cpu.load(header + 0x20, 1),
                                  'all_IO_success_candidate_byte': cpu.load(cpu.slot(-0x7b2c), 1)})
        result = {'passed': True, 'case_count': len(cases), 'cases': cases,
                  'input_SHA256': elf.sha256,
                  'actual_instruction_model': True, 'I/O_prompt_warning_longjmp_callees_mocked': True,
                  'hardware_fault_or_disk_write_execution': False,
                  'finding': 'When error policy is mocked to continue, two failed seeks can reach sector writes at an unchanged stale cursor; failed retry seek after short bulk write can reach sector writes at the advanced cursor. Final utility status/cleanup and real kernel errors are not modeled.',
                  'whole_checker_failure_cleanup_or_stability_proven': False}
        with (output / 'result.json').open('x', encoding='utf8') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        print(json.dumps({'passed': True, 'actual_instruction_cases': len(cases), 'hardware_IO': False,
                          'conditional_stale_cursor_write_reproduced': True}))
    except BaseException as error:
        with (output / 'failure.json').open('x', encoding='utf8') as f:
            json.dump({'passed': False, 'error': repr(error), 'hardware_IO': False}, f, indent=2)
        raise


if __name__ == '__main__':
    main()
