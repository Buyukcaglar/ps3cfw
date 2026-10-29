# PS3 Native Selectors Attributes Flags and Initialization

Date: 20 October 2026. Read-only static examination of the saved P4 kernel and P13 checker advances the four PS3-specific questions left by FORMAT-RESEARCH-2.md. The allocator's unit selector, the EA storage format, several feature-flag branches and lazy-initialization instruction order now have native evidence. Complete profile admission, security-value interpretation and durable interrupted-write recovery remain open.

No product development, source incorporation, builds, target execution/emulation, fixture/model tests, installation, keys, media, device/console actions or publication occurred. Inline disassembly and byte hashing are static research. Earlier packets' statements that binaries were not reopened describe those earlier packets; this packet explicitly inspected the following existing artifacts after hash verification.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| analysis/build-p4-v3/lv2-patched.elf | 3641960 | dc9d6e24fb5bd9eaa15678e8fc1b2076cc0358a1be574d87a9f14e0fa468280a |
| analysis/p13-review/utility-P13.native.elf | 224208 | e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86 |
| analysis/build-p13-first/candidate.native.elf | 224208 | Same checker bytes under a second existing path |

[PS3-NATIVE-SOURCES.json](PS3-NATIVE-SOURCES.json) binds selected inputs, ELF mappings, raw range hashes, native flag excerpts and pointer/string bindings. Kernel addresses below abbreviate prefix 0x8000000000000000. Kernel file offsets in these ranges are low VA+0x10000; checker code uses VA+0xF0. Address names inferred from behavior are distinguished from literal symbol/descriptor bindings. Firmware bytes are research evidence, not a source-code grant for incorporation.

## Allocator and normalization selectors

NAC-01. The allocator's runtime shift is now identified beyond the earlier model assumption. Its module TOC chain reaches shared shift word VA 0x3684f0, initialized to 9; adjacent word 0x3684f4 is initialized to 512. The allocation update at 0x1f3fc4..0x1f3fd8 uses that shift for di_blocks. A real setter at 0x2bc218..0x2bc230 stores 12 and 4096 into those same globals. Its caller invokes predicate 0x2a6a78 and branches to the setter when the low return byte is nonzero. A returned buffer word +0x34 equal to 0x800 bypasses that predicate; its semantic name remains unresolved. The other branch sets a local 512 value but does not reset both globals in the inspected code.

| Link | Native VA | File offset | Value |
| --- | --- | --- | --- |
| Kernel TOC +0xD8 | 0x34fc88 | 0x35fc88 | Module TOC 0x308440 |
| Module TOC -0x7F10 | 0x300530 | 0x310530 | Shift pointer 0x3684f0 |
| Shift / adjacent size | 0x3684f0 / 0x3684f4 | 0x3784f0 / 0x3784f4 | Initial 9 / 512 |
| Setter's module TOC slot | 0x352188 | 0x362188 | Module TOC 0x30a440 |
| Setter stores | 0x2bc22c / 0x2bc230 | 0x2cc22c / 0x2cc230 | New 12 / 4096 |

