# Independent review of the P1 format/refusal result

Date: 2026-10-11. Reported hardware: CECHA00; Crucial BX500 2 TB (previously supplied SKU `CT2000BX500SSD1`). The user reports that P1 installation and the control-drive boot went smoothly, and that the 2 TB drive prompted for formatting but, after acceptance, displayed that the installed hard disk is not supported. The exact delay, presence of a format progress display, and intervening reboot have not yet been supplied. These are user observations, not a console execution trace.

## Current conclusion

**The exact unsupported-disk message still points to the already identified admission check. This independent pass has not identified a second formatter capacity gate that causes that message.** The offer to format does not, by itself, establish that the modified `emer_init` capacity check had already run. Determining the module actually loaded after accepting the prompt is consequently a prerequisite to proposing a new filesystem patch.

The normal `emer_init` error state is at VA `0x14d1b8`. Among the 41 loads of its TOC pointer, the reviewed code has one constant-8 writer: VA `0x40794`, following the return from the capacity helper. The generic state setter and all state classifiers reachable through the reviewed normal-format failure handlers do not introduce another state-8 path.

This is a bounded static conclusion for the pinned ELF. It does not exclude a different executable with the same message, an unexpected executing firmware copy, incorrectly reported device geometry, or memory corruption. None of those alternatives is established as the hardware cause here. A new threshold or filesystem change is not justified solely by the reported screen.

## Inputs and reproducible evidence

- Original `analysis/coreos/emer_init.elf`: SHA-256 `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`.
- Independently decoded P1 `analysis/candidate-review/candidate-readback.python.elf`: SHA-256 `113a234147286b0a5874d035aa668376702c7416fb8b532ff536b7fee50b94ff`.
- The original instruction at ELF file offset `0x36198`, VA `0x46198`, is `38 00 01 80`; the P1 instruction is `38 00 01 f0`.
- `analysis/p2-format-review/capture.py` reads these regular files and writes disassembly and metadata only into its own directory. Run `python analysis/p2-format-review/capture.py`. It uses Capstone PPC64 big endian and the already reviewed code PT_LOAD mapping. `summary.json` records callback descriptors, message-table addresses, raw word references, all 41 state-pointer load addresses, and the gate bytes.

For the addresses in this report, the ELF's first PT_LOAD maps file offset = VA minus `0x10000`. The main TOC is `0xeb798`; TOC offset `-0x7ddc` is slot VA `0xe39bc`, which contains the error-state pointer `0x14d1b8`. A scan of the entire ELF for that big-endian pointer word finds exactly this one slot. Literal-word scans are cross-checks, not proofs against every synthesized address or indirect reference.

## Why this screen identifies state 8

The normal error handler at `0x4117c` loads the state pointer. At `0x41188` it loads the state value, and at `0x4118c` it bounds the jump-table dispatch to states 0 through 8. State 8's jump-table entry at `0x4131c` is relative offset `0x1d4` from table base `0x412fc`, selecting handler `0x414d0`.

The handler loads the language table at VA `0xe0338` through TOC `-0x7ca4` and joins `0x41350` to select the localized string. English entry VA `0xe033c` contains pointer `0xbc768`. A second English entry at `0xe0380` uses the same string. Its decoded contents are:

> The installed hard disk is not supported. You must install a hard disk that is compatible with this system.

`0x411f4`–`0x41208` pass the selected message to display helper `0x46e54`. The other occurrence of this English message, at VA `0xd1ad8`, belongs to the separate Safe Mode message table, already traced in `binary-review.md`.

The normal UI's format and storage errors are different messages:

| Normal error state | English string VA | Meaning of selected message |
| --- | --- | --- |
| 1 | `0xb9e00` | Appropriate system storage was not found |
| 2 | `0xba478` | No applicable update data was found |
| 3 | `0xbb3d8` | Data corrupted |
| 4 | `0xbb5e0` | System storage cannot be accessed |
| 5 | `0xbb9b8` | Error during format operation |
| 6 | `0xbbdd0` | Serious error |
| 7 | `0xbc5a8` | Update data unsupported |
| 8 | `0xbc768` | Installed hard disk unsupported |

The quoted language is embedded firmware evidence, not an internet source. It does not identify which on-console executable emitted the user's screen without runtime readback.

## State-8 setter and capacity units

The normal startup callback beginning at `0x4060c` loads the error-state pointer into `r30` at `0x406cc`. If that state is zero, it calls `0x4613c` at `0x40754` with a one-byte output at stack offset `0x71`. A zero return plus a false output reaches:

```text
VA        bytes       instruction
0x40768  88010071     lbz   r0,0x71(r1)
0x4076c  2f800000     cmpwi cr7,r0,0
0x40770  409e00a8     bne   cr7,0x40818
0x40784  39600008     li    r11,8
0x40794  917e0000     stw   r11,0(r30)
0x40798  90090000     stw   r0,0(r9)       # r0 was set to -1 at 0x40778
```

