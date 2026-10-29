"""G1 check: is the installed checker module the one from a given candidate?

    python tools/check_installed.py --host <ps3-ip>            # expects P13
    python tools/check_installed.py --host <ps3-ip> --candidate HDD2TB-RDI12

Reads /dev_flash/sys/internal/libfs_utility_init.sprx over webMAN FTP and
compares it with `self_sha256` / `self_bytes_after` in the candidate's
build-manifest.json. Also reports whether an observer record is on usb000.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ps3ftp import Console

ROOT = Path(__file__).resolve().parent.parent
MODULE = '/dev_flash/sys/internal/libfs_utility_init.sprx'


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('--host', required=True)
    a.add_argument('--candidate', default='HDD2TB-P13')
    args = a.parse_args()
    m = json.loads((ROOT / 'firmware' / args.candidate / 'build-manifest.json').read_text(encoding='utf-8'))
    want_sha, want_size = m['self_sha256'], m['self_bytes_after']
    con = Console(args.host)
    got = con.read(MODULE)
    ok = got['sha256'] == want_sha and got['bytes'] == want_size
    print(json.dumps({'module': MODULE, 'bytes': got['bytes'], 'sha256': got['sha256'],
                      'expected': args.candidate, 'expected_sha256': want_sha, 'match': ok}))
    rec = con.size('/dev_usb000/HDD2TB-P8.bin')
    print(f'observer record on usb000: {"present (" + str(rec) + " B): move it before the next check" if rec is not None else "absent"}')
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
