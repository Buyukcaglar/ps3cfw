"""Extract the supplied PUP into analysis, with integrity and provenance records.

No raw-device access, firmware patching, or archive-controlled output paths.
PKG decryption uses the reviewed PS3DumpChecker port of fail0verflow ps3tools.
"""
import hashlib
import hmac
import io
import json
import struct
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'tools/python_packages'), str(ROOT / 'tools/PS3DumpChecker/tools')]
import coreos_decrypt as pkgtool
from Crypto.Cipher import AES

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fast_ctr(key, iv, data):
    return AES.new(key, AES.MODE_CTR, nonce=b'', initial_value=int.from_bytes(iv, 'big')).decrypt(data)

# Verify the optimized CTR path against the reviewed implementation, including
# carry across the low 64 counter bits, before replacing its slow byte loop.
for iv in (bytes(16), bytes.fromhex('0000000000000000ffffffffffffffff')):
    sample = bytes(range(256))
    assert fast_ctr(bytes(16), iv, sample) == pkgtool.aes128ctr(bytes(16), iv, sample)
pkgtool.aes128ctr = fast_ctr

PUP = ROOT / 'CFW 4.93 Evilnat Cobra 8.5 [CEX]/PS3/UPDATE/PS3UPDAT.PUP'
OUT = ROOT / 'analysis'
OUT.mkdir(exist_ok=True)
data, entries = pkgtool.parse_pup(PUP)
count = len(entries)
header_len = pkgtool.be64(data, 0x20)
data_len = pkgtool.be64(data, 0x28)
assert header_len + data_len == len(data)
assert 0x30 + count * 0x40 + 0x20 <= header_len
key = (ROOT / 'tools/ps3keys/pup-hmac').read_bytes()
assert len(key) == 64
digest_table = {}
for i in range(count):
    offset = 0x30 + count * 0x20 + i * 0x20
    index = pkgtool.be64(data, offset)
    assert index not in digest_table
    digest_table[index] = data[offset + 8:offset + 28]
assert set(digest_table) == set(range(count))
header_end = 0x30 + count * 0x40
header_hmac_ok = hmac.compare_digest(hmac.digest(key, data[:header_end], 'sha1'), data[header_end:header_end + 20])
assert header_hmac_ok, 'PUP header HMAC mismatch'
names = {0x100:'version.txt', 0x101:'license.txt', 0x103:'update_flags.txt',
         0x200:'ps3swu.self', 0x201:'vsh.tar', 0x202:'dots.txt',
         0x300:'update_files.tar', 0x501:'spkg_hdr.tar', 0x601:'ps3swu2.self'}
entry_records = []
pupout = OUT / 'pup'
pupout.mkdir(exist_ok=True)
for index, entry in enumerate(entries):
    off, size = entry['offset'], entry['length']
    assert header_len <= off <= len(data) and size <= len(data) - off
    blob = data[off:off + size]
    ok = hmac.compare_digest(hmac.digest(key, blob, 'sha1'), digest_table[index])
    assert ok, f'Entry {index} HMAC mismatch'
    name = names.get(entry['id'], f'entry_{entry["id"]:x}.bin')
    (pupout / name).write_bytes(blob)
    entry_records.append(dict(entry, name=name, sha256=sha(blob), hmac_ok=ok))

def extract_tar(blob, destination):
    records = []
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:') as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            assert member.isfile(), f'Unsupported archive member {member.name!r}'
            parts = PurePosixPath(member.name).parts
            assert parts and not member.name.startswith('/') and not any(p in ('..', '.') or ':' in p or '\\' in p for p in parts)
            target = destination.joinpath(*parts)
            assert target.resolve().is_relative_to(destination.resolve())
            content = archive.extractfile(member).read()
            assert len(content) == member.size
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            records.append({'path': member.name, 'size': len(content), 'sha256': sha(content)})
    return records

updates = extract_tar((pupout / 'update_files.tar').read_bytes(), OUT / 'update_files')
packages = []
for record in updates:
    if not record['path'].startswith('dev_flash'):
        continue
    pkgpath = OUT / 'update_files' / record['path']
    pkg = bytearray(pkgpath.read_bytes())
    assert pkg[:4] == b'SCE\0' and pkgtool.be16(pkg, 0xA) == 3
    revision = pkgtool.sce_decrypt_header(pkg)
    assert revision >= 0, f'Cannot decrypt {pkgpath}'
    pkgtool.sce_decrypt_data(pkg)
    content = pkgtool.unpkg_content(pkg)
    files = extract_tar(content, OUT / 'flash')
    packages.append({'package': record['path'], 'key_revision': revision, 'content_sha256': sha(content), 'files': files})
    print(record['path'], len(files), 'files', flush=True)

manifest = {'input': str(PUP), 'size': len(data), 'sha256': sha(data),
            'md5': hashlib.md5(data).hexdigest(), 'companion_md5_matches': hashlib.md5(data).hexdigest().upper() == (PUP.parents[2] / 'md5.txt').read_text().strip().upper(),
            'version': (pupout/'version.txt').read_text(), 'header_hmac_ok': header_hmac_ok,
            'hmac_scope': 'Integrity under public PUP key; not author authenticity or installation safety',
            'entries': entry_records, 'update_files': updates, 'flash_packages': packages}
assert manifest['companion_md5_matches']
(OUT/'pup-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('PUP header and all', count, 'entry HMACs passed; extracted', sum(len(x['files']) for x in packages), 'flash files')
