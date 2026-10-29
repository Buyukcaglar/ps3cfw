# Sustained PNY capacity test after the bounded API pilot

AV's native reader ran and returned to XMB by owner report. AW is the next
hardware dependency because the long fill needs native free-space, write,
64-bit seek and stat calls that the accepted reader did not exercise. Its
binary is limited to 33 MiB and contains no sustained fill mode.

The proposed later volume is **1,568 GiB** in sixteen new files of 98 GiB each.
That is 1,683,627,180,032 bytes, 32 GiB beyond the old 1,536 GiB byte threshold.
The planned floor is **64 GiB of available free space**, with at least another
2 GiB allowed initially for metadata and unrelated system activity. Admission
therefore requires at least 1,634 GiB available at the start. These figures are
a proposed scope, not permission to run or a claim about AW's as-yet-unmeasured
free-space values. Recalculate the admission check from AW's native byte record.

Use an exclusive nonce-owned directory and exclusive files, with a small
ownership receipt created on the confirmed spare PNY. A full writer must bind
that receipt and refuse a different session, existing destination or changed
preconditions. Preserve real data and all partial/completed test files. No
automatic deletion, truncation, raw access, firmware change or fault injection.

Generate deterministic public-nonce patterns unique to file number and 64-bit
logical offset. Use an injective pre-permutation index domain for all sixteen
files, verify independent Python vectors and expected whole-file hashes, and
compare every byte/word on full readback. Check the actual progress of short I/O,
all seek positions, fsync/close, EOF and stat sizes. No successful byte count
alone establishes integrity. Use at most a few MiB of working memory.

The writer first performs a small internal admission/readback check, then writes
the corpus with periodic free-space and cancellation checks. Reopen and verify
each finished file; after every file is written, read all files again to catch
cross-file aliasing. Preserve an append-only, bounded, checksummed USB progress
log and a final receipt after validated output publication. Periodic reports
must include bytes, file/offset, status and recent progress so a black screen
cannot be mistaken for a silent hang. Do not promise a completion time without
measured throughput; the multi-terabyte traffic can require a long unattended run.

Cancellation must be demonstrated through an ordinary file-control route on
the actual console before arming the full job. A proposed fixed USB STOP token
can be copied through the existing webMAN file service, with no process/RAM
commands. Validate the token/session, poll between bounded chunks, stop further
payload writes, flush/close the current file and publish cancellation status.
If that route is unavailable, implement and qualify an alternative before
release. AW's STOP-PROBE validates only the native token reader, and the host
case validates the stop boundary; neither proves the live operator path.

After the full corpus passes, one ordinary controller shutdown/power-on must
preserve it. A separate read-only verification mode then checks all corpus data
again without rewriting files. Finally, return only spare PNY once for guarded,
read-only decrypted metadata mapping and independently streamed coverage/hash
verification. Prove high physical extents and distinct allocation, retain
evidence across the former boundary, and compare pre-existing controls. Never
whole-hash a sparse disk image or replay an old archive over changed state.

Only after code, host faults, cancellation, package/ABI and the concrete volume,
reserve, preservation and operating instructions are reviewable should the
owner approve the full run. P13 remains installed. The final populated Crucial
acceptance follows sustained PNY evidence. Other faults, populated repair,
remaining reserved/free sectors, power-loss durability and universal stable
2 TB support are separate unqualified claims. Greater than 2 TB remains later.

API sources reviewed: pinned PSL1GHT sys/file.h for calls 801/802/803/804/809/818/820;
PS3DevWiki LV2 syscall table for 840's two free-byte outputs; RPCS3's CellFsStat
layout corroborates its 52-byte packed structure. The pilot must test the real
implementation; emulator source is not real-hardware acceptance.

https://github.com/ps3dev/PSL1GHT/blob/f649a08fd536a9e27c08c7db2d93a2d7ee4c3bbe/ppu/include/sys/file.h
https://www.psdevwiki.com/ps3/LV2_Functions_and_Syscalls#LV2_Syscalls
https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/Cell/lv2/sys_fs.h
