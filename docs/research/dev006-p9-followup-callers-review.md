# P9 follow-up allocation caller review

13 October 2026. This is an offline review of the exact installed P9 ELF, SHA-256
`1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2`.
HW002U's complete installed SELF readback and 16-file comparison passed separately.
No checker, memory probe, repair or additional game test ran for this review.

The direct linked-call inventory in `analysis/dev006/p9-allocation-callers-v1`
contains 24 calls to the enumerated allocation/create/growth interfaces. Its
short linear scan marked 18 local zero comparisons and six unresolved cases.
Those classifications are clues rather than control-flow or cleanup proofs.
The deeper exact captures in `analysis/dev006/p9-priority-callers-v2` resolve
the six cases as follows.

| Allocation site | Deeper local finding | Remaining limit |
| --- | --- | --- |
| `0xe7c8` | The original generic resize at `0xe7a4` still copies the new size into an unchecked replacement. P9 removed its sole previously observed direct caller; the current inventory finds zero direct calls to this helper. | Indirect/described entry reachability is unproved. The generic helper is not globally fixed or certified unreachable. |
| `0x14550` | The first result is saved in r31 while a second allocation runs at `0x14564`. Comparisons at `0x1456c`/`0x14574`, with branches through `0x14514` and `0x14584`, precede publishing/dereferencing the new node and data. Early failed attempts invoke the original error route; later failed attempts can return fewer allocated buffers. | Partial-pair allocation leaks/cleanup, the caller's minimum-buffer assumptions and error-context validity are not proved. |
| `0x1e844` | The first 8192-byte allocation is saved in a structure. After the second allocation, it is reloaded and checked at `0x1e860`, then the second result at `0x1e874`. Either null reaches the original error call at `0x1e8d0`. | Complete cleanup after either partial failure and resumed-context handling remain open. |
| `0x1f6a0` | The bitmap result is stored/reloaded through a structure; `0x1f6b4` checks it and `0x1f6b8` branches to `0x1ffa4` on null. The diagnostic then reaches common cleanup/return through `0x1fb68`. | Common cleanup has disk-related calls and is not established side-effect-free or fully failure-safe. |
| `0x1f840` | After both pointer-table allocations, `0x1f868` checks the reloaded first result and `0x1f874` the second. Either null reaches `0x1fb50`, diagnostic/common cleanup, and the return value assembled as `0x80010004`. | Pre-call arithmetic and complete partial-allocation cleanup are not qualified by these null checks. |
| `0x25e44` | This inherited P8 observer preserves the native result. The pointer-validation routine tests null at `0x253f8` and returns null without reading a preceding chunk header. The wrapper checks that return at `0x25e70`; its accounting routine has a separate null-result path through `0x25610`. | Wrapper accounting remains partial; alias coverage, concurrency and an allocator-wide bound are not proved. |

The original error routine at `0xef90` reports, then calls `0xee98`, which invokes
the context-restore routine at `0xc778`. The latter reloads stack/TOC/registers
and the saved return address. Thus the instruction after the error call is not
an ordinary local continuation when that context is valid. This observation
does not prove the validity of every saved context or all later cleanup.

This pass does not identify another active immediate null-dereference in the
five delayed-check cases. It does not prove all 24 callers safe, that every
allocator interface was enumerated, or that the original generic resize can
never be reached indirectly. No new candidate is justified solely by this
inventory. P9 remains unchanged.

The next useful hardware preparation is a disposable native 2 TB fixture on
the empty PNY, with the migrated Crucial kept intact. Establish drive identity,
native format/boot and a verified restoration route before recovery/failure
experiments. Independent allocator coverage/peak/headroom and write-side-effect
work remain DEV006 gates. Stable support remains unqualified.
