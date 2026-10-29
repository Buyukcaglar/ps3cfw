# Bounded filesystem binary review

Date: 2026-10-11. Scope: read-only inspection of modules extracted from the supplied Evilnat 4.93 CEX PUP. This review adds filesystem/checker evidence to the root firmware analysis; it does not complete the checker, updater, crypto, or recovery audit. No original firmware file was patched, and no physical disk or console was accessed.

## Reproduction and identity

Five extracted dev_flash inputs were decrypted with the local `tools/scetool_keys/Release/scetool.exe` using the existing local PS3 data directory. Outputs are isolated under `analysis/fs-review/`. The existing `analysis/coreos/emer_init.elf` was inspected read-only. All output hashes are SHA-256:

| Decrypted file | SHA-256 |
| --- | --- |
| `libfs_utility.sprx.elf` | `b4ceceb4f478486f7b98192d1688f05dc91a4ac0234f3468a883a227b0fba297` |
| `libfs_utility_init.sprx.elf` | `6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a` |
| `libfs_utility_full.sprx.elf` | `f519759b800c07059bc563354253c33bdfebb2fdb8387f79cfcc3aa875fe67c3` |
| `libfs_utility2.sprx.elf` | `bfc50fd50d6a79c140d8cc433e7fbfc90aad7b2b7850532525f461d5434c28b1` |
| `sys_init_osd.self.elf` | `70e589b177930515330d72e0d7beafb7998c84f0b6f3408bdb19debf6f337597` |
| `emer_init.elf` | `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d` |

`analysis/fs-review/scan.py` generates `summary.json` and PPC64 big-endian disassembly listings from file-backed executable segments. `xrefs.py` resolves selected exact string pointers through the PRX TOC for the inspected library modules and the entry-descriptor TOC of static executables. Its references are partial: a missing reference is not proof that a string or path is unused. Disassembly also covers read-only data inside executable segments, so only examined instruction sequences are evidence of executable code.

All addresses below are the ELF's link-time virtual addresses; PRX addresses are before runtime relocation. In `libfs_utility.sprx.elf`, the inspected VA maps to file offset VA+`0xf0`; its TOC is `0x3cfc0`. In `libfs_utility_init.sprx.elf`, the inspected VA likewise maps to file offset VA+`0xf0`; its TOC is `0x2e7c0`. For the first load segment of emer_init, file offset is VA-`0x10000`.

## What is directly present

| Module | Directly observed code/string evidence | Scope of conclusion |
| --- | --- | --- |
| `libfs_utility.sprx` | `newfs_cfs started` at `0x2ddc0`, referenced at `0xa00c`; `cannot alloc %u bytes for blockmap` at `0x316a0`, referenced at `0x2bb54`; UFS superblock and checker diagnostics | Both formatting and filesystem-check implementations are present |
| `libfs_utility_full.sprx` | `newfs_cfs started` at `0x14268` with code reference; formatting geometry diagnostics | A separate formatting implementation is present |
| `libfs_utility_init.sprx` | `cannot alloc %u bytes for blockmap` at `0x24f30`, referenced at `0x1fc34`; matching checker arithmetic and allocation sequence | Another checker implementation is present |
| `libfs_utility2.sprx` | Decrypted successfully; sparse relevant strings | No capacity or checker conclusion from this bounded pass |
| `sys_init_osd.self` | `newfs_cfs started` at `0x39100`, referenced at `0x2895c`; format and memory-allocation diagnostics | Boot initialization contains a separate formatting path |
| `emer_init.self` | `newfs_cfs started` at `0xd8530`, referenced at `0x7ad84`; format and memory-container diagnostics | Recovery contains its own formatting/environment code |

Presence of several copies means that updating only one shared filesystem utility is not enough to establish consistent support across boot, initialization, normal operation, and recovery. This review has not yet established which caller selects every copy in the user's exact CECHA00 boot/recovery configuration.

## Direct checker allocation evidence

In `libfs_utility.sprx.elf`:

```text
0x2b534  ld     r11, 0x438(r10)
0x2b53c  std    r11, 0(r26)
...
0x2b6b8  ld     r9, 0(r26)
0x2b6c0  addi   r9, r9, 7
0x2b6c4  sradi  r9, r9, 3
0x2b6c8  addze  r9, r9
0x2b6cc  addi   r9, r9, 1
0x2b6d0  sradi  r9, r9, 1
0x2b6d4  addze  r9, r9
0x2b6d8  slwi   r31, r9, 1
0x2b6dc  mr     r3, r31
0x2b6e0  bl     0x1a638
0x2b6ec  cmpwi  cr7, r3, 0
0x2b6f4  beq    cr7, 0x2bb54
```

