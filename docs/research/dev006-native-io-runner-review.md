# Native I/O runner preparation

The remaining capacity qualification needs deterministic data generated on the
PS3, because the available Wi-Fi link is too slow for a full corpus and Ethernet
is unavailable. PC-side filesystem writes would not qualify GameOS allocation
or its I/O path. The planned sustained test will use only owned files on spare
PNY, distinct patterns by file and offset, a retained free-space reserve, checked
write/read/seek/flush/close outcomes and post-restart/read-only PC verification.
Its write volume and cancellation/deletion policy are not yet released.

First validate a minimal userland runner on real hardware. HW002AQ reads one
known 353,203-byte file and writes only one new 160-byte USB result. It has no
HDD writer or dynamic command/argument interpreter. The native package install
is the ordinary new-title operation, not a firmware or plugin replacement.

The syscall numbers/register contract and process-entry parameter layout were
checked against the pinned open-source PSL1GHT headers/crt at commit
f649a08fd536a9e27c08c7db2d93a2d7ee4c3bbe. Sources:
https://github.com/ps3dev/PSL1GHT/blob/f649a08fd536a9e27c08c7db2d93a2d7ee4c3bbe/ppu/include/sys/file.h
https://github.com/ps3dev/PSL1GHT/blob/f649a08fd536a9e27c08c7db2d93a2d7ee4c3bbe/ppu/crt/crt0.S
https://github.com/ps3dev/PSL1GHT/blob/f649a08fd536a9e27c08c7db2d93a2d7ee4c3bbe/ppu/include/sys/process.h

The first Zig-linked ELF mixed descriptor code with ABI2 flags and branched to
data descriptors. It was rejected before USB staging. The final ELF uses the
portable PSDK3v2 GNU GCC4.5.2/assembler/linker, from the producer's pinned archive:
https://github.com/Estwald/PSDK3v2/tree/c920bc3e2c0fcb7c7d0e03e0be323625aa24c0ba
Archives match Git blob SHA1 and recorded SHA256. Only project-local extraction
and child-process DLL search paths were used; no system toolchain installation.

Two GNU builds are byte-identical. Independent checks cover ELF64 big-endian
PPC64, ABI flags0, RX/RW load segments, process parameters, all executable
sections including GNU save/restore helpers and 31 direct calls into code. The
first audit stopped at traceback data; it is superseded by independent-audit-v3,
which scans all 2,868 executable-section bytes. Native launch remains unproven.

The upstream Windows C packager retained a leading slash on relative paths,
preventing its EBOOT NPDRM classification. A separate local copy changes only
four relative-path normalization sites. No crypto/SELF algorithm changed.
Independent Python debug-package decoding verifies the three exact relative
paths, EBOOT type1 and the complete unchanged ELF inside the NPDRM fake SELF.
Earlier invalid packages remain preserved and are not released. Final package:
diagnostics/HDD2TB-AQ-SMOKE-v2-relative/HDD2TB-AQ-SMOKE.pkg, 71,344 bytes.

21 mocked failure/success contracts check marker refusal, exclusive output,
read-only HDD open, read/hash/count failures and cleanup/error returns. 72 host
SHA-256 boundary/chunk cases match Python hashlib; 66 parser cases and nine USB
identity guards pass. These are host evidence, not PowerPC/native execution.
The native SHA known-answer check runs again before the real HDD read.

No root/derived key is used by the runner, package, USB marker or parser.
P13 remains installed. There are no ad hoc VSH RAM patches, checker requests or
kernel probes. The result records the HDD read phase before USB write/flush;
it must not be reported as final USB-flush/close or power-loss durability proof.
