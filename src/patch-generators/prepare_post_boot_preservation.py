"""Prepare a fresh conservative AM archive and independent coverage verifier."""
import ast
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[2]
A=R/'observations/HW002AM'
O=R/'analysis/dev006/pny-post-boot-allocation-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path,text):
    with path.open('x',encoding='utf8') as f:f.write(text)


def main():
    verified=json.loads((A/'inspection-independent-verification.json').read_text('utf8'))
    assert verified['passed']
    parent=R/'analysis/dev006/pny-allocation-preservation-v1'
    O.mkdir(exist_ok=False)
    source=(parent/'Program.cs').read_text('utf8').replace('HW002AL','HW002AM').replace(
        'pny-allocation-preservation-v1','pny-post-boot-allocation-v1')
    put(O/'Program.cs',source)
    put(O/'AllocationPreserver.cs',(parent/'AllocationPreserver.cs').read_text('utf8'))
    put(O/'AllocationPostBootPny.csproj',(parent/'AllocationPnyPreservation.csproj').read_text('utf8'))
    wrapper_parent=R/'tools/Preserve-HW002AL-AllocatedPny.ps1'
    wrapper=wrapper_parent.read_text('utf8').replace('HW002AL','HW002AM').replace(
        'pny-allocation-preservation-v1','pny-post-boot-allocation-v1').replace(
        'AllocationPnyPreservation.dll','AllocationPostBootPny.dll')
    put(R/'tools/Preserve-HW002AM-AllocatedPny.ps1',wrapper)
    verifier_parent=R/'analysis/dev006/verify_allocation_preservation.py'
    verifier=verifier_parent.read_text('utf8').replace('HW002AL','HW002AM').replace(
        'pny-allocation-preservation-v1','pny-post-boot-allocation-v1').replace(
        'pny-post-ak-diagnostic-v1','pny-post-boot-diagnostic-v1')
    for old,new in [
        ("assert allocated_inodes == m['Geometry']['allocatedInodes'] == 4820",
         "assert allocated_inodes == m['Geometry']['allocatedInodes']"),
        ("assert payload_fragments == m['Geometry']['nonreservedFragments'] == 137510",
         "assert payload_fragments == m['Geometry']['nonreservedFragments']"),
        ("assert (records, covered, archive_bytes) == (m['Records'],m['CoveredBytes'],m['ArchiveBytes']) == (9239,3144794112,3145200628)",
         "assert (records, covered, archive_bytes) == (m['Records'],m['CoveredBytes'],m['ArchiveBytes'])\n"
         "    assert 0 < covered < 16*1024**3"),
        ("assert digest.hexdigest() == m['ArchiveSha256'] == '2ce62545237f535b26c472f52eaa3255f2ab7edb623f3889bd8ff1b759fea8e7'",
         "assert digest.hexdigest() == m['ArchiveSha256']")]:
        assert old in verifier,old
        verifier=verifier.replace(old,new)
    ast.parse(verifier)
    put(R/'analysis/dev006/verify_post_boot_preservation.py',verifier)
    put(O/'source-provenance.json',json.dumps({
        'parent_program':str((parent/'Program.cs').relative_to(R)),'parent_program_sha256':sha(parent/'Program.cs'),
        'parent_coverage':str((parent/'AllocationPreserver.cs').relative_to(R)),
        'parent_coverage_sha256':sha(parent/'AllocationPreserver.cs'),
        'wrapper_parent':str(wrapper_parent.relative_to(R)),'wrapper_parent_sha256':sha(wrapper_parent),
        'verifier_parent':str(verifier_parent.relative_to(R)),'verifier_parent_sha256':sha(verifier_parent),
        'changes':['New AM namespace and session/binary paths','Coverage and physical readonly adapters unchanged',
                   'Independent verifier derives actual counts/bytes/hash without assuming an unchanged filesystem'],
        'physical_IO_or_key_access':False,'parent_modified':False},indent=2)+'\n')
    print(json.dumps({'AM_conservative_preservation_prepared':True,'physical_IO':False}))


if __name__=='__main__':main()
