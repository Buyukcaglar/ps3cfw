# Supplied-source research dossier

Checked 2026-10-11 (UTC+3). This is source research, not a hardware qualification or a claim that any proposed patch is safe. No drive, console, or original firmware was modified for this research.

## Access and evidence status

| User-supplied source | Access | Evidence category |
| --- | --- | --- |
| [Reddit maximum HDD discussion](https://www.reddit.com/r/PS3/comments/wqmrq3/what_is_the_maximum_hdd_size_compatible_with_the/) | Direct fetch timed out; search index supplied the post and discussion text | Mixed first-person reports and repeated community advice; no controlled firmware analysis |
| [PSX-Place size-limit discussion](https://www.psx-place.com/threads/thoughs-in-breaking-through-the-ps3-hdd-size-limit-discussion-ideas.42797/) | Read all 15 posts, February–June 2024 | Developer discussion, explicit hypotheses, and first-person HPA use |
| [PSDevWiki Harddrive](https://www.psdevwiki.com/ps3/Harddrive) | Read maximum-capacity section, relevant surrounding storage material, page history and Talk page | Community technical documentation; new disassembly claims require independent binary verification |
| [ConsoleMods upgrading storage](https://consolemods.org/wiki/PS3:Upgrading_your_Storage) | Read complete storage guide | Practical community guidance, not a controlled capacity experiment |
| [PS3 HDD Adventures](https://ps3hdd.pages.dev/) | Read landing page, 512e article, and linked recovery/migration/resize working notes | First-person technical investigations with commands, metadata and logs |

## 1. Reddit supplied discussion

[Discussion, begun 2022-08-17](https://www.reddit.com/r/PS3/comments/wqmrq3/what_is_the_maximum_hdd_size_compatible_with_the/) gives contradictory capacities: common advice recommends 1 TB; some users report years of 1.5 TB use; another claims approximately 1.8 TB with extra setup. A popular warning distinguishes successful formatting/game installation from functioning filesystem maintenance, and describes accumulating damage after crashes or interrupted transfers. The thread also mixes internal and external storage and includes unsupported claims about an “official” capacity limit. No linked Sony specification establishing that numerical limit was verified here.

Use: identify real-world symptoms and investigation cases. Do not use votes, long uptime, or successful game installation as proof of recovery correctness or 4.93 behavior. The supplied thread is older than 4.93 and cannot establish whether the provided PUP is fixed.

## 2. PSX-Place supplied discussion

[Thread 42797](https://www.psx-place.com/threads/thoughs-in-breaking-through-the-ps3-hdd-size-limit-discussion-ideas.42797/) distinguishes PS3 partitioning from PS2 APA. Berion says the actual cause was unknown in 2024 and suggests firmware constraints rather than an intrinsic UFS2/partition-format ceiling. Luisile reports the unsupported-drive startup message with 2 TB drives; psy1 reports years using a Samsung EVO capped to 1.525 TB. These are user reports, not universal compatibility results.

The proposed scheme of lifting HPA after boot to access hidden space was explicitly theoretical. If a crash prevents restoring HPA, the next boot again sees the oversized drive and can refuse it. That makes the scheme unsuitable as the stable first milestone.

Post #10 points to a recovery-module immediate patch, explicitly described as unproven. Post #13 reiterates that the underlying cause or causes remained unknown. Thus the discussion provides leads and counterexamples, not a completed full-capacity 2 TB fix. HPA exposes only a restricted range of sectors; it does not extend the amount PS3 can use.

## 3. Current PSDevWiki capacity claims

[Current article](https://www.psdevwiki.com/ps3/Harddrive#Internal_Harddrive_maximum_capacity) identifies these leads:

| Claimed location | Claimed barrier |
| --- | --- |
| `emer_init.self`, VA `0x46198` | `li r0,0x180; sldi r0,r0,32`, unsigned capacity comparison; reject above 1536 GiB |
| LV2 read/write path, 4.93 VA-low `0x28086c` | `clrldi r28,r28,32` allegedly truncates a 64-bit region bound at 2^32 sectors |
| LV2 mount path, 4.93 VA-low `0x2cac74` | 128 KiB cylinder-group-summary bound; geometry-dependent ceiling near 3 TB |
| `libfs_utility*.sprx` | Filesystem-check bitmap/container sizing; retail and DECR launch paths allegedly differ |

The article claims a patched REBUG 4.84.1 DECR 3 TB experiment and code similarity to 4.93 CEX. It offers no linked patch set, hashes, test corpus, or measurement log for that experiment. Treat these as high-value leads, especially the exact recovery comparison, pending examination of this project's actual binaries. The page itself warns that the historical approximately 963 GiB check boundary is not tied to an identified constant.

### Provenance and internal contradiction

[Page history](https://www.psdevwiki.com/ps3/history/Harddrive) attributes the capacity rewrite (+5,860 bytes) to Sage on **2026-09-16 11:53**. The page's current revision is [oldid 78223](https://www.psdevwiki.com/ps3/index.php?title=Harddrive&oldid=78223). This is substantially newer than the supplied 2024 forum discussion. The [Sage profile](https://www.psdevwiki.com/ps3/User:Sage) does not link test artifacts. A requested revision diff failed to fetch; the history and rendered current revision were accessible.

Independent arithmetic exposes an error in the current table: **3,907,029,168 < 4,294,967,296**. Its approximately 2 TB row therefore does **not** cross 2^32 512-byte sectors, contrary to its note. Consequently the table cannot be copied unquestioningly, and a marketed 2 TB target must be distinguished from a 2 TiB target. This error does not by itself disprove the disassembly snippets.

### Earlier Talk-page patch lead

[Talk:Harddrive, Firmware Patches](https://www.psdevwiki.com/ps3/Talk:Harddrive#Firmware_Patches) records the same unsupported-drive error and threshold, then proposes replacing PowerPC bytes `38 00 01 80` with `38 00 01 F0`, or `38 00 02 01` for a wider threshold. It explicitly says this was **untested on hardware**, based on 4.75, and other factors could fail. The filename in the supplied forum was misspelled `ermer_init`; the documented module is `emer_init`.

These four-byte patterns alone are insufficient patch specifications: exact module hash, instruction context, section/address mapping and failure path are needed. The original bound's presence in the supplied 4.93 binary would establish a remaining static barrier; successful removal would still require recovery and integrity tests.

## 4. ConsoleMods guide

[Guide](https://consolemods.org/wiki/PS3:Upgrading_your_Storage#Notes_on_Drive_Compatibility) recommends at most 1 TiB for avoiding filesystem-recovery problems, while also using “1.75 TB (1.5 TiB)” for a higher technical capacity. Those two numbers are not exact equivalents. It requires 512-byte sector support and physical SATA compatibility. The “8%” reserved-space setting is a separate topic from drive detection/capacity support.

Its migration guidance distinguishes NOR consoles, which need firmware reinstallation, from NAND models. It also states that the built-in Backup Utility does not preserve trophies by itself. That matters for a loss-prevention plan: a single nominal backup operation cannot be assumed to preserve everything.

The guide provides useful compatibility and preservation cases, but does not prove a single fixed maximum across drive model, console, firmware and recovery mode. No exact 4.93 full-capacity 2 TB result appears in the guide.

## 5. andshrew primary technical investigations

[Landing page](https://ps3hdd.pages.dev/) explains per-console encryption, `eid_root_key`, Linux decryption and BSD UFS2 access. Its linked work is aimed at recovery, repair and migration, not demonstrating a universally safe 2 TB firmware modification.

[512e investigation](https://ps3hdd.pages.dev/blog/ps3-512e-compat/) documents tests on CECH-2503A, firmware 4.90. Compared with 512n, its 512e filesystem has `fsbtodb=0` where the examined BSD implementations expect 3, and inode block counts use different units. The article shows concrete metadata, `du` discrepancies, and BSD check errors. It distinguishes those observations from a hypothesis about possible PS3 reliability consequences.

Its warning is material to recovery tooling: merely changing the superblock enough for BSD to mount is not sufficient. New BSD-written files use differing block-count units; PS3 resets the field on remount. NetBSD read/write mounting can remove soft-updates metadata needed by PS3. USB bridges may obscure sector-format reporting. Sample drive-model lists are not guarantees; MX500 variants differ. Qualify the actual drive via direct SATA and preserve original images before any repair experiment.

### Linked recovery and resize notes

[FreeBSD recovery/migration notes](https://gist.github.com/andshrew/1d0b5e35308a6fd9770831e47950be0a) show a `fsck` repair and describe recovering a 640 GB-origin clone on a larger drive after PS3 reported unrepairable storage. They explicitly call themselves a record rather than a tutorial and describe model-dependent encryption/access commands. This supports recoverability in that instance, not automatic safety for every filesystem or capacity.

[NetBSD expansion notes](https://gist.github.com/andshrew/4c1fe1c432d3d77e9bddf978426d34a2) document a 60 GB image cloned to 320 GB, partition extension, `fsck_ffs`, `resize_ffs`, and a successful PS3 boot reporting 298 GB. This is bounded evidence that controlled UFS2 expansion can work at smaller sizes. It neither crosses the disputed thresholds nor qualifies modern 512e conversions. Reserve changes are recorded separately from expansion.

## Followed first-person reports and contradiction

[“2TB SSD ... as 1525 GB”](https://www.reddit.com/r/PS3/comments/qlf8mk/2tb_ssd_on_ps3_works_as_1525_gb/) reports CECHC03/Rebug 4.86 with a capped 2 TB SSD and claims service-menu restoration works. Later in the same discussion, a Samsung SM863a capped to **3,200,000,000 sectors** on OFW 4.90 reportedly reaches a format prompt when “Restore File System” is run; a 1 TB 860 Pro reportedly passes. andshrew says option 3 left his system unbootable, distinguishes option 5 formatting from option 3 checking, and describes apparent automatic checks that leave UFS `clean flag 0`. His linked technical notes support the investigation route. This is direct evidence against equating a displayed check/normal boot with a completed successful check. Long operation without visible failures also cannot establish future recovery behavior.

[“PS3 fat with 2TB SSD (success)”](https://www.reddit.com/r/PS3/comments/1650655/ps3_fat_with_2tb_ssd_success/) was accessible, but no verified full-native-capacity 4.93 qualification was extracted. Its title alone should not be treated as evidence that every sector is usable or repair works.

## Independent capacity arithmetic and project consequences

These are arithmetic, not community capacity recommendations. “GB” in PS3 screens and forum posts may mean GiB; record exact bytes and logical sectors in all future tests.

| Quantity | Bytes | 512-byte logical sectors |
| --- | ---: | ---: |
| 1 TB decimal | 1,000,000,000,000 | 1,953,125,000 |
| 1 TiB | 1,099,511,627,776 | 2,147,483,648 |
| `0x180 << 32` = 1536 GiB | 1,649,267,441,664 | 3,221,225,472 |
| Capped 3,200,000,000 sectors | 1,638,400,000,000 | 3,200,000,000 |
| 2 TB decimal | 2,000,000,000,000 | 3,906,250,000 |
| Example marketed 2 TB drive | 2,000,398,934,016 | 3,907,029,168 |
| `0x1F0 << 32` = 1984 GiB | 2,130,303,778,816 | 4,160,749,568 |
| 2 TiB | 2,199,023,255,552 | 4,294,967,296 |
| `0x201 << 32` = 2052 GiB | 2,203,318,222,848 | 4,303,355,904 |

Implications for a plan, pending binary verification:

1. First milestone should use the actual native sector count of the user's marketed 2 TB drive, not an ambiguous “2TB” string. It is below 2 TiB and above the alleged recovery gate.
2. Keep whole-device detection, partition/region creation, UFS2 mount, read/write bounds, and successful filesystem repair as separate gates.
3. Establish a spare-drive baseline and measure post-check filesystem state and content hashes. Repeat at near-full occupancy and after controlled interrupted writes; tests must never use the sole valuable-data copy.
4. A recovery gate patch is a plausible entry experiment. Blindly adding LV2 and geometry patches for decimal 2 TB would enlarge scope without first establishing necessity.
5. The >2 TiB phase requires fresh overflow/boundary analysis, including the alleged region-size truncation and geometry/memory paths. The current wiki's 3 TB and 8–16 TB claims remain externally reported research, not this project's achieved behavior.
6. Normal shutdown, recovery, failed/partial update, firmware reinstallation and return to the original drive all need explicit outcomes. A boot-only success does not satisfy a stable or data-preserving release.

No firmware image has been executed on hardware in this research. No zero-data-loss guarantee can be established by these sources; the achievable target is bounded, repeatable integrity evidence plus verified backup/recovery procedures.
