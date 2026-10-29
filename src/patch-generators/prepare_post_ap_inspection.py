"""Prepare a new read-only AP post-checker diagnostic and independent verifier."""
import ast
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / 'observations/HW002AP'
O = R / 'analysis/dev006/pny-post-counter-inspection-v1'


def put(path, text):
    with path.open('x', encoding='utf8') as f:
        f.write(text)


def main():
    assert json.loads((A / 'read-only-preflight-v1/result.json').read_text('utf8'))['completed']
    parent = R / 'analysis/dev006/pny-post-recovery-inspection-v1'
    O.mkdir(exist_ok=False)
    program = (parent / 'Program.cs').read_text('utf8').replace('HW002AO', 'HW002AP').replace(
        'pny-post-recovery-diagnostic-v1', 'pny-post-counter-diagnostic-v1')
    put(O / 'Program.cs', program)
    put(O / 'PostCounterPnyDiagnostic.csproj', (parent / 'PostRecoveryPnyDiagnostic.csproj').read_text('utf8'))
    wrapper = (R / 'tools/Inspect-HW002AO-PostRecoveryPny.ps1').read_text('utf8')
    for old, new in [('HW002AO', 'HW002AP'), ('PostRecovery', 'PostCounter'),
                     ('pny-post-recovery-inspection-v1', 'pny-post-counter-inspection-v1'),
                     ('pny-post-recovery-diagnostic-v1', 'pny-post-counter-diagnostic-v1')]:
        wrapper = wrapper.replace(old, new)
    put(R / 'tools/Inspect-HW002AP-PostCounterPny.ps1', wrapper)
    verifier = (R / 'analysis/dev006/verify_ao_inspection.py').read_text('utf8')
    verifier = verifier.replace('HW002AO', 'HW002AP').replace(
        'pny-post-recovery-diagnostic-v1', 'pny-post-counter-diagnostic-v1')
    verifier = verifier.replace('observations/HW002AM/private/pny-post-boot-diagnostic-v1/controls.json',
                                'observations/HW002AO/private/pny-post-recovery-diagnostic-v1/controls.json')
    verifier = verifier.replace('controls_equal_AM', 'controls_equal_AO').replace(
        'whole_fixed_controls_equal_AM', 'whole_fixed_controls_equal_AO')
    ast.parse(verifier)
    put(R / 'analysis/dev006/verify_post_ap_inspection.py', verifier)
    sealer = (R / 'analysis/dev006/seal_ao_inspection.py').read_text('utf8')
    for old, new in [
        ('HW002AO', 'HW002AP'), ('PostRecovery', 'PostCounter'),
        ('pny-post-recovery-inspection-v1', 'pny-post-counter-inspection-v1'),
        ('pny-post-recovery-diagnostic-v1', 'pny-post-counter-diagnostic-v1'),
        ('hw002an-complete-hw002ao-ready-checkpoint.json', 'hw002ap-injected-native-ready-checkpoint.json'),
        ('record_hw002ao_report.py', 'record_ap_native_report.py'),
        ('prepare_ao_inspection.py', 'prepare_post_ap_inspection.py'),
        ('seal_ao_inspection.py', 'seal_post_ap_inspection.py'),
        ('verify_ao_inspection.py', 'verify_post_ap_inspection.py'),
    ]:
        sealer = sealer.replace(old, new)
    # The sealer derives expected code from AM, so its AM->AP session replacement
    # must name the new post-counter session rather than the AO session.
    sealer = sealer.replace("'pny-post-boot-diagnostic-v1', 'pny-post-recovery-diagnostic-v1'",
                             "'pny-post-boot-diagnostic-v1', 'pny-post-counter-diagnostic-v1'")
    ast.parse(sealer)
    put(R / 'analysis/dev006/seal_post_ap_inspection.py', sealer)
    put(O / 'source-provenance.json', json.dumps({
        'parent': (parent / 'Program.cs').relative_to(R).as_posix(),
        'changes': 'AP/new session/assembly only; exact frozen read-only algorithm',
        'verifier_baseline': 'AO pre-injection controls; actual counts/orphan set, no assumed correction',
        'physical_IO_or_key_access': False,
    }, indent=2) + '\n')
    print(json.dumps({'AP_post_native_inspection_prepared': True, 'physical_IO': False}))


if __name__ == '__main__':
    main()
