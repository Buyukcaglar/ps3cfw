# Roadmap (revised 2026-10-29 at takeover)

## Definition of done

The project is done when an owner-usable firmware for CECHA00 + marketed 2 TB
SATA SSD has passed G1-G3 below, the owner's data runs on the 2 TB drive (M5),
and a 3-month soak (M6) shows no filesystem damage. "Stable" means **this
envelope, black-box tested**: CECHA00, Evilnat 4.93 Cobra 8.5 CEX base, the three
tested drive models, filesystem fill down to 64 GiB free, clean and dirty
shutdowns, Recovery Restore File System. It does not mean >2 TB, 4Kn, sudden
power loss during heavy writes, or a formal proof of Sony's closed-source checker.

## What changed and why

The previous plan (STABLE001, gates E01-E09) required whitebox proof of every
resource path, continuous lower bounds, every alias and route inside Sony's
checker. Those criteria cannot be finished, so each round produced another
diagnostic build (RDI1-RDI13) and another owner install + restore cycle, chasing
one kernel object that turned out to be the stock VSH printf lock singleton (see
TECHNICAL.md section 4). **E01-E09 and the RDI program are retired.** Evidence
from them is kept in `archive/`. Replacement rules:

1. Every gate has a written pass/fail criterion decidable from one bounded test.
2. Diagnostic builds are made only after a release-candidate test **fails**, to
   explain that failure. Never to prove the absence of a problem.
3. Behavior that stock firmware has too is not a regression.
4. One owner sitting per milestone; a repeat only after a FAIL with a concrete hypothesis.
5. Owner UI reports ("all green", XMB capacity, photos) are accepted evidence for UI-level outcomes.
6. Test drives (PNY) need no preservation archive before a session; they are disposable.

## Milestones

### M0: Takeover cleanup [DONE 2026-10-29]
Removed ~10 TB logical (~127 GiB real) of generated material, consolidated
protected data in `vault/`, kept the P13 build reproducible (`tools/verify_build.py`
-> READY), rewrote the docs, and recorded the history in `archive/`.

### Prep work (offline) [DONE 2026-10-29]
Tools are listed in `tools/README.md`. The FTP tools were tested against a local
FTP server, not yet against webMAN. The first real use is Session A.
* **P-1 `tools/stage_usb.py`**: copies a PUP to `<USB>\PS3\UPDATE\PS3UPDAT.PUP`
  after checking it against SHA256SUMS. It writes `.partial`, fsyncs and renames,
  then re-reads from the device with unbuffered I/O and compares SHA-256. It
  refuses targets that are not FAT32 + USB bus, and the system/boot disk.
  `--clear-observer` moves an old observer record aside.
* **P-2 `tools/read_observer.py`**: fetches the 272 B record over FTP and decodes
  it. Verdicts: PASS / YELLOW / FAIL / NO-FULL-SCAN / PASS-UNMEASURED. It was
  cross-checked against the archived parser.
* **P-3 `tools/verify_retained.py`** + `tools/data/lexar-retained-v1.json`: this
  is the read-only Lexar check. It covers 16 control files (109,089,728 B, full
  SHA-256), the sizes of the 55 filler files and 165 recorded slices, all with
  SHA-256 from the passing 2026-10-18 read. `--controls-only` is for use after M5.
* **P-4** `docs/checklists/SESSION-A.md`: 8 owner steps + the agent runbook.
* Extras: `check_installed.py` (G1 module comparison) and `delete_filler.py` (M5).

**Observer record behavior (affects every check).** The observer creates
`/dev_usb000/HDD2TB-P8.bin` with O_CREAT|O_EXCL. While a record exists, later
checks write nothing. So after each check the agent fetches the record and
renames it on the stick (`read_observer.py --rename-to HDD2TB-<gate>.bin`).
The stick never has to leave the console.

### Session A: one owner sitting covers G1, G3a, G2, G3b, then M5 (~1.5-2 h) [DONE 2026-10-29]
Checklist and agent runbook: `docs/checklists/SESSION-A.md`. Results: G1 PASS, G3a PASS,
G2 YELLOW (accepted: completed, 0 failed allocs, readback exact; the observer table overflowed,
so the peak of 63.7 MiB is a lower bound), G3b PASS. Evidence in `runs/<gate>-20261029/`.

**G1: Back to the release candidate (PNY fitted, as now).**
Stage P13 (SHA `652c0c03...`), Recovery Mode -> 6 System Update once, restore
webMAN if it vanished.
PASS: XMB returns, capacity unchanged (1658/1863 GB), one FTP read of the installed
`libfs_utility_init.sprx` equals P13's SELF (78,487 B, `7a57307b...`; `check_installed.py`).
FAIL -> reinstall once; if it still fails, stop and investigate. (Brick
recovery needs the NAND flasher + `vault/nand/`.)

**G3a: Automatic repair route after a dirty shutdown (PNY, empty, decisive).**
USB stick inserted. At idle XMB switch off with the rear main power switch. Power on.
PASS: the console runs its own file system check and returns to XMB; the
observer record shows budget 128 MiB, status 0, failed_allocs 0. Rationale: an
empty 2 TB volume needs ~58 MiB of bitmap, so any 32 MiB route would fail. A pass
proves that the automatic route uses the patched budget.
FAIL (repair error, or a record with a 32 MiB budget) -> the record/route
identifies the unpatched caller. Patch it offline (new candidate P14) and repair
the PNY via Recovery -> 3.
INCONCLUSIVE: no check message on screen and no record. The boot check may run
before usb000 mounts, so a missing record alone is not a failure. If the owner saw
a check message and the console reached XMB with capacity unchanged, that is a
PASS without a record. INCONCLUSIVE is recorded and **not repeated**; G3b and the
M6 monthly checks cover the same route.

