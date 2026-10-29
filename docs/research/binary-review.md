# Independent review of supplied firmware storage paths

Reviewed 2026-10-11. Read-only examination of the ELF files extracted by the parent task. This review confirms code in these files; it does not establish an executed console result, a safe patch, or data integrity on a physical drive.

## Identity and address conventions

| File | SHA-256 |
| --- | --- |
| `analysis/coreos/emer_init.elf` | `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d` |
| `analysis/coreos/lv2_kernel.elf` | `3aaab44f55c2187864e758d84e9db022f1a9e40465addf06d95b15b0723122a9` |

For the emer_init addresses used below, ELF file offset = VA minus `0x10000`. Its code and data PT_LOAD segments both support that mapping at the cited locations. The observed function-descriptor entries use 32-bit code/TOC addresses; the common TOC is `r2 = 0xeb798`. Treating these entries as three 64-bit ELFv1 descriptor fields gives misleading values.

For the cited LV2 code, full VA = `0x8000000000000000` + listed low address, and ELF offset = low address + `0x10000`.

## 1. The comparison operand is capacity in bytes

The helper at emer_init VA `0x43384` saves its second argument (`r4`) as the output pointer in `r29`. It calls syscall `0x261` with a temporary information buffer at `SP+0x70`:

```text
VA        Bytes       Instruction
43390     7c9d2378    mr    r29,r4
433a4     39600261    li    r11,0x261
433a8     38810070    addi  r4,r1,0x70
433ac     44000002    sc
433cc     e8010098    ld    r0,0x98(r1)
433d4     812100a0    lwz   r9,0xa0(r1)
433e4     7c0049d2    mulld r0,r0,r9
433e8     f81d0000    std   r0,0(r29)
```

Thus the output is the 64-bit product of the information buffer's 64-bit field at offset `0x28` and unsigned 32-bit field at offset `0x30`. The [LV2 syscall documentation](https://www.psdevwiki.com/ps3/LV2_Functions_and_Syscalls) identifies syscall 609 (`0x261`) as `sys_storage_get_device_info`, and those fields as total sectors and sector size. The rejection path's own log labels the product `[Bytes]`, independently supporting the units.

There is no 32-bit truncation between the multiply, the output store, and the gate's 64-bit load. This is a real capacity test, not a mislabeled sector-count comparison. The instruction produces a low-64-bit product; no broad claim of arithmetic safety for all hypothetical device geometries is needed for 2 TB.

## 2. The original 1536 GiB rejection remains

The function beginning at VA `0x4613c` obtains capacity through that helper. The main device argument is constructed as `0x0101000000000007`; an alternate route first queries `0x0101000000000010` and falls back to the former. The selector calls `sys_ss_get_boot_device`; this does not by itself identify the alternate as a NAND/NOR device. Successful queries converge on this gate:

```text
VA        ELF offset  Bytes       Instruction
46198     36198       38000180    li    r0,0x180
4619c     3619c       e8810078    ld    r4,0x78(r1)
461a0     361a0       780007c6    sldi  r0,r0,32
461a4     361a4       7fa40040    cmpld cr7,r4,r0
461a8     361a8       419d00bc    bgt   cr7,0x46264
```

`0x180 << 32` is **1,649,267,441,664 bytes**, exactly **1536 GiB**, or **3,221,225,472 sectors at 512 bytes**. This unsigned comparison rejects capacities strictly greater than the threshold. Equality follows the accepted path; this gate alone does not prove the equal-capacity device works in every other path.

Accepted path: store byte `1` to the caller's result pointer at `0x461bc`; return zero.

Oversized path at `0x46264`: resolve a diagnostic format string via TOC-relative slot `-0x7b04`, print the measured capacity, store byte `0` to the same result pointer at `0x462c4`; return zero. The zero return here means the query itself completed, while the separate Boolean reports that capacity is unsupported. It is not a normal successful-drive result.

The TOC resolution is:

```text
r2                         = 0xeb798
r2 - 0x7b04                = 0xe3c94
32-bit pointer at 0xe3c94   = 0xc7e68
string at 0xc7e68          = Untolerable capacity HDD detected : cap. %lld[Bytes].!!!!
```

A marketed 2 TB drive with 2,000,398,934,016 bytes exceeds this gate. No firmware execution is needed to establish that the extracted module still contains this refusal condition.

## 3. The rejection reaches the unsupported-hard-disk error page

Two direct callers of the capacity-support helper were found in the decoded code: VA `0x40754` and VA `0x4aef8`. The second yields a fully traced Safe Mode error-message chain:

1. At `0x4aef8`, the caller passes `SP+0x71` as the Boolean output to function `0x4613c`.
2. At `0x4af00–0x4af10`, query return zero plus Boolean zero selects the refusal path.
3. At `0x4af1c–0x4af34`, it obtains the state pointer through TOC slot `-0x7a24` and stores state **4**. That slot resolves to memory VA `0x16e554`.
4. At `0x4c650–0x4c654`, the error-page dispatcher loads the same state. Its case 4 at `0x4c73c` requests localized message index **0x18** through function `0x4a380`.
5. `0x4a380` looks up a language table via TOC slot `-0x7a50` (`0xe06a4`) and message index. Entry 24 at `0xe0704` points to table `0x143608`; its English entry (`+4`) points to `0xd1ad8`.
6. At `0x4c760`, the returned message is retained in `r31`; the path logs `Display ErrorPage : SafeModeErrPage4 !!!!` and rejoins `0x4c6bc`, where it passes that message to the display helper at `0x46e54`.

