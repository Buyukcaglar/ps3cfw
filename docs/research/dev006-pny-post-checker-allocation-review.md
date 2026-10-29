# PNY post-checker allocation finding and conservative preservation

14 October2026. P13 remains installed. Primary-agent source/result review;
no independent human or subagent review is claimed.

## Observed results

HW002AK's owner-reported PNY Restore File System, unchanged capacity and normal
restart remain passed within their requested scope. The fresh diagnostic
reported one worker, utility0, flags512, zero observed allocation failures and
partial hook maximum64833888 bytes. Full installed P13 and two whole control
files matched. These results did not establish whole filesystem integrity.

For AL, the owner reported PNY on Windows Disk4 and separately confirmed normal
controller shutdown through the red standby light. Fresh Windows/ATA queries
and opened-native-handle checks matched serial<serial>,
firmwareHT3C09BA,2000398934016bytes and512/512sector geometry.

The new strict capture refused "Allocated inode is unreachable from root."
Its stopped.json, logs and initial build/source evidence are retained. No
strict preservation archive was produced. The capture made no physical writes;
its handle closed when the process stopped. No old capture was rerun.

A separate diagnostic reused the frozen private Core DLL, invoked its geometry
constructor and Inventory(false), preserved the exact strict refusal, and only
read fields after that refusal. It saved a private decoded metadata read cache.
28 compiled identity/descriptor/schema guards passed. The corrected diagnostic
build had0warnings/0errors; the first compile failure is retained separately.
No shared or original private Core source/build was modified.

Independent Python parsing verified11614 read-cache records and110536192
payload bytes, walked the directory graph independently and checked all inode
allocation bits. It found4815 reachable nodes,4820 allocated inode bits
including reserved0/1, and three unreachable inode records:

- Inode3: allocated bit, zero-filled256-byte record.
- Inode65734790: regular file,262160bytes, link count1.
- Inode65734795: regular file,99328bytes, link count1.

The primary superblock reports clean1 and zero pending blocks/inodes. The
compiled reachable-tree ownership pass found98 nonreserved nonfree fragments
outside reachable inode extents; orphan extents were not included in that count.
This is not evidence that all98 are unexplained leaks. A prior Crucial inspection
also encountered unreachable inodes; the repeated shape is context, not a cause.

## Conservative preservation

Strict refusal was retained. A distinct read-only preservation route instead
saved every nonreserved nonfree fragment, native metadata, initialized inode
table area and any allocated inode slot beyond that initialized area, plus
outside-primary ranges. It includes the unreachable records, their allocations,
and unknown allocated fragments without reclaiming anything.

The explicit Version2 policy is
all-nonreserved-nonfree-fragments-plus-initialized-and-allocated-inode-metadata.
StrictFilesystemInventoryPassed is false in the manifest. Free payload and
uninitialized/unallocated inode space are omitted. The preservation route
links the same pinned Core DLL, uses a GENERIC_READ handle, rejects all exposed
disk write methods, and checks ATA identity before/after. Local root and returned
derived material are cleared in finally and never hashed/exported; this is not
a forensic clearing claim about every library temporary.

43 compiled guards passed: identity/schema checks plus independent host coverage
fixtures including contiguous runs, final fragment, metadata and an allocated
inode beyond initialization. Build0warnings/0errors.16GiB coverage and host free
space guards bound this disposable-fixture capture.

The3145200628-byte archive SHA256 is
2ce62545237f535b26c472f52eaa3255f2ab7edb623f3889bd8ff1b759fea8e7.
It contains9239 records and3144794112 covered bytes in6677 merged ranges.
Two full live SSD comparisons passed. Separate Python bitmap-integer coverage
derivation matched every range and independently verified every record/hash:
4820 allocated inode bits and137510 nonreserved nonfree fragments. All device
handles are closed. This qualifies byte preservation under this policy, not
semantic filesystem consistency or physical restoration.

## Offline comparison

Two separately reviewed offline programs held AJ/AL archive source locks and
verified both whole archives/record digests before local own-console key use.
No device, console or network access occurred. Fixed before/after MMS and root
directory reads showed:

- boot_plugins.txt occupied inode3 in AJ and inode4 in AL. Both full38-byte
  payloads have the established5a9655ab476cd567eb04493fd82b7517eeb4b347ecc4e154b12ac77a6cd4db3b
  hash. AJ inode3 used fragment2366; AL inode4 uses2367. Fragment2366 is among
  the allocations not owned by the current reachable tree.
- Inodes65734790/65734795 were free and zero-filled in AJ; both are allocated
  regular records in AL. Their former names and creation phase are unproved.
- The entire99328-byte orphan65734795 payload equals the current
  /mms/db/metadata_db_system.idx payload. The262160-byte orphan has no exact
  match among the five fixed named MMS files checked in either archive.
- md_schema.scm and metadata_db_hdd.idx are unchanged in these snapshots.
  metadata_db_hdd,metadata_db_system and metadata_db_system.idx changed.

The observations span a checker and multiple ordinary boots. They do not
identify whether the checker, normal MMS database replacement, another native
path or a firmware bug produced the allocations. No disk metadata was repaired,
and no allocation was freed. No firmware change is justified solely by this
strict-reader rejection.

## Next control

HW002AM requests one normal P13 PNY boot and controller shutdown, with no USB,
Restore File System, update, database rebuild, game or file transfer. Return
PNY to the PC afterward and refresh its actual disk number/ATA identity. Then
compare its read-only inode/fragment/MMS state with AL. This distinguishes an
ordinary-use change from the combined checker/boot interval; a single control
still cannot certify long-term stability or prove the earlier cause.

Lexar, populated Crucial and original1TB stay intact. No physical recovery or
fault writer is released. Complete native memory/headroom/teardown, failure
recovery, populated/near-full repair, fullcapacity, durability and>2TiB remain
open. F:firmware was neither read nor backed up.
