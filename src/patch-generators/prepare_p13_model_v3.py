"""Correct fault fixture reachability, preserving both failed model drafts and ELF."""
import ast
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]


def main():
    parent = R / 'analysis/dev006/model_p13_read_seek_v2.py'
    source = parent.read_text('utf8')
    changes = [
        ('p13-read-seek-model-v2', 'p13-read-seek-model-v3'),
        ("[('initial-seek', 0, bulk, 'full')", "[('initial-seek', 0, bulk, 'full', 0)"),
        ("[('retry-seek', 1, bulk, 'full')", "[('retry-seek', 1, bulk, 'full', 0)"),
        ("for kind in ('full', 'short'):\n                                failure_cases.append(('sector-reseek', 2 + at, -1, kind))",
         "for kind in ('negative', 'short'):\n                                failure_cases.append(('sector-reseek', 2, -1, kind, at))"),
        ('for family, failed_seek, bulk, kind in failure_cases:',
         'for family, failed_seek, bulk, kind, failed_sector in failure_cases:'),
        ('bulk, failed_seek, error, kind, 0)', 'bulk, failed_seek, error, kind, failed_sector)'),
        ("'bulk_result': bulk, 'first_sector': kind, 'error': error,",
         "'bulk_result': bulk, 'sector_result_kind': kind, 'failed_sector': failed_sector, 'error': error,"),
        ("json.dump({'pass': False, 'error': repr(error), 'hardware_IO': False}, stream, indent=2)",
         "json.dump({'pass': False, 'error': repr(error), 'hardware_IO': False,\n                       'context': {k: repr(v) for k, v in locals().items() if k in ('bases', 'count', 'family', 'failed_seek', 'bulk', 'kind', 'failed_sector')}}, stream, indent=2)"),
    ]
    for old, new in changes:
        assert old in source, old
        source = source.replace(old, new)
    ast.parse(source)
    target = R / 'analysis/dev006/model_p13_read_seek_v3.py'
    with target.open('x', encoding='utf8') as stream:
        stream.write(source)
    with (R / 'analysis/dev006/p13-read-model-v3-provenance.json').open('x', encoding='utf8') as stream:
        json.dump({'parent': str(parent.relative_to(R)),
                   'parent_sha256': hashlib.sha256(parent.read_bytes()).hexdigest(),
                   'destination_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                   'changes': changes,
                   'v1_and_v2_failures_retained': True,
                   'v1_fixture_error': 'Zero-length completed bulk read does not reach retry seek',
                   'v2_fixture_error': 'Successful sector read branches around reseek; only a short/failed sector reaches reseek, whose seek index is 2 in these single-bad-sector fixtures',
                   'firmware_draft_modified': False, 'AST_passed': True}, stream, indent=2)
        stream.write('\n')
    print('Fresh v3 fault fixtures follow actual branch reachability; ELF unchanged.')


if __name__ == '__main__':
    main()
