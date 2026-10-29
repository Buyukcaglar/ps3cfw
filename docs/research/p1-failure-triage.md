# HDD2TB-P1 Crucial refusal: current decision

**Current boundary (HW001E complete, P3 prepared):** the photograph confirms `HDD2TB-P2D`, PS3 CAP **2,000,398,934,016 bytes** and GATE **1,649,267,441,664 bytes**. CAP matches the prior PC measurement. See [HW001E result](../observations/HW001E/result.json). The new **HDD2TB-P3** combines the 1984 GiB emergency limit with the same limit in sysconf_plugin's format-confirmation path: three actually different decoded bytes across two modules. Two complete builds match and a separate-parser final-PUP/crypto/scope audit passed. See [code review](../research/p3-code-review.md), [rebuild review](../research/p3-rebuild-review.md) and [software record](../candidates/HDD2TB-P3/software-verification.json). Review was by the primary agent using separate parser/decoder implementations; no separate human/agent review is claimed. Next is [HW001F](../candidates/HDD2TB-P3/HW001F.md): working-HDD Recovery installation/XMB control, then native formatting/first XMB and one normal reboot on the same empty Crucial. Live [STATUS](../plan/STATUS.json) records actual USB staging. P3 remains experimental; checker/repair, full-capacity I/O and durability are not qualified.

The earlier sections below retain the sequence of investigation; their pending-install/readback and exclusive emer-message-source statements are superseded by HW001D.

Date: 2026-10-11. P1 SHA256 remains `F7ABF409C9F0B6D04B5D9F8F44FB76142363759BEB3DD8F060EC1A2DC5400F68`; the supplied original also retains its pinned SHA256. The user's installation/control success and post-confirmation refusal are recorded separately in `observations/HW001-P1-user-result.json`.

## What changed after the hardware report

The user tested the Crucial BX500 identified earlier as `CT2000BX500SSD1`. They report a format offer followed by the unsupported-hard-disk message after accepting it. The exact prompt, five-second START+SELECT instruction, progress display, delay and intervening reboot remain unknown. Initial commentary inferred that the first check had passed; the subsequent UI trace does not justify that inference from an unspecified format offer alone.

The normal and Safe Mode copies of that message in the pinned recovery executable both follow the same capacity helper. The normal state8 and Safe Mode state4 assignments each have one identified constant writer, following a successful capacity query with an oversized result. Inspected format-error classifiers select other messages. The internal recovery callback's own format warning comes after admission, but the earlier externally shown prompt has not been classified. This is bounded static evidence, not a trace of the user's console.

Parallel audits traced 64-bit region creation and last-sector addressing. A bounded instruction model of the embedded geometry helper accepts representative 2 TB sizes, with a 106,496-byte summary below the observed 128 KiB LV2 bound. These findings do not prove formatting works; they establish no additional minimal formatter/region patch for this reported message. The separate 32 MiB full-checker budget remains a real repair barrier and is not established as this refusal's cause.

## Actual Crucial PC measurement

The user then connected the empty/unformatted Crucial through USB, identified Windows Disk3 and authorized probing plus elevation. The independently reviewed helper rechecked its Windows USB identity, exact size and nonboot/nonsystem flags before each command. It retrieved ATA IDENTIFY, annotated IDENTIFY words and existing SMART information. All three queries returned zero status; SAT12 fallback was not used. No initialization, formatting, data-sector write, firmware change, setting or self-test command was issued.

| Observation | Result |
| --- | --- |
| ATA model / firmware | `CT2000BX500SSD1` / `M6CR091` |
| ATA exposed capacity | 2,000,398,934,016 bytes |
| ATA logical sector count | 3,907,029,168 |
| Logical / reported physical sector bytes | 512 / 512 |
| P1 ceiling | 2,130,303,778,816 bytes |
| Margin below P1 ceiling | 129,904,844,800 bytes |
| Word86 bit10 | Set; consistent with the traced extended-capacity parser |
| SMART self-assessment | PASS; selected reallocation/pending/uncorrectable/CRC counters zero |

Windows Get-Disk and ATA report the same capacity. Windows exposes the USB bridge's identity/revision; direct SAT IDENTIFY exposes the actual SSD firmware and a different serial. Use the ATA identity for the sample record. The raw values and query scope are in `observations/Crucial-PC-probe-summary.json`; original captures are in `observations/Crucial-PC-ATA-20261011-160513-777/`.