The gate's helper `0x43384` uses syscall 609 (`sys_storage_get_device_info`). At `0x433cc` it loads the 64-bit sector count from device-info offset `0x28`; at `0x433d4` it loads the 32-bit sector size from offset `0x30`; at `0x433e4` it multiplies with `mulld`; at `0x433e8` it stores a 64-bit byte capacity to the caller's output. Thus the threshold is compared in **bytes**, not gigabytes or sector count.

```text
VA        original / P1 bytes   instruction
0x46198  38000180 / 380001f0   li    r0,0x180 / li r0,0x1f0
0x4619c  e8810078              ld    r4,0x78(r1)
0x461a0  780007c6              sldi  r0,r0,32
0x461a4  7fa40040              cmpld cr7,r4,r0
0x461a8  419d00bc              bgt   cr7,0x46264
```

The ordinary HDD device ID is `0x0101000000000007`. The alternative boot-selector route queries `0x0101000000000010`, falls back to HDD 7 after a query failure, and joins the same comparison. At the over-capacity target `0x46264`, the routine eventually stores false to the one-byte output and returns zero. Its diagnostic identifies capacity in bytes. A device-info query failure instead returns nonzero and bypasses this state-8 assignment in the normal caller.

P1's threshold is `0x1f0 << 32` = **2,130,303,778,816 bytes** (1984 GiB). Decimal 2 TB and the commonly observed 2 TB SATA size 2,000,398,934,016 bytes are both below this threshold. Neither the SKU nor the user's current report establishes the actual device-info fields reported by this console. No sector geometry or byte-capacity observation has been made on the tested Crucial drive.

## Completeness checks on the normal state path

The 41 direct TOC state-pointer loads are saved in `error-state-references.txt` and `summary.json`. Every reference was reviewed for reads, constant state writes, or passage to a classifier. Within the startup/error region, the only three `li ...,8` instructions are:

| VA | Use |
| --- | --- |
| `0x3f228` | Eight-byte length argument; no error-state assignment |
| `0x3fb30` | Callback index 8, stored through the separate pointer TOC `-0x7d80` |
| `0x40784` | Error state 8, stored at `0x40794` after the capacity test |

These two separate uses of the number 8 must not be conflated: callback index 8 selects function `0x3fecc`; it does not select the unsupported-disk message by itself.

Generic setter `0x3e92c` writes its `r3` argument into the normal error state at `0x3e9e8`. Its six direct callers are `0x3b0a0`, `0x3b138`, `0x3b254`, `0x3b2e8`, `0x3bd88`, and `0x407cc`. Every caller explicitly sets `r3=6`. A whole-ELF raw pointer-word search finds no `0x3e92c` function descriptor. This narrows ordinary indirect-entry concerns but is not a whole-program control-flow proof.

The state classifiers at `0x3e518`, `0x3e590`, `0x3e5cc`, `0x3e610`, and `0x3e67c` have been inspected through all of their local branch targets and jump-table cases. They write states 2, 3, 4, 5, or 6, never 8. In particular, `0x3e610` maps a format-related return to state 5 under its flag condition, and `0x3e67c` maps later preparation/setup errors into states 2/3/4/6.

The duplicate unsupported-disk text in Safe Mode was also checked separately. Its error-state pointer is VA `0x16e554`, TOC offset `-0x7a24`. The 37 direct pointer loads are saved in `safe-mode-error-state-references.txt` and `summary.json`. The observed constant-4 assignment is VA `0x4af34`, bytes `90 0b 00 00`, preceded by `li r0,4` at `0x4af20`; it follows the same gate call `0x4613c` at `0x4aef8`, again requiring zero return and false output. Other inspected Safe Mode state writers clear the state or assign 1/2/3. The dynamic writer `0x4a9f8` stores the argument of function `0x4a8d4`; its three direct callers at `0x4b52c`, `0x4c084`, and `0x4cb30` explicitly pass 0, 0, and 1 respectively. No separate Safe Mode format-error path to state 4 was identified. Handler `0x4c650` selects message index `0x18` for state 4 at `0x4c754`; lookup `0x4a380` resolves English VA `0xd1ad8` and dispatches the display helper. This agrees with the normal path's admission-check interpretation while retaining the same static-analysis limits.

## Internal callback order and formatting errors

The callback table at VA `0x142c64` is a 14-entry table of a 32-bit descriptor pointer plus a 32-bit next index. Descriptor layout is a 32-bit code address and 32-bit TOC. Dispatch `0x3fa30` loads the current callback index and invokes its descriptor at `0x3fa90`. Zero-return advances to the table's next index; the sentinel error return `0x0fffffff` routes to callback index 10, or 12 for its special target case. Index 10 is the normal error-display callback `0x4104c`.

| Index | Callback code VA | Ordinary next index |
| --- | --- | --- |
| 0 | `0x4060c` (contains capacity gate call) | 1 |
| 1 | `0x42930` | 2 |
| 2 | `0x4260c` | 3 |
| 3 | `0x42160` | 4 |
| 4 | `0x41dd0` | 7 |
| 5 | `0x42e60` | 6 |
| 6 | `0x40b90` | 7 |
| 7 | `0x40504` | 9 |
| 8 | `0x3fecc` | 9 |
| 9 | `0x3e510` | 13 |
| 10 | `0x4104c` | 13 |
| 11 | `0x41814` | 4 |
| 12 | `0x415e4` | 10 |
| 13 | `0x3e510` | 13 |

