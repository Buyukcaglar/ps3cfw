# P9 setup failure branches and cleanup entry

13 October 2026. Exact installed P9 ELF SHA256
`1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2`.
This is primary-agent source/binary/model review, without another human or agent
review. No checker, memory probe or fault injection was executed for this audit.

Fresh captures preserve the complete cleanup function14e80..15344, setup
prologue, five setup allocation checks, failure exits, heap lifecycle and the
worker's setup-result dispatch. The first larger worker capture crossed an
embedded switch table; the strict decoder rejected it. Its partial captures
and failure record remain in p9-setup-cleanup-v2. v3 captures valid bounded
code intervals. Its raw-word alias listing used the original retail TOC and
must not be interpreted as P9 loaded aliases; the relocated model supersedes
that listing.

P8 expanded text and rebased the data segment by0x3000. P9 retains this layout.
The actual P9 TOC descriptor target is data offset0x9560, virtual0x317c0;
508 type1 relocation records target that offset. The first model attempt used
the retail TOC and failed a memory-bound assertion before emitting a result.
The retained first-attempt source records that failure. The corrected model
applies type1 pointer relocations at three independent text/data placements.
Setup's write-FD slot at displacement-7430 and cleanup's-7b38 resolve to the
same P9 global4f620; read-FD slots-7418/-7ab4 resolve to5f740.

The corrected actual-instruction model passes36 setup cases and6 cleanup-entry
cases. It uses the saved PNY geometry:106496-byte cylinder summary,
60981796-byte even fragment bitmap and52816-byte group table. The two directory
tables use max(directory_count,128): the paired requests are552/512bytes for
the minimum case and596/556bytes for the139-directory fixture. Each of the
five setup allocations is failed independently, plus the successful check
path, with volatile-register/condition clobbers. The last pair is allocated
before either result is checked. Null results reach one cleanup(0) call and,
**assuming that mocked cleanup returns**, the error80010004 and original saved
registers/stack/LR. Successful summary reads, buffer setup at14450, native
allocator behavior, later phases and actual cleanup callees are excluded.

The descriptor opens for writing on an ordinary setup lane before these large
allocations. A failed setup is consequently not established as disk-write-free.
For the ordinary cleanup entry, a negative write descriptor skips to read-FD
close10d28; a nonnegative write descriptor reaches flush1558c. The six entry
cases stop before those callees. Flush internals, buffer-list validity, partial
allocation leaks, longjmp/context validity, special mounted-device control
105dc, all error exits and data-preserving OOM behavior remain open. No global
safe-cleanup conclusion or new patch follows from these checks.

Evidence: analysis/dev006/p9-setup-cleanup-v1,v2,v3 and
analysis/dev006/p9-setup-failure-model-v2/result.json. The two independent
preserved PNY HDD controls and a fresh whole installed SELF readback are a
separate HW002X baseline. The next bounded test uses the disposable native PNY
and existing P9, without induced allocation failure or corruption. It cannot
qualify populated Crucial repair or an allocator-wide peak/bound.
