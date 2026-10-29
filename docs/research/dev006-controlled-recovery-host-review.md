# Controlled recovery preparation after the P13 clean checker

14 October 2026. Primary-agent source and result review; no independent human
or subagent review is claimed. This is host prototype evidence and a release
of read-only PNY identity queries, not a physical recovery writer or fault test.

HW002AI passed the reported P13 Lexar Restore File System/XMB/capacity/ordinary
restart sequence. A fresh 272-byte diagnostic was independently unpacked:
one full worker call, utility status 0, 128 MiB requested budget, flags 512,
6935 observed allocations / 6917 frees, zero observed allocation failures,
largest request 62446924 and partial wrapper accounting maximum 66388880 bytes.
Eighteen objects / 127504 bytes precede native deletion; this is not a leak
measurement or proof that teardown returned. Whole 78487-byte P13 SELF and two
whole HDD control files match before exactly. Diagnostic SHA256 is
df60c222a78078c2647b8ea57fb4bb167a2907f630d83a9e244e4224ff8fffa1.
The small allocation-count variation from earlier clean runs is recorded without
attributing it to P13's helpers. Complete native allocator coverage remains open.

## Gap being addressed

The consumed HW002W physical replayer accepts only an already identical PNY.
Its successful same-byte replay did not prove that a deliberately changed
physical fixture can be restored. The retained archive also predates subsequent
PNY use, so it must not replace a new current-drive preservation capture.
No old writer, physical handle, shared PS3HDDTool build or original host image
was invoked in this preparation.

## New host prototype

analysis/dev006/controlled-recovery-v1/host_recovery.py reads an explicitly pinned
archive and verifies its full manifest, record coverage/digests and whole-file
SHA256 before admitting a plan. Each plan lists at most 32 distinct, ordered,
512-byte sectors inside preserved coverage, with exact allowed current bytes
and exact archive baseline bytes. Source identity, disk length and archive hash
are bound. All covered target bytes are compared before any target write.
Unlisted differences and unknown partial-sector states are rejected.

A host journal records the complete plan and before/after bytes with fsync
before target mutation. Each changed sector is reread after the intent record,
written once and read back. After a target flush, all preserved ranges are
compared again. Explicit resume repeats full precomparison and admits only the
plan's exact before/after states; complete journals are consumed. A torn sector
or malformed journal is refused rather than automatically overwritten.

The only included target backend is a memory overlay over a read-only archive.
There is no physical transport, console API, key access or sparse-image writer.
The host-only backend flag is an API contract, not a security sandbox against
someone supplying different Python code. Journal paths are limited to the new
host-journals directory. Python source files and test artifacts are preserved.

40 initial and 6 additional host cases passed. They cover identity/geometry/
range/coverage/digest rejection, unplanned and unknown changes, journal collision,
interruption between complete sector writes, interruption after a complete
write before its progress record, safe explicit resume, short target reads,
changed data before a write, short writes, readback mismatch, journal durability
failure, malformed journals and target-flush failure. The tests exercise actual
host journal fsync; target media writes/flushes and interruptions are modeled.
They do not establish atomic physical sectors or power-loss durability.

The retained PNY archive was read-only and fully verified:
3146703596 archive bytes, SHA256
d51e04e241517196c473e31eddc99d75b2c727be78c3357271f2b69d623195d5.
Two host overlay sectors at offsets 81920 and 2000398933504 were changed and
restored. All 3146297344 preserved bytes were compared before and after.
A separate sequential parser checked all 9233 record digests and target bytes.
The high host offset demonstrates integer/address handling in this prototype,
not native PS3 full-capacity I/O or >2 TiB support. The old 2 TB sparse image
was never opened, hashed or modified. Excluded free/uninitialized regions are
not covered by this archive or by the claimed comparisons.

## Next hardware dependency and release scope

HW002AJ requests only connection of the stored spare PNY to the PC and its
current Windows disk number. Lexar stays fitted in the PS3; populated Crucial
and original 1 TB stay stored intact. No firmware update or PS3 repair is needed.

The new Probe-HW002AJ-PnyReadOnly.ps1 requires a fresh matching connection
report and sealed bindings. It refreshes Windows non-system USB model/size/
sector identity, runs two fixed smartctl -j -i SAT identification queries with
bounded waits, and requires the exact known PNY ATA model, serial, firmware,
capacity, sector count and 512/512 geometry. Eighteen pure validation cases
passed and PowerShell parsing reported zero errors. Tests imported only the two
validation functions; the preflight's device-query main has not run.

This first read-only preflight opens no filesystem image or decryption key and
changes no device settings. After identity verification, a new read-only native
capture/preservation adapter must be prepared for that actual device number.
It must prove current inventory, coverage and recovery data before any new
physical writer can be separately reviewed. No raw writer, restore, mutation,
fault injection or native recovery experiment is released here.

Future physical recovery still needs fresh media identity and preservation,
exclusive opened-handle identity checks, held source locks, a separately reviewed
exact-sector writer, flushed physical readback and demonstrated changed-fixture
restoration. Arbitrary changed disks, torn-sector automatic recovery, unknown
differences, full forensic preservation, actual checker fault recovery, populated
or near-full repair, complete native memory/headroom/teardown, durability and
stable support remain unqualified. P13 itself is unchanged.