For this internal sequence, the admission callback precedes the formatter callbacks. This **does not prove that an earlier prompt shown by VSH before launching `emer_init` was after admission**. The external prompt-to-executable loader sequence requires its own trace.

Concrete normal-format path:

- Callback `0x42160` initial state displays the localized system-partition format warning at `0x42280`. English VA `0xc2e98` asks for START+SELECT held for five seconds. It then handles updater search/preparation and hands off to callback `0x41dd0`.
- Callback `0x41dd0` invokes job descriptor `0xe24a0` through `0x3ff6c` at `0x42060`, with job label `job_format` at VA `0xb86d0`. This descriptor resolves to code `0x41c58` and TOC `0xeb798`.
- Job `0x41c58` sets phase `0x70`, calls `prepare_partitions` at `0x54430` via call `0x41c9c`, saves its result, and ends the job if it fails. The caller diagnoses `emer_init::prepare_partitions() ERROR %d`.
- On success it sets phase `0x80`, calls `setup_updating_environment` at `0x55b64` via `0x41d48`, and saves that result. The caller diagnoses `emer_init::setup_updating_environment() ERROR %d` if needed.
- Callback failure handling at `0x41ecc` selects the phase. Phase `0x70` reaches classifier `0x3e610` via `0x42134`; phase `0x80` reaches `0x3e67c` via `0x41f08`. Both return the sentinel error outcome; neither classifier can assign state 8.
- The preparation function `0x54430` calls HDD partition/storage helpers and formatter wrapper `0x7a918` at `0x546f8`. Inspected error exits return ordinary preparation codes; they do not directly load or write the normal state pointer. Earlier filesystem review already establishes the embedded newfs implementation. No newly found size threshold in these stages can currently be tied to the exact unsupported-disk text.

Full storage-format success and every low-level formatter consumer remain separate audits. This report closes the error-message/state distinction; it does not claim those consumers are safe at 2 TB.

## Requirements before a P2 cause/fix claim

1. Obtain the precise screen sequence and timing: was there a controller-connect screen, a five-second START+SELECT instruction, any formatting percentage, or a reboot between acceptance and refusal? The observed English words should be preserved exactly.
2. Establish the `emer_init` SELF/ELF actually selected by the post-confirm boot path. Installed firmware version, successful installation, and control boot do not read back the active module's patched byte.
3. Establish the tested SSD's actual device-info sector count and sector-size fields, preferably with a read-only console probe plus independent PC ATA identity. Do not infer exposed geometry from capacity printed on the SSD label.
4. If the patched comparison is confirmed executing and the reported byte count is below P1's threshold, instrument the known decision/output/state path before altering filesystem geometry. A diagnostic build is not a storage-support fix, and cannot be called stable.

There is presently **no independently justified minimal P2 formatter patch** from this pass. The next concrete discriminator is execution provenance at the existing admission check, alongside the exact capacity returned to it. No firmware writer, flash operation, physical-drive write, console command, or new hardware test was performed by this reviewer.

## Independent installed-ROS inspector review

Reviewed `tools/inspect_installed_ros.py` SHA-256 `0c5629cecd773e79d5f976be0634478c728373d09a999eb9cc9385fff3aaeea2` read-only. No blocking defect was found for its declared input: the canonical 268435456-byte NAND dump produced by Evilnat's Dump Flash. Local PS3DumpChecker `config.xml` explicitly uses content offsets `0xc0030` and `0x7c0020`, prefixes `000000000000000000000000006fffe0` at the preceding 16 bytes, and the two accepted top-level selection-header forms at `0xc0000`. Its `Patcher.cs` confirms the content offsets, and the local Evilnat `dumpFlash()` implementation confirms the canonical NAND file size/layout method. Physical NAND/ECC and NOR inputs are intentionally rejected by this inspector.

The inspector opens the resolved regular input only in `rb` mode, requires a fresh output directory, and refuses an output directory containing the input. Its table parser bounds count, declared size, entries against the table and content size, duplicate names, and overlapping nonempty entries. Only the two SHA-256-pinned project SELF inputs are automatically decoded. An unknown SELF is identified as unknown and extracted for separate analysis. Known decoded ELF hashes and the gate instruction are checked before marking decoding verified. The report explicitly distinguishes a later selection header from proof of historical execution.

An independent in-memory parser test used the actual original CoreOS and the actual decoded P1 SELF in the retained table. Fifteen cases passed: baseline/P1 identification; zero/oversize counts; wrong content size; table/out-of-region/oversize entries; duplicate/unterminated/padded names; overlapping entries; unknown SELF identity; and Windows device/extended namespace rejection. Results are in `analysis/p2-format-review/ros-inspector-review.json`. These tests neither create nor inspect a real console dump, and do not replace the root's complete synthetic canonical-dump workflow validation or the pending hardware readback.
