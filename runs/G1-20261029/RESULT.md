# G1: reinstall P13 -> PASS (2026-10-29)

## Step 0: USB staging, 2026-10-29 (PC clock 12:22, UTC+3)
* Stick: SanDisk 3.2 Gen1, serial <serial>, FAT32, USB bus, not boot/system (G:).
* `tools/verify_build.py` -> READY (vault ok, P13 rebuild 652c0c03...6d).
* Staged `firmware/HDD2TB-P13` PUP -> `G:\PS3\UPDATE\PS3UPDAT.PUP` (replaced RDI12).
  Unbuffered device re-read: 215,765,852 B, SHA-256
  652c0c0312cd51283473e653df6e2cdfd874a674f6fb7e83979c45d28fed066d = P13. MATCH.
* The old observer record (RDI12 run, 2026-10-22) moved to
  `G:\HDD2TB-old\HDD2TB-P8-20261029-122233.bin`. No `HDD2TB-P8.bin` is left at the stick root.
* The stick also holds old-session leftovers and copies of the NAND dump (= vault HW001D),
  `eid_root_key` and `xRegistry.sys` (both = vault). Left untouched.
* The eject first failed (the tool could not find `powershell.exe`, then the shell verb was
  ignored). Fixed in `stage_usb.py` (volume-API eject). Volume dismounted after the copy was verified.

## Owner report
"all green 1.13": install completed, XMB normal, webMAN at <ps3-ip>.

## Tool verdicts
* `check_installed.py --host <ps3-ip>` -> PASS: installed
  `/dev_flash/sys/internal/libfs_utility_init.sprx` = 78,487 B, SHA-256
  7a57307b62aed291803b22a4db5da6d541c004f699368957a266e7f2442b6389 (P13 SELF).
* webMAN `cpursx.ps3`: HDD 1,658.2 GB free (unchanged from RDI12), firmware 4.93 CEX
  Cobra 8.5, USB000 mounted (104 GB free), so the stick is in the right port.
* Observer record on usb000: absent (no full check ran yet), as expected.
