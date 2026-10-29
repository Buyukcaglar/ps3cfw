# HW001B NAND dump protocol review

Purpose: collect the CECHA00's installed flash contents after successful P1 installation/control-drive boot, so that the installed ROS/`emer_init` bytes can be checked on the host. This step does not install or patch firmware. It does create ordinary dump files on HDD and USB.

## Exact supplied menu

The supplied firmware's `analysis/flash/dev_flash/vsh/resource/explore/xmb/category_network.xml` establishes this path:

**Network → ★ Custom Firmware Tools → Dump Tools → Dump Flash**

Evidence: Network root queries `#seg_cfw_settings` (lines 10–15); that view queries `#seg_settings_menu` (line 130); its Dump Tools entry queries `#seg_dump_tools` (line 208); the latter contains the `dump_flash` item (line 1679), whose attributes specify `module_name=xai_plugin` and `module_action=dump_flash` (lines 1572–1579).

The displayed English labels were also read directly from the supplied `explore_plugin_full.rco`: its English compressed text block at file offset `0x39154` decodes to `★ Custom Firmware Tools`, `Dump Tools`, and `Dump Flash`, with description `Dumps NOR/NAND Flash to dev_hdd0/tmp or /dev_usb` followed by icon glyphs. The supplied `xai_plugin.rco` English block at `0x9e78` contains success text `%s Flash dumped to\n\t\t%s`.

RCO inspection used `rcomage dump ... - --resdir -` for structure and in-memory zlib/UTF-16BE decoding for text. No RCO extraction or resource writes were needed.

## Pinned source behavior

Pinned local source revision: `tools/xai_plugin_source` HEAD `7c444b70759836b5fa1c9895b0788545e9b214ce`. The dispatcher in `xai_plugin/prx.cpp:838` calls `dumpFlash()` for action `dump_flash`. Its implementation is `xai_plugin/cex2dex.cpp:505–730`.

For NAND, that implementation:

- Selects flash device `0x0100000000000001`, total output target `0x10000000` bytes = **268,435,456 bytes / 256 MiB**. It checks that LV1 CFW peek access is available.
- Obtains the platform version and formats filename from `NAND_DUMP` in `cfw_settings.h:47`: `FLASH-NAND-FW%X.%X%X.bin`, normally **`FLASH-NAND-FW4.93.bin`** for version 4.93. The name is derived from the platform call; the name alone cannot establish which code bytes are installed.
- Creates/truncates `/dev_hdd0/tmp/<filename>` using `CELL_FS_O_CREAT | CELL_FS_O_TRUNC | CELL_FS_O_RDWR`, then writes the dump there. Even with a USB destination, HDD temporary space is required.
- Reads the flash storage device with `lv2_storage_read`, which maps to syscall **602**, in 16-sector / 8192-byte chunks starting at sector zero, with flags `0x22`.
- For NAND, places the storage-read stream beginning at output offset `0x40000`; reads SYSROM through `lv1_peek` (syscall 8) and inserts copies at output offsets `0` and `0xF000000`. It synthesizes `0xFF` bytes in the ranges beginning at `0xEFC0000` and `0xF040000`, with the latter extending to `0x10000000`.
- Searches mounted `/dev_usb000` through `/dev_usb126` and selects the first one that exists. If found, creates/truncates `/dev_usbNNN/<filename>`, copies the output in 256 KiB chunks, then removes the HDD temporary file after the USB copy path succeeds. With no USB found, it keeps the HDD file.
- Reports the destination and emits a single beep on success. The error path closes handles, removes dump output files it finds and emits three beeps. The source does not provide robust independent verification of every short read/write count; host validation remains necessary.

The reviewed source function contains **no flash-storage write call, LV1 poke, writable flash mount, or firmware installer call**. The flash-facing operations in that source path are reads. Its filesystem operations write, truncate and delete regular output files; the action dispatcher also logs the selected action through `log_function`. Calling this operation “fully read-only on the HDD/USB” would therefore be incorrect.

This is a software/logical NAND dump with reconstructed SYSROM/padding areas. It is not established as an untouched physical NAND-chip image with raw spare/ECC data, or as a fully validated hardware recovery backup.

## Source versus supplied binary boundary

The menu/action identity is verified against the actual supplied XML/RCO. The storage-read/output-file behavior above is verified against the pinned **source**, not a completed disassembly of the supplied xai module. The supplied `xai_plugin.sprx` and the source checkout's prebuilt `xai_plugin.sprx` have different SHA-256 hashes; that difference alone does not determine the cause or semantic differences. This review must not be cited as proof that every instruction of the supplied binary is identical to the source implementation.

| Input | SHA-256 |
|---|---|
| Supplied `category_network.xml` | `0f7e9c94fcdd36ccc4670672df5970b34ae51c816a554830a45f00fe64ca5009` |
| Supplied `explore_plugin_full.rco` | `43c41041ef3fe26b99b3beda9a6cf28d5e7c8ce423d3424f18f7c30fb17dd3cc` |
| Supplied `xai_plugin.rco` | `da9043e3260ae2bb37151165c75c85fc6cfd600ebc97c8d6c33476adb3b287e5` |
| Supplied `xai_plugin.sprx` | `6f4375be005791d1b6d8f4999f5baaeddaffb1794a300fb119dc67d937e17294` |
| Pinned checkout prebuilt `xai_plugin.sprx` | `f538ed2eb080c97a83c5b9ad04f5de7459baaa2822b47fb1b03d3be411029fc7` |

## Concrete collection protocol

1. Boot the already installed P1 using the known working control HDD; leave the rejected 2 TB drive out of this collection step. Connect a PS3-readable USB drive with at least 256 MiB free, and ensure at least that much is free on HDD for the temporary file. Use one USB storage device so the destination is unambiguous. Preserve an existing same-named dump elsewhere first, since this function truncates that filename.
2. Open **Network → ★ Custom Firmware Tools → Dump Tools → Dump Flash**. Let the operation finish and record the success destination, or the exact failure message/beeps. Do not select any flash-writing or conversion action.
3. After completion, copy the dump from the USB root to the project's host-side evidence intake without editing it. Expected NAND size is exactly **268,435,456 bytes**. If no USB destination was selected, the success message points to `/dev_hdd0/tmp/<filename>` instead.
4. On the host, preserve the original capture, record SHA-256 and console/version context, then inspect both ROS candidates and embedded `emer_init` signatures/threshold bytes. A successful dump notification and matching file size are collection checks; the dump must still be parsed and matched before drawing any conclusion about which P1 code is installed or executing.

The dump contains console-specific flash data. Its role here is private local evidence for installed-byte verification; no publication or flashing of the captured image is part of HW001B.
