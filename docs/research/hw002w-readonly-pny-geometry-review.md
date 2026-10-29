# HW002W read-only PNY geometry capture review

This primary-agent review releases only the new bounded PC metadata reader.
It is not a separate human/agent review or a recovery/write authorization.
The PNY's HW002V format/XMB/restart pass is a contextual user report; its photo
shows1658GBfree/1863GBtotal. "pny connected" confirms return to PC, with fresh
Windows identification selecting the sole matching USB PNY as Disk3. The user
did not separately repeat a disk number, shutdown details or timings.

The reader verifies fresh ATA model/serial/firmware/capacity/sectors before
opening the physical handle and again after metadata consistency reads. The
opened handle must independently match full length, USB bus, PNY vendor/product
and the current transport serial. The shared bridge serial is not accepted as
unique ATA identity. ATA queries use the hash-pinned existing smartctl only
with `-j -i -d sat /dev/pdN`. No settings/self-test/unlock commands are issued.
These are stable-before/after observations, not an atomic same-handle ATA query
or permission to hot-swap during capture. No raw writer is released.

CreateFileW requests GENERIC_READ only and OPEN_EXISTING. The only IOCTLs are
GET_LENGTH_INFO and QUERY_PROPERTY. Physical data operations are ReadFile and
aligned seek, with1MiB/request and4MiB total including complete consistency
rereads. No WriteFile, truncate, mount, filesystem repair or network operation
exists. Any target/geometry/dirty-state mismatch stops without a repair attempt.
The handle is closed on normal completion and exceptions.

The existing hash-pinned inspector is safely imported for its pure CBC/layout
helpers; its Crucial-specific reader/main are not invoked. Key access happens
after opened-handle checks. Only this CECHA00's authorized48-byte local key is
read. Root-key bytearray is cleared, no root/derived key contents or hashes are
emitted, and no key is part of any evidence binding. Ordinary Python key-object
memory is not claimed securely erased.

Capture scope is the1536-byte label, primary UFS superblock,1MiB primary prefix,
106496-byte cylinder summary, selected middle/last group headers, one bounded
direct root-directory extent and a secondary superblock probe. Exact partition
and UFS geometry must match the already reviewed same-capacity layout before
following summary/root locations. Summary totals must match the superblock;
selected group headers and root-inode bounds are checked. Every captured raw
span is reread and compared. This is not a full allocated-inode/group/data scan.

All captures and any root-directory contents are kept under HW002W/private in a
new exclusive directory. Public output contains geometry/counts rather than
root-entry names. Private data captures are not cryptographic key material.
Source/review/host-guard evidence and current Windows identity are pinned before
execution. Host tests use old local decoded metadata and synthetic descriptors;
they open no physical disk and read no key. Those checks do not establish PNY
hardware results, whole integrity, full-capacity/alias behavior or restoration.

After capture, independently verify saved representations, replay partition/
superblock/summary parsing and compare geometry with the retained Crucial
capture. Design a verified restoration route before any fault/recovery test;
this metadata subset alone is not a disk backup or restorable fixture.
