# Independent review of the saved Crucial ATA / SMART probe

Reviewed 2026-10-11. Scope: regular files in `observations/Crucial-PC-ATA-20261011-160513-777/` only. This reviewer issued no hardware commands. The saved completion time is 2026-10-11 16:05:16 +03:00. These are observations through the PC's USB/SAT path, not observations of the PS3's SATA connection.

## Identity and addressing

`identify.json`, the annotated IDENTIFY words, and the Windows target snapshot agree on capacity and sector size.

| Field | Saved result |
|---|---|
| ATA model | CT2000BX500SSD1 |
| ATA firmware | M6CR091 |
| ATA native serial | 2549E9CEB9DB |
| Windows USB target serial | 474238EE1A62; distinct from the ATA serial |
| Windows target | Disk 3, USB, nonboot, nonsystem |
| User capacity | 3,907,029,168 sectors / 2,000,398,934,016 bytes |
| Logical / physical sector size | 512 / 512 bytes as reported through SAT |
| Last addressable user LBA | 3,907,029,167 |
| Windows partition classification | RAW |

RAW means Windows did not recognize a partition layout; it does not establish that the SSD is empty, zeroed, or free of previous PS3 data. The Windows USB serial and ATA serial must retain their different labels in future target guards and reports.

The annotated ATA IDENTIFY response provides an independent arithmetic check:

- Words 100-103 are `0x88b0:e8e0:0000:0000`, yielding 3,907,029,168 sectors. Multiplication by 512 gives the exact reported byte capacity.
- Word 83 is `0x7401` and word 86 is `0x8401`; bit 10 advertises/enables the 48-bit addressing command feature. The words 60-61 value `0xffff:0x0fff` is the 28-bit command capacity field, not this drive's total capacity.
- Word 106 is `0x4000`: the sector information is valid and the larger-logical-sector and multiple-logical-sectors-per-physical-sector flags are clear. Words 117-118 being zero therefore do not mean a zero-byte sector. Word 209 is `0x4000`, with valid alignment information and zero offset.

The observed capacity is about 1863.016685 GiB. It exceeds the original 1536 GiB threshold by 351,131,492,352 bytes and is 129,904,844,800 bytes below P1's 1984 GiB threshold. The sector count fits an unsigned 32-bit count and every user LBA fits unsigned 32 bits; this capacity does not itself cross the 2 TiB / 2^32-sector boundary with 512-byte sectors.

Consequently, the saved PC response supplies no evidence for a 4 KiB logical-sector incompatibility or an unsigned 32-bit LBA rollover on this SSD. It does not establish what the PS3 receives, that the installed P1 capacity gate executes on the failed path, or that all intervening signed-width conversions are safe. The reported 6.0 Gb/s SATA speed also describes the PC-side path; it does not establish a PS3 negotiated link speed.

`identify-words.txt` is annotated text, not a binary 512-byte IDENTIFY response. No separate binary-response checksum verification is claimed.

## Query scope and results

`status.json` records three completed queries, all with exit status 0 and `-d sat`. No `sat,12` fallback was used:

```text
-j -i -d sat /dev/pd3
-i --identify=wn -d sat /dev/pd3
-i -H -A -c -l error -l selftest --json=o -d sat /dev/pd3
```

These commands request identity and existing SMART information. They do not request SMART enable/disable changes, a self-test, TRIM, media writes, partition initialization, or formatting. The helper saves ordinary observation files on the PC. The existing SMART state is available and enabled; the probe did not enable it. TRIM support is reported, but no TRIM command was requested.

## SMART interpretation and limits

The device's overall SMART self-assessment reports `PASSED`. Selected database-labeled reallocation, uncorrectable, pending-ECC and SATA CRC attributes have raw values of zero (IDs 5, 187, 196-199); no attribute has a failure flag in this snapshot. The reported current temperature is 30 C. These observations do not qualify the full media, high-LBA access, PS3 formatting, sustained operation, or freedom from future data loss.

The standard SMART Error Log request reports **unsupported**, not an empty error log. This must be preserved despite the separately reported error-logging and general-purpose-logging capability bits. No extended error log was requested, so the result does not settle availability or contents of other logs.

The standard self-test log has revision 1 and count 0: no self-tests are logged. No self-test was started by these commands. The JSON status describes code 0 as `completed without error`, but the included text explicitly allows either a previous successful test or no test ever run. It is therefore incorrect to say that this probe ran or passed a self-test. The short/extended polling estimates (2/10 minutes) are capabilities only.

Attribute names come from smartctl's Crucial/Micron database match. Vendor-specific raw encodings and units have not been independently established from manufacturer documentation:

- ID 202, labeled `Percent_Lifetime_Remain`, is normalized 100, worst 100, threshold 1, raw 0. Raw 0 must not be described as zero percent life remaining, nor should a specific remaining-life percentage be promised from this field alone.
- ID 250, labeled `Read_Error_Retry_Rate`, is normalized 100, raw 5. This does not establish five uncorrectable media errors.
- ID 174 reports raw 17 under `Unexpect_Power_Loss_Ct`; the snapshot cannot attribute those events to particular PS3 attempts or the current PC session.
- ID 9 has raw 0 under `Power_On_Hours`; this does not establish a new or unused drive. ID 12 reports raw 23 under `Power_Cycle_Count`.
- ID 246 has raw 3176 under `Total_LBAs_Written`. Do not convert this to a host-written byte total without validating the vendor's unit and encoding. Unknown vendor attributes remain unknown.

## Consequence for the firmware investigation

The observed native capacity matches the previously modeled decimal-2-TB geometry input and lies inside P1's intended admission range. There is no new evidence here for a sector-size patch, a reduced-capacity workaround, or a SMART-setting change. The next decisive evidence remains the installed firmware/gate identity and the exact post-confirmation failure path. Successful PC identity queries and a device-reported SMART pass do not identify that PS3 failure or establish stable 2 TB support.

## Evidence integrity

SHA-256 values of the saved regular files reviewed:

| File | SHA-256 |
|---|---|
| identify.json | d81ab6b1ddafee4837fd6e35972e0125e552636cc8204f82f58648347835a9d2 |
| identify-words.txt | 375bcd7fa785189fafc523e631af48e375b51164b8be7279957c1c2c6fcebed2 |
| health.json | 305750165f069c2da9c533d67259bad1d6cc3a2886d1d1882715e32f24329f6c |
| status.json | 85e2287d3b2aec9c17ad1278ab1b0c678f998dcf34f0bd72abc1c538eb819b22 |
| windows-target.json | 94b8168c2918546453a6e8d50a49c28386fe8ef88013c64667512d3433bd274a |
