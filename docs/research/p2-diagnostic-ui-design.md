# Independent final UI review: bounded HDD2TB-P2D capacity screen

Date: 2026-10-11. Input: original `analysis/coreos/emer_init.elf`, SHA-256 `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`. **Final static UI review: PASS, with the runtime limits stated below.** This review covers the delivered P2D implementation and fresh final-PUP readback. It does not establish installation, execution, observed capacity, successful formatting, stability, or absence of writes on hardware.

## Final artifact readback

The final candidate `candidates/HDD2TB-P2D/PS3/UPDATE/PS3UPDAT.PUP`, SHA-256 **`4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71`**, was read afresh after construction. `analysis/p2-diagnostic-ui-review/review_final.py` independently reads its PUP table and update tar, reuses the previously reviewed package/SELF decryption helpers, and compares the complete resulting ELF against an independently specified patch set. It does not import or execute the P2D builder.

The extracted SELF SHA-256 is `dcd3820c12f5ab04983e404a99c9ad8102fa51f42218a631a2c9ea2de890c118`. Its decoded 1,266,432-byte ELF SHA-256 is **`9163b5485e2f94e39e321b37ca4b8c39e4eb9368a51e9a1d31aa2dccf4e88f43`**. The entire ELF exactly matches the five instruction replacements and one 59-byte format span specified below: **75 bytes actually differ from the original**, all within those six spans. It also equals both saved full builder decoder outputs. The stock gate's load/compare/branch and the rejection output/return sequences are byte-identical to the original. The second PT_LOAD and both original English unsupported literals are unchanged. The final artifact contains **no static localized-text tags**. Machine-readable result: [final-ui-review.json](../analysis/p2-diagnostic-ui-review/final-ui-review.json).

Reviewed `tools/build_hdd2tb_p2d.py` SHA-256: `01ffd605d7d667bd5956dd94608d87e43cec0abfe1138d5c58eea524713e7a48`. It checks the pinned original, exact old words and format, fixed ELF length, explicit modified-span allowlist, stock gate bytes, and retained false-output/return bytes before packaging. It preserves the original first-section slot, checks both full SELF decoders against the target, and never changes language pointers. No material UI-buffer, PPC register/branch ABI, or unsigned-format blocker was identified in the final artifact. Signature validity and full package scope are separate reviews; this UI review makes no independent cryptographic-signature claim.

The material remaining limitation is runtime evidence: P2D has no separate disk-write-inhibition mechanism, no hardware-proven screen, and no native 2 TB support or storage-stability result. Its expected stopping behavior depends on the actual device-info product exceeding the preserved stock threshold. Stop hardware testing if the expected tag is replaced by a later five-second format warning or a format-progress display.

## Delivered behavior and purpose

The delivered temporary **P2D diagnostic uses the original `0x180 << 32` admission threshold**, the existing byte-capacity computation and rejection return, and a persistent stock error-text buffer. On the existing over-capacity branch, it formats the actual 64-bit value that the admission comparison consumed and shows it through the ordinary normal/Safe Mode error handlers. LV2, partitioning, formatter logic, device queries, comparison, return values, and state assignments remain unchanged.

The original threshold is **1,649,267,441,664 bytes = 1536 GiB**. P1 used **2,130,303,778,816 bytes = 1984 GiB**. P2D is therefore an observation probe using the stock acceptance baseline, not a larger-drive support fix. Starting from the original ELF requires no instruction change at the threshold. Starting from P1 requires `0x46198: 380001f0 -> 38000180` (ELF offset `0x36198`, sole changed threshold byte `f0 -> 80` at `0x3619b`).

A correctly reported decimal 2 TB drive exceeds the stock gate and should take the diagnostic rejection path before `emer_init`'s reviewed formatter callbacks. This is conditional: if the PS3 reports a capacity at or below the stock gate, the unchanged logic can pass it. A hardware procedure must not describe this candidate as an unconditional formatting block or a guarantee of zero writes.

