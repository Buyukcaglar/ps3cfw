# 2 TB SSD on a launch PS3 (CECHA00): user guide

Firmware **HDD2TB-P13 (v1.0)**, accepted 2026-10-29. Long-term soak (M6) runs until
about 2027-01-29; this guide gets its final update after that.

This guide is for using the setup. The project history and technical evidence are in
`docs/TECHNICAL.md`, `docs/STATUS.md` and `runs/`.

---

## 1. What this firmware does

Stock PS3 firmware has two limits that stop a 2 TB SSD from working as the internal drive:

* It refuses drives larger than 1.5 TiB (about 1.65 TB).
* Its file-system repair tool (Recovery Mode option 3, and the automatic check after a power
  cut) only gets 32 MB of memory. A 2 TB drive needs about 60 MB, so a repair would fail.

HDD2TB-P13 is Evilnat 4.93 Cobra 8.5 CEX with four system files changed:

* **Drive size limit** raised to 1984 GiB (about 2.13 TB).
* **A kernel limit hit when mounting very large drives** raised, so the drive mounts.
* **Repair tool memory** raised from 32 MB to 128 MB, plus several error-handling fixes in it.
* **A small recorder** that writes a 272-byte memory report (`HDD2TB-P8.bin`) to the USB stick
  in the rightmost port whenever a full repair runs. It does nothing when no stick is present.

Everything else is unchanged Evilnat 4.93 Cobra 8.5 CEX.

## 2. Requirements

| Item | Requirement |
|---|---|
| Console | **CECHA00 only** (launch 60 GB "fat" model with NAND flash). Never install on any other model. |
| Current firmware | Evilnat 4.93 Cobra 8.5 CEX already installed. Never install over official (OFW) or hybrid (HFW) firmware. |
| Drive | 2 TB-class SATA SSD with **512-byte sectors**, at most 2,130,303,778,816 bytes. |
| Tested drives | Lexar NQ100 2TB (in daily use), PNY 2TB SATA SSD, Crucial BX500 2TB (CT2000BX500SSD1). |
| Not supported | Drives larger than 2 TB, drives with 4K-native sectors. |
| Also needed | A FAT32 USB stick. For data moves and backups: a Windows PC and a SATA-to-USB adapter. |

Other 2 TB SSDs with 512-byte sectors will probably work but have not been tested.

## 3. The files

| File | What it is |
|---|---|
| HDD2TB-P13 `PS3UPDAT.PUP` | The firmware. 215,765,852 bytes, SHA-256 `652c0c0312cd51283473e653df6e2cdfd874a674f6fb7e83979c45d28fed066d` |
| Evilnat 4.93 Cobra 8.5 CEX `PS3UPDAT.PUP` | Unmodified baseline, for going back (section 10). 215,764,316 bytes, SHA-256 `ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a` (MD5 `D3AF31CE6BDBC6790A5504CF8B3DA1B2`) |

**Download P13** from the releases page of github.com/Buyukcaglar/ps3cfw (release 26.10.29,
file `PS3UPDAT.PUP`). The baseline is Evilnat's own file and is not redistributed there; you
already have it installed. In the owner's working copy the two files are
`firmware/HDD2TB-P13/PS3/UPDATE/PS3UPDAT.PUP` and
`firmware/baseline-evilnat-4.93-cex/PS3/UPDATE/PS3UPDAT.PUP`. The changes themselves are
documented in `docs/TECHNICAL.md` and `src/`.

To check a copy: `certutil -hashfile PS3UPDAT.PUP SHA256` in a Windows command prompt.
In the owner's working copy, `python tools/verify_build.py` also rebuilds P13 and compares it
byte for byte; it needs build inputs that are not published.

## 4. Recovery Mode

Installing and repairing both go through Recovery Mode.

1. Shut the console down to standby (red light). Switch the rear main power switch off and
   on again.
2. Touch and hold the front power button. Keep holding through the beep at about 5 seconds;
   the console switches itself off at about 10 seconds. Release.
3. Touch and hold the power button again. Keep holding through the beep at about 5 seconds,
   and release at the quick double beep at about 7 seconds.
4. Connect the controller with a USB cable, in a port other than the rightmost one, and
   press the PS button.

This is the CECH-A00 sequence from Sony's support page (playstation.com, "PS3 safe mode").

The menu has six options. **Only ever use 3 and 6:**

| Option | Use it? |
|---|---|
| 1 Restart System | harmless, leaves the menu |
| 2 Restore Default Settings | not needed (resets settings) |
| **3 Restore File System** | **yes**: checks and repairs the drive, keeps your data |
| 4 Rebuild Database | no: rebuilds the XMB database and can lose some data |
| 5 Restore PS3 System | **never**: formats the drive and erases everything |
| **6 System Update** | **yes**: installs the firmware from the USB stick |

## 5. Installing or reinstalling the firmware

1. Copy the P13 file to the stick as `PS3\UPDATE\PS3UPDAT.PUP`. With the stick in the PC,
   `python tools/stage_usb.py --drive X: --eject` does this. It checks the source, re-reads
   the copy from the stick and ejects it.
2. Shut the PS3 down to standby. Put the stick in the **rightmost** front USB port.
3. Recovery Mode (section 4), option **6 System Update**, confirm once. Do not interrupt it.
4. The console restarts to the XMB. Check *Settings > System Settings > System Information*:
   version 4.93, and free space unchanged.
