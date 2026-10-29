# HW001H metadata and P4 mount change

2026-10-11. Primary-agent review of actual local read-only disk evidence, kernel instructions and bounded layout evaluation. No separate agent or human review is claimed.

The user supplied this CECHA00's 48-byte eid_root_key locally and identified the connected Crucial as Disk4. The verified inspector initially stopped with Windows access denied, before obtaining a device handle. The same guarded inspector then ran through an elevated hidden PowerShell process and completed at `observations/HW001H/capture-20261011-192252-058`. It opened GENERIC_READ only, verified the opened handle's length and USB serial, and captured 1,172,992 bytes from five bounded ranges. Ten raw/decoded files pass their recorded size/SHA256 checks. Key contents and derived material were neither printed nor exported. No device writes, mounts, filesystem repair, initialization, formatting, HPA or settings changes were issued.

The CBC-192 decryption yields the expected disk-label and UFS2 magic, plausible root inode, and cylinder-summary totals exactly matching the superblock. This is strong format/key correspondence, not a complete integrity test. Windows reports RAW because it does not recognize this encrypted PS3 layout.

| Observed field | Value |
| --- | ---: |
| Physical bytes / logical sector bytes | 2,000,398,934,016 /512 |
| HDD0 start /length, sectors | 32 /3,902,834,832 |
| HDD0 filesystem and partition bytes | 1,998,251,433,984 |
| Second region start /length, sectors | 3,902,834,864 /4,194,296 |
| UFS2 fragment /block bytes | 4096 /16384 |
| fs_ncg /fs_cssize /fs_contigsumsize | 6602 /106496 /8 |
| fs_clean /fs_flags /fs_pendingblocks | 1 /2 /0 |
| Sum of directory /free-block /free-inode /free-fragment summaries | 1 /118134415 /244221181 /7 |
| Root inode | directory0755, links2,512bytes, first fragment2368 |
| Even-byte rounded full-check bitmap | 60,981,796 bytes |

The mount name is empty and summary counts remain consistent with a fresh format. The root directory data itself was not captured; no assertion about its entries or whole-volume consistency follows. A clean flag does not establish integrity after the forced shutdown.

## Concrete mount rejection

LV2 ELF SHA256 `3aaab44f55c2187864e758d84e9db022f1a9e40465addf06d95b15b0723122a9`. At low VA2cac4c the kernel tests fs_contigsumsize at+524. For a positive value, VA2cac64..70 computes:

`fs_cssize + 4*fs_ncg + fs_ncg =106496+26408+6602 =139506 bytes`.

VA2cac74 sets the limit131072 (`3c000002`, lisr0,2); VA2cac7c branches to2caeec when the unsigned aggregate exceeds it. The failure sets numeric status0x80010038 and takes the mount cleanup path. This is a demonstrated rejection for the measured geometry if that mount path executes. No runtime PC/return trace was captured, so it is not conclusive proof that this is the sole cause of the photographed ten-minute stall.

Correction to the earlier inspector report: its `summary_within_traced_128KiB_mount_bound:true` checks **fs_cssize alone**. It is insufficient to evaluate the actual aggregate guard. The new offline report records the complete predicate and supersedes that interpretation without modifying the original captured evidence.

## Allocation and copy bounds for the proposed change

P4 changes only ELF2dac77 from02 to03, replacing `lisr0,2` with `lisr0,3`: aggregate ceiling196608bytes. It preserves P3's admission gates, formatting geometry, reserve, cryptography, updater/version and checker behavior.

The existing code uses a64KiB primary buffer. For the actual summary>64KiB, VA2cae48..58 requests aggregate-65536 =73970bytes from kernel malloc at64824. It checks for a null result at2cae64..68 and preserves the original cleanup path. The kernel allocator's13 size classes at2d82cc span32..131072bytes;73970 selects131072. This is an existing class, not a newly invented pool or allocation API. Live pool headroom is still a hardware question.

Summary reads are in16384-byte blocks, with the final8192bytes; the copy switches to the allocated tail after65536bytes. The remaining40960 summary bytes,26408 max-cluster bytes and6602 contiguous-directory bytes end at73970 exactly. The bounded evaluation verifies copies and array ends on this actual geometry, representative smaller valid layouts,192KiB equality/above-bound cases and the allocation-failure branch. It is an arithmetic/control-flow model, not execution of Sony kernel code or proof for arbitrary damaged superblocks. For valid UFS2 summaries, summary allocation is fragment-rounded and includes16bytes per cylinder group; arbitrary inconsistent/corrupt geometry is outside this experiment's qualification.

Evidence: `analysis/hw001h/metadata-analysis.json`, its hashed mapped captures and `analysis/hw001h/analyze_metadata.py`. Upstream [FreeBSD5.5 ffs_vfsops](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/5.5/sys/ufs/ffs/ffs_vfsops.c) corroborates the summary/max-cluster/contiguous-directory roles; Sony's actual split-buffer allocation and guard are established by the local binary, not inferred from FreeBSD source.

This justifies a minimal preserved-filesystem boot experiment. It does not resolve the independently known32MiB full-check budget: the actual60,981,796-byte bitmap alone exceeds that budget. No repair, database rebuild, valuable-data migration or larger-capacity qualification is admitted by P4.
