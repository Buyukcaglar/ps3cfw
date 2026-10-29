# Adaptive populated-volume fill design

This design follows the owner's choice of a populated spare Lexar. P13 remains
installed. The original 1 TB/image, populated Crucial and PNY are preserved. The
Lexar file-level copy must finish with complete verification and closed handles,
then owner boot/restart/game acceptance and HW002BA's read-only native baseline
must pass before a sustained writer is packaged or armed.

The bounded AW native I/O pilot and AZ external stop test have passed. AZ saw
the exact external stop, synced/closed its open HDD descriptor, fully verified
the retained 1 MiB payload and returned to XMB. That is not qualification of
cancellation during hours of writing or full-volume verification.

## Payload and admission

Use fresh nonce-owned ordinary files only. Maximum combined filler is 1 TiB,
in at most 64 files of at most 16 GiB each. Writes are 1 MiB; there is no sparse
preallocation, truncation, existing-file append, deletion, raw write, game/save
write or firmware modification. Each stage has a new nonce and disjoint paths.
Every opened output must use O_EXCL. Unexpected existing files fail closed.

Stage one targets 128 GiB available; stage two targets 64 GiB. Each also keeps
2 GiB metadata/background headroom and the next 1 MiB write. The target is based
on the available output of native call 840, not XMB rounding or the other raw
output. A 32 GiB stage or smaller is rejected. BA admits expected populated
available space of 512..1100 GiB; stage-two admission uses its prior checkpoint,
not that initial-population range.

The nominal new payload budget is the minimum of:

- floor((actual available - selected reserve - 2 GiB) / 1 MiB) * 1 MiB;
- 1 TiB minus all previously retained filler, rounded down to 1 MiB.

This is an upper bound, never a promise to write that amount. Query native space
before every chunk. Stop cleanly when reserve + margin + next chunk cannot fit,
at the combined cap, or at the file-count cap. Validate all additions/subtractions
before use. A file reaching 16 GiB is synced/closed and verified before opening
the next exclusive file. Enforce the same policy during cancellation/resume.

After each write, re-query space. Reject free-space errors, available greater
than the other output, outputs larger than the admitted device, or a drop larger
than payload plus a bounded metadata allowance. A reserve breach is a failed
stage, never success. Concurrent software can consume space independently;
the writer cannot guarantee a reserve against arbitrary background writes.
Run with no game, install, download or unrelated copy active. Do not reclaim
Sony/UFS reserved space to make XMB look closer to nominal 2 TB.

## Pattern, verification and ownership

Generate 64-bit big-endian words from a session seed, file index and word index
using the bijective SplitMix64 finalizer. Put file index in bits 32..37 and word
index in bits 0..30 (16 GiB file). XOR with the session seed before mixing. This
is injective within the admitted session/file/offset domain, including offsets
across 4 GiB, and makes aliasing distinguishable. Session receipts bind the full
nonce, algorithm/version, path, exact bytes and complete SHA-256.

Keep write-side hashes; fsync/close, reopen read-only and check every byte against
the independent expected pattern, SHA, exact size and EOF. After all allocation,
reread every completed file again to detect later cross-file aliasing. Compare
the 16 BA static-game controls before/after. These sampled executables do not
represent every game asset; mutable saves/databases are handled separately.
Final PC read-only extent mapping establishes actual high physical placement.

## Progress and cancellation

Reuse the accepted AV startup/SDK layout and process_exit3. No new RAM, kernel,
VSH or process-memory probe is allowed. Use fixed nonce-bound USB READY, STOP,
progress, result and DONE namespaces with exclusive creation. Keep old records.

Poll the exact STOP marker before opening an HDD output, at least every 16 MiB
during writing and verification, and at file boundaries. Publish bounded USB
progress at most every 256 MiB/phase boundary, fsync/close each receipt. The
service route is the proven single USB-to-USB webMAN copy; its next session
requires fresh WAIT/progress and absent STOP/DONE before one copy is issued.
There is no wall-clock guarantee for a stalled syscall or a dead service.

On stop, issue no more payload writes. Sync/close the current descriptor, retain
all new files, and publish a cancellation receipt naming the partial tail.
Do not spend minutes verifying a 16 GiB file before returning control. Later
read-only validation must check any partial file before another stage can be
released; do not resume or overwrite it blindly. No automatic deletion/rollback
of filler, and no replay of consumed sessions. Failures retain exact evidence
and reach process exit after bounded cleanup where syscalls return.

## Remaining native gates

1. Complete Lexar PC transaction and owner boot/restart/short game baseline.
2. Read HW002BA's exact native free-space/control receipt; bind concrete budget.
3. Review the integrated writer, fault tests, linked code, package and service
   controls. The policy/pattern model is host evidence only, not that writer.
4. Execute first fill to the 128 GiB checkpoint; full generated-byte/global
   alias/control checks, ordinary restart/persistence and same short game check.
5. Only after it passes, release the second fresh session toward 64 GiB; repeat
   checks. No 32 GiB stage, forced power loss, corruption or populated repair.
6. Final read-only PC extent/coverage evidence and populated Crucial acceptance.

The current host model implements arithmetic/decision and pattern domains only.
It opens no disks, console connection, console keys or firmware, and releases no
native writer. Universal stable/data-loss-free support remains unqualified.
