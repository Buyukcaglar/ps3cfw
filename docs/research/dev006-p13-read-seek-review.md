# P13: stop the checker block reader after a reported seek failure

14 October 2026. Review by the primary agent using separate instruction-model,
byte/relocation and package/crypto implementations. No independent human or
subagent review is claimed. This release is for the disposable Lexar installation
and ordinary boot gate only; stable support remains unqualified.

HW002AG P12 clean Lexar Restore File System and ordinary restart passed in the
user's reported scope. The fresh 272-byte record was independently unpacked:
one full worker call, utility status 0, requested budget 134217728, flags 512,
6933 observed allocations / 6917 frees, zero observed allocation failures,
largest request 62446924 and partial wrapper accounting maximum 66388880 bytes.
Sixteen objects / 127440 bytes precede native deletion. That snapshot is not a
leak measurement or proof that native teardown returned. Compared with the P11
run, the small count/accounting difference is observed, not attributed to P12's
helpers or diagnosed as a leak. Whole installed P12 SELF and two whole HDD
control files match before exactly. No real fault or populated-drive repair ran.

## Source finding

The ordinary block reader at 14aec seeks through f7e8, then reads through f5d8.
Its initial negative-seek branch at 14b88 reaches the usual warning/prompt and
retry seek. A second negative result at 14bd4 warns again, then continues into
the zero-fill and sector-read fallback. If those sector reads return their full
requested sizes, the wrapper can return 0 with its I/O-success byte still 1,
even though the failed seeks left the underlying cursor at a different position.
P12's setup guard reacts to nonzero reader results, so it cannot catch this
particular false-success return.

Twelve actual-instruction cases demonstrate that conditional continuation for
three separate text/data placements, two read sizes and two negative error
values. The seek mock retains its previous cursor on error; positional read
payloads are synthetic. Both failed seeks precede reads from offset 123456
instead of requested offset 18944. This is a modeled error path, not an observed
SSD/kernel failure or real filesystem corruption.

After a short/failed sector read, the wrapper also reseeks at 14c4c and ignores
its return. A full sector read branches around that reseek. P13 guards this
reported negative return too, stopping further reads within that invocation.

## Exact correction

P13 changes three unlinked hook words at 14b88, 14bd4 and 14c50, and 48 previously
zero bytes at 26640..26670. The first two helpers use the original signed compare
result; the third compares the sector-reseek return. A negative result clears
the existing I/O-success byte, sets the reader's error result to 1 and branches
to the original 14cf0 epilogue. This preserves native register restoration,
stack, TOC and return linkage. Successful seek paths return to the original next
instruction. No new call, syscall, allocation, import, relocation, stack frame,
memory size, heap budget or observer change is introduced. Existing P10/P11/P12
helpers remain byte-identical.

Reported seek failures now abort instead of attempting the original seek-error
retry policy. Short/failed-read fallback remains unchanged when its seeks
succeed. A destination buffer may already contain partial data; it is not
promised valid on the new nonzero return. In P12's setup caller, a nonzero summary
read follows the retained cleanup/exit-8 path. The correction does not undo
earlier I/O or certify that every caller honors all errors.

## Verification and limits

594 passing instruction-model cases comprise 72 reader comparisons with all
seeks successful, 72 initial-seek failures, 42 retry-seek failures, 72 reseek
failures and 336 comparisons with P12 setup behavior (240 allocation failures,
48 successes through original buffer initialization, 48 summary-read failures).
Failure cases stop all subsequent read/seek calls, return nonzero and clear the
existing I/O-success flag. Reader returns check nonvolatile GPRs, stack, TOC, LR
and modeled CR2..4. Kernel I/O, allocator/free/close, memset, warning/prompt,
formatting and nonlocal exit remain mocks. Ordinary unmounted yes mode is the
bounded modeled context; full native unwinding, timing/mounted/preen execution,
all indirect callers and all underlying fault policies are not proved.

Failed v1/v2 model drafts are retained. V1 incorrectly injected a retry after
a successful zero-length read; v2 incorrectly expected a reseek after a full
sector read. V3 fixtures follow the actual branches: only a short/failed sector
reaches its recovery reseek. Neither fixture correction changed the ELF, and no
failed model draft was packaged or executed on hardware.

A separate full-byte audit restores all P12 bytes after masking only the three
words and 48 owned bytes, checks branch/link/relocation scope, and verifies the
12 helper instructions. Two complete PUP, SELF and manifest builds are identical.
Separate parsing verifies PUP/PKG HMAC, PKG ECDSA, SPKG header equality, SELF
section HMAC/digest2, native/Python whole ELF equality, and loaded-byte changes
at four base pairs. CoreOS, versions, sysconf and other flash contents are
unchanged. Existing CFW SELF signature policy is inherited; Sony authenticity
is not claimed. The 58000-event observer validation is inherited software
evidence, not a new native hardware measurement.

PUP SHA256: 652c0c0312cd51283473e653df6e2cdfd874a674f6fb7e83979c45d28fed066d
(215765852 bytes).
SELF SHA256: 7a57307b62aed291803b22a4db5da6d541c004f699368957a266e7f2442b6389
(78487 bytes).
ELF SHA256: e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86.

Actual read/seek/OOM fault injection, complete native heap peak/headroom/teardown,
other error cleanup, changed-disk recovery, populated/near-full repair,
full-capacity alias resistance/durability, stable support and >2 TiB remain open.
Next hardware gate is only HW002AH P13 Recovery-6 installation and ordinary
boot/restart on the fitted disposable Lexar, then exact installed-file readback.
No manual checker, game, disk swap or real fault is requested for that gate.
