# G3b: dirty shutdown on the populated near-full Lexar -> PASS (2026-10-29)

## Procedure
Right after G2, Lexar fitted, stick in usb000 with a free record slot. At an idle XMB the owner
switched off the rear main power switch, powered on, and accepted the same two notices as in G3a
(not turned off properly / will restart and check the file system).

## Owner report
"returned to xmb in about 3 minutes". No error message reported.

## Tool verdicts
* `read_observer.py --host <ps3-ip> --save runs/G3b-20261029 --rename-to HDD2TB-G3b.bin`
  -> PASS-UNMEASURED (record sha256 d9a4a5f8...53, renamed on the stick to `HDD2TB-G3b.bin`).
  Budget 134,217,728 B, status 0, worker 1, argc 3, failed allocs 0, largest request 62,446,924 B
  (Lexar bitmap), alloc/free 19,498 / 19,490, tracked peak 66,794,288 B (63.70 MiB, lower bound:
  TABLE_FULL + UNKNOWN_FREE, as in G2).
* `verify_retained.py --host <ps3-ip> --save runs/G3b-20261029` -> **PASS**: 236 checks,
  0 mismatches, 138.5 s.
* webMAN `cpursx.ps3`: "HDD: 65.10 GB free" (after G2: "66.0 GB free"). This is a webMAN display
  quirk: `free_size()` in `tools/webman-source/include/file/file_size.h` prints the
  decimal as (MiB % 1024) / 100, an integer 0..10. "65.10" = 65 GiB + 1000..1023 MiB (~65.98 GiB)
  and "66.0" = 66 GiB + 0..99 MiB. The real change is 1-123 MiB, not 0.9 GB.

## Game check (checklist step 7)
Owner: "checked gt6 and lbp3 no problems on both" (games and saves work). All G3b criteria met.
