# Exact checker budget audit — Evilnat 4.93 CEX

This is a read-only static audit of the user's supplied firmware. It establishes separate quick-status and full-repair caller paths. It does not establish runtime memory headroom, full disk integrity, or an installable/stable firmware. No physical media, original PUP, original extracted SELF, or flash contents were modified by this audit. Derived outputs are confined to `analysis/checker-audit/`.

## Engineering decision

Raising the independently identified `emer_init` acceptance threshold from `0x180 << 32` bytes to `0x1f0 << 32` bytes is a reasonable **first empty scratch-disk admission probe** for native decimal 2 TB media. That first result should establish whether the existing incompatible-drive rejection has been crossed; formatting and initial boot are separate later checkpoints. It is not an adequate complete implementation of reliable 2 TB support: this audit found a real full filesystem checker caller that allocates only **32 MiB** for its backing buffer and heap. A 2 TB filesystem with 4 KiB fragments requires approximately **58.2 MiB for its one-bit-per-fragment block map alone**.

The two observations are compatible: clean boot uses a distinct `-F` path which avoids full checker maps. Passing clean boot can therefore coexist with failure when a later repair is required. Acceptance must not be presented as recovery safety.

For the next repair experiment, the full caller's backing-buffer allocation and heap-size argument must be changed together, or the checker must be redesigned. A **128 MiB candidate** has static plausibility as an experiment, but is not proven sufficient or allocatable from the selected parent pool in every caller context. This audit does not recommend changing fragment size or inode density to disguise the memory problem before the current geometry and checker working set are measured.

## Inputs and reproducibility

The unchanged source PUP SHA-256 is `ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a`.

Additional copies were decrypted into this audit's own directory using the existing local `scetool` and key directory. Previously decrypted filesystem utilities were inspected read-only in `analysis/fs-review/`.

| Derived input | SHA-256 |
|---|---|
| `vsh.elf` | `e3681dbe492a508383ecf69ee5e3595cc9eb1c9cc3c300a3360b9d90c048afc4` |
| `sysconf_plugin.elf` | `89f2f34dd8aebdc951bd4506eba0b66f8284925d544f1825dc2c434fe266659b` |
| `hdd_copy.elf` | `3e5a29792a414c92a4e16165e3ca76dfdb6d780b055e46c6455091b8932d01d7` |
| `libfs.sprx.elf` | `b927cab05973ef71fbcd6103f1e44f498de0a0c21300c32d7fd7807e006e0e7e` |
| `liblv2.elf` | `aac69540830b4a6673b93331bf52266f360551a2732adcbb3c7a808daddf09c5` |
| Existing `libfs_utility_init.sprx.elf` | `6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a` |
| Existing `libfs_utility.sprx.elf` | `b4ceceb4f478486f7b98192d1688f05dc91a4ac0234f3468a883a227b0fba297` |

