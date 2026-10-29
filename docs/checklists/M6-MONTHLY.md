# M6 monthly check (about 15 minutes, once a month until ~2027-01-29)

## Owner steps
1. Leave the SanDisk stick in the **rightmost** front USB port (it can stay there all the time).
2. Recovery Mode as before, option **3 Restore File System**, confirm once. Do not interrupt.
   (Session A on 2026-10-29 took under 4 minutes.)
3. At the XMB, start one game and load a save, then quit.
4. Report: the date, roughly how long the check took, any message (photo), and the webMAN IP.

**Stop rules:** never accept Format, Rebuild Database or Restore PS3 System prompts. Never
interrupt a check. Anything unexpected: photo, stop, report.

**Do not confuse:** XMB *Settings > System Settings > Restore PS3 System* is a factory reset that
formats the drive and erases everything. The check is only *Recovery Mode > 3 Restore File System*.
Enter Recovery Mode with the power button, not with webMAN's "recovery" link (it writes an EEPROM
flag and hard-reboots).

## Agent steps (`IP` = webMAN IP, `YYYYMM` = month)
1. `python tools/read_observer.py --host IP --save runs/M6-YYYYMM --rename-to HDD2TB-M6-YYYYMM.bin`
   The rename is required: the observer never overwrites a record (O_EXCL).
2. Pass: status 0, failed_allocs 0, budget 134,217,728, tracked peak <= 70 MiB (Session A + 10 %).
3. `python tools/verify_retained.py --host IP --controls-only --save runs/M6-YYYYMM` -> PASS.
4. Write `runs/M6-YYYYMM/RESULT.md` and add one line to `docs/SESSIONS.md`.

A failed check is the only reason for further work (CLAUDE.md rule 2). A record with the same
TABLE_FULL flags as in Session A is expected and is not a failure.