**G2: Near-full populated repair with measurement (swap to the Lexar: ~66 GiB free, 331k+ files).**
Normal shutdown, fit the Lexar, USB inserted, Recovery Mode -> 3 Restore File System once.
PASS: completes, XMB, capacity unchanged; observer status 0, failed_allocs 0,
**peak <= 96 MiB** (75 % of the 128 MiB arena); P-3 readback all exact.
YELLOW (peak 96-128 MiB, completed): accept for the tested fill, but record that
growth headroom is thin; container slot 1 has only ~183 MiB available, so
raising the arena is not free. Plan an admission rule or algorithm change before
any fuller use.
FAIL (error/OOM) -> stop. The record's `largest_failed_request` drives a targeted fix.

**G3b: Dirty shutdown on the populated near-full Lexar (confirmation).**
Same as G3a on the Lexar right after G2. PASS: automatic check completes, P-3
readback exact, one game launches. Risk: a failure could damage the Lexar's
filesystem. Its content is a copy (original 1 TB HDD stored, raw image in
`vault/`), so the owner accepted it (D3, 2026-10-29).

### M4: Release decision (offline) [DONE 2026-10-29: D1]
* **D1 (accepted): ship P13 as v1.0.** It is the tested binary. The only
  side effect: when a USB stick is present during a check, it gets a 272 B
  `HDD2TB-P8.bin` record.
* Option: lean build (P13 minus the P6-P8 observer). It needs the P9-P13 fixes
  rebased onto P5's `libfs_utility_init` plus G1/G3a/G2 re-run. Backlog unless
  the owner wants it.

### M5: Production cutover (folded into the end of Session A) [DONE 2026-10-29]
55 filler files deleted, 16 control files verified, free space 924.6 GB. The console releases
deleted blocks in the background (~1 h for 858 GiB); keep it on until free space is stable.
Lexar becomes the daily drive (D2). Runs only if G2 and G3b passed and the
retained-data check is exact. Delete the 55 BF/BH filler files (858.19 GiB) with
`delete_filler.py`; the path list is in `tools/data/lexar-retained-v1.json`.
It deletes only paths whose size matches. Then run `verify_retained.py
--controls-only`. The owner reports the new XMB free space (~920 GB) and that
one game and save work. Keep the original 1 TB HDD and `vault/original-1tb-hdd`
untouched until M6 passes.

### M6: Soak (3 months, low effort) [STARTED 2026-10-29, ends ~2027-01-29]
Normal use. Monthly: one Restore File System with the USB stick inserted (observer
peak trend) and one game check (`docs/checklists/M6-MONTHLY.md`). Results go to
`runs/M6-<yyyymm>/` and one line in `docs/SESSIONS.md`.
Rationale: andshrew's report of inode damage after ~6 months of apparently normal use.
PASS: no repair errors, no data loss, stable peak. "Stable peak" (set before the first
check): status 0, failed_allocs 0, and the tracked peak within +10 % of Session A
(63.7 MiB). The peak is a lower bound on this populated drive, so treat it as a trend only.
Then retire the 1 TB HDD as a backup only.

### M7: Package and documentation (offline) [DRAFT 2026-10-29: `docs/USER-GUIDE.md`; finalize after M6]
User-facing README: install route, exact supported drives, limitations, rollback
(stock FW refuses >1536 GiB: refit the 1 TB HDD, never accept format prompts).
Published 2026-10-29 (owner request) as the redacted public repo github.com/Buyukcaglar/ps3cfw,
with the P13 PUP as release 26.10.29 (versions are yy.MM.dd; notes in `public/docs/releases/`).
Update: `python tools/export_public.py --out C:\projects\ps3cfw`, then commit and push from there.
Never push this private repository itself.

## Backlog (not on the critical path)
* **BIG001/BIG002 >2 TB (3-4 TB).** Needs a new gate value beyond 2 TiB, an LV2
  aggregate mount ceiling >192 KiB (runs out around 2.7-2.8 TB), checker memory
  >128 MiB (bitmap alone 87-116 MiB) within ~183 MiB container headroom, 32-bit
  sector/size audits, and LV2 region-size truncation (wiki rev 78223). Research in
  `docs/research/four-tb-*`. Separate project.
* **PERF001 throughput study.** Analysed 2026-10-29 (`docs/research/PERF001/ANALYSIS-20261029.md`):
  reads capped at ~60 MB/s by the console storage stack; writes 28.7 MB/s for ~26 GiB, then
  ~11.7 MB/s, an SSD-side cliff (cache/thermal, no TRIM), not the filesystem. Recommendation:
  no firmware performance work. Optional only: offline PC TRIM of free space (large, risky)
  or a 128-512 KiB request-size sweep (informational).
* **PS3-REPAIR-CLI.** PC-side checker/repair research in `docs/research/PS3-REPAIR-CLI/`.
* **PUB001 public from-baseline patcher.** The public repo cannot build a PUP: the P13 build
  starts from the unpublished P12 PUP and patched module. Wanted: a script that takes a
  user-supplied baseline PUP (SHA-256 `ad1c01f8...3f9a`), applies P1-P13 from published patch
  data only (byte patches, no Sony code), repacks, and must reproduce P13 SHA-256 `652c0c03...6d`.

## Owner decisions (all accepted 2026-10-29)
* **D1** Ship P13 as v1.0; the lean build stays in the backlog.
* **D2** Lexar is the production drive; delete the filler, no fresh migration.
* **D3** The G3b dirty-shutdown risk on the populated Lexar is accepted.
* **D4** E01-E09/RDI are retired in favor of the black-box gates above.
