# Independent review of the first 2 TB admission candidate

Review date: 2026-10-11. Scope: the supplied Evilnat 4.93 CEX firmware, CECHA00 NAND console, a disposable native-capacity 2 TB SATA SSD, and one proposed executable change in `emer_init`. This review does not authorize a physical write and did not perform one. Repacking and candidate verification are owned by the main task.

## Finding

There is no concrete boot-logic reason found here that forbids using a **single-immediate capacity-gate change as an admission/format experiment** on a scratch SSD. The two traced callers share the same gate, including startup recovery and Safe Mode. Raising the gate to `0x1f0 << 32` admits ordinary decimal 2 TB devices while continuing to reject a 2 TiB device. It does not fix or qualify the filesystem, repair, SATA negotiation or SSD sector-geometry paths.

The initial experiment must be described as an **unqualified hardware probe**, not a stable 2 TB firmware release. The evidence reviewed here does not establish data-loss-free operation or flash safety.

## Exact proposed semantic change

Input decoded `analysis/coreos/emer_init.elf` SHA-256:

`ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`

At VA `0x46198`, file offset `0x36198`, replace instruction bytes `38 00 01 80` (`li r0,0x180`) with `38 00 01 f0` (`li r0,0x1f0`). Only the last instruction byte changes. The later `sldi r0,r0,32`, unsigned 64-bit comparison and conditional refusal remain as supplied.

| Bound | Bytes | 512-byte sectors | Effect at this gate |
| --- | ---: | ---: | --- |
| Supplied `0x180 << 32` | 1,649,267,441,664 | 3,221,225,472 | Refuses a native decimal 2 TB drive |
| Proposed `0x1f0 << 32` | 2,130,303,778,816 | 4,160,749,568 | Admits normal decimal 2 TB drives |
| Exact 2 TiB | 2,199,023,255,552 | 4,294,967,296 | Still refused by proposed gate |

The proposal is a 1984 GiB admission ceiling, approximately 2.1303 TB decimal. It does not advertise 2 TiB support. A commonly reported 2 TB device size of 2,000,398,934,016 bytes / 3,907,029,168 sectors is below both the proposed gate and 2^32 sectors. Actual device IDENTIFY data remains required; the box label is not sufficient evidence of the size or logical/physical sector geometry.

The relevant low-64-bit capacity product is calculated by `0x43384`, from the information buffer returned by syscall 609, and stored through the output pointer. The gate's refusal log explicitly calls the result bytes. See `binary-review.md` for the provider trace. The `[LV2 syscall table](https://www.psdevwiki.com/ps3/LV2_Functions_and_Syscalls)` documents the information fields used here.

## Boot-device selection and common gate coverage

The selector called at `0x4616c` is `0x4445c`. It calls `0x57c8c`, which calls `0x8b9dc`: syscall 875 / `0x36b`, `sys_ss_get_boot_device`. It is **not** the flash-extension/NAND-vs-NOR syscall 874. On a successful call, `0x57c8c` returns true exactly when the returned 64-bit boot-device value equals 1; otherwise it returns false. On a syscall failure it returns false.

The actual LV2 syscall-table entry for 875 is at low VA `0x365738`, descriptor `0x8000000000338380`, code `0x80000000002265cc`. That implementation queries the hypervisor repository node `sys / flash / boot` with hypercall `0x5b` and copies an eight-byte value to the caller. This confirms the selector's purpose without assigning undocumented numerical boot-device meanings.

The queried GameOS IDs are constructed with `lis r3,0x101`, then `sldi r3,r3,32`, then `ori`:

- Default route: **`0x0101000000000007`**, the internal HDD device.
- Boot-device-equals-1 route: first **`0x0101000000000010`**, publicly labeled `cardctrl_dev_id`, then fallback to the internal HDD if the first query fails.
- All successful capacity queries converge on the **same instruction at `0x46198`**. Thus the patch is not bypassed by selecting the alternate queried device.

