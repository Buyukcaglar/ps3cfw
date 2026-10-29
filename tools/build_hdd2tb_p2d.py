"""Build a bounded on-screen admission diagnostic, on regular files only.

P2D retains the supplied baseline's 1536 GiB admission behavior, so the known
2 TB Crucial is expected to stop and show the byte capacity returned on PS3.
It is not a larger-drive fix. P1 artifacts and builder are never written.
SPDX-License-Identifier: GPL-2.0-only
"""
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

import build_hdd2tb_p1 as base

ROOT = base.ROOT
WORK = ROOT / 'analysis/build-p2d'
DEST = ROOT / 'candidates/HDD2TB-P2D'
P1_BUILDER_SHA = 'fe4cde05884e5dcf8f9b399ee85c7835801d17c3cd390d187e749fbb20d75499'
DIAGNOSTIC_FORMAT = b'HDD2TB-P2D&#xa;CAP=%llu B&#xa;GATE=1649267441664\0'
ORIGINAL_FORMAT = b'Untolerable capacity HDD detected : cap. %lld[Bytes].!!!!\n\0'
CODE_PATCHES = [
    (0x36268, '3b610080', '83628338', 'Oversize snprintf destination: existing persistent 0x400-byte error buffer'),
    (0x314D0, '812282d4', '83a28338', 'Normal unsupported case: load persistent buffer into r29'),
    (0x314D4, '8162835c', '60000000', 'Normal unsupported case: bypass language-index load'),
    (0x314DC, '4bfffe74', '4bfffd18', 'Normal unsupported case: join existing display at VA0x411f4'),
    (0x3C758, '4bffdc29', '80628338', 'Safe Mode unsupported case: use persistent buffer instead of language lookup'),
]


def patched_elf(original):
    assert base.sha(original) == base.ELF_SHA
    result = bytearray(original)
    patches = []
    for off, before, after, purpose in CODE_PATCHES:
        old, new = bytes.fromhex(before), bytes.fromhex(after)
        assert original[off:off + len(old)] == old and len(old) == len(new) == 4
        result[off:off + 4] = new
        patches.append({'elf_offset': off, 'virtual_address': off + 0x10000,
                        'before': before, 'after': after, 'purpose': purpose})
    off = 0xB7E68
    assert original[off:off + len(ORIGINAL_FORMAT)] == ORIGINAL_FORMAT
    assert len(DIAGNOSTIC_FORMAT) <= len(ORIGINAL_FORMAT)
    replacement = DIAGNOSTIC_FORMAT.ljust(len(ORIGINAL_FORMAT), b'\0')
    result[off:off + len(replacement)] = replacement
    patches.append({'elf_offset': off, 'virtual_address': off + 0x10000,
                    'before': ORIGINAL_FORMAT.hex(), 'after': replacement.hex(),
                    'purpose': 'Unsigned byte-capacity diagnostic and explicit baseline gate label'})
    allowed = {offset for p in patches for offset in range(p['elf_offset'], p['elf_offset'] + len(bytes.fromhex(p['after'])))}
    actual = [i for i, (a, b) in enumerate(zip(original, result)) if a != b]
    assert set(actual) <= allowed and len(result) == len(original)
    assert max(allowed) < 843832, 'Every patch must be in the original first PT_LOAD'
    assert result[0x36198:0x361AC].hex() == '38000180e8810078780007c67fa40040419d00bc'
    assert result[0x362B4:0x362E4] == original[0x362B4:0x362E4], 'False-output/return sequence must stay stock'
    return bytes(result), patches, actual


