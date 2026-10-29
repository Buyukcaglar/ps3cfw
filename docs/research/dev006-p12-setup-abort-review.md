# P12: abort setup without committing an incomplete summary

13 October2026. Primary-agent source/model review plus separate byte/relocation
and package/crypto/parser implementations; no independent human/subagent review
is claimed. This is a bounded error-path change, not stable-storage admission.

HW002AE P11 clean Lexar checker/restart passed contextually. Its fresh272B log
was independently unpacked:worker1,utility0,128MiB,flags512,zero observed failures,
Lexar bitmap62446924,6929alloc/6917free and partial accounting maximum66388624.
Whole78423B installed SELF and two HDD controls matched before exactly. Snapshot
12objects/127312B precedes native delete; it is neither leak nor teardown proof.
No real failure was exercised, and no F:firmware backup/read/write was performed
by that diagnostic capture.

## Concrete incomplete-summary path

Actual setup1f694 allocates the summary, then reads it block by block through
14aec. On a short/failed bulk read, the ordinary reader zeroes the destination
and retries sectors. A failed sector stays zero, increases the error count and
clears the existing I/O-success byte. Setup checks the nonzero result at1f74c,
asks CONTINUE at1f76c and, in ordinary yes mode, can proceed to later allocations.
If the bitmap allocation then fails, actual cleanup(0) can write the dirty
superblock and the nonnull but incomplete summary. P11's null-pointer guard
does not reject that nonnull buffer.

Twelve actual-instruction modeled cases cover both captured geometries, three
base pairs and failure in the first/last summary block. Actual warning/prompt,
read fallback and cleanup instructions run. Synthetic device data is0xa5;
one failed512B sector remains zero, and the entire summary is subsequently
presented to mocked writes. The earlier actual minimum-free-space correction
demonstrates a reachable source of dirty primary state. Kernel I/O, memset,
allocator/free/close, strcmp/format and nonlocal exit are explicitly mocked.
This is not observed hardware corruption or a claim about every kernel failure.

## Exact correction

P12 changes two words of P11 and64 previously zero bytes265c0..26600. At1f754,
the nonzero-summary-read path now clears the uncommitted dirty bytes of the
primary and auxiliary buffers and the existing I/O-success byte, then takes
the original1fd34 cleanup(0)/nonlocal-exit8 route. A successful read branches
past this hook exactly as before. It no longer offers to continue a reported
summary-read failure or allocates the later bitmap/tables afterward.

The common setup-allocation-failure call at1fb6c is retargeted with its link
bit preserved to the second clear-state helper. That helper tail-branches to
the original cleanup14e80, preserving its existing return-to1fb70 and original
80010004 setup return. This discards uncommitted setup corrections on failure
instead of allowing cleanup to flush them. It does not undo earlier writes.

Helpers use only volatile r0/r9 and existing global pointers. They add no
call, syscall, allocation, stack frame, import, relocation, memory size or
observer/budget change. Clearing in-memory dirty state is confined to the
two setup failure routes, not normal checker writeback. Tests explicitly seed
an empty buffer queue and valid captured geometry; arbitrary dirty/nonempty
queue states and all other failure routes remain outside this proof.

## Verification and limits

336 differential instruction-model cases comprise240 setup-OOM cases over
all five failure positions, two directory inputs, initial primary dirty0/1,
negative/positive descriptors, both drives and three base pairs;48 successful
setup cases through the original buffer-initialization call; and48 first/last
summary-read failure cases. P12 reaches original exit8 after cleanup without
CONTINUE or later allocations, and setup failure cleanup makes no modeled
writes under the stated preconditions. Original OOM status/close/free routes
are preserved. Successful setup observations are identical to P11. Modeled
nonvolatile/TOC/stack/LR/CR2..4 are checked on ordinary setup returns; native
nonlocal unwinding is not emulated. Fast bounded dictionary updates implement
the same explicit mocked read/memset bytes, not native kernel semantics.

A separate full-byte audit recovers all P11 bytes by masking two words and64
owned bytes. The existing P10 seek guards/P11 null-summary guard, headers,
relocations, data, imports,128MiB budget and observer flags are unchanged.
Hook link/targets and16 helper instructions are checked. Two complete PUP,
SELF and manifest builds match. Separate package parsing verifies PUP/PKG HMAC,
PKG ECDSA, SPKG header equality, SELF section HMAC/digest2, native/Python whole
ELF agreement and loaded-byte deltas at four base pairs. CoreOS, sysconf,
versions, other flash packages and other tar contents remain unchanged.
Existing CFW SELF signature policy is inherited; Sony authenticity is not
claimed. The58000-event observer validation is inherited, not rerun hardware.

PUP7fb5d6e57ef53654f336745dbc9463c8e6b2cded03b05cdbeb80e5125215fb7c,
215765852B. SELF78455B/eb38afbb59179553ba3055d19727770b90bfec6b1111326345a4bd01644736bc.
ELF82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85.

The aligned branch inventory is a candidate-word scan, not complete CFG or
indirect reachability proof. The models use successful mock seeks; other
read-wrapper seek/retry/error policies remain open. This fix does not prove
that every underlying fault is correctly reported by the reader, validate all
nonnull buffers, undo prior writes, qualify arbitrary dirty queues, or prove
native allocator coverage/headroom/teardown/full error cleanup. True fault
recovery, populated/near-full repair, full-capacity alias resistance/durability,
stable support and >2TiB remain open. Next hardware gate is only P12 install/
ordinary boot/restart/exact installed-file readback on the fitted Lexar. No
manual checker, real I/O/OOM fault, corruption, game or populated-drive test.
