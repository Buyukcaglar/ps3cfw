# M5: production cutover on the Lexar -> DONE (2026-10-29)

## Preconditions
G1, G3a PASS; G2 YELLOW (accepted); G3b PASS incl. GT6 + LBP3 game/save check. Owner decision D2.

## Filler deletion
* `delete_filler.py --host <ps3-ip>` dry run (`dry-run.out`): 55 of 55 present at the recorded
  sizes, 858.19 GiB, 0 skipped.
* `delete_filler.py --host <ps3-ip> --execute` at 13:31 UTC+3 (`execute.out`): 55 deleted,
  858.19 GiB, 0 skipped, 40 s.
* The console released the blocks in the background (`free-space.log`). Free space went from about
  66 GiB to 924.6 GB by 14:15 (rate 4-11 GiB/min, slower while FTP reads ran), then stayed at 924.6
  for three samples. Expected 65.98 + 858.19 = 924.17 GiB; the extra ~0.4 GiB fits the files' freed
  indirect blocks.
* Afterwards: no `HDD2TB-*` entries left in `/dev_hdd0/tmp` (24 other entries untouched).

## Control files
* `verify_retained.py --host <ps3-ip> --controls-only --save runs/M5-20261029` -> **PASS**:
  16 of 16 files (109,089,728 B) full SHA-256 match, 0 mismatches, 857 s (slow: disk busy releasing
  blocks). The follow-up listing in that command timed out at FTP login (console busy) and was
  repeated after the release (see above).
* Owner: GT6 and LBP3 games and saves work (checked before the deletion, in G3b).

## State after M5
Lexar NQ100 is the production drive: migrated original 1 TB contents, 924.6 GB free of 1907 GB.
The original 1 TB HDD and `vault/original-1tb-hdd` stay untouched until M6 passes.
