# One-count native consistency test: evidence and boundaries

The fresh AO baseline's primary free-inode total is 244,216,362, equal to
6,602 groups * 36,992 inodes/group minus 4,822 allocated inode bits. The same
three unreachable inode records and 98-fragment set persist unchanged across
AL/AM/AO; their original cause is unresolved. No unknown allocation is treated
as disposable or reclaimed by the PC tool.

The proposed sole plaintext change is a decrement of one in the primary
superblock's fs_cstotal.cs_nifree at +0x400. Its physical ciphertext sector is
LBA162 / byte82944. Host-only preparation fully verifies the held current AO
archive, decrypts that sector with the owner's authorized CECHA00 material,
matches the independent decoded metadata cache, and verifies exact original
and modified codec roundtrips. Only the 64-bit count differs in plaintext.
Root/derived secrets are not serialized, hashed or exported.

Primary upstream comparison:
[FreeBSD releng/6.0 pass5.c](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/6.0/sbin/fsck_ffs/pass5.c)
accumulates reconstructed cylinder-group counters and compares/copies the
summary total. Its [fs.h](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/6.0/sys/ufs/ffs/fs.h)
defines the free-inode field. These support the design, not identical PS3
semantics or a hardware result.

Exact P13 ELF SHA256
e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86:
at0x1e590..0x1e5c0 the derived checker compares64bytes beginning at superblock
+0x3f0 against reconstructed totals; unequal data branches to0x1e690.
The summary warning/answer call is0x14784. On acceptance,0x1e6a8..0x1e6b4
copies64bytes using _sys_memmove, then clears +0xd0/+0xd2 and marks the primary
buffer dirty for a nonnegative writer descriptor. _sys_memcmp and
_sys_memmove were resolved from import NIDs, not inferred solely from call
shape. Actual storage writes happen later and are not proved by this slice.

analysis/dev006/p13-summary-counter-v1/evidence.json preserves exact string
xrefs and listings. p13-summary-repair-model-v1/result.json contains24 bounded
actual-instruction cases: equal and ±1 totals, accepted/refused answer,
two synthetic placements and two nonnegative descriptors. Imported comparison,
copy and answer semantics are explicit host mocks. Whole passes1..5, allocator
behavior, native I/O/flush and answer internals are outside that model.

The prospective keyless physical tool is limited to one write of the exact
reviewed ciphertext sector. It holds source files against write/delete
sharing; validates full source digest/records and all preserved live bytes;
uses exclusive target identity/length/alignment checks, a flushed host journal
and full preserved postcomparison allowing exactly that changed sector.
Its original-only rollback refuses other changes. It is not a generic restore
engine after native metadata activity. The AN exact-tail-sector test already
proved the common transport in one bounded physical case; it does not prove
this filesystem inconsistency or the native checker.

Future acceptance uses current bitmap/group-derived free-inode totals, controls,
metadata comparison and a fresh USB full-worker record. An observed corrected
end state would qualify one end-to-end recovery route. Native mounting/startup
could correct it before manual checking, so no checker-branch causality is
claimed without further instrumentation. Existing orphan changes must be
reported separately. Hardware execution awaits direct owner approval.
