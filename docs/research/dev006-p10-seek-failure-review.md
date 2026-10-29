# P10: stop block writes after failed positioning

13 October2026. This primary-agent review uses separate byte/relocation,
instruction-model and package/crypto/parser implementations. No independent
human or subagent review is claimed. P10 is an experimental local failure-path
correction to exact P9, not a new complete checker or general stability claim.

HW002AA's Lexar clean checker passed by contextual user report and a fresh
independently parsed272-byte diagnostic: utility0/fullworker1/128MiB/
largestrequest62446924/zeroobservedfailures/consistent unsaturated partial
maximum66388384/flags512. PNY clean checker passed separately. Neither ran a
seek-failure path. A first independent record-verifier draft used wrong field
indices and failed before authority writes; its source/error are preserved,
corrected direct header/core/footer verification passed. No physical fault
test or console memory/syscall probe was performed in this development.

## Concrete conditional unsafe-write path

The P9 block writer14918..14aec calls seek-wrapperf7e8 at14974,149c4 and14a24.
The wrapper passes a64-bit byte position to syscall818; its captured ordinary
error path converts a nonzero syscall status to -1. Its alternate descriptor
route and real kernel error semantics are not emulated. An unsuccessful seek
does not establish the intended disk position, so subsequent writes must not
rely on that position regardless of the real kernel's cursor behavior.

For the first two calls, the writer detects a negative result but calls the
error policy14888 and, if it returns, branches into retry writing. The third
seek, which repositions after a failed sector write, had no result check before
the next iteration. In a synthetic failing-seek environment retaining the old
cursor, writes can consequently target stale/advanced offsets using a different
buffer sector. This is an actual code-path/model finding, not an observed
hardware corruption or a claim about every kernel failure outcome.

The first48-case model mocked warning/prompt behavior and demonstrated only a
conditional continuation. The separate second48-case model executes actual
ordinary non-preen/non-mounted warning and prompt instructions with yes-answer
mode. strcmp/formatter/kernel I/O/nonlocal-exit callees remain explicit mocks.
That ordinary path can continue, so the finding is not based solely on assuming
that a fatal preen warning returns. Forced-abort behavior is modeled separately.
The mixed text inventory's first scan hit embedded data; bounded captures and
failure were retained. The next inventory scans aligned candidate words and
explicitly does not claim CFG/alias closure or that every candidate is code.

## Exact correction

P10 redirects the two post-error-policy continuation words14ad8/14ae8 to a
shared32-byte helper region26500..26520. It clears the same I/O-success byte
that the existing bulk-write failure path clears, sets returnr3=-1 and branches
to the original block-writer epilogue14a68. The original warning/abort policy
still runs first. It neither retries nor attempts more writes for that block.

The third hook replaces the nop after the sector-reposition seek at14a28. The
helper checks its64-bit result: negative joins the same failure exit, otherwise
returns by direct branch to14a2c. No new call, syscall, heap allocation, memory
size, PRX relocation, indirect jump or raw heap access is introduced. CR7 and
volatileGPR0/3/9 may change; original nonvolatile registers/TOC/stack/LR and
CR2..4 are preserved. Other blocks/callers, write-error policy and full failure
cleanup are not redesigned. A prior partial write is not undone by this fix.

## Verification and limits

312 actual-instruction differential cases cover three independent text/data
placements,512/4096/16384-byte blocks, low/zero/>signed32-bit-sector/high-Lexar
positions, all three seek failures, successful short-write recovery, sector
write failure with a successful reposition, negativeFD and forced abort.
All three error paths stop further modeled writes and clear the existing flag;
ordinary successful paths preserve the P9 I/O observations exactly. Both actual
PNY and Lexar superblock flush layouts, clean/dirty and present/missing summary
fixtures, are compared. The missing-buffer case remains an unclosed conditional
failure-state concern; this fix does not supply a new valid summary buffer.
Kernel I/O/strcmp/formatting/nonlocal-exit implementations are mocks, so this is
not hardware fault injection or proof of all actual cleanup/result propagation.

The separate delta audit restores exactly three hook words and32 previously
zero helper bytes to recover the entire P9 ELF. Program headers, relocations,
data, existing P9 guards, observer code/flags and128MiB budget are unchanged;
no relocation site or target overlaps the new helper. Two full builds match
byte-for-byte. The separate package audit validates PUP HMAC, PKG HMAC/ECDSA,
matching SPKG header, SELF section HMAC/digest2, native/Python whole-ELF agreement
and loaded-byte deltas at four base pairs. Whole CoreOS/sysconf/version entries,
other flash packages and other tar members/headers/padding/trailer are unchanged.
SELF signature bytes are inherited under the existing CFW verifier policy;
Sony authenticity or SPKG signature is not claimed. Earlier58000-event P8
observer validation is inherited unchanged, not rerun as a P10 hardware test.

PUP SHA885af0721b448e329a1d8528824b00fc607b8d7f3332ce6e79f03bfcd95a636d,
215765852bytes. Utility SELF SHA
92230e04459b7bf74193a4c38ae68b6c45bee896bfdb5c657bcf9f6ab7937e26,
78375bytes. ELF SHA
daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688.

The next bounded hardware test is installation/ordinary boot on the currently
fitted disposable Lexar, followed by exact installed-file readback when webMAN
is available. A new before-update fixed file GET was refused by HTTP at1.11;
no fresh Lexar SELF baseline is claimed. Existing P9 attribution remains the
prior X whole-SELF readback and no-update sequence. No manual checker, induced
seek failure, dirty flag, format, rebuild or populated-data test is included
in the P10 installation protocol. Genuine failure/recovery testing requires
a verified restorable fixture. Full native allocator bound/headroom/alias
coverage/teardown, all failure cleanup, full-capacity/alias resistance,
durability, populated/near-full repair and >2TiB remain open. Stablefalse.
