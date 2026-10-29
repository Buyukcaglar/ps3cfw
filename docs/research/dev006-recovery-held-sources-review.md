# Recovery preparation after the P13 PNY checker baseline

14 October 2026. Primary-agent source/result review; no independent human or
subagent review is claimed.

HW002AK passed the owner's explicit PNY Restore File System, unchanged-capacity
and normal-restart report. A fresh 272-byte record was independently unpacked:
one full worker, utility0, 128MiB, flags512, zero observed allocation failures,
6761 allocations/6753 frees, largest request60981796 and consistent unsaturated
partial wrapper maximum64833888 bytes. Eight objects/123088bytes were observed
before native deletion. This does not measure a leak or prove teardown returned.
The full78487-byte P13 module and two whole PNY control files match the reviewed
build/fresh AJ PC baseline. The third fixed HTTP retrieval returned404; the
earlier absent host lookup is a separate observation. No repeated checker,
console mutation, memory probe, raw-device operation or F:firmware access ran.

P13 clean checker observations now cover both PNY and Lexar native geometries.
Complete native memory/headroom/teardown, fault recovery, populated/near-full
repair, full integrity, durability and stable support remain unqualified.

## Recovery changes

The distinct controlled-recovery-v2 keeps the original host-only recovery plan
and overlay backend. It retains the original archive/sector digest, coverage,
identity, exact-before/after admission, full covered pre/post comparison and
per-sector readback behavior. A physical backend is still refused; the
host_only flag is an API contract, not a sandbox against arbitrary caller code.

Windows CreateFile sharing now holds the manifest and archive against concurrent
writers and deletion for their entire archive lifetime. Only fixed project host
evidence roots are admitted. Opened-handle final path and file type must match
the requested host file. Journals use exclusive creation or explicit existing
resume, deny concurrent writers/deletion and use write-through plus fsync.
These are host filesystem operations, not physical media durability evidence.

The new journal grammar requires one exact prepared plan, sequential attempt
numbers, a run-start after full precomparison, ordered nonoverlapping sector
intent/verification pairs, flush before completion, and no events after
completion. Duplicate fields/prepared records, unknown fields/events, invalid
types/indexes, mismatched plan pins, unfinished lines and invalid saved sequences
are refused. Explicit resume creates a new attempt boundary only after a full
covered target precomparison. It still admits only exact before/after states;
unknown/torn sector contents are refused without automatic rewriting.

48 new host cases exercise actual Windows source/journal sharing locks, actual
host journal fsync, strict valid/invalid sequences, an interruption after a
complete modeled sector write, explicit full-precomparison resume that skips
that already restored sector, and constructor/normal-close handle release.
The target writes/flush/interruption remain memory-overlay models. The original
v1 sources, 46 cases, journals and all archives remain unchanged.

A separate exercise uses the retained AJ archive with these held locks, verifies
every archive record, restores two changed host-overlay sectors (one above the
former capacity gate) and independently compares every preserved byte. AJ is
historical after AK, so this does not establish current media identity or permit
restoring its old bytes over the current PNY. The 2TB sparse host image is never
opened, hashed or modified. No root/derived decryption material is used.

## Next dependency

The current PNY has been through the native checker since its AJ capture.
A fresh post-AK preservation capture is required before changed-target physical
recovery preparation. HW002AL asks the owner for normal shutdown and connection
of only the spare PNY to the PC, with its current Windows disk number.
Lexar, populated Crucial and original1TB stay intact. No firmware update,
PS3 repair, game test or induced fault is requested.

Only the new namespace Probe-HW002AL-PnyReadOnly.ps1 is released after a fresh
matching human connection report and binding checks. It performs Windows
metadata and two fixed ATA identification queries. Its pure validators passed
18 cases and the PowerShell source parsed without errors. No physical writer,
filesystem sector capture, key use or settings changes are released by that
identity preflight. After identity succeeds, prepare a new disk-number-pinned
read-only capture. Later physical restoration still needs a separate reviewed
exact-sector adapter, current preservation, exclusive target identity/source
locks, durable journal and physical changed-fixture readback before a console
fault-recovery test. No unverified physical recovery is claimed here.
