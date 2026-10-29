# Technical reference

Baseline: Evilnat 4.93 Cobra 8.5 CEX, `PS3UPDAT.PUP` 215,764,316 B,
SHA-256 `ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a`
(archive MD5 D3AF31CE6BDBC6790A5504CF8B3DA1B2). All addresses are ELF link-time VAs.

## 1. Why stock firmware fails with 2 TB

| Barrier | Where | Stock value | Effect |
|---|---|---|---|
| Recovery/format admission gate | CORE_OS `emer_init.self` VA 0x46198 | `0x180 << 32` = 1,649,267,441,664 B (1536 GiB) | "unsupported HDD" before format |
| XMB/sysconf admission | `dev_flash/vsh/module/sysconf_plugin.sprx` | same 1536 GiB class limit | refusal after format offer (HW001) |
| LV2 aggregate mount ceiling | CORE_OS `lv2_kernel` VA 0x2cac74 | 128 KiB (`lis 2`) | mount fails when CG summary aggregate exceeds it (Lexar needs 144,397 B) |
| Full checker budget | `sysconf_plugin` VA 0x300ac / 0x300c8 (`fsck_cfs -y hdd0`) | 32 MiB backing + 32 MiB heap | `cannot alloc %u bytes for blockmap` once bitmap > ~32 MiB (~1 TiB volume) |

The boot-time quick check (`fsck_cfs -F hdd0`, VSH 0xd11a4, 2 MiB) never enters
full checking, so **clean boot passing says nothing about repair**.

Bitmap arithmetic (4 KiB fragments): 2.0 TB volume = 61,035,158 B (58.2 MiB);
Lexar NQ100 measured 62,446,924 B. Theoretical 32 MiB bitmap boundary = 1 TiB.

## 2. Patch set: baseline -> P13

| Step | Module | Change |
|---|---|---|
| P1 | `emer_init.self` @ ELF off 0x36198 | `38000180` -> `380001f0`: gate 1984 GiB (2,130,303,778,816 B, below 2 TiB) |
| P3 | `sysconf_plugin.sprx` | sysconf admission 1984 GiB |
| P4 | `lv2_kernel` @ 0x2cac74 | `3c000002` -> `3c000003`: aggregate mount ceiling 192 KiB (196,608 B) |
| P5 | `sysconf_plugin.sprx` @ 0x300ac, 0x300c8 | `lis 0x200` -> `lis 0x800`: 128 MiB backing + heap; reject nonzero alloc status / zero address before calling the checker |
| P6-P8 | `libfs_utility_init.sprx` | heap observer (`src/checker_telemetry_p8`): 16,384-slot table, writes a 272 B record to `/dev_usb000/HDD2TB-P8.bin` when a USB stick is present. Diagnostic only |
| P9 | `libfs_utility_init.sprx` | bounded array-growth failure/overread fix; calloc multiplication-overflow rejection |
| P10 | same | stop block writes after a failed seek; keep I/O-failure flag |
| P11 | same | refuse dirty primary superblock flush when summary buffer missing |
| P12 | same | abort on summary read error before CONTINUE; discard uncommitted setup state before OOM cleanup |
| P13 | same | stop block reader on negative seek results; return nonzero through original epilogue |

P2D (on-screen diagnostic) was a throwaway step. RDI1-RDI13 were diagnostic
builds on top of P13 (resource receipts); they add no functional change.

Release candidate **HDD2TB-P13**: 215,765,852 B, SHA-256
`652c0c0312cd51283473e653df6e2cdfd874a674f6fb7e83979c45d28fed066d`.
Patched `libfs_utility_init.sprx` SELF 78,487 B, SHA-256
`7a57307b62aed291803b22a4db5da6d541c004f699368957a266e7f2442b6389`.

Signature policy: modified SELFs keep the original signature bytes; they load
only because the CFW disables signature checks. PUP HMAC is regenerated.

## 3. Build

`tools/build_hdd2tb_p13.py` repacks `firmware/HDD2TB-P13/inputs/libfs_utility_init-p13.elf`
into the P12 PUP (SELF re-encryption with retained keys, flash tar reflow, PKG
and spkg header regeneration, PUP HMAC). `build_hdd2tb_p1.py`, `p3.py`, `p5.py`
are imported as libraries. Older `build_hdd2tb_p*.py` document each step but
their parent PUPs were removed in the 2026-10-29 cleanup.

`python tools/verify_build.py` rebuilds P13 in `build/` and checks it byte-exactly
(verified 2026-10-29).

A from-baseline build (for a lean release without the observer, or for any new
patch) needs: baseline PUP + the four modified modules. All final module bytes
can be extracted from the P13 PUP; baseline ELFs are in `firmware/reference-elf/baseline/`.
Patch generators used for P8-P13 are kept in `src/patch-generators/` (reference;
paths inside them point at the old layout).

