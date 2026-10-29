# PS3 Accounting Attributes Flags and Inode Initialization

Date: 20 October 2026. This follow-up advances the four remaining format investigations through pinned source comparison and saved native-analysis text. The new facts support a more precise format specification; PS3 profile acceptance and damaged-state repair policy remain open. All proposed rules below are planning requirements, not an implemented or tested parser.

The accounting comparison now has a saved PS3 checker path linking inode allocation counts to fsbtodb. EA record framing can be specified for a corroborated BSD-family format, with a concrete old-header discrepancy excluded. Flags require separate legacy/new fields and dialect-specific meanings. Damaged inode prefixes require independent coverage evidence rather than a guessed replacement prefix.

Source revisions, raw-byte hashes, selected local hashes and notice classifications are in [FORMAT-RESEARCH-SOURCES.json](FORMAT-RESEARCH-SOURCES.json). [FORMAT-FINDINGS.md](FORMAT-FINDINGS.md) remains the initial disk/crypto/field register. No source incorporation, product development, builds/tests, new fixture execution, private keys, media inspection, console actions or publication occurred.

## Accounting variants

ACC-01. In the saved P13 [checker listing](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-198b0-1adf4.txt:980), VA 0x1a7f8..0x1a828 loads fs_fsize at superblock+0x34 and fs_fsbtodb at +0x64. It computes fs_fsize / (fs_fsize >> fs_fsbtodb), multiplies the counted-fragment accumulator and compares the result with UFS2 di_blocks at inode+0x18. For admitted positive power-of-two geometry and a valid shift, the factor is 2^fsbtodb. This is a concrete saved source-path relationship, not a universal rule inferred from USB sector presentation.

The [fragment callback](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-194f8-198b0.txt:28) increments the count even on some range-error paths. A count match therefore cannot establish valid ownership. This pass does not prove every data/indirect callback or malformed-inode route. Listing provenance records a P13 checker ELF of 224,208 bytes, SHA-256 e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86; that binary was not opened, rerun or re-disassembled here.

| Named candidate | Fragment bytes | Stored fsbtodb | Count units per owned fragment in this path | Derived bytes per di_blocks unit |
| --- | --- | --- | --- | --- |
| Conventional example | 4096 | 3 | 8 | 512 |
| Alternate published example | 4096 | 0 | 1 | 4096 |

