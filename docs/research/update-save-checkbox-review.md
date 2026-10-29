# Update checkbox: bounded local review

The local updater resources support the interpretation that **Save Update Data on System Storage retains an update-data copy on the currently fitted internal drive for later selection/deletion**. Nothing found in this bounded review makes it a larger-drive compatibility setting. Unchecking it for P1 did not prevent P1 CoreOS from being installed in the NAND bank identified by the later dump. A saved file on the working HDD would not move onto the empty Crucial when the drives are exchanged.

This is a local resource/string inspection, not a complete reverse engineering of all updater branches. The parent separately investigated external primary-author documentation. This report does not independently prove an exact persistent cache pathname.

## Verified from the supplied firmware

The English text block of `analysis/flash/dev_flash/vsh/resource/software_update_plugin.rco` starts at file offset `0x4414`, is zlib-compressed and decodes to 7,684 bytes of UTF-16BE text. RCO SHA-256: `c51466649184db696c8073849c7440e58d537d49ae549805fc2e33476b759673`.

The decoded resource explicitly distinguishes these actions:

| Resource key | Exact English text, excluding terminal NUL |
|---|---|
| `msg_tool_save_updatedata_hdd` | Save Update Data on System Storage |
| `msg_tool_update_via_hdd` | ★ Update via System Storage |
| `msg_tool_delete_updatedata_hdd` | ★ Delete Update Data on System Storage |
| `msg_tool_save_updatedata_install_version_variable_ask` | Do you want to save the update data on the system storage?\nThe update data can be installed on the system software of version %1 or later. |
| `msg_tool_error_updatedata_item_exceeded_delete` | %1 items of update data have already been saved on the system storage.\nTo save the update data newly, you must delete saved update data. |

The RCO contains `checkbox_save_updater_select_list` with initialization handler `onInitCheckboxUpdaterSelectList` and button handler `onPushButtonUpdaterSelectList`. A separate `checkbox_swu_auto_power_off` exists; the save option is not that separate automatic-shutdown option.

The extracted `software_update_plugin.sprx` decodes to ELF SHA-256 `af5f1ab2eb0642f460a11b99ee60bd3060e4f792bed3a493c34082ef24f6a22a` (SELF SHA-256 `fc124adeca85d488b730b207cea2ad0e3f24f059a568e1aa6b67add951a1820d`). Its string data contains the same checkbox and save-message keys, plus path components `/updater`, `/push`, `/PS3UPDAT.TMP`, `/PS3UPDAT.PUP`, `/updater_file_path.txt`, `/dev_hdd0` and `/dev_hdd1`. It also contains full temporary/staging paths such as `/dev_hdd1/PS3UPDATE/pup_data.txt` and `/dev_hdd1/PS3UPDATE/resource.txt`.

These path strings show that the updater has several HDD and staging locations. They do **not**, without tracing their callers and concatenation, prove that every such location is controlled by this checkbox or establish the final numbered saved-update folder. In particular, this local review does not conflate the full `/dev_hdd1/PS3UPDATE/...` staging paths with a persistent saved-update catalog.

## Implication for this project's evidence

The separate installed-bank audit in `research/hw001b-independent-review.md` already showed that the NAND header-declared selected ROS1 CoreOS is byte-identical to P1, including the modified `emer_init.self` and decoded P1 gate. That evidence establishes installed bytes; it does not establish which bank/path actually executed at the earlier Crucial refusal. The unchecked-save observation therefore does not explain a failure to install P1, and does not close the unresolved execution-path question.

For P2D, keeping the checkbox unchecked preserves the P1 update procedure as closely as possible. Checking it would be expected to add retained update data on the working HDD; no local evidence indicates that it changes the P2D code bytes or the capacity threshold in NAND. If it was already checked, record that fact rather than reinstalling solely to change the checkbox. The P2D marker and displayed capacity remain the relevant next runtime observation.

No updater runtime was exercised. No candidate, protocol, source firmware, P1 image, NAND dump or physical disk was modified. Own artifacts are `analysis/update-checkbox-review/software_update_plugin.elf`, `software_update_plugin.rco.xml`, `english-text.json`, `selected-plugin-strings.json` and the read-only resource inspection script `inspect_resources.py`.
