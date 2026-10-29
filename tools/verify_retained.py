"""Read-only check of retained data on the Lexar over webMAN FTP.

Expected values: tools/data/lexar-retained-v1.json (from the passing 2026-10-18
post-restart read): 16 whole game executables (109,089,728 B) plus 55 filler
sizes and 165 x 64 KiB pattern slices (beginning, 4 GiB crossing, tail/EOF).
About 120 MB of client reads; took 212 s last time.

    python tools/verify_retained.py --host <ps3-ip> --save runs/G2-20261030
    python tools/verify_retained.py --host <ps3-ip> --controls-only   # after filler deletion (M5)
    python tools/verify_retained.py --list-filler                        # paths for M5
"""
import argparse, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ps3ftp import Console

DATA = Path(__file__).resolve().parent / 'data/lexar-retained-v1.json'
CAP = 128 * 2**20


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('--host')
    a.add_argument('--data', type=Path, default=DATA)
    a.add_argument('--controls-only', action='store_true')
    a.add_argument('--save', type=Path, help='run directory for retained-check.json')
    a.add_argument('--list-filler', action='store_true')
    args = a.parse_args()
    spec = json.loads(args.data.read_text(encoding='utf-8'))
    if args.list_filler:
        for f in spec['filler_files']:
            print(f"{f['bytes']:>12} {f['path']}")
        print(f"{len(spec['filler_files'])} files, {sum(f['bytes'] for f in spec['filler_files']) / 2**30:.3f} GiB")
        return 0
    if not args.host:
        a.error('--host is required')

    con, rows, client, t0 = Console(args.host), [], 0, time.time()

    def record(kind, path, ok, **detail):
        rows.append({'kind': kind, 'path': path, 'ok': ok, **detail})
        if not ok:
            print(f'MISMATCH {kind} {path} {detail}')

    for c in spec['controls']:
        size = con.size(c['path'])
        got = con.read(c['path']) if size == c['bytes'] else {'bytes': 0, 'sha256': None, 'eof': None}
        client += got['bytes']
        record('control', c['path'], size == c['bytes'] and got['sha256'] == c['sha256'] and got['eof'],
               size=size, sha256=got['sha256'])
    if not args.controls_only:
        sizes = {}
        for f in spec['filler_files']:
            sizes[f['path']] = con.size(f['path'])
            record('filler-size', f['path'], sizes[f['path']] == f['bytes'], size=sizes[f['path']])
        for s in spec['samples']:
            if client + s['bytes'] > CAP:
                sys.exit('client read cap reached; aborting')
            if sizes.get(s['path']) is None:
                record('sample', s['path'], False, label=s['label'], reason='file missing')
                continue
            got = con.read(s['path'], s['offset'], s['bytes'])
            client += got['bytes']
            record('sample', s['path'], got['bytes'] == s['bytes'] and got['sha256'] == s['sha256']
                   and (got['eof'] or not s['expect_EOF']), label=s['label'], offset=s['offset'],
                   sha256=got['sha256'], eof=got['eof'])

    bad = [r for r in rows if not r['ok']]
    summary = {'data': spec['id'], 'host': args.host, 'checked': len(rows), 'mismatches': len(bad),
               'client_bytes': client, 'seconds': round(time.time() - t0, 1),
               'controls_only': args.controls_only, 'passed': not bad}
    if args.save:
        args.save.mkdir(parents=True, exist_ok=True)
        (args.save / 'retained-check.json').write_text(json.dumps({'summary': summary, 'rows': rows}, indent=1) + '\n',
                                                       encoding='utf-8')
    print(json.dumps(summary))
    print('PASS' if not bad else 'FAIL')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
