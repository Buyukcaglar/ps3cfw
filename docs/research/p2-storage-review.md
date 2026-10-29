# P2 storage and emergency-loader review

Date: 2026-10-11. Read-only static review after the user reported that HDD2TB-P1 installed and booted with the control drive, but accepting the startup format prompt with a Crucial `CT2000BX500SSD1` produced the unsupported-hard-disk message. The observed drive geometry, exact executing emergency image and underlying storage status have not been captured. The format prompt alone does not establish that the modified admission comparison ran.

## Result

This pass found no second capacity branch in the traced LV2/LV1 region-creation chain that justifies another patch for decimal 2 TB. Its start and length arguments, disk-length field and initial range comparisons remain 64-bit. The earlier LV2 read-path region-length truncation is real, but a normal decimal-2TB/512-byte region length fits its unsigned 32-bit range. It therefore does not explain the reported failure by itself.

The LV1 emergency loader requests `emer_init.self` from bank selector 0. In the `ros` header format, selector 0 means the header-declared current half, while selector 1 switches to the other half. Matching the P1 emergency image in a flash dump's declared half would establish installed bytes and their declared selection. It would still not establish which executable ran during the failed boot. This is the next useful evidence boundary, given the separate UI audit's connection between the precise unsupported message and the admission helper.

## Reproduction and inputs

Run `python analysis/p2-storage-review/capture_p2_evidence.py`. This captures 25 bounded disassemblies plus `analysis/p2-storage-review/p2-evidence-manifest.json`. The helper only reads existing regular firmware files and writes investigation artifacts under its own directory; it does not rebuild PUPs or access physical disks.

| Input | SHA-256 |
| --- | --- |
| `analysis/coreos/lv2_kernel.elf` | `3aaab44f55c2187864e758d84e9db022f1a9e40465addf06d95b15b0723122a9` |
| `analysis/candidate-review/lv1.elf` | `dec10390c6617078b693ffd859598ce96e81d8c0de37ae34e4e95d2563f0cef3` |
| `analysis/p2-storage-review/lv1-embedded-33.elf` | `3956a8b12b387280793fe601cac988dacaecdcd9368a7b6a9080c153505ac97b` |

Addresses in the next sections are ELF virtual addresses. LV2 addresses use high base `0x8000000000000000`; abbreviated LV2 addresses below omit that base. Main LV1 uses low addresses; the embedded secure-process ELF uses `0x80000000` code and `0xc0000000` data addresses. Do not apply one image's VA/file mapping to another.

The embedded debug SELF has outer LV1 ELF file offset `0x34beb0`, VA `0x55beb0`, authentication ID `0x1070000033000001`, header length `0x480` and ELF/data length `0x4a860`. Removing the plaintext debug header produces a valid ELF with public section offsets agreeing with header-plus-ELF offsets. A native scetool attempt could not find a keyset; its zero process exit did not validate this extraction. The extraction is a direct plaintext-layout observation, not independent native decryption proof.

## LV2 to LV1 region creation

The actual 4.93 syscall table at `0x363be0` gives these descriptors/entry points:

| Syscall | Meaning used here | Descriptor VA | Code VA |
| --- | --- | --- | --- |
| 609 | Get device information | `0x33fee0` | `0x27b6a8` |
| 610 | Get global storage configuration | `0x33ff10` | `0x27ba40` |
| 614 | Create storage region | `0x33ffb8` | `0x27c28c` |
| 615 | Delete storage region | `0x33ffa0` | `0x27c1d8` |
| 622 | Get region offset | `0x33ff58` | `0x27be64` |

