# HW002Q source and bounded capture review

The native sparse write phase and read-only after-boot phase are consumed and passed. `observations/HW002P/after-boot-verification.json` independently audits the three post-boot hash bodies, exact tail records, original-file/control equality, durable intents and the contextual user restart report. It binds55 immutable evidence files. Those results establish persistence within scope; physical placement remains unknown.

## Device and secret custody

The new Q tool reuses the frozen reviewed `PhysicalReader` in `inspect_crucial_metadata.py`. Windows identity must match the freshly reported disk number, exact Crucial size/serial, USB bus, logical512 and non-system/non-boot status. CreateFile requests GENERIC_READ only; opened-handle length and storage descriptor serial/USB checks precede local key access. No source device write APIs are used. The local48-byte root key is read only after the verified open, a derived CECHA00 CBC192 key remains in process memory, and the temporary root bytearray is overwritten. This does not promise secure erasure of every interpreter copy. Neither root nor derived material is displayed, stored, hashed or sent over the network.

Review/native evidence bindings, the exact fixed P contract, verified native after-boot result, actual manual move report and fresh Windows identity are checked before crypto import or output creation. Output must be a new child of observations/HW002Q. Private paths are refused as evidence-hash inputs, including case variants. Importing Q only loads import-safe frozen metadata modules; it performs no device or key access. Local reports/snapshots/own payloads use exclusive creation.

## Mapping and read bounds

The frozen `MetadataCache` accepts only the primary partition, rounds bounded reads to512-byte sectors, rejects changed overlaps/short reads/decode lengths, and caps raw cache traffic at32MiB. The tested sparse mapper skips zero-pointer subtrees, validates reviewed geometry/reserved ranges and bounds indirect blocks. Q accepts only the two fixed P paths and exact native sizes. It additionally requires exactly one hole ending at the fixed write offset and one64-byte final data span. It compares the calculated location against the separate inherited pointer lookup and rejects overlapping payload blocks or any payload-block overlap with captured metadata/directory sectors.

Q reads the label again, then freshly re-reads every captured metadata sector with a separate32MiB limit and at most1MiB per read. Exact bytes must agree, and the saved snapshot must replay both mappings. This is a consistency check, not a whole-filesystem audit. Only after mapping and consistency pass are the two512-byte payload sectors read at their measured addresses. The first64 bytes must equal the fixed native payload. Only those own64 bytes are saved and hashed; sector padding and unrelated payload are discarded. No whole-file read/hash of the approximately202GiB sparse target occurs. The actual high-file address determines `high_physical_payload_match`; the predicted group6500 never does.

The source closes the reader through nested finally blocks even if local stream flush/close fails. Failed captures retain available partial artifacts and an error result when local output remains writable. Local filesystem failure can also prevent the final report; process exit and handle closure therefore remain required operator checks. There is no rollback, raw writer, repair, mount, cleanup, network request or firmware operation.

## Host validation

`analysis/dev006/test_hw002q_capture.py` passed83 checks. Synthetic one-level and triple-indirect files use actual frozen geometry and real directory/inode traversal. Complete captures include saved metadata replay, every-sector consistency re-read, exact two64-byte payload outputs, address reporting and handle closure. A synthetic below-gate placement completes with the high-address flag false. Tests reject overlapping payloads, wrong size, dirty state, changing metadata, bad physical payload, open failure before key access and local fsync failure with reader cleanup. Plan/range tests reject arbitrary targets, changed offsets, short/oversized/misaligned reads and unexpected sparse shapes. Preflight tests cover missing review/move, changed evidence, incomplete native persistence, wrong Windows identity, missing custody, existing/outside output and private hash paths. Temporary dummy48-byte inputs are isolated; no actual secret, raw device or network is used.

Review was performed by the primary agent with the host test evidence; no independent subagent review is claimed. No hardware Q capture has run at review time. Fresh manual graceful shutdown/move and current identity remain required.

## Claim boundary

Actual high-address payload equality would support only these fixed native writes/ordinary-restart/read observations. The two payloads are identical, so alias resistance is not established. Full fill, populated integrity/repair, crash durability, migration, other SSDs and >2TiB remain open; stable support is false. DEV006's partial observer peak is not a complete bound, and HW002L's unexplained allocations remain unresolved. No populated repair or offline injection/reclaim is authorized by this capture. Preserve the1TB source when the user later populates Crucial with real game data.
