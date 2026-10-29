# HW001F: format completion followed by startup stall

Date: 2026-10-11. Candidate context: HDD2TB-P3, PUP SHA256 `9197335b04b6cdf8c40393d6375dd6ee77d2f62fc85da5cac0989d012ed00eaa`.

## Observed and reported evidence

The five original photographs are preserved with hashes in `observations/HW001F/photo-manifest.json`. They show the two native format confirmations, progress at 24%, the format-completed screen, and the startup wave without XMB icons. The user reports no XMB after approximately ten minutes total and no HDD activity indicator. Front power did not shut down normally; after a failed first attempt, continued pressing after three beeps forced shutdown. This is an uncontrolled shutdown observation, not a durability qualification.

The user separately confirms P3 reached XMB on the previous 1 TB HDD before fitting the Crucial, and the same 1 TB HDD still reaches XMB and works after reinsertion. This is a useful installation/boot control. Installed P3 module bytes have not been read back. The Crucial was formatted through the native UI, but actual filesystem geometry, data integrity, full-capacity addressing and successful mount remain unverified. The user reports 2 TB recognition; no XMB System Information capacity photograph has been received.

## Static investigation

`analysis/hw001f-boot/trace_boot.py` makes mapped read-only captures, recorded by hash in `static-captures.json`. The baseline VSH SHA256 is `e3681dbe492a508383ecf69ee5e3595cc9eb1c9cc3c300a3360b9d90c048afc4`; filesystem initialization utility SHA256 is `6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a`. P3's audited changes are confined to emergency/sysconf admission constants; it does not change these two modules. These captures identify candidate startup paths, not the blocked runtime instruction.

| Path | Static evidence | Implication and limit |
| --- | --- | --- |
| VSH startup `0xd103c` | Under its state predicates, backing request at `0xd118c` and heap argument at `0xd11a0` are both 2 MiB. Calls `0xd9d6c`, stores its status, and calls mount helper `0xda0f8` with `/dev_hdd0` only when status is zero. | The traced ordinary startup lane is distinct from the 32 MiB full-repair caller. Actual predicates/runtime route are unknown. |
| VSH check helper `0xd9d6c` | Calls fs_utility_init NID `6b5896b0` at stub `0x6379a0`; export resolves to utility VA `0x2d0`, which calls `0x1938`. It retries `0x8001002d` with 100,000 microsecond sleeps, counter initially 200. | At most 201 explicit sleeps (20.1 seconds), provided called operations return. This loop's sleep count alone cannot explain ten minutes. Imported calls and helper operations may themselves block. No symbolic error name is asserted. |
| Quick checker launch | Arguments read directly from mapped VSH strings: `fsck_cfs`, `-F`, `hdd0`. Supplied-buffer call is at `0xd9ebc`; fallback is at `0xd9ec8`. Status 0 or 7 becomes helper success; 3 through 6 requests a full check via error status. | Log text says `full_fsck returned error` even in this quick-check helper. It must not be used alone to classify the lane. No checker return has been measured on the Crucial. |
| Utility quick branch | At `0x18618..0x18624`, the `-F` flag branches to `0x19254`, before the full-check setup. The quick lane opens/reads the volume and examines superblock state at `+0x520`. | A large full-check bitmap allocation is not demonstrated on this lane. This does not exclude other startup or dirty-state recovery paths. See the earlier complete checker audit. |
| HDD mount helper `0xda0f8` | Calls wrapper `0xda0b0`, then VSH `0x6325b4` -> `0x632468`; syscall `0x345` at `0x632528`. Retries `0x8001002b`, counter initially 5, with 3-second sleeps. Logs mount point and success/error. | Six attempts and at most 18 seconds of explicit sleep, if calls return. A blocking filesystem/kernel operation remains possible; the photographs do not prove it. |

The full-repair 32 MiB backing/heap limitation documented in `research/checker-budget-audit.md` remains unresolved, but these observations do not establish it as the startup stall's cause. Raising memory constants or suppressing checks is not justified by the present result. A live background animation and lack of the activity indicator do not establish filesystem health or identify the blocked thread.

## Next hardware dependency

Use the existing P3 and preserve the formatted Crucial. Observe physical Safe Mode entry only, as `observations/HW001G/PROTOCOL.md` specifies. This checks whether the emergency interface can recognize the post-format state and present a responsive menu. It does not prove XMB's `/dev_hdd0` mount or clean filesystem integrity. After the forced shutdown, a repair prompt is possible; photograph it and stop before accepting it.

If Recovery is reachable, retain its exact screen/state and choose the next instrumentation or read-only disk-forensics step from that evidence. If Recovery stalls or refuses the disk, trace the emergency discovery/mount path before another firmware revision. If existing evidence cannot localize the blocked stage, a separately reviewed startup diagnostic may be needed around quick-check/mount calls; no such candidate has been built or staged in this iteration.

No new firmware, USB staging, raw device access, format, repair, database rebuild or NAND readback was performed in this iteration. Stable support remains false.
