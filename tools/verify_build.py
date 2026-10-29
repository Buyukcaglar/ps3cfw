"""Readiness check: rebuild HDD2TB-P13 from P12 and confirm vault integrity.

Rebuilds into build/verify-<time>/ (git-ignored), compares the PUP with
firmware/HDD2TB-P13/SHA256SUMS.txt, then removes the scratch directory.
No device, USB or network access.

    python tools/verify_build.py            # rebuild + vault check
    python tools/verify_build.py --vault    # vault check only (fast)
"""
import argparse, hashlib, shutil, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P13 = ROOT / 'firmware/HDD2TB-P13'

# Fixed identities recorded at the 2026-10-29 takeover. Large images are checked
# by size only: hashing 931 GiB takes hours and proves little for a rename.
VAULT = {
    'vault/nand/HW001B_FLASH-NAND-FW4.93.bin': ('sha256', '<nand-sha256-private>'),
    'vault/nand/HW001D_FLASH-NAND-FW4.93.bin': ('sha256', '<nand-sha256-private>'),
    'vault/console-keys/eid_root_key': ('size', 48),
    'vault/original-1tb-hdd/source-image-20261012T094859-d8fa48f5/capture/disk-3.raw': ('size', 1000204886016),
    'firmware/baseline-evilnat-4.93-cex/PS3/UPDATE/PS3UPDAT.PUP': ('sha256', 'ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a'),
    'firmware/HDD2TB-P12/PS3/UPDATE/PS3UPDAT.PUP': ('sha256', '7fb5d6e57ef53654f336745dbc9463c8e6b2cded03b05cdbeb80e5125215fb7c'),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def check_vault():
    ok = True
    for rel, (kind, want) in VAULT.items():
        p = ROOT / rel
        if not p.is_file():
            print(f'MISSING  {rel}'); ok = False; continue
        got = sha256(p) if kind == 'sha256' else p.stat().st_size
        good = got == want
        ok &= good
        print(f"{'ok      ' if good else 'MISMATCH'} {rel}")
    return ok


def check_build():
    want = (P13 / 'SHA256SUMS.txt').read_text().split()[0].lower()
    work = ROOT / 'build' / f'verify-{time.strftime("%Y%m%dT%H%M%S")}'
    try:
        subprocess.run([sys.executable, str(ROOT / 'tools/build_hdd2tb_p13.py'),
                        '--work', str(work / 'work'), '--dest', str(work / 'dest')], check=True, cwd=ROOT)
        got = sha256(work / 'dest/PS3/UPDATE/PS3UPDAT.PUP')
    finally:
        shutil.rmtree(work, ignore_errors=True)
    good = got == want
    print(f"{'ok      ' if good else 'MISMATCH'} P13 rebuild {got}")
    return good


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--vault', action='store_true', help='skip the rebuild')
    args = a.parse_args()
    ok = check_vault() and (args.vault or check_build())
    print('READY' if ok else 'NOT READY')
    sys.exit(0 if ok else 1)
