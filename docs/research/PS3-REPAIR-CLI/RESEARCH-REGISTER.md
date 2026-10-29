# Research Register

Date: 20 October 2026. All entries remain open. INITIAL-RESEARCH.md and FORMAT-RESEARCH-2.md record earlier packets; PS3-NATIVE-RESEARCH.md is the current native selector/EA/flag/initialization disposition. Eight source-research tasks remain in progress; no complete format, licensing or repair specification is closed.

Dependencies below refer to research questions. TASKS.json holds the dependency graph and bounded current source-research authority. Preliminary research can proceed before prerequisite acceptance without releasing development. Sources S01-S35 are defined in SOURCE-REUSE.md.

## Initial research disposition

| Entry | Verified progress | Closure still required |
| --- | --- | --- |
| R02 | LIC-01 through LIC-08: missing native donor source grant; combined PS3HDDTool terms; mixed old-reader terms; sampled BSD notices and declared dependencies | Contribution/provenance resolution, selected suite composition, complete included-file/dependency ledger |
| R03 | FMT-D01 through D05 and C01 through C05: real disklabel fields, discovery exclusions, candidate layers/origins and exact key forms | Reserved region/ACL/roles/variants, competing-map rules, named profiles and independent vectors |
| R04 | FMT-U01/02 resolves initialized-prefix inode-slot units; U05-U09 adds EA comparator/stub, partial CG, directory/link and flag differences | Damaged-state arbitration, EA payload, PS3 flag/replica semantics and independent profile evidence |
| R05 | FMT-U03/04 separates addressing from accounting and records our fixed /512 assumption against a bounded published alternate observation | Complete profile identification, checked conversions, mixed states, cropped origins and 4Kn policy |
| R06/R07/R13/R14 | New regression requirements RG-PART-02, RG-KEY-01, RG-PS3-04/05/06 and RG-DIR-01 feed later coverage, repair, reporting and oracle work | These tracks have inputs, not completed designs or executed cases |

No downstream implementation dependency, qualification gate or support cell was released. The field-unit fact is narrower than CLI-011's full acceptance criteria.

## Follow-up format disposition

| Entry | New verified source facts | Remaining PS3 research |
| --- | --- | --- |
| R05 | ACC-01..06: saved checker derives counts from fsbtodb; allocator uses a runtime shift; BSD source supplies a counterexample to universal shift-based inference; normalization is separate | Runtime shift/selector binding, cross-profile scope, mixed states, all ownership/count units and writable admission |
| R04 EA | EA-01..06: seven-byte comparator framing, old-helper mismatch, namespaces/ACL comparison and native extent-accounting branch | PS3 payload byte order, namespace/value semantics, native binding and damaged-content repair |
| R04 flags | FLG-01..05: legacy/new fields differ; donor bits/actions conflict; migration mask is narrow; existing PS3 flags observation is bounded | PS3 feature activation/ownership, legacy marker, pending transitions and replica policy |
| R04/R06 prefix | PFX-01..06: stored/working counts differ, early donor trust and probable-end/free defaults are unsafe, generations need not be zero | PS3 initialization/alignment/persistence and arbitration when several evidence domains are damaged |
| R07/R14 | Proposed accounting/EA/flag/prefix decision tables and six new regression requirements | Independently authored cases and action prerequisites; no execution or validation implied |

These resolve narrower comparator/source questions and define proposed refusal rules. They do not close a research entry, authorize implementation or qualify a supported profile.

## Current PS3 native disposition

| Entry | Native source facts established | Research still needed |
| --- | --- | --- |
| R05 | NAC-01..04: initialized global 9/512, real 12/4096 setter, internal-HDD IDENTIFY bit predicate, normalization failure-as-false and geometry-dependent unit caveat | Complete aliases/resets/lifecycle, caller fields, replacement/mixed-image consistency and writable profile selection |
| R04 EA | NEA-01..05: VOP/OPD binding, BE seven-byte records, inode-backed extents, namespaces/access predicates and opaque value transfers | Actual names/value consumers, complete security enforcement, malformed handling, interrupted updates and cross-profile evidence |
| R04 flags | NFL-01..05: native low-bit/clean behavior, legacy marker selection, warning-only ACL/MAC branches and bit0x02-to-dependency-mask bridge | Complete consumers and legacy writes, pending/snapshot/replica policy and failure paths |
| R04/R06 prefix | NIN-01..04: kernel memory mutation/submission order and distinct P13 repair allocator/pass5 prefix behavior | Concrete buffer callbacks/dependency completion/failure/retry, later inode/directory publication and durable interruption arbitration |

Earlier open-item tables describe their packet boundaries; this table is current. No whole research-entry closure or technical gate follows from these native paths. Independent case requirements are saved, not executed.

