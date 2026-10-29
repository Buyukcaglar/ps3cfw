# HW002W native PNY preservation archive review

The initial2.4MiB geometry capture is complete and closed. For actual fixture
preservation, a private source snapshot of40Core files was copied byte-for-byte
from the published PS3HDDTool tree into analysis/dev006/pny-fixture-preservation.
The shared tree/builds and previous migration sessions are not modified or
invoked. The copied Core and a new PNY-only adapter build in their own directory.
Build succeeded with four existing CA2022 warnings in the unused PKG parser;
no PKG reader is invoked. This is a primary-agent source/interface review, not
an independent human/agent review or reuse of another session's target readback.

The adapter's capture entry invokes only TargetPreservation.CreateReadOnly with
an IDiskSource that cannot write. Native access is GENERIC_READ/OPEN_EXISTING,
denying write sharing. Exposed writes throw; there is no WriteFile, physical
flush, disk-state mutation or filesystem mount. Allowed IOCTLs query length,
storage properties and geometry/alignment. Opened PNY vendor/product, transport
serial, capacity and512/512geometry are checked before local key access. Fresh
ATA model/serial/firmware/capacity/sectors are checked before opening and after
closing that native handle. The shared bridge serial alone cannot select it.
Do not hot-swap during capture; ATA before/after is not an atomic handle query.

The first request is strict inventory. Any allocation/ownership/summary/dirty/
identity error stops without an archive completion marker or physical write.
The separately supported detached-directory mode is not released by this first
wrapper; it requires review of the strict finding and a fresh output session.
There is no general ignore/force-integrity mode.

CreateReadOnly's call chain builds a UfsVolume over the supplied read-only
transport, checks the inventory and HDD user-directory coverage, computes
preservation ranges, checks host free space, streams a new host archive, then
checks every chunk against the live target twice before publishing its manifest.
Included ranges cover allocated data/indirect/EA storage, initialized inode
records, group/backup-superblock metadata, summaries and all bytes outside the
primary volume. Free payload and uninitialized inode tables are excluded.
This is live-filesystem preservation, not whole-device forensic byte equality.

The already authorized CECHA00 root key is read locally only after identity
checks and is derived in memory; root and derived arrays are cleared in finally.
No key bytes or fingerprints are emitted. A historical same-console xRegistry
snapshot is bundled and checked for HDD user coverage. This does not establish
current flash-registry byte identity or authorize migration/profile changes.

The host-only verify/export entry invokes Verify and Export on an archive and a
new PC image path; it opens no physical drive or key. Export verifies its written
ranges, while excluded free ranges read as zero ciphertext. A verified archive/
export is still not a physically exercised restore route. No physical restore,
checker invocation, fault injection, new firmware or populated repair is released.

The compiled adapter's14synthetic identity/descriptor cases open no device/key.
All copied source, new adapter/wrapper, runtime binaries, self-test and geometry/
hardware findings are bound in preservation-review.json before native execution.
Cancellation uses a private cancel.flag and leaves the incomplete archive unused.
