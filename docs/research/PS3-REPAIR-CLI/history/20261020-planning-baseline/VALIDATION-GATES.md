# Validation Gates

Date: 20 October 2026. All G00-G12 gates are not assessed for the future C/C++ suite. These are acceptance requirements for later authorized work. Planning-document checks are recorded separately in PLAN-VALIDATION.json.

## Evidence and capability ledger

Each result binds exact source revision, host OS/version/architecture, backend/bridge, crypto layers and sector origin, partition/filesystem dialect, geometry/accounting convention, operation and capacity. Record source-reviewed, compiled, generated-validated, image-validated, physical-validated and console-accepted independently. Never collapse them into a single tested flag.

Read, scan, export, plan, image apply, physical apply, recovery, backup/restore and migration qualify separately. Every report includes coverage, primary error, cleanup/recovery state, input identity and plan binding. Private keys and unrequested payload contents are excluded from audit artifacts.

## Gate register

| Gate | Required result | Closure evidence |
| --- | --- | --- |
| G00 Requirements provenance and custody | Exact scope and candidate reuse decisions; explicit user authority per future action | Requirements, profile schema, source/notice inventory and preservation rules |
| G01 PS3 format and repair specifications | Byte-exact profiles, units, flags and action/refusal rules | Field/invariant catalogue, annotated independent structures and unresolved-feature register |
| G02 Independent corpus and oracles | Fixture construction and expectations independent from product writer/checker | Corpus manifests, known-answer vectors, oracle review and deliberately disagreeing cases |
| G03 Shared core crypto and image I O | Exact I/O, bounded parsing, crypto and appropriate host builds | Per-target build results, generated vectors, checked arithmetic and I/O faults |
| G04 Complete bounded UFS2 inspection | Full supported ownership/graph/accounting evidence and honest incomplete status | Coverage maps, independent ownership/counter outputs, resource and read-only evidence |
| G05 Reviewable plans and overlays | Deterministic justified changes, preconditions and independently verified isolated results | Action plan, sector allowlist, overlay manifest and byte/content comparisons |
| G06 Image repair and transaction recovery | Verified completion or defined recoverability at every failure point | State-machine review, cut-point matrix, recovery receipts and retained failures |
| G07 Per platform physical qualification | Every advertised OS/backend/architecture operation has exact transport acceptance | Disposable-media identity, exclusion, I/O, flush/readback and removal receipts |
| G08 Per profile console acceptance | Exact admitted layouts and accounting survive approved native use | Baseline preservation, repair findings, console results and post-use independent comparison |
| G09 FAT checking and repair | FAT12/16/32 separately checked and repaired with recovery, plus exact dev_hdd1 native operation acceptance | Independent FAT cases, plans, byte diffs, fault recovery and dev_hdd1 console results |
| G10 VFLASH and partition repair | Nested bounds and critical role semantics preserved | Raw/nested before-images, map arbitration, restore and separate console acceptance |
| G11 Companion suite | Capture, export, archives, restore and migration preserve coverage, source custody and destination confinement | Acquisition/read-map integrity, hostile archive/path, topology/content and interrupted-operation evidence |
| G12 Complete suite release | Exact artifacts and advertised tuples satisfy all relevant mandatory gates | Support ledger, independent review, package hashes/notices and recovery manuals |

TASKS.json contains gate prerequisites and constituent tasks. G03 builds do not imply G07 physical exercise. G08 is per profile; optional greater-than-2-TiB acceptance is separately recorded by CLI-056. G09/G10/G11 cannot be omitted from a complete-suite claim.

## Inspection and repair states

Inspection results must distinguish:

- complete_consistent: every structure/ownership domain required by the admitted profile was inspected and its declared invariants held.
- complete_inconsistent: coverage is complete and specified violations exist.
- incomplete: unreadable or unknown regions, unresolved structures, resource refusal or truncation prevent a complete conclusion.
- unsupported: the input is outside a supported interpretation profile.
- aborted or fatal_error: user cancellation and operational termination remain identifiable.

Repair outcomes must separately represent planned, applied_verified, partially_applied_recovery_required, rolled_back_verified, rollback_incomplete and refused. A completed export may still be explicitly partial. Final numeric exit codes are settled in CLI-024; exit zero cannot conceal incomplete requested checking, unresolved supported corruption or recovery-required failure.

A coverage record identifies CGs, inode initialized/unknown regions, directories, data/indirect/EA ownership, replicas, partitions and unreadable ranges. A failed directory/inode read cannot turn its objects into proven orphans. No global map rewrite, orphan reclamation or clean marker is permitted while dependent ownership is incomplete.

## Corruption and ambiguity matrix