## R01 Scope and supported profiles

Question: What exact operation, host, architecture, backend, console crypto, partition/dialect, accounting convention and capacity combinations will be promised?

Output: requirements, support ledger and complete-suite definition, including partial milestones and explicit optional extensions. Close when each claim maps to a named tuple and evidence requirement; unknown tuples remain unsupported or incomplete. Dependencies: none. Tasks: CLI-001/003/004/080. Sources: S01/S13/S18.

## R02 Source provenance and reuse

Question: Which files may be copied, adapted, translated or used only as references, and which notices/dependencies follow them?

Output: pinned per-file source/notice manifest and incorporation decision. Close when every intended inclusion has resolved provenance and terms; unresolved candidates stay excluded from incorporation. Dependencies: R01. Tasks: CLI-002/006/069/074. Sources: S01/S07/S08/S15/S20.

## R03 PS3 disk and encryption specification

Question: What are the authoritative disklabel fields, table signatures, lengths, overlaps, nested VFLASH maps, layer order, byte swaps, sector/tweak origins and accepted key forms for each actual console profile?

Output: byte-exact maps and independent generated known answers, with wrong-key, truncation, overlap, nested-boundary and competing-candidate cases. Close each profile only with corroborating evidence beyond one magic value. Dependencies: R01. Tasks: CLI-007/008/031/077. Sources: S05/S15/S21.

## R04 PS3 filesystem dialect specification

Question: What are the exact superblock, cylinder group, inode, directory, EA, sparse/tail, symlink, flag and replica rules?

Output: field/invariant register linking source, observed structure and independently authored fixture. cg_initediblk inode-slot units are resolved by FMT-U01/02; initialized/free/stale arbitration, corrupt prefixes, partial final CGs and preserved unknown bytes remain open. EA extent ownership and payload integrity require separate evidence. Dirty/pending-free/snapshot and same-bit flag differences need explicit PS3 policy. Close only for named supported dialects. Dependencies: R03. Tasks: CLI-010-014/032/033. Sources: S07/S08/S10/S16/S19/S23.

## R05 Units capacity and crypto addressing

Question: How do host logical/physical units, crypto sectors, fragments, fsbtodb and di_blocks interact on conventional and observed 512e layouts?

Output: checked conversion rules, profile identification evidence and low/high/boundary vectors. ACC-01..06 gives the checker relationship/BSD counterexample; NAC-01..04 binds native selectors while global lifecycle and mixed-image authority remain unresolved. Close profiles separately; adapter presentation is not sufficient to choose on-disk accounting. Native 4Kn needs its own decision. Greater-than-2-TiB host access and PS3 firmware/console acceptance remain separate. Dependencies: R03/R04. Tasks: CLI-009/018/026/055/056. Sources: S05/S19/S21/S22/S28/S32.

## R06 Complete damaged filesystem inspection

Question: Which inode regions and allocation evidence remain trustworthy when initialization fields, maps, headers or directories disagree?

Output: pass design, coverage/confidence model, complete reserved/data/indirect/EA ownership and bounded fallback policy. Close when missing reads and unknown structures cannot lead to false clean, free or orphan conclusions, including same-inode duplicate references. Dependencies: R04/R05. Tasks: CLI-011/019/032-040/076. Sources: S02/S07/S10.

## R07 Repair decision catalogue

Question: Under what evidence can maps, counters, links, block counts, records, dot entries, disconnected trees, conflicting pointers and replicas be changed?

Output: one specification per action containing prerequisites, postconditions, exact changed ranges, dependencies, ambiguity/refusal cases and independent oracle. Full-domain evidence must precede global allocation reconstruction. Dependencies: R06. Tasks: CLI-014/015/041/042/073/077. Sources: S03/S07/S10/S16.

## R08 Recovery salvage and original content

Question: When should the tool export, reconnect, copy competing data, truncate or reclaim, and how does it represent confidence?

Output: preservation-first policy, raw-name export mapping, partial-content manifests, destination confinement and separate loss-labelled outcomes. Close when disconnected objects, stale records and duplicate ownership cannot be silently discarded; hostile names/links cannot escape export or restore roots. Logical consistency and original payload identity remain different claims. Dependencies: R06/R07. Tasks: CLI-023/039-041/061-065/083. Sources: S07/S12/S13/S18/S19.

## R09 Overlay journal and recoverable commit

Question: How can a reviewed plan change encrypted metadata and recover after partial writes, process loss, uncertain flush, corrupted journals and interrupted rollback?

