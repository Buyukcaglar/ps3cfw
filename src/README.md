# Sources

| Folder | What | Notes |
|---|---|---|
| `checker_telemetry_p8/` | Heap observer compiled into P6-P13 `libfs_utility_init` (`tm_record` layout = the 272 B USB record header) | Part of P13; drop it for a lean build |
| `native-fill-metrics-v2/` | Native PS3 fill/verify app (HW002BH, APP_VER01.16): UI, ETA, pattern writer, metrics. Built PKG: `packages/HDD2TB-BH-FILL-v2.pkg` | `build.py` still points at the old layout (`analysis/dev006/...`, `observations/HW002BH`, `diagnostics/`); fix paths before rebuilding. Toolchain: `tools/toolchains/psdk3v2-c920bc3-portable` + zig 0.15.2 |
| `patch-generators/` | `prepare_p*.py` / `model_p*.py` that produced the P8-P13 patched ELFs and their PPC models | Reference only; paths refer to the pre-2026-10-29 layout. Full context in `archive/` |

`packages/HDD2TB-BF-FILL-v16.pkg` is the app that did the first 792 GiB native fill (source in `archive/`, `analysis/dev006/native-fill-final-v16`).