## 4. Checker resource facts (measured)

* Full checker route: sysconf `0x2ffd4` (thread `fsck_cfs_main`) -> `0x30058` ->
  `fs_utility_init` NID `1F3CD9F1` (`libfs_utility_init` 0x10e4c). Direct callers of
  the launcher: sysconf 0x4db20 and 0x580f0; which UI context (Recovery restore,
  automatic post-dirty-boot repair) each serves is not statically labeled. Gate G3
  settles the automatic route empirically: an empty 2 TB full check cannot fit in 32 MiB.
  Other checker copies (`libfs_utility.sprx`, export 0x11060, default heap 0xea84)
  have no known HDD0 full-repair caller.
* Backing comes from VSH container slot 1 (syscall 350, flags 0x200). RDI1 sample:
  container total 223,346,688 B, available 192,413,696 -> 58,195,968 -> 192,413,696 B
  (before / during / after).
* Observer partial peak on clean 2 TB volumes: ~64.8 MB (64,833,888 B) of the
  134,217,728 B arena, flag 512 = incomplete coverage (only known wrapper lanes).
* Cleanup (RDI series, PNY): 128 MiB backing returned, checker private heap mutex
  `_lv2hea` retired, worker joined, statuses 0.
* The one "retained" kernel object is the **VSH process's static printf lock**
  (0x7480a8, ID e.g. 0x95013b09, protocol 2 / recursive 32), lazily created once
  by the stock checker's first `vprintf` (caller utility+0x20940 -> create helper
  0x60d078). Process-lifetime singleton, created the same way by stock firmware,
  does not grow per run. **Not a leak; closed.** Do not destroy/reset it.
* **Not measured:** observer peak on a populated drive (the 2026-10-17 populated
  Lexar check ran without USB) and at 64 GiB free.

## 5. Drive geometry

| Drive | ATA model / FW | Bytes | Sectors | XMB free/total |
|---|---|---|---|---|
| Crucial | CT2000BX500SSD1 / M6CR091 | ~2,000,398,934,016 | 3,907,029,168 | 1658 / 1863 GB |
| PNY | PNY 2TB SATA SSD / HT3C09BA, SN <serial> | 2,000,398,934,016 | 3,907,029,168 | 1658 / 1863 GB |
| Lexar | Lexar SSD NQ100 2TB / SN21128, SN <serial> | 2,048,408,248,320 | 4,000,797,360 (512n) | 1698 / 1907 GB |

Lexar: 6,761 cylinder groups, summary 110,592 B, aggregate mount 144,397 B
(stock 128 KiB would fail, 192 KiB leaves ~52 KiB). The 192 KiB ceiling runs
out at roughly 2.7-2.8 TB, so it is a 2 TB-class fix, not a general one.

## 6. Evidence summary (P13 lineage)

| Area | Result | Where (archive zip paths) |
|---|---|---|
| Admission/format/XMB | Crucial (P4+), PNY, Lexar native format, XMB, restart | `observations/HW001I`, `HW002V`, `HW002Y` |
| Full checker, empty volumes | many passes on Crucial/PNY/Lexar with 128 MiB | `observations/HW002X`, `HW002AA`-`AK` |
| Full checker, populated | Lexar ~1.6 TB used, 130 GiB free: pass, XMB, capacity unchanged; no telemetry | `observations/HW002BG/native-check-v1` |
| Migration | 1 TB original -> Lexar, file level, 331,755 nodes / 830,359,369,613 B verified | `observations/HW002AY/RESULT.md` |
| Native fill | BF 792.46 GiB / 50 files, full readback twice; BH +65.73 GiB to 66.0 GiB free, retained 792 GiB re-verified | `observations/HW002BF/final-v16/RESULT.md`, `HW002BH/metrics-v2/native-receipt-v1/RESULT.txt` |
| Persistence | ordinary restart, 16 game executables + 165 pattern slices exact | `observations/HW002BH/post-restart-v1/RESULT.txt` |
| High-LBA placement | PC-side extent reads above 1536 GiB match | `observations/HW002BG/native-check-v1/resume-v5`, `HW002BJ` |
| Games | GT6 near-full new save/reload; LBP3 create/save/play | `observations/HW002BI`, `HW002S` |
| Throughput | reads ~60 MB/s inside FS calls (console-capped, position independent); writes 28.7 MB/s for ~26 GiB, then ~11.7 MB/s (SSD-side cliff, not fill). App-level 14.4 MB/s read and 11.25 -> 7.03 MB/s write were test-app CPU bound | `docs/research/PERF001/ANALYSIS-20261029.md` |

Not established: dirty-shutdown automatic repair, repair at 66 GiB free,
populated heap peak, power loss, months-long soak, >2 TB.
