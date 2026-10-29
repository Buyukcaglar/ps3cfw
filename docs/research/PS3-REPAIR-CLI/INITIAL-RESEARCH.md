# Initial Source Research Record

Date: 20 October 2026. Scope authorized by the latest user instruction: read-only source reuse, licensing and PS3 format research, plus planning-document updates. This bounded research pass is finished; the full research tasks remain in progress. No development, source incorporation, dependency installation, compilation, product tests, device/console actions, private keys or publication occurred.

This records the initial packet. The subsequent [format follow-up](FORMAT-RESEARCH-2.md) advances accounting, EA contents, flags and damaged prefixes without closing full-profile gates. The pre-follow-up twelve-file package is preserved in history/20261020-initial-research; current task/gate status is in TASKS.json and PLAN-VALIDATION.json.

The later [PS3 native packet](PS3-NATIVE-RESEARCH.md) establishes artifact-specific selector, EA and initialization bindings. Earlier open-item lists are historical packet boundaries; use the native packet and current registers for remaining research. The fourteen-file format package is preserved in history/20261020-format-followup.

## Result and planning decisions

The shared C/C++ suite remains technically feasible. The source foundation is more selective than the initial roadmap implied: UFS2Xplorer is a technical reference pending source terms/provenance; our PS3HDDTool has documented combined terms for selected reuse; BSD checking algorithms are candidates after file-level and PS3-policy adaptation. No donor is a ready complete PS3 repair engine.

| Verified result | Consequence | Detailed evidence |
| --- | --- | --- |
| UFS2Xplorer's pinned tree has no verified repository source grant; the explicit icon licence is unrelated. README acknowledges inherited PS3HDDTool code. | Direct incorporation stays unresolved; complete the contribution/provenance map or retain reference-only status. | LIC-01 through LIC-03 in [LICENSING-REUSE.md](LICENSING-REUSE.md) |
| Our publication uses BSD-3-Clause AND a custom source-sharing addendum. The old reader has GPL, individual BSD and unmarked files. | Preserve file-level terms; a C++ translation is not a route to assuming fewer obligations. Complete composition review before selection. | LIC-04 through LIC-08 |
| An upstream PS3 partition parser corroborates eight 0x90-byte entries at 0x30, full BE64 signatures and 512-byte start/length units. | A bounded parser can be specified without rediscovering these constants. Reserved-region, role and recovery authority remain unresolved. | FMT-D01/02 in [FORMAT-FINDINGS.md](FORMAT-FINDINGS.md) |
| UFS2Xplorer and both inspected PS3HDDTool discovery paths use inadequate signature/layout heuristics. Migration instead uses explicit supplied partition/profile inputs. | Do not promote migration success into automatic map-discovery acceptance. Replace discovery authority and preserve failed/ambiguous candidate evidence. | FMT-D03/04 |
| The old reader distinguishes fat NOR outer CBC from Slim outer XTS; both may have nested XTS VFLASH. Root and legacy combined CBC inputs both have 48 bytes. | Specify named layers/origins and explicit key kinds. Generic NAND/NOR shorthand and length-only key detection are insufficient. | FMT-C01 through FMT-C05 |
| cg_initediblk is an exclusive initialized inode-slot prefix, corroborated by allocator/newfs/checker source and bounded saved native evidence. | The unit question is resolved at source-semantics level. Damaged-prefix arbitration and native/profile qualification remain open. | FMT-U01/02 |
| Our migration core uses 512-byte inode accounting. Firsthand PS3 research describes a separate 4096-byte accounting case. | Do not treat observed 512e variants as already supported; separate addressing, accounting, crypto and physical I/O units. | FMT-U03/04 |
| FreeBSD 8 provides ordinary-UFS2 EA extent accounting, but its content scan is a stub. NetBSD branches have incompatible/omitted EA paths. | Use FreeBSD as an additional ownership comparator; EA payload/namespace repair is still research. | FMT-U05/06 |
| Flag bits have conflicting meanings across BSD donors; directory, inline-link and partial-final-group details need explicit cases. | Keep a PS3 versioned policy and preserve/refuse unknown semantics. No generic normalization or automatic clean decision. | FMT-U07 through FMT-U09 |
| Source shows legacy UI secret logging, old-reader seek/context/boundary defects, native-donor short-read substitution and hidden destructor writes. | Exclude these policies; convert source defects into later independent regression requirements. None was reproduced on media here. | FORMAT-FINDINGS.md and [SOURCE-REUSE.md](SOURCE-REUSE.md) |

## What this phase does not need to rediscover

