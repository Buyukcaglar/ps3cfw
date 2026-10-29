"""Read-only ELF mapping, PPC64 disassembly and bounded string references."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'python_packages'))
from capstone import Cs, CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN
from elftools.elf.elffile import ELFFile

parser = argparse.ArgumentParser()
parser.add_argument('file', type=Path)
parser.add_argument('--va', type=lambda x: int(x, 0))
parser.add_argument('--size', type=lambda x: int(x, 0), default=0x100)
args = parser.parse_args()
with args.file.open('rb') as stream:
    elf = ELFFile(stream)
    segments = [dict(s.header) for s in elf.iter_segments()]
    print(json.dumps({'file': str(args.file), 'sha256': hashlib.sha256(args.file.read_bytes()).hexdigest(),
                      'entry': hex(elf.header.e_entry), 'segments': segments}, indent=2))
    if args.va is not None:
        matches = [s for s in segments if s['p_type'] == 'PT_LOAD' and
                   s['p_vaddr'] <= args.va and args.va + args.size <= s['p_vaddr'] + s['p_filesz']]
        if len(matches) != 1:
            raise ValueError('VA range is not in exactly one file-backed PT_LOAD segment')
        seg = matches[0]
        offset = seg['p_offset'] + args.va - seg['p_vaddr']
        stream.seek(offset)
        blob = stream.read(args.size)
        print(f'file_offset={offset:#x}')
        dis = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)
        for ins in dis.disasm(blob, args.va):
            print(f'{ins.address:016x} {ins.bytes.hex()} {ins.mnemonic:10s} {ins.op_str}')
