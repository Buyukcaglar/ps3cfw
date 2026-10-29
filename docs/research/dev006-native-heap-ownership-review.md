# Native heap backing ownership and deletion evidence

13 October 2026. Primary-agent exact-binary/model review. Fresh8captures pin
retail liblv2 SHAaac69540830b4a6673b93331bf52266f360551a2732adcbb3c7a808daddf09c5
and P9 ELF SHA1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2.
No hardware operation or firmware change was performed by this investigation.

The selected utility creation passes flags80150000 and an8-byte attributes
record containing the caller-provided backing pointer. In the native create
path, a valid nonzero pointer with negative flags and low bit clear reaches
raw initialization using that pointer, bypassing syscall348. The ownership
flags retain the sign bit in this provided-buffer route. Default/fallback
allocation instead clears that bit before storing flags at heap+1d0 through
the captured name/flags setter. The metadata getter7974 returns those flags
and the original backing pointer from heap+10.

Native deletion's78ec..7924 release gate skips syscall349 for negative stored
flags, and calls it for a nonnegative owned buffer. This explains why the
selected provided backing must be released by its outer caller rather than
twice by native deletion and that caller. The previously reviewed P5 caller
has one349 after a successful utility call; its42-case model is inherited,
not rerun or upgraded to hardware accounting by this audit.

The new model executes actual ownership-selection instructions, the owner
field store/getter and release gate.72 creation-island cases cover sign/low-bit
flags, absent/zero/valid supplied pointer, allocation success/error and register
upper bits.78 release-gate cases cover both owner signs and success/error from
the mocked free syscall. Raw initialization, name/mutex setup and unlock are
explicit mocks; release begins after earlier delete operations are assumed to
have returned. It does not emulate the full heap or prove all cleanup.

The captured owned-buffer free gate overwrites the mocked syscall349 error
before assembling a zero return. That result is not a new defect claim in the
selected provided-buffer lane, which skips that native free, and does not
justify a new firmware patch by itself. Global initialization failures, lock/
mutex return handling, actual parent free status and concurrent/escaped heap
interfaces remain unqualified. Native raw delete7fb4 follows extra-segment
links without a discovered cycle bound; damaged control structures are outside
this model. A complete alias, failure cleanup or corruption recovery proof is
not established.

The inherited P9 observer finalizes its table before calling native delete.
Matched-delete1 is consequently an entry witness, not a separately serialized
successful native-delete return. HW002X reports3charged objects/122928bytes at
that snapshot; it alone proves neither a leak nor release. Utility0 and exact
installed identity are separate observations. Keep flag512 and the native
peak/bound, concurrency, fragmentation and repair-context headroom gates open.

Evidence: analysis/dev006/native-heap-lifecycle-v1/evidence.json and captures;
analysis/dev006/native-heap-ownership-model-v1/result.json. Independent drive
qualification on the empty Lexar is a separate branch and does not relax any
populated Crucial, near-full, fault or stable-support requirement.
