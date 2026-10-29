"""Build the bounded CECHA00 2 TB admission experiment on regular files only.

SPDX-License-Identifier: GPL-2.0-only
Format references: naehrwert/scetool, fail0verflow ps3tools and Evilnat's
PKG/SPKG tools. Public crypto material stays in the pinned vendor directories.
This builder deliberately retains the baseline's already-invalid SELF ECDSA
signature and relies on the baseline's independently observed CFW override.
It does not claim an authentic Sony signature or hardware qualification.
"""
import hashlib
import hmac
import io
import json
import os
import struct
import subprocess
import sys
import tarfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'tools/python_packages'),
               str(ROOT / 'tools/PS3DumpChecker/tools'), str(ROOT / 'tools')]
from Crypto.Cipher import AES
import coreos_decrypt as pkg_reader
from decrypt_self import keysets, number, ctr, decode

SOURCE = ROOT / 'firmware/baseline-evilnat-4.93-cex/PS3/UPDATE/PS3UPDAT.PUP'
SOURCE_SHA = 'ad1c01f8aae443643d1c4b31f164fa1bb6b65c504bab9b238065830a5e8e3f9a'
ELF_SHA = 'ddd89c7d36765533a249a77878c68ac0b2fb9cd819b88527857a079e34f6564d'
SCETOOL = ROOT / 'tools/scetool_keys/Release/scetool.exe'
NEWPKG = ROOT / 'tools/mfw-builder/tools/new_pkg.exe'
SPKGTOOL = ROOT / 'tools/mfw-builder/tools/spkg.exe'
TOOL_PINS = {
    SCETOOL: 'e828a84482b917005c5ee66864646a7ddbec37d79a75bd38835fef84836304a5',
    NEWPKG: 'f07adf8e0165efca51de1892f63173653af45a1598aabffd9550f3bafefb0d64',
    SPKGTOOL: 'a8f74f5e2b9d548a6b5d2468d93baea91bd026c1c76736491ceef3d85b4658f9',
}
WORK = ROOT / 'analysis/build-p1'
DEST = ROOT / 'candidates/HDD2TB-P1'
PUP_KEY = (ROOT / 'tools/ps3keys/pup-hmac').read_bytes()
pkg_reader.aes128ctr = ctr


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def run(argv, log):
    env = dict(os.environ)
    env['PS3'] = str(ROOT / 'tools/scetool_keys/PS3/data')
    env['PS3_KEYS'] = str(ROOT / 'tools/mfw-builder/ps3keys')
    result = subprocess.run([str(a) for a in argv], env=env, cwd=ROOT,
                            capture_output=True, text=True, check=True)
    log.write_text(result.stdout + result.stderr, encoding='utf-8')


def pup_entries(data):
    assert data[:8] == b'SCEUF\0\0\0'
    count = number(data, 0x18, 8)
    header_size = number(data, 0x20, 8)
    assert header_size + number(data, 0x28, 8) == len(data)
    assert count == 9 and header_size == 656
    table_end = 0x30 + count * 64
    assert hmac.compare_digest(hmac.digest(PUP_KEY, data[:table_end], 'sha1'), data[table_end:table_end+20])
    result = []
    next_offset = header_size
    for i in range(count):
        ident, off, length, extra = struct.unpack_from('>4Q', data, 0x30 + 32*i)
        assert off == next_offset and off + length <= len(data)
        next_offset = off + length
        idx, digest = struct.unpack_from('>Q20s', data, 0x30 + 32*count + 32*i)
        assert idx == i
        blob = data[off:off+length]
        assert hmac.compare_digest(hmac.digest(PUP_KEY, blob, 'sha1'), digest)
        result.append({'id': ident, 'offset': off, 'length': length, 'extra': extra, 'data': blob})
    assert next_offset == len(data)
    assert [e['id'] for e in result] == [0x100,0x101,0x103,0x200,0x201,0x202,0x300,0x501,0x601]
    return result


