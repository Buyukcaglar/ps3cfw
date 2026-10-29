# Session log (newest first; at most ~15 lines per entry)

## 2026-10-29: public repo ps3cfw + release 26.10.29 (owner request)
* New `tools/export_public.py`: copies tracked files minus exclusions (owner drive file list,
  retained-check results, TV photos, .exe/.pdb), redacts serials, LAN IPs, a USB volume GUID
  (embeds the PC MAC), NAND dump hashes, the owner's name and time zone, overlays `public/`
  (public README, release notes), then scans for key bytes and those values -> CLEAN.
* Pushed as github.com/Buyukcaglar/ps3cfw with fresh history and the noreply commit email.
  No vault, archive, keys, third-party clones or intermediate binaries.
* Release 26.10.29: P13 `PS3UPDAT.PUP` after `verify_build.py` READY; the asset was downloaded
  again and its SHA-256 matched.
* User guide made generic for public readers; private README status corrected (P13 installed).

## 2026-10-29: M7 user guide draft (offline)
* Wrote `docs/USER-GUIDE.md`: requirements, files and hashes, Recovery Mode (Sony CECH-A00 sequence),
  install, new-drive format + PS3HDDTool data move, maintenance, performance, never-do list,
  rollback order (fit a <=1.5 TB drive before the baseline), brick recovery.
* Found: `vault/nand/` dumps hold early test firmware (2026-10-11); the guide recommends a fresh
  Dump Flash backup with P13 installed.

## 2026-10-29: PERF001 performance review (offline)
* Found the native RO1 read benchmark (2026-10-17) and BH per-call write metrics (2026-10-18)
  in the archive; the PERF001 docs still called RO1 unreleased.
* Reads: ~60 MB/s inside FS calls everywhere on the disk; the old ~14 MB/s was pattern+SHA CPU.
  Random 4 KiB 0.77 ms, 64 KiB 1.28 ms; latencies suggest ~64 KiB device requests at ~1 ms each.
* Writes: 28.7 MB/s for 26-28 GiB, then ~11.7 MB/s, at 923 and at 106 GiB free alike; the cliff
  is SSD-side (cache or thermal), the floor fits no-TRIM garbage collection; allocator ruled out.
* Recommendation: no firmware performance work. Wrote `docs/research/PERF001/ANALYSIS-20261029.md`
  and `tools/perf_summary.py`; corrected TECHNICAL, PITFALLS 18 and the ROADMAP backlog.

## 2026-10-29: Session A (owner sitting) + M5
* Staged P13 on the SanDisk (SN <serial>), device re-read MATCH. Fixed stage_usb's PowerShell path and eject.
* G1 PASS: installed `libfs_utility_init.sprx` = P13 SELF; 1,658.2 GB free unchanged.
* G3a PASS (PNY): rear-switch power cut -> "will restart, check the file system" -> check completed;
  record: budget 128 MiB, status 0, peak 61.83 MiB, largest request 60,981,796 (bitmap). No P14 needed.
* G2 YELLOW, accepted (Lexar, Recovery -> 3): <4 min, status 0, 0 failed allocs, readback 236/236 exact.
  The observer's 16,384-slot table overflowed, so the peak of 63.7 MiB is a lower bound.
* G3b PASS (Lexar): power cut, auto check ~3 min, readback 236/236 exact, GT6 + LBP3 games/saves OK.
* M5 done: 55 filler files deleted (858.19 GiB); background block release took ~45 min to 924.6 GB free;
  16 control files exact. M6 soak started; monthly checklist in `docs/checklists/M6-MONTHLY.md`.
* One owner sitting, no repeats, no diagnostic builds.

## 2026-10-29: prep P-1..P-4 (offline)
* New tools: `stage_usb.py`, `read_observer.py`, `verify_retained.py` (+ `tools/data/lexar-retained-v1.json`
  extracted from the archived HW002BH contract/result), `check_installed.py`, `delete_filler.py`, `ps3ftp.py`.
* Tested locally: USB staging with device re-read (and refusal of C:/D:), observer decoding against
  the archived parser (synthetic HW002AK record -> PASS, 61.83 MiB), and the FTP tools against a local
  pyftpdlib server. Not yet run against webMAN.
* Found: the observer opens its record with O_EXCL, so each record must be renamed after its
  check. G3a can be INCONCLUSIVE (boot check before usb000 mounts); no repeat in that case.
* `docs/checklists/SESSION-A.md` written. M5 folded into the end of Session A.
* Git initialized; baseline committed. No console, device or network action.

## 2026-10-29: takeover and cleanup
* The previous agent stalled in the RDI1-RDI13 diagnostic loop (an owner firmware
  install + restore cycle per round) chasing the stock VSH printf lock. Retired
  E01-E09/RDI; new finite roadmap G1-G3, M4-M7.
* Disk use 1,118 GiB -> 991 GiB real (988 GiB is protected `vault/`); 97,010 -> ~27,000 files.
* Deleted: synthetic PS3HDDTool images and test artifacts, superseded PUPs (P1-P11,
  P2D, RDI1-11, RDI13 and duplicate copies), 19 of 20 PNY preservation archives,
  one-shot scripts, build intermediates, a writer process memory dump, duplicate docs.
* Kept per owner: original 1 TB image, both NAND dumps (plus the console key and
  other device captures). Kept PUPs: baseline, P12, P13, RDI12. Latest PNY archive.
* All text history -> `archive/history-pre-takeover-20261029.zip` (36,087 files, CRC-verified).
* The P13 build path was updated; `tools/verify_build.py` rebuilds P13 byte-exactly -> READY.
* No console, device, USB or network action.
* Owner accepted D1-D4: P13 = v1.0, Lexar = production (delete filler), G3b risk OK, E01-E09/RDI retired.
