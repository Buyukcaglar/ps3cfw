"""Prepare fresh post-native AP conservative preservation and AO comparison."""
import ast
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / 'observations/HW002AP'
O = R / 'analysis/dev006/pny-post-counter-allocation-v1'


def put(path, text):
    with path.open('x', encoding='utf8') as f:
        f.write(text)


def transform(text):
    for old, new in [
        ('HW002AO', 'HW002AP'), ('pny-post-recovery-allocation-v1', 'pny-post-counter-allocation-v1'),
        ('pny-post-recovery-diagnostic-v1', 'pny-post-counter-diagnostic-v1'),
        ('AllocationPostRecoveryPny', 'AllocationPostCounterPny'),
        ('prepare_ao_preservation.py', 'prepare_post_ap_preservation.py'),
        ('verify_ao_preservation.py', 'verify_post_ap_preservation.py'),
        ('seal_ao_preservation.py', 'seal_post_ap_preservation.py'),
    ]:
        text = text.replace(old, new)
    return text


def main():
    assert json.loads((A / 'inspection-independent-verification.json').read_text('utf8'))['passed']
    parent = R / 'analysis/dev006/pny-post-recovery-allocation-v1'
    O.mkdir(exist_ok=False)
    put(O / 'Program.cs', transform((parent / 'Program.cs').read_text('utf8')))
    with (O / 'AllocationPreserver.cs').open('xb') as f:
        f.write((parent / 'AllocationPreserver.cs').read_bytes())
    put(O / 'AllocationPostCounterPny.csproj', (parent / 'AllocationPostRecoveryPny.csproj').read_text('utf8'))
    put(R / 'tools/Preserve-HW002AP-AllocatedPny.ps1',
        transform((R / 'tools/Preserve-HW002AO-AllocatedPny.ps1').read_text('utf8')))
    for old, new in [('verify_ao_preservation.py', 'verify_post_ap_preservation.py'),
                     ('seal_ao_preservation.py', 'seal_post_ap_preservation.py')]:
        source = transform((R / 'analysis/dev006' / old).read_text('utf8'))
        ast.parse(source)
        put(R / 'analysis/dev006' / new, source)
    compare = (R / 'analysis/dev006/compare_ao_metadata.py').read_text('utf8')
    compare = compare.replace('HW002AO', 'HW002__NEW').replace('HW002AM', 'HW002AO').replace('HW002__NEW', 'HW002AP')
    compare = compare.replace('pny-post-recovery-diagnostic-v1', 'pny-post-counter-diagnostic-v1')
    compare = compare.replace('pny-post-boot-diagnostic-v1', 'pny-post-recovery-diagnostic-v1')
    compare = compare.replace('Owner-reported ordinary P13 boot/shutdown after exact tail-sector restoration, no checker/update',
                              'Owner-reported P13 Restore File System route after one-count summary mismatch')
    ast.parse(compare)
    put(R / 'analysis/dev006/compare_ap_metadata.py', compare)
    put(O / 'source-provenance.json', json.dumps({
        'parent_program': (parent / 'Program.cs').relative_to(R).as_posix(),
        'coverage_byte_identical_to_AO': True,
        'changes': 'AP/session/assembly namespaces only; independent actual outcomes, AO baseline',
        'physical_IO_or_key_access': False,
    }, indent=2)+'\n')
    print(json.dumps({'AP_post_native_conservative_preservation_prepared': True, 'physical_IO': False}))


if __name__ == '__main__':
    main()
