# P2 formatter review after the first CECHA00 test

Scope: immutable `analysis/coreos/emer_init.elf`, SHA-256 `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d`. Addresses below are ELF virtual addresses; file offsets are VA minus `0x10000`. Source PUP and firmware outputs were not modified by this audit. Supporting bounded disassembly and the host geometry model are in `analysis/p2-formatter-review/`.

## Result and limit of the result

The user reports that P1 installs and boots with the control drive. With a Crucial `CT2000BX500SSD1`, startup offers formatting; accepting that prompt results in the unsupported-hard-disk message. Neither the exact time between confirmation and error nor an underlying error code has been supplied. A format prompt alone does **not** prove the patched capacity comparison has already executed; the caller/UI audit must establish that order.

This audit has not identified a second formatter capacity constant that justifies another patch. The embedded newfs retains 64-bit capacity and last-sector addressing in the traced path. Its geometry routine, evaluated with synthetic 2 TB inputs and the wrapper's defaults, produces valid geometry without a size error. The 32 MiB full-checker budget found earlier is a separate repair limitation and has not been connected to this early format failure.

No formatter patch is proposed on this evidence. The next patch must follow an actual rejecting branch or a measured error, not merely suppress formatting errors.

## Formatting caller and filesystem selection

The following statically connected route exists in `emer_init`:

| Address | Action / next stage |
|---|---|
| `0x51418` | Storage-region setup coordinator; emits `creating storage regions for (v)HDD...`; calls `0x70a5c`, then `0x704fc` |
| `0x704fc` | Iterates configured partitions; emits region/name/filesystem diagnostics at `0x705f8`; calls `0x70460` at `0x70620` |
| `0x70460` | Calls `0x7a918` at `0x704d0` |
| `0x7a918` | Tail branch to filesystem selector `0x7a644` |
| `0x7a644` | Recognizes filesystem name; `CELL_FS_UFS` matches at `0x7a70c` and selects `0x7aa8c` at `0x7a8d8` |
| `0x7aa8c` | Calls `0x7ae14` with zero optional pointers and verbose flag 1 |
| `0x7ae14` | Tail branch to embedded `newfs_cfs` outer wrapper `0x7aac4` |

The partition loop's table resolves HDD0 to `CELL_FS_UTILITY:HDD0`; its UFS type string is `CELL_FS_UFS`. The selector uses syscall 836 for other filesystem names. The branch that checks an existing mount before formatting uses syscalls 837/838. These facts establish one concrete embedded-format route, not that the observed failure traversed it. Separate caller/UI tracing owns that final connection.

## Capacity units and early writes

At `0x7ab74`, outer newfs obtains device information through `0x7cba4`. It reads sector count with `ld` from info `+0x28` at `0x7ab90`, sector bytes with `lwz` from `+0x30` at `0x7ab88`, and multiplies with `mulld` at `0x7ab94`. These are a 64-bit sector count and 64-bit product; the narrower field is sector size.

The helper at `0x7be44` divides byte capacity by supplied sector bytes with `divdu` at `0x7bf60` and stores the sector count with `std` at `0x7bf68`. The beginning of main mkfs, `0x7e7a0`, checks that signed 64-bit count is positive at `0x7e8e8`–`0x7e8f0`.

The first capacity-dependent write in mkfs precedes geometry creation: `0x7e928` calls `0x7d814` to test/write the last sector. Its address remains 64-bit through:

1. `0x7d830` / `0x7d83c`: copy sector address into `r4` / `r30` without narrowing; the nearby `clrldi` instructions narrow the buffer pointer and request byte length.
2. `0x808d0`: captures the address in `r26`; `mulld` at `0x80980` or `0x809fc` converts address to a 64-bit byte offset.
3. `0x7b4e4`: captures that offset in `r29`; validates byte-offset alignment with a 64-bit `and` / `cmpdi`; `divdu` at `0x7b5d8` converts offset back to device sectors in syscall 603 argument `r5`. The syscall request length `r6` is narrowed, which is appropriate for the small writes traced here; the LBA is not narrowed there.

There is a separate device-info attribute path in `0x7ac80`–`0x7ad6c` that attempts a large zero/erase pass. Its current total/position registers and syscall LBA are 64-bit, while its per-iteration remaining-length comparison uses 32-bit `cmplw`. Native decimal 2 TB sector counts remain below `2^32`; this observation does not certify that path for larger media, sector variants, erase flags, or I/O failures. The path logs an erase error and continues to newfs. The asynchronous/LV2 audit must assess its actual request semantics separately.

An aligned instruction scan of the loaded emer code found only one literal `li *,0x180`: original capacity threshold at `0x46198`. Other instructions with immediate bits `0x180`, `0x1f0` or `0xc000` were structure/stack offsets or masks in the inspected contexts. For example, `0x8172c` contributes `0xc0000006` to an ioctl command; it is not a second capacity ceiling. This scan cannot exclude a limit computed from other constants, held in a table, or implemented in another module.

## Geometry fields and bounded host evaluation

The default wrapper initializes 4096-byte fragments, 16384-byte blocks, inode density 8192 and maxcontig 8. Main mkfs turns sector count into fragment count with a 64-bit arithmetic shift and `std` at `0x7ebb4`–`0x7ebbc`. Context `+0x460` corresponds to the superblock size field; the filesystem superblock starts at context `+0x28`.

Geometry helper `0x7e0e0` uses 64-bit `fs_size` for the number-of-groups calculation at `0x7e588`–`0x7e5a0`: load 64 bits, round up with the per-group fragment count, divide using `divd`, then store the much smaller group count as 32 bits. Per-group fragment/inode values are 32-bit quantities. This is not a 32-bit truncation of the volume size.

