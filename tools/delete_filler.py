"""M5: delete the 55 BF/BH test filler files (858.19 GiB) from the Lexar via webMAN FTP.

    python tools/delete_filler.py --host <ps3-ip>             # dry run: sizes only
    python tools/delete_filler.py --host <ps3-ip> --execute   # delete

Deletes exactly the paths listed in tools/data/lexar-retained-v1.json, and only
when the remote size equals the recorded size. Lists other HDD2TB-* entries left
in /dev_hdd0/tmp for manual review; never deletes anything else.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ps3ftp import Console

DATA = Path(__file__).resolve().parent / 'data/lexar-retained-v1.json'


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('--host', required=True)
    a.add_argument('--execute', action='store_true')
    args = a.parse_args()
    files = json.loads(DATA.read_text(encoding='utf-8'))['filler_files']
    con, freed, skipped = Console(args.host), 0, []
    for f in files:
        size = con.size(f['path'])
        if size is None:
            print(f"absent   {f['path']}")
            continue
        if size != f['bytes']:
            skipped.append(f['path'])
            print(f"SKIP     {f['path']} size {size} != recorded {f['bytes']}")
            continue
        if args.execute:
            con.delete(f['path'])
            print(f"deleted  {f['path']}")
        else:
            print(f"would delete {f['path']} ({size} B)")
        freed += size
    listed = {f['path'].rsplit('/', 1)[-1] for f in files}
    left = [n for n in con.names('/dev_hdd0/tmp') if n.startswith('HDD2TB') and n not in listed]
    print(f"{'freed' if args.execute else 'would free'} {freed / 2**30:.2f} GiB; skipped {len(skipped)}")
    if left:
        print('other HDD2TB-* entries in /dev_hdd0/tmp (review manually):', ', '.join(sorted(left)))
    return 1 if skipped else 0


if __name__ == '__main__':
    sys.exit(main())
