"""Prepare fixed Disk4 post-AK read-only capture from the reviewed AJ adapter."""
import ast
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
O = R / 'analysis/dev006/pny-post-ak-preservation-v1'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def put(path, text):
    with path.open('x', encoding='utf8') as f:
        f.write(text)


def main():
    obs = R / 'observations/HW002AL'
    preflight = json.loads((obs / 'read-only-preflight-v1/result.json').read_text('utf8'))
    assert preflight['completed'] and preflight['DiskNumber'] == 4
    core = R / 'analysis/dev006/pny-fixture-preservation/Core/bin/Release/net10.0/PS3HddTool.Core.dll'
    assert sha(core) == 'a5eb4f05798b1581487b6030a34e127b3f9057e0330dabc1d80cafec6c4fbfa5'
    O.mkdir(exist_ok=False)
    parent = R / 'analysis/dev006/pny-current-preservation-v1/Program.cs'
    source = parent.read_text('utf8').replace('HW002AJ', 'HW002AL').replace(
        'pny-preservation-current-v1', 'pny-preservation-post-ak-v1')
    needle = 'volumeFragments=fs.Superblock.TotalFragments,'
    assert source.count(needle) == 1
    source = source.replace(needle,
        'volumeFragments=BinaryPrimitives.ReadInt64BigEndian(fs.RawSuperblockData!.AsSpan(0x438)),\n'
        '                nativeSizeByteOffset=0x438,legacyVolumeFragments32=fs.Superblock.TotalFragments,')
    put(O / 'Program.cs', source)
    project = R / 'analysis/dev006/pny-current-preservation-v1/CurrentPnyPreservation.csproj'
    put(O / 'PostAkPnyPreservation.csproj', project.read_text('utf8'))
    parent_wrapper = R / 'tools/Capture-HW002AJ-CurrentPny.ps1'
    wrapper = parent_wrapper.read_text('utf8').replace('HW002AJ', 'HW002AL').replace(
        'pny-preservation-current-v1', 'pny-preservation-post-ak-v1').replace(
        'pny-current-preservation-v1', 'pny-post-ak-preservation-v1').replace(
        'CurrentPnyPreservation.dll', 'PostAkPnyPreservation.dll')
    put(R / 'tools/Capture-HW002AL-PostAkPny.ps1', wrapper)
    parent_seal = R / 'analysis/dev006/seal_current_pny_capture.py'
    seal = parent_seal.read_text('utf8').replace(
        'controlled-recovery-preparation-ready-checkpoint.json', 'recovery-v2-preparation-ready-checkpoint.json')
    for a, b in [
        ('HW002AJ', 'HW002AL'), ('hw002aj', 'hw002al'),
        ('pny-current-preservation-v1', 'pny-post-ak-preservation-v1'),
        ('prepare_current_pny_capture.py', 'prepare_post_ak_pny_capture.py'),
        ('seal_current_pny_capture.py', 'seal_post_ak_pny_capture.py'),
        ('Capture-HW002AL-CurrentPny.ps1', 'Capture-HW002AL-PostAkPny.ps1')]:
        seal = seal.replace(a, b)
    seal = seal.replace("    assert 'positioned!=first' in source",
        "    assert 'positioned!=first' in source\n"
        "    assert 'ReadInt64BigEndian(fs.RawSuperblockData!.AsSpan(0x438))' in source\n"
        "    assert 'nativeSizeByteOffset=0x438' in source")
    ast.parse(seal)
    put(R / 'analysis/dev006/seal_post_ak_pny_capture.py', seal)
    put(O / 'source-provenance.json', json.dumps({
        'parent': str(parent.relative_to(R)), 'parent_sha256': sha(parent),
        'source_sha256': sha(O / 'Program.cs'), 'private_Core_DLL_sha256': sha(core),
        'wrapper_parent': str(parent_wrapper.relative_to(R)), 'wrapper_parent_sha256': sha(parent_wrapper),
        'sealer_parent': str(parent_seal.relative_to(R)), 'sealer_parent_sha256': sha(parent_seal),
        'changes': ['AJ to AL namespace', 'new post-AK session and binary paths',
                    'Correct geometry report to native64bit UFS2 size at0x438; retain legacy32bit field separately'],
        'parents_or_Core_rebuilt_or_modified': False, 'physical_writer_present': False}, indent=2) + '\n')
    print(json.dumps({'post_AK_PNY_readonly_sources_prepared': True, 'disk': 4, 'physical_IO': False}))


if __name__ == '__main__':
    main()
