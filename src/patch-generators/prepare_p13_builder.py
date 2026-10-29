"""Instantiate isolated P13 builder and separate package parser without old writers."""
import ast
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
PURPOSE = 'Stop the block reader on negative initial, retry or per-sector seek results; clear existing IO-success flag and return nonzero through the original epilogue; P12 guards/storage/observer/budget retained'


def adapt(parent, target, changes):
    source = (R / parent).read_text('utf8')
    for old, new in changes:
        assert old in source, old
        source = source.replace(old, new)
    ast.parse(source)
    with (R / target).open('x', encoding='utf8') as stream:
        stream.write(source)
    return {'parent': parent, 'parent_sha256': hashlib.sha256((R / parent).read_bytes()).hexdigest(),
            'target': target, 'target_sha256': hashlib.sha256((R / target).read_bytes()).hexdigest(),
            'changes': changes, 'AST_passed': True, 'parent_modified': False}


def main():
    builder = adapt('tools/build_hdd2tb_p12.py', 'tools/build_hdd2tb_p13.py', [
        ('P11 plus bounded summary-read/setup-abort guards', 'P12 plus bounded reader negative-seek guards'),
        ("PARENT='d299aad533a12ff8a7a6e5bc0e20093977de18e7e9eef0aac7cc58b4aa065552'",
         "PARENT='7fb5d6e57ef53654f336745dbc9463c8e6b2cded03b05cdbeb80e5125215fb7c'"),
        ('candidates/HDD2TB-P11/PS3/UPDATE/PS3UPDAT.PUP', 'candidates/HDD2TB-P12/PS3/UPDATE/PS3UPDAT.PUP'),
        ('b5e140fe5ce114e2b25924b30cfb77b6cb956741ff45f91ccd0a1adf873932b6', 'eb38afbb59179553ba3055d19727770b90bfec6b1111326345a4bd01644736bc'),
        ('904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e', '82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85'),
        ('analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf', 'analysis/dev006/p13-read-seek-v1/libfs_utility_init-p13.elf'),
        ('analysis/dev006/p12-setup-abort-model-v1/result.json', 'analysis/dev006/p13-read-seek-model-v3/result.json'),
        ("'candidate':'HDD2TB-P12'", "'candidate':'HDD2TB-P13'"),
        ('Abort on summary read error before CONTINUE/later allocations; discard uncommitted setup-buffer dirty state before OOM cleanup; P11 guards/storage/observer/budget retained', PURPOSE),
        ('analysis/dev006/prepare_p12_setup_abort_guard.py', 'analysis/dev006/prepare_p13_read_seek_guard.py'),
        ('analysis/dev006/p12-setup-abort-v1/manifest.json', 'analysis/dev006/p13-read-seek-v1/manifest.json'),
        ('analysis/dev006/model_p12_setup_abort.py', 'analysis/dev006/model_p13_read_seek_v3.py'),
        ('analysis/dev006/p12-setup-delta/review.json', 'analysis/dev006/p13-read-delta/review.json'),
        ("ROOT/'candidates/HDD2TB-P12'", "ROOT/'candidates/HDD2TB-P13'")])
    audit = adapt('analysis/dev006/audit_p12.py', 'analysis/dev006/audit_p13.py', [
        ('P11', '__P13_PARENT__'), ('P12', 'P13'), ('__P13_PARENT__', 'P12'),
        ('p12-review', 'p13-review'), ('candidate-p12-v2', 'candidate-p13-v2'),
        ('d299aad533a12ff8a7a6e5bc0e20093977de18e7e9eef0aac7cc58b4aa065552', '7fb5d6e57ef53654f336745dbc9463c8e6b2cded03b05cdbeb80e5125215fb7c'),
        ('904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e', '82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85'),
        ('analysis/dev006/p12-setup-abort-v1/manifest.json', 'analysis/dev006/p13-read-seek-v1/manifest.json'),
        ('analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf', 'analysis/dev006/p13-read-seek-v1/libfs_utility_init-p13.elf'),
        ('for at in (0x1f754,0x1fb6c):', 'for at in (0x14b88,0x14bd4,0x14c50):'),
        ('y[0][0x265c0:0x26600]=x[0][0x265c0:0x26600]', 'y[0][0x26640:0x26670]=x[0][0x26640:0x26670]'),
        ('analysis/dev006/p12-setup-abort-model-v1/result.json', 'analysis/dev006/p13-read-seek-model-v3/result.json'),
        ('except_two_hooks_and64_helper_bytes', 'except_three_hooks_and48_helper_bytes')])
    with (R / 'analysis/dev006/p13-builder-provenance.json').open('x', encoding='utf8') as stream:
        json.dump({'builder': builder, 'separate_parser_audit': audit}, stream, indent=2)
        stream.write('\n')
    print('Fresh P13 builder and separate parser prepared; both AST checked.')


if __name__ == '__main__':
    main()
