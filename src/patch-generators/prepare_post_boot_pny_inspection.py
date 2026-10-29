"""Prepare a fresh AM diagnostic and outcome-independent saved-metadata verifier."""
import ast
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
O = R / 'analysis/dev006/pny-post-boot-inspection-v1'
A = R / 'observations/HW002AM'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def put(path,text):
    with path.open('x',encoding='utf8') as f:
        f.write(text)


def main():
    preflight=json.loads((A/'read-only-preflight-v1/result.json').read_text('utf8'))
    assert preflight['completed'] and preflight['DiskNumber']==4
    O.mkdir(exist_ok=False)
    parent=R/'analysis/dev006/pny-post-ak-inspection-v1/Program.cs'
    source=parent.read_text('utf8').replace('HW002AL','HW002AM').replace('pny-post-ak-diagnostic-v1','pny-post-boot-diagnostic-v1')
    put(O/'Program.cs',source)
    project=R/'analysis/dev006/pny-post-ak-inspection-v1/PostAkPnyDiagnostic.csproj'
    put(O/'PostBootPnyDiagnostic.csproj',project.read_text('utf8'))
    wrapper_parent=R/'tools/Inspect-HW002AL-PostAkPny.ps1'
    wrapper=wrapper_parent.read_text('utf8')
    for old,new in [('HW002AL','HW002AM'),('pny-post-ak-diagnostic-v1','pny-post-boot-diagnostic-v1'),
                    ('pny-post-ak-inspection-v1','pny-post-boot-inspection-v1'),('PostAkPnyDiagnostic.dll','PostBootPnyDiagnostic.dll')]:
        wrapper=wrapper.replace(old,new)
    put(R/'tools/Inspect-HW002AM-PostBootPny.ps1',wrapper)
    verifier_parent=R/'analysis/dev006/verify_post_ak_inspection.py'
    verifier=verifier_parent.read_text('utf8').replace('HW002AL','HW002AM').replace('pny-post-ak-diagnostic-v1','pny-post-boot-diagnostic-v1')
    replacements=[
        ("assert records == inspection['cache_records'] == 11614","assert records == inspection['cache_records']"),
        ("assert payload_bytes == inspection['cache_bytes'] == 110536192","assert payload_bytes == inspection['cache_bytes']"),
        ("assert len(claimed) == 4815","assert len(claimed) == inspection['reachable_nodes']"),
        ("assert len(allocated) == 4820 and orphans == [3, 65734790, 65734795]",
         "assert len(allocated) == inspection['allocated_inode_bits_including_reserved']\n"
         "    assert orphans == sorted(row['inode'] for row in inspection['unreachable_inodes'])"),
        ("    assert not any(get(inode_at(3), 256))","    inode3_zero = not any(get(inode_at(3),256)) if 3 in orphans or 3 in reachable else None"),
        ("'inode3_record_all_zero': True","'inode3_record_all_zero': inode3_zero"),
        ("    assert controls == old_controls","    controls_equal_AL = controls == old_controls"),
        ("'whole_fixed_controls_equal_AJ_and_AK': 2","'whole_fixed_controls_equal_AL': 2 if controls_equal_AL else 0"),
        ("'strict_preservation_archive_produced': False","'strict_preservation_archive_produced': False"),
        ("(R / 'observations/HW002AJ/private/pny-preservation-current-v1/controls.json')",
         "(R / 'observations/HW002AL/private/pny-post-ak-diagnostic-v1/controls.json')")]
    for old,new in replacements:
        assert old in verifier,old
        verifier=verifier.replace(old,new)
    ast.parse(verifier)
    put(R/'analysis/dev006/verify_post_boot_pny_inspection.py',verifier)
    put(O/'source-provenance.json',json.dumps({
        'parent':str(parent.relative_to(R)),'parent_sha256':sha(parent),
        'new_source_sha256':sha(O/'Program.cs'),
        'wrapper_parent':str(wrapper_parent.relative_to(R)),'wrapper_parent_sha256':sha(wrapper_parent),
        'verifier_parent':str(verifier_parent.relative_to(R)),'verifier_parent_sha256':sha(verifier_parent),
        'changes':['AL to AM and new session/binary namespace only for compiled diagnostic',
                   'Independent verifier derives counts/orphan set from actual cached metadata, with no expected unchanged outcome',
                   'Fixed control comparison uses AL baseline; captures differences explicitly'],
        'physical_IO_or_key_access':False,'Core_rebuilt_or_modified':False},indent=2)+'\n')
    print(json.dumps({'AM_readonly_inspection_sources_prepared':True,'disk':4,'physical_IO':False}))


if __name__=='__main__':
    main()
