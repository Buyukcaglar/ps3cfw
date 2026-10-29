# Project tools (`tools/*.py`)

| Script | Purpose | Touches |
|---|---|---|
| `verify_build.py` | Vault integrity + byte-exact rebuild of P13 into `build/` | local only |
| `build_hdd2tb_p13.py` | Canonical P13 build (P12 PUP + `firmware/HDD2TB-P13/inputs/`) | local only |
| `build_hdd2tb_p1/p3/p5.py` | Libraries imported by the P13 build (SELF/PKG/PUP repacking); earlier `p*.py` document each patch step | local only |
| `stage_usb.py` | Copy a PUP to the FAT32 stick, verify by unbuffered device re-read, optional `--clear-observer`, `--eject` | USB stick (writes) |
| `check_installed.py` | G1: compare the installed `libfs_utility_init.sprx` with a candidate's SELF | console FTP (read) |
| `read_observer.py` | Fetch/decode the 272 B observer record; `--rename-to` frees the O_EXCL name | console FTP (read + rename on USB) |
| `verify_retained.py` | Lexar retained-data check (16 controls, 55 sizes, 165 slices) or `--controls-only` | console FTP (read) |
| `delete_filler.py` | M5: delete exactly the 55 recorded filler files (dry run unless `--execute`) | console FTP (delete) |
| `ps3ftp.py` | Shared webMAN FTP helper | - |
| `perf_summary.py` | Re-derive the PERF001 RO1/BH/BF read/write tables from the archive | local only (archive read) |
| `decrypt_self.py`, `analyze_pup.py`, `inspect_elf.py` | SELF/PUP/ELF inspection helpers | local only |

`data/lexar-retained-v1.json` holds the expected values (from the passing
2026-10-18 read) and the filler path list. FTP tools were tested against a local
pyftpdlib server (2026-10-29), not yet against webMAN.

Everything else under `tools/` is third-party: scetool (+keys), mfw-builder, ps3keys,
ps3tools, PS3DumpChecker, PS3-HDD-Reader, cobra/webman/xai sources, psl1ght
reference, smartmontools, `toolchains/` (psdk3v2 portable, zig 0.15.2),
`python_packages/` (pycryptodome), and `PS3HDDTool/` (the owner's published fork).
