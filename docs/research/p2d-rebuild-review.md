# Independent rebuild and cryptographic review: HDD2TB-P2D

Date: 2026-10-11. **The final P2D PUP passes this independent file-format, cryptographic-integrity and exact-byte preservation audit.** This establishes the software artifact described below; it does not establish runtime display correctness, successful installation or stable larger-drive support. The separate diagnostic ABI/UI review and hardware experiment remain separate gates.

This reviewer inspected only regular project files and invoked native scetool in decode mode. No builder, firmware/flash writer or physical-disk command was run by this reviewer. P1's builder and PUP remain unchanged.

## Exact artifact and purpose

| Artifact | Value |
|---|---|
| Final PUP | `candidates/HDD2TB-P2D/PS3/UPDATE/PS3UPDAT.PUP` |
| PUP size | 215,764,316 bytes |
| PUP SHA-256 | `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71` |
| Freshly decoded full ELF SHA-256 | `9163b5485e2f94e39e321b37ca4b8c39e4eb9368a51e9a1d31aa2dccf4e88f43` |
| Decoded ELF size | 1,266,432 bytes |
| New builder SHA-256 inspected | `01ffd605d7d667bd5956dd94608d87e43cec0abfe1138d5c58eea524713e7a48` |

P2D deliberately retains the supplied stock admission instruction `38 00 01 80` (`0x180 << 32` = 1,649,267,441,664 bytes / 1536 GiB). It does **not** retain P1's 1984 GiB threshold. This purpose supersedes the earlier preliminary P2 plan's retain-P1-threshold requirement. Native 2 TB capacity is expected to take the original refusal branch and show an executing-image tag plus the PS3 runtime capacity; the diagnostic is not a larger-drive fix.

The intended text is `HDD2TB-P2D`, `CAP=%llu B`, and `GATE=1649267441664`, separated by the existing UI's `&#xa;` markup. The runtime value must still be observed on the console; this review does not substitute the PC capacity into that field.

## Independent method and exact change scope

The auditor is a separate adaptation of the P1 read-only auditor, under `analysis/p2d-crypto-review/`. It imports neither builder. Its local `audit_sce.py` is an unchanged copy of the inspected SCE verifier. The audit freshly reads the final candidate PUP, parses/decrypts its contents, and independently decodes the extracted SELF with both the Python decoder and pinned native scetool. Both full decoded ELFs are byte-identical.

The reviewer-owned `reviewed-patches.json` specifies exact original and replacement bytes; it is not loaded from the builder's manifest. Applying those six ranges to the independently decoded supplied ELF yields exactly the full candidate ELF. There are 75 actually changed ELF bytes and no others:

| ELF offset / VA | Before | After | Scope |
|---|---|---|---|
| `0x36268` / `0x46268` | `3b610080` | `83628338` | Existing oversize formatting destination selects the existing persistent error buffer |
| `0x314d0` / `0x414d0` | `812282d4` | `83a28338` | Normal unsupported handler selects the diagnostic buffer |
| `0x314d4` / `0x414d4` | `8162835c` | `60000000` | Normal handler bypasses the localization-index load |
| `0x314dc` / `0x414dc` | `4bfffe74` | `4bfffd18` | Normal handler joins the existing display path |
| `0x3c758` / `0x4c758` | `4bffdc29` | `80628338` | Safe Mode unsupported handler selects the diagnostic buffer |
| `0xb7e68` / `0xc7e68` | Original 59-byte oversized-HDD log format | 49-byte diagnostic format, zero-padded to 59 bytes | Candidate tag, unsigned byte-capacity format and explicit baseline gate label |

Every range is within the original first PT_LOAD. The ELF/program headers and complete remaining ELF are unchanged. In particular, the gate's capacity provider, threshold, unsigned comparison and accepted/refused return sequences remain stock. No formatter, filesystem, checker workspace, LV1, LV2 or other CoreOS executable change is hidden in the package.

## Completed integrity and preservation checks

