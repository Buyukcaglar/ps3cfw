# DEV006 after the populated baseline

13 October 2026. Primary-agent exact-binary investigation; no separate reviewer claimed. HW002R's baseline and post-ordinary-restart comparisons passed for16 complete files/1,444,498 bytes, exact P8 checker utility and the migrated webMAN control. This closes that bounded sample/persistence observation, not populated repair or whole integrity.

## New static evidence

`analysis/dev006/allocator-wide-measurement-v1/evidence.json` pins11 fresh disassembly captures from the original retail checker and liblv2, including option dispatch and public heap wrappers. `_sys_heap_malloc` is at740c, free7380, memalign7610, create76d4, delete784c and mallinfo7204. The utility imports malloc/free/create/delete but not memalign or mallinfo. This import inventory is not proof that the selected heap cannot reach other interfaces indirectly.

Malloc at7450 acquires the native heap lock through71a0, calls the allocator at8c84, retains its result, and releases through71d4 at746c. Free acquires at73b8, mutates through8364, then tail-calls71d4. The mallinfo wrapper acquires the same lock, calls its internal walker7c44, and releases it. A future observer must not call the public mallinfo entry while already holding the native heap lock. A wrapper-level observation after the native operation returns has a different locking situation and still needs coverage/concurrency proof.

The complete walker capture shows output offset1c receives heap-field1ac minus the computed current free total; offset20 receives that free total. Offset14 is copied from heap-field1b0. These are current statistics; none is established as a remembered peak. Calling this snapshot at arbitrary times would provide observations rather than a full high-water proof. Repeated full chunk walks also need an explicit performance bound before use on a331,755-node populated filesystem.

`analysis/dev006/heap-address-forms-v1/evidence.json` extends the earlier aligned-pointer scan:2,581 explicit TOC memory accesses were inventoried up to the last import stub. The same five accesses address heap-pointer slot26a08; the raw32/64-bit search, including unaligned byte positions, finds only the known32-bit pointer at26a08 and the same relocation to global4ba44. Five other explicit r2 forms are a context save/restore pair atc660/c784 and three function-descriptor TOC loads at17504/1ce30/1d098, each preserved in its own context capture. No direct TOC arithmetic was identified in this inventory. Cross-register/indexed aliases, mutable data, callback arguments and external code remain unresolved; flag512 must remain set.

The option switch table at18324 maps `n` to18d70. That handler increments the no-answer flag through TOC displacement-78fc and clears the yes-answer flag at-78f8. `y` swaps the two pointer loads and shares the increment/clear tail. This establishes recognition and flag setup, not that `-n` prevents every raw write, mount-side effect or dirty-state update. No checker invocation using this option is released.

## Implementation gates for another diagnostic

1. Close selected-heap handle/alias escape and all allocator-interface paths, including callback/import behavior and default creation. Keep partial-accounting flags until that proof exists.
2. Design the independent allocator-wide measurement, including synchronization, allocator administration/fragmentation, failures, bulk teardown and a bounded observer cost. A current-free snapshot, sampled maximum, or the existing charged-chunk table alone cannot be renamed a guaranteed peak.
3. Capture repair-context parent-container headroom and validate failure paths. XMB allocation success is a distinct observation; the128MiB caller buffer is not yet a guaranteed populated-checker budget.
4. Audit write behavior and select a verified restorable fixture before any populated checker execution. Recognized `-n` is insufficient authorization for invoking an assumed read-only scan on the migrated library.
5. Only then implement a separately reviewed candidate with ABI/locking/model checks, exact patch allowlist, reproducible rebuild and package/installed-byte gates. No P9 candidate has been created by these audits.

Normal migrated-game launch/save/load/trophy observations are a separate hardware branch and may proceed without repair, artificial dirty flags or another firmware update. Keep the1TB source and retained image/hash cache/archive. Do not repeat the consumed HW002R reads or historical writers. Stable support remains false.