The embedded English message at VA `0xd1ad8` (ELF offset `0xc1ad8`) reads:

> The installed hard disk is not supported. You must install a hard disk that is compatible with this system.

The binary uses `&#xa;` for the line break. This directly links the capacity refusal to the same wording the user describes. This is stronger evidence than simply finding the text somewhere in the file.

The other caller at `0x40754` also tests the Boolean and records refusal state **8** at `0x40794`, then exits through a failure/sentinel return. Its complete later UI-dispatch chain was not required for, and is not claimed by, this review.

## 4. Additional LV2 findings relevant to the later tier

At full VA `0x800000000028086c` (ELF offset `0x29086c`), the supplied LV2 has the documented instruction `7b9c0020`, `clrldi r28,r28,32`. The nearby code is:

```text
280858 ld     r28,0x10(r29)
280860 lwz    r11,0x80(r31)
280864 ld     r9,0x78(r31)
280868 clrldi r0,r11,32
28086c clrldi r28,r28,32
280870 add    r0,r0,r9
280878 cmpld  cr7,r0,r28
28087c li     r3,-7
280880 bgt    cr7,0x2808f0
```

Observed: a 64-bit value from `r29+0x10` is reduced to 32 bits and used as the upper bound for a 64-bit start-plus-count request. The instruction and bound behavior match the wiki lead. The wiki's identification of this field as region sectors is consistent with the storage-path context but was not independently reconstructed end-to-end here. Removing this clear is therefore a candidate for the >2 TiB audit, not a qualified patch.

**Decimal 2 TB is below 2^32 512-byte sectors.** It does not intrinsically trigger this specific truncation if the field really contains the proposed region's sector count. The region is smaller than the entire device. A claim that this truncation explains a native marketed 2 TB device's initial startup refusal would conflate distinct barriers.

At full VA `0x80000000002cac74` (ELF offset `0x2dac74`), the instruction sequence confirms an unsigned bound of `0x20000` (128 KiB) against a computed value:

```text
2cac58 lwz   r27,0x9c(r31)
2cac64 lwz   r5,0x2c(r31)
2cac68 slwi  r0,r5,2
2cac6c add   r0,r0,r27
2cac70 add   r29,r0,r5
2cac74 lis   r0,2
2cac78 cmplw cr7,r29,r0
2cac7c bgt   cr7,0x2caeec
```

Observed formula: unsigned 32-bit comparison of `field_0x9c + 5 * field_0x2c` to 131,072. The identification as UFS cylinder-group summary sizing and the default-capacity ceiling near 3 TB are external research leads; this review confirms the code and constant, not that geometry estimate or a functioning modified large filesystem.

## Conclusion and limits

**The provided extracted 4.93 module still implements the original 1536 GiB capacity refusal, with a traced path to the unsupported-hard-disk error message.** It is therefore reasonable to plan a narrowly bounded 2 TB patch investigation instead of assuming upgrading from 4.91 removes the problem.

The first milestone needs a complete native-capacity 2 TB boot/format/mount/check/integrity qualification, including high-LBA and recovery paths. That cannot be inferred from this comparison or from removing one instruction. The >2 TiB phase adds separate bounds, overflow and geometry audits. No modified PUP, flash write or physical-drive test was performed by this reviewer.

Reproduce the decisive read-only disassembly:

```powershell
python tools/inspect_elf.py analysis/coreos/emer_init.elf --va 0x43384 --size 0x80
python tools/inspect_elf.py analysis/coreos/emer_init.elf --va 0x4613c --size 0x1a8
python tools/inspect_elf.py analysis/coreos/emer_init.elf --va 0x4aee0 --size 0x58
python tools/inspect_elf.py analysis/coreos/emer_init.elf --va 0x4c634 --size 0x178
python tools/inspect_elf.py analysis/coreos/lv2_kernel.elf --va 0x8000000000280858 --size 0x38
python tools/inspect_elf.py analysis/coreos/lv2_kernel.elf --va 0x80000000002cac58 --size 0x28
```

## Read-only extraction-tool audit

The reviewer also read `tools/analyze_pup.py`, `tools/decrypt_self.py`, `tools/capture_evidence.py`, and their imported PKG decoder. No error was found that undermines the capacity-gate conclusion for these inputs. The local root manifest uses the correct top-level PUP entry identifiers; unrelated helper reports with different labels should not override it.

An independent script that did not import the extraction writers reread the original PUP, decoded its entry table, recomputed its header HMAC and all **9 entry HMACs**, compared all 9 extracted entry bytes and manifest SHA-256 values, and checked the stored sizes and SHA-256 values of all **1110 extracted flash files**. It found no duplicate flash paths. It also independently compared the two decoded ELF pairs byte-for-byte; both matched.

These are integrity/reproducibility checks. The public PUP HMAC key is not proof of Evilnat author identity, and neither that check nor the SELF decoder verifies installation safety. The Python SELF decoder explicitly records `signature_verified: false`; it does not validate all metadata section HMACs or signatures. Its agreement with native scetool on the two relevant complete ELFs is the applicable cross-check here. The parser scripts are research tools for this identified input, not hardened general-purpose hostile-archive validators.

The initial evidence-capture script's handler window from `0x4c650` for `0x140` bytes ends before the message-to-display join at `0x4c7a8`. The disassembly itself is correct, but that short window alone does not reproduce the entire UI chain. The broader command above and the data addresses in section 3 provide the missing trace.
