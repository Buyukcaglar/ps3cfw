# Independent HW001B NAND ROS review

Date: 2026-10-11. Input is the ordinary file `observations/HW001B/incoming/FLASH-NAND-FW4.93.bin`, 268,435,456 bytes. This independent pass read only the 32-byte ROS selection header and the two ROS firmware regions. It did not read/hash other console fields, access physical disks, modify the dump or build firmware.

## Result

**ROS1 is the header-declared current bank and its entire 7,340,000-byte CoreOS content exactly matches HDD2TB-P1.** Its `emer_init.self` and independently decoded ELF also exactly match P1, including the `0x1f0 << 32` capacity threshold.

ROS0 carries SDK text `492.000\n` and SELF application-version field `0x0004009200000000`. Its emergency SELF container differs from the supplied 4.93 baseline, but its decoded **ELF is byte-identical to that baseline** and retains the original `0x180 << 32` threshold. The alternative bank is therefore not an unknown emergency-code variant after this review. These version fields are the dump's declarations, not independent authentication of a particular public 4.92 release.

This establishes the firmware bytes in the later dump and their declared selection. It does not establish which bank/image executed at the earlier failed 2TB startup, prove a fallback occurred, or qualify the entire flash image. No flash or bank-selection change is recommended on this evidence.

## Reproduction and read scope

Run `python analysis/hw001b-independent/inspect_hw001b.py`. The script independently parses the ROS header/tables, extracts emergency SELF copies into its own directory, verifies section HMACs, and decodes each with both the Python decoder and native scetool. It does not import the root ROS inspector or use its extracted emergency images. Native/Python ELF outputs agree for both banks.

The exact input spans read are recorded in `analysis/hw001b-independent/report.json`:

| File offset | Bytes | SHA-256 of this span |
| --- | ---: | --- |
| `0xc0000` | 32 | `c978c3eda810d7c10a29631257fa30e5b67535de79dfbf7301d0d152877b2c3d` |
| `0xc0020` | 7,340,016 | `78b379b08139d23ba2251a4a562760d08c91fe190f070df7aba7c20c23fa46e9` |
| `0x7c0010` | 7,340,016 | `c73fb31ac0eb59668463d9d5da3f14e731a2ae6859e0eadde61ad587a61a00cb` |

Each larger span comprises a 16-byte ROS prefix and its 7,340,000-byte CoreOS content. Input size and modification time remained unchanged during the scoped read. This review deliberately did not independently calculate a whole-dump hash.

## Current-bank mapping

The 32-byte big-endian header at `0xc0000` contains:

```text
pointer0 = 0x700010
pointer1 = 0x700010
length   = 0xe00000
reserved = 0
```

The previously traced secure-process loader, `0x8001cd50`, uses header `+8` for the current payload offset and computes the half displacement as `(length - 0x20)/2 = 0x6ffff0`. For selector 0, current prefix = `0xc0000 + 0x700010 = 0x7c0010`; its file table begins 16 bytes later at **`0x7c0020` (ROS1)**. Selector 1 subtracts `0x6ffff0`, giving prefix `0xc0020` and file table **`0xc0030` (ROS0)**. Both prefixes and both 25-entry CoreOS tables validate in this dump.

The emergency lookup at secure-process `0x8000dedc` explicitly supplies selector 0 in the inspected loader chain. Thus the static mapping and current dump agree that this path would load ROS1. That conditional statement is stronger than simply naming the header's bank, but remains a static statement: live boot state and execution during the earlier failure are not recorded here. No automatic alternate-bank retry was identified in the previously inspected local lookup methods.

## Emergency-image identities

| Property | ROS0 | ROS1 |
| --- | --- | --- |
| SDK bytes decoded as ASCII | `492.000\n` | `493.000\n` |
| SELF app version | `0x0004009200000000` | `0x0004009300000000` |
| Emergency SELF SHA-256 | `f50f78140174bcb34d489eb35c203e7f3c42b6c238d1d43554eca3c12b46c736` | `0e47265423f2d041d2da770d451376f69667269f35fe4cd6e349e8e2c318c639` |
| Emergency ELF SHA-256 | `ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d` | `113a234147286b0a5874d035aa668376702c7416fb8b532ff536b7fee50b94ff` |
| ELF relation to supplied 4.93 baseline | Byte-identical | One changed byte, file offset `0x3619b` |
| Instruction at VA `0x46198` | `38000180`: `li r0,0x180` | `380001f0`: `li r0,0x1f0` |
| Byte threshold | 1,649,267,441,664 (1536 GiB) | 2,130,303,778,816 (1984 GiB) |
| Native/Python decoded ELF equality | Pass | Pass |
| All four SELF section HMACs | Pass | Pass |

Both use key revision `0x1c`, APP SELF type 4, authentication ID `0x10700003fc000001` and vendor ID `0x01000002`. Their existing SELF ECDSA signatures do not verify under the matching published appldr public key, consistent with the project's existing CFW signature-dependence evidence. Section-HMAC success and decoder agreement are integrity/identity checks; they do not establish Sony-authenticated firmware or execution.

ROS1's full CoreOS SHA-256 is `13863e6d281013c9bf76ec6b8448d4941e6fc6a7dc406eff6def96b2a22978a6`, exactly matching the saved P1 build's content file. ROS0's is `fbc6e8624df57b9ead60a6b7ecdbb775b165356e87ecd5db9efd4b227ebe8c4f`.

For the measured Crucial capacity of 2,000,398,934,016 bytes, ROS0's emergency program would fail the original capacity comparison if that program were executed with that returned capacity. ROS1/P1's comparison would accept it. The retained evidence does not choose an unobserved runtime path between these cases. A narrow diagnostic that identifies the executing image and records its actual device-info/capacity decision remains warranted before a further compatibility patch.
