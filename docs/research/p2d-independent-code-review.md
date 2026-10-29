# HDD2TB-P2D independent final code and scope review

## Result and evidence boundary

**PASS for the bounded static code/scope review; no blocking branch, register, stack or return-path issue identified.** This is a diagnostic candidate, not a 2 TB support release or a hardware safety qualification. Crypto/signature verification and buffer lifetime have separate reviewers. This review does not claim that every asynchronous path preserves the message, that the UI renders it correctly on the console, or that installation/runtime testing has occurred.

The reviewed final PUP is `candidates/HDD2TB-P2D/PS3/UPDATE/PS3UPDAT.PUP`, SHA-256 `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71`. The immutable supplied source PUP is SHA-256 `ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a`. Both hashes were checked before and after this audit. No firmware writer, physical-drive access, or change to either PUP was performed.

The independent script `analysis/p2d-scope-review/review_scope.py` imports readers/decoders, not either firmware builder. It freshly extracts the final and source PUPs, decrypts their CoreOS packages and SELF files, applies its own literal six-range expectation, and writes `analysis/p2d-scope-review/report.json`. The final native scetool and Python SELF decodes are byte-identical. The final decoded ELF SHA-256 is `9163b5485e2f94e39e321b37ca4b8c39e4eb9368a51e9a1d31aa2dccf4e88f43`; the supplied source decoded ELF is `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`.

## Exact change scope

All 25 CoreOS entries retain their original table/order/offsets/lengths. Only `emer_init.self` differs. The entire decrypted CoreOS content outside its original SELF span is byte-identical. Both decoded ELFs are 1,266,432 bytes; there are exactly 75 differing bytes, all within these six independently specified ranges:

| ELF file offset | Runtime VA | Change |
|---|---|---|
| `0x36268` | `0x46268` | Oversize message destination: `addi r27,r1,0x80` becomes `lwz r27,-0x7cc8(r2)` |
| `0x314d0` | `0x414d0` | Normal unsupported-drive state: load persistent message pointer into `r29` |
| `0x314d4` | `0x414d4` | Remove language table load with `nop` |
| `0x314dc` | `0x414dc` | Non-link branch now targets the existing display join at `0x411f4` |
| `0x3c758` | `0x4c758` | Safe Mode unsupported-drive state: replace language lookup call with `lwz r3,-0x7cc8(r2)` |
| `0xb7e68` (59 bytes) | `0xc7e68` | Replace and NUL-pad the existing oversize format string with `HDD2TB-P2D&#xa;CAP=%llu B&#xa;GATE=1649267441664` |

In particular, the stock `li r0,0x180; ld r4,0x78(r1); sldi r0,r0,32; cmpld r4,r0; bgt` at `0x46198..0x461a8` is unchanged. Its unsigned threshold is `0x180 << 32 = 1,649,267,441,664` bytes, or 1536 GiB. P1's `0x1f0` gate is deliberately absent. No formatter, partition-creation, repair, LV1 or LV2 code differs. This statement is an exact byte-scope result, not a guarantee about all actions performed by unchanged firmware.

## Control flow and ABI

### Oversize helper

The helper at `0x4613c` still distinguishes query status from its output Boolean. The successful-query oversize branch reaches `0x46264`; it still returns status zero and stores false to the caller's output byte at `0x462c4`. The admission, refusal and nonzero-query-error epilogues are unchanged. The output false is still consumed by the normal caller to set state 8 and by the Safe Mode caller to set state 4. A successful query at or below the stock gate still returns the original true output.

The changed instruction at `0x46268` loads the existing TOC slot `0xe3ad0` (`r2=0xeb798`, displacement `-0x7cc8`), whose unchanged 32-bit pointer is `0x14d610`. The range used by the existing `snprintf` size of 1024 lies inside a writable PT_LOAD memory span. `r27` and `r28` are already saved/restored nonvolatile registers. The existing `clrldi r28,r27,32` supplies the pointer form expected by the formatter. The original stack allocation remains unchanged.

After the existing log call, `ld r6,0x78(r1)` reloads the full 64-bit capacity for `snprintf`: `r3=destination`, `r4=1024`, `r5=format`, `r6=capacity`. The existing `strlen` and TTY syscall consume the resulting buffer. No extra syscall or storage call was inserted.

