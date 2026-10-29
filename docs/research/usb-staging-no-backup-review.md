# USB staging: independent no-backup revision review

Date: 2026-10-11. **PASS: the revised helper implements the user's instruction not to back up firmware found on F:.** No blocking issue was found in this bounded static review.

Reviewed file: `tools/Stage-ReviewedFirmware.ps1`.
SHA-256: `cd010f539c4997d1ac25672c744e606724e93f128b2679028673ae84a838cb6e`.
PowerShell's AST parser reports no errors. The reviewer did not execute the helper, interact with F:, probe any physical drive, rebuild firmware or edit the earlier review.

The previous backup variable, backup-directory creation, copy-from-existing-USB-firmware block and `PreviousBackup` receipt field are removed. The helper never copies existing F: firmware to a workspace file, another USB file or any other backup destination. It reads the existing target only for its hash/concurrent-change checks; `PreviousSHA256` is metadata, not a content backup.

The copy input is the reviewed candidate under the workspace's `candidates` directory. A differing target is replaced only after this new candidate is copied to a uniquely named temporary file inside `F:\PS3\UPDATE`, flushed, closed and hash-verified. `Move-Item` then moves that new temporary file over `F:\PS3\UPDATE\PS3UPDAT.PUP`. There is no preservation copy of the replaced content. A matching target skips all USB mutation steps.

The following protections remain intact:

- Explicit release approval; matching live candidate/source/manifest identities, size and SHA-256; pinned software/protocol review hashes.
- Fixed F: destination; FAT32/MBR/USB, writable/online and nonboot/nonsystem checks; reparse-point refusal and repeated per-run target-identity checks.
- Temporary-file `CreateNew`, source and temporary-file hash checks, and refusal if the existing target changes concurrently.
- Fresh final destination hash/length readback and workspace JSON receipts. The new receipt explicitly records `BackupCreated=false` and `ConsoleInstallationProven=false`.
- No formatting, partition changes, raw physical-drive access or flash writer.

Only the workspace receipt directory was inspected for historical output: `observations/USB-staging` contains the initial inventory, one timestamped receipt and `latest.json`, all ordinary JSON files. No backup file/directory was present there. This is a bounded directory observation, not a claim that unrelated backup files were searched or removed elsewhere.

The earlier `research/usb-staging-review.md` is preserved unchanged (SHA-256 `76babec9f58ac05992136d77430aeb80a5172137f37b23e17a54db9087d77024`) as a review of the superseded backup-enabled implementation. Active release instructions now state the no-backup policy; live script/review hash references should identify this revision.

This revision was reviewed statically; the replacement branch was not exercised. A final helper receipt can establish file presence at its recorded time, but cannot establish console installation or power-loss-safe FAT32 replacement. The current candidate and hardware experiment scope remain unchanged.