The [GameOS device-ID table](https://www.psdevwiki.com/ps3/DeviceID) provides the public names. Neither the selector nor the alternate ID should be described as a NAND-specific branch. The IDs above correct a shortened-ID documentation error in the earlier review; the original disassembly and threshold arithmetic were unaffected.

Only two direct `bl 0x4613c` callers were found in the executable segment by an aligned PPC64 big-endian instruction scan:

1. **Startup/recovery caller at `0x40754`.** A successful query with `supported=false` sets error state at `0x14d1b8` to 8 (`0x40794`) and error code at `0x14d1b4` to -1. The error dispatcher at `0x4117c` reads that state. Jump table VA `0x412fc`, entry 8 at `0x4131c`, is signed relative offset `0x1d4`, leading to `0x414d0`. That path selects TOC `-0x7ca4` -> language table VA `0xe0338`; English element `+4` at `0xe033c` points to VA `0xbc768`, the unsupported-hard-disk message. It joins `0x41350`, then `0x411f4`, and calls display function `0x46e54` at `0x41208`.
2. **Safe Mode caller at `0x4aef8`.** The same result sets state 4 at `0x16e554` and code -1 at `0x16e550`. The handler `0x4c650` selects localized message index `0x18` at `0x4c754`, which resolves to the same English wording, and calls display function `0x46e54`. The earlier binary review contains the message-table trace.

The English message is: “The installed hard disk is not supported.” Its following sentence requires a disk compatible with the system. The trace proves the message reached from this gate, not the identity of an unrecorded error shown on the user's separate 4.91 installation.

“Startup/recovery caller” here means the startup utility path **inside `emer_init`**. This is not a claim that every ordinary XMB boot, including an already valid HDD, must run the gate. Successful `supported=true` returns at both callers continue into later storage probing and preparation. Changing the constant changes this one decision; it does not establish the later decisions succeed.

Evidence windows are saved under `analysis/candidate-review/`:

- `normal-capacity-caller.txt`, `normal-error-dispatch.txt`, `normal-unsupported-ui.txt`
- `capacity-gate.txt`, `safe-mode-capacity-caller.txt`
- `boot-selector-wrapper.txt`, `boot-selector.txt`, `boot-device-syscall.txt`

All the listed `emer_init` addresses map to file offset `VA - 0x10000`. The jump-table and language-pointer observations were read as big-endian integers from the ELF.

## Updaters, duplicate modules and packaging boundaries

Both PUP updater SELFs were decoded independently with the project Python decoder:

| Module | Decoded ELF size | Decoded ELF SHA-256 |
| --- | ---: | --- |
| `ps3swu.self` | 12,067,936 | `f96138b1a1e406195a001c035b9e17a273a1f9f07f4ff576385fec50750a58af` |
| `ps3swu2.self` | 12,067,936 | same; complete ELF byte equality |
| `lv1.self` | 4,130,048 | `dec10390c6617078b693ffd859598ce96e81d8c0de37ae34e4e95d2563f0cef3` |
| `hdd_copy.self` | 867,824 | `3e5a29792a414c92a4e16165e3ca76dfdb6d780b055e46c6455091b8932d01d7` |

Native scetool independently decoded `ps3swu` and `lv1`; those entire outputs matched the Python outputs byte-for-byte (`native-decoder-crosscheck.json`). The different encrypted updater files are not different decoded programs in this PUP.

The two decoded updater programs, `lv1`, and `hdd_copy` were searched for the exact local gate sequence, gate prefix, capacity-refusal string, `emer_init.self` name, and the original `emer_init.self` first 32 bytes. The exact gate sequence and capacity string were present only in the separately decoded `emer_init`; the `emer_init.self` name was present in `lv1` as a name. None of these searches exposed another embedded copy of the capacity gate in the updater programs. All 15 aligned `li *,0x180` updater instances were examined in surrounding disassembly; they were masks, buffer sizes, returned sizes or error construction, not this shifted capacity bound. `hdd_copy` had no such immediate. Saved results: `embedded-copy-scan.json` and `*.0x180-context.txt`.

This is a bounded duplicate search, not exhaustive semantic reconstruction of the 12 MB updater or proof that no distinct capacity check exists anywhere. It supports retaining the supplied updater bytes for the minimal first experiment. It does not support skipping a full installable-container verification.

The local `UPL.xml.pkg` was decrypted read-only to `analysis/candidate-review/UPL.xml`. Its CoreOS entry names `CORE_OS_PACKAGE.pkg`; the XML has no CoreOS hash or size field. With the original filename and version retained, this review finds no XML field that must change for the one-immediate experiment. The manifest lists exactly one such CoreOS package. The [CoreOS format documentation](https://www.psdevwiki.com/ps3/CoreOS) identifies `emer_init.self` as a ROS/flash CoreOS member loaded by LV2; it is not a normal `dev_flash` file to replace over FTP.

A complete candidate requires coherent regeneration/verification of the nested modified SELF, CoreOS image and encrypted package, the matching CoreOS companion in `spkg_hdr.tar`, both enclosing tar entries as applicable, and the PUP entry/header integrity metadata. Replacing a decrypted ELF on the USB stick is not sufficient. Public PUP HMAC success is not a signature or compatibility proof. Positive claims about the rebuilt SELF/PKG/SPKG and applicable Evilnat verifier patches belong to the separate packing audit. The later finished-candidate scope readback is recorded below; it does not approve crypto authentication or installation safety.

## Finished HDD2TB-P1 candidate: independent scope readback

The reviewer read **both PUP files afresh**, without importing `tools/build_hdd2tb_p1.py` or relying on its build manifest, and independently checked the scope of the finished candidate. Readback completed on 2026-10-11.

- Original PUP SHA-256: `ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a`.
- Candidate `candidates/HDD2TB-P1/PS3/UPDATE/PS3UPDAT.PUP` SHA-256: `f7abf409c9f0b6d04b5d9f8f44fb76142363759beb3dd8f060ec1a2dc5400f68`.
- Both complete PUPs are **215,764,316 bytes**. The original was rehashed again after this review, and remained unchanged.
- All **9 top-level entry IDs, their order, extra fields, offsets and lengths** are preserved. All header and entry HMACs pass. Header differences are confined to the HMACs of entries `0x300` and `0x501` and the overall header HMAC. The other **7 entry payloads are byte-identical**, including both updater SELFs and the top-level version/flags material.
- Of the **50 `update_files.tar` members**, only `CORE_OS_PACKAGE.pkg` changes. Its size decreases from 5,521,529 to 5,521,527 bytes; its padded tar extent stays the same. Of the **48 `spkg_hdr.tar` members**, only `CORE_OS_PACKAGE.pkg.spkg_hdr.1` changes, retaining 640 bytes. All other member contents and complete header/padding extents are byte-identical. Member names and order are unchanged. Changed-member headers differ only where permitted for size/checksum. The complete trailing zero suffix of each tar is preserved. Independent Python `tarfile` reads and explicit header checksum calculations pass.
- Both CoreOS packages decrypt to **7,340,000 bytes**. All **25 CoreOS names, offsets and lengths** are identical. All bytes outside the `emer_init.self` extent, including the CoreOS layout table, other 24 members and gaps/padding, are byte-identical. `emer_init.self` remains **546,480 bytes**.
- The freshly extracted original and candidate SELFs were each decoded with **both Python and native scetool**. The two decoders agree on each entire ELF. Both ELFs are **1,266,432 bytes**. The original ELF hash matches the previously analyzed input; the candidate ELF SHA-256 is `113a234147286b0a5874d035aa668376702c7416fb8b532ff536b7fee50b94ff`.
- The **only decoded ELF byte difference** is file offset `0x3619b`, `0x80 -> 0xf0`. This gives the proposed instruction at VA `0x46198` exactly; no LV2, filesystem or additional executable change is hidden in this candidate's extracted CoreOS content.

One wording qualification: the UPL **file bytes** are unchanged inside the unchanged `UPL.xml.pkg` member; its enclosing `update_files.tar` payload changes because that tar also contains CoreOS. No standalone UPL top-level PUP entry exists here.

Reproduce the independent regular-file readback with:

```powershell
python analysis/candidate-review/independent_candidate_scope.py
```

The script writes only into `analysis/candidate-review/`. The detailed comparisons and all nested-member hashes are in `independent-candidate-scope.json`; fresh extracted modules, both decoder outputs and native logs are also retained there. This check uses the reviewed vendor SCE package decoder and the project Python SELF decoder, with native SELF decoding as the independent cross-check. It does not verify ECDSA and does not exercise hardware.

**Scope verdict: pass. No blocking unexplained content difference was found.** This verdict applies only to the exact PUP hash above and the stated byte/layout/integrity properties. It is not a claim of stable storage support, successful flashing, effective installed-CFW signature override, or a successful console test.

The reviewer also read `tools/build_hdd2tb_p1.py`. For the pinned, hash-asserted original input, its PUP parser checks the fixed 9-entry/656-byte header, contiguous non-overlapping payload extents, end-of-file and all public HMACs. Rebuilding preserves the original header template, IDs and extra fields, and reparses the result. Its tar replacement walks bounded 512-byte records, rejects unexpected prefixes and nonzero suffixes, requires one existing target, updates only its length/checksum/content, and compares the resulting semantic member map. Tar paths are dictionary keys here, not filesystem extraction destinations. Its CoreOS writer requires one `emer_init.self`, equal module length and equality before/after that extent. No bounds/repacking defect affecting this candidate was found. This is a known-input research builder relying on active assertions, not a hardened arbitrary-archive service; run without `python -O`. Its cryptographic signing and verifier assumptions are outside this review and remain the separate crypto review's responsibility.

## CECHA00 NAND installation sequence

CECHA00 has NAND flash; its firmware files are not dependent on the replacement SSD's NOR-style virtual-flash installation. The [flash layout](https://www.psdevwiki.com/ps3/Flash) and [CoreOS placement](https://www.psdevwiki.com/ps3/CoreOS) are consistent with the module being installed in console flash. The [ConsoleMods blank-drive instructions](https://consolemods.org/wiki/PS3:Upgrading_your_Storage#Installing_a_Blank_SATA_Drive) distinguish NAND CECHA/B/C/E/G from NOR: NAND normally formats the replacement disk without asking for a firmware reinstall.

Therefore the expected sequence is **install the verified candidate while booted with a working supported scratch drive, confirm candidate boot, power off, then insert the native 2 TB scratch SSD**. The installed flash must contain the patched module before the oversized-drive startup is tested. Merely placing a candidate PUP on USB beside a blank 2 TB SSD while the installed 4.91 flash still contains the old gate does not establish any way past that old gate.

This expected NAND behavior still needs observation on the actual console. If the replacement-drive path unexpectedly asks to reinstall firmware, record the exact prompt and requested version; do not substitute stock firmware, because that would remove the change being tested. If the initial candidate fails to reach a working environment with the small scratch drive, stop before testing the 2 TB SSD.

A firmware installation modifies console flash and may change shared console state even if a production HDD is unplugged. Removing the production disk protects its sectors from this experiment; it does not make an unqualified firmware installation risk-free. A known original CFW PUP plus a validated console-specific flash/key backup supports recovery planning but is not a guarantee of software recovery after a malformed flash update. Do not call a preserved original HDD a guaranteed rollback device across the version change.

## Suggested first hardware-test protocol

Before handing the candidate to the console, the main task should provide exact PUP hashes, original provenance, a manifest of every changed nested member, independent full re-extraction, the one-byte decoded-ELF diff, and affirmative SELF/PKG/SPKG verification. Preserve the supplied PUP. Document how to recognize the installed candidate rather than relying only on “4.93” in System Information, which the original firmware also reports.

1. Record CECHA00 identity, current firmware/kernel mode, working BD/Bluetooth/Wi-Fi condition, and the exact SSD model, firmware, native sector count and logical/physical sector sizes. Save the current console-specific flash/key backups through the established read-only CFW backup procedure and verify the copied files on the PC. Keep private keys out of public reports.
2. Power the console off completely and remove the production HDD. Keep it disconnected throughout the experiment. Use a supported disposable small SATA drive as the candidate-install control; any format applies only to that control drive. Verify the console can boot normally with that control before installing the candidate.
3. Use a known-working USB storage device with the candidate at `PS3/UPDATE/PS3UPDAT.PUP`, as documented by the [PUP installation path](https://www.psdevwiki.com/ps3/Playstation_Update_Package_(PUP)#Installation). Check the file hash after copying. Install through the normal applicable local-update UI and capture the displayed identity and any error. Do not swap the SATA drive during an update.
4. With the small control drive still installed, confirm successful update completion, two clean cold boots, normal XMB use, and access to Safe Mode. Establish candidate identity by the task's chosen verification mechanism. A failed control boot is a candidate installation/package failure and ends the initial experiment.
5. Shut down cleanly, disconnect power, and install one explicitly disposable native-capacity 2 TB SSD. Use its normal SATA connection, without an HPA/DCO cap or sector-translating USB bridge. Start the console and record the entire prompt/error sequence. Accept format only after identifying that the attached device is the disposable SSD. Record timing, freezes, resets and all error codes.
6. If formatting completes and XMB starts, record System Information and, if an already validated read-only diagnostic is available, the console's storage-info sector count and byte size plus partition-region endpoints. “XMB starts” alone is an admission/format result; the native capacity must not be inferred solely from the SSD's model name or free-space number.
7. Copy a small disposable payload with PC-side hashes, read it back and compare. Perform at least two clean cold boots and reconfirm the payload. Inspect Safe Mode access. Any repair check/rebuild should operate only on scratch data and have a separately stated expected result; a successful menu entry is not a successful filesystem check.
8. Stop and preserve observations on refusal, format failure, check failure, missing data or a changed device identity. Do not retry with arbitrary firmware or restore real data to make the result appear successful. Return to the supported control drive only after a full shutdown, then follow the documented recovery plan if necessary.

For a narrow first milestone, report results separately: **candidate installed on control drive; 2 TB admitted; format completed; XMB booted; native capacity observed; clean reboot/hash readback passed; recovery operation result**. No single row establishes the others.

This protocol deliberately avoids induced power loss. High-LBA allocation/readback, full-volume fill, repair correctness and clean flags, backup/restore, normal workload and repeated cold-boot qualification remain later gates. Keeping the original LV2/newfs/fsck for the first probe makes the admission hypothesis testable without claiming those later gates are solved.
