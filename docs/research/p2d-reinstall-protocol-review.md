# Independent review: P2D same-version reinstall route

Date: 2026-10-11. Console: CECHA00 NAND. Current reported outcome: the XMB update attempt restarts and displays that the latest system software is already installed and no update is needed. The user reports leaving the save/backup checkbox unchecked. This report does not infer that P2D was installed from that attempt.

**Protocol conclusion: the ordinary physical Safe Mode → option 6 System Update route is supported for a bounded same-version CFW reinstall attempt. No version bump, downgrade, QA change, protection change, or new PUP is justified by this message.** Acceptance and completion of this particular modified PUP remain hardware observations, not facts established by these sources.

**Revised protocol readback: PASS.** Read the entire root-owned [HW001C.md](../candidates/HDD2TB-P2D/HW001C.md) after revision; reviewed SHA-256 `61a4fd7fa6d23abf464b79fc0abfeb1dd92a74ddf2bff7e6e69477dbe1cc6195`. No material scope mismatch was identified. The candidate PUP was also rehashed and remains `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71`. This review did not edit the protocol or firmware artifact.

## Identity and installation boundary

Use the already reviewed P2D candidate only:

- `candidates/HDD2TB-P2D/PS3/UPDATE/PS3UPDAT.PUP`
- 215,764,316 bytes
- SHA-256 `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71`

P1 and P2D both retain version 4.93. The current same-version refusal is consistent with a version admission path; it is not evidence that the diagnostic screen ran or that the candidate's changed `emer_init` was installed. The checkbox state does not establish an installation, checksum, or version change. The working HDD must remain fitted throughout this reinstall and its boot-control verification. Do not advance to the empty Crucial probe merely because the updater recognized version 4.93.

## Primary-source support

