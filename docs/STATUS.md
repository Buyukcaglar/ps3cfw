# Status (single source of truth; keep to one page, update every session)

Last updated: 2026-10-29 (Session A and M5 done).
**Next step: M6 soak.** Normal use; once a month the owner runs `docs/checklists/M6-MONTHLY.md`.
The soak ends ~2027-01-29. M7 user guide drafted (`docs/USER-GUIDE.md`); add the soak result after M6.
**Public:** github.com/Buyukcaglar/ps3cfw (redacted export, see README "Public copy"); release
26.10.29 = P13 PUP. Re-export and push after doc changes; new release only for a new PUP.

## Console
* CECHA00, Evilnat 4.93 Cobra 8.5 CEX base, webMAN MOD (IP <ps3-ip> on 2026-10-29, DHCP).
* **Installed firmware: HDD2TB-P13 = v1.0** (D1), PUP SHA-256 `652c0c03...6d`; installed
  checker module verified (G1).

## Drives
| Drive | Where | State |
|---|---|---|
| Lexar NQ100 2 TB (production) | **fitted in PS3** | migrated original 1 TB contents; filler deleted; 924.6 GB free of 1907 GB |
| PNY 2 TB (test, disposable) | stored | native formatted, near empty; G3a passed on it |
| Crucial BX500 2 TB | stored | populated by 2026-10-12 image migration; untouched since |
| Original 1 TB HDD | stored | **owner data; never write**; raw image in `vault/original-1tb-hdd`; keep until M6 passes |
| SanDisk USB (FAT32) | PS3, rightmost port (= usb000) | P13 PUP; records HDD2TB-G3a/G2/G3b.bin; root record slot free |

## Gates (ROADMAP)
| Gate | State |
|---|---|
| G1 reinstall P13 | **PASS** 2026-10-29 |
| G3a dirty-shutdown route (PNY) | **PASS**: auto check used the 128 MiB budget, peak 61.83 MiB |
| G2 populated near-full repair | **YELLOW, accepted**: completed <4 min, 0 failed allocs, readback exact; peak >= 63.7 MiB (observer table full) |
| G3b dirty shutdown (Lexar) | **PASS**: auto check, readback exact, GT6 + LBP3 OK |
| M4 release decision | done (D1: P13 = v1.0) |
| M5 cutover | **done**: 858.19 GiB filler deleted, 16 control files exact |
| M6 soak | started 2026-10-29; monthly checks |
| M7 package | draft written (`docs/USER-GUIDE.md`); finalize after M6 |

Evidence: `runs/<gate>-20261029/RESULT.md`.

## Known facts the next agent needs
* The observer never overwrites its record (O_EXCL). After every check, run
  `read_observer.py --rename-to ...`, or the next check leaves no record.
* On the populated Lexar the observer's 16,384-slot table overflows (TABLE_FULL), so the
  peak is a lower bound. This is expected, not a failure.
* webMAN free-space decimals are (MiB % 1024) / 100, not tenths (PITFALLS 20).
* After large deletions the console frees blocks in the background (~1 h per 858 GiB).

## Owner decisions (all accepted 2026-10-29)
D1 ship P13 as v1.0 (no lean build) - D2 Lexar is the production drive, filler deleted -
D3 G3b dirty-shutdown risk on the populated Lexar accepted - D4 E01-E09/RDI retired.
