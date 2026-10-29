# P11: reject a flush with a missing required summary buffer

13 October2026. Primary-agent review with separate instruction-model,
byte/relocation and package/crypto/parser implementations. No independent human
or subagent review is claimed. This is an experimental local error-path fix.

P10's clean Lexar checker/restart passed HW002AC. Fresh272B diagnostic reports
worker1,utility0,128MiB,zero observed allocation failures,flags512,Lexar bitmap
62446924 and consistent unsaturated partial wrapper maximum66387952bytes.
Whole installed78375B SELF and two whole HDD controls match before exactly.
The12objects/127248B snapshot precedes native delete and proves neither a leak
nor successful teardown. These clean results did not exercise an allocation
failure. The user returned USB toPC; the reviewed read transport was adapted,
not the console test, and no repeat checker or console write was performed.

## Demonstrated conditional path

Setup1f64c tests the minimum-free-space field. With synthetic value100, actual
ordinary non-preen/non-mounted yes-mode warning/prompt instructions can accept
correction to10 at1fb04 and mark the primary buffer dirty at1fb0c. A negative
write descriptor instead makes the actual prompt decline. The first summary
calloc result is stored at superblock+34c and checked at1f6b4. A null result
reaches the actual ordinary cleanup(0) and returns original80010004.

Ordinary cleanup calls flush1558c. In P10 it clears the dirty byte, writes the
superblock, then walks positive summary size using the null summary pointer.
The model observes a valid8192B superblock write at byte81920 followed by invalid
null/offset-buffer write attempts. Kernel writes/invalid-pointer errors,
allocation/free/close and format/strcmp are explicitly mocked. No real device
fault, disk write or observed corruption is claimed. The valid captured PNY
and Lexar geometries, clean alternate buffer and empty synthetic queue are
explicit preconditions; whole setup and kernel semantics are not emulated.

The corrected12-case source/model spans three segment-base pairs, both drives
and descriptors-1/42. Its first draft incorrectly expected a correction even
without write access; that source/failure is retained and v2 honors the actual
prompt's refusal. The earlier120-case model proved only clean-buffer cleanup.
A capture-script syntax rejection was corrected before capture execution;
its rejected source is retained. None of these failed drafts produced firmware.

## Exact change

P11 changes only instruction155c0 and76 previously zero bytes26540..2658c of
P10. The helper executes the displaced write-descriptor-pointer load. Negative
global write descriptor, nonprimary buffer, nonpositive summary size or a
nonnull summary pointer returns to the original body at155c4.

For a dirty primary buffer, writable descriptor, positive summary size and
null summary pointer, it clears the existing I/O-success byte and branches to
the original epilogue1563c before either superblock or summary writes. The
primary dirty byte remains set: the failed flush has not committed that state.
It makes no call/syscall/allocation/import/relocation/memory-size change.
Volatile r0/r9/CR7 may change; the saved r28 and other nonvolatile state are
restored by the original epilogue. The flush return value is not newly
specified; the existing failure byte records the rejected flush. This does
not redesign all caller return-status or error propagation behavior.

The first guard encoder rejected a conditional return branch beyond PPC's
signed16 range, before producing any ELF. Its source/error are retained under
v1. The corrected v2 uses short local conditional branches to an unconditional
return branch. All19 helper instructions and six branch targets are decoded
and checked separately.

## Verification and limits

708 actual-instruction differential cases cover576 flush combinations over
both captured layouts, three base pairs, primary/other buffers, clean/dirty,
present/missing summary, positive/zero/negative summary size, negative/positive
descriptor and initial I/O flag0/1;12 actual correction->summary allocation
failure->cleanup cases; and120 earlier clean-buffer/all-five-failure cases.
The rejection cases make no modeled seek or write, preserve dirty1 and clear
the I/O flag. All nonrejection observations are identical to P10. Modeled
nonvolatile GPRs/TOC/stack/LR/CR2..4 survive ordinary returns. The interpreter
models comparison values rather than every architectural CR/XER bit.

A separate full-byte audit recovers the entire P10 ELF by masking just the
one hook and76 owned bytes. Program headers, relocation records, data, P10's
seek stops, P9 allocation guards, observer flags and128MiB budget are exact.
No relocation site/target overlaps the helper and it contains no new calls.
Two full PUP/SELF/manifest builds are byte identical. A separate parser checks
PUP/PKG HMAC, PKG ECDSA, SPKG header agreement, SELF section HMAC/digest2,
native/Python whole ELF equality and loaded deltas at four base pairs. CoreOS,
sysconf, versions, other flash packages and other tar members are unchanged.
Existing CFW SELF signature policy is inherited; Sony authenticity is not
claimed. P8's58000-event observer tests are inherited, not a new native test.

PUP d299aad533a12ff8a7a6e5bc0e20093977de18e7e9eef0aac7cc58b4aa065552,
215765852bytes. SELF b5e140fe5ce114e2b25924b30cfb77b6cb956741ff45f91ccd0a1adf873932b6,
78423bytes. ELF904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e.

This guard does not validate a nonnull but short/partial/stale summary, undo
prior writes, suppress every later write after a failed flush, prove whole
allocation-failure cleanup/native teardown, or establish complete native memory
bounds/headroom/alias coverage. Populated/near-full repair, true fault recovery,
full-capacity alias resistance/durability and >2TiB remain open. Stablefalse.
Next bounded hardware gate is only P11 installation/ordinary boot/restart on
the fitted disposable Lexar and exact installed-file readback. No manual
checker, deliberate allocation failure, corruption, game or populated test.
