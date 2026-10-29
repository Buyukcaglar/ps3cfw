# Source Reuse Assessment

Date: 20 October 2026. Status: candidate reuse decisions for a future C/C++ suite. No donor code has been copied or translated by this planning package.

Initial research update: [LICENSING-REUSE.md](LICENSING-REUSE.md) supplies the verified terms/inclusion decisions; [FORMAT-FINDINGS.md](FORMAT-FINDINGS.md) supplies field evidence and corrections. UFS2Xplorer remains reference-only pending source terms and provenance. Technical adaptation suitability in this table is conditional on resolving that gate; it is not permission to incorporate code. Additional selected hashes are in RESEARCH-SOURCES.json; the original snapshot is unchanged.

The [format follow-up](FORMAT-RESEARCH-2.md) adds accounting and content-policy evidence with hashes/notices in FORMAT-RESEARCH-SOURCES.json. BSD EA helpers and damaged-CG reconstruction are comparison material; neither is an unchanged safe parser or PS3 repair authority.

The [PS3 native packet](PS3-NATIVE-RESEARCH.md) adds direct artifact bindings and mapped ranges in PS3-NATIVE-SOURCES.json. Native algorithms are behavior evidence for the specification; no firmware source grant or incorporation decision is implied. The hostile-input/parser and persistence requirements still require independent implementation and qualification later.

## Source register

Line locators refer to the assessed versions. Reconcile a changed file against SOURCE-SNAPSHOT.json before relying on a locator.

