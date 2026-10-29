# Session A: G1, G3a, G2, G3b (+ M5 if all pass)

One sitting, about 1.5-2 hours, mostly waiting. After each numbered step, tell the
agent what you saw. The agent replies "go on" (usually within 5 minutes) before
you start the next step.

## Owner steps

Have ready: the SanDisk USB stick, the Lexar, the usual screwdriver, a phone for
photos of any unexpected screen.

0. **PC:** plug the SanDisk stick into the PC and say its drive letter. The agent
   stages P13 and ejects it.
1. **PS3 (PNY fitted, RDI12):** normal shutdown to red standby. Put the stick in
   the **rightmost** front USB port. The controller cable goes in a different port.
2. **G1, install P13:** Recovery Mode as before, then option **6 System Update**,
   confirm once. Do not interrupt it. After XMB returns: if webMAN is missing,
   install the same UPDWEBMOD package as before. Report: XMB free/total, webMAN IP.
3. **G3a, power cut (PNY):** at the XMB leave it idle for 2 minutes. Switch the
   **rear main power switch OFF**, wait 10 seconds, switch it ON, press power.
   Report: any message (e.g. "not turned off properly", "checking / restoring the
   file system") with a photo if possible, roughly how long, XMB free/total.
4. **Swap drives:** normal shutdown to red standby. Replace the PNY with the
   **Lexar**. The stick stays in the rightmost port.
5. **G2, repair on the full Lexar:** Recovery Mode, option **3 Restore File System**,
   confirm once. It may take a long time. Do not interrupt. Report: duration,
   messages, XMB free/total (last known: ~65 GB free / 1907 GB).
6. **G3b, power cut (Lexar):** same as step 3. Report as in step 3.
7. **Game:** start Gran Turismo 6 (or any game), load the save, quit to the XMB. Report OK or not.
8. **Done:** leave the Lexar fitted. If the agent confirms that all passed, it deletes
   the 858 GiB of test filler. Afterwards report the new XMB free space (expect ~920 GB).

**Stop rules:** never accept Format, Rebuild Database or Restore PS3 System
prompts. Never interrupt an update or a check. Anything unexpected: photo, stop,
report.

## Agent runbook (`RUN=runs/<gate>-<yyyymmdd>`, `IP` = owner-reported webMAN IP)

| After | Command | Pass |
|---|---|---|
| 0 | `python tools/verify_build.py` then `python tools/stage_usb.py --drive X: --clear-observer --eject` | READY; STAGED with device re-read; observer record absent |
| 2 (G1) | `python tools/check_installed.py --host IP` | match P13 SELF `7a57307b...`, 78,487 B; capacity unchanged |
| 3 (G3a) | `python tools/read_observer.py --host IP --save runs/G3a-DATE --rename-to HDD2TB-G3a.bin` | owner saw an automatic check + XMB + capacity unchanged; record (if any): budget 134,217,728, worker 1, status 0. Budget 32 MiB or repair error = FAIL (patch the other caller, P14). No message and no record = INCONCLUSIVE (no repeat) |
| 5 (G2) | `read_observer.py --host IP --save runs/G2-DATE --rename-to HDD2TB-G2.bin`, then `python tools/verify_retained.py --host IP --save runs/G2-DATE` | verdict PASS (peak <= 96 MiB) or YELLOW (<= 128 MiB); retained PASS. Expect largest_request ~62,446,924 (Lexar bitmap) |
| 6 (G3b) | `read_observer.py ... runs/G3b-DATE --rename-to HDD2TB-G3b.bin`, then `verify_retained.py --host IP --save runs/G3b-DATE` | automatic check completed; retained PASS |
| 7 | none | owner reports that the game and save work |
| 8 (M5) | `python tools/delete_filler.py --host IP` (dry run), then `--execute`, then `verify_retained.py --host IP --controls-only --save runs/M5-DATE` | 858.19 GiB freed, 0 skipped; 16 controls PASS |

Stop the session on: G1 mismatch after one reinstall, any repair error, a G2 FAIL
(do not run G3b on the Lexar then), or a retained-data mismatch (do not run M5).
Write `runs/<gate>-DATE/RESULT.md` (owner report verbatim + tool verdicts), update
`docs/STATUS.md`, and append to `docs/SESSIONS.md`.
