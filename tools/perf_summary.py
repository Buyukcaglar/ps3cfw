"""Re-derive the PERF001 native read/write results from the archived evidence (read-only).

    python tools/perf_summary.py            # all three tables
    python tools/perf_summary.py ro1|bh|bf  # one table

ro1: RO1 read benchmark on the populated Lexar (2026-10-17, 106 runs): per stage, median
     end-to-end and syscall-active MB/s and per-read latency (ticks at 79.8 MHz).
bh:  second fill (2026-10-18): write-call vs application MB/s per 2 GiB written.
bf:  first fill (2026-10-15..17): application write MB/s (UI recent rate) per 8 GiB written.
MB/s = 10^6 B/s. See docs/research/PERF001/ANALYSIS-20261029.md for the interpretation.
"""
import collections, csv, io, json, statistics as st, sys, zipfile
from pathlib import Path

ZIP = Path(__file__).resolve().parent.parent / 'archive/history-pre-takeover-20261029.zip'
RO1 = ('observations/HW002BG/ro1-release-proposal-v1/authorized-stage-v1/'
       'receipt-verification-v1/saved-native-timing-analysis.json')
BH = 'observations/HW002BH/metrics-v2/native-receipt-v1/performance/performance.csv'
BF = 'analysis/PERF001/bf-analysis/decoded-progress.csv'
STAGES = {1: 'CAL', 2: 'CPU', 3: 'SEQ', 4: 'BUF', 5: 'PLACE', 6: 'RANDOM', 7: 'FILES', 8: 'OVERHEAD'}
# ro1.c: SEQ mode 0 = read only, 1 = pattern+SHA verified, 2 = slice SHA; BUF mode 0/1/2 =
# 4 KiB/64 KiB/1 MiB requests; PLACE file 0/1/2 = early/middle/late file; RANDOM = 8192 x 4 KiB
# then 1024 x 64 KiB per repeat; FILES = 16 game files, whole-file SHA; OVERHEAD = 4 KiB controls.


def ro1(z):
    d = json.loads(z.read(RO1))
    f = d['frequency']
    groups = collections.defaultdict(list)
    for r in d['runs']:
        if r['stage'] in (1, 2):
            continue
        size = r['read_bytes'] // max(r['metrics'][0]['calls'] - 1, 1) if r['stage'] == 6 else ''
        groups[(STAGES[r['stage']], r['mode'], r['file'] if r['stage'] == 5 else '', size)].append(r)
    cpu = [r['elapsed_ticks'] / f for r in d['runs'] if r['stage'] == 2]
    print(f'RO1: CPU-only pattern+SHA+compare, 256 MiB passes: median {st.median(cpu):.2f} s '
          f'= {268435456 / st.median(cpu) / 1e6:.2f} MB/s')
    print(f"{'stage':8} {'mode':>4} {'file':>4} {'req':>6} {'runs':>4} {'e2e MB/s':>9} {'sys MB/s':>9}"
          f" {'reads':>6} {'p50 us':>8} {'p99 us':>8}")
    for k in sorted(groups, key=lambda k: (list(STAGES.values()).index(k[0]), k[1], str(k[2]), str(k[3]))):
        rs, m = groups[k], [r['metrics'][0] for r in groups[k]]
        calls = sum(x['calls'] for x in m)
        e2e = st.median([r['end_to_end_MBps'] for r in rs])
        sysr = [r['syscall_active_MBps'] for r in rs if r['syscall_active_MBps']]
        p50 = st.median([sum(x['quantile_bounds_ticks']['p50']) / 2 for x in m if x['calls']] or [0])
        p99 = max([x['quantile_bounds_ticks']['p99'][1] for x in m if x['calls']] or [0])
        print(f"{k[0]:8} {k[1]:>4} {str(k[2]):>4} {str(k[3]):>6} {len(rs):>4} {e2e:>9.2f}"
              f" {st.median(sysr) if sysr else 0:>9.2f} {calls:>6} {p50 / f * 1e6:>8.0f} {p99 / f * 1e6:>8.0f}")


def bh(z):
    rows = list(csv.DictReader(io.StringIO(z.read(BH).decode())))
    acc, prev = collections.defaultdict(lambda: [0, 0, 0, None]), None
    for r in rows:
        if prev and r['phase'] == prev['phase'] == '2':
            b = acc[int(int(r['written_bytes']) / 2**30 // 2) * 2]
            b[0] += int(r['write_bytes']) - int(prev['write_bytes'])
            b[1] += int(r['write_time_us']) - int(prev['write_time_us'])
            b[2] += int(r['elapsed_us']) - int(prev['elapsed_us'])
            b[3] = b[3] or float(r['available_GiB'])
        prev = r
    print('BH: GiB written | free GiB | write-call MB/s | app MB/s | write-call ms/MiB')
    for g in sorted(acc):
        w, t, e, free = acc[g]
        if t:
            print(f'  {g:3d}-{g + 2:<3d} {free:7.1f} {w / t:8.2f} {w / e:8.2f} {t / 1000 / (w / 2**20):8.1f}')


def bf(z):
    rows = list(csv.DictReader(io.StringIO(z.read(BF).decode())))
    acc, free = collections.defaultdict(list), {}
    for r in rows:
        if r['phase'] == '2' and int(r['recent_Bps']) > 0:
            g = int(int(r['written_bytes']) / 2**30 // 8) * 8
            acc[g].append(int(r['recent_Bps']) / 1e6)
            free.setdefault(g, int(r['available_bytes']) / 2**30)
    print('BF: GiB written | free GiB | median app write MB/s (UI recent rate)')
    for g in sorted(acc):
        print(f'  {g:4d}-{g + 8:<4d} {free[g]:7.1f} {st.median(acc[g]):7.2f}')


if __name__ == '__main__':
    want = sys.argv[1:] or ['ro1', 'bh', 'bf']
    with zipfile.ZipFile(ZIP) as z:
        for name in want:
            {'ro1': ro1, 'bh': bh, 'bf': bf}[name](z)
            print()