NAC-02. Kernel predicate 0x2a6a78..0x2a6dc4 removes identifier bits 32..39 and requires the remainder to equal 0x0101000000000007. The [local storage header](C:/Projects/PS3Firmware/tools/cobra-source/8.5/4.93/CEX/SRC/lv2/include/lv2/storage.h:9) names that identifier ATA_HDD and uses the removed field for partitions. The function queries device information, has an early false path for an output byte +0x47, opens the device and sends command 0xEC with a 512-byte response. [Microsoft's ATA documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ata/ns-ata-_identify_device_data) corroborates IDENTIFY DEVICE and the sector-related fields; the calls and constants here come from native bytes.

For the returned raw IDENTIFY bytes, define H=byte[0xD5]&0xF0, E=byte[0xD4]&0x0F and V=LE32(bytes[0xEA..0xED]). V is a count of words before any conversion to bytes. The kernel and P13 selector implement this predicate:

| H | True condition |
| --- | --- |
| 0x60 | E equals 3 |
| 0x50 | V nonzero, low eight bits zero, and V&0xFFF equals zero |
| 0x70 | V nonzero, low eight bits zero, and (V shifted left by E)&0xFFF equals zero |
| Other | False |

Native anchors are kernel 0x2a6c5c..0x2a6dc0 and checker 0x11920..0x119f8. Word 106 value 0x6003 satisfies the first case. The extended cases test raw words, so this is not a complete ATA geometry decoder or proof of native 4Kn support. Device-info byte +0x47 and all query-status semantics remain incompletely named.

NAC-03. P13 helper 0x11708..0x11904 zeroes a 512-byte caller buffer and hardcodes the internal-HDD identifier. It uses storage syscalls 600/open, 616/device-command and 601/close, with command byte +0x0B=0xEC, selector 2 and length 512. The caller at 0x11904 collapses helper failure into false. This is a console-internal-HDD predicate, not a query bound to an arbitrary image/backend or necessarily the descriptor passed to normalization.

The [normalization path](C:/Projects/PS3Firmware/analysis/four-tb-8k-offline-20261014/checker-review/normalization.txt:78) calls that selector: true explicitly sets this helper's working unit to 4096 and changes stored shift 3 to 0; false changes shift 0 to 3. Later readsb derives its unit as fs_fsize/(1<<fsbtodb), so stored 0/3 imply 4096/512 only for 4096-byte fragments. Other values and failure/alternate-superblock branches require their own admission. Following write calls are statically present; successful completion and persisted consistency were not exercised. A failed identification can therefore select a conversion branch in the donor. The new CLI must retain absent/failed identification as unknown rather than copy this false-default policy.

NAC-04. Together with the native di_blocks calculation in ACC-01, these paths supply a concrete mechanism consistent with the two observed accounting conventions. They do not establish complete global lifecycle/reset/alias behavior, concurrency or multiple-volume effects, all formatting/writer/pending-free interactions, cross-firmware consistency, or original units in a damaged/mixed image. Preserve image-specific provenance and raw counts; do not use the host's current ATA response or majority agreement to normalize an image from another context.

## EA payload binding and access behavior

NEA-01. The previous label-only gap is closed for this P4 artifact. Named VOP descriptors and ELFv1 function descriptors bind actual EA operations:

| Operation | Operation-pair VA | Named descriptor | Function descriptor | Code VA |
| --- | --- | --- | --- | --- |
| Get | 0x35ffd8 | 0x360f80 | 0x335bf0 | 0x20ac90 |
| List | 0x35ffe8 | 0x360fb8 | 0x335bd8 | 0x20aab0 |
| Open | 0x35fff8 | 0x360ff0 | 0x335b60 | 0x209658 |
| Set | 0x360008 | 0x361060 | 0x335c20 | 0x20ae50 |
| Delete | 0x35ffc8 | 0x361028 | 0x335c38 | 0x20b304 |
| Close | 0x35ffb8 | 0x360f48 | 0x335c08 | 0x20adf8 |

Each function descriptor uses kernel TOC 0x34fbb0. Open/read 0x209228 reaches dinode extsize at +0x5C; the [native mapping path](C:/Projects/PS3Firmware/analysis/four-tb-fileio-offline-20261014/bmap-rest.txt:1), VA 0x20bfd8..0x20bff8, maps logical blocks -1/-2 through EA addresses +0x60/+0x68. This establishes an inode-backed stream path rather than a diagnostic-string resemblance.

NEA-02. Native lookup at 0x209098 reconstructs a BE32 record length from offsets +0..3, reads namespace +4, value-tail padding +5, name length +6 and name bytes +7. Value start is align8(7+N); value length is L-start-pad. It returns the first matching key. Setter 0x20ae50 constructs that same big-endian seven-byte format, zeroes padding and bounds a new EA area to two filesystem blocks. These close framing and byte order at source level for this artifact. Native get/set transfer opaque value bytes; the old BSD sizeof/NUL helper remains excluded.

NEA-03. Permission helper 0x2c2214 recognizes namespaces 1 and 2 for non-null credentials. Namespace 1 invokes a vnode access operation; get/list supply mask 0x100 and set/delete 0x80. Namespace 2 calls 0x2b177c, which succeeds exactly when credential word +4 equals zero. The conventional root interpretation is an inference; that word predicate is direct evidence. Other namespace values return 0x80010009. A null credential bypasses this namespace check, so names/values from an offline image cannot be interpreted solely through the non-null-credential path.

NEA-04. Generic EA-write progress at 0x20a9ec..0x20aa20 can clear inode special-permission bits 0xC00 for a nonzero credential word +4. This is ordinary permission-side behavior of the write path, not proof of ACL payload interpretation. The generic EA routines do not demonstrate Sony-specific value schemas or name-specific ACL decoding. The mount warnings in NFL-04 likewise separate EA storage support from ACL/MAC enforcement.

NEA-05. Native parsing is not a damaged-input validator: the lookup reads length before a complete fixed-header check and lacks the proposed positive-length/name/padding bounds before its observed walk. A zero length can prevent progress. Reuse the explicit byte specification and preservation requirements, not this parser unchanged. PS3-created names and value schemas, consumers, full permission paths, malformed-stream handling, cross-firmware variants and interrupted EA persistence remain open. No nonzero user EA specimen or runtime access result was obtained.

## Native feature flags and clean state

NFL-01. At 0x2ca900..0x2ca934 the mount path reads fs_flags at +0x520, masks out bits 0x01 and 0x08, clears fs_fmod, then sets bit 0x01 if fs_clean at +0xD1 is zero. The separate remount path 0x2ca4d0..0x2ca4f0 clears/rederives bit 0x01 similarly. This directly corroborates an unclean-state role for bit 0x01 in the inspected kernel; it is not a finding that the underlying disk was damaged.

NFL-02. Dirty read/write admission at 0x2ca94c..0x2ca960 tests bits 0x04 and 0x02 alongside mount mode/force-related conditions. An inspected teardown path at 0x2c9c9c..0x2c9cb8 sets fs_clean to 1 exactly when fs_flags&0x05 is zero, then calls helper 0x2c868c with wait argument 1. Its nonzero-return branch forces the clean byte back to zero at 0x2c9e14. This supports bit interactions, not an independent consistency proof or stable-storage guarantee.

NFL-03. Ordinary-UFS2 superblock candidate admission at 0x2caaa0..0x2caabc compares stored sblockloc with the candidate offset. If they disagree, it tests the sign of legacy byte +0xD3: bit 0x80 set rejects/retries that candidate; bit clear permits the older-layout path. This establishes a native marker use in selection. It does not prove every legacy-field conversion/write rule, and does not authorize the CLI to copy, OR or upgrade flag fields.

NFL-04. At 0x2cafec and 0x2cb008 the mount path tests bits 0x20 and 0x10. Resolved TOC pointers lead to diagnostic literals reporting multilabel without MAC support and ACL flags without ACL support. These native warnings bind the labels to this route; they do not prove every kernel consumer lacks those features. Their presence also does not make generic EAs unsupported. Unknown feature combinations and values remain preserved until the relevant behavior is established.

NFL-05. The superblock bit 0x02 branch at 0x2cb16c..0x2cb204 calls 0x1feec0. That helper sets mount word +0xAC mask 0x00200000 at 0x1feed0/0x1feed4. The inode allocator tests that mount mask before dependency registration at 0x1f4358..0x1f436c. This is now a concrete bridge from the feature branch to the initialization dependency hook. Separately, native mount/reload/teardown paths can zero pending counts in memory; the inspected initial-mount path does so at 0x2cab40..0x2cab48 after diagnostics. None of these donor mutations is automatic host repair authority.

Remaining flag work concerns full legacy conversion/write semantics, every relevant feature consumer and failure path, pending-free units/transitions, snapshot/quota/other bits, replica propagation and cross-firmware behavior. Flags and clean bytes remain evidence fields, never substitutes for complete ownership and content coverage.

## Interrupted inode initialization

NIN-01. Kernel allocator 0x1f40a8..0x1f4640 now establishes this path order in the saved artifact:

| Instruction range | Action established |
| --- | --- |
| 0x1f4358..0x1f436c; 0x1f4560..0x1f457c | Selects the dependency route, then calls 0x205b80 at 0x1f4578 before bitmap mutation |
| 0x1f4370..0x1f43c4 | Sets inode bit, decrements CG/global/group free counts and marks modified state |
| 0x1f444c..0x1f44e0 | Tests UFS2 initialization threshold and obtains the next inode-table block buffer |
| 0x1f44e4..0x1f4534 | Zeroes one filesystem block and writes each 256-byte inode's generation field +0x50 with helper-derived nonzero value |
| 0x1f4538..0x1f4544 | Adds fs_inopb to CG+0x78 after preparing table bytes in memory |
| 0x1f4418..0x1f441c | Schedules/marks the CG buffer through helper 0x1ea468 |
| 0x1f4420..0x1f442c | If present, dispatches the table buffer through helper 0x1e6128 |
| 0x1f4430..0x1f4440 | Returns the allocated inode number |

NIN-02. Table helper 0x1e6128 marks buffer flag 0x04 and enters 0x1e6060, which invokes a descriptor through buffer+0xD8, slot +8. CG helper 0x1ea468 is a delayed-dirty scheduling path. The allocator does not test those helper returns before its inode return. This does not prove errors are lost globally: callback, dependency and lower-layer reporting remain material. The dependency path at 0x205b80 creates/links metadata state, but its complete prepare/completion/failure graph is not established.

Thus instruction order is now known; durable order is not. No physical cache flush, stable-write completion, atomic prefix/table update or power-loss guarantee follows from an asynchronous call or successful inode number.

NIN-03. P13 repair allocation is a different path. The [repair allocator](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-16d80-172e0.txt:2), VA 0x16d80..0x172e0, selects an inode-status byte equal to 1, sets its allocation bit, decrements free count and populates one inode through 0x16b5c. This complete routine does not update CG+0x78 or initialize a whole inode block. The [fallback-status helper](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-140d4-14188.txt:2) and its initialization/lifetime need separate evidence; uncovered status is not proof of free space. The [pass5 path](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-1d208-1e73c.txt:416) copies or clamps an existing prefix; it does not establish the corresponding bytes were initialized.

NIN-04. Future interruption cases must distinguish the following retained evidence. These are candidate states requiring investigation, not claims that every state is reachable under the native dependency machinery.

| Retained evidence | Required interpretation boundary |
| --- | --- |
| Old prefix with prepared zero/generation bytes beyond it | Could be unpublished initialization or stale data; no automatic growth |
| New prefix with old/torn/unreadable table bytes | Initialization history unknown; no automatic certification or lazy zeroing |
| New prefix with generations but incomplete inode mode/data | Prepared records are not necessarily committed live inodes |
| Allocation bit beyond prefix or counters disagreeing with table | Competing claims; preserve and block dependent reclaim/global reconstruction |
| Plausible inode beyond prefix with clear bitmap | Stale/unpublished/damaged-map candidate; no automatic resurrection |
| Unknown write completion or checker-created metadata | Separate transaction/repair provenance; no inherited kernel crash guarantee |

The next source work must bind actual CG/table buffer operations and dependency callbacks through completion, retry and failure, then trace later inode and directory publication. First-format minimum/alignment and cross-profile behavior also remain open. Whole-table reading or generation patterns cannot recover original allocation intent alone.

## Planning consequences and remaining gates

The source-level advances are specific: default/runtime accounting states and selectors are identified; EA framing, byte order and operation binding are established in P4; low flag behaviors and a dependency bridge are traced; kernel versus checker initialization is distinguished. The remaining questions are now lifecycle, consumers, persistence and damaged-state arbitration rather than basic comparator layout.

Add independent future cases for selector acquisition failure and image/device mismatch; raw ATA predicate cases including non-generalized extended logical sectors; shared global 9/512 versus 12/4096 and missing reset; BE EA records, first-match duplicates, unknown namespaces, null/non-null credentials and opaque values; clean/legacy marker disagreements and ACL/MAC warning-only paths; and each initialization interruption state with dependency enabled/disabled. No such fixtures were executed here.

CLI-009/010/011/012/014 retain partial research status; CLI-002/007/008 remain in progress and 75 tasks remain planned. All 13 gates remain not_assessed and passed=false. Source evidence does not release development, complete a supported profile, prove native repair, or establish durable recovery. Native 4Kn and greater-than-2-TiB console acceptance remain separately unqualified.

## Concurrent project context

During validation, the separately owned README and three plan roots changed from the original source snapshot. Their current context was refreshed without overwrite: the active handoff is now analysis/dev006/metadata-budget-proof-v3/CONTINUATION.txt, reporting offline formatter/source-proof advances with installed RDI2 unchanged and broader native/profile/resource gates still open. That separate task was not continued here. The new manifest records current context hashes separately from historical baselines; PLAN-VALIDATION.json distinguishes unchanged research inputs from this recorded context drift. The hash-bound P4/P13 artifacts used above remain the stated versions, without borrowing acceptance from the newer offline variants.
