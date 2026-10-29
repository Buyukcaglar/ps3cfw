# HW002Z read-only Lexar metadata capture review

This primary-agent source and host-test review releases only the new bounded PC
reader. It does not claim an independent reviewer, hardware execution, a disk
backup, repair authorization or general storage stability. HW002Y's contextual
user pass and saved photo establish native format/XMB/ordinary restart with
1698 GB free / 1907 GB total, without timings. The photo alone identifies
neither the experimental patch nor an ATA serial. Firmware remains P9 by the
prior whole-utility readback and unchanged-firmware sequence.

The new reader is tools/Capture-HW002Z-LexarGeometry.py. Old PNY capture and
replay tools remain unchanged and must not be used for Lexar. The caller must
supply a newly reported disk number after an ordinary shutdown and PC
connection; historical Disk3 is not a current binding. No physical query or
console key access has occurred in this preparation.

The reader refreshes Get-Disk inside the capture, before and after physical
reads. It accepts only USB, nonboot/nonsystem, 512/512 sectors, normalized
Lexar SSD NQ100 2TB model and 2048408248320 bytes. Fresh smartctl -j -i -d sat
queries must additionally match ATA serial <serial>, firmware SN21128
and 4000797360 sectors. The opened handle independently verifies length,
USB descriptor vendor/product and current bridge serial. The bridge serial
474238EE1A62 and bridge UniqueId are shared and are not unique ATA identity.
Bracketing identity queries and same-span rereads do not establish atomic
same-handle ATA identity or permit hot-swapping during capture.

CreateFileW requests GENERIC_READ and OPEN_EXISTING. DeviceIoControl is limited
to GET_LENGTH_INFO (0x7405c) and QUERY_PROPERTY (0x2d1400); data operations are
ReadFile and aligned SetFilePointerEx. No WriteFile, truncation, volume mount,
repair, network, disk setting or SMART test command exists. Each read is at
most 1 MiB, with a 4 MiB total including every exact consistency reread. EOF,
alignment, type, length and cumulative-budget checks precede the fake/real API.
Short reads and identity mismatches fail closed. Normal and exceptional
constructor paths close the handle; CloseHandle errors are propagated.

Only the hash-pinned pure CBC/layout helpers from inspect_crucial_metadata.py
are imported; its historical Crucial PhysicalReader/main never execute. The
own-console 48-byte eid_root_key is read only after opened-handle checks. Its
bytearray is cleared after derivation. No root/derived key contents or hashes
are output or included in evidence bindings. Python key-object memory is not
claimed securely erased. Captured metadata and directory bytes stay private.

The contract permits the known native layout family only: two partitions,
primary start32, fixed secondary4194296 sectors and8 trailing sectors. For the
measured Lexar capacity this predicts primary3996603024 sectors /2046260748288
bytes and secondary start3996603056. This is a guard expectation, not a native
Lexar observation. A differing label is saved and capture stops before
following its pointers. Primary superblock fields must satisfy canonical
16384-byte blocks/4096-byte fragments, fpg73900/ipg36992, metadata fragment
locations20/24/28/2340, zero legacy group offsets and contigsumsize8. Filesystem
size must equal the primary extent, group count must be its ceiling division,
and the16-byte-per-group summary must be fragment rounded and fit group0.
Dirty/pending/modified metadata stops without a repair attempt.

From those conditional values only: fs_size499575378, groups6761,
summary110592, aggregate110592+6761*5=144397 bytes, tail78861 and existing
131072-byte allocation class, within the inherited196608 aggregate ceiling.
The checker even-byte fragment bitmap is62446924 bytes. These expected values
must be recomputed from actual captured fields before being called measured.
The native mount formula/class analysis is in hw001h-mount-review.md. The
existing parser's cssize-only128KiB indicator is insufficient by itself;
HW002Z records and checks the full aggregate and tail separately. Neither the
bitmap nor the mount arithmetic proves a checker-wide peak or sufficient
repair-context headroom.

Capture scope is a1536-byte label,8192-byte primary superblock,1MiB primary
prefix, actual primary summary, selected middle/last16384-byte group headers,
one direct root-directory extent of at most16384 bytes and an8192-byte
secondary superblock probe. Group0 is checked inside the prefix. Summary
totals must equal the primary superblock totals. Selected group magic/index,
root inode type/size and extent bounds are checked. Every raw span is reread
exactly; before/after ATA and Windows identity must agree. This is not a scan
of all groups, inodes, allocated payload, free space or alternate superblocks.

The76 host cases use synthetic identities/descriptors, synthetic larger-drive
geometry and retained decoded PNY metadata. Fake kernel calls exercise the
actual constructor/read/close guards, final sector, invalid ranges, cumulative
budget, short reads, wrong opened model/length and constructor cleanup. AST
checks verify the physical API/access allowlist. No physical device, actual
console key or network was accessed by these tests. Host results do not
establish Lexar hardware geometry, full-capacity I/O, alias resistance,
durability, restoration or stable support.

Source, pure helper, smartctl executable, tests/results, three decoded fixtures,
prior Lexar ATA identity and HW002Y result/protocol are pinned before execution.
Outputs are exclusive and fresh under HW002Z/private, with failures preserved.
After capture independently hash/parse saved evidence, compare actual fields,
summary sums and calculated bounds. Do not trigger repair or manufacture a
new firmware revision merely for the capacity difference. Populated Crucial,
original1TB and stored PNY remain intact. F: firmware is not touched or backed
up by this work.