Output: immutable observation/plan binding, isolated overlay, versioned before-images and durable state machine. Close when every write/publication cut point has a defined verified recovery or explicit uncertain terminal state. Support originally dirty baselines and directory/EA/indirect sectors; do not inherit the migration journal's narrower admission. Dependencies: R03/R07 plus R10's persistence contract. Tasks: CLI-021/022/043-050. Sources: S04/S09/S11/S12/S14.

## R10 Host transport and acquisition

Question: What guarantees can Windows, Linux, macOS and each admitted bridge provide for exact I/O, identity, mount exclusion, alignment, durability and hotplug?

Output: shared backend contract, per-host capability matrix, capture/read-map design and disposable-media qualification plans. Close each read/write/recovery capability independently. Unknown bytes never become successful zeros; reconnect with changed identity blocks writes. Dependencies: R01/R03/R05; contract co-design with R09. Tasks: CLI-023/025/027-030/051/061/079. Sources: S04/S14.

## R11 FAT VFLASH and partition repair

Question: How do the supported FAT12/16/32 variants, duplicate FATs, cluster chains, long/short names, bad clusters, FSInfo/boot copies and nested roles affect reconstruction?

Output: separate FAT specifications/actions/oracles and VFLASH/partition role constraints. Close generic FAT image behavior before critical nested-region repair. Competing maps or unproven region roles remain preserved and unwritable. Dependencies: R03/R05/R09. Tasks: CLI-016/017/057-060/077/078. Sources: S15/S21.

## R12 Resource and performance envelope

Question: How much memory, scratch, recursion, queueing and repair-growth reserve can the largest admitted corrupted layout require?

Output: bounds/admission specification, disk-backed or external-sort decision, cancellation/exhaustion rules and labelled performance protocol. Close from complete structural requirements, not reachable file count or observed average usage. A 64-bit host removes the small console arena limit but does not make resources unlimited. Dependencies: R04/R06. Tasks: CLI-019/038/068/076. Sources: S02/S17/S22.

## R13 CLI findings and audit records

Question: How are incomplete inspection, inconsistency, unsupported profiles, planning, applied verification, recovery-required, rollback and cancellation reported?

Output: stable machine schema, explicit exit/result contract, terminal-safe names, secure key input and review/apply preconditions. Close with examples covering partial inspection, stale plans, remaining errors and failed rollback. Numeric exit codes are a design decision; no zero may hide incomplete/failed work. Dependencies: R06/R07/R09/R10. Tasks: CLI-005/021/024/044/066/070/079.

## R14 Independent validation corpus

Question: How can fixtures and expected results avoid the same mistakes as the writer/checker under test?

Output: declarative byte layouts, independent mathematical oracle, known before-corruption states, per-regression witnesses, interacting corruption cases, bounded fuzz/sanitizer targets and fault injection protocol. Include corrupt capture/archive metadata and destination-confinement attacks. Close when disagreements are explained from the specification and bytes rather than majority agreement or phase labels. Dependencies: begin with R04; extend with R06-R11. Tasks: CLI-020/049/050/065/076/079/080/082/083. Sources: S06/S10/S13/S18.

## R15 Device and console acceptance

Question: What finite, disposable-media experiments establish each exact physical operation and PS3 compatibility claim?

Output: profile-specific intake, preservation, controlled damage/repair, host readback, console workflow and post-use comparison plans. Close only after separately authorized execution of accepted image/device prerequisites and exact native protocols. Firmware update/recovery, game/save behavior, ordinary I/O and checker success are separate claims. Dependencies: R09/R10/R14. Tasks: CLI-051-056/060/073/078. Sources: S16/S17/S18/S19.

## R16 Distribution and maintenance

Question: How will supported toolchains, dependency locks, packages, notices, report/journal versions and security updates remain reproducible and recoverable?

Output: build/package matrix, file-level notices, dependency inventory, update policy and a usable old-journal recovery route. Close per advertised OS/architecture and operation. Exact version/ABI/tool decisions remain pending CLI-006. Dependencies: R01/R02/R13 and relevant qualification evidence. Tasks: CLI-006/067-072/074. Sources: S01/S07/S13/S20.

## Priority and research parallelism

Start R01/R02, then R03 and R04/R05. R06 feeds R07/R08, followed by R09 image repair design. R10 transport contracts, R12 resources, R13 reporting and R14 fixtures can advance alongside the scanner after their format inputs exist. R11 remains a first-class parallel companion track.

R09 and R10 are a design co-dependency, not a circular task graph: first specify the common contract, then implement/qualify independent backends and transactions according to TASKS.json. Native resource work in S17 supplies questions but is not a required predecessor to host research.

Each closure record must state the supported tuple, evidence sources, unresolved questions and downstream tasks released by the research decision. No research conclusion itself authorizes development or hardware execution.