Each deterministic action family must also be combined with an unreadable prerequisite and a conflicting-evidence case. Correct refusal is tested alongside successful repair.

| Family | Required cases | Acceptance |
| --- | --- | --- |
| Disk and crypto profiles | Wrong key, wrong layer/order, swapped keys, wrong sector origin, ambiguous valid candidates, nested boundary and changed disk | Explicit admission/refusal; no write from a single magic match |
| Superblocks and geometry | Bad/plausible incompatible magic, overflow sizes/counts, truncated/overlapping partitions, conflicting replicas, partial final CG, unknown flags | Bounded accesses; justified authority; no generic host normalization |
| Inode initialization | Zero/extreme/stale/contradictory prefixes, map disagreement, references to unknown tables, plausible stale records | Unknown ownership retained; fallback is bounded and cannot invent live/free evidence |
| Ownership | Same-inode and cross-inode duplicates; data/indirect/EA alias; reserved metadata reference; cross-CG/end-volume pointers | Record every competing typed owner; traversal order does not choose the intended owner |
| Sparse and indirect trees | Direct/single/double/triple holes, absent middle subtree, zero between pointers, cycles, repeated indirect block, tail fragments | Exact logical offsets/lengths; indirect metadata included; bounded arithmetic/work |
| Inode interpretation | Unknown type/flags, size/count mismatch, zero/extreme links, timestamps/modes/owners, inline/block symlink boundary, empty inode with EA | Preserve valid fields; profile-aware actions; unsupported states explicit |
| External attributes | Ordinary PS3 UFS2 magic with EAs, multiple/tail/corrupt/overlapping EA blocks, old/current NetBSD disagreement | EA fields/permissions/content/ownership retained for valid cases; no unsupported conversion |
| Directories | Minimum/aligned record sizes, overlong/cross-boundary name, duplicate raw names, non-UTF8, invalid inode/type, dot/dotdot, loops/multiple parents | Raw names preserved; graph/reference evidence complete; invalid records not silently dropped |
| Maps and summaries | One CG, only global totals, only CS array, fragments/clusters, directory totals, initialized counts, final-group tail, pending frees | Full independent reconstruction from trusted evidence; no deltas from corrupt authority |
| Orphans and duplicates | Positive/zero-link inode, disconnected tree, missing inode evidence, stale/deleted data, competing owners | Export/reconnect/reclaim policies separate; ambiguity preserves evidence |
| I O and media damage | Short reads at every structure, unreadable maps/tables/indirect/EAs/payload, failed seeks, zero progress writes | Incomplete coverage, no successful synthetic zeros, bounded retries and no dependent write |
| Units and capacity | Conventional and observed 512e units, USB masking, actual profile mismatch, high LBAs, 2 TiB crossings, unsupported native 4Kn | Addressing/accounting/alignment separated; source convention preserved; unsupported profile refused |
| Scale and hostile input | Dense/sparse trees, high inode placement, huge prefixes, many links/CGs, deep graphs, allocation and scratch exhaustion | Declared resource/work limits hold; safe cancellation and no false clean/reclaim |
| Capture maps and archives | Corrupt/truncated/swapped manifests or payloads, false completed intervals, reordered/duplicate/overlapping ranges, stale checkpoints and interrupted publication | No unread byte is certified; manifest/payload/base identities and hashes agree before restore or resume |
| Export and restore confinement | Dotdot/absolute/drive/UNC names, separators, device names, case/Unicode collisions, symlinks/hardlinks/reparse redirects and target replacement | All writes remain inside the selected destination and preserve source bytes; mapping is explicit and hostile paths refused |

Include regression IDs RG-IO-01 through RG-ORACLE-01 from SOURCE-REUSE.md in corpus manifests. Every required case binds its expected findings, coverage, permissible plan and unchanged-byte/content constraints.

## Independent correctness

1. Author byte-level layouts from a declarative specification separately from the product writer.
2. Use independent mathematical ownership, initialized-prefix, sparse-position, fragment/cluster and count calculations; a second implementation/language is a candidate.
3. Use our strict PS3HDDTool only inside its admitted subset. Its refusal on corrupt input is not an oracle for the intended repair.
4. Compare adapted NetBSD only after PS3 EA/accounting/flag differences are addressed.
5. Retain golden pre-corruption images and known original content/metadata where possible.
6. After repair, perform independent traversal, sector-diff allowlist checking and unaffected-content comparison.
7. Recheck idempotence: complete scan has no remaining supported inconsistency and a second plan is empty.
8. Qualify native memory safety with declared sanitizer/fuzz targets and budgets for every admitted disk, filesystem, plan, overlay, journal, capture-map and archive input. Preserve crash/exhaustion cases and review actual coverage; a run count alone is not acceptance.

