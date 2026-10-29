# Firmware images

| Folder | Role | PUP SHA-256 |
|---|---|---|
| `baseline-evilnat-4.93-cex/` | Unmodified Evilnat 4.93 Cobra 8.5 CEX (base of every build; rollback target) | ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a |
| `HDD2TB-P12/` | Build parent of P13 (needed for `tools/build_hdd2tb_p13.py`) | 7fb5d6e57ef53654f336745dbc9463c8e6b2cded03b05cdbeb80e5125215fb7c |
| `HDD2TB-P13/` | **Release candidate.** `inputs/` holds the patched libfs_utility_init ELF the build consumes | 652c0c0312cd51283473e653df6e2cdfd874a674f6fb7e83979c45d28fed066d |
| `HDD2TB-RDI12/` | Diagnostic build **currently installed** on the console (identity reference only; do not reinstall) | 2a1e3738a687a9e2114c7b45cd0a09b039bb473c79cb9872aa8a871e88ce091a |
| `reference-elf/baseline/` | Decrypted baseline ELFs for reverse engineering: sysconf_plugin, libfs_utility_init, libfs_utility, libfs, liblv2, vsh, hdd_copy, emer_init | - |

Each candidate folder keeps its `build-manifest.json` and `software-verification.json`.
The `HW00*.md` owner instructions inside them are historical; use the current ROADMAP checklist instead.