## Delivered first-load-only patch set

All instruction replacements and the diagnostic format reside in the first PT_LOAD. For these VAs, ELF offset is VA minus `0x10000`. None of these changes requires patching the second PT_LOAD, the language-pointer tables, the ELF layout, or BSS size.

| VA | ELF offset | Original bytes | Delivered bytes | Meaning |
| --- | --- | --- | --- | --- |
| `0x46268` | `0x36268` | `3b610080` | `83628338` | `addi r27,r1,0x80` -> `lwz r27,-0x7cc8(r2)`; existing rejection formatter now writes the persistent stock error buffer |
| `0x414d0` | `0x314d0` | `812282d4` | `83a28338` | Load normal message pointer into `r29` from the same BSS pointer |
| `0x414d4` | `0x314d4` | `8162835c` | `60000000` | Remove the now-unused normal language-table load |
| `0x414dc` | `0x314dc` | `4bfffe74` | `4bfffd18` | Branch directly to display join `0x411f4` instead of localized selection `0x41350` |
| `0x4c758` | `0x3c758` | `4bffdc29` | `80628338` | Replace Safe Mode message lookup with `lwz r3,-0x7cc8(r2)` |

Leave normal instruction `0x414d8 = 81428334` unchanged: it loads the display-parameter pointer into `r10`. Leave Safe Mode `0x4c754 = 38600018` unchanged; its value is simply overwritten by the following replacement. Leaving that harmless instruction avoids another modified word.

The original 59-byte NUL-terminated format at VA `0xc7e68`, ELF offset `0xb7e68`, is replaced with this 49-byte NUL-terminated ASCII format and **10 zero padding bytes**:

```text
HDD2TB-P2D&#xa;CAP=%llu B&#xa;GATE=1649267441664
```

The markup `&#xa;` is the firmware's existing line separator. Expected presentation for a conventionally reported 2 TB SATA drive is:

```text
HDD2TB-P2D
CAP=2000398934016 B
GATE=1649267441664
```

This displayed number is an example, not an observation of the user's Crucial SSD. The exact value on the console must be photographed or transcribed.

The existing format is `Untolerable capacity HDD detected : cap. %lld[Bytes].!!!!` followed by a newline and NUL. Although additional zero alignment bytes follow it, there is no need to consume those bytes. Preserve the original 59-byte span and its neighbors exactly.

## Why the buffer is suitable

`r2 = 0xeb798`. Its existing TOC slot at VA `0xe3ad0` (displacement `-0x7cc8`) contains pointer `0x14d610`. This is the normal error builder's existing **1024-byte mutable buffer**. The next referenced object begins at `0x14da10`, exactly `0x400` bytes later.

The second PT_LOAD is writable, begins at VA `0xe0000`, has file size `0x64c70` and memory size `0x99360`. The buffer therefore lies in its valid BSS, outside its file-backed data. Its lifetime is the module's lifetime, surviving the return from `0x4613c`. No new allocation, extension, stack escape, or write into an RX string is required.

The original normal error cases 3/5/6 already load this pointer at `0x413ac`, `0x41418`, or `0x41444`, clear the first byte, and assemble a message with a `0x400` bound. The pointer is reloaded for display at `0x413f4`. An aligned first-load instruction scan finds exactly these four original direct TOC loads. A whole-ELF raw pointer-word scan finds the BSS address only at its TOC slot. These are useful alias cross-checks, not a proof against every synthesized address or memory corruption.

The neighboring `0x14da10` object is separately used by normal error handling at `0x41150` as a **16-byte** destination for a numeric error-code string. That operation starts at the byte after the reused 1024-byte buffer and does not clear it. Existing state-3/5/6 buffer construction is not taken by normal state 8's dispatch.

