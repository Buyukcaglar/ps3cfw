"""Stage a firmware PUP on the FAT32 USB stick and verify it from the device.

    python tools/stage_usb.py --drive E:                        # P13 (default)
    python tools/stage_usb.py --drive E: --pup firmware/baseline-evilnat-4.93-cex/PS3/UPDATE/PS3UPDAT.PUP
    python tools/stage_usb.py --drive E: --clear-observer --eject

Refuses volumes that are not FAT32 on a USB, non-boot, non-system disk. Copies
via a temporary name with fsync, then re-reads the staged file with
FILE_FLAG_NO_BUFFERING (bypassing the Windows cache) and compares SHA-256.
--clear-observer moves an existing HDD2TB-P8.bin into HDD2TB-old\\ so the
observer (O_EXCL) can write a fresh record.
"""
import argparse, ctypes, hashlib, json, mmap, os, shutil, subprocess, sys, time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PUP = ROOT / 'firmware/HDD2TB-P13/PS3/UPDATE/PS3UPDAT.PUP'

# Absolute path: Git Bash's PATH has no powershell.exe.
POWERSHELL = str(Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe')


def volume_identity(letter):
    ps = (f"$ErrorActionPreference='Stop';$v=Get-Volume -DriveLetter {letter};"
          f"$p=Get-Partition -DriveLetter {letter};$d=Get-Disk -Number $p.DiskNumber;"
          "[pscustomobject]@{FileSystem=[string]$v.FileSystem;Label=[string]$v.FileSystemLabel;"
          "Size=$v.Size;Free=$v.SizeRemaining;BusType=[string]$d.BusType;Disk=$d.Number;"
          "Model=[string]$d.FriendlyName;Serial=[string]$d.SerialNumber;"
          "Boot=($d.IsBoot -or $p.IsBoot);System=($d.IsSystem -or $p.IsSystem)}|ConvertTo-Json -Compress")
    r = subprocess.run([POWERSHELL, '-NoProfile', '-NonInteractive', '-Command', ps],
                       capture_output=True, timeout=30)
    if r.returncode:
        sys.exit(f'Volume query for {letter}: failed: {r.stderr.decode(errors="replace").strip()}')
    return json.loads(r.stdout.decode('utf-8-sig'))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def sha256_unbuffered(path, chunk=1 << 20):
    """SHA-256 read with FILE_FLAG_NO_BUFFERING so bytes come from the device."""
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k32.ReadFile.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                             ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID]
    handle = k32.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x20000000 | 0x08000000, None)
    if handle in (None, wintypes.HANDLE(-1).value):
        raise OSError(ctypes.get_last_error(), 'CreateFileW (no buffering) failed')
    buf = mmap.mmap(-1, chunk)                     # page-aligned, as NO_BUFFERING requires
    addr = ctypes.addressof(ctypes.c_char.from_buffer(buf))
    h, n = hashlib.sha256(), wintypes.DWORD()
    try:
        while True:
            if not k32.ReadFile(handle, addr, chunk, ctypes.byref(n), None):
                raise OSError(ctypes.get_last_error(), 'ReadFile failed')
            if not n.value:
                break
            h.update(buf[:n.value])
    finally:
        k32.CloseHandle(handle)
        del addr
        buf.close()
    return h.hexdigest()