Agreement between the same writer/checker is insufficient. A disagreement stays open until explained by the bytes, profile and specification. Phase labels, counts of tests or successful compilation are not a substitute for an oracle.

## Transaction and recovery fault matrix

Inject failures immediately before and after every externally visible transition:

- Identity/profile/precondition admission and acquisition of exclusive ownership.
- Journal creation, header/range table, every before-image record, checksums, finalization, file flush and directory-entry publication.
- Dirty-state marker write, flush and readback.
- Every full or partial target encrypted/physical-unit write, including directory, inode, indirect, EA, bitmap and summary updates.
- Final metadata/content verification, clean-marker write/flush/readback, commit receipt and journal disposition.
- Every rollback restore record, flush/readback and final original-state restoration.

Faults include short I/O, interrupt/retry errors, zero-progress write, flush failure, full journal/scratch device, process kill, modeled torn writes, corrupt/truncated/reordered/duplicated records, stale plan, wrong key/profile/revision/device, external modification and a second interruption during recovery.

Required invariants:

1. Complete before-images are durable and verified before corresponding overwrites.
2. Before-images cover all affected ciphertext and host physical RMW bytes, including unrelated bytes sharing a write unit.
3. Rollback restores the supported original clean/dirty state only after restore verification; it never upgrades an originally dirty input to clean.
4. Wrong identity or unexplained external change blocks resumed writes.
5. Recovery is repeatable/idempotent within its stated state machine, with explicit version compatibility.
6. Flush failure yields uncertain persistence/recovery-required status until resolved; evidence remains available.
7. Journal placement has adequate capacity and a persistence contract independent of the repair target.
8. Destructors, error callbacks, process exit and cache eviction cannot implicitly commit target changes.
9. Loss of a status file or missing journal is not proof of completed repair.
10. Report publication failure cannot erase the primary disk/recovery result.

Software cut-point/fault models establish software behavior. Stronger persistence claims need separately authorized sacrificial-device tests; success of a host flush API does not qualify every bridge/device firmware.

## Windows Linux and macOS matrix

For each advertised host/architecture/backend, qualify images and physical operations separately. Specify and test:

- Whole-device identity/size and stable reopen, changed paths and same-looking replacement media.
- Mounted partitions, automounters, filesystem drivers and competing raw handles.
- Read-only enforcement and explicit write capability; privilege/elevation boundary.
- Logical/physical geometry, alignment and fully journaled RMW where supported.
- Exact and short I/O, large offsets, retry/cancellation and media removal.
- Durable flush ordering, failure propagation and final readback.
- USB/SATA bridge changes, cache behavior and reconnect during commit/recovery.
- Compiler, sanitizer/fuzz applicability and native runtime on each supported architecture.

A backend mock, successful cross-compilation, real image test and actual device qualification must have different result fields. Native ARM64 and emulated x86 runs must not be presented interchangeably.

## FAT VFLASH and other suite operations

FAT12/16/32 require separate cluster-width, FAT-copy, loop/cross-link, reserved/bad-cluster, directory/LFN, end-marker and FAT32 auxiliary-record cases. Partition reconstruction requires independent starts/lengths/role evidence; a plausible table alone is not sufficient.

VFLASH requires proven nested layer addressing and bounded views before inspection; any write needs a complete preservation/restore procedure and exact console-role acceptance. Generic FAT acceptance cannot be promoted to all VFLASH roles.

Capture/archives must report complete versus partial bytes, unreadable intervals and exact coverage. Allocation-based archives are not bit-for-bit images and are unsafe as the only preservation strategy when their allocation evidence is damaged.

Migration retains separate source-change, topology/content, preservation, rollback and target-capacity gates. Filesystem repair does not prove application database, content licence or console account correctness.

## Console qualification and release stops

Future native plans use disposable or independently restorable copies. Record console, firmware, actual crypto/layout profile, drive/bridge, geometry and exact approved actions. Compare baseline, intended host repair, agreed boot/mount/read/write/delete or representative game/save behavior, native checker if authorized, and post-use metadata/content changes. Console-origin changes must be distinguished from host-repair changes.

Stop dependent writes on unresolved units/profile/flags, ambiguous map authority, incomplete ownership, failed exclusion, changed identity, any unhandled short I/O, unavailable durable flush, damaged/missing before-images, insufficient resources, unsupported journal revision or write outside the plan.

Release only exact accepted operation tuples. Final complete-suite acceptance requires mandatory UFS2, FAT, VFLASH/partition, acquisition/recovery and backup/migration tracks; intermediate UFS2 or image-only results remain explicitly partial. Existing native firmware E01-E09 and stable=false records do not change these new suite gate statuses.