All following addresses are ELF link-time VAs, before PRX relocation. Use program headers to translate data addresses: the second `sysconf_plugin` segment has a different file-to-VA bias from its first segment. `inspect_exports.py`, `scan_imports.py`, `codequery.py`, and `trace.py` under `analysis/checker-audit/` preserve the methods. PRX table layout was checked against the [PS3 PRX format notes](https://www.psdevwiki.com/ps3/PRX). NIDs are used as identities even where their private API names remain unknown; the [community NID database](https://www.psdevwiki.com/ps3/Ps3.xml) likewise leaves these exports unnamed.

## 1. Heap APIs and utility policy

`libfs_utility` imports `_sys_heap_create_heap` (NID `B2FCF2C8`, stub VA `0x2d068`), `_sys_heap_malloc` (`35168520`, `0x2cf08`), `_sys_heap_free` (`8A561D92`, `0x2cfe8`), and `_sys_heap_delete_heap` (`AEDE4B03`, `0x2d048`). Names were independently matched using the established PS3 NID hash procedure and the [RPCS3 sys_heap registrations](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/Cell/Modules/sys_heap.cpp). RPCS3's heap implementation is not evidence of Sony's actual available memory or allocation behavior.

The utility has two heap-creation lanes:

- At VA `0x1a91c`, the supplied backing-buffer address and heap size are passed to heap creation with flags `0x80150000`. The small parameter structure contains size `8` and the buffer address.
- At VA `0x1a9a4`, the default heap creation uses flags `0x00150000` and no supplied backing-buffer structure.
- The backing-buffer initializer at `0x1aa1c` scans argv for the exact string `-F` (VA `0x2ea88`). It requires at least **2 MiB** if `-F` is present and at least **32 MiB** otherwise; it accepts a larger caller-supplied size. Corresponding size comparisons are at `0x1aa94` and `0x1aafc`.
- The default initializer at `0x1ab68` creates 2 MiB for `-F` and 32 MiB otherwise. The heap name is `cellFsck_Library`.

The `libfs_utility_init` copy has the corresponding backing-buffer initializer at VA `0xeafc`: `-F` comparison via import `0x214c8`, 2 MiB minimum at `0xeb74`, 32 MiB minimum at `0xebdc`, heap creation wrapper `0xe9fc`. Its exported NID `263172B8` maps to VA `0x11060`; callback-capable NID `1F3CD9F1` maps to `0x10e4c`. Both pass the caller's backing-buffer address and requested size to `0xeafc`.

The syscall identities were cross-checked against the [RPCS3 syscall binding table](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/Cell/lv2/lv2.cpp): syscall350 allocates memory from an existing container, and syscall349 frees an allocated address. The backing-buffer path must not be called a new container creation.

The real retail heap implementation was also decrypted from `liblv2.sprx` to close the buffer interpretation. Its NID `B2FCF2C8` export is VA `0x76d4`. When flags are negative (high bit set) and the supplied structure is valid, VA `0x7824` loads the structure's word at offset 4; if it is nonzero and flags bit 0 is clear, VA `0x7840` uses the caller's requested size, stores that supplied address to the local base slot, and branches into heap setup at `0x7798`. It bypasses the default syscall348 allocation at `0x7788`. This confirms that the filesystem utility wrapper's incoming `r5` value is a backing address, not a new container ID; the wrapper stores it in the heap parameter structure. If the supplied address is zero, the implementation falls back to its own default allocation; therefore a caller allocation failure must be handled explicitly before proposing a larger-buffer patch. Evidence: `retail-create-heap.txt`.

This distinction matters: simply changing the utility's default 32 MiB constant would not necessarily enlarge the concrete caller's separately allocated 32 MiB backing buffer.

## 2. Clean-boot quick check: exact VSH caller

VSH imports `fs_utility_init` NID `263172B8` at stub VA `0x637930`, and the default variant NID `A9B04535` at `0x6379d8`.

VSH function VA `0xd9d6c` builds argc `3` and argv:

```text
fsck_cfs
-F
hdd0
```

Its supplied-buffer branch at VA `0xd9ebc` calls `0x637930` with the incoming buffer address in `r5` and heap size in `r6`; if there is no buffer it calls the default variant at `0xd9ec8`.

The direct boot caller at VA `0xd11a4` supplies **2 MiB** (`lis r6,0x20` at `0xd11a0`). Its backing buffer is requested with 2 MiB at `0xd118c`, via syscall `350` (`0x15e`, wrapper `0xc94c4`), using a parent container ID and flags `0x200`. The buffer is freed via syscall `349` (`0x15d`) at `0xd11b4`. These are `sys_memory_allocate_from_container` and `sys_memory_free`, not container create/destroy operations.

The checker recognizes `-F` at `libfs_utility_init` VA `0x18e54` and sets the flag referenced via TOC offset `-0x7910`. At `0x18618`–`0x18624`, that flag branches to `0x19254`, before the full setup call at `0x186f0` (`0x1f230`, the routine containing the large block-map allocation). The quick lane opens the volume, invokes a superblock-reading helper at `0x19278`, tests fields/flags including superblock offset `0x520`, and returns status without entering full checking. VSH diagnostic strings distinguish `need full_fsck()` statuses from success.

Thus the 2 MiB quick-check budget is not the full repair budget, and the existence of this path cannot demonstrate that a large full check succeeds.

Evidence snapshots: `vsh-checker-launch.txt`, `vsh-checker-budget-callers.txt`, `init-container-wrapper.txt`, `init-fsck-main.txt`.

## 3. Full-repair path: exact sysconf caller

The retail `sysconf_plugin` imports `fs_utility_init` NID `1F3CD9F1` at stub VA `0x12f868`. Its function at VA `0x30058` builds:

```text
fsck_cfs
-y
hdd0
```

The exact allocation/call sequence is:

| VA | Instruction/action | Consequence |
|---|---|---|
| `0x3009c` | calls import `0x12cd50` with `r3=1` | obtains a parent container ID via VSH NID `E7C34044(1)` |
| `0x300a4` | `addi r6,r1,0x70` | output allocated-address pointer |
| `0x300a8` | `li r5,0x200` | memory allocation flags |
| `0x300ac` | `lis r3,0x200` | requests `0x02000000` bytes = **32 MiB** |
| `0x300b4` | calls `0x1d4d4` | wrapper issues syscall `350` at `0x1d4e0` |
| `0x300bc` | `lwz r5,0x70(r1)` | loads allocated buffer address |
| `0x300c8` | `lis r6,0x200` | requests a **32 MiB checker heap** within that buffer |
| `0x300d4` | calls `0x12f868`, argc=3, callback `r7=0x15b208`, `r8=0` | invokes callback-capable checker wrapper |
| `0x300e4` | syscall `349` | frees backing buffer after return |

This full check does not select `-F`, so it reaches the general checker path and its map allocation. The wrapper in `libfs_utility_init` at `0x10e4c` preserves buffer-address/size arguments `r5/r6`, calls `0xeafc` at `0x10eb8`, installs callbacks and proceeds to the checker main (the continuation after `0x10f80` has also been inspected). Its minimum is 32 MiB; a larger supplied heap is allowed.

The parent container getter is now resolved in this exact VSH: NID `E7C34044` exports VA `0x6024a4`, which reads element `r3` from the ID array at VA `0x7074cc`. The full sysconf caller requests element 1. This establishes the selected existing pool's identity by slot, but its live capacity, reservation, other users, and available headroom remain unknown. No new container is created by the checker launch.

Function VA `0x2ffd4` creates a thread with this entry descriptor at VA `0x15b228`, named `fsck_cfs_main` (string VA `0x1391e8`), then joins it. There are direct calls to that launcher at VA `0x4db20` and `0x580f0`. They establish concrete system-configuration call sites. Their complete higher-level UI state and dirty-boot/recovery handoff selection remain to be fully labeled; this audit does not assert every restore path has now been closed.

A later experiment that requests 128 MiB would require changing **both** instruction words `3c600200` at VA `0x300ac` and `3cc00200` at VA `0x300c8` to encode `0x800` as the `lis` immediate (128 MiB), along with an independent check that the allocation succeeds and the selected parent pool leaves sufficient system headroom. These are candidate patch sites, not patches made by this audit. The current code does not visibly validate the allocation result before loading its output; a larger request must not be assumed harmless on failure.

Evidence snapshots: `sysconf-full-checker-launch.txt`, `sysconf-checker-callers.txt`, `sysconf-fsck-thread-context.txt`, `sysconf-full-checker-context.txt`, `init-callback-wrapper.txt`.

## 4. Full checker allocation consequence

As established in the earlier [filesystem review](filesystem-review.md), `fs_size` is loaded as 64 bits from superblock offset `0x438`. In the init copy, block-map allocation is at VA `0x1f798`–`0x1f7c0`: add 7, divide by 8 with rounding, then round to an even number of bytes and pass through the calloc wrapper at `0xe718`. The failure path at `0x1fc34` reports `cannot alloc %u bytes for blockmap`.

At 4096-byte fragments, a whole 2,000,000,000,000-byte filesystem would require 61,035,158 bytes after rounding, about **58.21 MiB** for this map alone. The actual HDD0 partition is smaller than the physical disk, so its exact requirement must use the created superblock. It will nevertheless exceed 32 MiB for a near-full 2 TB HDD0 partition. The bitmap-only theoretical 32 MiB boundary is **1 TiB**; other live allocations lower the practical boundary. This provides a concrete mechanism consistent with reports of repair problems near a terabyte, without claiming a precisely measured 963 GiB limit.

Other simultaneous allocations include `fs_cssize` (superblock offset `0x9c`, allocation `0x1f6a0`), `fs_ncg * 8` (`0x1f7d8`–`0x1f7e4`), and directory-related tables based on at least 128 entries and superblock field `0x3f0` (`0x1f7fc`–`0x1f858`). Additional pass-specific allocations and worst-case population-dependent peaks remain unbounded. Heap allocator overhead and fragmentation also matter.

For 2 TB, these arithmetic stages do not overflow the 32-bit final byte count. For larger disks, the 32-bit multiply and allocation interfaces need independent overflow checks; a nominally 64-bit `fs_size` does not make every caller safe.

## 5. Recovery formatter and restore handoff: bounded findings

`emer_init` contains a distinct embedded `newfs_cfs`; earlier field tracing showed its helper at VA `0x7be44` uses the supplied sector size, divides the byte count with `divdu` at `0x7bf60`, and stores the count as 64 bits at `0x7bf68`. Default 4096/16384/8192 constants are present, but the complete logical/physical-sector contract and every layout result remain qualification work.

Recovery's restore-file-system handler includes a call to VA `0x7b808` at `0x4cd94`, followed by an error path whose exact diagnostic is `cellFsUtilitySetCfsFsckFlag() error code [%x]`. On success it updates boot state and calls `0x960e4`. This is evidence of a persistent flag/handoff workflow, not an embedded full checker in this handler. The connection from that handoff to all `sysconf_plugin` invocation contexts is not fully traced yet.

Two container leads must not be conflated with HDD0 fsck:

- A 1 MiB allocation near VA `0x6a8f0` is proven to accompany `/dev_flash`, `CELL_FS_FAT`, and `CELL_FS_IOS:BUILTIN_FLSH1`, with `-use_memory_container`. It is not the HDD0 checker heap.
- VA `0x79d18` creates a 20 MiB container and parses supplied parameters. Its entire role and capacity-dependent working set are not established here; do not label that 20 MiB as the full checker budget.

A printable-string scan of `hdd_copy` did not find an fsck/newfs name; this negative result does not establish that it has no relevant storage or recovery path.

## 6. Required experiment and qualification gates

The user's CECHA00 and reported rejected SSD models define the initial hardware lane. No ATA-reported capacity or sector sizes have yet been observed. The first threshold experiment should use an empty, genuinely disposable/spare target, with the original drive physically kept apart and rollback/console flash backup already secured. Its first checkpoint is the admission result; do not treat a format offer as a completed format/boot or repair qualification. Collect exact model/firmware, native LBA count, logical and physical sector sizes, boot/format messages, created HDD0 layout and superblock geometry. Preserve hashes and logs, and stop media qualification on any checksum mismatch or repair failure.

`0x1f0 << 32` is 2,130,303,778,816 bytes = 1984 GiB. It accepts ordinary native decimal 2 TB capacities while remaining below 2 TiB (4,294,967,296 sectors at 512 bytes). It is not an implementation of >2 TiB support. The current 1536 GiB gate already lies above the signed 32-bit 512-sector boundary; decimal 2 TB remains below the unsigned 32-bit sector boundary. This supports the scope of the first acceptance experiment but does not substitute for whole-stack width tracing.

Even after acceptance/format/boot, do not import irreplaceable user data as a test. Before claiming practical support, the engineering sequence must include:

1. Instrument or otherwise measure the full check's actual heap/backing-buffer use, failure return, and high-water mark on representative newly formatted and densely populated 2 TB fixtures.
2. Resolve syscall350's parent container pool headroom and all full checker callers; apply a consistent budget policy that handles allocation failure cleanly.
3. Exercise normal clean boot, dirty boot and repair, Recovery Menu Restore File System, database rebuild, same-version reinstall/update and rollback on disposable data. A `-F` success is only a quick-status check.
4. Fill and verify above 1 TiB and near the disk end; repeat checksum readback after shutdown/restart and after repair. Qualify physical power interruption only with scratch data and a recovery plan, after ordinary I/O and repair pass.
5. Preserve the original drive and validated external copies until the full acceptance plan in `validation-plan.md` is satisfied. No finite test proves a universally data-loss-free system.

At this audit's close, **the full-repair backing-buffer memory barrier is confirmed statically; its runtime budget fix and complete recovery-path coverage are pending**.
