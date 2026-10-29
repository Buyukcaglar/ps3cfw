# P2 capacity diagnostic: build and independent validation plan

Date: 2026-10-11. This is a review plan, not approval of an unbuilt P2 image. Only regular project files were inspected; no firmware writer, builder, flash writer or physical-disk command was run for this review.

## Evidence and intended scope

HW001B's saved NAND report identifies ROS1's `emer_init.self` exactly as P1, independently decodes `38 00 01 f0` at the capacity threshold, and declares ROS1 selected. ROS0 remains unidentified. The report explicitly does not prove which executable ran during the earlier failed boot. The PC/SAT capture establishes the Crucial's reported 2,000,398,934,016-byte, 512/512-byte-sector geometry on that PC path; a PS3 runtime capacity observation is still needed.

P2 should preserve P1's 1984 GiB admission behavior and add a recognizable candidate marker plus the capacity actually used by the rejection path. It should make no formatter, layout, filesystem, checker-budget, LV1, LV2, device-info-provider, encryption or limit change. A successful diagnostic is evidence about the executing image and value, not stable 2 TB support.

The inspected build and audit tools are:

| File | SHA-256 |
|---|---|
| `tools/build_hdd2tb_p1.py` | fe4cde05884e5dcf8f9b399ee85c7835801d17c3cd390d187e749fbb20d75499 |
| `analysis/rebuild-review/audit_candidate.py` | e2245e90fc19890146dbcde33c7b992f39237f6a91053b2b9a2066722714d88b |
| `analysis/rebuild-review/audit_sce.py` | ce31f4fde8753e3104ff18e36b68bfe526a6dd45c54d8423e8a6f8f4a51006e8 |
| `analysis/candidate-review/independent_candidate_scope.py` | fe0ce92c5b6ee2f5c49aaaa8a675d1f0bf540d9d28740ca49918cc22087f8f0e |

## Builder reuse

A separate builder derived from P1 is reasonable. Keep the P1 builder, P1 PUP, manifest, hardware record and review outputs unchanged. Use distinct P2 work/candidate directories and reject accidental output paths inside P1. Pin the supplied source PUP (`ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a`) and P1 reference PUP (`f7abf409c9f0b6d04b5d9f8f44fb76142363759beb3dd8f060ec1a2dc5400f68`). Hash them before and after the build/review.

Derive P2 from the immutable supplied image plus an explicit desired-ELF patch set. Preserve P1's threshold byte and specify every further P2 range using module, ELF offset, VA mapping, exact old bytes, exact new bytes and purpose. Enforce equal lengths, nonoverlapping ranges, exact baseline-byte matches, and complete equality between the final target ELF and application of that patch set. A broad allowed region or a hash supplied only by the builder is insufficient. Compare against both the supplied ELF and P1 so the inherited threshold edit remains distinct from new diagnostics.

Retain P1's no-change controls for PUP, tar, native compression, focused SELF replacement and template PKG reconstruction. Retain pinned native tools, enabled assertions, all original table/layout assumptions and independent final decode checks. Replace P1-specific names, offsets, single-byte assertions and claim fields deliberately; do not leave a manifest describing P2 as a one-byte threshold experiment.

### Compressed-section constraint

The existing `focused_self` only rebuilds section 0, retaining all other SELF section ciphertexts. The original section begins at SELF offset 1920 (`0x780`); section 1 begins at 367424 (`0x59b40`). The available section-0 slot is therefore 365504 bytes. P1's section-0 stream is 365499 bytes: only **five bytes** of headroom remain. The supplied stream is 365498 bytes.

Same ELF length does not guarantee that a diagnostic fits after compression. Keep the slot bound as a hard failure. Do not move section offsets, extend the SELF or overwrite the following section to make a candidate fit. If a new encoding/placement is needed, review it explicitly and repeat no-change and final-PUP validation. The first PT_LOAD covers ELF offsets `0..0xce038` and VA `0x10000..0xde038`; the known normal and Safe Mode English strings are within it. A patch to a language-table/TOC pointer in the second PT_LOAD, rather than to those strings, would exceed the current section-0-only build treatment and requires separate support.

The final decoded **full** ELF must equal the desired ELF. Matching only the decompressed first section would miss unsupported edits elsewhere or a reconstruction error.

## Diagnostic semantics review

The existing oversized path at VA `0x46264` formats the capacity from stack `+0x78` into a 0x400-byte local buffer and logs it. The value was used by the unsigned 64-bit comparison at `0x461a4`. The P1 threshold remains `li r0,0x1f0; sldi r0,r0,32`. A diagnostic should reuse the same measured 64-bit value rather than make a second storage query whose result could differ.

Before accepting exact P2 patch bytes, independently disassemble the affected basic blocks and inspect the replacement data:

1. Preserve the capacity query inputs, fallback order and return handling, threshold construction, unsigned comparison, accepted/refused result stores, caller state assignments and return values. Instrumentation may add calls or redirects, but their convergence and register effects must leave these outcomes intact.
2. Check live-register preservation, CR/LR/CTR and TOC use, stack alignment/frame bounds, complete displaced instructions and branch targets. Check descriptor versus direct-code entry conventions for any call. An existing logger and a screen helper cannot be assumed to share an ABI.
3. Verify the formatter's real argument widths and format grammar. Existing `%lld` reports a signed representation; values with bit 63 set require an explicit representation rule. A marker and hexadecimal or unsigned byte value are useful only if supported by the selected formatter. Avoid narrowing the value to 32 bits or converting it to an unexplained GB/GiB value.
4. Prove buffer ownership, writable mapping, output length and NUL termination. The gate's local buffer ceases to be valid after return; storing its pointer for a later error screen is unsafe. A persistent buffer must remain valid through both normal and Safe Mode display, and fit the full message. Do not infer runtime writability from a convenient string address.
5. Preserve readable failure context and record which localized path is changed. English-only instrumentation requires an English screen for the experiment. A missing marker on another language or path cannot establish that P2 failed to execute.
6. Prove that the numeric value is the current runtime value, rather than a static example or PC-derived number. Place the candidate marker so its presence identifies P2 execution. Define what absence means: wrong language/path or a pre-instrumentation failure can also suppress it.

A marker shown only on refusal cannot prove P2 execution when the drive is accepted. If an entry marker is added to address that ambiguity, it must receive its own exact allowlist and control-flow review.

## Fresh, independent final-PUP audit

Use a new review directory and a dedicated P2 auditor. Do not rerun or overwrite the P1 review directory. Reuse the read-only parsing/cryptographic logic after inspection, without importing or executing either builder. Pin the final P2 PUP hash and the reviewed allowlist independently; the builder manifest is evidence to cross-check, not the authority for what may change.

The reusable audit must freshly read and extract the **final candidate PUP**, rather than trusting builder intermediates:

- Validate PUP bounds, ordered IDs, reserved metadata and all entry/header HMACs. Only payload entries `0x300` and `0x501` may change. Permit only their mathematically required header lengths/offsets/HMACs; preserve all version and unrelated header bytes.
- Independently parse each tar, verify checksums, member order and zero trailers, preserve every unrelated raw member/header/padding byte, and allow only `CORE_OS_PACKAGE.pkg` and its matching `.spkg_hdr.1` to differ. Replacement member header changes are limited to required size/checksum fields.
- Decrypt candidate PKG and verify all section HMACs, decompression boundaries, absence of overlaps and PKG ECDSA mathematically. Preserve original info1 (including its `+0x20` value of 1), metadata key/IV tables and layout; allow only affected lengths, digests, payload and signature. Verify the SPKG's decrypted header matches the PKG's header.
- Preserve the entire 25-entry CoreOS table, offsets, lengths, padding and all files except `emer_init.self`; compare the entire content outside that file, not only named-file hashes.
- Verify the modified SELF's section HMACs, slot bound, retained section layout/keys/IVs, and ciphertext/plaintext identity of every untouched section. Constrain changed plaintext-header bytes to the required section length, HMAC and digest2 fields. Preserve the baseline signature bytes and explicitly report that the SELF ECDSA remains invalid under its original public key and relies on the existing CFW override. The SPKG's invalid signature status is likewise inherited treatment, not authentic Sony signing.
- Decode the freshly extracted candidate SELF with both the Python decoder and pinned native scetool, require identical full ELFs, and compare exact byte changes to the independently reviewed P2 allowlist. Verify digest2 against the complete decoded ELF. Preserve ELF/program headers and all bytes outside the allowlist.
- Independently compare against P1 to confirm its threshold is retained and only the diagnostic bytes are new. Hash source, P1 reference, final P2 and scripts again after the audit.

The current P1 auditors contain hardcoded candidate hashes, paths, single changed-byte checks and P1 claim strings. Their scope is a good template; they are not ready-made generic P2 approval scripts. The second scope auditor also assumes all outer entry offsets and sizes are unchanged. If P2 compression changes PKG/PUP lengths, evaluate the actual required offset/size differences, rather than dropping those checks wholesale. No signature key material should enter reports.

## Qualification and interpretation gates

Gate A: exact patch/ABI/control-flow review complete, build controls pass, fresh independent extraction/crypto/preservation audit passes, artifacts hashed and the experiment instructions name the exact P2 hash. This establishes a software-verified diagnostic candidate only.

Gate B: user installs that exact candidate using the working control drive; a normal boot establishes basic control compatibility. Preserve the original data drive and existing NAND dump separately. Firmware installation still writes console flash, and testing with the disposable target retains P1's existing possibility of entering formatting; adding diagnostics does not make that workflow read-only.

Gate C: the user repeats the known Crucial startup sequence and captures complete screens, marker, exact numeric value, delay and any reboot/progress transition. Do not repeat a format step against the original drive. Stop and preserve results on an unexpected error, inconsistent marker/value or changed control behavior.

The refusal value must be compared with both 2,000,398,934,016 bytes observed on the PC and 2,130,303,778,816 bytes used by P1's gate. A different value narrows the geometry/provider investigation; a different executable marker narrows the loading/copy investigation. A P2 marker with a below-threshold value on the traced oversized path contradicts the expected static comparison and requires checking capture freshness, exact hook placement and state preservation before proposing a fix. Missing output remains an unresolved diagnostic, not permission to enlarge limits or modify filesystems blindly.

Neither the diagnostic display, control boot nor another format attempt qualifies full-capacity media access, fsck repair, populated-volume recovery, interruption durability or stable 2 TB support. Those remain later stages in the storage validation plan.
