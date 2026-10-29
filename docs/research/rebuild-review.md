# Rebuild pipeline review for the initial hardware-test candidate

Date: 2026-10-11. This review concerns the supplied Evilnat 4.93 CEX image and an experimental recovery-capacity patch. It establishes file-format, cryptographic-integrity, preservation, and existing CFW verifier evidence. It does not establish a completed installation, successful boot, full-capacity formatting, repair reliability, or stable 2TB support. All experiments below used ordinary files and copies; original firmware files and physical disks were not modified.

## Sources and independent checks

- Existing local fail0verflow-derived ps3tools checkout, commit `fa0f1f58781f2c832851bfb898179fc49ff043b1`: `pkg.c`, `unpkg.c`, `cospkg.c`, `cosunpkg.c`, `puppack.c`, `sceverify.c`, `tools.c`.
- Existing local native scetool 0.3.1 source/build from Sorvigolova/scetool, commit `78ca17e106d30d8354f011b4aaaf800c827833ef`: `frontend.cpp`, `self.cpp`, `sce.cpp`, `keys.cpp`, `ecdsa.cpp`.
- [haxxxen MFW builder](https://github.com/haxxxen/ps3mfw-builder-0.2.1-mod/tree/c3778f1156f6326e18c6bbad0b6154a66c17e817), pinned `c3778f1156f6326e18c6bbad0b6154a66c17e817`. Relevant primary workflow source is [ps3mfw_base.tcl](https://github.com/haxxxen/ps3mfw-builder-0.2.1-mod/blob/c3778f1156f6326e18c6bbad0b6154a66c17e817/ps3mfw_base.tcl), with historical verifier patch definitions in [02_patch_cos.tcl](https://github.com/haxxxen/ps3mfw-builder-0.2.1-mod/blob/c3778f1156f6326e18c6bbad0b6154a66c17e817/tasks/02_patch_cos.tcl).
- Evilnat-authored PKG/SPKG tools source, preserved in the [Gitorious archive](https://archive.midnightchannel.net/SonyPS/PS3/Source%20Code/gitorious.ps3dev.net/PKG-SPKG_Tools/). Downloaded archive SHA256: `4dcc28defdd70940462bb2d2c96d422e7a11fc1202b55719daf655500d7aa4fa`. Its copyright/README attribute modifications to Evilnat and initial tools to fail0verflow; archive hosting itself is not author authentication. Source saved in `analysis/rebuild-review/pkg-spkg-tools-source`.

Independent read-only checker: `analysis/rebuild-review/audit_sce.py`. It decrypts metadata, checks section HMACs, and verifies ECDSA using a separate Python integer implementation. It asserts curve generator/public-point membership and generator order, and outputs no key material. A valid original CoreOS PKG signature supplies a positive cryptographic control. The script is an additional check, not Sony's actual updater or SPU execution.

## Observed original image integrity and signatures

`original-sce-audit.json` records:

| Original component | Section HMACs | ECDSA under corresponding public key | Interpretation |
| --- | --- | --- | --- |
| `emer_init.self` | All four pass | Fails; matching APP revision 0x1C keyset has no private material | Existing custom-firmware format already depends on permissive loader behavior. |
| `lv2_kernel.self` | All three pass | Fails; matching LV2 keyset has no private material | Same distinction between content integrity and valid Sony signature. |
| `CORE_OS_PACKAGE.pkg` | All three pass | Passes under retail PKG public key; archived PKG private material mathematically matches that public key | Proper PKG header signing can be regenerated and independently verified. |
| `CORE_OS_PACKAGE.pkg.spkg_hdr.1` | Header-only object; data hashes belong to the companion PKG | Fails under retail SPKG public key; archived SPKG private material does not match that public key | Do not claim a valid Sony SPKG signature. Preserve the supplied CFW's existing verification behavior. |

The decrypted CoreOS PKG and SPKG headers are byte-identical, SHA256 `6a723c9ecc9533159609a1e5c3ffaf26766eb12461b9b1519ea90a0934f4019a`. Their wrapper encryption keys/IVs differ. The SPKG carries the PKG header signature inside a different encryption wrapper.

The native Evilnat `spkg.exe`, run on a private copy of the original CoreOS PKG, reproduced the original 640-byte SPKG **byte for byte**, SHA256 `bbafcac3917ff30a6e89a7f5d9b56e16574d168907b504768ac28e0527c19db0`. Result: `native-spkg-roundtrip.json`. This Windows binary uses environment variable **PS3_KEYS** for its old-format key directory; scetool uses a different environment/path convention.

## Actual supplied verifier patterns

The original `spu_pkg_rvk_verifier.self` was decoded into the owned review directory. The historical MFW SPKG signature-check replacement sequence `04002a03408000030400018232000100` occurs at ELF offset `0x3150`; the corresponding unpatched pattern is absent. See `spkg-verifier-pattern.json`.

The original LV0 was decoded and its loaders exported on copies, without importing or rebuilding LV0. In the extracted `appldr.elf`, the historical Habib/MFW signature-override replacement `408000023400c080` occurs at offset `0x4ce0`, and its unpatched predecessor is absent. However, the historical general ECDSA-check sequence remains unpatched at offset `0x5740`. See `appldr-verifier-pattern.json`.

These observations corroborate specific existing CFW patches. They do **not** establish that every signature check is disabled or provide a complete SPU control-flow proof. Keeping the current key revision and unchanged loaders avoids introducing a new loader-key compatibility assumption. A new candidate still needs the actual initial installation and boot test.

## SELF rebuilding constraints

Native scetool `--template` copies selected key revision, authentication/vendor identity, APP/FW version, control/capability flags, and ISO seed. It rebuilds layout, crypto keys, HMACs, and control digests; it does not preserve the original encrypted SELF byte layout wholesale.

There is a significant status-reporting limitation: `_sce_sign_header` returns false when no private key exists, but its caller ignores this return and can print “Data encrypted” and write the file anyway. Encryption success must not be described as a verified valid signature.

For this exact `emer_init`, the appropriate native comparison flags are:

```text
-0 SELF -1 TRUE -s TRUE -7 TRUE -t originalSELF -e inputELF outputSELF
```

The original ELF has seven program headers. Three share a zero-sized offset, and the TLS/processor headers also have zero file data. The original SELF contains three PHDR metadata sections plus one SHDR section. Default/template `skip_sections=TRUE` reproduces that four-section pattern. `-s FALSE` would add redundant sections. `-7 TRUE` retains the existing section headers; compression must be requested explicitly with `-1 TRUE`.

An unmodified native template roundtrip produced the original SELF length (546,480 bytes), header length (1,920), section count (four), key count (30), and all segment offsets/compressed sizes. Re-decoding produced the **byte-identical original ELF**, SHA256 `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`. All four HMACs passed; ECDSA remained invalid as expected. See `template-roundtrip.json` and `template-self-audit.json`.

The root's native patched comparison at `analysis/development/p1/emer_init.self` also passed all four HMACs. Its certificate header, SELF extended header, APP identity, ELF header, and all seven program headers matched the original. The only public control-info change was its 20-byte Digest2. Original Digest2 equals SHA1 of the full original ELF; candidate Digest2 equals SHA1 of its full patched ELF. See `native-patched-self-audit.json`, `native-patched-public-header-comparison.json`, and `elf-digest-controls.json`. Native rebuilding changes otherwise unnecessary metadata such as the SHDR metadata index, motivating the narrower alternative below.

### Preferred narrow alternative

A focused template-preserving writer can retain the original file length, offsets, key revision, control/capability structure, crypto tables, invalid signature bytes, and every unchanged ciphertext section. Replace only the compressed code section within its existing slot; update that section's compressed size in both metadata and public segment info, section HMAC, and the independently matched ELF Digest2; re-encrypt metadata with the original metadata keys.

The newly declared compressed length bounds the stream. The unused tail of the old slot is unreferenced padding and must not be reinterpreted as another section. Require exact bounds/overlap checks, a no-change byte-identical roundtrip, independent HMAC verification, native and Python decoding to the exact intended ELF, and byte equality of all unchanged ciphertext sections. This strategy preserves existing CFW signature dependence; it does not generate a valid Sony SELF signature. The candidate implementation and final audit belong to the root builder/reviewer.

## CoreOS PKG, SPKG, tar and PUP requirements

1. Preserve the original CoreOS content's ordered file table, entry names, offsets, sizes, reserved bytes, padding, and total 7,340,000-byte payload. Replace only the allowlisted SELF. Old `cospkg.c` enumerates filesystem order and reallocates offsets; do not use it unmodified for a minimal patch.
2. Regenerate the CoreOS SCE PKG compressed content, declared compressed size, affected section HMACs and retail PKG ECDSA signature. Preserve all other information fields, including the supplied `info1+0x20` value of 1. The archived Evilnat `new_pkg` source describes a modern 0x280-byte header and 20 key-table entries; the bundled native binary differs from that source in an information field, as detailed below. Old `ps3tools/pkg.c` builds a different 0x2C0/24-entry layout. Independently verify the exact output rather than relying on process exit status.
3. Generate the matching 0x280-byte `CORE_OS_PACKAGE.pkg.spkg_hdr.1` by wrapping the **same newly generated plaintext header** under SPKG wrapper encryption. Evilnat `spkg.c` performs this operation directly; its source does not independently resign the SPKG.
4. Replace only those named members in the original `update_files.tar` and `spkg_hdr.tar`, preserving member order, metadata, unrelated member bytes, archive trailers, and padding where possible. Do not regenerate every flash package or alter LV0/loaders.
5. Rebuild all nine PUP entries using the supplied IDs and original order/metadata. `puppack.c` in the original local ps3tools checkout omits modern **0x501 `spkg_hdr.tar` and 0x601 `ps3swu2.self`**. Preserve both; do not use its hardcoded table unmodified. Recalculate changed entry offsets/lengths, corresponding entry HMACs and header HMAC; preserve unrelated entry payloads exactly. PUP HMAC uses publicly available shared material and is integrity evidence, not author authentication.
6. Re-extract the completed PUP independently, compare every nested member, recheck all integrity layers, and confirm the intended single decoded instruction change and untouched source firmware hash.

The original **UPL.xml.pkg needs no modification** for this scope. Independent decryption yields 5,818 bytes, SHA256 `9578987cab327641b9a9174dcd566e092b68590b9ca99ce1397d67f1a39d308e`; its CoreOs record contains only Type and FileName. The entire XML has no package-size or package-hash fields. Keep it unchanged when package filename and firmware identity stay unchanged. Extract saved as `UPL-original.xml`.

### Native PKG source/binary mismatch and correction

The root's no-change control discovered that the bundled Windows `new_pkg.exe` changes the 64-bit `info1+0x20` value from the supplied image's 1 to the compressed content size (`0x543d79` in the original). The archived Evilnat `new_pkg.c` explicitly writes 1 at that offset, while the older fail0verflow `pkg.c` writes the compressed size. The bundled binary therefore does not implement the archived source's behavior exactly. This review did not establish that field's concrete runtime interpretation; changing it cannot be accepted merely because the compressed payload decodes correctly.

The final builder uses the native tool only to supply the compressed content stream, then reconstructs the PKG from the original plaintext header and information sections. It preserves `info1` byte for byte, retains the original crypto tables and layout, updates the declared compressed size and `info0` compressed-size field, recalculates affected HMACs, and generates a new retail PKG ECDSA signature. Its nonce follows RFC6979 with SHA1. The configured PKG private scalar mathematically matches the corresponding public key; the final signature independently verifies under that public key. A no-change template PKG control returns the exact original package bytes. This resolves the specific mismatch without assuming a meaning for the opaque `info1` field.

## Final candidate independent audit

Candidate: `candidates/HDD2TB-P1/PS3/UPDATE/PS3UPDAT.PUP`, 215,764,316 bytes, SHA256 `f7abf409c9f0b6d04b5d9f8f44fb76142363759beb3dd8f060ec1a2dc5400f68`.

The independent extractor `analysis/rebuild-review/audit_candidate.py` does not import the builder or invoke a firmware writer. It reads the completed PUP, checks the original source hash, parses/checksums both raw tar archives, decrypts/checks changed SCE components independently, and invokes native scetool on independently extracted review copies. Full results are saved in `analysis/rebuild-review/candidate-final-audit.json`.

- All nine PUP entry HMACs and the header HMAC pass. Only entries `0x300` and `0x501` differ; version/reserved/header-padding fields, IDs and order are preserved.
- Only the CoreOS PKG and its companion SPKG header differ in the nested archives. All unrelated raw members, tar metadata, order and trailers are identical.
- The candidate PKG's three section HMACs pass, and its new ECDSA signature mathematically verifies under the retail PKG public key. The independently decrypted companion SPKG header exactly matches that PKG header. Its signature remains invalid under the separate SPKG public key, consistent with the supplied image's existing CFW behavior.
- `info1` is byte-identical, with its 64-bit value at offset `0x20` still 1. `info0` changes only in its compressed-size field. Header keys, IVs, layout and all other information fields remain identical.
- All 25 ordered CoreOS file records, offsets, lengths and padding remain identical. Only `emer_init.self` differs; every byte outside that file's original range is identical.
- The modified SELF's four section HMACs pass. Its original invalid signature bytes remain unchanged; all unrelated plaintext header fields, other decoded sections and other section ciphertexts remain identical. The replacement compressed stream fits within its original slot.
- Native decoding of the independently extracted original and candidate SELF yields exactly one changed ELF byte, at `0x3619b`: instruction `38000180` becomes `380001f0`. The candidate ELF SHA256 is `113a234147286b0a5874d035aa668376702c7416fb8b532ff536b7fee50b94ff`. Both full-ELF Digest2 values match the corresponding SHA1.

The reviewed builder's deterministic signer, header updates, bounds checks and no-change controls reveal no unresolved file-format or cryptographic-integrity blocker for this exact candidate. Unchanged components are established by byte identity; this audit does not claim that every unchanged component's inner signature was separately recomputed. These results remain offline evidence, with no console installation or runtime test performed.

## Remaining hardware boundary

The exact candidate above has passed the independent offline complete-package checks described here. The existing CFW verifier modifications are corroborated, with the limitations stated above. The user's disposable-drive installation and initial-boot test remain pending. This is an experimental capacity-gate candidate; successful packaging is not an accepted stability or data-safety result.
