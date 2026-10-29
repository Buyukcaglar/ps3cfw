# Working rules for agents on PS3Firmware

Read `docs/STATUS.md` first, then the relevant milestone in `docs/ROADMAP.md`.
Background: `docs/TECHNICAL.md` (patch set, addresses, evidence), `docs/PITFALLS.md`.

## Anti-loop rules (the reason this file exists)
1. Work only toward a ROADMAP gate. Each gate has a fixed pass/fail criterion;
   do not add criteria after the fact or demand proofs of Sony internals.
2. No new diagnostic firmware unless a release-candidate test **failed**, and then
   only to explain that failure. "Not yet proven" is not a failure.
3. If stock firmware behaves the same way, it is not a regression. Check before investigating.
4. One owner sitting per milestone. Batch steps. A second sitting needs a recorded
   FAIL plus a concrete hypothesis. Never ask the owner to repeat an approval.
5. Owner reports ("all green", XMB capacity, photos) are valid evidence for UI outcomes.
6. If two consecutive sessions end without moving a gate, stop and tell the owner
   plainly what is blocking, instead of planning another round.

## Docs discipline
* `docs/STATUS.md` = current state, at most one page, overwritten each session.
* `docs/SESSIONS.md` = append one entry (newest first, <= 15 lines) per session.
* Gate evidence goes to `runs/<gate>-<yyyymmdd>/` (RESULT.md + small captures).
  No per-step directories, no hash-pinned custody chains, no "consumed script" registries.
* Plain ASCII/UTF-8 without BOM. No compressed or telegraphic prose.
* Do not recreate README/ROADMAP/PROMPT copies of the same log.

## Protected data (see `vault/MANIFEST.md`)
* Never delete, modify or publish `vault/`. The owner's ruling: the original 1 TB image
  and the NAND dumps must stay. Never print or export `vault/console-keys/eid_root_key`.
* Keep `firmware/baseline-*`, `HDD2TB-P12`, `HDD2TB-P13` and whatever is installed on the console.
* `archive/history-pre-takeover-20261029.zip` is read-only history; read it with Python `zipfile`.

## Device safety
* PC-side raw disk access: identify the drive by ATA model + serial every time (disk
  numbers change). Read-only by default. Any raw write needs explicit owner approval
  naming the serial. Never let Windows initialize/format a PS3 drive.
* Never touch the original 1 TB HDD. Never use the unrelated exFAT drive (was `F:`).
* Before staging any PUP: `python tools/verify_build.py`, then re-read the staged
  file and compare SHA-256.
* Console access is read-only via webMAN (HTTP/FTP at the IP the owner reports);
  no RAM probing, no writes unless the gate requires them.

## Owner checklist template (one sitting, <= 10 numbered steps)
Goal of the sitting / what to have ready (drive, USB, power) / numbered steps with
the exact menu path (e.g. "Recovery Mode: hold power until the 2nd beep, then option 3") /
"what to report": XMB free/total, any message text or photo, webMAN IP / stop rules:
never accept format, rebuild or Restore PS3 System prompts; do not interrupt a running check.

## Environment
Windows 11, Python `C:\Python314\python.exe` (3.14), git, .NET SDK 10. Bash and
PowerShell are both available. PowerShell 5.1: use `-LiteralPath` and `-Encoding utf8`.
Third-party tools under `tools/` are their own git clones; project-owned scripts are `tools/*.py`.
