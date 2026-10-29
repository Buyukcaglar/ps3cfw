# Pitfalls

## Process (what stalled the previous effort)
1. **Unfinishable acceptance criteria.** E01-E09 demanded a whitebox proof of
   closed-source internals (every alias, continuous lower bound, all routes). No
   finite test could close them, so 13 RDI rounds each cost the owner one firmware
   install + restore cycle without closing a gate. Every gate must be decidable by
   one bounded test.
2. **Instrumenting to prove a negative.** Diagnostic builds made "just to be sure"
   create new uncertainty (new code, new receipts, new parsers). Instrument only
   to explain an observed failure.
3. **Not comparing with stock.** The retained kernel object was the stock VSH
   printf lock. Asking "does stock firmware do this too?" would have closed it at RDI5.
4. **Ceremony overhead.** Hash-pinned custody of 18,000+ files, "consumed" one-shot
   scripts, per-step approvals, preservation archives of a disposable drive before
   every session, 11-request HTTP gate sets. The rules generated most of the work.
5. **Log-style docs.** README, ROADMAP and INITIAL_TASK_PROMPT were near-identical
   100 KB stacks of "CURRENT:" paragraphs with compressed words and UTF-8 mojibake.
   STATUS.json was 163 KB. Keep STATUS to one page; append the history to SESSIONS.md.
6. **Distrusting owner reports.** "All green / capacity unchanged" was recorded
   but treated as insufficient, which triggered more cycles. Accept UI-level owner reports.

## Technical
1. **Clean boot is not repair.** The boot quick check (`-F`, 2 MiB) never builds the
   bitmap. Every acceptance test must include a full check (Restore File System
   or the automatic post-dirty-boot check).
2. **Several capacity gates.** emer_init (recovery/format), sysconf (XMB) and the
   LV2 aggregate mount ceiling. The Lexar's 2.048 TB needs 144,397 B > the stock
   128 KiB, while 2.000 TB drives do not, so test the largest "2 TB" variants.
3. **Gate value 0x1f0<<32 = 1984 GiB**, deliberately below 2 TiB. Do not raise it
   casually: >2 TiB touches 32-bit sector paths that are not audited.
4. **Checker memory comes from a shared VSH container** (slot 1, ~183 MiB
   available before the check). 128 MiB fits; there is little room to grow. P5
   rejects allocation failure before calling the checker; keep that in any rebase.
5. **Modified CORE_OS = brick risk.** emer_init and lv2_kernel are patched. Always
   verify the PUP SHA-256 after staging. Brick recovery needs a NAND hardware
   flasher and `vault/nand/`. Neither dump is a pristine pre-project image:
   HW001B = ROS1 P1 (selected) + ROS0 older 4.92-era bank with baseline emer_init;
   HW001D = ROS0 P2D (selected) + ROS1 P1. Both carry the console's unique
   per-box data, which is what matters for unbricking. Never share them.
6. **Signatures.** Modified SELFs keep stale signatures and load only on CFW with
   signature checks off. Never install on OFW/HFW or another model.
7. **Install route.** Same-version reinstall via Recovery Mode -> 6 System Update.
   There is no "save update data" option in Safe Mode; do not instruct it. The
   reinstall can drop webMAN: reinstall the existing UPDWEBMOD package. Cobra
   disables `boot_plugins.txt` in recovery by design; do not patch that.
8. **Windows and PS3 drives.** PS3 drives look RAW/uninitialized. **Never click
   "Initialize disk".** Disk numbers and letters change between connections:
   identify drives by ATA model + serial. Raw reads need elevation; raw writes need
   explicit owner approval naming the serial.
9. **Sparse files.** Device images report terabytes but occupy far less. Never copy
   or hash them with tools that densify; size checks are enough for renames.
10. **Paths with brackets** (`[CEX]`) break PowerShell wildcards. Use `-LiteralPath`
    (the baseline folder was renamed to `firmware/baseline-evilnat-4.93-cex`).
11. **Encoding.** Write UTF-8 without BOM (ASCII preferred). PowerShell 5.1
    `Set-Content` defaults to ANSI. Git Bash has no `powershell.exe` on PATH, so
    Python tools call it by absolute path. Bash heredocs eat backslashes, so edit
    Windows paths in code with the Edit tool. The Shell.Application "Eject" verb
    is silently ignored here; `stage_usb.py` ejects through the volume API.
12. **Sector format.** Only 512-byte logical drives were tested (Lexar 512n, PNY
    512/512). 512e behaves differently in UFS accounting (andshrew). Keep the
    support list exact; 4Kn is unsupported.
13. **Observer side effect.** P13 writes `/dev_usb000/HDD2TB-P8.bin` (272 B) when
    a USB stick is present during a check. Harmless, but tell users.
14. **Filler on the Lexar.** ~858 GiB of nonce-owned test files share the disk with
    migrated owner data. Delete them only from an exact list (archive manifests).
15. **HDD crypto mode.** CECHA00 uses AES-CBC-192 with byte-swap-16 (`cbc192-bswap16`);
    slims use XTS-128. PS3HDDTool needs `vault/console-keys/eid_root_key`. Its write
    paths are journaled but still dangerous: owner approval per run.
16. **Delayed corruption.** One public report shows inode damage after ~6 months of
    normal use, so short tests do not prove longevity. That is why M6 and the
    retained 1 TB backup exist.
17. **Rollback.** Stock/baseline firmware refuses >1536 GiB drives and may offer to
    format. Never accept. Rollback = baseline PUP + refit the original 1 TB HDD.
18. **Throughput.** The test apps' ~14 MB/s reads and 11 -> 7 MB/s writes were CPU-bound
    (pattern + SHA-256). Inside FS calls: reads ~60 MB/s (console cap); writes 28.7 MB/s for
    ~26 GiB, then ~11.7 MB/s. The write cliff follows bytes written, not fill level.
    Not a defect signal. See `docs/research/PERF001/ANALYSIS-20261029.md`.
19. **Observer table overflow.** The P13 observer tracks at most 16,384 live chunks. On a
    populated volume (Lexar, 331k nodes) it overflows (flags TABLE_FULL + UNKNOWN_FREE), and
    its peak becomes a lower bound (`peak_is_lower_bound` in `read_observer.py`). The checker
    itself is unaffected: the native free always runs. Do not build diagnostics to resolve it
    unless a check actually fails.
20. **webMAN free-space decimals are not decimals.** `cpursx.ps3` prints GiB plus
    (MiB % 1024) / 100, so "65.10 GB" (~65.98 GiB) is more than "65.9 GB". Compare only the
    integer part, or read the exact free MiB another way.