### Normal error display

The replacement instruction at `0x414d0` loads the BSS message pointer into already-saved `r29`. The unchanged instruction at `0x414d8` loads the required context-pointer slot into `r10`. The instruction `4bfffd18` at `0x414dc` is a non-link branch to `0x411f4`, not a call; it does not introduce an LR dependency.

At the destination, the existing code supplies `r3=message`, `r4=*context`, and zeroes `r5/r6/r7` before calling display helper `0x46e54`. That helper captures these arguments and does not require the skipped language-lookup temporaries `r9/r11` or an incoming `r8`. Its later use of `r8` follows its own initialization. The state/callback writes, common return path and saved-register restores remain unchanged.

### Safe Mode error display

The replacement `lwz r3,-0x7cc8(r2)` at `0x4c758` feeds the existing `mr r31,r3` at `0x4c760`. The pointer therefore survives the unchanged intervening logging calls in already-saved nonvolatile `r31`. The display join at `0x4c6bc` supplies it to the same display helper with its original context and zero arguments.

The skipped language helper at `0x4a380` is a bounded string lookup using loads/arithmetic and volatile condition/register state; no required state write or resource operation was identified. Replacing its `bl` with a load does not unbalance a frame. Subsequent calls set LR normally and the handler restores its original saved caller LR/registers on return. Its common state writes and return value remain unchanged.

## Unsigned capacity and formatting checks

The host model covers zero, one, gate-minus-one, gate, gate-plus-one, the measured Crucial byte count, P1's threshold, `2^63-1`, `2^63`, and `2^64-1`. The unchanged unsigned comparison admits the first four and rejects the remaining cases. This assumes the underlying capacity query succeeds. It is an arithmetic model, not emulation of PS3 syscalls or hardware.

The newly used `%llu` is also supported by the unchanged embedded libc's static path: double `l` is mapped to internal modifier `q` at `0x27078/0x271ac`; conversion `u` routes to `0x274e4`, which selects the 64-bit variadic `ld` at `0x28284`; decimal conversion selects base 10 and uses `divdu` at `0x309a0`, bypassing the signed `d/i` handling. The quotient after the first unsigned division by 10 fits in signed 64 bits, consistent with the subsequent signed division loop. This supports the formatting choice statically, without claiming actual PS3 formatter execution.

The maximum unsigned 64-bit number has 20 decimal digits. The full raw diagnostic string with that value takes 65 bytes including NUL, below the existing 1024-byte `snprintf` bound. The literal XML entities are counted in that bound. Whether they render as line breaks remains a console/UI observation.

## Hardware interpretation and stopping boundary

If the PS3 reports the measured Crucial capacity of `2,000,398,934,016` bytes, the unchanged stock gate must take the oversize branch and the expected displayed digits are `CAP=2000398934016 B`. That is a conditional prediction. A marker plus those digits establishes execution of this rejection formatter with that capacity; it does **not** explain the earlier P1 failure or establish full-capacity support, repair correctness or durability.

If the capacity provider reports a value at or below the stock gate, the unchanged admission path may proceed toward formatting. Thus P2D is not an unconditional write inhibitor. The reviewed `candidates/HDD2TB-P2D/HW001C.md` correctly stops before the START+SELECT warning or any further format/update confirmation in that outcome, and bounds acceptance of an initial simple format offer to the empty Crucial only. The original data drive remains the control and requires a stop on any unexpected initialization offer.

The persistent buffer's full cross-transition lifetime is intentionally left to its separate review. This report does not rule out abnormal state injection, synthesized references, asynchronous overwrites, or console-specific runtime behavior. Installation and hardware observation remain the next evidence gate.

## Reproduction and artifacts

Run `python analysis/p2d-scope-review/review_scope.py` from the workspace. The saved report contains exact patch bytes, all differing ELF byte offsets, both source/final hashes, the capacity boundary cases and scope limits. Freshly extracted SELF/ELF files, native decoder output and bounded disassembly for the callers, handlers, argument setup and libc paths are kept in that same analysis directory. The final extraction was repeated after the parent's deterministic rebuild and matched the same pinned PUP hash.
