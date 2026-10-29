# HW002R version 2 listing decoder correction

Primary-agent source review; no separate reviewer claimed. Original read-review, sources and incomplete baseline remain immutable. Version1 read the exact P8 utility and migrated webMAN control, then failed decoding the root LIST data as UTF-8, before any sample file. Its connection closed. This is a host-side decoding failure, not storage-integrity evidence.

Version2 retains the fixed manifest, command allowlist, exact complete P8 checks, sample/control hash comparisons, passive-peer restrictions, byte/time bounds and final close from the original review. Only the FTP text encoding is latin-1, with separate version2 source/review/check/result names. Manifest file paths are already restricted to printable ASCII. Thus outbound paths are unchanged bytes; root-listing text is decoded losslessly, and only the exact ASCII dev_hdd0 row/free-space digits are interpreted. No non-ASCII name support or filename conversion is claimed.

Version2 baseline and after-boot outputs are exclusive baseline-v2/after-boot-v2. After-boot continues to require a separate actual ordinary-restart/no-prompt report and the passed version2 baseline. The original pre-migration return-control draft is not used. No writes, repairs, memory probes, firmware operations, source-device access, key access or automatic retry occurs.
