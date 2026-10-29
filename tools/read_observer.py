"""Fetch and decode the P13 heap-observer record (272 B, /dev_usb000/HDD2TB-P8.bin).

The observer opens the file O_WRONLY|O_CREAT|O_EXCL: it never overwrites, so a
second checker run in the same sitting writes nothing unless the previous record
was moved away. Use --rename-to after every check.

    python tools/read_observer.py runs/G2-20261030/HDD2TB-P8.bin
    python tools/read_observer.py --host <ps3-ip> --save runs/G2-20261030 --rename-to HDD2TB-G2.bin

Layout (from src/patch-generators/prepare_p8_native.py and the HW002AK parser):
  0..127   32 x u32 witness words (budget, backing, status, create/delete, worker count)
  48..63   identity "HDD2TB-P8-NATI"
  128..255 tm_record core header (src/checker_telemetry_p8/telemetry.h)
  256..271 footer: u32 0x50384654 ("P8FT"), u32 0, u64 256
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path

REMOTE = '/dev_usb000/HDD2TB-P8.bin'
ARENA = 134217728
PASS_PEAK = 96 * 2**20          # ROADMAP G2: <= 75 % of the arena
CORE = ('magic version bytes lock epoch heap base budget flags active coverage finished '
        'alloc_calls free_calls failed_allocs null_frees live_bytes peak_bytes live_count peak_count '
        'largest_request largest_failed_request utility_status events route backing_status '
        'log_open_status log_write_status log_close_status log_bytes_hi log_bytes_lo reserved').split()
FLAGS = ('BAD_GEOMETRY BAD_POINTER BAD_HEADER DUPLICATE TABLE_FULL UNKNOWN_FREE ACCOUNTING '
         'NOT_LOCKED NOT_ACTIVE INCOMPLETE_COVERAGE IDENTITY').split()   # telemetry.h, bit 0 up


def decode(blob):
    problems = []
    if len(blob) != 272:
        return {'valid': False, 'problems': [f'size {len(blob)} != 272']}
    if blob[48:64] != b'HDD2TB-P8-NATI\0\0':
        problems.append('identity string missing')
    if struct.unpack_from('>IIQ', blob, 256) != (0x50384654, 0, 256):
        problems.append('footer missing (record write incomplete)')
    w = struct.unpack_from('>32I', blob)
    c = dict(zip(CORE, struct.unpack_from('>32I', blob, 128)))
    initialized = w[22] == 1
    if w[1] != 2 or w[5] != 1:
        problems.append('callback-export witness not consumed (unexpected entry route)')
    if initialized and (c['magic'] != 0x4832544d or c['version'] != 1 or c['bytes'] != 131200):
        problems.append('core header identity invalid')
    consistent = (initialized and c['flags'] == 512 and c['coverage'] == 0 and c['lock'] == 0
                  and c['active'] == 0 and c['finished'] == 1 and c['base'] == w[2]
                  and c['budget'] == w[3] and c['utility_status'] == w[8]
                  and w[16] == 1 and w[17] == 1 and w[21] == 0 and w[23] == 1
                  and c['alloc_calls'] == w[18] and c['free_calls'] == w[19]
                  and c['events'] == c['alloc_calls'] + c['free_calls']
                  and c['peak_bytes'] <= c['budget'] and c['live_bytes'] <= c['peak_bytes'])
    budget, status, worker = w[3], w[8], w[26]
    if not worker:
        verdict = 'NO-FULL-SCAN'          # quick check only; the gate was not exercised
    elif status or c['failed_allocs'] or c['largest_failed_request']:
        verdict = 'FAIL'
    elif budget != ARENA:
        verdict = 'FAIL'                  # an unpatched (32 MiB) route reached the checker
    elif not consistent:
        # Completed inside the 128 MiB budget, but the peak is not a full count. TABLE_FULL
        # (>16,384 live chunks, e.g. a populated volume) makes peak_bytes a lower bound.
        verdict = 'PASS-UNMEASURED'
    elif c['peak_bytes'] <= PASS_PEAK:
        verdict = 'PASS'
    else:
        verdict = 'YELLOW'
    return {
        'valid': not problems, 'problems': problems, 'verdict': verdict,
        'sha256': hashlib.sha256(blob).hexdigest(),
        'requested_budget_bytes': budget, 'backing_address': hex(w[2]),
        'utility_status': hex(status), 'full_worker_calls': worker,
        'heap_create_delete': [w[16], w[17]], 'missing_delete': w[21],
        'argc': w[24], 'core_initialized': initialized, 'accounting_consistent': consistent,
        'flag_names': [n for i, n in enumerate(FLAGS) if c['flags'] >> i & 1],
        'peak_is_lower_bound': bool(c['flags'] & 16),
        'peak_bytes': c['peak_bytes'], 'peak_MiB': round(c['peak_bytes'] / 2**20, 2),
        'peak_fraction_of_arena': round(c['peak_bytes'] / ARENA, 4),
        'largest_request': c['largest_request'], 'failed_allocs': c['failed_allocs'],
        'largest_failed_request': c['largest_failed_request'],
        'alloc_calls': c['alloc_calls'], 'free_calls': c['free_calls'], 'route': c['route'],
        'core': c, 'witness_words': list(w),
        'note': 'Peak = charged chunks seen at the known allocator wrappers (flag 512: partial '
                'coverage); excludes heap bookkeeping. An indicator, not a proven native maximum.',
    }


def fetch(host, save, rename_to):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ps3ftp import Console
    con = Console(host)
    size = con.size(REMOTE)
    if size is None:
        print(f'No record at {REMOTE}. Either no full check ran through the observed route, '
              'the stick was not mounted as usb000 (use the rightmost port), or the old record '
              'was not moved away before this check.')
        sys.exit(2)
    if size > 4096:
        sys.exit(f'Refusing oversized record ({size} B)')
    got = con.read(REMOTE, keep=True)
    blob = got['data']
    if len(blob) != size:
        sys.exit(f'Short read {len(blob)}/{size} B')
    save.mkdir(parents=True, exist_ok=True)
    local = save / 'HDD2TB-P8.bin'
    with open(local, 'xb') as f:
        f.write(blob)
    if rename_to:
        con.rename(REMOTE, '/dev_usb000/' + rename_to)
        print(f'Renamed on console to /dev_usb000/{rename_to}; the next check can write a fresh record.')
    return blob


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('file', nargs='?', type=Path, help='saved 272 B record')
    a.add_argument('--host', help='console IP (webMAN FTP)')
    a.add_argument('--save', type=Path, help='run directory for the fetched record (required with --host)')
    a.add_argument('--rename-to', help='new name on the stick after a successful local save')
    args = a.parse_args()
    if args.host:
        if not args.save:
            a.error('--save is required with --host')
        blob = fetch(args.host, args.save, args.rename_to)
    elif args.file:
        blob = args.file.read_bytes()
    else:
        a.error('give a FILE or --host')
    result = decode(blob)
    text = json.dumps(result, indent=1)
    if args.host:
        (args.save / 'observer.json').write_text(text + '\n', encoding='utf-8')
    print(text)
    print(f"\nVERDICT {result.get('verdict')}  peak {result.get('peak_MiB')} MiB of 128 MiB  "
          f"budget {result.get('requested_budget_bytes')}  status {result.get('utility_status')}")