The selected superblock layout agrees with the older upstream UFS2 `fs_size` field at `0x438`; the 64-bit load is direct binary evidence. For a positive fragment count `N` in the relevant range, the request is the even-byte rounding of `ceil(N/8)`, stored in a 32-bit result by `slwi`. The allocation failure target loads the exact blockmap diagnostic, reports the request, and goes to a failure path. [Upstream structure comparison](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/5.5/sys/ufs/ffs/fs.h).

The called wrapper at `0x1a638` is calloc-like: it multiplies two arguments using `mullw`, zero-extends the 32-bit product, calls `0x1a634`/`0x1a600`, and clears the returned area on success. `0x1a600` loads an allocator handle through a TOC global and calls an imported function. The exact imported allocator identity, all heap creation callers, and real available bytes were not fully traced in this pass. The allocation API width is therefore a separate item to audit even though a 2 TB bitmap is far below 4 GiB.

The checker also allocates a cylinder-group summary (`fs_cssize`, load at `0x2b5bc`), an array using `fs_ncg * 8` (`0x2b6fc`–`0x2b704`), and additional directory/inode-related tables (`0x2b71c`–`0x2b798`). The fragment bitmap is not the complete memory requirement. A separate checker copy in `libfs_utility_init` has the corresponding blockmap allocation/failure at `0x1f7c0`/`0x1fc34`.

For decimal 2 TB and 4096-byte fragments, a whole-disk one-bit-per-fragment estimate is approximately **58.2 MiB**; the actual user-data region is smaller and the other allocations add overhead. This is arithmetic sizing, not a measured retail checker peak. A checker that starts or handles an empty filesystem has not established populated, fragmented, near-full filesystem repair.

This bounded trace did **not** establish a fixed 963 GiB filesystem-check ceiling, a 128 MiB retail checker container, or proof that changing a container is sufficient. Those wiki assertions must remain unverified until the exact retail caller and peak working set are traced and exercised.

## Direct format-path evidence

The ordinary utility's newfs wrapper at `0x9fa8` obtains a 64-bit device sector count and a sector-size field. At `0xa09c` it loads the count with `ld`, and at `0xa0a4` multiplies by sector size with `mulld`; it passes the resulting bytes and sector size into the formatting helper at `0x12f60`. That helper divides using `divdu` at `0x12fd8` and stores the resulting count as 64 bits at `0x12fe0`. Thus this particular stage does not truncate device capacity to 32 bits. It does not prove all following format or I/O code is wide enough.

The helper initializes globals with constants `0x1000` (4096) at `0x13004`, `0x4000` (16384) through the clamp at `0x13028`, `8` at `0x13060`, and `0x2000` (8192) at `0x13078`. Their roles are consistent with the conventional fragment/block/minimum-free/inode-density defaults, but complete field-level provenance to the final on-disk superblock is unfinished. The formatter's diagnostic paths explicitly validate power-of-two fragment size, increase fragment size to the reported sector size, and check cylinder-group geometry.

The recovery helper beginning at `0x7be44` likewise accepts the sector-size argument in `r4`, preserves it in `r8`, divides the byte count using `divdu` at `0x7bf60`, and stores the count as 64 bits at `0x7bf68`. It also initializes 4096/16384/8192 constants in the same area (`0x7be84`, `0x7be94`, `0x7bf00`). The recovery formatter is therefore another concrete path to audit for logical-versus-physical sector interpretation and compatible geometry. No geometry patch has been proposed from these constants alone.

## Consequences for the next engineering step

The root analysis's directly identified capacity refusal remains the first blocker. Removing that refusal would only admit a disk into later stages; this review identifies genuine formatter/checker consumers that require their own evidence.

The next bounded audit should trace **the exact retail checker invocation and allocator/container budget**, separately for normal dirty-boot repair and Recovery Menu Restore File System, then follow every updater/reinstaller and format copy. Capture complete function identities and call paths, actual input units and full request widths, map allocation formulas, and establish conservative peak-memory headroom on a populated 2 TB fixture. Keep the observed 64-bit newfs count stage distinct from proof of a fully 64-bit filesystem and storage stack.

On the reported CECHA00, the expected ATA crypto lane is CBC-192 rather than Slim XTS; that inference comes from model/encryption documentation, not physical ATA or crypto observation. The user's three SSD identifiers do not establish their exposed sector geometry. [CECHA family](https://www.psdevwiki.com/ps3/CECHAxx), [firsthand encryption account](https://www.psdevwiki.com/ps3/HDD_Encryption).

No real-media check, formatter run, filesystem creation, firmware rebuild, flash write, checker-memory measurement, or durability test occurred. The source-backed staged gates remain in `research/validation-plan.md`.