def eject_volume(letter, tries=10):
    """Flush, lock, dismount and eject the volume (what Safely Remove does; locale independent)."""
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k32.DeviceIoControl.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
                                    wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                    wintypes.LPVOID]
    handle = k32.CreateFileW(rf'\\.\{letter}:', 0xC0000000, 3, None, 3, 0, None)
    if handle in (None, wintypes.HANDLE(-1).value):
        raise OSError(ctypes.get_last_error(), f'open volume {letter}: failed')
    n = wintypes.DWORD()

    def ioctl(code, inbuf=None, size=0):
        return k32.DeviceIoControl(handle, code, inbuf, size, None, 0, ctypes.byref(n), None)
    try:
        k32.FlushFileBuffers(handle)
        for _ in range(tries):
            if ioctl(0x00090018):                       # FSCTL_LOCK_VOLUME
                break
            time.sleep(0.5)
        else:
            raise OSError(ctypes.get_last_error(), 'volume is in use (close Explorer windows on it)')
        if not ioctl(0x00090020):                       # FSCTL_DISMOUNT_VOLUME
            raise OSError(ctypes.get_last_error(), 'dismount failed')
        allow = ctypes.c_ubyte(0)                       # PREVENT_MEDIA_REMOVAL = FALSE
        ioctl(0x002D4804, ctypes.byref(allow), 1)       # IOCTL_STORAGE_MEDIA_REMOVAL
        if not ioctl(0x002D4808):                       # IOCTL_STORAGE_EJECT_MEDIA
            raise OSError(ctypes.get_last_error(), 'eject failed')
    finally:
        k32.CloseHandle(handle)


def copy_verified(src, dst, want):
    tmp = dst.with_name(dst.name + '.partial')
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src, 'rb') as fi, open(tmp, 'wb') as fo:
        shutil.copyfileobj(fi, fo, 1 << 20)
        fo.flush()
        os.fsync(fo.fileno())
    os.replace(tmp, dst)
    got = sha256_unbuffered(dst)
    if got != want:
        sys.exit(f'STAGED FILE MISMATCH: {got} != {want}. Do not use this stick.')
    return got


def main():
    a = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    a.add_argument('--drive', required=True, help='USB drive letter, e.g. E:')
    a.add_argument('--pup', type=Path, default=DEFAULT_PUP)
    a.add_argument('--clear-observer', action='store_true')
    a.add_argument('--eject', action='store_true')
    args = a.parse_args()
    letter = args.drive.rstrip(':\\/').upper()
    if len(letter) != 1 or letter == 'C':
        sys.exit('Give a single non-system drive letter')

    v = volume_identity(letter)
    print(json.dumps(v))
    if v['FileSystem'] != 'FAT32' or v['BusType'] != 'USB' or v['Boot'] or v['System']:
        sys.exit(f'Refusing {letter}: needs FAT32 on a USB, non-boot, non-system disk')

    sums = args.pup.parent.parent.parent / 'SHA256SUMS.txt'
    want = sums.read_text().split()[0].lower() if sums.is_file() else None
    have = sha256_file(args.pup)
    if want and have != want:
        sys.exit(f'Source PUP {have} does not match {sums}')
    if v['Free'] < args.pup.stat().st_size + 2**20 and not (Path(f'{letter}:/PS3/UPDATE/PS3UPDAT.PUP').exists()):
        sys.exit('Not enough free space on the stick')

    usb = Path(f'{letter}:/')
    if args.clear_observer and (usb / 'HDD2TB-P8.bin').exists():
        old = usb / 'HDD2TB-old'
        old.mkdir(exist_ok=True)
        target = old / f'HDD2TB-P8-{time.strftime("%Y%m%d-%H%M%S")}.bin'
        os.replace(usb / 'HDD2TB-P8.bin', target)
        print(f'moved old observer record to {target}')

    t0 = time.time()
    got = copy_verified(args.pup, usb / 'PS3/UPDATE/PS3UPDAT.PUP', have)
    print(f'STAGED {args.pup.relative_to(ROOT) if args.pup.is_relative_to(ROOT) else args.pup} -> '
          f'{letter}:\\PS3\\UPDATE\\PS3UPDAT.PUP  sha256 {got}  ({time.time() - t0:.0f} s, device re-read)')
    print('observer record present: ' + str((usb / 'HDD2TB-P8.bin').exists()))

    if args.eject:
        eject_volume(letter)
        print(f'EJECTED {letter}: (dismounted); safe to unplug')
    return 0


if __name__ == '__main__':
    sys.exit(main())
