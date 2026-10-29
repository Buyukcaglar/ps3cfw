# HW002W PNY baseline replay review

This is a distinct write phase after the completed read-only capture. Its only
physical target is the empty/disposable PNY supplied for checker/recovery tests,
ATA <serial>, current Windows Disk3. The populated Crucial and source
1TB remain stored. No new firmware, original-data migration, format, dirty flag
or checker operation is involved. This primary-agent review is not an independent
human/agent approval. There is no general physical recovery command.

The strict4822-node/no-orphan archive is verified against the live PNY twice;
Core Verify and sparse host export subsequently passed. Source manifest/raw
archive hashes, exact identity/geometry and3146703596-byte archive size are fixed
in the replayer. Held read-only manifest/archive handles deny writing/deletion
during verification/replay. Core Verify checks the canonical manifest/chunks;
a separate scanner validates every chunk's exact ordered range, sector bounds,
coverage and digest before opening a target. No key file is accessed by replay.

The host test altered an archived superblock sector and placed a marker in an
excluded free sector. The compiled restore rewrote/compared all3146297344covered
bytes. An independent Python parser compared all9233archive chunks, verified
the damaged sector restored and the excluded marker unchanged, then restored
that marker's original host bytes.19synthetic range/digest/identity rejection
cases also passed without disk/key/archive access. These are host observations,
not Windows physical-write or console-boot results.

The physical entry requires a pinned review and fresh Windows PNY metadata,
then fresh ATA model/serial/firmware/size/sector checks. Its exclusive native
handle is hard-coded to PhysicalDrive3 and must match the PNY vendor/product,
transport serial, size and512/512alignment before any write. The bridge serial
alone cannot identify the target. ATA is checked again after closing the handle.
There is no volume-offline, initialize, format, SAT security/settings or other
drive-selection API. Do not hot-swap during execution.

Crucially this release compares EVERY covered physical byte with the source
archive before the first WriteFile. Any changed byte aborts without writes.
It can only replay an already identical baseline; it is not released to recover
a physically corrupted/changed disk. Aligned buffers, sector/count limits,
write-through, explicit flush and complete covered-range reread are required.
Partial writes, failed flush, source/target errors or ATA changes stop with a
nonzero result. Attempt tracking reports possible writes even if the first
native write fails partially. Handles close through using/finally. The archive
stays intact for later recovery engineering; do not blindly rerun a failed writer.

Physical replay proves the native write/flush/readback path only if its result
passes, followed by a new console boot observation. It does not exercise real
corruption recovery, power interruption or whole unallocated ciphertext equality.
The archive excludes free payload/uninitialized inode space. A later changed-
fixture restoration command still needs separate review and failure testing.
Stable support, populated repair and allocator-wide memory bounds remain open.