In Safe Mode's state-4 handler, `0x4c744` passes zero to `0x43184`. That function is only `lwz r9,-0x7c10(r2); stw r3,0(r9); blr`; it does not clear the diagnostic buffer. The handler's later `snprintf` and logging use its separate stack destination `r28 = r1+0x70`. They do not use the BSS diagnostic destination. No clear or overwrite of the BSS destination was identified between the reviewed over-capacity formatter and either display join. As with the earlier admission-path review, this is a bounded static observation rather than a complete alias or concurrency proof.

## Existing calling conventions and preserved behavior

At rejection entry `0x46264`, the byte capacity remains in `r4` for the existing printf-like call `0x266b4` at `0x46274`. The existing diagnostic format is loaded into `r29` and passed as `r3`. Retaining **one and only one** integer conversion preserves that call's variadic argument contract.

At the bounded formatter `0x267b4` call at `0x4628c`, arguments remain:

| Register | Value |
| --- | --- |
| `r3` | Destination, now `0x14d610` through existing `r28` |
| `r4` | Bound `0x400` |
| `r5` | Format at `0xc7e68` |
| `r6` | 64-bit capacity reloaded from gate stack offset `0x78` |

`0x4626c` already zero-extends the destination into `r28`. The bounded formatter terminates the output, and the short candidate text is far below the 1024-byte limit, including a 20-digit maximum unsigned 64-bit capacity. Existing logging then reads the same buffer. The helper's false output store, zero return, stack restoration, and the calling state setters are retained.

Normal state 8's direct replacement sets `r29`, while the unchanged `0x414d8` supplies `r10`. Join `0x411f4` copies `r29 -> r3`, loads `r4 = *r10`, zeros `r5/r6/r7`, and calls the original display helper `0x46e54`. `r29` is already saved by the error-handler prologue. Removed `r9/r11` values were only the language-selection temporaries; they are not needed by that join.

Safe Mode's replacement supplies `r3` in the same register as the removed lookup's return. Existing `0x4c760` copies it to preserved register `r31`. Intermediate logging uses the separate stack message buffer. At `0x4c6bc`, `r31` becomes display argument `r3`; the unchanged code loads the display parameter and calls `0x46e54`. No new calls, frames, save slots, or callee-saved register obligations are introduced.

These two handler changes display the diagnostic ASCII text for **all language selections**, because they bypass language lookup. For this bounded diagnostic build that is intentional and must be disclosed.

## Unsigned formatting is supported by this binary

There are no literal `%llu` strings in the original ELF. Literal presence must not be claimed. It contains 16 `%lld` and 40 `%llx` occurrences; both logging wrappers share the same underlying formatter at `0x26b48`.

The parser itself establishes `%llu` support:

1. At `0x27078` it handles `l`; `0x27084` tests whether the next character is also `l`. This reaches `0x271ac` and `0x271b4`, which stores internal modifier `q` (`0x71`).
2. Conversion dispatch uses the signed-offset table at `0x27298`. The entry for ASCII `u` selects `0x274e4`, the unsigned integer path; `d` selects the distinct signed path `0x27810`.
3. At `0x2751c`, modifier `q` selects `0x28274`. `0x28284` uses a 64-bit `ld` from the next variadic argument slot, then joins `0x27540` to store the full value.
4. Numeric writer `0x3092c` selects base 10 for `u`, without the signed `d/i` negation route. Its first digit operation at `0x309a0` is `divdu`. Dividing an unsigned 64-bit value by 10 makes the remaining quotient fit in signed 64 bits, allowing the subsequent signed-division continuation to produce all remaining digits safely.

Thus `%llu` reports even a malformed high-bit capacity as unsigned decimal rather than a negative number. This is static control-flow evidence, not an execution test of the printf implementation. `%s` is also present in the original strings and has its own dispatch target `0x27700`, but this diagnostic does not need another conversion or another variadic argument.

## Original localized messages remain unchanged

