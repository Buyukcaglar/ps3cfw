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
        self.code = {i.address: i for lo, hi in ((0x14618, 0x14784), (0x14888, 0x14aec), (0x15344, 0x153e8), (0x1558c, 0x1572c),
                     (0x14e80, 0x15344), (0x26500, 0x26520),
                     (0x1f694, 0x1f6bc), (0x1f798, 0x1f880), (0x1fb50, 0x1fbb4),
                     (0x1fc34, 0x1fc48), (0x1fc90, 0x1fcac), (0x1ffa4, 0x1ffb8))
                     for i in elf.instructions(lo, hi)}
        self.seeks, self.writes, self.messages = [], [], []
        self.seek_results, self.write_results = [], []
        self.cursor = 123456
        self.prompt_answer = 1
        self.invalid_buffer_returns_error = False
        self.setup_allocations = []
        self.cleanup_frees = []
        self.cleanup_closes = []
        self.g[1], self.lr = 0x70000000, 0x76543210
        self.store(self.slot(-0x7b08), 512, 4)
        self.store(self.slot(-0x7b38), 42, 4)
        self.store(self.slot(-0x7b2c), 1, 1)
        self.store(self.slot(-0x7b00), 0, 4)
        self.store(self.slot(-0x7b10), 0, 4)
        self.store(self.slot(-0x7ba4), 0, 1)  # Ordinary non-preen mode.
        self.store(self.slot(-0x7b34), 0, 4)  # Ordinary non-mounted device.
        self.store(self.slot(-0x7a8c), 0, 1)
        self.store(self.slot(-0x7b28), 1, 1)  # Yes-answer mode.
        self.store(self.slot(-0x7b3c), 0, 1)

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
        if address == 0xe718:
            count = (self.g[3] & 0xffffffff) * (self.g[4] & 0xffffffff)
            result = 0 if self.alloc_index == self.fail_at else 0x08000000 + self.alloc_index * 0x10000000
            self.setup_allocations.append({'index': self.alloc_index, 'request': count, 'result': result})
            self.alloc_index += 1
            if result: self.regions.append((result, result + max(count, 512)))
            self.clobber(result)
        elif address == 0xe7a0:
            self.cleanup_frees.append(self.g[3])
            self.clobber(0)
        elif address == 0x10d28:
            self.cleanup_closes.append(signed(self.g[3], 32))
            self.clobber(0)
        elif address == 0xf7e8:
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
        elif address in (0x20918, 0x20b04):
            self.messages.append({'callee': hex(address), 'format_pointer': self.g[3]})
            self.clobber(0)
        elif address == 0x214c8:
            self.store(self.g[1] + 0x28, self.g[2], 8)  # Import glink TOC save.
            self.clobber(0 if self.g[3] == self.g[4] else 1)
        elif address == 0xee98:
            raise Abort('Modeled nonlocal exit ' + str(self.g[3]))
        else:
            raise AssertionError('Unexpected external ' + hex(address))

    def run(self, pc, ends=()):
        sentinel = 0x76543210
        for step in range(30000):
            if pc == sentinel:
                return {'returned': True, 'steps': step}
            if pc in ends:
                return {'returned': False, 'end': pc, 'steps': step}
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
            elif mnemonic == 'ori': self.g[reg(args[0])] = self.g[reg(args[1])] | imm(args[2])
            elif mnemonic == 'slwi': self.g[reg(args[0])] = (self.g[reg(args[1])] << imm(args[2])) & 0xffffffff
            elif mnemonic == 'sldi': self.g[reg(args[0])] = (self.g[reg(args[1])] << imm(args[2])) & MASK
            elif mnemonic == 'sradi':
                value, shift = signed(self.g[reg(args[1])], 64), imm(args[2])
                self.ca = int(value < 0 and bool(value & ((1 << shift) - 1)))
                self.g[reg(args[0])] = (value >> shift) & MASK
            elif mnemonic == 'addze': self.g[reg(args[0])] = (self.g[reg(args[1])] + self.ca) & MASK
            elif mnemonic == 'mfcr': self.g[reg(args[0])] = sum(({ -1: 8, 0: 2, 1: 4}[self.cr[i]]) << (4 * (7-i)) for i in range(8))
            elif mnemonic == 'mtocrf':
                mask, value = imm(args[0]), self.g[reg(args[1])]
                for index in range(8):
                    if mask & (1 << (7-index)):
                        bits = (value >> (4 * (7-index))) & 15
                        self.cr[index] = -1 if bits & 8 else 1 if bits & 4 else 0
            elif mnemonic == 'mr': self.g[reg(args[0])] = self.g[reg(args[1])]
            elif mnemonic == 'extsw': self.g[reg(args[0])] = signed(self.g[reg(args[1])], 32) & MASK
            elif mnemonic == 'clrldi': self.g[reg(args[0])] = self.g[reg(args[1])] & ((1 << (64 - imm(args[2]))) - 1)
            elif mnemonic in ('addi', 'add'):
                rhs = imm(args[2]) if mnemonic == 'addi' else self.g[reg(args[2])]
                self.g[reg(args[0])] = (self.g[reg(args[1])] + rhs) & MASK
            elif mnemonic == 'xor': self.g[reg(args[0])] = self.g[reg(args[1])] ^ self.g[reg(args[2])]
            elif mnemonic == 'srawi': self.g[reg(args[0])] = (signed(self.g[reg(args[1])], 32) >> imm(args[2])) & MASK
            elif mnemonic == 'srwi': self.g[reg(args[0])] = (self.g[reg(args[1])] & 0xffffffff) >> imm(args[2])
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
    output = ROOT / ('analysis/dev006/p10-setup-cleanup-model-' + args.revision)
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    try:
        elf = PinnedElf('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf',
            'daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688')
        rows = []
        for bases in ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000)):
            for drive, folder in (('PNY', 'observations/HW002W/private/native-pny-capture-v1'),
                                  ('Lexar', 'observations/HW002Z/private/native-lexar-capture-v1')):
                raw = (ROOT / folder / 'primary-superblock.decoded.bin').read_bytes()
                groups, summary = (struct.unpack_from('>i', raw, at)[0] for at in (0x2c, 0x9c))
                size = struct.unpack_from('>q', raw, 0x438)[0]
                bitmap = (((size + 7) // 8 + 1) // 2) * 2
                for directories in (0, 139):
                    for failed in range(5):
                        for write_fd in (-1, 42):
                            cpu = CPU(elf, bases)
                            cpu.fail_at = failed
                            header = cpu.slot(-0x7b88)
                            cpu.g[30] = header
                            cpu.store(header + 0x1c, 0x06001000, 4)
                            cpu.store(header + 0x20, 0, 1)  # Explicit clean in-memory buffer precondition.
                            for n, byte in enumerate(raw): cpu.store(0x06001000 + n, byte, 1)
                            cpu.store(0x06001000 + 0x3f0, directories, 8)
                            cpu.store(cpu.g[26], size, 8)
                            cpu.store(cpu.slot(-0x7b38), write_fd, 4)
                            cpu.store(cpu.slot(-0x7ab4), 17, 4)
                            # Empty synthetic buffer queue and clean auxiliary buffer.
                            cpu.store(cpu.slot(-0x7b4c) + 4, 0, 4)
                            cpu.store(cpu.slot(-0x7b4c) + 0x10, 0, 4)
                            cpu.store(cpu.slot(-0x7b50) + 0x20, 0, 1)
                            cpu.store(cpu.slot(-0x7b50) + 0x1c, 0, 4)
                            cpu.cr.update({2: 1, 3: -1, 4: 0})
                            saved_cr = {index: cpu.cr[index] for index in (2, 3, 4)}
                            state = cpu.run(0x1f694, {0x1f6bc})
                            if not state['returned']:
                                assert state['end'] == 0x1f6bc
                                # Successful summary reads/buffer initialization are excluded.
                                state = cpu.run(0x1f798, {0x1f87c})
                            assert state['returned'] and cpu.g[1] == 0x700006b0
                            assert cpu.g[3] == signed(0x80010004, 32) & MASK
                            assert all(cpu.g[reg] == value for reg, value in cpu.saved.items())
                            assert all(cpu.cr[index] == value for index, value in saved_cr.items())
                            expected = [summary, bitmap, groups * 8,
                                        (max(directories, 128) + 10) * 4,
                                        max(directories, 128) * 4]
                            requested = [row['request'] for row in cpu.setup_allocations]
                            assert requested == expected[:5 if failed >= 3 else failed + 1]
                            assert cpu.cleanup_closes == ([17] if write_fd < 0 else [17, 42])
                            assert not cpu.seeks and not cpu.writes
                            assert cpu.cleanup_frees == ([] if write_fd < 0 else [0])
                            rows.append({'drive': drive, 'segment_bases': [hex(x) for x in bases],
                                'directory_input': directories, 'failed_allocation': failed,
                                'write_FD': write_fd, 'requests': requested, 'passed': True,
                                'actual_ordinary_cleanup_returned': True,
                                'flush_and_block_writer_instructions_available_but_clean_buffers_skipped_IO': True,
                                'mocked_close_descriptors': cpu.cleanup_closes,
                                'mocked_free_arguments': cpu.cleanup_frees})
        result = {'passed': True, 'case_count': len(rows), 'cases': rows,
            'source': elf.relative, 'source_sha256': elf.sha256,
            'actual_setup_error_ordinary_cleanup_and_return_instructions_executed': True,
            'cleanup_function_no_longer_wholly_mocked_in_these_cases': True,
            'explicit_preconditions': ['ordinary non-mounted/non-preen mode',
                'in-memory superblock and auxiliary buffer dirty bytes zero',
                'synthetic empty buffer queue', 'valid metadata pointers and captured geometry'],
            'mocked_callees': ['five calloc results', 'native free', 'descriptor close',
                'format/strcmp/kernel IO/nonlocal exit if reached'],
            'successful_summary_reads_and_later_setup_excluded': True,
            'all_real_preallocation_dirty_state_paths_proven': False,
            'dirty_buffer_or_nonempty_queue_cleanup_proven': False,
            'real_native_free_close_bulk_delete_or_kernel_side_effects_proven': False,
            'allocation_failure_hardware_or_disk_IO': False, 'stable_support': False}
        with (output / 'result.json').open('x', encoding='utf8') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        print(json.dumps({'passed': True, 'setup_to_actual_cleanup_cases': len(rows),
                          'disk_IO_or_hardware_failure_injection': False, 'stable_support': False}))
    except BaseException as error:
        with (output / 'failure.json').open('x', encoding='utf8') as f:
            json.dump({'passed': False, 'error': repr(error), 'hardware_IO': False}, f, indent=2)
        raise


if __name__ == '__main__':
    main()

