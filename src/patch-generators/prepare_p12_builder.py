"""Prepare isolated P11-template P12 builder and separate-parser package audit."""
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def adapt(source,target,changes):
    text=(R/source).read_text('utf8')
    for old,new in changes:
        if old not in text:raise ValueError('Missing template contract: '+old)
        text=text.replace(old,new)
    with (R/target).open('x',encoding='utf8') as stream:stream.write(text)
    return {'parent':source,'parent_sha256':hashlib.sha256((R/source).read_bytes()).hexdigest(),
        'target':target,'changes':changes,'parent_modified':False}


def main():
    builder=adapt('tools/build_hdd2tb_p11.py','tools/build_hdd2tb_p12.py',[
        ('P10 plus bounded missing-summary pre-flush rejection','P11 plus bounded summary-read/setup-abort guards'),
        ("PARENT='885af0721b448e329a1d8528824b00fc607b8d7f3332ce6e79f03bfcd95a636d'",
         "PARENT='d299aad533a12ff8a7a6e5bc0e20093977de18e7e9eef0aac7cc58b4aa065552'"),
        ('candidates/HDD2TB-P10/PS3/UPDATE/PS3UPDAT.PUP','candidates/HDD2TB-P11/PS3/UPDATE/PS3UPDAT.PUP'),
        ('92230e04459b7bf74193a4c38ae68b6c45bee896bfdb5c657bcf9f6ab7937e26','b5e140fe5ce114e2b25924b30cfb77b6cb956741ff45f91ccd0a1adf873932b6'),
        ('daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688','904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e'),
        ('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf','analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf'),
        ('analysis/dev006/p11-summary-guard-model-v1/result.json','analysis/dev006/p12-setup-abort-model-v1/result.json'),
        ("'candidate':'HDD2TB-P11'","'candidate':'HDD2TB-P12'"),
        ('Reject dirty primary superblock flush before writes when its positive-size summary buffer is missing; retain dirty byte and clear I/O-success flag; P10 guards/storage/observer/budget retained',
         'Abort on summary read error before CONTINUE/later allocations; discard uncommitted setup-buffer dirty state before OOM cleanup; P11 guards/storage/observer/budget retained'),
        ('analysis/dev006/prepare_p11_summary_guard.py','analysis/dev006/prepare_p12_setup_abort_guard.py'),
        ('analysis/dev006/p11-summary-guard-v2/manifest.json','analysis/dev006/p12-setup-abort-v1/manifest.json'),
        ('analysis/dev006/model_p11_summary_guard.py','analysis/dev006/model_p12_setup_abort.py'),
        ('analysis/dev006/p11-summary-delta/review.json','analysis/dev006/p12-setup-delta/review.json'),
        ("ROOT/'candidates/HDD2TB-P11'","ROOT/'candidates/HDD2TB-P12'")])
    audit=adapt('analysis/dev006/audit_p11.py','analysis/dev006/audit_p12.py',[
        ('Separate-parser P11','Separate-parser P12'),("O=ROOT/'analysis/p11-review'","O=ROOT/'analysis/p12-review'"),
        ("a=(ROOT/'candidates/HDD2TB-P10/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P11/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()",
         "a=(ROOT/'candidates/HDD2TB-P11/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();b=(ROOT/'candidates/HDD2TB-P12/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()"),
        ('885af0721b448e329a1d8528824b00fc607b8d7f3332ce6e79f03bfcd95a636d','d299aad533a12ff8a7a6e5bc0e20093977de18e7e9eef0aac7cc58b4aa065552'),
        ('candidates/HDD2TB-P11/build-manifest.json','candidates/HDD2TB-P12/build-manifest.json'),
        ('analysis/candidate-p11-v2/PS3/UPDATE/PS3UPDAT.PUP','analysis/candidate-p12-v2/PS3/UPDATE/PS3UPDAT.PUP'),
        ("audit(au[PACKAGE],'P10 flash','PKG'),audit(bu[PACKAGE],'P11 flash','PKG')",
         "audit(au[PACKAGE],'P11 flash','PKG'),audit(bu[PACKAGE],'P12 flash','PKG')"),
        ("'P11 header'","'P12 header'"),
        ("audit(old,'P10 utility','SELF'),audit(new,'P11 utility','SELF')",
         "audit(old,'P11 utility','SELF'),audit(new,'P12 utility','SELF')"),
        ("oldelf=common.decode_both(old,'utility-P10');newelf=common.decode_both(new,'utility-P11')",
         "oldelf=common.decode_both(old,'utility-P11');newelf=common.decode_both(new,'utility-P12')"),
        ('daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688','904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e'),
        ('analysis/dev006/p11-summary-guard-v2/manifest.json','analysis/dev006/p12-setup-abort-v1/manifest.json'),
        ('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf','analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf'),
        ('for at in (0x155c0,):','for at in (0x1f754,0x1fb6c):'),
        ('y[0][0x26540:0x2658c]=x[0][0x26540:0x2658c]','y[0][0x265c0:0x26600]=x[0][0x265c0:0x26600]'),
        ('analysis/dev006/p11-summary-guard-model-v1/result.json','analysis/dev006/p12-setup-abort-model-v1/result.json'),
        ('P10_sysconf_unchanged','P11_sysconf_unchanged'),
        ('P10_loaded_bytes_preserved_except_one_hook_and76_helper_bytes_four_base_pairs',
         'P11_loaded_bytes_preserved_except_two_hooks_and64_helper_bytes_four_base_pairs'),
        ('P10_relocations_and_program_headers_exactly_preserved','P11_relocations_and_program_headers_exactly_preserved')])
    with (R/'analysis/dev006/p12-builder-provenance.json').open('x',encoding='utf8') as stream:
        json.dump({'builder':builder,'separate_parser_audit':audit},stream,indent=2);stream.write('\n')
    print('Separate P12 builder/audit sources prepared; prior sources unchanged.')


if __name__=='__main__':main()
