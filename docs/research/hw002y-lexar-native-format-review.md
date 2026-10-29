# Lexar native format and ordinary boot experiment review

13 October 2026. Primary-agent review within the user's standing development/
hardware-test authorization and explicit availability of both empty disposable
spares. The current user identifies the connected Lexar as WindowsDisk3. Fresh
Windows/ATA/model/serial/capacity/sector evidence identifies the actual target;
the USB bridge serial/UniqueId reused by other drives is not sole identity.

The fixed read-only probe runs a hash-pinned smartctl through the installed
on-demand administrator helper. Four commands completed with status0, and ATA
identity agrees before/after. No data/settings writes, SMART enable/self-test,
initialize/format, HPA/DCO or console action occurred. Evidence and the completed
administrator receipt are preserved. The native probe processes have exited.
SMART self-assessment pass/no logged errors is limited health evidence, not a
media test. Missing vendor attributes must not be called zero or interpreted
as a wear percentage without established semantics.

This Lexar exposes2048408248320bytes, about1907.73GiB, larger than the tested
2000398934016-byte PNY/Crucial. Its4000797360logical sectors remain below2^32.
It fits P9's inherited1984GiB admission ceiling2130303778816bytes. The existing
P9 package inherits the earlier reviewed admission and aggregate-mount changes;
only the utility has a fresh complete installed-file readback in HW002X. No new
whole installed firmware/kernel identity is claimed by this capacity arithmetic.

With4KiB fragments, the entire physical drive yields an upper bound of62512460
even-rounded bitmap bytes. This is a bound on that one request, not a total
checker working set or128MiB sufficiency proof. Assuming the same native format
parameters seen on the other two drives (fpg73900,16-byte group summaries,
4KiB summary rounding, positivecontigsumsize), there would be at most6768groups,
110592summary bytes and144432aggregate bytes. That aggregate fits the inherited
196608limit and its78896-byte tail fits the existing131072allocation class.
These are conditional projections; the Lexar is unformatted and its actual
filesystem geometry is not yet measured. Do not substitute predictions for
post-format native metadata evidence.

Prerequisites for this first model-specific observation are sufficient: exact
currentP9utility readback and clean PNY checker/boot controls, freshly identified
disposable Lexar, compatible512logical sectors, admission/geometry arithmetic
and preserved original1TB/populatedCrucial/PNY. The user will operate the native
format confirmations; no PC format/writer or firmware update is issued. USB
storage is removed to avoid treating an existing inherited diagnostic as a
new attempt. Active format is not interrupted at an arbitrary timeout.

The release scope is exactly first native format/XMB/capacity and one ordinary
shutdown/power-on with this empty Lexar. Stop and report unsupported/errors or
unexpected update/repair/restore prompts. Do not repeat operations or infer
that1863GB is the only correct displayed size. No manual repair, fault, power
loss, populated/near-full experiment or firmware candidate is released. Native
layout inspection follows separately. Stable storage support remains false.