5. If webMAN disappeared, reinstall it from its `.pkg` with the Package Manager.

Optional proof that P13 is what got installed: `python tools/check_installed.py --host <webMAN IP>`
should print PASS.

## 6. Fitting a new 2 TB drive

A new drive starts empty. Games, saves, users and webMAN stay on the old drive until you
copy them across (step 7).

1. Install P13 first (section 5), with the current drive still fitted.
2. Shut down normally, switch off the rear main power switch, and swap the drive.
3. Switch on and power up. The console offers to format the new drive. Accept the format
   and its confirmation. **This is the only time accepting a format is correct, and only
   for a new, empty drive.**
4. After the format, use the restart it asks for. At the XMB, *System Information* should
   show about 1658 GB free of 1863 GB (PNY, Crucial) or 1698 GB free of 1907 GB (Lexar).
5. If the console asks for update data, give it the stick with **P13**, never an official
   Sony update.
6. Reinstall webMAN and any other homebrew from their `.pkg` files.
7. To copy your data from the old drive (or from an image of it): use the **PS3HDDTool**
   fork on a PC (github.com/Buyukcaglar/PS3HDDTool). It copies at file level onto the freshly
   formatted drive and verifies every file. It needs your console's 48-byte `eid_root_key`,
   which is unique to the console. Keep it private (the owner keeps it in `vault/`, which is
   never published).
   * This is how the Lexar was filled on 2026-10-14/15: 331,755 files, 830 GB, all verified.
   * Sony's own Backup Utility has not been tested with this setup.

When connecting a PS3 drive to a Windows PC, **cancel** any "initialize disk" or format prompt.

## 7. Everyday use and maintenance

* **Use the console normally.** Shut down with *Users > Turn Off System* or by holding the
  power button until it beeps.
* **After a power cut** the console shows "The system was not turned off properly", then offers
  to restart and check the file system. **Accept (X / OK) both.** On the full Lexar the check
  took about 3 minutes. This route was tested on 2026-10-29.
* **Monthly check during the soak (until about January 2027).** Recovery Mode option 3,
  then start one game. Steps: `docs/checklists/M6-MONTHLY.md`.
* **The USB stick in the rightmost port.** During each full repair the firmware writes
  `HDD2TB-P8.bin` to it. It never overwrites an existing report, so after a check move or
  rename the file if you want the next report.
* **Free space after deleting files is fully usable.** The PS3 does not send TRIM to the
  SSD; that only affects write speed (section 8), not capacity.
* **Keep at least ~60 GB free.** The fullest state that was tested and repaired was 66 GB free.

## 8. Performance to expect

* **Loading (reads): about 60 MB/s sequential and under 1 ms per small random read.** The
  console sets this limit, not the SSD, so a faster SSD will not load faster.
* **Installing (writes): about 29 MB/s for the first ~25 GB after the console has been idle,
  then about 12 MB/s.** The slowdown happens inside the SSD. It recovers after a few hours
  without heavy writing. Most single game installs stay within the fast part.

Details: `docs/research/PERF001/ANALYSIS-20261029.md`.

## 9. Never do these

* Never choose **Restore PS3 System** (Recovery option 5 or *System Settings > Restore PS3
  System*) or **Format Utility**. Both erase the drive.
* Never install an **official Sony update**. It removes the custom firmware and the 2 TB
  support, and the drive is then refused.
* Never install P13 on any model other than CECHA00, or over non-Evilnat firmware.
* Never interrupt a firmware update or a file-system check, and never cut power during one.
* Never let Windows initialize or format a PS3 drive.
* Never share your console's keys, NAND backups or drive images (`vault/` in the owner's
  copy). They are unique to the console.

## 10. Going back to stock Evilnat 4.93

Stock firmware refuses the 2 TB drive and will offer to format it. **Never accept that offer.**
To go back:

1. Shut down and fit a drive of 1.5 TB or less (for example the original 1 TB drive).
2. Install the baseline file (section 3) with Recovery Mode option 6, the same way as section 5.
3. The 2 TB drive keeps its data. Stock firmware just cannot use it. Reinstall P13 to use it again.

## 11. If the console no longer starts

A failed firmware install on this NAND model can leave the console unable to start. The fix
needs a hardware NAND flasher and a NAND backup of **this** console.

* Make a NAND backup before installing anything. If a backup was taken while a different
  build was installed (the owner's backups from 2026-10-11 hold early test firmware),
  reinstall P13 with Recovery Mode option 6 after restoring it.
* **Recommended: make a fresh backup once P13 is installed:**
  1. Move any old `FLASH-NAND-FW4.93.bin` off the stick.
  2. Put the stick in the console, then in the XMB choose *Network > Custom Firmware Tools >
     Dump Tools > Dump Flash*.
  3. The result is `FLASH-NAND-FW4.93.bin`, exactly 268,435,456 bytes, on the stick.
  4. Store it on the PC next to the other NAND backups, under a new name. Never share it.

## 12. Known limits and what was not tested

* Only 2 TB-class drives. Larger drives need further firmware work.
* Power loss was tested only at an idle XMB, not during heavy writing.
* Repair on a nearly full drive (66 GB free) completed without errors. Its exact memory peak could
  not be measured (at least 64 MB of the 128 MB available).
* Months-long behavior is being checked by the soak until about January 2027.

Use at your own risk: a corrupted firmware install can brick the console, and only a NAND
backup and flasher can recover it.