def main():
    assert sys.flags.optimize == 0
    assert base.sha((ROOT / 'tools/build_hdd2tb_p1.py').read_bytes()) == P1_BUILDER_SHA
    for tool, digest in base.TOOL_PINS.items():
        assert base.sha(tool.read_bytes()) == digest
    WORK.mkdir(parents=True, exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)
    original = base.SOURCE.read_bytes()
    assert base.sha(original) == base.SOURCE_SHA
    entries = {e['id']: e['data'] for e in base.pup_entries(original)}
    assert base.rebuild_pup(original, {}) == original
    update, spkg = base.tar_members(entries[0x300]), base.tar_members(entries[0x501])
    raw_pkg = update['CORE_OS_PACKAGE.pkg']
    for ident, name, blob in ((0x300, 'CORE_OS_PACKAGE.pkg', raw_pkg),
                              (0x501, 'CORE_OS_PACKAGE.pkg.spkg_hdr.1', spkg['CORE_OS_PACKAGE.pkg.spkg_hdr.1'])):
        assert base.replace_tar(entries[ident], name, blob) == entries[ident]
    info0, info1, content = base.package_parts(raw_pkg)
    files = dict(base.pkg_reader.cosunpkg_files(content))
    assert len(files) == 25
    original_self = files['emer_init.self']
    (WORK / 'original.self').write_bytes(original_self)
    base.decode(WORK / 'original.self', WORK / 'original.elf')
    old_elf = (WORK / 'original.elf').read_bytes()
    target, patches, changed = patched_elf(old_elf)
    (WORK / 'patched.elf').write_bytes(target)
    for label in ('control', 'patched'):
        source_elf = WORK / ('original.elf' if label == 'control' else 'patched.elf')
        base.run([base.SCETOOL, '-0', 'SELF', '-1', 'TRUE', '-s', 'TRUE', '-7', 'TRUE',
                  '-t', WORK / 'original.self', '-e', source_elf, WORK / f'{label}-native.self'],
                 WORK / f'{label}-native.log')
    original_stream = base.compressed_code(original_self)
    control_stream = base.compressed_code((WORK / 'control-native.self').read_bytes())
    assert control_stream == original_stream
    assert base.focused_self(original_self, control_stream, old_elf, old_elf) == original_self
    native_stream = base.compressed_code((WORK / 'patched-native.self').read_bytes())
    clear, start, end, _ = base.self_plain(original_self)
    section = start + 96
    available = base.number(clear, section + 48, 8) - base.number(clear, section, 8)
    compressor = {'method': 'native scetool default', 'native_stream_size': len(native_stream),
                  'available_slot_size': available}
    stream = native_stream
    if len(stream) > available:
        # Standard zlib-wrapped DEFLATE, decoded independently by native scetool.
        # Different compression is permitted only inside the same existing slot.
        code_size = len(zlib.decompress(original_stream))
        encoder = zlib.compressobj(9, zlib.DEFLATED, 15, 8, zlib.Z_DEFAULT_STRATEGY)
        stream = encoder.compress(target[:code_size]) + encoder.flush()
        compressor.update({'method': 'Python zlib DEFLATE, level9/wbits15/memLevel8/default strategy',
                           'runtime_version': zlib.ZLIB_RUNTIME_VERSION})
    compressor['selected_stream_size'] = len(stream)
    assert len(stream) <= available
    assert zlib.decompress(stream) == target[:len(zlib.decompress(original_stream))]
    candidate_self = base.focused_self(original_self, stream, old_elf, target)
    (WORK / 'candidate.self').write_bytes(candidate_self)
    base.decode(WORK / 'candidate.self', WORK / 'candidate-python.elf')
    base.run([base.SCETOOL, '-d', WORK / 'candidate.self', WORK / 'candidate-native.elf'],
             WORK / 'candidate-native-decode.log')
    assert (WORK / 'candidate-native.elf').read_bytes() == (WORK / 'candidate-python.elf').read_bytes() == target
    matches = []
    for i in range(base.pkg_reader.be32(content, 4)):
        at = 16 + 48 * i
        if content[at + 16:at + 48].rstrip(b'\0') == b'emer_init.self':
            matches.append((base.pkg_reader.be64(content, at), base.pkg_reader.be64(content, at + 8)))
    assert len(matches) == 1
    offset, size = matches[0]
    assert size == len(original_self) == len(candidate_self)
    new_content = bytearray(content)
    new_content[offset:offset + size] = candidate_self
    assert new_content[:offset] == content[:offset] and new_content[offset + size:] == content[offset + size:]
    native_control, _ = base.native_pkg(info0, info1, content, WORK / 'control-pkg')
    assert base.template_pkg(raw_pkg, native_control) == raw_pkg
    native_candidate, _ = base.native_pkg(info0, info1, new_content, WORK / 'candidate-pkg')
    candidate_pkg = base.template_pkg(raw_pkg, native_candidate)
    pkg_path = WORK / 'CORE_OS_PACKAGE.pkg'
    pkg_path.write_bytes(candidate_pkg)
    base.run([base.SPKGTOOL, pkg_path], WORK / 'native-spkg.log')
    candidate_spkg = Path(str(pkg_path) + '.spkg_hdr.1').read_bytes()
    assert base.package_parts(candidate_pkg)[2] == new_content
    result = base.rebuild_pup(original, {
        0x300: base.replace_tar(entries[0x300], 'CORE_OS_PACKAGE.pkg', candidate_pkg),
        0x501: base.replace_tar(entries[0x501], 'CORE_OS_PACKAGE.pkg.spkg_hdr.1', candidate_spkg),
    })
    path = DEST / 'PS3/UPDATE/PS3UPDAT.PUP'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result)
    assert base.sha(base.SOURCE.read_bytes()) == base.SOURCE_SHA
    manifest = {
        'candidate': 'HDD2TB-P2D', 'stage': 'software-built; independent final review pending; hardware untested',
        'purpose': 'On-screen unsigned byte-capacity and executing-image diagnostic; not 2TB support',
        'source_sha256': base.SOURCE_SHA, 'candidate_sha256': base.sha(result),
        'candidate_md5': hashlib.md5(result).hexdigest(), 'candidate_size': len(result),
        'original_elf_sha256': base.ELF_SHA, 'patched_elf_sha256': base.sha(target),
        'self_sha256': base.sha(candidate_self), 'patches': patches, 'changed_elf_byte_offsets': changed,
        'gate': {'instruction': '38000180', 'threshold_bytes': 0x180 << 32,
                 'stock_baseline_admission_and_return_preserved': True,
                 'p1_1984_gib_admission_not_retained': True},
        'diagnostic': {'format': DIAGNOSTIC_FORMAT[:-1].decode(), 'buffer_va': '0x14d610',
                       'buffer_limit_bytes': 1024, 'normal_and_safe_mode_unsupported_cases_redirected': True,
                       'languages': 'English diagnostic for these cases regardless of selected UI language'},
        'compression': compressor,
        'controls': {'pup_no_change_byte_identical': True, 'tar_no_change_byte_identical': True,
                     'native_no_change_compression_byte_identical': True, 'focused_self_no_change_byte_identical': True,
                     'template_pkg_no_change_byte_identical': True, 'two_full_self_decoders_match': True},
        'self_treatment': {'layout_and_length_preserved': True, 'unchanged_ciphertext_sections_preserved': True,
                          'metadata_keys_ivs_preserved': True, 'existing_invalid_ecdsa_signature_retained': True},
        'pkg_treatment': {'original_info1_preserved': True, 'layout_keys_ivs_preserved': True,
                         'ecdsa_regenerated': True, 'independent_signature_verification_pending': True},
        'tools': {str(p.relative_to(ROOT)): base.sha(p.read_bytes())
                  for p in (base.SCETOOL, base.NEWPKG, base.SPKGTOOL, Path(__file__), ROOT / 'tools/build_hdd2tb_p1.py')},
        'changed_pup_entries': ['0x300/update_files.tar', '0x501/spkg_hdr.tar'],
        'coreos_files': [{'name': name, 'before_sha256': base.sha(blob),
                         'after_sha256': base.sha(candidate_self if name == 'emer_init.self' else blob)}
                        for name, blob in files.items()],
        'hardware_tested': False, 'stable_storage_support': False,
    }
    base.save_json(DEST / 'build-manifest.json', manifest)
    (DEST / 'SHA256SUMS.txt').write_text(base.sha(result).upper() + '  PS3/UPDATE/PS3UPDAT.PUP\n', encoding='ascii')
    print(json.dumps({k: manifest[k] for k in ('candidate', 'candidate_sha256', 'candidate_md5', 'candidate_size',
                                             'patched_elf_sha256', 'compression')}, indent=2))


if __name__ == '__main__':
    main()