`analysis/p2-formatter-review/geometry_model.py` implements only the integer instruction subset reached by this helper. It executes the immutable routine's decoded instructions against synthetic memory prepared from the preceding wrapper/mkfs defaults. Calls to the diagnostic printer are recorded and the exit helper fails the run; there is no I/O, kernel, filesystem image, PS3 boot or physical-device simulation. A missing mask/shift seed was corrected during construction before the recorded results; the retained final JSON contains the corrected run. Treat it as a bounded arithmetic check, not a hardware or formatter qualification.

Recorded results in `geometry-model-results.json`:

| Synthetic input bytes | Fragment count | `fs_fpg` | `fs_ipg` | `fs_ncg` | Rounded `fs_cssize` |
|---:|---:|---:|---:|---:|---:|
| 1,000,000,000,000 | 244,140,625 | 73,900 | 36,992 | 3,304 | 53,248 |
| 1,649,267,441,664 (1536 GiB) | 402,653,184 | 73,900 | 36,992 | 5,449 | 90,112 |
| 2,000,000,000,000 | 488,281,250 | 73,900 | 36,992 | 6,608 | 106,496 |
| 2,000,398,934,016 (illustrative native 2 TB) | 488,378,646 | 73,900 | 36,992 | 6,609 | 106,496 |
| 2,130,303,778,816 (1984 GiB) | 520,093,696 | 73,900 | 36,992 | 7,038 | 114,688 |
| 2,199,023,255,552 (2 TiB) | 536,870,912 | 73,900 | 36,992 | 7,265 | 118,784 |

All return 0 without error diagnostics, retain density 8192, and give `fs_cgsize=16384`, `fs_dblkno=2340`. An independent arithmetic read of the cylinder-group-size expression at `0x7e354`–`0x7e3c4` agrees with the 73,900-fragment stopping point: `180 + ceil(36992/8) + ceil(73900/8) + 8*4 + ceil((73900/4)/8) = 16384`. Main mkfs computes summary size by rounding `fs_ncg*16` to fragment bytes at `0x7ec34`–`0x7ec50`.

The listed native-sized value is illustrative, **not an observed ATA capacity for this user's Crucial**. Real HDD0 capacity is also reduced by its partition/region layout. The model establishes that these representative arithmetic inputs do not inherently make this helper fail; it does not establish every neighboring size, the effective runtime defaults, or on-device allocation success. The modeled 2 TB summary is below the independently observed LV2 128 KiB summary bound; no patch to that LV2 bound is justified by this model alone.

The code sequence and diagnostics strongly resemble the historical FreeBSD newfs implementation. Primary comparison sources are [FreeBSD 5.5 mkfs.c](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/5.5/sbin/newfs/mkfs.c) and [FreeBSD 5.5 fs.h](https://raw.githubusercontent.com/freebsd/freebsd-src/releng/5.5/sys/ufs/ffs/fs.h). These sources support field interpretation; they do not establish binary identity or license a claim that all Sony behavior is upstream behavior.

## Failure propagation and exact information loss

The following error path is statically confirmed:

| Stage | Error propagation |
|---|---|
| Raw-write wrapper `0x7b4e4` | Any nonzero syscall 603 return becomes `-1` at `0x7b5f0`–`0x7b5f8`; the original kernel return is lost here |
| Disk write `0x808d0` | Negative lower return stays negative; short write also becomes `-1` |
| `wtfs` `0x7d814` | A negative disk-write result prints `wtfs: %d bytes at sector %jd`; calls `0x7d718` with exit code 36 (`0x24`) at `0x7d894`–`0x7d898` |
| Exit helper `0x7d718` | Codes 1–29 select `0x80010002`; codes above 29 select `0x8001002b`. It restores a saved context through `0x28574`, which matches longjmp behavior |
| Main mkfs | Context save at `0x7e804` / `0x28450` matches setjmp behavior. Nonzero returns route through `0x7fb8c` to the function return. Special return 1 checks its completion flag; other nonzero values retain their code |
| Helper `0x7be44` | Nonzero mkfs result branches from `0x7c040` to its return without replacing it |
| Outer `0x7aac4` | Any nonzero helper result is printed by `newfs() return %d`, then converted to `-1` at `0x7ae0c` |
| Partition loop | A nonzero selected formatter return branches from `0x70628` to its failure/log return. The coordinator maps failure into status bit `0x10` at `0x5148c` |

Other outer errors such as get-device-info, work-area setup, context/open and finalization also collapse to `-1`. Thus the generic upper failure does not identify which geometry rule or I/O operation failed. The exact user-visible unsupported state connection still requires the separate UI audit or instrumentation.

Useful existing diagnostics, if a supported collection method is available, are the device-info fields, selected partition ID/filesystem, `newfs_cfs started`, the last-sector-write diagnostic and the exact `newfs() return` value. A minimal diagnostic candidate should record the decision and return before conversion, not change the result to success.

## Next decision

1. Finish the caller/UI branch ordering. Establish whether the post-confirmation unsupported screen is reached directly by `0x46198` or after a formatting/region error. P1's prompt is insufficient to choose between those routes.
2. If capacity is still the rejecting branch, verify which code copy is executing before changing arithmetic. If a format operation fails, capture its selected device/region and return at the earliest point before it is collapsed; keep syscall 603's original return available for diagnosis.
3. Validate native device IDENTIFY and the effective region size/sector contract. Do not infer these from the SSD marketing model alone.
4. Only then select a minimal fix with exact expected original bytes and a second hardware experiment. There are no defensible replacement bytes from this formatter audit yet. Full-checker memory, dirty boot, repair, updates and populated-volume stress remain independent release gates even after formatting succeeds.