This is the SSD's ATA report through this USB bridge. It is not a direct capture of the PS3's device-info fields. It narrows capacity/sector-format explanations but does not establish end-to-end compatibility, full media health, hidden-capacity settings or data durability.

## Completed installed-bank observation

The user supplied the canonical 256 MiB NAND dump for HW001B. Its header selects ROS1, and **ROS1's entire CoreOS exactly matches P1**. Native/Python decoding confirms P1's `380001f0` gate. ROS0 carries 4.92 metadata, with emergency code byte-identical to the supplied baseline and its stock `38000180` gate. See `observations/HW001B/RESULT.md` and `research/hw001b-independent-review.md`.

This establishes installed bytes and selection metadata at dump time. It does not prove which bank or module executed during the earlier failure. No bank-selector change is justified.

## Next required observation

The first P2D update attempt is now recorded in `observations/HW001C/initial-install-result.json`: save-update unchecked, followed after restart by “The latest version of the system software is already installed. There is no need to update.” P2D installation/execution is unconfirmed. Source, P1 and P2D all declare 4.93 and have byte-identical updater executables. This is an installation-route/version refusal, not a new Crucial compatibility result. The next step is the ordinary Recovery **6. System Update** route on the working HDD after rechecking the actual USB copy's hash. The revised HW001C protocol distinguishes its ordinary update START+SELECT prompt from the later Crucial format warning. Stop if Recovery also refuses; no version bump, downgrade or protection change is justified. See `p2d-same-version-reinstall-review.md` and `p2d-reinstall-protocol-review.md`. The old HW001B dump does not establish post-attempt installed bytes.

The user reported leaving **Save Update Data on System Storage** unchecked during P1, initially proposed checking it for P2D, then confirmed leaving it unchecked for the attempted P2D update. This option retains a PUP installer on the currently installed HDD for later reuse, as directly explained by developer DeViL303 in [post 219](https://www.psx-place.com/threads/4-88-update-is-live-official-hfw-hen-released.34066/page-11). Unchecked did not prevent P1 installation, as shown by HW001B. Saving a PUP on the working HDD does not carry that file onto the swapped empty Crucial. There is no evidence that checking it fixes capacity admission. Record the setting; do not reinstall solely to change it. The result template includes that field. This checkbox clarification changed no firmware; the subsequent version refusal separately required the protocol revision above.

**HDD2TB-P2D / HW001C measures the byte capacity consumed by the executing rejection path.** It is a diagnostic, not a compatibility fix: it restores the supplied stock 1536 GiB admission threshold so a correctly reported native 2 TB drive takes the existing refusal branch. Five instruction edits and one bounded format string direct that branch's actual unsigned capacity into the existing normal/Safe Mode error display.

P2D does not retain P1's 1984 GiB threshold, change the capacity query, formatter, filesystem, LV1/LV2 or checker budgets, or unconditionally block formatting. If PS3 reports a value at or below the stock threshold, the original accepted path remains reachable. `candidates/HDD2TB-P2D/HW001C.md` stops the experiment at the diagnostic or unexpected format warning. No real data belongs on the test SSD.

Two complete builds produced SHA256 `4852F56F26C30231E0F663CDD9C0BE3FE328CF5690FA7FEA257297544BAACB71`. Independent rebuild/crypto and diagnostic-code reviews are linked by its software-verification record. Hardware installation, display and PS3 capacity are still unobserved. The next compatibility revision depends on the returned marker, capacity and exact screen sequence.

Supporting independent reviews: `p2-format-path-review.md`, `p2-storage-review.md`, `p2-formatter-review.md`, `hw001b-dump-protocol-review.md`, `crucial-probe-review.md`. Their separate static, synthetic and measurement limits remain in force.

## Current outcome: HW001F format-completed UI, post-format stall

The earlier P1/P2D refusal discussion above is historical. P3 raises both demonstrated admission gates and now reaches the format-completed screen on the Crucial. The user confirms working 1 TB XMB before and after, but the Crucial remains at the startup wave after about ten minutes, and normal shutdown fails. Current detailed evidence and static quick-check/mount trace are in `research/hw001f-startup-triage.md` and `observations/HW001F/result.json`. Next is physical Recovery entry/menu observation only, `observations/HW001G/PROTOCOL.md`; retain the formatted state and accept no operation. No stable-support claim or speculative memory increase is justified.
