# G3a: automatic repair route after a dirty shutdown (PNY) -> PASS (2026-10-29)

## Procedure
P13 installed (G1 PASS), PNY fitted, SanDisk stick in usb000 with no record at the root
(checked over FTP before the check). The owner switched off the rear main power switch at
an idle XMB, waited, powered on.

## Owner report (photos in this folder)
1. `screen1`: "The system was not turned off properly the last time it was used..." -> OK.
2. `screen2`: "The file system on the system storage may be corrupted. This system will
   restart, check the file system and restore it if it is corrupted..." -> OK (X).
3. `screen3`: "Checking and restoring the file system... Do not turn off the system." (82 %).
4. Owner: "Completed successfully". The console restarted to the XMB. The whole route took
   a few minutes (screen 2 at about 12:48, record fetched 12:50 UTC+3).

## Tool verdicts
* `read_observer.py --host <ps3-ip> --save runs/G3a-20261029 --rename-to HDD2TB-G3a.bin`
  -> **PASS**. Record valid (sha256 b0d59d9a...2e), renamed on the stick to `HDD2TB-G3a.bin`.
  * requested budget 134,217,728 B (128 MiB, patched), utility status 0, full worker calls 1,
    argc 3, heap create/delete 1/1, accounting consistent.
  * peak 64,833,712 B (61.83 MiB, 48 % of the arena); largest request 60,981,796 B
    (the PNY bitmap, identical to the earlier PNY measurement); failed allocs 0.
* webMAN `cpursx.ps3`: HDD 1,658.2 GB free (unchanged), uptime 42 s after the restart.

## Conclusion
The automatic check after a dirty shutdown takes the patched route: the 58 MiB bitmap was
allocated inside the 128 MiB budget, which a 32 MiB route could not have done. No P14 needed.
