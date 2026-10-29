"""Fail the ordinary block reader on reported negative seek returns, no devices."""
import hashlib
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf, ROOT


def branch(source, target):
    delta = target - source
    assert delta % 4 == 0 and -(1 << 25) <= delta < (1 << 25)
    return 0x48000000 | (delta & 0x3fffffc)


def negative_branch(source, target):
    delta = target - source
    assert delta % 4 == 0 and -32768 <= delta < 32768
    return 0x419c0000 | (delta & 0xfffc)


def main():
    output = ROOT / 'analysis/dev006/p13-read-seek-v1'
    output.mkdir(exist_ok=False)
    elf = PinnedElf('analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf',
                    '82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85')
    assert elf.bytes_at(0x26640, 48) == bytes(48)
    hooks = {0x14b88: (0x419c0200, 0x26654),
             0x14bd4: (0x419c0270, 0x2665c),
             0x14c50: (0x60000000, 0x26664)}
    words = [0x3b000001, 0x812284d4, 0x38000000, 0x98090000,
             branch(0x26650, 0x14cf0),
             negative_branch(0x26654, 0x26640), branch(0x26658, 0x14b8c),
             negative_branch(0x2665c, 0x26640), branch(0x26660, 0x14bd8),
             0x2fa30000, negative_branch(0x26668, 0x26640), branch(0x2666c, 0x14c54)]
    helper = b''.join(struct.pack('>I', word) for word in words)
    decoded = list(elf.decoder.disasm(helper, 0x26640))
    expected = [('li', 'r24, 1'), ('lwz', 'r9, -0x7b2c(r2)'), ('li', 'r0, 0'),
                ('stb', 'r0, 0(r9)'), ('b', '0x14cf0'),
                ('blt', 'cr7, 0x26640'), ('b', '0x14b8c'),
                ('blt', 'cr7, 0x26640'), ('b', '0x14bd8'),
                ('cmpdi', 'cr7, r3, 0'), ('blt', 'cr7, 0x26640'), ('b', '0x14c54')]
    assert [(i.mnemonic.rstrip('+-'), i.op_str) for i in decoded] == expected
    def offset(at):
        h = next(h for h in elf.loads if h[3] <= at < h[3] + h[5])
        return h[2] + at - h[3]
    new = bytearray(elf.data)
    for at, (old, target) in hooks.items():
        assert elf.word(at) == old
        struct.pack_into('>I', new, offset(at), branch(at, target))
    new[offset(0x26640):offset(0x26640) + 48] = helper
    restored = bytearray(new)
    for at in hooks:
        restored[offset(at):offset(at) + 4] = elf.bytes_at(at, 4)
    restored[offset(0x26640):offset(0x26640) + 48] = bytes(48)
    assert restored == elf.data
    with (output / 'libfs_utility_init-p13.elf').open('xb') as stream:
        stream.write(new)
    with (output / 'source.py').open('xb') as stream:
        stream.write(Path(__file__).read_bytes())
    with (output / 'helper.txt').open('x', encoding='utf8') as stream:
        stream.write(''.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}\n' for i in decoded))
    with (output / 'manifest.json').open('x', encoding='utf8') as stream:
        json.dump({'source': elf.relative, 'source_sha256': elf.sha256,
                   'elf_sha256': hashlib.sha256(new).hexdigest(), 'file_bytes_unchanged': len(new),
                   'hooks': {hex(at): {'old': hex(old), 'new': hex(branch(at, target))}
                             for at, (old, target) in hooks.items()},
                   'helper_virtual_address': '0x26640', 'helper_bytes': 48,
                   'purpose': 'Negative initial, retry or per-sector seek result clears existing IO-success byte, returns nonzero through original reader epilogue, and stops further reads/reseeks from that wrapper invocation',
                   'successful_seeks_and_read_error_fallback_intended_unchanged': True,
                   'reported_seek_failures_abort_instead_of_retrying': True,
                   'no_new_calls_syscalls_allocations_imports_relocations_memory_sizes_or_observer_changes': True,
                   'all_callers_cleanup_or_stability_proven': False,
                   'packaged_or_hardware_tested': False}, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'P13_decoded_draft': True, 'hooks': 3, 'owned_helper_bytes': 48,
                      'elf_sha256': hashlib.sha256(new).hexdigest(), 'hardware_IO': False}))


if __name__ == '__main__':
    main()
