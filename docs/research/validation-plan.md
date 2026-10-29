# Engineering and qualification plan for PS3 internal storage

Research date: 2026-10-11. This is a proposed engineering plan, not a tested firmware release or a claim of data-loss-free operation. No console, flash, or physical disk has been accessed by this research task.

## User-reported hardware and scope

The user identified the console as **CECHA00** and reported rejection of three nominal 2 TB SATA SSDs on installed 4.91 CFW:

| Drive family | User-supplied identifier |
| --- | --- |
| Lexar NQ100 2 TB | `LNQ100X002T-RNNNG` |
| PNY CS900 2 TB | `CS900` / `SSD7CS900` (full capacity-specific SKU not supplied) |
| Crucial BX500 2 TB | `CT2000BX500SSD1` |

These are reports, not results of device interrogation in this project. Native sector counts, logical/physical sector sizes, ATA IDENTIFY fields, SSD controller revisions, current HPA/DCO exposure, firmware revisions, and health have not been observed. Similar rejection of three models is consistent with a common firmware gate, but does not prove the hardware configuration independently of binary evidence.

CECHAxx is documented as a NAND phat family. Combining that model identification with Glevand's encryption account makes **CBC-192 ATA encryption** the expected initial qualification path for this CECHA00; verify it against the actual console/image before relying on the assumption. The Slim XTS tests below remain necessary for any later cross-model release, but do not describe the user's initial crypto configuration. NAND backup/restoration and boot-state handling must be model appropriate. [Model documentation](https://www.psdevwiki.com/ps3/CECHAxx), [firsthand encryption reverse engineering](https://www.psdevwiki.com/ps3/HDD_Encryption).

## Define the target precisely

The user almost certainly means approximately **1.75 TB**, rather than 1.75 GB. The first milestone is a drive sold as **2 TB**, exposing its entire native capacity to the PS3, with the ordinary system/cache partitions and filesystem reserve retained. Increasing the XMB free-space number, cloning a smaller filesystem without growing it, or hiding part of a drive with HPA/DCO is not this milestone.

| Boundary | Exact bytes | 512-byte sector count | Why it matters |
| --- | ---: | ---: | --- |
| 1 TiB | 1,099,511,627,776 | 2,147,483,648 | Signed 32-bit sector boundary |
| 1536 GiB | 1,649,267,441,664 | 3,221,225,472 | Capacity gate verified in the supplied emer_init binary |
| 2 TB, decimal | 2,000,000,000,000 | 3,906,250,000 | Nominal first target; actual drive IDENTIFY capacity can be slightly larger |
| 2 TiB | 2,199,023,255,552 | 4,294,967,296 | Unsigned 32-bit sector boundary |
| 3 TB, decimal | 3,000,000,000,000 | 5,859,375,000 | Useful later milestone crossing the 2 TiB boundary |

A decimal 2 TB drive does **not** cross 2^32 512-byte sectors. Claims about a 2 TiB truncation cannot, by themselves, explain refusal of a decimal 2 TB drive. Also distinguish a sector **count** from the inclusive last LBA, which is count minus one. Every byte/sector conversion must state its unit and sector size.

## Technical evidence and its limits

1. The Sony-authored Linux PS3 storage library passes `u64` start-sector and sector-count arguments through to LV1 storage read/write calls. That is evidence of a 64-bit public interface, not proof that GameOS, LV1, the SATA command construction, and ENCDEC all use the high bits correctly. [Primary implementation](https://raw.githubusercontent.com/torvalds/linux/master/drivers/ps3/ps3stor_lib.c).
2. FreeBSD 5.5 UFS2 defines 64-bit disk addresses and 64-bit file sizes. Its superblock also contains 32-bit geometry fields beside 64-bit size fields. Thus the UFS2 format is not inherently limited to decimal 2 TB, but Sony's fork, helper arithmetic, allocations, and checker still require inspection. [Inode definitions](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/5.5/sys/ufs/ufs/dinode.h), [superblock and cylinder-group definitions](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/5.5/sys/ufs/ffs/fs.h). These are comparison sources; a matching upstream structure is not yet proof of Sony's implementation.
3. Glevand's documented reverse engineering distinguishes CBC ATA encryption on phat models from XTS on Slim models. XTS requires the correct sector number, and ATA data uses half-word swapping. VFLASH has an additional encryption layer. Qualify the actual console family rather than inferring encryption solely from NOR versus NAND. [Original technical account and examples](https://www.psdevwiki.com/ps3/HDD_Encryption).
4. Andshrew's firsthand 512e tests found differing `fsbtodb` and inode block-count units, plus PS3 changes on remount. BSD variants can alter compatibility flags. These results justify a separate 512e test lane; they do not establish that every 512e PS3 drive loses data. [512e investigation](https://ps3hdd.pages.dev/blog/ps3-512e-compat/).
5. The same author's expansion experiment reports a 60 GB-to-320 GB clone/resize that booted. It is useful as a method lead, but does not qualify 2 TB migration, recovery, or SSD behavior. [Original working notes](https://gist.github.com/andshrew/4c1fe1c432d3d77e9bddf978426d34a2).
6. The current Harddrive wiki lists recovery, LV2 truncation, mount-geometry, and checker-memory limits with 4.93 addresses. This project's [binary review](binary-review.md) now verifies the capacity refusal and its error-message path, plus the cited LV2 instruction sequences. The [filesystem review](filesystem-review.md) confirms several formatter/checker copies and allocation arithmetic; full caller, geometry and memory-budget semantics remain open. The wiki table incorrectly says a listed 3,907,029,168-sector 2 TB disk crosses 2^32 sectors. [External research lead](https://www.psdevwiki.com/ps3/Harddrive).

## Qualification gates and dependencies

### G0 — Preservation and test configuration

Before any console testing, verify the reported CECHA00/NAND configuration, currently installed firmware flavor, minimum supported firmware, Cobra state, disk model/firmware/serial, native capacity, exposed capacity, logical/physical sector sizes, and connection topology. Capture the original error text and whether it occurs during cold boot, first format, recovery, or firmware reinstall. This distinguishes a capacity refusal from sector-size, SATA, power, drive-health, or stale-layout failures.

Keep the user's original disk physically disconnected during experiments. Obtain verified encrypted raw images and separate file-level backups while the original console is functional; retain encryption material privately and validate that the expected filesystem and sample files can actually be read from a copy. Record hashes, read errors, image length, and device identity. Secure key handling is required; public reports should contain no console-specific secrets. Preserve a verified console-flash backup with a model-appropriate recovery method before changing console firmware. A saved dump by itself does not prove that the console can be recovered.

**Exit:** a disposable test console or explicitly identified scratch configuration, disposable target disks, independently checked backup copies, and a rollback rehearsal on scratch media. Original-disk reinsertion is not assumed to undo firmware state or pairing changes.

### G1 — Reconstruct the complete rejection and I/O path

Disassemble the exact supplied PUP's relevant decrypted modules and preserve their hashes. Trace the displayed incompatible-drive error back to the branch that selects it, then trace the capacity value from IDENTIFY/device-info through its callers. Audit boot, blank-disk initialization, quick/full format, ordinary mount, filesystem check, recovery restore, database rebuild, backup/restore, updater/reinstaller, and any alternate kernel/recovery module copies in the package.

For each path, document capacity type, units, endianness, signedness, arithmetic overflow behavior, comparison semantics, and error behavior. Follow byte-to-sector multiplication, region-start addition, transfer splitting, filesystem fragment-to-sector shifts, and cross-ABI structure fields through LV2 and LV1. Trace synchronous and asynchronous I/O independently. A 64-bit load followed by a clear, store, or compare of 32 bits must be assessed in context. Changing every `0x180` constant or NOPing every capacity branch is unacceptable.

**Exit:** a reproducible local evidence packet showing the actual 4.93 branch/dataflow and all known related consumers. A known wiki address without a mapped function and calling path does not pass this gate.

### G2 — Offline arithmetic, layout, and checker budget

Build small host-side models of the identified arithmetic and serialized structures. Exercise one sector below/at/above each identified threshold, the actual 2 TB model's sector count, 2^31, 2^32, zero, maximum transfer count, and arithmetic overflow inputs. For requests, test last-valid-sector, end-exactly-at-region, one-past-end, and transfers crossing each boundary. Use the overflow-resistant condition `start <= size && count <= size - start`, adjusted for zero-length request semantics established from the original code.

Construct disposable sparse images with the expected big-endian PS3 partition table and UFS2 geometry. Check that all system/cache/user regions are disjoint, within the native disk, aligned as intended, and represented without truncation. Verify alternate superblock locations, cylinder groups, inode and free-space accounting, clean/dirty flags, soft updates, and FS-to-device conversion. Native PC tooling is a diagnostic oracle only after compatibility has been established on image copies.

Compute and measure checker peak memory and runtime as functions of fragment count, inode count, cylinder groups, directory workload, and container size. For perspective, a single bit per 4096-byte fragment at decimal 2 TB is already about 58.2 MiB, before other maps and code. This is a sizing calculation, not a measurement of Sony's checker. Increasing a constant without checking allocation size and every index is insufficient.

**Exit:** boundary models pass, filesystem geometry is internally consistent, and every boot/recovery/checker environment has a measured or conservatively established memory budget with margin.

### G3 — Minimal, reproducible candidate firmware

Implement only changes justified by G1/G2. For the first 2 TB milestone, retain existing layout and filesystem geometry unless evidence proves a change necessary. Limit qualification initially to 512-byte logical sectors; test 512n and 512e as distinct configurations where physically available. Native 4Kn is a separate project requiring an end-to-end sector-size and crypto-data-unit audit, not a workaround for the capacity barrier.

Each patch record needs input module hash, function/offset mapping, original and replacement instructions/bytes, rationale, affected paths, expected capacity range, and fail-closed version checks. Retain range checks and corrupt-metadata checks. Re-extract the rebuilt PUP and prove that only allowlisted module regions and required package metadata changed. Independently review disassembly and every changed branch. Distinguish an in-memory Cobra patch from code needed before Cobra starts and from independent recovery/updater code.

**Exit:** a reviewable candidate and reproducible patch manifest; no claim of console safety or support yet.

### G4 — Low-level hardware and encryption qualification

Use sacrificial disks only. Establish a smaller-capacity control on the same console and exact candidate. Test device discovery and raw region I/O using distinct deterministic data per sector. Validate low sectors, above 1 TiB, both sides of the previous gate, middle/end of the target, and guards around every tested interval. Read back after flush, clean shutdown, reboot, and cold power cycle.

For XTS, compare correctly indexed encrypted/decrypted samples at distant LBAs, including addresses sharing the same low 32 bits during the later >2 TiB phase. Prove that high-address writes do not alias low addresses. For CBC families, verify their actual per-sector handling independently. Trace the sector number supplied to ENCDEC; do not change crypto units or key derivation without evidence. Run tests both with and without ordinary Cobra/homebrew workloads where relevant to the intended support configuration.

**Exit:** correct data reaches every required LBA with preserved guard data and no high-bit alias, transport error, or crypto inconsistency. OtherOS/Linux success is supplementary; it cannot substitute for testing the exact GameOS path.

### G5 — Full-capacity filesystem and workload qualification

Fresh-format the native 2 TB scratch disk through the candidate's normal and recovery paths. Capture actual region geometry and reported total/free space. Map file extents or record filesystem I/O to prove that the test writes reach the formerly inaccessible area and the highest allocatable user-data blocks. Merely creating a huge sparse file or seeing a capacity in XMB does not pass.

Write verifiable, incompressible data across essentially all allocatable space, retaining system-required reserve. Run separate large-file, many-small-file, directory-depth, rename/delete, fragmented-space, inode-pressure, and near-full-disk workloads. Include game install/delete, legal test content, saves, XMB database operations, cache use, repeated boots, and simultaneous reads/writes. The predeclared engineering minimum should include at least two complete fill/readback cycles, repeated cold boots and clean shutdowns, and a multiday mixed-workload soak on each qualified drive/console class; these are project acceptance thresholds, not a statistical lifetime guarantee.

Hash all test files against an external manifest after each disruptive operation. Capture checker logs, error codes, free-space/inode counts, duration, memory peak, and SMART/health deltas. Every failure needs a root cause and rerun of affected gates, not just another successful boot.

**Exit:** full usable-capacity access, stable accounting and workload behavior, and zero unexplained data/hash errors on the declared matrix.

### G6 — Repair, recovery, update, and interruption qualification

On cloned sacrificial fixtures, test clean filesystem check; controlled dirty filesystem; interrupted file creation/write/rename/deletion and metadata updates; database rebuild; Restore File System; backup/restore; full initialization; and a firmware reinstall/update that carries all required storage patches. Inject read/write faults and out-of-space conditions where a controlled harness permits it. Test interruption at known filesystem write stages; reserve real power cuts for fixtures with a verified restoration procedure.

Separate committed/acknowledged data from uncommitted data. Record any permissible losses under the established sync/flush semantics and require that unrelated, previously committed data remains intact. Confirm that damaged high-LBA content is visited by the checker and that memory exhaustion returns a diagnosable failure without destructive fallback formatting. Check empty, nearly full, highly fragmented, and many-file fixtures; a clean empty checker pass is weak evidence.

Old firmware or recovery tools may reintroduce the refusal or mis-handle the larger layout. Test and document that boundary. Downgrading firmware on a 2 TB disk cannot be promised as safe rollback. The rollback procedure must specify which firmware can mount the disk, how data is exported, and when a small known-good disk is required. Validate that the original disk's pairing/system state can be recovered on the supported console before production migration.

**Exit:** supported recovery and update paths work on populated disks; unsupported paths have explicit blocking/detection or a tested escape procedure; interruption outcomes are bounded by observed durability guarantees.

### G7 — Migration and release admission

Only after G0–G6 should the user's data be migrated to a newly formatted qualified target. Prefer backup/restore or verified file-level transfer with supported metadata handling over ad hoc geometry changes. If raw cloning or offline UFS2 expansion is needed, qualify it as a separate migration path on cloned source fixtures first, including per-console encryption, region offsets, cache/system partitions, alternate superblocks, and PS3 remount behavior.

Retain the untouched original and backup images until the migrated target passes manifest checks, save/content usability checks, a normal filesystem check, reboot, and a defined acceptance period. Maintain a support matrix naming CECH family, exact candidate hashes, drive model/firmware, logical/physical sectors, format/migration method, and checker/update paths exercised. Limit claims to that matrix. A single console and one 2 TB SSD cannot establish universal PS3 support, and no finite test campaign proves impossibility of future data loss.

**Exit:** a bounded qualified release with reproducible provenance, working migration/restore instructions, and documented limitations.

## Beyond 2 TB

After full decimal 2 TB qualification, move first to a target that genuinely crosses **2 TiB**, typically a native 3 TB or larger drive. A 2.1 TB target would be above 2 TB yet still below the unsigned 32-bit sector boundary and would not answer the main width question.

Repeat G1/G2 for every device-info, LV1 region, ATA taskfile, ENCDEC tweak, kernel request, partition, UFS2, checker, and userland-capacity consumer. Specifically exercise both sides of 2^32 sectors, region-relative and absolute LBAs with identical low halves, and boundary-crossing multi-sector requests. Widen proven narrow types without silently altering userland ABIs; use compatible structure versions or explicit conversion boundaries where necessary.

Treat mount-summary buffers, cylinder-group geometry, checker memory, and inode indexing as independent capacity gates. If geometry must change, evaluate memory, small-file waste, inode exhaustion, compatibility, alternate-superblock recovery, and migration costs together. Do not presume that doubling fragment size or removing a mount cap is sufficient. Preserve normal filesystem reserve; changing it is unrelated to extending addressability.

Next capacity tiers require fresh qualification rather than extrapolation. Mechanical fit, SATA power/startup behavior, thermal behavior, and sector format must match the actual internal bay. External adapters or externally powered disks qualify a different hardware arrangement. Native 4Kn remains out of scope until its independent pipeline and recovery audit passes.

## Dependencies and useful parallel work

Critical path: **G0 preservation → G1 exact rejection/dataflow → G2 limits and budgets → G3 reviewed candidate → G4 low-level hardware → G5 full filesystem → G6 repair/update/durability → G7 migration/release → >2 TiB repeat**.

G0 configuration collection, literature/provenance review, G1 boot/format tracing, G1 checker/recovery tracing, and host-side synthetic-fixture design can run in parallel. Once exact structures are known, static ABI/crypto auditing and offline filesystem/budget work can proceed independently. Candidate rebuild/integrity review and hardware-test harness development can also proceed in parallel, but real-media qualification must use the final identified candidate hashes.

## Unresolved questions required before hardware work

- For the reported CECHA00 and three named SSDs, what are the exact drive firmware revisions, native sector counts, logical/physical sizes, current HPA/DCO exposure, and health? What is the complete PNY model identifier?
- What exact incompatible-drive error code/text appears, at which startup stage, and does it also appear with a blank verified drive?
- Which remaining retail format, mount, checker and updater call paths consume capacity and geometry, beyond the locally verified recovery refusal and the bounded formatter/checker traces?
- Is there any independent recovery/updater copy or alternate kernel that would escape a runtime patch?
- How much memory is available to each checker invocation on this retail configuration, and what is its populated-filesystem peak?
- What are the actual flush/commit durability guarantees of this firmware/drive combination, and are failures surfaced through the full stack?
- Can a verified original image be decrypted/read, restored to scratch media, and mounted on this exact console? Can console state be restored safely after candidate firmware experiments?
- Which physical drives and console/encryption families can be included in the initial support matrix?
