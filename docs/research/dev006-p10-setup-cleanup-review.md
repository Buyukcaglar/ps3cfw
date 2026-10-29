# P10 conditional setup-to-cleanup instruction review

The new 120-case model executes the actual ordinary cleanup and return
instructions after each of five modeled setup allocation failures. It uses
the captured PNY and Lexar geometries, three relocated segment-base pairs,
directory inputs 0/139, and write descriptors -1/42. Saved GPRs, stack, LR and
the modeled CR2..4 values survive. Requested allocation sizes match both layouts.
Native calloc/free/close and kernel I/O remain mocks; no physical drive,
console, secret or hardware failure injection was used.

The prior model replaced cleanup wholly with a mock. This extension reaches
the real ordinary cleanup branches, with zero dirty bytes in the primary and
auxiliary buffers and an empty synthetic buffer queue. Under those explicit
conditions there are no modeled seeks/writes. FD -1 closes the read descriptor;
FD42 closes both descriptors and calls mocked free(NULL). It does not establish
that every earlier allocated object is freed, nor that a bulk heap delete returns.
Successful summary reads, later buffer initialization, mounted/preen paths,
dirty/nonempty-queue cleanup and native allocator behavior are excluded.

Independent result checks confirm the unique 120-case matrix and expected
request/close/free shapes. Fresh selected P10 instruction captures equal P9
outside P10's writer guard. Inherited metadata correction at1fb0c and1fc60 can
mark the primary buffer dirty before all setup allocations finish. Therefore
the clean-buffer precondition is not proved for all real setup failures.
Missing-summary/dirty-buffer handling and complete failure cleanup remain open.

Source documentation erratum: the copied model's opening docstring still says
P9 and mocked warning/prompt internals. The executed source actually pins P10
and includes the ordinary warning/prompt instructions inherited from v2. Its
executed source snapshot is retained unchanged; mocks are listed in result.json.
The interpreter represents CR comparison values, not every architectural CR/XER
bit, and is not a general PPC emulator or hardware execution proof.

Evidence: analysis/dev006/p10-setup-cleanup-model-v1/source.py and result.json;
observations/HW002AC/offline-cleanup-source/verification.json. These conditional
software results do not qualify stability or real fault recovery. Next hardware
gate is only one ordinary clean P10 Lexar checker regression, with fresh USB
custody, exact installed SELF and fixed HDD control files before/after.
