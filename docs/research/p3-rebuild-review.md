# P3 final package and preservation audit

11 October 2026. Candidate `candidates/HDD2TB-P3/PS3/UPDATE/PS3UPDAT.PUP`, SHA256 `9197335b04b6cdf8c40393d6375dd6ee77d2f62fc85da5cac0989d012ed00eaa`, **215,764,316 bytes**. Static software approval applies to the HW001F admission experiment only.

The primary agent performed the rebuild and review; no independent person/agent is claimed. The finished PUP was freshly parsed by `analysis/p3-review/audit_p3.py`, which imports the separately implemented read-only `audit_candidate` and `audit_sce` readers and no builder. Exact change expectations are encoded in the auditor rather than loaded from the build manifest. Native scetool and separately implemented Python SELF decoding agree on original and final complete ELFs.

## Verified final-byte scope

- All nine PUP entry/header HMACs pass. IDs, order, reserved/version fields and all header bytes outside allowed payload-position/length/HMAC fields are preserved. Only entries `0x300` and `0x501` change; both updater executables and top-level version/flags material are byte-identical.
- Only `CORE_OS_PACKAGE.pkg`, `dev_flash_005.tar.aa.2026_01_08_191610` and their corresponding two SPKG companions change. Outer tar member order, metadata outside required size/checksum fields, untouched raw member extents and zero trailers are identical.
- All 25 CoreOS file positions, lengths and bytes outside emer_init are identical. The emergency SELF equals P1 and decodes to SHA256 `113a234147286b0a5874d035aa668376702c7416fb8b532ff536b7fee50b94ff`; only original ELF byte `0x3619b` changes.
- The flash package's entire uncompressed tar is identical outside the same-length `dev_flash/vsh/module/sysconf_plugin.sprx` extent, including tar headers, directory entries and padding. The sysconf ELF SHA256 is `48edc374dc3a113582445ec5964c562a934c5258b6a8b040d25126317aa25af9`; only offsets `0x4e37f` and `0x4e38e` differ. All other PRX segments, relocations and ciphertexts are identical.
- Both modified SELFs retain layout, authentication/key-revision fields, metadata keys/IVs, signature bytes and all unaffected plaintext-header fields. Changed header fields are limited to compressed size, affected section HMAC and full-ELF Digest2. All section HMACs pass. Compressed streams fit the original slots; metadata-to-payload alignment gaps are unchanged.
- Both PKGs have valid section HMACs and independently verified retail PKG ECDSA signatures. Original info1 (including `+0x20 == 1`), section layout and key/IV tables are preserved. Only compressed lengths, affected HMACs and signature change as required. Candidate SPKG plaintext headers match their companion PKGs exactly.

## Resolved source-header distinction

The first audit assertion assumed the source flash PKG/SPKG plaintext headers would match in full, as the source CoreOS pair does. It failed on the supplied flash pair. `source_header_investigation.py` confirms differences confined to metadata-header AES key/IV and ECDSA signature; section metadata and payload data keys match. Both original flash PKG and original flash SPKG signatures independently verify under their respective public keys. They were separately wrapped/signed, not mismatched payload headers. The auditor now normalizes only these specific original fields and still requires full equality of the **candidate** PKG/SPKG headers. No candidate bytes changed to accommodate this source-format distinction.

## Explicit signature dependence and limits

Original sysconf SELF has a valid APP signature; the changed sysconf SELF retains its original signature bytes, which no longer verify. The original flash SPKG has a valid SPKG signature; regenerated flash SPKG does not verify under the SPKG public key. These are **new invalid-signature instances**, not identical original signature validity. CoreOS emergency SELF/SPKG already had invalid signatures in the supplied CFW and P1.

P3 depends on the existing Evilnat CFW APP-loader and SPKG-verifier overrides. The original verifier binaries and exact patched sequences are documented in `research/rebuild-review.md`, `analysis/rebuild-review/appldr-verifier-pattern.json` and `spkg-verifier-pattern.json`. The APP/SPKG mechanism is shared, but pattern evidence is not a full SPU control-flow proof. No valid Sony SELF/SPKG signature or universal disabled verification is claimed. Initial installation and working-HDD XMB boot must qualify this dependency on the user's console before any Crucial format test. No new loader/key/protection patch is introduced.

Machine evidence: `analysis/p3-review/final-audit.json`, per-package crypto reports and `source-header-investigation.json`; native/Python decoded copies are confined to that review directory. Unchanged packages inherit complete byte identity; all their inner signatures were not recomputed. File checks do not establish installation, native format, address correctness, repair or durability. Separate-parser checks are independent of builder implementation, not independent human review.