[Sony's PS3 Safe Mode instructions](https://www.playstation.com/ja-jp/support/hardware/ps3-safe-mode//) explicitly include the **CECH-A00** family. Its Fat-model sequence uses red standby, rear main-switch off/on, then a first front-power hold through a single beep until shutdown, release, and a second hold released at the double beep. A USB-connected controller and PS button enter the menu. Sony lists system-software update as the sixth item, using storage media; initialization is a separate item. This supports physical entry and menu selection, not Sony endorsement of this custom PUP or a guarantee that it will be accepted.

[Developer aldostools' direct reply to a CECHA00 owner](https://www.psx-place.com/threads/help-with-clean-installation-of-evilnat.37205/post-332055) specifies the same or higher CFW version, checking the PUP hash, and using Recovery Menu → System Update if XMB installation fails. The reply separately discusses destructive restoration, which is not part of this task. This is primary developer guidance for the proposed CFW fallback route, though it predates this 4.93 diagnostic.

[Developer DeViL303's Evilnat reinstall guidance](https://www.psx-place.com/threads/i-installed-hen-on-my-cfw-evilnat-by-mistake.37820/) likewise directs reinstalling the CFW PUP and trying Safe Mode when XMB will not install it. It is supporting developer guidance, not a test of P2D.

[Developer Coro's firmware installation guide](https://www.psx-place.com/threads/guide-to-installing-ps3-firmware-and-link-repo.32933/), cited by the revised actual protocol, was read in full. Its first post recommends Safe Mode when XMB refuses, checks the copied USB file, uses the direct USB port nearest the disc drive, removes game discs, and describes START+SELECT update search. Those points support the revised procedure. Its separate workaround and downgrade sections are not adopted by this protocol.

[Evilnat's release post](https://www.psx-place.com/threads/4-93-evilnat-w-cobra-v8-5-cex-pex-d-pex.39743/) documents that its software “Toggle Recovery Mode” tool is **not supported on NAND models**. Therefore do not replace the physical-button procedure with that CFW menu tool. A developer reply by Joonie in the same long-running thread says NAND models need recovery for a same-version HFW install; that is additional context, not direct proof of P2D acceptance. The thread retains older dated replies under its updated release title.

[Sony's current system-software page](https://www.playstation.com/en-us/support/hardware/ps3/system-software/) separately documents FAT32 USB layout `PS3/UPDATE/PS3UPDAT.PUP` and following the console's reinstallation instructions. It does not document CFW same-version acceptance. Do not obtain a replacement official PUP from that page for this experiment; it is cited only for the storage layout and general reinstall workflow.

## Review requirements for the updated HW001C procedure

The proposed procedure fits this scope if it preserves all of the following:

1. Verify the actual USB copy against the pinned P2D SHA-256. Keep the working HDD fitted, the empty Crucial aside, and the preserved data/backup protected.
2. Leave the stationary refusal through its normal Back/exit control, then shut down normally. Do not force off a copying, installing, or other active update operation. The Fat-model rear-switch preparation is performed only after shutdown/red standby. AC and rear power must be available again for physical Safe Mode entry.
3. Describe **two separate front-power holds with a release between them**. The first ends when the console shuts itself off; the second ends at the rapid double beep. Do not use PS4/PS5's shorter one-hold entry instructions.
4. Connect a controller with a USB cable that carries data and press PS. Select **6. System Update only**. Do not choose Restore PS3 System, default restoration, filesystem repair, database reconstruction, OtherOS tools, Factory Service Mode, QA/protection toggles, or an internet update.
5. Allow the ordinary update-data prompt and its requested simultaneous START+SELECT **only during this menu-6 installation phase on the working HDD**. Capture the wording and required version if it differs from expectation. A format/initialize/data-deletion prompt on the working HDD is a stop, even if it also mentions those buttons.
6. If Safe Mode rejects the same-version candidate, reports corruption, requests a different version, or produces an unrecognized destructive prompt, stop and preserve the exact screen/code. Do not turn that refusal into a request for a different firmware or a protection workaround.
7. Let a recognized update complete without interruption, then verify the working HDD reaches XMB. Only after this successful installation/control stage does the prior empty-Crucial diagnostic procedure resume.

These are review criteria for the root-owned protocol, not authorization for a separate installation workflow or an assertion that updates cannot affect existing data.

## START+SELECT prompts are distinguished by meaning and phase

The pinned original `analysis/coreos/emer_init.elf` provides direct static confirmation that START+SELECT appears in distinct flows. At ELF offset `0xb1a20`, VA `0xc1a20`, the English text requests storage media containing update data of a specified version or later and a simultaneous press. At ELF offset `0xb2e98`, VA `0xc2e98`, a different English text explicitly warns that the system-storage system partition will be formatted, data may be deleted, and both buttons must be held for at least five seconds. The file SHA-256 remains `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`.

Therefore the blanket instruction “never press START+SELECT” would incorrectly obstruct the normal menu-6 update-data prompt. The correct restriction is contextual: normal update prompt on the working HDD may proceed; formatting or initializing that working HDD may not. During the later Crucial observation, the five-second formatting warning remains an unexpected result and a stop. P2D still uses the original 1536 GiB gate and has no independent universal disk-write inhibitor.

## Remaining evidence boundary

This review establishes that the revised physical recovery route and menu selection agree with Sony and CFW-developer documentation. It does not prove P2D's Safe Mode installation, which ROS bank will become active, the runtime diagnostic screen, native 2 TB admission, full-capacity I/O, repair, or durability. The artifact and its prior static/crypto reviews are unchanged. Record any subsequent hardware outcome separately.

## Actual revised procedure: final readback findings

The readback confirms an explicit USB-copy hash recheck; working-HDD installation/control before any Crucial swap; normal exit from the stationary refusal; red standby and the Fat-model rear-switch preparation; two distinct front-power holds; a USB data cable and PS button; and option 6 only. It explicitly forbids QA/update-protection changes and interruption of an update. Another version refusal, corruption/error screen, or any initialization/format request for the working HDD stops the attempt.

The working-HDD option-6 START+SELECT **update-search** prompt is expressly permitted. The later Crucial **five-second format warning** remains a stop. Initial simple acceptance is confined to the empty Crucial, with its possible initialization consequence stated. Unexpectedly active progress is handled without a power cut. A missing marker, different capacity, blank screen, error, or reboot is recorded as an outcome rather than used to justify retries or claim successful P2D execution. The protocol correctly preserves conditional stock-gate behavior and makes no native 2 TB reliability claim.
