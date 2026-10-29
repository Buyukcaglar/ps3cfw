"""Read-only SELF to ELF decoder for local cross-checking of scetool output.

Implements the metadata and ELF assembly described by naehrwert/scetool
sce.cpp/self.cpp (GPLv2). No signature verification, signing or patching.
"""
import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools/python_packages'))
from Crypto.Cipher import AES

def number(data, off, width):
    assert 0 <= off <= len(data) and width <= len(data) - off
    return int.from_bytes(data[off:off+width], 'big')

def keysets(path):
    current = None
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith(('#', ';')):
            continue
        if line.startswith('['):
            if current:
                yield current
            current = {'name': line.strip('[]')}
        elif '=' in line and current is not None:
            key, value = line.split('=', 1)
            current[key.strip()] = value.strip()
    if current:
        yield current

def ctr(key, iv, data):
    return AES.new(key, AES.MODE_CTR, nonce=b'', initial_value=int.from_bytes(iv, 'big')).decrypt(data)

def decode(path, output):
    data = path.read_bytes()
    assert data[:4] == b'SCE\0' and number(data, 10, 2) == 1
    base = 0x20 + number(data, 0xC, 4)
    end = number(data, 0x10, 8)
    assert base + 0x60 <= end <= len(data)
    app = number(data, 0x28, 8)
    kind = number(data, app + 12, 4)
    kind_name = {1:'LV0', 2:'LV1', 3:'LV2', 4:'APP', 5:'ISO', 6:'LDR', 7:'UNK_7', 8:'NPDRM'}[kind]
    assert kind_name != 'NPDRM', 'NPDRM layer is intentionally unsupported'
    matches = []
    for key in keysets(ROOT / 'tools/scetool_keys/PS3/data/keys'):
        if key.get('program_type', key.get('self_type')) != kind_name or 'erk' not in key or 'riv' not in key:
            continue
        meta = AES.new(bytes.fromhex(key['erk']), AES.MODE_CBC, bytes.fromhex(key['riv'])).decrypt(data[base:base+64])
        if meta[16:32] != bytes(16) or meta[48:64] != bytes(16):
            continue
        matches.append((key, meta))
    assert matches, 'No key yields the full metadata zero-padding pattern'
    # Multiple historical labels may share the same actual key. Report labels,
    # require identical metadata, and avoid treating labels as firmware proof.
    assert len({meta for _, meta in matches}) == 1
    meta = matches[0][1]
    header = ctr(meta[:16], meta[32:48], data[base+64:end])
    count, key_count = number(header, 12, 4), number(header, 16, 4)
    assert count <= 4096 and 32 + 48*count + 16*key_count <= len(header)
    key_table = header[32+48*count:32+48*count+16*key_count]
    elf_offset = number(data, 0x30, 8)
    phdr_offset = number(data, 0x38, 8)
    shdr_offset = number(data, 0x40, 8)
    assert data[elf_offset:elf_offset+6] == b'\x7fELF\x02\x02', 'Only ELF64 big endian is supported'
    elf_header = data[elf_offset:elf_offset+64]
    phoff = number(elf_header, 32, 8)
    shoff = number(elf_header, 40, 8)
    phsize, phnum = number(elf_header, 54, 2), number(elf_header, 56, 2)
    shsize, shnum = number(elf_header, 58, 2), number(elf_header, 60, 2)
    assert phsize == 56 and phnum < 4096
    phdr = data[phdr_offset:phdr_offset+phsize*phnum]
    assert len(phdr) == phsize*phnum
    result = bytearray(elf_header)
    def write(offset, content):
        assert 0 <= offset and offset + len(content) < 512*1024*1024
        if len(result) < offset + len(content):
            result.extend(bytes(offset+len(content)-len(result)))
        result[offset:offset+len(content)] = content
    write(phoff, phdr)
    sections = []
    for index in range(count):
        section = struct.unpack_from('>QQ8I', header, 32+48*index)
        off, size, stype, pindex, hashed, hashidx, encrypted, keyidx, ividx, compressed = section
        assert off <= len(data) and size <= len(data)-off
        blob = data[off:off+size]
        if encrypted == 3:
            assert keyidx < key_count and ividx < key_count
            blob = ctr(key_table[keyidx*16:(keyidx+1)*16], key_table[ividx*16:(ividx+1)*16], blob)
        else:
            assert encrypted == 1
        if compressed == 2:
            blob = zlib.decompress(blob)
        else:
            assert compressed == 1
        if stype == 2:
            assert pindex < phnum
            poff = number(phdr, pindex*56+8, 8)
            plen = number(phdr, pindex*56+32, 8)
            assert len(blob) == plen, f'Segment {pindex} length mismatch'
            write(poff, blob)
        sections.append({'index': index, 'type': stype, 'program_header_index': pindex,
                         'encrypted': encrypted, 'compressed': compressed,
                         'decoded_size': len(blob), 'sha256': hashlib.sha256(blob).hexdigest()})
    if shdr_offset:
        assert shdr_offset + shsize*shnum <= len(data)
        write(shoff, data[shdr_offset:shdr_offset+shsize*shnum])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result)
    return {'input': str(path), 'output': str(output), 'self_sha256': hashlib.sha256(data).hexdigest(),
            'elf_sha256': hashlib.sha256(result).hexdigest(), 'elf_size': len(result),
            'matching_key_labels': [{'name': key['name'], 'version': key.get('version')} for key, _ in matches],
            'sections': sections, 'signature_verified': False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(decode(args.input, args.output), indent=2))
