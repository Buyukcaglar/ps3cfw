# Independent research: PS3 internal SATA capacity

Research date: 2026-10-11. This document records independently discovered primary-source leads and qualifications. It does not report a console test or authorize installation of a modified firmware. No physical disk was accessed, no HPA/DCO was changed, and no supplied firmware file was modified by this research task.

## Most consequential findings

1. The current PS3 Developer Wiki contains a **September 2026 addition**, substantially newer than the commonly repeated 2016–2024 explanations. It supplies unusually specific 4.93 CEX disassembly locations and claims a patched 3 TB Reference Tool experiment. Treat these as valuable leads to verify against the exact supplied PUP, not as independent proof of stable retail-console operation.
2. Decimal 2 TB and binary 2 TiB are different targets. A representative 2 TB disk has 3,907,029,168 sectors of 512 bytes. That is below 2^32 sectors. A 32-bit *unsigned* LBA ceiling alone cannot explain rejection of that disk. A signed 32-bit sector calculation, earlier byte-capacity gate, filesystem geometry, or another path can still fail below 2 TiB.
3. Public source corroborates 64-bit partition starts/sizes and capacity reporting. This is an internal PS3 partition table, not a PC MBR capacity problem. It does not prove that every firmware consumer preserves those widths.
4. Repairability is an independent acceptance gate. The BSD checker allocates more than its whole-volume bitmap; file and directory population must be tested, not just blank formatted capacity.
5. The official Evilnat first post and source repositories provide no discovered claim that stock 4.93 enables full internal 2 TB or larger drives. Its HDD-space toggle changes a reserved-space policy, which is a separate feature.

## Current wiki addition: exact research lead, limited corroboration

