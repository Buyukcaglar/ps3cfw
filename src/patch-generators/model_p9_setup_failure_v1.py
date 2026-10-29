"""Actual P9 setup check/return and cleanup-entry gates, with explicit callees mocked.

No whole-checker, allocator, disk writes, or cleanup-callee semantics are emulated.
The saved native PNY geometry supplies sizes. Code and pointer relocations are
read from pinned ELF, with independent code/data segment placements.
"""
import hashlib
import json
import struct
from pinned_binary import PinnedElf, ROOT

MASK = (1 << 64) - 1


def signed(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value >> (bits - 1) else value


class CPU:
    def __init__(self, elf, bases):
        self.elf, self.bases = elf, bases
        self.g = [0x2345000000000000 + i * 111 for i in range(32)]
        self.g[1] = 0x70000000
        # P8 expanded text by 0x3000 and rebased the data segment. The TOC is
        # the native descriptor target at data offset 0x9560, not retail VA2e7c0.
        self.g[2] = bases[1] + 0x9560
        self.lr, self.ca = 0x76543210, 0
        self.cr = {i: 0 for i in range(8)}
        self.memory = {}
        self.regions = [(self.relocate(h[3]), self.relocate(h[3]) + h[6]) for h in elf.loads]
        self.regions += [(0x6fffe000, 0x70001000), (0x06000000, 0x06004000)]
        self.calls, self.trace = [], []
        self.code = {i.address: i for lo, hi in (
            (0x1f694, 0x1f6bc), (0x1f798, 0x1f880), (0x1fb50, 0x1fbb4),
            (0x1fc34, 0x1fc48), (0x1fc90, 0x1fcac), (0x1ffa4, 0x1ffb8),
            (0x14e80, 0x14ef0), (0x1522c, 0x1527c),
        ) for i in elf.instructions(lo, hi)}
        toc_relocations = 0
        for header in elf.headers:
            if header[0] != 0x700000a4:
                continue
            for offset in range(header[2], header[2] + header[5], 24):
                site, reserved, vi, ai, kind, addend = struct.unpack_from('>QHBBIQ', elf.data, offset)
                if kind == 1:
                    self.store(bases[ai] + site, bases[vi] + addend, 4)
                    toc_relocations += int(vi == 1 and addend == 0x9560)
        assert toc_relocations >= 30, 'Native descriptor TOC target changed'
        self.returned = False
        self.fail_at = None
        self.alloc_index = 0
        self.saved = {i: 0x3456000000000000 + i * 777 for i in range(23, 32)}
        for i, value in self.saved.items():
            self.store(self.g[1] + 0x668 + (i - 23) * 8, value, 8)
        self.store(self.g[1] + 0x6c0, 0x76543210, 8)
        self.g[30] = 0x06000000
        self.store(self.g[30] + 0x1c, 0x06001000, 4)
        self.g[26] = 0x06003000

    def relocate(self, address):
        index = next(i for i, h in enumerate(self.elf.loads) if h[3] <= address < h[3] + h[6])
        return self.bases[index] + address - self.elf.loads[index][3]

    def access(self, address, count):
        if not any(lo <= address and address + count <= hi for lo, hi in self.regions):
            raise AssertionError('Out-of-bounds model memory: ' + hex(address))

    def load(self, address, count):
        self.access(address, count)
        return int.from_bytes(bytes(self.memory.get(address + i, 0) for i in range(count)), 'big')

    def store(self, address, value, count):
        self.access(address, count)
        for i, byte in enumerate((value & ((1 << (count * 8)) - 1)).to_bytes(count, 'big')):
            self.memory[address + i] = byte

    def slot(self, displacement):
        return self.load(self.g[2] + displacement, 4)

    def clobber(self, result):
        for reg in (0, *range(3, 13)):
            self.g[reg] = 0xface000000000000 + reg
        self.g[3] = result & MASK
        for cr in (0, 1, 5, 6, 7):
            self.cr[cr] = 1

    def call(self, address):
        row = {'target': hex(address), 'r3': self.g[3], 'r4': self.g[4]}
        self.calls.append(row)
        if address == 0xe718:
            row['allocation_index'] = self.alloc_index
            row['requested_product'] = (self.g[3] & 0xffffffff) * (self.g[4] & 0xffffffff)
            assert row['requested_product'] <= 0xffffffff
            result = 0 if self.alloc_index == self.fail_at else 0x08000000 + self.alloc_index * 0x100000
            self.alloc_index += 1
            row['mock_result'] = result
            self.clobber(result)
        elif address in (0x20b04, 0x14e80):
            row['mocked_callee_returns'] = True
            self.clobber(0)
        else:
            raise AssertionError('Unexpected mocked callee ' + hex(address))

    def run(self, pc, ends=()):
        for _ in range(180):
            if pc in ends:
                return pc
            i = self.code[pc]
            self.trace.append(hex(pc))
            mnemonic = i.mnemonic.rstrip('+-')
            args = i.op_str.split(', ') if i.op_str else []
            next_pc = pc + 4
            def reg(text): return int(text[1:])
            def imm(text): return int(text, 0)
            def ea(text):
                delta, base = text[:-1].split('(')
                return (self.g[reg(base)] + imm(delta)) & MASK
            if mnemonic in ('li', 'lis'):
                self.g[reg(args[0])] = (imm(args[1]) * (65536 if mnemonic == 'lis' else 1)) & MASK
            elif mnemonic in ('lwz', 'ld', 'stw', 'std', 'stdu'):
                address = ea(args[1])
                count = 8 if mnemonic in ('ld', 'std', 'stdu') else 4
                if mnemonic in ('lwz', 'ld'):
                    self.g[reg(args[0])] = self.load(address, count)
                else:
                    self.store(address, self.g[reg(args[0])], count)
                if mnemonic == 'stdu':
                    self.g[1] = address
            elif mnemonic == 'mr': self.g[reg(args[0])] = self.g[reg(args[1])]
            elif mnemonic == 'clrldi': self.g[reg(args[0])] = self.g[reg(args[1])] & ((1 << (64 - imm(args[2]))) - 1)
            elif mnemonic == 'extsw': self.g[reg(args[0])] = signed(self.g[reg(args[1])], 32) & MASK
            elif mnemonic == 'addi': self.g[reg(args[0])] = (self.g[reg(args[1])] + imm(args[2])) & MASK
            elif mnemonic == 'ori': self.g[reg(args[0])] = self.g[reg(args[1])] | imm(args[2])
            elif mnemonic == 'slwi': self.g[reg(args[0])] = (self.g[reg(args[1])] << imm(args[2])) & 0xffffffff
            elif mnemonic == 'sldi': self.g[reg(args[0])] = (self.g[reg(args[1])] << imm(args[2])) & MASK
            elif mnemonic == 'sradi':
                value, shift = signed(self.g[reg(args[1])], 64), imm(args[2])
                self.ca = int(value < 0 and bool(value & ((1 << shift) - 1)))
                self.g[reg(args[0])] = (value >> shift) & MASK
            elif mnemonic == 'addze': self.g[reg(args[0])] = (self.g[reg(args[1])] + self.ca) & MASK
            elif mnemonic in ('cmpwi', 'cmpdi'):
                field, left, right = args if len(args) == 3 else ('cr0', *args)
                value = signed(self.g[reg(left)], 32 if mnemonic == 'cmpwi' else 64)
                self.cr[int(field[2:])] = (value > imm(right)) - (value < imm(right))
            elif mnemonic in ('beq', 'bne', 'bge', 'blt'):
                field, target = args if len(args) == 2 else ('cr0', args[0])
                value = self.cr[int(field[2:])]
                take = {'beq': value == 0, 'bne': value != 0, 'bge': value >= 0, 'blt': value < 0}[mnemonic]
                if take: next_pc = imm(target)
            elif mnemonic == 'b': next_pc = imm(args[0])
            elif mnemonic == 'bl': self.lr = pc + 4; self.call(imm(args[0]))
            elif mnemonic == 'mfcr': self.g[reg(args[0])] = 0
            elif mnemonic == 'mflr': self.g[reg(args[0])] = self.lr
            elif mnemonic == 'mtlr': self.lr = self.g[reg(args[0])]
            elif mnemonic == 'mtocrf': pass  # Only on an unexecuted cleanup return in this experiment.
            elif mnemonic == 'blr': self.returned = True; return self.lr
            elif mnemonic != 'nop': raise AssertionError((mnemonic, args))
            pc = next_pc
        raise AssertionError('Model step bound')


def main():
    output = ROOT / 'analysis/dev006/p9-setup-failure-model-v2'
    output.mkdir(exist_ok=False)
    elf = PinnedElf('analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf',
                    '1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2')
    geometry_path = ROOT / 'observations/HW002W/geometry-verification.json'
    geometry = json.loads(geometry_path.read_text('utf8'))['geometry']
    cases, gates, aliases = [], [], None
    for bases in ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000)):
        for directories in (0, 139):
            for failed in (None, 0, 1, 2, 3, 4):
                c = CPU(elf, bases)
                c.fail_at = failed
                c.store(0x06001000 + 0x9c, geometry['summary'], 4)
                c.store(0x06001000 + 0x2c, geometry['ncg'], 4)
                c.store(0x06001000 + 0x3f0, directories, 8)
                c.store(c.g[26], geometry['size'], 8)
                end = c.run(0x1f694, {0x1f6bc})
                if not c.returned:
                    assert end == 0x1f6bc
                    # Explicit boundary: successful summary reads are outside this model.
                    end = c.run(0x1f798, {0x1f87c})
                allocations = [row for row in c.calls if row['target'] == '0xe718']
                expected = [geometry['summary'], 60981796, geometry['ncg'] * 8,
                            (max(directories, 128) + 10) * 4, max(directories, 128) * 4]
                requested = [row['requested_product'] for row in allocations]
                # The pair is allocated before either of its two results is checked.
                count = 5 if failed is None or failed >= 3 else failed + 1
                assert requested == expected[:count], (failed, requested)
                if failed is None:
                    assert end == 0x1f87c and not c.returned
                    assert not any(row['target'] == '0x14e80' for row in c.calls)
                else:
                    assert c.returned and end == 0x76543210
                    assert c.g[3] == signed(0x80010004, 32) & MASK
                    assert c.g[1] == 0x700006b0
                    assert all(c.g[reg] == value for reg, value in c.saved.items())
                    cleanup = [row for row in c.calls if row['target'] == '0x14e80']
                    assert len(cleanup) == 1 and cleanup[0]['r3'] == 0
                cases.append({'bases': [hex(x) for x in bases], 'directories': directories,
                              'failed_setup_allocation': failed, 'requests': requested,
                              'end': hex(end), 'cleanup_return_is_mocked': failed is not None,
                              'calls': c.calls, 'trace': c.trace})
        for fd in (-1, 42):
            c = CPU(elf, bases)
            c.store(c.slot(-0x7b34), 0, 4)  # Ordinary descriptor-based route only.
            assert c.slot(-0x7430) == c.slot(-0x7b38)
            assert c.slot(-0x7ab4) == c.slot(-0x7418)
            c.store(c.slot(-0x7b38), fd, 4)
            c.store(c.slot(-0x7ab4), 17, 4)
            c.g[3] = 0
            end = c.run(0x14e80, {0x14ee8, 0x15238})
            assert end == (0x15238 if fd < 0 else 0x14ee8)
            assert c.g[3] == (17 if fd < 0 else 42)
            gates.append({'bases': [hex(x) for x in bases], 'write_descriptor': fd,
                          'next_call_site': hex(end),
                          'next_callee': '0x10d28' if fd < 0 else '0x1558c',
                          'call_not_executed': True, 'trace': c.trace})
            aliases = {'write_descriptor_virtual_global': hex(c.slot(-0x7430) - bases[1] + elf.loads[1][3]),
                       'read_descriptor_virtual_global': hex(c.slot(-0x7418) - bases[1] + elf.loads[1][3])}
    result = {'passed': True, 'setup_cases': cases, 'cleanup_entry_cases': gates,
              'source': elf.relative, 'source_sha256': elf.sha256,
              'geometry_sha256': hashlib.sha256(geometry_path.read_bytes()).hexdigest(),
              'resolved_pointer_aliases': aliases,
              'P9_TOC_virtual_address': hex(elf.loads[1][3] + 0x9560),
              'retained_first_attempt': 'analysis/dev006/p9-setup-failure-model-v1/source-first-attempt.py',
              'first_attempt_limit': 'Initially seeded the original retail TOC VA after the P8 data rebase. Memory bounds rejected its first global read; no result was emitted. Corrected by descriptor-target relocations at data offset9560.',
              'full_failure_cleanup_or_side_effect_safety_proven': False,
              'hardware_or_checker_execution': False,
              'limits': 'Only five setup allocations, their checks/error return after mocked cleanup, and ordinary cleanup entry gates. Successful summary reads, buffer initialization, cleanup callees, later phases, longjmp, corrupt geometry, allocator semantics, concurrency and physical side effects are excluded. A writable descriptor can reach flush even after a failed setup allocation.'}
    with (output / 'result.json').open('x', encoding='utf8') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({'passed': True, 'setup_cases': len(cases), 'cleanup_gates': len(gates),
                      'aliases': aliases, 'whole_failure_cleanup_proven': False}))


if __name__ == '__main__':
    main()
