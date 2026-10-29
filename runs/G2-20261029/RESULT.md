# G2: Restore File System on the populated near-full Lexar -> YELLOW, accepted (2026-10-29)

## Procedure
After G3a: normal shutdown, PNY replaced by the Lexar NQ100 (SN <serial>),
SanDisk stick in usb000 with a free record slot. Recovery Mode -> 3 Restore File System, once.

## Owner report
"back at xmb, took less than 4 minutes". No error message reported.

## Tool verdicts
* `read_observer.py --host <ps3-ip> --save runs/G2-20261029 --rename-to HDD2TB-G2.bin`
  -> PASS-UNMEASURED. Record valid (sha256 0e83a9f6...15), renamed on the stick to `HDD2TB-G2.bin`.
  * budget 134,217,728 B (patched), utility status 0, full worker calls 1, argc 3,
    heap create/delete 1/1, **failed allocs 0**, largest failed request 0.
  * largest request 62,446,924 B = the Lexar bitmap (as predicted).
  * alloc/free calls 19,512 / 19,504. Tracked peak 66,793,920 B (63.70 MiB).
  * flags 560 = INCOMPLETE_COVERAGE (normal) + **TABLE_FULL** + UNKNOWN_FREE. More than 16,384
    chunks were live at once, so the observer's table (16,384 slots) overflowed. Later chunks
    were not counted, and their frees show as UNKNOWN_FREE. So 63.70 MiB is a lower bound.
    The free wrapper always calls the native free (`prepare_p8_native.py`, label free_native),
    so the overflow affects only the measurement, not the checker.
* `verify_retained.py --host <ps3-ip> --save runs/G2-20261029` -> **PASS**: 236 checks
  (16 control files full SHA-256, 55 filler sizes, 165 slices), 0 mismatches, 145 s.
* webMAN `cpursx.ps3`: HDD 66.0 GB free (unchanged), uptime 53 s after the restart.

## Classification against the fixed G2 criteria
* Completed, XMB, capacity unchanged, status 0, failed_allocs 0, readback exact: all met.
* "peak <= 96 MiB": not decidable from this record. The true peak lies between 63.70 MiB (tracked)
  and 128 MiB (no allocation failed). Estimate: at most 19,512 - 16,384 = 3,128 untracked chunks;
  at the tracked non-bitmap average (~265 B) that adds ~0.8 MiB, giving ~64.5 MiB. This is an estimate,
  not a bound.
* Therefore **YELLOW** (completed; headroom below 96 MiB not established), accepted for the tested
  fill (66 GB free) per ROADMAP. Not a failure: no diagnostic build (CLAUDE.md rule 2).
  Before any use fuller than the tested envelope, plan an admission rule or a measurement fix.