Retain the existing migration extent, raw-name, sparse, EA-ownership, accounting and preservation work as bounded donor specifications. Retain ciphertext before-images, device identity/exclusion and narrow read-only recovery overlays as designs, while recording their clean-source and operation limits. Existing tests and the one real Windows/CBC same-console migration remain donor evidence; their results do not transfer to the future C++ program.

Retain the pinned BSD multi-pass decomposition, real disklabel constants, candidate crypto derivation/layer rules, inode-slot prefix semantics and identified incompatibilities. Additional research should resolve unsupported semantics and action rules rather than repeat the original feasibility search. A 64-bit host and native core remain viable; no kernel UFS mount, Qt, .NET or BSD VM is required in the proposed production runtime.

## Exact status changes

TASKS.json now records these eight research tasks as in_progress with authority limited to source reading and planning documents:

| Task | Findings recorded | Why it is not complete |
| --- | --- | --- |
| CLI-002 Source provenance | Candidate terms, sampled file-level inventory, incorporation classifications and declared dependencies | UFS2Xplorer grants/history, final suite composition, complete included-file notices and selected dependency inventory unresolved |
| CLI-007 Disklabels | Corroborated fields, units, discovery exclusions and nested-map relation | Reserved region, roles, variants, ACLs, competing/damaged-map arbitration and independent cases unresolved |
| CLI-008 Crypto profiles | Candidate outer/nested layers, tweak origins, exact supplied key forms and implementation exclusions | Named model/firmware matrix and independent known answers unresolved |
| CLI-009 Units | Existing /512 assumption, alternate published observation and distinct conversion domains | Complete profile identification, mixed states, bounds, cropped input and native 4Kn decisions unresolved |
| CLI-010 Superblocks/features | Conflicting flag semantics and preservation requirement | Replica authority, field propagation and complete PS3 feature register unresolved |
| CLI-011 Cylinder groups/prefix | Inode-slot unit and final-group rule supported by pinned sources | Corrupt prefix/map/table arbitration, reservations, padding and independent/native evidence unresolved |
| CLI-012 Inodes/extents/EAs | EA comparator/stub limits, tails and inline-storage boundaries | Full PS3 EA payload, special-node, pointer/alias and boundary specifications unresolved |
| CLI-014 Dirty/unsupported states | Generic donor clearing/conversion is unsafe; migration admission is narrow | Pending frees, soft updates, snapshots, dirty-original repair and action/refusal policy unresolved |

The other 75 task statuses remain planned. Preliminary reading is permitted before prerequisite specifications close; it does not satisfy those dependencies or release implementation. CLI-001/003 support contracts are still open. All 13 gates remain not_assessed with passed=false. No product-support cell, research closure, repair result or native qualification was earned.

## Next research packet and closure criteria

1. Requirements/profile ledger: identify the first exact read/scan/plan/apply tuples and the full-suite tracks that remain mandatory. Do not let a first UFS2 milestone silently remove FAT/VFLASH/acquisition/recovery/backup/migration.
2. Incorporation decision: retain UFS2Xplorer reference-only pending documented source terms; choose the proposed donor composition and enumerate included files/notices. No external messages or author contact occurred or are implied.
3. Disk/crypto specification: settle whole table-region preservation, partition roles, nested bounds and cropped-image origins; write explicit key-kind and profile tables. Independent vector specifications come before later execution.
4. PS3 UFS policy: finish accounting-profile evidence, corrupted-prefix fallback, replicas/reserved metadata, EA payload/namespace semantics, same-bit feature conflicts and dirty/pending-free behavior. Saved native source analysis can supply evidence without consuming old hardware jobs.
5. Independent corpus/repair catalogue: specify fixtures for every new and existing regression, known pre-corruption bytes, complete ownership and refusal cases. Distinguish reusable migration admission from general damaged-input inspection.

G00 needs resolved scope, provenance and dependency decisions; this packet supplies partial evidence only. G01 needs complete named-profile field/action rules. G02 requires an independently specified corpus and later evidence appropriate to its gate. Research can continue within the current authority; implementation, builds, fixture execution and physical/native actions remain outside it.

## Evidence custody and document checks

The original eight planning files are preserved under history/20261020-planning-baseline. SOURCE-SNAPSHOT.json remains the original baseline; RESEARCH-SOURCES.json adds selected raw-source SHA-256 values, repository pins, local source hashes and explicitly unpinned published references. No whole-media/private-key hashes or user payload are included.

The current PLAN-VALIDATION.json records document readback, references, task/gate graphs, authorization consistency and selected source/context preservation. It is a planning-integrity receipt, not a build, product test, runtime result or legal clearance. Source findings are static unless explicitly labelled as a previously published experiment or existing donor result.