| ID | Source | Role and limitation |
| --- | --- | --- |
| S01 | [UFS2Xplorer revision](https://github.com/sagemono/UFS2Xplorer/tree/565ba57e6aabf6996ed4e0512548f4b697183ace) | Native C++20 architecture and selected components; not a qualified complete repair engine |
| S02 | [UFS2Xplorer checker](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_fs/ufs2_checker.cpp#L23) | Finding categories and known ownership/coverage gaps |
| S03 | [UFS2Xplorer writer](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_fs/ufs2_writer.cpp#L872) | Selected accounting references; mutation and reclamation require redesign |
| S04 | [Disk interface](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_disk/disk_source.h#L26), [image backend](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_disk/image_disk_source.cpp#L35), [POSIX backend](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_disk/raw_device_posix.cpp#L57) | Interface sketches and platform calls; exact I/O and durable/exclusive operation need strengthening |
| S05 | [Native crypto components](https://github.com/sagemono/UFS2Xplorer/tree/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_crypto), [decrypted views](https://github.com/sagemono/UFS2Xplorer/tree/565ba57e6aabf6996ed4e0512548f4b697183ace/src/ps3hdd_cryptodisk) | Audit against independent generated vectors, all sector origins and admitted layers |
| S06 | [Generated geometry fixture](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/tests/ufs2_real_geometry.h#L19), [policy tests](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/tests/test_real_geometry_policy.cpp#L148) | Regression ideas; synthetic construction and same-checker assertions are not independent qualification |
| S07 | [Current NetBSD fsck](https://github.com/NetBSD/src/tree/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs) | Primary C algorithm donor after PS3 dialect and dependency adaptation |
| S08 | [Older NetBSD comparator](https://github.com/NetBSD/src/tree/97570233e1d596cda4d80e34fef0b2d53a7fb154/sbin/fsck_ffs) | Historical differential reference; not authentic Sony source or a safe unchanged fallback |
| S09 | [NetBSD direct writes](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/utilities.c#L347), [dependencies](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/Makefile.common#L7) | Replace system utility globals, prompts, exits and direct target writes |
| S10 | [Our UFS2 migration core](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/UfsVolume.cs:62) | Strong PS3 invariants and accounting; fails on inconsistent or unsupported starting states |
| S11 | [Our journal](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/DirectJournal.cs:78) | Ciphertext before-image and recovery design; currently requires a clean original and protects allocated payload |
| S12 | [Our recovery overlay](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/SourceRecovery.cs:43) | Useful bounded read-only overlay and narrow detached-directory recovery policy |
| S13 | [Our test scope](C:/Projects/PS3Firmware/publication/PS3HDDTool/docs/TESTING.md:23), [independent oracle](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.MigrationTests/Oracle.cs:10) | Case specifications and independent expectations; results do not transfer to future native code |
| S14 | [Our direct transport](C:/Projects/PS3Firmware/publication/PS3HDDTool/PS3HddTool.Core/Migration/DirectDisk.cs:66) | Windows identity/exclusion/alignment/durability design; other hosts need independent adapters |
| S15 | [Older C disklabel reader](C:/Projects/PS3Firmware/tools/PS3-HDD-Reader/src/device.c:419), [disklabel structures](C:/Projects/PS3Firmware/tools/PS3-HDD-Reader/src/fs/ufs/ps3.h:5) | Actual partition and nested-region references; audit bounds and licence before incorporation |
| S16 | [Native filesystem review](C:/Projects/PS3Firmware/research/filesystem-review.md:26), [checker review](C:/Projects/PS3Firmware/research/checker-budget-audit.md:50) | Binary-derived field and route evidence with explicitly bounded conclusions |
| S17 | [Current CFW context handoff](C:/Projects/PS3Firmware/analysis/dev006/metadata-budget-proof-v3/CONTINUATION.txt:1) | Concurrent offline formatter/source-proof advances; RDI2 unchanged, broader native gates open; separate task not continued here |
| S18 | [Real migration case](C:/Projects/PS3Firmware/publication/PS3HDDTool/docs/MIGRATION-CASE-STUDY.md:17) | One same-console Windows CBC migration and initial owner acceptance |
| S19 | [PS3 512e investigation](https://ps3hdd.pages.dev/blog/ps3-512e-compat/), [external repair notes](https://gist.github.com/andshrew/1d0b5e35308a6fd9770831e47950be0a) | Firsthand profile differences and bounded external fsck recovery experience |
| S20 | [Our licence](C:/Projects/PS3Firmware/publication/PS3HDDTool/LICENSE.md:3), [notices](C:/Projects/PS3Firmware/publication/PS3HDDTool/NOTICE.md:3) | Combined terms and upstream provenance; resolve incorporation before copying/translating |
| S21 | [Older C crypto profiles](C:/Projects/PS3Firmware/tools/PS3-HDD-Reader/src/types.h:59) | Fat NAND, fat NOR and Slim distinctions; validate actual profile rather than generic NOR shorthand |
| S22 | [Native resource verdict](C:/Projects/PS3Firmware/analysis/dev006/stable-resource-verdict-v1/VERDICT.txt:21) | Initialized-inode cost and separate large-capacity design; no host or 4 TB qualification inherited |
| S23 | [FreeBSD 8 comparator](https://github.com/FreeBSD/freebsd-src/tree/5381b89e043e6a4c0316344f7fe8272596d3011c), [FreeBSD 5.5 allocator](https://github.com/FreeBSD/freebsd-src/blob/d4c364b3dcf6dfe4e20c70d31912aad7e6219c14/sys/ufs/ffs/ffs_alloc.c#L1650-L1662) | Initialized inode-slot semantics and ordinary-UFS2 EA ownership; EA content scanner is a stub; neither is Sony source |
| S24 | [Upstream kpartx PS3 parser](https://github.com/opensvc/multipath-tools/blob/4cacf3347a51a7975d36109e29c15614bf7fb2ee/kpartx/ps3.c#L6-L62) | Full signatures, eight 0x90-byte entries, start/length units; reference only, not admitted repair logic |
| S25 | [Archived Glevand partition patch](https://github.com/sguerrini97/ps3linux-patches/blob/90c8c9c5ec16ac18afd3136b39b80e50475a25df/0035-ps3-partition.patch#L63-L89) | Corroborating layout with shared lineage; not independent hardware qualification |
| S26 | [Donor build dependencies](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/CMakeLists.txt#L1-L25), [declared manifest](https://github.com/sagemono/UFS2Xplorer/blob/565ba57e6aabf6996ed4e0512548f4b697183ace/vcpkg.json#L1-L15) | C++20/Qt-free design; declared baseline differs from proof of actual classic-mode dependency resolution |
| S27 | [EA kernel operations](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_vnops.c#L1168-L1245), [corrected record description](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sys/ufs/ufs/extattr.h#L78-L106) | Seven-byte comparator record framing; old FreeBSD helper differs; PS3 content binding still open |
| S28 | [Saved native accounting path](C:/Projects/PS3Firmware/analysis/four-tb-checker-cleanup-offline-20261016/checker-range-198b0-1adf4.txt:980), [allocator](C:/Projects/PS3Firmware/analysis/four-tb-alloc-cache-offline-20261014/alloc-full.txt:115) | P13 fsbtodb-derived check and runtime allocator shift; static path evidence, not uniform profile detection or conversion proof |
| S29 | [BSD compatibility flags](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sys/ufs/ffs/ffs_vfsops.c#L951-L957) | Separate legacy byte/new word and donor mutation policies; preserve PS3 fields rather than normalize |
| S30 | [CG reconstruction](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/fsck_ffs/fsutil.c#L429-L491), [probable-end scan](https://github.com/FreeBSD/freebsd-src/blob/5381b89e043e6a4c0316344f7fe8272596d3011c/sbin/fsck_ffs/inode.c#L333-L393) | Bounds checks and heuristic rebuild comparison; unscanned/free distinction and no automatic prefix reconstruction |
| S31 | [Verified native artifact/range manifest](PS3-NATIVE-SOURCES.json) | Hash-verified P4/P13 static evidence; no target execution, universal profile or source grant |
| S32 | [Native accounting/normalization selectors](PS3-NATIVE-RESEARCH.md) | Internal-HDD IDENTIFY predicate, global 9/512 and 12/4096 setter, failure-as-false hazard; complete global lifecycle open |
| S33 | [Native EA operation binding](PS3-NATIVE-RESEARCH.md) | VOP/OPD-bound BE seven-byte format and access predicates; values opaque and parser insufficient for damage |
| S34 | [Native flag branches and literals](PS3-NATIVE-SOURCES.json) | Unclean/clean masks, legacy candidate marker, ACL/MAC warnings and dependency bridge; remaining consumers/persistence open |
| S35 | [Native lazy-init listing](C:/Projects/PS3Firmware/analysis/four-tb-alloc-cache-offline-20261014/alloc-full.txt:172), [dependency registration](C:/Projects/PS3Firmware/analysis/four-tb-alloc-cache-offline-20261014/inode-metadata-initialization.txt:2) | Mutation/submission order and kernel/checker distinction; no stable-write or interruption guarantee |

## Component decisions

| Component | Decision | Required work |
| --- | --- | --- |
| UFS2Xplorer CMake and library separation | Reference design; incorporation unresolved | Keep Qt-independent core; settle terms, dependency versions and native host matrix in CLI-002/006 |
| Native CBC/XTS/key derivation | Technical adaptation candidate; reference-only now | Resolve source terms first. Prove independent known answers later; include fat NOR outer CBC, nested layers, explicit key kinds, byte order, profile and view/tweak origin |
| PS3 disklabel discovery | New bounded specification using references | S15/S24/S25 corroborate the real map. Neither our PMA/first-offset class nor actual UI discovery is authoritative; migration uses supplied partition/profile inputs |
| PS3 UFS2 field and ownership rules | Port selected S10 algorithms | Retain byte names, holes, indirect metadata, EAs, fragment tails, links and summaries; add corrupt-input coverage and checked continuation |
| UFS2Xplorer parser and extent routines | Reference now; checked adaptation only after terms resolve | Consolidate pointer iterators, validate geometry/records, preserve unknown bytes and sparse positions |
| UFS2Xplorer consistency checker | Replace integrity authority | Full inode-domain and reserved ownership must precede global conclusions; retain useful finding categories |
| NetBSD passes 1 and 1b | Adapt C algorithms | Full inode/block inventory and competing-owner identification with PS3 EA, prefix and units |
| NetBSD passes 2 through 4 and dir helpers | Adapt C algorithms and policy | Directory integrity, connectivity, reconnection and references; preserve/export before destructive disposition |
| NetBSD pass 5 | Adapt reconstruction | Rebuild maps, fragment/cluster counts, summaries and totals from complete evidence, preserving PS3 layout and replicas |
| NetBSD setup/host policy | Replace host policy | Explicit PS3 feature policy, library context and three-platform I/O; no generic flag clearing/conversion |
| FreeBSD format/EA paths | Additional pinned comparator | Useful initialized-slot, tail and ordinary-magic EA ownership evidence; eascan stub does not validate EA contents; selected terms still need inclusion audit |
| BSD EA stream helpers | Explicit-offset specification reference | Corrected seven-byte layout and kernel construction inform independent specification. Exclude old sizeof-based/NUL helper and legacy hostile-input assumptions; PS3 byte order/namespaces remain open |
| BSD damaged-CG/prefix paths | Compare decisions; replace evidence defaults | No early prefix trust, uncovered USTATE-as-free, probable-end free suffix, automatic CG zeroing or disputed lazy initialization |
| UFS2Xplorer writer | Selected arithmetic reference | Replace automatic flush, orphan lifecycle and delta-only correction with planned transactions |
| Our migration journal | Port design with new schema | Dirty originals, arbitrary changed directory/EA/indirect sectors, complete physical write units and durable sidecar publication |
| Our preservation and recovery | Port specifications and designs | Clearly distinguish allocation backup from raw image, incomplete capture, narrow recovery overlay and general salvage |
| Our migration and hash verification | Companion-suite donor | Preserve topology, raw names, holes, EAs, source-change checks and mandatory comparison as separate qualification |
| Donor tests | Reuse cases and independently derived expectations | Avoid a writer and its own checker as the sole oracle; retain disagreeing fixtures |

## Known findings that must become regression cases

These are assessed code-path findings and required future outcomes. They do not claim a reproduced device failure.

| Regression ID | Finding or incompatibility | Required future outcome | Tasks |
| --- | --- | --- | --- |
| RG-IO-01 | S04 can return requested-length zero-filled buffers after short reads | Exact unreadable coverage; no fabricated metadata or dependent write permission | CLI-025-030, CLI-037 |
| RG-IO-02 | Default no-op flush and incomplete identity/exclusion | Propagated flush failures, valid recovery state and per-host exclusion | CLI-025, CLI-045-051 |
| RG-PART-01 | Our legacy heuristic partition candidate path | Checked disklabel/length/overlap and ambiguity refusal | CLI-007, CLI-031, CLI-077 |
| RG-FMT-01 | Weak geometry and directory record boundaries | Checked arithmetic and strict partial-CG/record limits | CLI-010-013, CLI-032 |
| RG-SCAN-01 | Root traversal is not independent full ownership | Separate inode inventory and namespace evidence; unknowns block global conclusions | CLI-034-037 |
| RG-SCAN-02 | Read/traversal errors can disappear from findings | Explicit incomplete status and dependent repair refusal | CLI-037-040 |
| RG-OWN-01 | Same-inode duplicate ownership omitted | Detect data/data, data/indirect and EA aliasing even with one inode owner | CLI-033-034 |
| RG-OWN-02 | Reclamation omits indirect and EA allocations | All typed allocations accounted for before any free | CLI-012, CLI-033, CLI-041 |
| RG-SPARSE-01 | Some pointer enumeration compresses holes | Logical positions and exact hashes survive every indirect boundary | CLI-033, CLI-039 |
| RG-SYMLINK-01 | Inline symlink bytes can be interpreted as block pointers | Profile-derived inline threshold and EA ownership, including empty nodes | CLI-012, CLI-033 |
| RG-TAIL-01 | Orphan reclaim treats extents as full blocks | Correct profile-specific tail ownership and unchanged adjacent bytes | CLI-012, CLI-041 |
| RG-SUM-01 | Delta updates cannot reconstruct already corrupt totals | Independent full reconstruction and summary-only fault correction | CLI-036, CLI-042 |
| RG-POL-01 | Positive-link unreachable objects can be reclaimed | Preserve/export/reconnect policy with complete prerequisites | CLI-015, CLI-041 |
| RG-CLI-01 | Inconsistent result can exit zero and damage does not gate writes | Stable explicit outcomes and checked apply admission | CLI-024, CLI-044, CLI-066 |
| RG-TXN-01 | Writer destructor flushes and suppresses failure | No hidden target writes; explicit commit and error propagation | CLI-021-022, CLI-046 |
| RG-TXN-02 | Our undo assumes clean original and protects allocated payload | Exact dirty rollback and journaled directory/EA/indirect changes | CLI-022, CLI-045-050 |
| RG-PS3-01 | NetBSD EA semantics differ from ordinary PS3 UFS2 | Preserve EA fields, permissions, contents and ownership | CLI-012, CLI-032-036, CLI-050 |
| RG-PS3-02 | Addressing units differ from inode accounting units | Explicit source convention; no automatic host normalization | CLI-009, CLI-055 |
| RG-PS3-03 | Generic flag and format normalization | Preserve/refuse unknown features until their policy is established | CLI-010, CLI-014 |
| RG-ORACLE-01 | Same writer/checker can confirm the same mistake | Independent partial-CG, ownership, counter, byte and content oracles | CLI-020, CLI-049-050 |
| RG-PART-02 | Low-half OR signatures, wrong entry strides and ignored sizes in discovery donors | Full intact signatures and authoritative bounded lengths; damaged/ambiguous maps cannot authorize writes | CLI-007, CLI-031, CLI-077 |
| RG-KEY-01 | Same-length root/combined-CBC inputs, filename inference and legacy source secret logging | Explicit key kind/layer; no secret-valued logs/reports; independently specified wrong-kind cases | CLI-008, CLI-024, CLI-026, CLI-066 |
| RG-PS3-04 | Prefix unit resolved, but damaged prefix/bitmap/table can disagree | Inode-slot interpretation with explicit unknown coverage and bounded arbitration; no invented free/live status | CLI-011, CLI-034, CLI-037 |
| RG-PS3-05 | EA extent accounting can pass while payload scanner is a stub | Separate ownership and payload-semantic confidence; preserve/refuse unsupported EA repair | CLI-012, CLI-032-036, CLI-050 |
| RG-PS3-06 | Same flag bit has different meanings in donor dialects | Versioned PS3 policy; no donor-mask clearing or automatic normalization | CLI-010, CLI-014, CLI-032 |
| RG-DIR-01 | Existing parser is not a complete proof of NUL/minimum directory-record rules | Independently specified terminator, alignment, minimum length, block boundary and slack preservation | CLI-013, CLI-035, CLI-050 |
| RG-ACCT-01 | Native fsbtodb-derived accounting, fixed-/512 BSD accounting and unresolved allocator selector can disagree | Named-profile count evidence; mixed/insufficient cases remain unwritable; no majority normalization | CLI-009, CLI-012, CLI-034, CLI-042, CLI-050 |
| RG-EA-01 | Old sizeof/NUL helper conflicts with seven-byte EA kernel framing | Independent byte offsets, all alignment boundaries, raw non-NUL names and spanning records | CLI-012, CLI-020, CLI-032, CLI-050 |
| RG-EA-02 | Duplicate/malformed/unknown EA content can affect permissions despite valid extents | Separate ownership/framing/semantic results; preserve original stream, namespace and inode modes | CLI-012, CLI-014, CLI-041, CLI-050 |
| RG-FLAG-01 | Legacy/new fields and donor masks can trigger incidental conversion/replay/clearing | Preserve both fields and dirty/pending/snapshot state; no generic replay or feature reset | CLI-010, CLI-014, CLI-032, CLI-045, CLI-050 |
| RG-PREFIX-01 | Early prefix trust and uncovered status defaults can turn unknown into free | Validate before dependent work; explicit coverage states block global rebuild/clean decisions | CLI-011, CLI-034, CLI-037, CLI-042, CLI-050 |
| RG-PREFIX-02 | First-record probable-end heuristic, nonzero free generations and lazy zeroing can hide/destroy survivors | Later-survivor and interrupted-init cases; no automatic shrink/grow/zero/reclaim over disputed ranges | CLI-011, CLI-012, CLI-020, CLI-041, CLI-050 |
| RG-NATIVE-ACCT-01 | Console-global IDENTIFY predicate, query failure-as-false and shared unit state can misclassify an unrelated/mixed image | Image-bound provenance, unknown query outcome, exact raw predicate cases, non-4096 fragments and no host-driven normalization | CLI-009, CLI-026, CLI-032, CLI-042, CLI-050 |
| RG-NATIVE-EA-01 | Bound native BE EA format coexists with unchecked walk, first-match keys and opaque values | Independent bounded BE parsing, duplicates/malformed streams, credential/namespace distinctions and unchanged modes/values | CLI-012, CLI-014, CLI-032, CLI-041, CLI-050 |
| RG-NATIVE-FLAG-01 | Native mount can mutate flags/pending counts and issue warning-only feature branches | Full scan despite clean byte; no incidental replay, pending-count reset, legacy upgrade or assumed ACL enforcement | CLI-010, CLI-014, CLI-032, CLI-045, CLI-050 |
| RG-NATIVE-INIT-01 | Kernel dependency/mutation/submission order differs from P13 repair allocation and durable order is unknown | Separate operation provenance, proposed interruption states, completion/error dependencies and no disputed prefix growth/zeroing | CLI-011, CLI-014, CLI-037, CLI-041, CLI-045, CLI-050 |

The S02 checker starts from root, suppresses some reads, omits EA ownership and same-inode duplicates, and lacks a complete inspection state. Its finding cap does not bound ownership maps or recursive work. S03 reclamation uses full blocks without complete indirect/EA ownership; summary updates use stored baselines; its destructor can flush during error unwinding. The CLI does not reliably block those branches or return an unsuccessful final status. These findings make it a diagnostic and regression donor, not the future repair gate.

NetBSD current pass1 supports EAs under a distinct format magic and can clear EA fields/permissions on ordinary UFS2. The older comparator disables the EA ownership walk. Both need PS3 adaptation. Its generic flag conversions and fixed inode-accounting convention require separate profile rules. See [current EA handling](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/pass1.c#L426) and [older handling](https://github.com/NetBSD/src/blob/97570233e1d596cda4d80e34fef0b2d53a7fb154/sbin/fsck_ffs/pass1.c#L420).

## Provenance and dependency gate

CLI-002 must inventory each file as verbatim, adapted, translated, reference-only or independently specified. Record the assessed commit/hash, original notices, modifications and distribution basis. Public hosting is not the reuse decision.

- Our source carries BSD-3-Clause AND LicenseRef-WNT-CPYLFT-1.3.0; a C# to C++ translation must not be assumed to remove those obligations.
- The older C reader has GPLv2 declarations, GPL-2.0-or-later AES wording, individually BSD-noticed files and an unmarked PS3 header. Keep each file's actual terms; direct reuse remains undecided.
- The newly sampled current NetBSD fsck files have three-condition BSD headers. Other selected headers/helpers need their own inventory; do not assign a single licence to the whole utility or new FreeBSD comparator.
- The assessed UFS2Xplorer tree and 45-file marker inventory supplied no verified source grant; the explicit licence covers icons. README credits PS3HDDTool derivation. Resolve new-contribution grants and inherited provenance before incorporation.
- Crypto providers, build helpers, testing dependencies and distributed binaries need their own inventory.

Research and comparison can continue while a candidate's incorporation remains unresolved. No release gate may treat technical similarity as licence clearance.

## Evidence already earned

S13 records 200 migration regressions and a generated sparse 1 TB-to-2 TB stress fixture, not a fully populated terabyte copy. S18 records one real same-console CBC migration. Preserve these as bounded donor evidence rather than future C++ acceptance.

S06 uses generated sparse geometry and commonly the same writer/checker. Its final partial group needs a correct independent fixture. The new corpus must include cases that pass one donor and fail another, with the disagreement explained from bytes and specification.

