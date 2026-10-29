# Independent review of reviewed-firmware USB staging

Date: 2026-10-11. **PASS: no blocking issue found in the bounded staging implementation for the current reviewed P2D candidate.** This was a read-only source/evidence review. The reviewer did not execute the helper, rebuild firmware, query physical drives or write to F:.

Reviewed helper: `tools/Stage-ReviewedFirmware.ps1`, SHA-256 `6202056a17ac3fe386893276611b9701226b1a852f47fbf83b7848e663edf425`. PowerShell's AST parser reports no syntax errors; parsing did not execute the script. This review applies to those exact script bytes.

The user's project instruction authorizes automatically staging each reviewed prepared candidate at `F:\PS3\UPDATE\PS3UPDAT.PUP`, with location/hash verification. The helper performs that regular-file operation and does not authorize or perform console installation.

## Source and review guards

The helper derives the workspace from its own location and takes the current candidate from `plan/STATUS.json`. Candidate IDs are restricted to letters, digits, underscores and hyphens. The source and review paths must agree with the current status. Project paths must resolve inside the project, and existing reparse points are refused.

Staging requires explicit `software_release_approved=true`, matching candidate IDs/hashes in status, software verification and build manifest, the exact pinned build-manifest hash, source size/hash agreement, no false Boolean software gate, and present independent review records. The helper rehashes the review reports, optional protocol revision reviews and current hardware protocol.

For current P2D, this reviewer independently rechecked:

- Candidate SHA-256 `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71` and size 215,764,316 bytes match the actual workspace PUP and its release records.
- All six independent software-review references match their pinned hashes.
- All three protocol-revision review references and the current `HW001C.md` match their pinned hashes.
- The build manifest matches its pinned hash, and explicit software release approval is present. That approval covers the reviewed diagnostic artifact; it does not establish hardware success or stable 2 TB support.

The helper does not rebuild a candidate or derive approval from a file merely appearing in a candidate folder.

## Target and preservation behavior

The destination is fixed to F: and the required PS3 path. The helper obtains the partition backing F:, then its disk; it does not assume that a historical physical disk number still identifies the USB. It requires FAT32, MBR, USB, a writable/online disk, and nonboot/nonsystem status for both disk and partition. Existing reparse points along the destination are refused.

Its per-run target identity combines volume/disk unique IDs, disk/partition numbers and size. Identity is rechecked around staging and before final verification. These guards cannot make removable-device operations transactional against sudden unplugging, but they prevent knowingly proceeding after a detected target change.

If the existing destination hash already matches, the helper skips the whole destination-directory/copy/replace block. It freshly verifies the final target hash and length and writes ordinary receipt files only in the workspace.

If an existing PUP differs, the helper first copies it to a timestamped workspace backup and verifies that backup against the original hash. A backup collision or verification failure stops the operation. It also checks that the destination did not change concurrently before replacement. If no destination existed, it refuses to overwrite a concurrently appearing file.

For a required copy, the helper checks free space, creates a uniquely named temporary file inside the same `UPDATE` directory using `CreateNew`, copies through a write-through stream, flushes and closes it, and hashes both staged copy and source. Only then does it replace the destination through a file-level `Move-Item`. It reopens the final destination for hash and length verification. A pre-replacement failure retains the old destination; a verified workspace backup also exists when replacing a differing PUP. No stronger power-loss/atomic-replacement guarantee is claimed. Failed temporary files may remain; the script does not recursively delete them or other content.

The implementation has no format, partition, disk-initialization, filesystem-conversion, raw physical-drive or firmware-flash writer. Its mutations are limited to ordinary candidate/temp files under the fixed USB directory and backups/receipts under workspace `observations/USB-staging/`.

## Saved F: observation and expected current path

Saved inventory: `observations/USB-staging/initial-F-inventory.json`, SHA-256 `5b706072c4e9739f50325e4ab6f7ccc14371b21a67de409ca8a1b64a9fbc45e5`. It records a snapshot at 2026-10-11 14:11:47 UTC:

| Field | Saved observation |
|---|---|
| F: filesystem / drive type | FAT32 / Removable |
| Disk model / bus | SanDisk SanDisk 3.2 Gen1 / USB |
| Disk / partition | 3 / 1 |
| Partition style | MBR |
| Disk and partition boot/system flags | All false |
| Disk read-only/offline flags | Both false |
| Free bytes | 124,645,277,696 |
| Existing firmware path | `F:\PS3\UPDATE\PS3UPDAT.PUP` |
| Existing firmware size | 215,764,316 bytes |
| Existing firmware SHA-256 | `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71` |

Disk 3 in this snapshot is the SanDisk USB, whereas the earlier Crucial probe used that number for a different attached device. The helper's volume-to-disk lookup correctly avoids reusing that earlier identity.

The snapshot's existing PUP is already an exact match, so the expected execution route is `already_matches` with no F: mutation, conditional on the helper's fresh checks. This review does not turn the saved snapshot into a live execution receipt. The parent should run the reviewed helper and retain its final location/hash receipt. The source already passes its regular-file checks; no firmware rebuild is needed.

The backup/copy/replace branch was reviewed statically and was not exercised by this reviewer. Final readback establishes the file present at verification time, not a console installation, successful firmware execution or long-term removable-media durability.