Source: [Harddrive, revision 78223](https://www.psdevwiki.com/ps3/index.php?oldid=78223&title=Harddrive), with [revision history](https://www.psdevwiki.com/ps3/history/Harddrive). The history attributes the capacity-section expansion to Sage on 2026-09-16, adding 5,860 bytes. The previous revision is [77058, 2026-02-01](https://www.psdevwiki.com/ps3/index.php?oldid=77058&title=Harddrive).

The new section identifies four issues: fsck workspace, an emer_init recovery gate, LV2 region-size truncation, and UFS cylinder-group summary limits. Its cited 4.93 locations are emer_init VA 0x46198, LV2 low VA 0x28086c, and LV2 mount low VA 0x2cac74. The capacity gate is described as 0x180 shifted left 32 bits, or 1,649,267,441,664 bytes. It claims 3 TB operation on modified REBUG 4.84.1 DECR, with relevant routines matching 4.93 CEX, but no linked reproducible patch, hash-pinned experiment record, or endurance evidence was found in this search.

**Arithmetic correction:** the table says 3,907,029,168 sectors crosses 2^32; it does not. This internally inconsistent row should not be copied into the project conclusions. Local disassembly and actual geometry/readback remain necessary.

## Evilnat 4.93 release and published code

Primary author release: [Evilnat's maintained PSX-Place first post](https://www.psx-place.com/threads/4-93-evilnat-w-cobra-v8-5-cex-pex-d-pex.39743/). The post identifies 4.93 OFW as its CEX base, links CEX/PEX/D-PEX downloads dated 2026-03-31, and links the author's Cobra and xai repositories. The first post was last edited 2026-04-11. The inspected published feature list does not announce an internal capacity extension. Absence from a feature list is not a binary-level proof.

Observed repository heads, obtained from the GitHub tree API on the research date:

| Repository | Observed commit | Relevant material |
| --- | --- | --- |
| [xXEvilnatXx/Cobra-PS3](https://github.com/xXEvilnatXx/Cobra-PS3) | 608ac4aa052e69ad50e84d9509b8010257b7f331 | 8.5/4.93/CEX/SRC tree, storage definitions, hooks, symbols |
| [xXEvilnatXx/xai_plugin](https://github.com/xXEvilnatXx/xai_plugin) | 7c444b70759836b5fa1c9895b0788545e9b214ce | cfw_settings.cpp and functions.cpp |

Public source shows [Cobra storage.h](https://github.com/xXEvilnatXx/Cobra-PS3/blob/608ac4aa052e69ad50e84d9509b8010257b7f331/8.5/4.93/CEX/SRC/lv2/include/lv2/storage.h#L51) declaring a 64-bit sector count and 32-bit sector size (lines 57–58); its read/write declarations use 64-bit starting sectors (lines 96–97). These interfaces disprove the assumption that capacity must inherently be a 32-bit quantity everywhere. They do not audit the kernel implementation.

[xai cfw_settings.cpp, unlock_hdd_space](https://github.com/xXEvilnatXx/xai_plugin/blob/7c444b70759836b5fa1c9895b0788545e9b214ce/xai_plugin/cfw_settings.cpp#L3420) searches an in-memory UFS signature and toggles 8 to 1 plus an optimization field. It does not change ATA capacity, partition length, or the emer_init gate in that function. Its README describes this as recovering reserved internal HDD space. Preserve the normal reserve while qualifying capacity; mixing these changes would obscure failures.

The available repositories cover added CFW components, not a clean complete source release of Sony's storage stack. A source inspection is therefore complementary to PUP extraction and exact firmware disassembly.

## Checksum corroboration

The developer release post has no discovered PUP MD5; its MD5 mention concerns OtherOS files. A separate archive's own catalog lists standard 4.93 CEX PUP MD5 **D3AF31CE6BDBC6790A5504CF8B3DA1B2**, with displayed size 205.77 MB: [MidnightChannel Evilnat catalog](https://archive.midnightchannel.net/SonyPS/Firmware/index.php?cat=EVILNAT&legacy=1).

That is archive corroboration, not an author-signed checksum or a substitute for the supplied PUP's local SHA-256 and package-integrity verification. The noBD, noBT, and combined variants have different hashes; do not use their hashes for standard CEX.

## Internal partition widths: source-level corroboration

[3141card/picard's HDD Reader source, mirrored by jhonathanc](https://github.com/jhonathanc/PS3-HDD-Reader), observed commit 2e76371bd899f790fcc30ced163b9db62fb7671e, defines `d_partition` with 64-bit `p_start` and `p_size`: [src/fs/ufs/ps3.h, lines 15–17](https://github.com/jhonathanc/PS3-HDD-Reader/blob/2e76371bd899f790fcc30ced163b9db62fb7671e/src/fs/ufs/ps3.h#L15). [device.c](https://github.com/jhonathanc/PS3-HDD-Reader/blob/2e76371bd899f790fcc30ced163b9db62fb7671e/src/device.c#L419) byte-swaps these 64-bit values when discovering the partitions.

The project's recovery tool accepts raw HDD images and needs the console-specific EID root key. This gives an independent way to read test-image partitions and extract files, after its parser and high-offset arithmetic are independently qualified. Do not assume a third-party reader is automatically safe for writes or handles all capacities simply because its table fields are wide.

## Filesystem checking: why blank-volume success is insufficient

Primary upstream comparison: [FreeBSD releng/6.0 fsck_ffs/setup.c](https://github.com/freebsd/freebsd-src/blob/releng/6.0/sbin/fsck_ffs/setup.c#L263), lines 266–290. Its allocation chain includes the fragment bitmap, cylinder-group state, and arrays scaling with directory counts. The [UFS structures](https://github.com/freebsd/freebsd-src/blob/releng/6.0/sys/ufs/ffs/fs.h) are useful for mapping the PS3's derived implementation. [NetBSD 6 setup.c](https://github.com/NetBSD/src/blob/netbsd-6/sbin/fsck_ffs/setup.c) is a second upstream comparison, not proof of identical PS3 behavior.

Inference: a claimed memory container large enough for the bitmap alone does not establish repairability of a populated filesystem. Trace peak allocations and error handling in the PS3 checker, including automatic dirty-start, recovery-menu, and any firmware-update-triggered paths. At 4 KiB fragments, bitmap-only estimates are approximately 29.1 MiB at decimal 1 TB, 58.2 MiB at decimal 2 TB, 87.3 MiB at decimal 3 TB, and 116.4 MiB at decimal 4 TB. These arithmetic estimates exclude inode/directory state and allocator overhead.

## Primary experiments missed by common capacity summaries

[T.D./sandungas original maintenance-threshold discussion, page 5](https://www.psx-place.com/threads/ps3-1-75-tb-internal-hdd-upgrade-formatting-utility.11989/page-5): the 2022 discussion distinguishes startup refusal of filesystem maintenance from failures partway through a populated-disk check. Reports include approximately 960–965 GiB maintenance boundaries, and a separate user's failure around 600 GB used on smaller drives. This is empirical, heterogeneous forum evidence; it does not establish one universal constant.

[andshrew's cloning/expansion experiments, page 16](https://www.psx-place.com/threads/tutorial-hdd-mounting-and-decryption-on-linux.23308/page-16): December 2023 tests found different behavior with modern BSD growth tools versus NetBSD 6.0, including repair loops and incorrect free-space accounting. Initial successful operation was not a sufficient final check.

[andshrew's follow-up, page 19](https://www.psx-place.com/threads/tutorial-hdd-mounting-and-decryption-on-linux.23308/page-19): in May 2024, after roughly six months of apparently normal PS3 use following recovery, the filesystem showed invalid inode data and extended checking. This materially weakens any claim that a boot plus short write trial establishes safe long-term compatibility.

[Original migration/recovery notes](https://gist.github.com/andshrew/1d0b5e35308a6fd9770831e47950be0a) and [NetBSD 6.0 expansion notes](https://gist.github.com/andshrew/4c1fe1c432d3d77e9bddf978426d34a2) are useful reproducible research references. Do not run their write commands on the production disk; BSD-version compatibility itself is one of the unsettled variables.

## Sector format is a separate research axis

Primary author investigation: [andshrew, PS3 Compatibility with 512e Drives](https://ps3hdd.pages.dev/blog/ps3-512e-compat/), 2024-01-06. It reports CECH-2503A/OFW 4.90 experiments showing different UFS `fsbtodb` and inode block accounting between 512n and 512e media. Changing the superblock for PC access is later undone by PS3 mounting; PC-created file accounting may consequently disagree with PS3 expectations. NetBSD write mounting can also clear a flag needed by the console. The author separates observed differences from suspected corruption consequences; this does not prove every 512e drive is unsafe.

For capacity qualification, record the actual drive's model, firmware, native/current sector counts, and **both logical and physical sector sizes through direct SATA**. Bridges can alter reported geometry. Prefer a known 512-byte-logical baseline and do not introduce native-4K support into the initial 2 TB target. The same model name may cover different physical-sector implementations.

## Other tool sources worth investigating, without trusting their writers

[Pheeeeenom/PS3HDDTool](https://github.com/Pheeeeenom/PS3HDDTool) provides a current cross-platform codebase with UFS2 parsing, decryption, extraction, and PS3 write features; its current README explicitly describes synthetic verification. Its [PS3 filesystem reference](https://github.com/Pheeeeenom/PS3HDDTool/blob/main/docs/PS3_UFS2_Filesystem_Reference_Final.md) is a mapping lead. It should be reviewed and pinned before using it as an oracle; synthetic fixture tests are not retail PS3 endurance evidence.

[einsteinx2/PS3-Reclaim-HDD-Space](https://github.com/einsteinx2/PS3-Reclaim-HDD-Space) explains reserved UFS space tuning and source-level manipulation. This addresses filesystem free-space policy, not the physical capacity rejection.

## Research implications for the project plan

- First reproduce capacity decisions against the **exact PUP's modules**. Match strings and call graphs to the incompatible-HDD screen; do not guess from the UI message alone.
- Preserve a full signed/unsigned arithmetic audit trail at sector_count × sector_size, partition-end addition, request-end comparisons, byte↔fragment conversion, and filesystem-summary sizing.
- For decimal 2 TB, test the recovery gate and every boot/mount/repair consumer before changing a >2 TiB kernel path that may not be relevant yet.
- Keep separate tickets for decimal 2 TB, 2 TiB boundaries, and 3/4 TB media. Use exact sectors in evidence, never ambiguous TB labels.
- Preserve UFS geometry and reserve where possible for the first milestone. Any geometry change must be tested in formatter, mount, repair, free-space accounting, file copy, and backup/restore.
- Qualify repair with low occupancy, high occupancy, many small files/directories, near-full operation, deletions, background installs, reboot cycles, clean and dirty states, and high-offset patterned data readback. Keep independent checksums and fault-recovery evidence.
- Obtain private console recovery material before hardware experiments; do not print keys or publish dumps containing identity data. Use disposable media and retain the original disk untouched.
- An emulator or offline UFS reader can validate a component or fixture. It cannot prove the console's LV1/SATA/ENCDEC/boot/recovery path works safely.

## Search scope and unresolved provenance

Independent queries covered exact sector counts, emer_init/newfs_cfs/libfs_utility names, 2 TB/3 TB DECR reports, Evilnat 4.93 feature/changelog/hash claims, source partition widths, fsck allocations, and original author experiments. No separately indexed test log, downloadable patch manifest, or other primary record corroborating Sage's new 3 TB result was located. Its substantive claims remain priority local-verification targets. No claim of guaranteed zero data loss follows from this research.