ACC-02. The firsthand [PS3 512e investigation](https://ps3hdd.pages.dev/blog/ps3-512e-compat/) reports the same two conventions in its stated CECH-2503A/OFW 4.90 comparison. Its 24,576 allocated bytes correspond to di_blocks 48 or 6. It also reports that the console restored fsbtodb=0 after host modification. This observation supports the source-path interpretation without establishing that every 512e device, bridge, model or firmware uses that convention.

ACC-03. The saved [allocator listing](C:/Projects/PS3Firmware/analysis/four-tb-alloc-cache-offline-20261014/alloc-full.txt:115) updates UFS2 di_blocks by allocation size shifted by a runtime global. A prior offline model's seeded shift is not the console's observed runtime value. The complete relationship between that global, physical/format geometry and the checker's stored-shift convention still needs a named-profile trace. Do not use the synthetic model to establish 512e behavior.

ACC-04. Our [migration inventory](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/UfsVolume.cs:360) and generic NetBSD accounting use /512. They cannot judge the alternate convention unchanged. Addressing, inode accounting, crypto sectors, host logical sectors and physical write units stay separate quantities, but an identified PS3 profile may explicitly relate some of them. In particular, the inspected native checker derives its comparison factor from fsbtodb; the earlier generic warning that fsbtodb alone is not a universal unit declaration remains valid across unknown/mixed inputs.

ACC-05. A concrete source-derived counterexample prevents universal inference: FreeBSD 8 [newfs](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/newfs/mkfs.c#L248) sets fsbtodb from fragment size divided by formatting sector size, while lines 830-831 initialize root di_blocks through btodb. Its [param.h](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/sys/param.h#L117-L177) gives that accounting a default 512-byte unit. The reviewed source can therefore describe shift 0 with /512 counts, unlike the saved PS3 checker relationship. This is a source counterexample, not a generated or executed filesystem.

ACC-06. Saved [normalization instructions](C:/Projects/PS3Firmware/analysis/four-tb-8k-offline-20261014/checker-review/normalization.txt:1) contain selector-controlled shift 3-to-0 and 0-to-3 transitions followed by superblock-write paths. The [readsb path](C:/Projects/PS3Firmware/analysis/four-tb-8k-offline-20261014/checker-review/readsb-variable-device-unit.txt:35) separately derives its I/O unit from fragment size and stored shift. Full selector meaning, writer consistency and persisted results were not established. Treat normalization as a separate policy and possible provenance complication, not proof that changing one header field safely converts every inode.

### Proposed accounting admission

| Evidence | Classification and permitted conclusion |
| --- | --- |
| Named profile, valid geometry and matching independent typed-extent accounting | Use that profile's documented count unit and address translation. Keep the stored convention. |
| Most or all inode counts differ by a common factor | Profile hypothesis only. Shared corruption, incomplete traversal and host-modified fsbtodb remain possible; do not rewrite counts from majority agreement. |
| Stored shift conflicts with retained provenance or independently known metadata | Mixed or unresolved interpretation. Preserve both candidates and refuse count normalization. |
| Zero-length, sparse, inline-link or special inode lacks allocated extents | It may provide no distinguishing unit evidence. Include indirect and EA ownership where applicable; file length is not allocation size. |
| Duplicate, unreadable or unsupported extent domain | Ownership/count evidence is incomplete. A plausible numerical equality does not authorize map/count repair or clean certification. |
| Invalid signed shift, zero shifted divisor, overflow, impossible geometry or partial input | Reject the conversion before address arithmetic, allocation or division. Do not copy native instruction behavior on malformed metadata. |

Remaining accounting research: full named-profile checker/allocator consistency, all inode types and EA/indirect contributions, pending-free units, provenance for externally normalized images, cropped views, and explicit unsupported native 4Kn handling. Later independent fixtures must distinguish both conventions and mixed metadata at low/high addresses. No count correction or host normalization was performed.

## EA contents

EA-01. The corrected [NetBSD record description](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sys/ufs/ufs/extattr.h#L78-L106) and pinned [FreeBSD 8 kernel operations](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_vnops.c#L1168-L1245) corroborate this BSD-family stream layout:

| Record offset | Width | Meaning |
| --- | --- | --- |
| +0 | 4 | Total record length |
| +4 | 1 | Namespace identifier |
| +5 | 1 | Value-tail padding count |
| +6 | 1 | Raw name length |
| +7 | Name length | Raw name bytes; no guaranteed terminating NUL |
| align8(7 + name length) | Derived | Value begins after name padding |

Value length is record length minus value-start offset minus value-tail padding. The next record begins at the preceding record's declared end. There is no per-record filesystem-block boundary requirement. Length is copied in native byte order in this FreeBSD implementation; this alone does not prove PS3 EA payload byte order.

EA-02. The old [FreeBSD 8 extattr.h helper](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ufs/extattr.h#L75-L111) describes a NUL-terminated name and uses sizeof(struct extattr) in its base-length calculation. Kernel construction instead uses seven fixed bytes; at some name lengths padding is zero and a copied terminator can be overwritten by value data. Exclude that helper as a layout oracle. Independent future cases must straddle every eight-byte name/value boundary rather than agree with a transplanted struct.

EA-03. Kernel [append/replace logic](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_vnops.c#L1701-L1760) zeroes padding, moves later records for size changes and preserves a sequential stream. Lookup chooses the first matching namespace/name. Those facts make duplicates and noncanonical padding important findings; they do not justify silently sorting, deduplicating or rewriting a damaged stream. Its legacy parser is not a sufficient hostile-input validator.

EA-04. FreeBSD's [namespace registry](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/sys/extattr.h#L38-L47) assigns user=1 and system=2. Its [ACL structures/names](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/sys/acl.h#L71-L122) and [ACL checks](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ufs/ufs_acl.c#L147-L190) demonstrate a separate permission-sensitive payload format. The older [UFS1 .attribute backing-file mechanism](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ufs/ufs_extattr.c#L473-L477) does not supply a UFS2 stream prefix. These are comparator semantics, not a verified Sony namespace/ACL registry.

EA-05. Saved [PS3 labels](C:/Projects/PS3Firmware/analysis/four-tb-fileio-offline-20261014/ufs-labels.json:14) name EA-related functions and provide future static-research anchors. Labels alone do not bind the BSD stream format to a native implementation or establish a PS3-created nonzero-EA specimen. Our migration core validates EA extent length/ownership, not EA records or value semantics. Native extent-accounting evidence must remain separate from content validation.

EA-06. The saved P13 [ordinary-UFS2 branch](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-198b0-1adf4.txt:1190), VA 0x1ab40..0x1ac20, handles positive extsize, two EA addresses and a fragment-rounded final extent before calling the count descriptor. This strengthens PS3 extent-ownership corroboration. It does not establish payload framing, namespaces, permission consequences or a complete corruption validator.

### Proposed EA coverage and repair policy

Validate the seven-byte fixed header before field access; use checked offsets; require positive eight-byte-aligned record length within remaining stream bytes, padding count 0..7 and value-start plus padding no larger than record length. Bound the containing extents and exact reads independently. Permit block-spanning records and zero-length values in the comparator specification. Complete structural parsing means every declared stream byte is accounted for; it does not establish namespace/value semantics.

Keep separate results for extent ownership, record framing, namespace recognition, value semantics and native-profile acceptance. Until PS3-specific evidence closes the gaps, preserve order, raw names, values, padding, unknown namespaces and malformed tails. Duplicate keys remain ambiguous. Do not resynchronize a damaged tail into original authority, clear EAs, free their storage, translate host ACLs or normalize inode permissions automatically.

Remaining EA research: PS3 payload byte order, actual namespace/name registry, ACL/MAC/Sony values, canonical padding/order and native behavior on malformed/duplicate records. A named-profile native function trace or appropriately authorized nonzero-EA metadata evidence is still needed. New kernel/header sources have individually inventoried BSD notices; they were not incorporated.

## Feature flags and dirty state

FLG-01. The legacy byte fs_old_flags at superblock+0xD3 is distinct from the newer word fs_flags at +0x520 in the [PS3 reader layout](C:/Projects/PS3Firmware/tools/PS3-HDD-Reader/src/fs/ufs/fs.h:320). In the [FreeBSD compatibility path](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_vfsops.c#L951-L957), the legacy byte's 0x80 marker controls relocation of flags and sblockloc. The future tool must preserve/report both raw fields and identify the admitted layout; it must not OR them together, copy one over the other or perform an incidental format upgrade.

FLG-02. This is a source-version comparison, not the PS3 feature registry:

| Bit | FreeBSD 8 register | Current NetBSD register |
| --- | --- | --- |
| 0x01 | UNCLEAN | UNCLEAN compatibility value, marked unused |
| 0x02 | DOSOFTDEP | DOSOFTDEP |
| 0x04 | NEEDSFSCK | NEEDSFSCK compatibility value, marked unused |
| 0x08 | INDEXDIRS | SUJ |
| 0x10 | ACLS | POSIX1EACLS |
| 0x20 | MULTILABEL | MULTILABEL |
| 0x40 | GJOURNAL | GJOURNAL |
| 0x80 | FLAGS_UPDATED | FLAGS_UPDATED |
| 0x100 | No definition in this inspected register | DOWAPBL; comment notes a conflicting FreeBSD NFS4ACL use |
| 0x200 | No definition in this inspected register | DOQUOTA2; compatibility comment names a FreeBSD INDEXDIRS use |
| 0x400 / 0x800 | No definition in this inspected register | TRIM / NFS4ACLS |

Sources: [FreeBSD flags](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/fs.h#L378-L411), [NetBSD flags](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sys/ufs/ffs/fs.h#L430-L448). The 0x100/0x200 compatibility comments must not be attributed to definitions in FreeBSD 8. Matching a donor's known mask does not prove PS3 support.

FLG-03. [NetBSD setup](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/setup.c#L186-L206) can replay WAPBL based on its interpretation; lines 277-282 can clear flags outside its known mask. [FreeBSD mount logic](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_vfsops.c#L688-L720) clears indexed-directory state, derives UNCLEAN and can zero pending counts. These operating-system behaviors are excluded as generic PS3 repair policy. A wrong dialect can change semantics before ordinary checking even begins.

FLG-04. Our [migration admission](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/UfsVolume.cs:74) permits only word bits within 0xB2 and requires zero pending frees and snapshot entries. allowDirty permits fs_clean=0 but does not relax that word mask, so bit 0x01 still fails this public constructor. Bits 0x10/0x20 being admitted by that mask is not an implementation of PS3 ACL/MAC validation. This is a clean-source migration contract, not a complete dirty-volume scanner or feature specification.

FLG-05. An existing [PS3 mount review](C:/Projects/PS3Firmware/research/hw001h-mount-review.md:17) records fs_clean=1, fs_flags=2 and pendingblocks=0 for its stated captured layout. That bounded observation does not assign semantics to every bit or prove the filesystem consistent. No new media was inspected. Pending counts, clean bytes, flags, snapshots and replicas must remain separate evidence, including contradictions between them.

### Proposed flag and dirty-state decisions

| Condition | Planning rule |
| --- | --- |
| Named profile with understood flags and complete prerequisites | Full inspection may proceed. A clean byte never skips the requested integrity scan. |
| Unknown bit, conflicting dialect or unresolved legacy/new flag authority | Preserve fields; report unsupported interpretation; withhold dependent repair authority. |
| ACL/MAC, journal, quota, snapshot or other allocation-affecting feature | Require its actual PS3 semantics/ownership policy. Do not clear the bit or assume the feature absent because payload was not found. |
| Nonzero or contradictory pending frees / dirty markers | Preserve the state and allocations; do not turn pending counters into disposable space. Require explicit complete reconstruction and a qualified state-transition policy. |
| Candidate repair reaches a consistent overlay | Clean-marker/flag changes still need their own profile rule and transaction prerequisites. An originally dirty rollback restores the original dirty bytes. |
| Replica flags or transient fields disagree | Record per-copy values and timestamps/context where available. Do not propagate every field indiscriminately to every alternate. |

Remaining flag research: PS3 bit semantics and legacy marker behavior for each admitted firmware/layout; feature activation and ownership; pending-free transitions/units; and exact mutable/replicated field policy. Known donor behavior supplies research cases rather than authority to emulate it.

## Damaged initialized inode prefixes

PFX-01. Stored cg_initediblk is an inode-slot prefix, while an in-memory trimmed scan/status count is a different quantity. [FreeBSD newfs](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/newfs/mkfs.c#L324-L383) rounds fs_ipg to INOPB; stored initialization starts at min(ipg,2*INOPB) and [lazy allocation](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_alloc.c#L1777-L1789) advances by INOPB. Block alignment is therefore a candidate stored-prefix invariant for this source family, still needing PS3 profile confirmation. A trimmed working count may be unaligned.

PFX-02. Current [NetBSD pass1](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/pass1.c#L100-L174) trusts the prefix for scan/status sizing before bounds/alignment validation; pass5 only clamps later. Its [inoinfo fallback](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/utilities.c#L591-L604) represents slots beyond allocated status as USTATE. The future scanner needs explicit unknown/unscanned state, never an uncovered-to-free default. Validate CG identity, geometry, map spans, prefix range and admitted alignment before dependent reads, indexing or allocation.

PFX-03. [FreeBSD 8 CG checking](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/fsck_ffs/fsutil.c#L429-L491) adds niblk/ipg and prefix/fragment bounds, but its accepted-CG test is not a complete identity/map/alignment validator. An accepted rebuild zeroes the CG and starts a replacement prefix; [pass1 reconstruction](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/fsck_ffs/pass1.c#L154-L200) uses probable-end heuristics. Such synthetic metadata is a candidate, not recovered original authority.

PFX-04. The [FreeBSD probable-end check](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/fsck_ffs/inode.c#L333-L393) tests a first buffered inode's plausibility and can stop before later surviving records. Newfs/lazy initialization also assign nonzero random generation values to otherwise free slots. A zero record, nonzero generation, plausible inode or failed early probe cannot independently determine live/free state or initialization history.

PFX-05. Our [migration constructor](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/UfsVolume.cs:93) validates useful CG/map bounds and prefix range. Its inventory rejects allocated/referenced slots beyond the prefix rather than repairing them. Its lazy allocator can zero table ranges while extending initialization; that behavior cannot be carried over to a disputed range. The saved [native conditional proof](C:/Projects/PS3Firmware/analysis/dev006/metadata-budget-v1/prefix-bound-proof.json:37) requires valid bounds and no allocated bit beyond the prefix. The [trim snippet](C:/Projects/PS3Firmware/analysis/dev006/metadata-budget-v1/prefix-source/group-initial-and-trimmed-prefix.txt:49) reduces a working count under two route flags; it does not rewrite the stored prefix in the inspected range. Qualification remains false.

### Proposed prefix evidence and coverage policy

PFX-06. Keep distinct evidence dimensions: declared initialized range, bytes actually read, bitmap allocation, directory references, structural plausibility, validated ownership, unknown ranges and stale/salvage candidates. They cannot be collapsed into one allocated boolean.

| Evidence condition | Coverage and planning conclusion |
| --- | --- |
| Admitted profile; valid CG/maps; candidate-aligned prefix; complete reads; no allocation beyond prefix | Inspect declared [0,N) plus independent bitmap/reference/ownership domains. N is not a live-inode count. |
| Oversized prefix, wrong identity, invalid/overlapping maps or unknown alignment | Initialized extent is invalid or unresolved. No prefix-dependent allocation or automatic round/clamp repair. |
| Zero/short prefix contradicts a required or referenced inode | Preserve contradiction. Do not substitute two blocks, ipg or the highest set bit. |
| Allocated bit or directory reference beyond prefix | Bound candidate reads independently; mark competing claims disputed. No automatic bit clearing, prefix growth, reclaim or lazy zeroing. |
| Clear bitmap bit but plausible/referenced record inside prefix | Allocation evidence conflicts. Neither plausibility nor bitmap alone wins. |
| Unreadable table/maps/CG bytes | Unknown coverage blocks dependent global map/summary reconstruction, leak reclaim and clean certification. |
| Plausible unreferenced bytes beyond an admitted prefix | Stale/salvage candidate only; no automatic resurrection or ownership assignment. |
| Donor-style rebuilt CG or probable-end stop | Retain as synthetic alternative/partial coverage, not proof of a free suffix. |
| Resource or cancellation stop | Report unfinished ranges; do not redefine the initialized/live endpoint. |

Remaining prefix research: PS3 stored alignment/minimum/zero cases, cg_niblk consistency, lazy-init persistence ordering and interrupted initialization, arbitration when prefix/bitmap/table are simultaneously damaged, and independent damaged-state cases. Reading the entire inode table can improve salvage coverage but cannot by itself recover allocation intent or initialization history. Prefix shrink/growth and table zeroing remain unqualified repair actions.

## Validation requirements and current status

New planned cases must cover both accounting conventions, global-shift disagreement, mixed normalization and incomplete ownership; seven-versus-eight-byte EA header helpers, all alignment boundaries, non-NUL names, spanning/duplicate/unknown records; legacy/new flag conflicts and same-bit dialects; and prefix contradictions, nonzero free generations, early-record damage followed by survivors, interrupted lazy initialization and resource stops. These are specifications for later independent fixtures, not executed cases.

CLI-009/010/011/012/014 remain in progress with partial source findings. CLI-002/007/008 retain their earlier research state. The other 75 tasks remain planned. No gate or support tuple closes from this packet. The next research should target PS3-specific native bindings and damaged-state arbitration; it should reuse the verified comparator facts rather than repeat initial feasibility or transplant donor repair policy.
