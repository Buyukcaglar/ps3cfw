"""Prepare isolated P10-template P11 packaging and separate-parser audit sources."""
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def adapt(source,destination,changes):
    data=(R/source).read_text('utf8')
    for old,new in changes:
        if old not in data:raise ValueError('Missing template contract: '+old)
        data=data.replace(old,new)
    with (R/destination).open('x',encoding='utf8') as stream:stream.write(data)
    return {'source':source,'source_sha256':hashlib.sha256((R/source).read_bytes()).hexdigest(),
            'destination':destination,'changes':changes,'parent_modified':False}


def main():
    builder=adapt('tools/build_hdd2tb_p10.py','tools/build_hdd2tb_p11.py',[
        ('P9 plus bounded block-writer seek-failure stops','P10 plus bounded missing-summary pre-flush rejection'),
        ("PARENT='d5cb8678dedd18d6b232549c187df8ea154f804fd9c6edffa1e39da9d3640730'",
         "PARENT='885af0721b448e329a1d8528824b00fc607b8d7f3332ce6e79f03bfcd95a636d'"),
        ('candidates/HDD2TB-P9/PS3/UPDATE/PS3UPDAT.PUP','candidates/HDD2TB-P10/PS3/UPDATE/PS3UPDAT.PUP'),
        ('cf7852f4f5c1a5ae333c64ffaee3d8d52252a4b156a85add5672b1afee65250c','92230e04459b7bf74193a4c38ae68b6c45bee896bfdb5c657bcf9f6ab7937e26'),
        ('1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2','daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688'),
        ('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf','analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf'),
        ('analysis/dev006/p10-seek-guard-model-v1/result.json','analysis/dev006/p11-summary-guard-model-v1/result.json'),
        ("'candidate':'HDD2TB-P10'","'candidate':'HDD2TB-P11'"),
        ('Stop further block writes after any failed seek and retain I/O-failure flag; P9 storage/observer/budget retained',
         'Reject dirty primary superblock flush before writes when its positive-size summary buffer is missing; retain dirty byte and clear I/O-success flag; P10 guards/storage/observer/budget retained'),
        ('analysis/dev006/prepare_p10_seek_guard.py','analysis/dev006/prepare_p11_summary_guard.py'),
        ('analysis/dev006/p10-seek-guard-v1/manifest.json','analysis/dev006/p11-summary-guard-v2/manifest.json'),
        ('analysis/dev006/model_p10_seek_guard.py','analysis/dev006/model_p11_summary_guard.py'),
        ('analysis/dev006/p10-seek-delta/review.json','analysis/dev006/p11-summary-delta/review.json'),
        ("ROOT/'candidates/HDD2TB-P10'","ROOT/'candidates/HDD2TB-P11'")])
    audit=adapt('analysis/dev006/audit_p10.py','analysis/dev006/audit_p11.py',[
        ('Separate-parser P10','Separate-parser P11'),("O=ROOT/'analysis/p10-review'","O=ROOT/'analysis/p11-review'"),
        ("a=(ROOT/'candidates/HDD2TB-P9/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P10/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()",
         "a=(ROOT/'candidates/HDD2TB-P10/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P11/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()"),
        ('d5cb8678dedd18d6b232549c187df8ea154f804fd9c6edffa1e39da9d3640730','885af0721b448e329a1d8528824b00fc607b8d7f3332ce6e79f03bfcd95a636d'),
        ('candidates/HDD2TB-P10/build-manifest.json','candidates/HDD2TB-P11/build-manifest.json'),
        ('analysis/candidate-p10-v2/PS3/UPDATE/PS3UPDAT.PUP','analysis/candidate-p11-v2/PS3/UPDATE/PS3UPDAT.PUP'),
        ("audit(au[PACKAGE],'P10 flash','PKG'),audit(bu[PACKAGE],'P10 flash','PKG')",
         "audit(au[PACKAGE],'P10 flash','PKG'),audit(bu[PACKAGE],'P11 flash','PKG')"),
        ("'P10 header'","'P11 header'"),
        ("audit(old,'P10 utility','SELF'),audit(new,'P10 utility','SELF')",
         "audit(old,'P10 utility','SELF'),audit(new,'P11 utility','SELF')"),
        ("oldelf=common.decode_both(old,'utility-P9');newelf=common.decode_both(new,'utility-P10')",
         "oldelf=common.decode_both(old,'utility-P10');newelf=common.decode_both(new,'utility-P11')"),
        ('1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2','daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688'),
        ('analysis/dev006/p10-seek-guard-v1/manifest.json','analysis/dev006/p11-summary-guard-v2/manifest.json'),
        ('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf','analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf'),
        ('for at in (0x14ad8,0x14ae8,0x14a28):','for at in (0x155c0,):'),
        ('y[0][0x26500:0x26520]=x[0][0x26500:0x26520]','y[0][0x26540:0x2658c]=x[0][0x26540:0x2658c]'),
        ('analysis/dev006/p10-seek-guard-model-v1/result.json','analysis/dev006/p11-summary-guard-model-v1/result.json'),
        ('P9_sysconf_unchanged','P10_sysconf_unchanged'),
        ('P9_loaded_bytes_preserved_except_three_hooks_and32_helper_bytes_four_base_pairs',
         'P10_loaded_bytes_preserved_except_one_hook_and76_helper_bytes_four_base_pairs'),
        ('P9_relocations_and_program_headers_exactly_preserved','P10_relocations_and_program_headers_exactly_preserved')])
    with (R/'analysis/dev006/p11-builder-provenance.json').open('x',encoding='utf8') as stream:
        json.dump({'builder':builder,'separate_parser_audit':audit},stream,indent=2);stream.write('\n')
    print('Separate P11 builder/audit prepared; previous sources unchanged.')


if __name__=='__main__':main()
