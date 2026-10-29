"""Build a bounded seek-error stop guard on exact P9; no packaging/device I/O."""
import hashlib
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf, ROOT


def branch(source, target):
    displacement = target - source
    assert displacement % 4 == 0 and -(1 << 25) <= displacement < (1 << 25)
    return 0x48000000 | (displacement & 0x3fffffc)


def main():
    output = ROOT / 'analysis/dev006/p10-seek-guard-v1'
    output.mkdir(exist_ok=False)
    elf = PinnedElf('analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf',
        '1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2')
    assert elf.bytes_at(0x26500, 32) == bytes(32)
    hooks = {0x14ad8: (0x4bfffec8, 0x26500), 0x14ae8: (0x4bfffeec, 0x26500),
             0x14a28: (0x60000000, 0x26514)}
    words = [0x812284d4, 0x38000000, 0x98090000, 0x3860ffff,
             branch(0x26510, 0x14a68), 0x2fa30000, 0x419cffe8,
             branch(0x2651c, 0x14a2c)]
    helper = b''.join(struct.pack('>I', word) for word in words)
    new = bytearray(elf.data)
    def offset(address):
        h = next(h for h in elf.loads if h[3] <= address < h[3] + h[5])
        return h[2] + address - h[3]
    for address, (expected, target) in hooks.items():
        assert elf.word(address) == expected
        struct.pack_into('>I', new, offset(address), branch(address, target))
    new[offset(0x26500):offset(0x26500) + 32] = helper
    path = output / 'libfs_utility_init-p10.elf'
    with path.open('xb') as f: f.write(new)
    decoded = list(elf.decoder.disasm(helper, 0x26500))
    assert [(i.mnemonic, i.op_str) for i in decoded] == [
        ('lwz', 'r9, -0x7b2c(r2)'), ('li', 'r0, 0'), ('stb', 'r0, 0(r9)'),
        ('li', 'r3, -1'), ('b', '0x14a68'), ('cmpdi', 'cr7, r3, 0'),
        ('blt', 'cr7, 0x26500'), ('b', '0x14a2c')]
    with (output / 'helper.txt').open('x', encoding='utf8') as f:
        f.write(''.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}\n' for i in decoded))
    restored = bytearray(new)
    for address in hooks: restored[offset(address):offset(address) + 4] = elf.bytes_at(address, 4)
    restored[offset(0x26500):offset(0x26500) + 32] = bytes(32)
    assert restored == elf.data
    with (output / 'manifest.json').open('x', encoding='utf8') as f:
        json.dump({'source': elf.relative, 'source_sha256': elf.sha256,
            'elf_sha256': hashlib.sha256(new).hexdigest(), 'file_bytes_unchanged': len(new),
            'hooks': {hex(address): {'old': hex(expected), 'new': hex(branch(address, target))}
                      for address, (expected, target) in hooks.items()},
            'helper_virtual_address': '0x26500', 'helper_bytes': 32,
            'purpose': 'On any of the three block-writer seek failures, skip remaining writes for that block, clear existing I/O-success flag and return -1 through original epilogue',
            'existing_error_prompt_policy_before_first_two_guards_unchanged': True,
            'program_headers_relocations_data_imports_budget_observer_flags_unchanged': True,
            'whole_checker_failure_cleanup_or_stability_proven': False,
            'packaged_or_hardware_tested': False}, f, indent=2)
        f.write('\n')
    print(json.dumps({'P10_decoded_draft_created': True, 'hooks': 3, 'helper_bytes': 32,
                      'elf_sha256': hashlib.sha256(new).hexdigest(), 'device_IO': False}))


if __name__ == '__main__':
    main()