def rebuild_pup(template, replacements):
    entries = pup_entries(template)
    assert set(replacements).issubset({e['id'] for e in entries})
    head = bytearray(template[:number(template, 0x20, 8)])
    blobs = []
    offset = len(head)
    for i, e in enumerate(entries):
        blob = replacements.get(e['id'], e['data'])
        struct.pack_into('>QQ', head, 0x30+32*i+8, offset, len(blob))
        head[0x30+32*len(entries)+32*i+8:0x30+32*len(entries)+32*i+28] = hmac.digest(PUP_KEY, blob, 'sha1')
        blobs.append(blob)
        offset += len(blob)
    struct.pack_into('>Q', head, 0x28, offset-len(head))
    end = 0x30 + 64*len(entries)
    head[end:end+20] = hmac.digest(PUP_KEY, head[:end], 'sha1')
    out = bytes(head) + b''.join(blobs)
    pup_entries(out)
    return out


def tar_members(data):
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
        result = {}
        for m in archive.getmembers():
            assert m.isfile() and m.name not in result
            result[m.name] = archive.extractfile(m).read()
    return result


def replace_tar(data, name, replacement):
    """Preserve every original tar header and member except size/checksum/data."""
    members = tar_members(data)
    assert name in members
    pos = 0
    found = False
    parts = []
    while pos + 512 <= len(data) and data[pos:pos+512] != bytes(512):
        header = bytearray(data[pos:pos+512])
        member = header[:100].split(b'\0',1)[0].decode('ascii')
        assert not header[345:500].strip(b'\0'), 'Unexpected tar prefix'
        size = int(header[124:136].split(b'\0',1)[0].strip() or b'0', 8)
        start, end = pos+512, pos+512+((size+511)//512)*512
        assert end <= len(data)
        if member == name:
            assert not found and data[start:start+size] == members[name]
            found = True
            if replacement == members[name]:
                parts.append(data[pos:end])
            else:
                header[124:136] = f'{len(replacement):011o}\0'.encode()
                assert len(header) == 512
                header[148:156] = b'        '
                header[148:156] = f'{sum(header):06o}\0 '.encode()
                parts.extend((bytes(header), replacement, bytes((-len(replacement)) % 512)))
        else:
            parts.append(data[pos:end])
        pos = end
    assert found and not any(data[pos:]), 'Nonzero unexpected tar suffix'
    parts.append(data[pos:])
    out = b''.join(parts)
    expected = dict(members)
    expected[name] = replacement
    assert tar_members(out) == expected
    return out


def self_plain(data):
    base, end = 0x20+number(data,12,4), number(data,16,8)
    matches = []
    for key in keysets(ROOT / 'tools/scetool_keys/PS3/data/keys'):
        if key.get('self_type', key.get('program_type')) != 'APP':
            continue
        meta = AES.new(bytes.fromhex(key['erk']), AES.MODE_CBC, bytes.fromhex(key['riv'])).decrypt(data[base:base+64])
        if meta[16:32] == bytes(16) and meta[48:64] == bytes(16):
            matches.append(meta)
    assert matches and len(set(matches)) == 1
    meta = matches[0]
    plain = bytearray(data)
    plain[base:base+64] = meta
    plain[base+64:end] = ctr(meta[:16], meta[32:48], data[base+64:end])
    count = number(plain, base+64+12, 4)
    table = base+64+32+48*count
    return plain, base, end, table


def compressed_code(data):
    plain, base, end, table = self_plain(data)
    section = base+64+32
    off, size = number(plain,section,8), number(plain,section+8,8)
    assert number(plain,section+16,4) == 2 and number(plain,section+20,4) == 0
    assert number(plain,section+32,4) == 3 and number(plain,section+44,4) == 2
    ki, vi = number(plain,section+36,4), number(plain,section+40,4)
    stream = ctr(plain[table+16*ki:table+16*(ki+1)], plain[table+16*vi:table+16*(vi+1)], data[off:off+size])
    return stream


def focused_self(template, stream, original_elf, target_elf):
    """Keep baseline header layout, keys, IVs, signature and other ciphertext."""
    assert len(original_elf) == len(target_elf)
    plain, base, end, table = self_plain(template)
    section = base+64+32
    off, oldsize = number(plain,section,8), number(plain,section+8,8)
    nextoff = number(plain, section+48, 8)
    assert off == end and len(stream) <= nextoff-off
    assert zlib.decompress(stream) == target_elf[:len(zlib.decompress(compressed_code(template)))]
    # Baseline digest2 is confirmed against the independently decoded full ELF.
    ci, ci_end = number(plain,0x58,8), number(plain,0x58,8)+number(plain,0x60,8)
    digest_offsets = []
    while ci < ci_end:
        kind, size = number(plain,ci,4), number(plain,ci+4,4)
        assert size >= 16 and ci+size <= ci_end
        if kind == 2:
            assert size == 64 and plain[ci+36:ci+56] == hashlib.sha1(original_elf).digest()
            plain[ci+36:ci+56] = hashlib.sha1(target_elf).digest()
            digest_offsets.append(ci+36)
        ci += size
    assert ci == ci_end and len(digest_offsets) == 1
    struct.pack_into('>Q', plain, section+8, len(stream))
    si = number(plain,0x48,8)
    assert number(plain,si,8) == off and number(plain,si+8,8) == oldsize
    struct.pack_into('>Q', plain, si+8, len(stream))
    hi,ki,vi = (number(plain,section+x,4) for x in (28,36,40))
    hash_offset = table+16*hi
    digest = hmac.digest(plain[hash_offset+32:hash_offset+96], stream, 'sha1')
    plain[hash_offset:hash_offset+32] = digest+bytes(12)
    result = bytearray(template)
    result[:base] = plain[:base]
    result[base+64:end] = ctr(plain[base:base+16], plain[base+32:base+48], plain[base+64:end])
    result[off:off+len(stream)] = ctr(plain[table+16*ki:table+16*(ki+1)], plain[table+16*vi:table+16*(vi+1)], stream)
    # Original signature is already invalid. Retain it and all surrounding data.
    signed_length = number(plain,base+64,8)
    original_plain, *_ = self_plain(template)
    assert plain[signed_length:signed_length+42] == original_plain[signed_length:signed_length+42]
    assert result[nextoff:] == template[nextoff:] and len(result) == len(template)
    assert result[base:base+64] == template[base:base+64]
    return bytes(result)


def package_parts(raw):
    data = bytearray(raw)
    assert pkg_reader.sce_decrypt_header(data) >= 0
    pkg_reader.sce_decrypt_data(data)
    content = pkg_reader.unpkg_content(data)
    # The original/native packages use these three fixed section positions.
    assert pkg_reader.be64(data,0x80) == 0x280
    assert pkg_reader.be64(data,0xb0) == 0x2c0
    return data[0x280:0x2c0], data[0x2c0:0x300], content


def native_pkg(info0, info1, content, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    for name, blob in (('info0',info0),('info1',info1),('content',content)):
        (outdir/name).write_bytes(blob)
    output = outdir / 'CORE_OS_PACKAGE.pkg'
    run([NEWPKG,'retail',outdir,output], outdir/'native-new-pkg.log')
    assert output.is_file() and Path(str(output)+'.spkg_hdr.1').stat().st_size == 640
    return output.read_bytes(), Path(str(output)+'.spkg_hdr.1').read_bytes()


def ec_add(x, y, p, a):
    if x is None:
        return y
    if y is None:
        return x
    if x[0] == y[0] and (x[1]+y[1]) % p == 0:
        return None
    if x == y:
        slope = (3*x[0]*x[0]+a) * pow(2*x[1],-1,p) % p
    else:
        slope = (y[1]-x[1]) * pow(y[0]-x[0],-1,p) % p
    rx = (slope*slope-x[0]-y[0]) % p
    return rx, (slope*(x[0]-rx)-x[1]) % p


def ec_mul(k, point, p, a):
    result = None
    while k:
        if k & 1:
            result = ec_add(result, point, p, a)
        point = ec_add(point, point, p, a)
        k >>= 1
    return result


def sign_pkg_header(header, siglen):
    """ECDSA with RFC6979/SHA1 nonce; public retail PKG key matches its pubkey.

    Signature verification is performed separately by audit_sce.py, with an
    original valid Sony-format PKG as its positive control.
    """
    directory = ROOT / 'tools/mfw-builder/ps3keys'
    ctype = int.from_bytes((directory/'pkg-ctype-retail').read_bytes(),'big')
    raw = (ROOT/'tools/scetool_keys/PS3/data/ldr_curves').read_bytes()[ctype*121:(ctype+1)*121]
    raw = bytes(b ^ 255 for b in raw)
    assert len(raw) == 121
    p,a,b,n,gx,gy = (number(raw,o,s) for o,s in ((0,20),(20,20),(40,20),(60,21),(81,20),(101,20)))
    private = int.from_bytes((directory/'pkg-priv-retail').read_bytes(),'big')
    public = (directory/'pkg-pub-retail').read_bytes()
    assert (gy*gy-gx*gx*gx-a*gx-b) % p == 0
    assert ec_mul(n,(gx,gy),p,a) is None
    assert ec_mul(private,(gx,gy),p,a) == (number(public,0,20),number(public,20,20))
    digest = hashlib.sha1(header[:siglen]).digest()
    qlen, rolen = n.bit_length(), (n.bit_length()+7)//8
    def bits2int(data):
        return int.from_bytes(data,'big') >> max(0,len(data)*8-qlen)
    seed = private.to_bytes(rolen,'big')+(bits2int(digest)%n).to_bytes(rolen,'big')
    v, k = b'\x01'*20, bytes(20)
    k = hmac.digest(k,v+b'\x00'+seed,'sha1')
    v = hmac.digest(k,v,'sha1')
    k = hmac.digest(k,v+b'\x01'+seed,'sha1')
    v = hmac.digest(k,v,'sha1')
    while True:
        t = b''
        while len(t) < rolen:
            v = hmac.digest(k,v,'sha1')
            t += v
        nonce = bits2int(t)
        if 1 <= nonce < n:
            r = ec_mul(nonce,(gx,gy),p,a)[0] % n
            s = pow(nonce,-1,n)*(bits2int(digest)+r*private) % n
            if r and s:
                return r.to_bytes(21,'big')+s.to_bytes(21,'big')
        k = hmac.digest(k,v+b'\x00','sha1')
        v = hmac.digest(k,v,'sha1')


def template_pkg(template, native):
    """Keep original PKG infos/layout/keys; adopt native compressed content.

    The bundled native new_pkg modifies info1+0x20 to compressed length whereas
    the supplied image and archived Evilnat source use 1. Do not adopt that
    native metadata change. Only actual compressed-length fields are updated.
    """
    plain = bytearray(template)
    assert pkg_reader.sce_decrypt_header(plain) >= 0
    pkg_reader.sce_decrypt_data(plain)
    generated = bytearray(native)
    assert pkg_reader.sce_decrypt_header(generated) >= 0
    pkg_reader.sce_decrypt_data(generated)
    assert number(plain,12,4) == 0 and number(plain,16,8) == 640
    assert number(plain,0x6c,4) == 3 and number(plain,0x70,4) == 20
    offset,size = number(generated,0xe0,8),number(generated,0xe8,8)
    assert offset == 0x300
    stream = bytes(generated[offset:offset+size])
    assert len(zlib.decompress(stream)) == number(plain,0x18,8)-0x80
    new = bytearray(plain[:0x300]) + stream
    struct.pack_into('>Q',new,0xe8,len(stream))
    struct.pack_into('>Q',new,0x280+0x20,len(stream))
    assert new[0x2c0:0x300] == plain[0x2c0:0x300]
    table = 0x80+3*48
    for i in range(3):
        section = 0x80+48*i
        off,sz,hi = number(new,section,8),number(new,section+8,8),number(new,section+28,4)
        start = table+16*hi
        new[start:start+32] = hmac.digest(new[start+32:start+96],new[off:off+sz],'sha1')+bytes(12)
    siglen = number(new,0x60,8)
    assert siglen == 0x250
    if new[:siglen] != plain[:siglen]:
        new[siglen:siglen+42] = sign_pkg_header(new,siglen)
    # Encrypt data using retained section keys/IVs, then metadata header.
    for i in range(3):
        section = 0x80+48*i
        if number(new,section+32,4) != 3:
            continue
        off,sz = number(new,section,8),number(new,section+8,8)
        ki,vi = number(new,section+36,4),number(new,section+40,4)
        new[off:off+sz] = ctr(new[table+16*ki:table+16*(ki+1)],new[table+16*vi:table+16*(vi+1)],new[off:off+sz])
    new[0x60:0x280] = ctr(new[0x20:0x30],new[0x40:0x50],new[0x60:0x280])
    new[0x20:0x60] = template[0x20:0x60]
    return bytes(new)


def main():
    assert sys.flags.optimize == 0, 'Assertions are required'
    for path, expected in TOOL_PINS.items():
        assert sha(path.read_bytes()) == expected, f'Native tool hash mismatch: {path.name}'
    WORK.mkdir(parents=True, exist_ok=True)
    DEST.mkdir(parents=True, exist_ok=True)
    original = SOURCE.read_bytes()
    assert sha(original) == SOURCE_SHA
    entries = {e['id']:e['data'] for e in pup_entries(original)}
    assert rebuild_pup(original,{}) == original
    update = tar_members(entries[0x300])
    spkg = tar_members(entries[0x501])
    raw_pkg = update['CORE_OS_PACKAGE.pkg']
    assert replace_tar(entries[0x300],'CORE_OS_PACKAGE.pkg',raw_pkg) == entries[0x300]
    assert replace_tar(entries[0x501],'CORE_OS_PACKAGE.pkg.spkg_hdr.1',spkg['CORE_OS_PACKAGE.pkg.spkg_hdr.1']) == entries[0x501]
    info0,info1,content = package_parts(raw_pkg)
    files = dict(pkg_reader.cosunpkg_files(content))
    assert len(files) == 25
    original_self = files['emer_init.self']
    (WORK/'original.self').write_bytes(original_self)
    decode(WORK/'original.self', WORK/'original.elf')
    original_elf = (WORK/'original.elf').read_bytes()
    assert sha(original_elf) == ELF_SHA
    assert original_elf[0x36198:0x361ac].hex() == '38000180e8810078780007c67fa40040419d00bc'
    patched_elf = bytearray(original_elf)
    patched_elf[0x3619b] = 0xf0
    (WORK/'patched.elf').write_bytes(patched_elf)
    for label, elf in (('control',WORK/'original.elf'),('patched',WORK/'patched.elf')):
        run([SCETOOL,'-0','SELF','-1','TRUE','-s','TRUE','-7','TRUE','-t',WORK/'original.self','-e',elf,WORK/f'{label}-native.self'],WORK/f'{label}-native.log')
    control_stream = compressed_code((WORK/'control-native.self').read_bytes())
    assert control_stream == compressed_code(original_self), 'Native no-change compression is not byte identical'
    assert focused_self(original_self,control_stream,original_elf,original_elf) == original_self
    stream = compressed_code((WORK/'patched-native.self').read_bytes())
    candidate_self = focused_self(original_self,stream,original_elf,patched_elf)
    (WORK/'candidate.self').write_bytes(candidate_self)
    decode(WORK/'candidate.self',WORK/'candidate-python.elf')
    run([SCETOOL,'-d',WORK/'candidate.self',WORK/'candidate-native.elf'], WORK/'candidate-native-decode.log')
    assert (WORK/'candidate-native.elf').read_bytes() == (WORK/'candidate-python.elf').read_bytes() == patched_elf
    changed = [i for i,(a,b) in enumerate(zip(original_elf,patched_elf)) if a != b]
    assert changed == [0x3619b]
    # Surgical CoreOS replacement; all entry lengths/offsets and padding retained.
    count = pkg_reader.be32(content,4)
    matches = []
    for i in range(count):
        entry = 0x10+0x30*i
        name = content[entry+16:entry+48].rstrip(b'\0').decode('ascii')
        if name == 'emer_init.self':
            matches.append((pkg_reader.be64(content,entry),pkg_reader.be64(content,entry+8)))
    assert len(matches) == 1
    off,size = matches[0]
    assert size == len(candidate_self) == len(original_self)
    new_content = bytearray(content)
    new_content[off:off+size] = candidate_self
    assert content[:off] == new_content[:off] and content[off+size:] == new_content[off+size:]
    # Native no-change PKG control exercises all crypto/structure regeneration.
    native_control,_ = native_pkg(info0,info1,content,WORK/'control-pkg')
    control_pkg = template_pkg(raw_pkg,native_control)
    assert control_pkg == raw_pkg, 'Template PKG no-change control must be byte identical'
    control_parts = package_parts(control_pkg)
    assert control_parts[0][:32] == info0[:32] and control_parts[1] == info1 and control_parts[2] == content
    native_candidate,_ = native_pkg(info0,info1,new_content,WORK/'candidate-pkg')
    candidate_pkg = template_pkg(raw_pkg,native_candidate)
    pkg_path = WORK/'CORE_OS_PACKAGE.pkg'
    pkg_path.write_bytes(candidate_pkg)
    run([SPKGTOOL,pkg_path],WORK/'native-spkg.log')
    candidate_spkg = Path(str(pkg_path)+'.spkg_hdr.1').read_bytes()
    assert package_parts(candidate_pkg)[2] == new_content
    new_update = replace_tar(entries[0x300],'CORE_OS_PACKAGE.pkg',candidate_pkg)
    new_spkg = replace_tar(entries[0x501],'CORE_OS_PACKAGE.pkg.spkg_hdr.1',candidate_spkg)
    result = rebuild_pup(original,{0x300:new_update,0x501:new_spkg})
    pup = DEST/'PS3/UPDATE/PS3UPDAT.PUP'
    pup.parent.mkdir(parents=True,exist_ok=True)
    pup.write_bytes(result)
    assert sha(SOURCE.read_bytes()) == SOURCE_SHA
    manifest = {
        'candidate':'HDD2TB-P1','stage':'software-built; independent final review pending; hardware untested',
        'source_sha256':SOURCE_SHA,'candidate_sha256':sha(result),'candidate_md5':hashlib.md5(result).hexdigest(),
        'candidate_size':len(result),'original_elf_sha256':ELF_SHA,'patched_elf_sha256':sha(patched_elf),
        'patch':{'module':'emer_init.self','elf_file_offset':'0x36198','virtual_address':'0x46198',
                 'before':'38000180','after':'380001f0','actual_changed_byte_offset':'0x3619b',
                 'old_capacity_bytes':0x180<<32,'new_capacity_bytes':0x1f0<<32},
        'self_treatment':{'layout_and_length_preserved':True,'original_metadata_keys_ivs_preserved':True,
                          'unchanged_section_ciphertexts_preserved':True,'existing_invalid_ecdsa_signature_retained':True,
                          'requires_existing_cfw_appldr_signature_override':True},
        'controls':{'pup_no_change_byte_identical':True,'tar_no_change_byte_identical':True,
                    'native_compression_no_change_byte_identical':True,'focused_self_no_change_byte_identical':True,
                    'template_pkg_no_change_byte_identical':True,'two_self_decoders_match':True},
        'pkg_treatment':{'original_info1_preserved':True,'original_layout_keys_ivs_preserved':True,
                         'ecdsa_regenerated_with_matching_public_retail_pkg_private_material':True,
                         'nonce_method':'RFC6979 SHA1','independent_signature_verification_pending':True},
        'tools':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (SCETOOL,NEWPKG,SPKGTOOL,Path(__file__))},
        'changed_pup_entries':['0x300/update_files.tar','0x501/spkg_hdr.tar'],
        'coreos_files':[{ 'name':name,'before_sha256':sha(blob),'after_sha256':sha(candidate_self if name=='emer_init.self' else blob)} for name,blob in files.items()],
        'hardware_tested':False,'stable_storage_support':False,
    }
    save_json(DEST/'build-manifest.json',manifest)
    (DEST/'SHA256SUMS.txt').write_text(sha(result).upper()+'  PS3/UPDATE/PS3UPDAT.PUP\n',encoding='ascii')
    print(json.dumps({k:manifest[k] for k in ('candidate','candidate_sha256','candidate_md5','candidate_size','patched_elf_sha256')},indent=2))


if __name__ == '__main__':
    main()
