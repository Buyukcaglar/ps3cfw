# P3 composite admission code review

11 October 2026. Exact candidate SHA256: `9197335b04b6cdf8c40393d6375dd6ee77d2f62fc85da5cac0989d012ed00eaa`. Review performed by the primary agent, with a separate read-only parser and native/Python decoding. No separate human or agent review is claimed.

HW001E's photograph visibly shows `HDD2TB-P2D`, CAP `2000398934016 B` and GATE `1649267441664`. This confirms diagnostic execution and the byte capacity consumed on PS3, matching the prior PC measurement. The individual sector-count/sector-size fields are not separately displayed. It does not establish formatting, ordinary-startup callback execution, high-address I/O or stable support. The original photo and SHA256 are preserved in `observations/HW001E/result.json`.

## Exact scope

P3 combines the exact reviewed P1 CoreOS package/companion with a focused change to supplied `sysconf_plugin.sprx`, in `dev_flash_005.tar.aa.2026_01_08_191610`.

| Module | ELF offset / link-time VA | Before | After |
| --- | --- | --- | --- |
| emer_init | `0x36198` / `0x46198` | `38000180` | `380001f0` |
| sysconf_plugin | `0x4e37c` / `0x4e28c` | `39200182` | `392001f0` |
| sysconf_plugin | `0x4e38c` / `0x4e29c` | `65298000` | `65290000` |

Only **three decoded ELF bytes** actually differ across both modules. Emergency code is exact P1; it has no P2D diagnostic edits. The sysconf changes construct `0x1f0 << 32`, **2,130,303,778,816 bytes / 1984 GiB**, replacing `(0x182 << 32) | 0x80000000` /1546 GiB. `oris r9,r9,0` preserves the register while adding no low bits. Query success/failure handling, sector-field loads, 64-bit product, unsigned comparison and less-than-or-equal branch are unchanged. Emergency uses the same threshold and accepts equality. The verified Crucial capacity is below both new ceilings; 2 TiB is above them.

The separate parser decodes the actual final PUP, checks exact before/after instructions and the complete changed-byte lists, and derives the thresholds from those instruction immediates. Its boundary model covers zero, 1 TiB, both original ceilings, the observed Crucial, new ceiling minus one 512-byte sector, equality, plus one sector and 2 TiB. These are offline arithmetic assertions, not PowerPC/console execution tests. The earlier disassembly links the simple format-prompt callback to the sysconf capacity comparison. That runtime path remains an inference from static code and the earlier photographs.

No filesystem geometry, partition/region code, LV1/LV2, reserve policy, checker allocator, localization, version or update executable is changed. Relocation and other PRX segments retain complete plaintext/ciphertext identity. The known 32 MiB full-checker backing/heap requests are untouched; valuable-data migration and repair/durability qualification remain blocked by unresolved engineering work.

## Builder review

`tools/build_hdd2tb_p3.py` imports pinned P1 helper functions without invoking its main writer. P1/P2D/original artifacts remain immutable. Output paths are confined to project analysis/candidate directories and prohibit P1/P2D destinations. The builder has no device, USB-staging or console-flash action.

The PRX first load segment begins at ELF offset `0xf0`, unlike emer_init's offset zero. Focused PRX replacement uses the actual program header and preserves the **240-byte gap between encrypted metadata end and first payload**. The first attempted control correctly failed an overly strict inherited `payload_offset == metadata_end` assertion; accepting `payload_offset >= metadata_end` with exact gap preservation addresses the PRX layout. The successful no-change control reproduces the entire source SELF byte for byte.

Native changed code compression occupies 528,898 bytes within the original 528,976-byte slot; no fallback compression is needed. The focused writer updates only first-section compressed length, matching public segment-size field, section HMAC and complete-ELF SHA1 Digest2. Signature bytes are retained. Complete native/Python decodes agree on the exact target ELF. Flash tar replacement is same-length raw replacement inside the sole named regular member, preserving its header, every other file, directories, gaps and padding. Native no-change PKG reconstruction is byte-identical.

The core component is copied from exact pinned P1 after verifying its only changed CoreOS file is emer_init. Fresh final-PUP auditing independently proves that same decoded one-byte emergency patch and complete outside-module identity; the earlier review is not substituted for this final audit.

## Next hardware boundary

The bounded next test is working-HDD Recovery installation/control boot, then native formatting and first boot of the same empty Crucial, recording all prompts, progress/errors, XMB capacity and one normal reboot. See `candidates/HDD2TB-P3/HW001F.md`. This experiment changes console firmware and intentionally permits formatting only the disposable Crucial. A successful result would establish admission/initial format/boot for this tuple, not full-media I/O, repair, durability or data-loss-free storage.
