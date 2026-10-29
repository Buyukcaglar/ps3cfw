# P2D same-version refusal: bounded local review

The reported post-restart screen is consistent with updater version-admission behavior: P1 and P2D both declare **4.93**, and the unchanged downstream updater contains the `msg_update_latest_ver` resource key. The ordinary **Recovery/Safe Mode → System Update** path is a justified supported retry for a same-version reinstall, subject to the parent's separately verified procedure. Local static evidence does not guarantee that this exact candidate will be accepted on this console.

No version spoof, downgrade, rebuild, QA change or update-protection patch is justified by this observation. The visible save-update checkbox is not evidence that a QA change is needed. Its separate update-data retention purpose is covered by `research/update-save-checkbox-review.md`.

## Verified local identities

`analysis/p2d-install-review/inspect_install_scope.py` freshly reads the source, P1 and P2D PUPs and checks their pinned SHA-256 hashes. All three have byte-identical version entry `0x100`, update flags entry `0x103`, `ps3swu.self` entry `0x200`, and `ps3swu2.self` entry `0x601`:

| Field | All three images |
|---|---|
| Version text | `4.93 Evilnat [CEX]` |
| Update flags | ASCII `0000` plus newline |
| `ps3swu.self` SHA-256 | `4bca6b9d9d50a22a274a3b6fa3047dad178f7060004e18c956cb4a7dc2a696ff` |
| `ps3swu2.self` SHA-256 | `59de130bac3049d6875b9960087fc34922e45d3b5011b3918c2879e3d94f3d16` |

P2D's PUP SHA-256 remains `4852f56f26c30231e0f663cdd9c0be3fe328cf5690fa7fea257297544baacb71`. Its diagnostic patches do not change these version/updater fields.

## Existing same-version and Recovery resources

The supplied `software_update_plugin.rco` English resource has two distinct messages:

- `msg_update_same_version_found_install_ask`: “Update data of the same version as the current system software was found.\nDo you want to install the same version?”
- `msg_update_latest_ver`: “The latest version of the system software is already installed.\nThere is no need to update.”

The source `ps3swu.elf` contains `msg_update_latest_ver` at VA `0x10002030` and in its embedded resource names at VA `0x105cbcac`. It also contains `/dev_hdd1/PS3UPDATE/update_type.txt`. Those facts establish a downstream refusal-message facility and update-route state; this narrow review did not trace the exact condition that selected the user's screen.

The supplied `emer_init.elf` contains the Recovery menu's `System Update` text at VA `0xd24b8`. Its updater-media prompts include:

> Connect storage media that contains update data of version&#xa;%1 or later, and then press the START and SELECT buttons&#xa;at the same time.

The prompt's “or later” language is consistent with permitting the named version itself, rather than requiring a strictly greater version. Together with the explicit same-version confirmation resource, it supports the ordinary reinstall route. These strings alone do not prove every updater entry path accepts every same-version package, nor do they bind that separate media prompt to the exact menu-state branch without a wider trace. The parent's verified Recovery documentation provides the operational procedure.

## What the refusal establishes and what remains missing

The user's account places refusal **after restart**, so the XMB handoff and later updater should be treated separately. The message does not identify whether the intended USB file was actually selected, which specific version/state check refused it, or what flash/state operations preceded that screen. It is not evidence that P2D installed successfully. It also does not prove that every flash byte and update-state field remained unchanged; a new readback was not collected by this review.

The earlier HW001B NAND dump establishes the P1 bytes present at that earlier observation. It does not establish the present post-refusal bank contents. System Information's 4.93 label cannot distinguish P1, source 4.93 and P2D.

A raw hash of the **USB copy** used in this refused attempt is not present in this local inspection. The local candidate hash establishes the workspace file, not the copied USB file. The next attempt should first verify that copy against the P2D SHA-256 above, keep the known working control HDD fitted, and use only the ordinary Recovery menu **System Update** action. The other Recovery menu actions are not required for this retry. Stop and record another refusal rather than altering protections or escalating to arbitrary update/format actions.

After a reported successful reinstall and control-drive XMB boot, the P2D executing-image marker remains the next diagnostic evidence. Until then, do not interpret a Crucial refusal or missing marker as a result from known-installed P2D.

## Artifacts and boundaries

Saved `analysis/p2d-install-review/report.json` contains the payload identities, exact resource text and limits. Two bounded string extracts are saved beside it. Original and candidate PUP hashes were rechecked after inspection. No original, candidate, protocol, NAND dump or physical device was modified. No updater runtime was executed, and no whole-updater acceptance proof is claimed.