The [pinned Evilnat 4.93 CEX symbols](https://github.com/xXEvilnatXx/Cobra-PS3/blob/608ac4aa052e69ad50e84d9509b8010257b7f331/8.5/4.93/CEX/SRC/lv2/include/lv2/symbols.h) agree with the syscall table and storage helpers in this binary. The [LV2 syscall catalog](https://www.psdevwiki.com/ps3/LV2_Functions_and_Syscalls) supplies useful names, but its guessed syscall-610 interface must not override the actual entry: this entry writes two 4-byte global outputs rather than converting a capacity argument.

The concrete region-create chain is:

1. Syscall 614, `0x27c28c`, retains the original `r4`–`r7` arguments and uses an 8-byte kernel output for the created region ID. The `clrldi ...,32` at `0x27c2fc` narrows the object handle used by the kernel object lookup, not the start or length. The successful result is copied to userspace as 8 bytes.
2. Device dispatcher `0x27d13c` looks up the device and invokes interface vtable slot `+0x50`, retaining the 64-bit arguments. Missing device/interface returns `0x80010006`.
3. LV1-backed implementation `0xaa60c` loads the underlying device ID from object `+0x98`. At `0xaa798`–`0xaa7b0`, it supplies the retained start, length and option arguments to hypercall 250 (`li r11,0xfa; sc 1`). It captures returned region ID and asynchronous tag. The nonzero hypercall-return branch at `0xaa7d0` joins cleanup ending with `0x8001000c`; an upper generic error cannot recover the original HV rejection. Earlier object, queue and wait failures have their own branches, so this does not mean every storage failure is this one code.
4. The [HV syscall catalog](https://www.psdevwiki.com/ps3/HV_Syscalls) identifies 250 as region creation. In this actual LV1, constructor instruction `0x202c20` assigns function descriptor `0x34fc20` to record `0x3c2af0` (call number 250). That descriptor selects code `0x3090f4`. The adjacent `0x34fc08` descriptor is the delete wrapper, not the create wrapper.
5. `0x3090f4` adds the current LPAR and calls `0x251a4c` at `0x3091d8`. Device dispatch checks device identity/access/state, then calls `0x254a3c` at `0x251b9c`. That function checks device support/state and calls region manager `0x25c584` at `0x254b0c`.

In region manager `0x25c584`, `r5` is start sector and `r6` is length in sectors. The initial checks use `ld`, `divdu`, `cmpld` and 64-bit subtraction:

| Check / result | Address |
| --- | --- |
| Minimum start = `4096 / device_block_bytes`; start below minimum rejects | `0x25c5a4`–`0x25c5dc` |
| Region0's 64-bit length must exceed start | `0x25c5ec`–`0x25c5f8` |
| Requested length must be no larger than `region0_length - start` | `0x25c600`–`0x25c610` |
| Reserved argument `r7` must be zero | `0x25c614`–`0x25c618` |
| Those invalid-range/argument cases return numeric HV status `-17` | `0x25c7dc` |
| No free region object returns `-2` | `0x25c788` onward |
| Overlap with an existing region rejects with `-7` | `0x25c6b4`–`0x25c6c8`, cleanup through `0x25c888` |
| Access-entry setup failure returns `-32768` | `0x25c6e4` onward / `0x25c72c` |
| Partition-table update is called; its nonzero status propagates | `0x25c8e4` onward |

Record initializer `0x25d5ec` stores start at region `+0x40` and length at `+0x48` with `std`. Region0 initializer `0x25aed0` takes length from device `+0xd90` using `ld` at `0x25af94`, then calls that record initializer. No signed-32-bit sector-count comparison or 1536-GiB byte ceiling appears in this observed chain. This is not a proof that all device-specific methods or partition-table I/O succeed on 2 TB hardware.

## ATA capacity intake

The SATA/ATA initialization path publishes the 64-bit field at device `+0x1608` to the generic device sector count through `0x253350`, which uses `std` to device `+0xd90`. It sets logical block size to `0x200` in this path.

The parser sets its `+0x1610` selector from bit 10 of byte-swapped IDENTIFY word 86 at `0x270448`–`0x27048c`. If that selector is zero, `0x2706dc`–`0x270718` assemble words 60/61 and sign-extend the resulting 32-bit word. Otherwise `0x2707e4`–`0x270854` assemble words 100–103 into a 64-bit field without that signed-32-bit narrowing. The fields' legacy and extended capacity interpretation agrees with the primary [smartmontools ATA size parser](https://www.smartmontools.org/static/doxygen/atacmds_8cpp_source.html), which also provides a useful independent way to decode raw IDENTIFY.

There is no evidence that the tested Crucial takes the legacy branch. A conforming legacy 28-bit sector field does not itself reach `2^31`. Changing the legacy `extsw` without measuring the actual selector and IDENTIFY fields would be an unsupported patch. Retain words 60/61, 83, 86 and 100–103 in the actual drive-identity evidence, along with sector-size words and any HPA/DCO information; the retail SKU alone supplies none of those observed values.

## The separate LV2 region-read narrowing

The earlier instruction at LV2 `0x28086c` really zero-extends a region-length field to 32 bits. Nearby code loads requested starting sector as 64 bits, adds a zero-extended request-sector count, and compares that end against the low-32 region length with `cmpld`. Exceeding the resulting region bound returns internal numeric status `-7` at `0x28087c`/`0x2808f0`.

Exactly 2,000,000,000,000 bytes / 512 = 3,906,250,000 sectors, below `2^32`. The illustrative 2,000,398,934,016-byte SATA size is 3,907,029,168 sectors, also below `2^32`. On those ordinary geometries this narrowing preserves the region length. It remains a real barrier to investigate before greater-than-2TiB media; it is not a demonstrated cause of this decimal-2TB admission screen.

## Emergency filename and bank selection

The only literal `emer_init.self` in this LV1 ELF is inside embedded secure process 33. It resolves to embedded VA `0x80027e30`; the next filename is `hdd_copy.self` at `0x80027e40`. Main embedded TOC is `0xc000f300`.

| Stage | Observed behavior |
| --- | --- |
| `0x8000b9a0` | Mode 1 chooses `emer_init.self`; mode 2 chooses `hdd_copy.self`; other modes reject. It calls lookup `0x8000de70`. |
| `0x8000de70` | Builds the flash loader from cached format/device/base settings. At `0x8000dedc`, explicitly sets bank selector `r4=0`, then calls `0x8001d054`. |
| `0x8001d054` | Opens container kind 7 through `0x8001cebc`, reads its file table, then looks up the supplied filename with `0x8001de24`. |
| `0x8001cebc` | Allows selectors 0 and 1. Mode 1 uses `0x8001cd50`; mode 2 uses `0x8001cc24`. |
| Flash configuration `0x8001f008` | Repository `sys/flash/fmt` value 0 selects loader mode 1. Other formats can use repository bank values and `ros0`/`ros1`-style names; that is a distinct branch. |
| `0x8001cd50` | Finds literal `ros`; reads its 32-byte bank header via `0x8001dd44`; reads header `+8` current offset and `+16` enclosing length; calculates `(length-0x20)/2`. Selector 0 uses the current offset, while selector 1 adds/subtracts one half to choose the other. |
| `0x8001cc24` | For its separate format, queries the OS-bank repository and selects one of two names before finding the file table. |

No retry of the other selector, alternate emergency filename or duplicate emergency file was identified in this local lookup chain. This is bounded to the inspected methods; earlier boot-bank recovery policy, outer platform behavior and live repository state are not established by this observation.

For the CECHA00 NAND-style dump, a parsed header near `0xc0000` and full CoreOS comparison of both halves can establish the declared current half, exact P1 installation in either/both halves, and a stale original in an alternate half. The dump must first be identified as the actual expected reconstructed NAND layout; these absolute offsets are not universal for raw NAND pages, interleaved/ecc-bearing images, NOR or other dumper formats. The header alone is a declaration, and a successful control boot alone is not a readback of the emergency executable used for the later blank-drive boot.

## Next decision

First establish flash contents and declared selection using a read-only dump from the control drive, and retain the exact failure wording/order. If the expected P1 image is present in the declared half, measure the console's returned device-info geometry and, if needed, add a narrowly scoped diagnostic at the admission decision before attempting another capacity change. If an actual region-create failure is later observed, preserve the HV status before the LV2 wrapper collapses it, plus device ID/start/length/block size, so that the rejecting check can be reproduced. No replacement firmware bytes are recommended by this storage audit.

## Measured Crucial IDENTIFY comparison

Later on 2026-10-11, the parent investigator supplied a successful, authorized read-only PC SAT observation at `observations/Crucial-PC-ATA-20261011-160513-777/`. Its three retained smartctl 7.5 queries each report exit status 0. The ATA model is `CT2000BX500SSD1`, firmware `M6CR091`. The ATA serial identifies the SSD separately from Windows' USB-bridge serial; those two serial fields must not be treated as contradictory SSD identities.

| Saved observation | Value | Effect in the pinned LV1 code |
| --- | --- | --- |
| IDENTIFY word 64 | `0x0003` | Unrelated mode flag is evaluated in the selector block; no capacity truncation follows from it |
| Word 86 | `0x8401` | Bit 10 is 1; the instructions at `0x270448`–`0x27048c` store 1 to device `+0x1610` |
| Words 100–103 | `0x88b0:e8e0:0000:0000` | The selected extended-capacity instructions assemble `0x00000000e8e088b0` = **3,907,029,168 sectors** |
| Words 60/61 | `0xffff:0x0fff` | Legacy count is 268,435,455; this branch is bypassed when the observed word-86 selector is used |
| Logical / physical sector bytes | **512 / 512** | Agrees with LV1's literal `0x200` block-size publication in this ATA path |
| Word 106 / words 117–118 | `0x4000` / zero | Consistent with the saved smartctl default 512-byte logical-sector interpretation |
| Word 209 | `0x4000` | No nonzero sector-alignment offset is reported by the captured identity |

`analysis/p2-storage-review/compare_crucial_identify.py` reads those saved files and evaluates the exact decoded integer/load/store instructions in the selector and extended-capacity ranges against their little-endian ATA words. Its retained result, `crucial-ata-parser-comparison.json`, records input hashes, LV1 hash, each evaluated instruction and resulting register/store value. This is a bounded arithmetic evaluation: conditional entry into the extended path is selected from the measured flag, and command transport, device initialization, PS3 execution and virtual-device behavior are not emulated.

The resulting count matches the independently saved smartctl JSON. Multiplication by 512 gives **2,000,398,934,016 bytes**, exactly the saved capacity, **129,904,844,800 bytes below P1's 2,130,303,778,816-byte threshold**. The count also fits the LV2 read path's unsigned 32-bit region-length field. Generic device publication and region0 initialization retain that count through the previously traced `ld`/`std` operations.

**No contradiction requiring a code fix was found for the measured inputs.** In particular, neither the legacy sign extension nor a 4Kn/512-byte mismatch explains these observations. This establishes the drive geometry reported through the captured PC SAT path; it does not establish the PS3's actual returned device-info fields. Installed NAND readback and declared bank selection therefore remain useful next evidence, followed by a narrow on-console decision/geometry diagnostic if necessary.