- PUP: all nine ordered IDs and reserved metadata preserved; bounds and contiguous entry layout valid; all entry HMACs and header HMAC valid. Only `0x300` and `0x501` payloads differ. All other header bytes are preserved after accounting for required lengths/offsets and computed HMACs.
- Tar archives: independent parser and raw header checksums pass. Only `CORE_OS_PACKAGE.pkg` and `CORE_OS_PACKAGE.pkg.spkg_hdr.1` differ in their respective archives. Every unrelated raw member, header and padding record is identical; archive trailers are identical. Replacement-header differences are confined to required size/checksum fields.
- CoreOS PKG: all three section HMACs pass; the original PKG is a positive ECDSA verification control and the candidate PKG also verifies mathematically under the configured retail PKG public key. Decompression consumes exactly the declared stream, with no section overlap. Original info1, including `+0x20 == 1`, is preserved. Only the affected compressed length, info0 length, section digests, payload and PKG signature change; layout/key/IV tables remain intact.
- SPKG: its decrypted header matches the corresponding PKG header for source and candidate. The source and candidate SPKG signatures both fail under the configured SPKG public key, as disclosed below; no valid Sony SPKG signature is claimed.
- CoreOS contents: all 25 entries retain original order, offsets and lengths. Only `emer_init.self` differs. The complete content outside its original byte span, including unnamed gaps and padding, is identical.
- SELF: all four section HMACs pass. Original header layout, metadata keys/IVs and complete untouched section records/plaintexts/ciphertexts are preserved. Plaintext-header changes are confined to required section/compressed lengths, section HMAC and the complete-ELF digest2. Original signature bytes are retained and the source/candidate SELF signatures both fail under the configured APP public key. The digest2 matches the full independently decoded candidate ELF.
- Compression slot: native compression would produce 365,520 bytes in a 365,504-byte slot, exceeding it by 16. The selected Python zlib-ng 1.3.1 DEFLATE stream is 362,854 bytes, leaving 2,650 bytes. It remains entirely inside the original slot; the unused slot ciphertext and every following SELF byte are unchanged. Native scetool's fresh successful full decode cross-checks interoperability of this selected stream.
- P1 reference: the pinned P1 PUP was freshly read and its SELF independently decoded with both decoders. Its sole ELF change from stock remains offset `0x3619b`, `80 -> f0`. P2D instead has the stock `80` at that byte. P1's PUP SHA-256 remains `f7abf409c9f0b6d04b5d9f8f44fb76142363759beb3dd8f060ec1a2dc5400f68`; its builder remains `fe4cde05884e5dcf8f9b399ee85c7835801d17c3cd390d187e749fbb20d75499`.

The new builder was inspected without executing it. It imports pinned P1 helper functions, uses distinct P2D paths, and asserts the no-change PUP/tar/native-compression/focused-SELF/template-PKG controls plus full native/Python target-ELF agreement. The fresh independent audit above establishes the final artifact's contents directly; it does not claim an independent repeat build or bit-for-bit reproducibility of the compressor across other runtimes.

## Signature and hardware limits

The baseline's invalid SELF/SPKG signature treatment remains explicit. P2D depends on the existing custom-firmware verification overrides; valid section HMACs and a mathematically valid PKG signature do not turn it into authentic Sony firmware. Unchanged packages inherit byte identity; their entire inner signature trees were not all recomputed in this audit. No key material is included in these reports.

Exact-byte scope and fresh decoding establish the intended binary changes, but do not prove that the persistent buffer survives every normal/Safe Mode transition, that `%llu` renders as intended, or that the final screen is reached. Those require the separate instruction/dataflow review and console test. P2D retains stock acceptance below the original gate; if the console reports the Crucial at or below that gate, formatting could remain reachable. The hardware protocol must stop at an unexpected formatting warning and preserve the original data drive separately.

This candidate is suitable to advance past the rebuild/crypto gate, conditional on the separate diagnostic-code review. It is not qualified for populated storage, high-LBA media access, fsck recovery, interrupted writes, data-loss guarantees or stable 2 TB use.

## Reproduction and retained audit evidence

Run without Python optimization from the project root:

```text
python analysis/p2d-crypto-review/audit_p2d.py --candidate-sha256 4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71 --allowlist-sha256 e380ba38b679761e1c2cf23b087bde067d979f8f2797b8128a7a303620140cf4
```

| Evidence | SHA-256 |
|---|---|
| `analysis/p2d-crypto-review/audit_p2d.py` | `f46a0d856c880b780ca508cbb03b54ff629b1a98e8c8a9ee2312443a2dd2d7c6` |
| `analysis/p2d-crypto-review/audit_sce.py` | `ce31f4fde8753e3104ff18e36b68bfe526a6dd45c54d8423e8a6f8f4a51006e8` |
| `analysis/p2d-crypto-review/reviewed-patches.json` | `e380ba38b679761e1c2cf23b087bde067d979f8f2797b8128a7a303620140cf4` |
| `analysis/p2d-crypto-review/candidate-final-audit.json` | `d2b3659effca18c927887d546d028f32b9b3ea897f4f5a0c86e636d19ec46bc4` |

Source, pinned P1, final P2D, patch allowlist and P1-builder hashes were rechecked after extraction/decoding. The machine report retains the complete changed-byte lists, per-CoreOS-file hashes, section integrity and signature results. Extracted SELF/ELF review copies and native decoder logs are kept only in the new review directory.