The normal and Safe Mode original English unsupported-disk strings at VAs `0xbc768` and `0xd1ad8` are unchanged in the final artifact. No static-message tagging or conditional empty-buffer fallback was implemented. The delivered direct handlers bypass those localized strings and display the persistent diagnostic buffer.

An untagged unsupported message is an unexpected result for the reviewed P2D rejection/display path. It remains consistent with a different executable copy or a different message source, among other possibilities; it does not identify the executing ROS bank by itself. Investigate that result before changing another acceptance threshold.

## What a hardware result can establish

- A dynamic `HDD2TB-P2D`, `CAP=...`, `GATE=...` screen establishes that this patched module's over-capacity formatting and one of the patched display routes executed. It provides the exact product of sector count and sector size consumed by this gate.
- A capacity above P1's 2,130,303,778,816-byte threshold supplies a concrete explanation for P1 admission rejection, but does not identify which raw geometry field is wrong or why.
- A conventional approximately 2 TB capacity between the stock and P1 thresholds proves P2D's deliberate stock-gate rejection. It does not by itself explain the earlier P1 screen or prove which bank was executing then.
- A blank or untagged message is an unexpected diagnostic outcome requiring execution/copy/path investigation before another acceptance patch.
- A format progress screen or the internal START+SELECT-for-five-seconds warning instead of the tag means the expected rejection was not observed. The user should stop there and report the exact screen. No successful formatting or filesystem-support claim follows.

Before testing, use the control drive to install and verify the intended candidate by checksum; use only the disposable SSD for the drive-swap probe; keep the preserved working drive aside. Permit the already observed initial format question only as required to reach the same startup path. Do not instruct the user to advance through a later five-second format warning or progress screen for this diagnostic. Record candidate identity, SSD SKU, language, the full screen, and whether any reboot or progress display occurred. Updating firmware itself and earlier exterior startup behavior remain outside this narrow in-module no-formatter-path inference.

Raw sector count, sector size, and selected device ID are deliberately omitted from this minimal probe. The existing gate's formatter receives only the computed capacity. Capturing the other fields would require changing the helper's output contract or adding reviewed storage/instructions. Reading the helper's expired stack is not a valid substitute.

## Reproducible evidence

Run `python analysis/p2-diagnostic-ui-review/capture.py`. It asserts the original ELF hash, reads the original in read-only mode, verifies every original instruction, independently disassembles the proposed four-byte replacements in memory, and writes only its owned review directory. `design-evidence.json` records PT_LOAD bounds, original/proposed bytes, format lengths, pointer references, conversion-table targets, and original English strings. The accompanying gate, normal UI, Safe Mode UI, and format-parser captures support the control-flow statements above. The script does not write a patched ELF, SELF, PUP, or physical disk.

Run `python analysis/p2-diagnostic-ui-review/review_final.py` for the delivered-PUP readback. Its [PASS evidence](../analysis/p2-diagnostic-ui-review/final-ui-review.json) pins final PUP SHA-256 `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71`, ELF SHA-256 `9163b5485e2f94e39e321b37ca4b8c39e4eb9368a51e9a1d31aa2dccf4e88f43`, and all 75 changed byte offsets. It confirms exact six-span scope and the unmodified stock gate, rejection return, and English literals.

## HW001C protocol scope review

The saved [HW001C protocol](../candidates/HDD2TB-P2D/HW001C.md) was read in full after final construction. It names the same PUP checksum and byte length, reserves the known working drive as the installation/control drive, limits the initial format acceptance to the empty Crucial, and explicitly states that initialization may be authorized by that acceptance. It asks for the dynamic tag and actual digits; it does not promise that the PC's expected number is a PS3 measurement. It stops further actions at a later START+SELECT warning and directs the user not to interrupt an unexpectedly started progress operation by cutting power. It also states that capacities at or below the stock threshold can pass. No material mismatch with the delivered diagnostic's scope was identified. Hardware observation and native 2 TB support remain pending.
