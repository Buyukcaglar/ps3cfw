# P9 checker allocation safety review

13 October 2026. P9 is an experimental allocation-failure correction on the exact P8 parent. The user closed further LBP3 testing; HW002T's unperformed manual exercise is withdrawn and its baseline retained. No additional game exercise is part of this release.

PUP SHA-256 `d5cb8678dedd18d6b232549c187df8ea154f804fd9c6edffa1e39da9d3640730`,215,765,852bytes. Utility SELF SHA-256 `cf7852f4f5c1a5ae333c64ffaee3d8d52252a4b156a85add5672b1afee65250c`,78,343bytes. Decoded ELF SHA-256 `1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2`.

## Concrete defects and correction

The original helper at0xe7a4 allocates the requested new size, then copies that entire new size from the old pointer and frees the old pointer without checking the replacement allocation. Its sole observed direct caller grows a pointer array at0x16888. The real preceding instructions compare the used count with capacity and reach growth when equal, add100entries, multiply by4bytes and publish the enlarged capacity before allocation. The following code stores the returned pointer even when null, then reaches the existing error/status8 path.

P9 redirects this exact growth call to a252-byte combined helper region, with two additional patch sites for conditional pointer publication and calloc multiplication checking. The growth helper uses the caller's old count as the previous array length; it reads no heap headers. On success it allocates the requested larger buffer, copies only old_count*4bytes, frees the old buffer once, and returns the replacement for the original caller to publish. On allocation failure it rolls capacity back, returns null and leaves the old pointer/content intact. Conditional publication preserves the old pointer on that null return, and the original nonzero error path remains. Counts that would overflow the100-entry growth, inconsistent requested byte counts, or a missing old pointer with nonzero capacity fail through the same route.

The calloc guard evaluates the product of the two original32-bit arguments in64bits. A product exceeding UINT32_MAX returns null before allocation/zeroing. Nonoverflowing and zero-sized calls retain the original wrapper's behavior. Arithmetic already performed before those arguments and other allocation callers are outside this correction.

The generic original resize helper remains unchanged. Unknown indirect callers, complete checker allocation-failure safety and all malformed-filesystem behavior are unqualified. These are exact local fixes, rather than a new general allocator implementation.

## Verification

The actual helper, immediate caller and calloc instruction model passes266cases, including allocation failure, exact old-content preservation, first allocation, growth, metadata rollback, invalid/overflowing counts, multiplication boundaries/random pairs, register upper bits, nonvolatile GPR/CR2..4/TOC/stack preservation, volatile callee clobbers and restricted writes. Original-helper models independently reproduce a null copy destination after allocation failure and an out-of-range source read during successful growth. Allocator/import callees are mocked; this is not PowerPC hardware execution or full checker execution.

Static delta review independently permits only three original hook words at0x16888,0x16894,0xe728 and252bytes in previously zero owned code space0x26400..0x264fc. Program headers, file length, relocation records, data, imports, exports, existing P8 helper/core bytes and incomplete-coverage flags are identical. No new syscall, indirect call, raw heap-header read or module-memory growth is introduced. New direct callees are the existing utility allocator/free wrappers and memcpy import.

The first unreleased assembler draft encoded the64-bit mask field incorrectly. Disassembly caught it before packaging; that draft is retained and excluded. The first host-model attempt treated the new internal branch as an external mock and stopped; its source is retained. The final model includes internal instruction execution and destination/source bounds. Neither failed draft ran on the console or produced release firmware.

Two complete firmware builds match byte-for-byte, including the SELF and manifests. The separate package audit validates PUP HMACs, PKG HMAC/ECDSA, matching SPKG header, SELF section HMAC/digest2 and native/Python whole-ELF agreement. Full relocated P8/P9 comparisons at four segment-base pairs preserve every loaded byte except the declared three hooks and252helper bytes. Whole CoreOS, sysconf, version entries, all other flash packages, other tar members/headers/padding/trailer remain unchanged. SELF signature bytes are inherited under the existing CFW verifier policy; no Sony authenticity or SPKG signature claim is made.

Review provenance is the primary agent with separate parser/crypto/delta and instruction-model implementations. No independent human or subagent review is claimed. Prior P8 core58000-event evidence is inherited unchanged and was not rerun as a new P9 test.

## Hardware and remaining scope

A fresh read-only pre-update baseline, HW002U, passes16 complete sampled files/1,444,498bytes against the retained migration source and verifies the current P8 utility and migrated webMAN control. This sample excludes LBP3 profile/game paths. It establishes that bounded baseline; whole-drive integrity remains unproven.

The next hardware gate is Recovery6 installation on the currently fitted Crucial, XMB capacity/ordinary shutdown/restart and exact P9 utility/sample readback. No game exercise, manual Restore File System, database rebuild, format, artificial dirty flag, induced allocation failure or live memory/syscall probe is requested. The existing P8 observer/log identity remains inherited; old P8 logs cannot establish P9 execution. Identification is through the complete installed utility hash.

The earlier gates for another peak-measurement diagnostic and populated repair remain. This candidate's local failure corrections keep the128MiB checker budget, original storage layout and existing partial-accounting flags unchanged. Allocator-wide peak/bound, complete alias coverage, repair-context headroom, all write-side effects and a verified restorable fixture remain prerequisites for populated/near-full repair qualification. Stable support, full-capacity/alias resistance, durability, other drives and>2TiB support remain unqualified.
