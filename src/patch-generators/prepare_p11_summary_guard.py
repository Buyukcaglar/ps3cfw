"""Add a pre-write null-summary rejection to exact P10; decoded draft only."""
import hashlib
import json
import struct
from pinned_binary import PinnedElf, ROOT


def branch(source, target):
    delta = target - source
    assert delta % 4 == 0 and -(1 << 25) <= delta < (1 << 25)
    return 0x48000000 | (delta & 0x3fffffc)


def conditional(opcode, source, target):
    delta = target - source
    assert delta % 4 == 0 and -32768 <= delta < 32768
    return opcode | (delta & 0xfffc)


def main():
    output = ROOT / 'analysis/dev006/p11-summary-guard-v2'
    output.mkdir(exist_ok=False)
    elf = PinnedElf('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf',
        'daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688')
    at, size = 0x26540, 76
    assert elf.bytes_at(at, size) == bytes(size)
    assert elf.word(0x155c0) == 0x838284c8
    words = [0x838284c8, 0x813c0000, 0x2f890000,
        conditional(0x419c0000, at+12, at+72), 0x81228478, 0x7f844800,
        conditional(0x409e0000, at+24, at+72), 0x8124001c, 0x8009009c, 0x2f800000,
        conditional(0x409d0000, at+40, at+72), 0x8009034c, 0x2f800000,
        conditional(0x409e0000, at+52, at+72), 0x812284d4, 0x38000000, 0x98090000,
        branch(at+68, 0x1563c), branch(at+72, 0x155c4)]
    helper = b''.join(struct.pack('>I', w) for w in words)
    assert len(helper) == size
    decoded = list(elf.decoder.disasm(helper, at))
    assert [(i.mnemonic, i.op_str) for i in decoded] == [
        ('lwz', 'r28, -0x7b38(r2)'), ('lwz', 'r9, 0(r28)'), ('cmpwi', 'cr7, r9, 0'),
        ('blt', 'cr7, 0x26588'), ('lwz', 'r9, -0x7b88(r2)'), ('cmpw', 'cr7, r4, r9'),
        ('bne', 'cr7, 0x26588'), ('lwz', 'r9, 0x1c(r4)'), ('lwz', 'r0, 0x9c(r9)'),
        ('cmpwi', 'cr7, r0, 0'), ('ble', 'cr7, 0x26588'), ('lwz', 'r0, 0x34c(r9)'),
        ('cmpwi', 'cr7, r0, 0'), ('bne', 'cr7, 0x26588'), ('lwz', 'r9, -0x7b2c(r2)'),
        ('li', 'r0, 0'), ('stb', 'r0, 0(r9)'), ('b', '0x1563c'), ('b', '0x155c4')]
    def offset(address):
        segment = next(h for h in elf.loads if h[3] <= address < h[3]+h[5])
        return segment[2]+address-segment[3]
    draft = bytearray(elf.data)
    struct.pack_into('>I', draft, offset(0x155c0), branch(0x155c0, at))
    draft[offset(at):offset(at)+size] = helper
    restored = bytearray(draft)
    restored[offset(0x155c0):offset(0x155c0)+4] = elf.bytes_at(0x155c0, 4)
    restored[offset(at):offset(at)+size] = bytes(size)
    assert restored == elf.data
    with (output / 'libfs_utility_init-p11.elf').open('xb') as stream: stream.write(draft)
    with (output / 'helper.txt').open('x', encoding='utf8') as stream:
        stream.write(''.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}\n' for i in decoded))
    with (output / 'manifest.json').open('x', encoding='utf8') as stream:
        json.dump({'source': elf.relative, 'source_sha256': elf.sha256,
            'elf_sha256': hashlib.sha256(draft).hexdigest(), 'file_bytes_unchanged': len(draft),
            'hook': {'VA': '0x155c0', 'old': '0x838284c8', 'new': hex(branch(0x155c0, at))},
            'helper_virtual_address': hex(at), 'helper_bytes': size,
            'purpose': 'Dirty primary buffer with positive summary size and null summary pointer: clear existing I/O-success flag and return before any superblock/summary write, retaining dirty byte',
            'normal_present_summary_nonprimary_clean_or_negative_FD_paths_intended_unchanged': True,
            'no_calls_syscalls_allocations_new_imports_relocations_or_memory_size_changes': True,
            'whole_failure_cleanup_or_stability_proven': False, 'packaged_or_hardware_tested': False}, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'P11_decoded_draft': True, 'hook_words': 1, 'owned_helper_bytes': size,
        'elf_sha256': hashlib.sha256(draft).hexdigest(), 'hardware_IO': False}))


if __name__ == '__main__': main()
