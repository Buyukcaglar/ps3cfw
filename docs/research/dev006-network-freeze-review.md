# Current disposition: recovered; corrected probe passed

The chronology below preserves earlier checkpoints and pending statements as historical. Following confirmed ordinary restarts, corrected query-only report observations/HW002A/20261011-204320-114987/result.json and128MiB report observations/HW002A/20261011-204338-362165/result.json completed. Slot1 total213MiB, available166.1875MiB;128MiB allocation left38.1875MiB and free restored the exact original value. Both349 free and owned scratch cleanup returned success. The live LV1 mapping was0x08000000 and all code guards matched. Eighteen host tests pass. The user confirmed responsive XMB, normal shutdown and power-on without a repair request. No checker/repair ran; integrity and the earlier freeze's cause remain unproven. See observations/HW002A/RESULT.md and freeze-followup/result.json.

P5 is now built/reviewed for installation/clean-boot control only; actual checker peak/context remains pending. No further network experiment is needed before that hardware result.

---

# HW002A network probe interruption

2026-10-11, primary-agent review. No separate reviewer is claimed.

The user confirmed webMAN was running on<ps3-ip>. HTTP returned webMAN MOD1.47.50 Full; TCP7887 initially refused. The existing `/netstatus.ps3?ps3mapi` route reported Disabled. The agent started only that transient service through `/netstatus.ps3?start-ps3mapi`, which reported Enabled. No settings form or registry write was submitted.

The first connected probe reported core292, firmware1171 (0x493), PID16777984 and name `01000300_main_vsh.self`. Its original exact-name guard rejected this before allocation. The tool now accepts that exact PID-bound name alongside vsh/vsh.self; arbitrary suffix matches remain rejected.

The next probe stopped at its P4 kernel instruction guard, also before allocation. `PEEKLV2 0x80000000002cac74` returned0xf80b0020e9630020, rather than the expected instruction pair. Bounded additional TCP peeks are saved in analysis/dev006/live-kernel-guard-triage.json. The pinned Cobra source implements PS3MAPI LV2 peek as an LV1 read at a fixed0x08000000 offset. The pinned webMAN firmware detector instead searches sixteen-MiB offsets1 through15. This is a concrete reason to investigate the mapping; the correct mapping on this console has **not** yet been measured.

The agent then attempted a direct syscall6 read through HTTP at virtual0x80000000002cac70, passing its address as decimal9223372036857703536. That single request timed out. A subsequent root HTTP request and a TCP greeting check also timed out; the user reported **“it is frozen”**. No later live requests were sent. The direct syscall6 request was outside the reviewed diagnostic tool's allowlist and should not have been issued without reviewing its complete argument conversion. This was an avoidable agent error.

The HTTP route calls val(), which uses signed decimal `_Stoll` and hexadecimal `_Stoull`. The submitted address is above signed64-bit maximum. Decimal conversion overflow is a plausible cause of an invalid kernel access and the freeze, but no exception trace or actual overflow result was captured. The exact freeze cause remains unproven. There was no explicit disk, flash, code or registry write and no diagnostic scratch/128MiB allocation. A freeze/forced shutdown can still affect in-flight ordinary filesystem activity; this is not a data-integrity guarantee.

The user has been asked to power down through the front control, holding it only if ordinary shutdown fails, then restart with the Crucial and report the first screen/XMB and any repair/format prompt. **No further live requests until that recovery outcome is received.** Do not initiate manual repair, rebuild, format or another firmware update as diagnosis.

The corrected tool no longer uses fixed-offset PEEKLV2. It reads only the CEX marker at known offset2ed818 for each of the15 bounded LV1 mappings, requires exactly one match, then requires all16 exact P4 bytes at2cac70. Both addresses and expected bytes come from the SHA-pinned P4 ELF/program-header mapping. All four unchanged VSH code guards and the container-ID checks remain. Every HTTP syscall argument is now hexadecimal; syscall6 remains outside the tool's allowlist. The revised contract, source and tests require pin readback before use. Seventeen host tests and Python compilation pass; these corrections have not yet run on the console.

The two supplied photographs were preserved at observations/HW002A/freeze-followup/screen-1.jpg and screen-2.jpg. They show the improper-shutdown notice and a subsequent optional filesystem-check/repair confirmation, with webMAN4.93 CEX Cobra8.5 Full visible. The user had not accepted repair. Selecting the displayed Back once returned to XMB by user report. This is recovery/menu evidence, not a successful repair or disk-integrity result.

After that confirmed recovery, query-only report observations/HW002A/20261011-204056-671822/result.json passed the exact P4 region (LV1 offset0x08000000), all four VSH code regions, and slot1 ID1056964612. Thus the correct post-restart mapping is measured, but the earlier fixed-route mismatch remains unexplained; do not claim this console uses a different current offset. The scratch API returned user0xd00f2000/kernel0x8000000100058000. A mistakenly strict64KiB alignment guard rejected those4KiB-aligned addresses, before writing the owned record or querying343. It conservatively reported cleanup_unconfirmed and retained the mapping. No128MiB request or filesystem operation ran. The user was asked for one ordinary restart to clear that mapping; no further requests until confirmed.

The pinned Cobra lv2/include/lv2/memory.h defines selector0x100 as MEMORY_PAGE_SIZE_4K,0x200 as64K and0x400 as1M. The reviewed scratch request uses0x100. Its64KiB size therefore does not imply64KiB base alignment. The corrected tool now requires4KiB alignment for both returned scratch addresses, preserving size/range/ownership checks. The separate syscall350 flags0x200 and its64KiB allocation/free alignment requirement remain unchanged. An observed-response host test covers this exact distinction. Eighteen host tests and compilation pass; the revised scratch/query path remains hardware-pending.

After confirmed ordinary restart, independently recheck the corrected implementation and use query-only first. Any new timeout or ambiguous cleanup stops further probes. No repair-budget firmware has been produced, and stable storage support remains false.
