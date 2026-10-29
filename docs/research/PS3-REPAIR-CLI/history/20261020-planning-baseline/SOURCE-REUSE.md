# Source Reuse Assessment

Date: 20 October 2026. Status: candidate reuse decisions for a future C/C++ suite. No donor code has been copied or translated by this planning package.

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
| S17 | [Latest reviewed CFW handoff](C:/Projects/PS3Firmware/analysis/dev006/metadata-budget-workload-v2/CONTINUATION.txt:1) | Resource, recursion and failure questions; broader native gates remain open |
| S18 | [Real migration case](C:/Projects/PS3Firmware/publication/PS3HDDTool/docs/MIGRATION-CASE-STUDY.md:17) | One same-console Windows CBC migration and initial owner acceptance |
| S19 | [PS3 512e investigation](https://ps3hdd.pages.dev/blog/ps3-512e-compat/), [external repair notes](https://gist.github.com/andshrew/1d0b5e35308a6fd9770831e47950be0a) | Firsthand profile differences and bounded external fsck recovery experience |
| S20 | [Our licence](C:/Projects/PS3Firmware/publication/PS3HDDTool/LICENSE.md:3), [notices](C:/Projects/PS3Firmware/publication/PS3HDDTool/NOTICE.md:3) | Combined terms and upstream provenance; resolve incorporation before copying/translating |
| S21 | [Older C crypto profiles](C:/Projects/PS3Firmware/tools/PS3-HDD-Reader/src/types.h:59) | Fat NAND, fat NOR and Slim distinctions; validate actual profile rather than generic NOR shorthand |
| S22 | [Native resource verdict](C:/Projects/PS3Firmware/analysis/dev006/stable-resource-verdict-v1/VERDICT.txt:21) | Initialized-inode cost and separate large-capacity design; no host or 4 TB qualification inherited |

## Component decisions

| Component | Decision | Required work |
| --- | --- | --- |
| UFS2Xplorer CMake and library separation | Adapt design | Keep Qt-independent core; settle dependency versions and native host matrix in CLI-006 |
| Native CBC/XTS/key derivation | Audit then adapt selected code | Prove generated known answers against independent PS3HDDTool expectations; include nested layers, byte order, profile and absolute/relative LBA |
| PS3 disklabel discovery | New bounded parser using references | S15/S21 supply format evidence. Do not adopt our legacy heuristic Ps3DiskLayout.cs as repair authority; it takes an in-range candidate without validating the filesystem |
| PS3 UFS2 field and ownership rules | Port selected S10 algorithms | Retain byte names, holes, indirect metadata, EAs, fragment tails, links and summaries; add corrupt-input coverage and checked continuation |
| UFS2Xplorer parser and extent routines | Reference or checked adaptation | Consolidate pointer iterators, validate geometry/records, preserve unknown bytes and sparse positions |
| UFS2Xplorer consistency checker | Replace integrity authority | Full inode-domain and reserved ownership must precede global conclusions; retain useful finding categories |
| NetBSD passes 1 and 1b | Adapt C algorithms | Full inode/block inventory and competing-owner identification with PS3 EA, prefix and units |
| NetBSD passes 2 through 4 and dir helpers | Adapt C algorithms and policy | Directory integrity, connectivity, reconnection and references; preserve/export before destructive disposition |
| NetBSD pass 5 | Adapt reconstruction | Rebuild maps, fragment/cluster counts, summaries and totals from complete evidence, preserving PS3 layout and replicas |
| NetBSD setup/host policy | Replace host policy | Explicit PS3 feature policy, library context and three-platform I/O; no generic flag clearing/conversion |
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

The S02 checker starts from root, suppresses some reads, omits EA ownership and same-inode duplicates, and lacks a complete inspection state. Its finding cap does not bound ownership maps or recursive work. S03 reclamation uses full blocks without complete indirect/EA ownership; summary updates use stored baselines; its destructor can flush during error unwinding. The CLI does not reliably block those branches or return an unsuccessful final status. These findings make it a diagnostic and regression donor, not the future repair gate.

NetBSD current pass1 supports EAs under a distinct format magic and can clear EA fields/permissions on ordinary UFS2. The older comparator disables the EA ownership walk. Both need PS3 adaptation. Its generic flag conversions and fixed inode-accounting convention require separate profile rules. See [current EA handling](https://github.com/NetBSD/src/blob/acb07d978136d3b5a8032fe3dac4b7321db4da1f/sbin/fsck_ffs/pass1.c#L426) and [older handling](https://github.com/NetBSD/src/blob/97570233e1d596cda4d80e34fef0b2d53a7fb154/sbin/fsck_ffs/pass1.c#L420).

## Provenance and dependency gate

CLI-002 must inventory each file as verbatim, adapted, translated, reference-only or independently specified. Record the assessed commit/hash, original notices, modifications and distribution basis. Public hosting is not the reuse decision.

- Our source carries BSD-3-Clause AND LicenseRef-WNT-CPYLFT-1.3.0; a C# to C++ translation must not be assumed to remove those obligations.
- The older C reader declares GPLv2 and remains reference-only until the reuse/distribution decision is resolved.
- The inspected NetBSD files carry two- or three-condition BSD notices; enumerate every included header/helper instead of assigning one licence to the entire utility.
- The assessed UFS2Xplorer tree lacks a top-level source licence, while its README credits PS3HDDTool derivation. Resolve permissions/provenance before incorporation.
- Crypto providers, build helpers, testing dependencies and distributed binaries need their own inventory.

Research and comparison can continue while a candidate's incorporation remains unresolved. No release gate may treat technical similarity as licence clearance.

## Evidence already earned

S13 records 200 migration regressions and a generated sparse 1 TB-to-2 TB stress fixture, not a fully populated terabyte copy. S18 records one real same-console CBC migration. Preserve these as bounded donor evidence rather than future C++ acceptance.

S06 uses generated sparse geometry and commonly the same writer/checker. Its final partial group needs a correct independent fixture. The new corpus must include cases that pass one donor and fail another, with the disagreement explained from bytes and specification.

