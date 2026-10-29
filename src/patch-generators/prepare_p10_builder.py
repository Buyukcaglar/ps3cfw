"""Create a separate P9-template P10 packager and separate-parser package audit."""
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]


def adapt(source, destination, changes):
    text = (R / source).read_text('utf8')
    for old, new in changes:
        if old not in text:
            raise ValueError('Missing explicit template contract: ' + old)
        text = text.replace(old, new)
    with (R / destination).open('x', encoding='utf8') as f: f.write(text)
    return {'source': source, 'source_sha256': hashlib.sha256((R / source).read_bytes()).hexdigest(),
            'destination': destination, 'changes': changes, 'prior_source_modified': False}


def main():
    builder = adapt('tools/build_hdd2tb_p9.py', 'tools/build_hdd2tb_p10.py', [
        ('P8 plus bounded checker allocation-failure guards', 'P9 plus bounded block-writer seek-failure stops'),
        ("PARENT='d0260ed27fb2a9fa50b140c7f439ef5653ec231c0fc983fce51e3b054aa1a47a'", "PARENT='d5cb8678dedd18d6b232549c187df8ea154f804fd9c6edffa1e39da9d3640730'"),
        ('candidates/HDD2TB-P8/PS3/UPDATE/PS3UPDAT.PUP', 'candidates/HDD2TB-P9/PS3/UPDATE/PS3UPDAT.PUP'),
        ('5c1b2c1a9b894e6a091869fa30a5254f3191c45c2781485b82d5c73414a82153', 'cf7852f4f5c1a5ae333c64ffaee3d8d52252a4b156a85add5672b1afee65250c'),
        ('b7e65e2dd7d82aa5c9957c2af7a192f475ed26f4140f3ab25ea18866bed53f01', '1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2'),
        ('analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf', 'analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf'),
        ('analysis/dev006/p9-safety-model-v3/result.json', 'analysis/dev006/p10-seek-guard-model-v1/result.json'),
        ("'candidate':'HDD2TB-P9'", "'candidate':'HDD2TB-P10'"),
        ('Bounded checker array-growth failure/overread fix and calloc multiplication-overflow rejection; P8 storage/observer retained',
         'Stop further block writes after any failed seek and retain I/O-failure flag; P9 storage/observer/budget retained'),
        ('analysis/dev006/prepare_p9_safety_v2.py', 'analysis/dev006/prepare_p10_seek_guard.py'),
        ('analysis/dev006/p9-safety-v2/manifest.json', 'analysis/dev006/p10-seek-guard-v1/manifest.json'),
        ('analysis/dev006/model_p9_safety.py', 'analysis/dev006/model_p10_seek_guard.py'),
        ('analysis/dev006/p9-safety-delta/review.json', 'analysis/dev006/p10-seek-delta/review.json'),
        ("ROOT/'candidates/HDD2TB-P9'", "ROOT/'candidates/HDD2TB-P10'")])
    audit = adapt('analysis/dev006/audit_p9.py', 'analysis/dev006/audit_p10.py', [
        ('Separate-parser P9', 'Separate-parser P10'), ("O=ROOT/'analysis/p9-review'", "O=ROOT/'analysis/p10-review'"),
        ("a=(ROOT/'candidates/HDD2TB-P8/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P9/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()",
         "a=(ROOT/'candidates/HDD2TB-P9/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P10/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()"),
        ('d0260ed27fb2a9fa50b140c7f439ef5653ec231c0fc983fce51e3b054aa1a47a', 'd5cb8678dedd18d6b232549c187df8ea154f804fd9c6edffa1e39da9d3640730'),
        ('candidates/HDD2TB-P9/build-manifest.json', 'candidates/HDD2TB-P10/build-manifest.json'),
        ('analysis/candidate-p9-v2/PS3/UPDATE/PS3UPDAT.PUP', 'analysis/candidate-p10-v2/PS3/UPDATE/PS3UPDAT.PUP'),
        ("'P8 flash'", "'P9 flash'"), ("'P9 flash','PKG'", "'P10 flash','PKG'"),
        ("'P9 header'", "'P10 header'"), ("'P8 utility'", "'P9 utility'"),
        ("'P9 utility','SELF'", "'P10 utility','SELF'"),
        ("oldelf=common.decode_both(old,'utility-P8');newelf=common.decode_both(new,'utility-P9')",
         "oldelf=common.decode_both(old,'utility-P9');newelf=common.decode_both(new,'utility-P10')"),
        ('b7e65e2dd7d82aa5c9957c2af7a192f475ed26f4140f3ab25ea18866bed53f01', '1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2'),
        ('analysis/dev006/p9-safety-v2/manifest.json', 'analysis/dev006/p10-seek-guard-v1/manifest.json'),
        ("['output_sha256']", "['elf_sha256']"),
        ('analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf', 'analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf'),
        ('len(after)-len(before)>0', 'len(after)-len(before)>=0'),
        ('for at in (0x16888,0x16894,0xe728):', 'for at in (0x14ad8,0x14ae8,0x14a28):'),
        ('y[0][0x26400:0x264fc]=x[0][0x26400:0x264fc]', 'y[0][0x26500:0x26520]=x[0][0x26500:0x26520]'),
        ('analysis/dev006/p9-safety-model-v3/result.json', 'analysis/dev006/p10-seek-guard-model-v1/result.json'),
        ("model['cases']", "model['case_count']"),
        ('P8_sysconf_unchanged', 'P9_sysconf_unchanged'),
        ('P8_loaded_bytes_preserved_except_three_hooks_and252_helper_bytes_four_base_pairs', 'P9_loaded_bytes_preserved_except_three_hooks_and32_helper_bytes_four_base_pairs'),
        ('P8_relocations_and_program_headers_exactly_preserved', 'P9_relocations_and_program_headers_exactly_preserved')])
    with (R / 'analysis/dev006/p10-builder-provenance.json').open('x', encoding='utf8') as f:
        json.dump({'builder': builder, 'separate_parser_audit': audit}, f, indent=2)
        f.write('\n')
    print('P10 packager and separate-parser audit prepared; prior builders unchanged.')


if __name__ == '__main__':
    main()
