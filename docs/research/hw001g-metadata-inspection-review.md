# HW001G result and next metadata inspection

2026-10-11. Existing P3, CECHA00, preserved formatted Crucial CT2000BX500SSD1. User explicitly authorizes requesting and using the console's own HDD decryption material.

## Returned hardware evidence

Two photographs show the controller USB-cable/PS-button prompt followed by the complete six-option Safe Mode menu. No firmware USB was present according to the user. `Restart System` is highlighted; movement, elapsed time and shutdown behavior were not supplied. No menu operation execution is shown. The exact images and hashes are in `observations/HW001G/photo-manifest.json`; structured result is `result.json`.

Recovery-menu reachability distinguishes this from the normal-startup wave stall. It does not establish that XMB's filesystem mount succeeds, that the on-disk superblock is valid, or that 2 TB addressing/repair is qualified. No additional Recovery operation is requested.

## Why inspect metadata next

P3's admission changes permit native formatting to report completion, but the actual partition sizes, UFS2 fragment/block geometry, cylinder summary size, clean/dirty flags and soft-updates state remain unread. Reading those fields can discriminate between actual formatter output and the earlier geometry model before expanding firmware scope. Metadata alone cannot identify a blocked runtime PC, validate all cylinder groups or prove integrity. Startup instrumentation remains a possible next step if metadata is coherent.

## Source and implementation review

Primary source acquired read-only for analysis: [3141card PS3-HDD-Reader](https://github.com/jhonathanc/PS3-HDD-Reader), pinned commit `2e76371bd899f790fcc30ced163b9db62fb7671e`, under `tools/PS3-HDD-Reader`. Its `src/kgen.c` derives a retail ATA key by AES-256-CBC encryption of `sb_indiv_seed_00`, with the 32-byte EID root key and following 16-byte IV. Its `src/device.c` swaps each raw 16-bit pair, then applies CBC-192 using the first 24 derived bytes and a zero IV per 512-byte sector for FAT/NAND. The primary partition table is at sector zero; UFS2 superblock is at partition offset 65,536, big-endian magic at +0x55c. Field offsets are cross-checked against `src/fs/ufs/fs.h` and table entries against `src/fs/ufs/ps3.h`.

The acquired reader also contains write functions and opens disks with read/write access. It is **not executed** for this probe. New `tools/inspect_crucial_metadata.py` implements only the bounded CECHA00 read/decode path, with GPL-2.0-only attribution. The upstream license is retained at `tools/PS3-HDD-Reader/LICENSE`. There is no XTS/VFLASH or general repair fallback.

`tools/Inspect-CrucialMetadataReadOnly.ps1` identifies exactly one nonboot/nonsystem USB disk matching the earlier Crucial bridge serial, size, model substring and 512-byte logical sectors. It does not reuse the historical Disk3 assumption. Python rechecks the recorded identity, opens that selected PhysicalDrive with **GENERIC_READ only**, and queries length and USB serial through that open handle before reading sectors. The only DeviceIoControl codes are information queries: disk length and storage descriptor. There is no WriteFile, DeviceIoControl mutation, volume mount, disk-attribute change, partition change, ATA setting or repair operation. Missing privileges or identity mismatches stop the probe.

Captures are limited to the 1,536-byte disklabel, an 8 KiB potential primary superblock per nonempty partition, and for recognized UFS2 a prefix of at most 1 MiB and a cylinder-summary region of at most 128 KiB. Region offsets, nonoverlap and device bounds are checked before following entries; geometry is checked before following the summary pointer. Both raw encrypted and decoded copies are saved locally with offsets, lengths and SHA256 values. No console key bytes, key hash or derived keys are printed or written. Outputs are created exclusively; partial/error captures are preserved.

## Verification and limits

`analysis/hw001g-followup/make_dotnet_fixture.ps1` independently generates a synthetic encrypted image using .NET AES, synthetic 48-byte console material, zero-IV sector encryption and raw pair swapping. The Python inspector recovers byte-identical disklabel and superblock and leaves the fixture image hash unchanged. Thirteen checks pass, including partition starts above 2^31, wrong key/length, out-of-bounds/overlapping partitions, impossible filesystem size, truncated metadata and unaligned ciphertext. Record: `analysis/hw001g-followup/metadata-tool-verification.json`, including exact inspector/wrapper hashes.

This verifies synthetic crypto/format handling, not the actual console material or physical-handle path. Windows descriptor formatting could differ; a guard rejection must be investigated, not bypassed. Real decryption additionally requires partition-table and UFS2 magic plus consistent geometry. Wrong key or unsupported layout stops. A valid clean flag is not integrity proof. The capture is intentionally partial, not a full disk backup.

## Obtaining the local console material

The supplied firmware's `category_network.xml` includes `seg_dump_tools` and `dump_erk` invoking xai_plugin's `dump_erk`. Local primary source `tools/xai_plugin_source` commit `7c444b70759836b5fa1c9895b0788545e9b214ce` maps this to `dumpERK(ERK)` and `dumperk()`. Source `erk.cpp` saves a 48-byte `eid_root_key` to `/dev_hdd0/tmp` and, if present, a USB device. Existing material from this same CECHA00 is preferable to repeating extraction.

The built-in extractor performs transient LV1/LV2 memory patches and payload execution; it is not merely a file read. Its normal cleanup restores saved patches, but this source review is not an exhaustive extraction failure-path or binary-equivalence proof. No new extractor, flash patch or conversion tool is supplied. Use only existing CFW's Dump ERK on the working 1 TB HDD; stop on an error or different UI. The next protocol requests no flash writing or CEX/DEX conversion.

## Current dependency

`observations/HW001H/PROTOCOL.md`: provide the local 48-byte file and connect the preserved formatted Crucial via the same adapter. Cancel Windows initialization/format prompts. Then the agent can perform the guarded read-only inspection and continue analysis. No new firmware was generated, staged or backed up in this iteration. Stable support remains false.
