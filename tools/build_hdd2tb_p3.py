"""Composite 1984 GiB admission experiment; regular-file copies only.

Reuses P1's exact reviewed emergency SELF and surgically changes two constants
in supplied sysconf_plugin. No diagnostic, checker, geometry or updater edits.
Never stages USB or operates on physical devices. SPDX-License-Identifier: GPL-2.0-only
"""
import argparse
import hashlib
import io
import json
import struct
import tarfile
import zlib
from pathlib import Path
import build_hdd2tb_p1 as base

ROOT=base.ROOT
PKG_NAME='dev_flash_005.tar.aa.2026_01_08_191610'
MEMBER='dev_flash/vsh/module/sysconf_plugin.sprx'
OLD_SELF_SHA='aea64c000bbd33b953bb4bd46eaecaadc88a35d2049e1d6b05aa280c7cb97502'
OLD_ELF_SHA='89f2f34dd8aebdc951bd4506eba0b66f8284925d544f1825dc2c434fe266659b'
P1_SHA='f7abf409c9f0b6d04b5d9f8f44fb76142363759beb3dd8f060ec1a2dc5400f68'
P1_BUILDER_SHA='fe4cde05884e5dcf8f9b399ee85c7835801d17c3cd390d187e749fbb20d75499'
PATCHES=[(0x4e37c,bytes.fromhex('39200182'),bytes.fromhex('392001f0')),
         (0x4e38c,bytes.fromhex('65298000'),bytes.fromhex('65290000'))]

def first_load(elf):
    phoff=base.number(elf,32,8)
    assert base.number(elf,54,2)==56
    assert base.number(elf,phoff,4)==1
    return base.number(elf,phoff+8,8),base.number(elf,phoff+32,8)

def focused_prx(template,stream,old,new):
    """Preserve SELF slot/layout; first PRX segment starts at ELF offset0xf0."""
    assert len(old)==len(new)
    plain,start,end,table=base.self_plain(template)
    section=start+96
    off,oldsize=base.number(plain,section,8),base.number(plain,section+8,8)
    nextoff=base.number(plain,section+48,8)
    poff,plen=first_load(old)
    assert end<=off and poff==0xf0 and len(stream)<=nextoff-off
    assert zlib.decompress(base.compressed_code(template))==old[poff:poff+plen]
    assert zlib.decompress(stream)==new[poff:poff+plen]
    ci=base.number(plain,0x58,8);ciend=ci+base.number(plain,0x60,8);digest_count=0
    while ci<ciend:
        kind,size=base.number(plain,ci,4),base.number(plain,ci+4,4)
        assert size>=16 and ci+size<=ciend
        if kind==2:
            assert size==64 and plain[ci+36:ci+56]==hashlib.sha1(old).digest()
            plain[ci+36:ci+56]=hashlib.sha1(new).digest();digest_count+=1
        ci+=size
    assert ci==ciend and digest_count==1
    struct.pack_into('>Q',plain,section+8,len(stream))
    si=base.number(plain,0x48,8)
    assert base.number(plain,si,8)==off and base.number(plain,si+8,8)==oldsize
    struct.pack_into('>Q',plain,si+8,len(stream))
    hi,ki,vi=(base.number(plain,section+x,4) for x in (28,36,40))
    at=table+16*hi
    plain[at:at+32]=base.hmac.digest(plain[at+32:at+96],stream,'sha1')+bytes(12)
    result=bytearray(template)
    result[:start]=plain[:start]
    result[start+64:end]=base.ctr(plain[start:start+16],plain[start+32:start+48],plain[start+64:end])
    result[off:off+len(stream)]=base.ctr(plain[table+16*ki:table+16*(ki+1)],plain[table+16*vi:table+16*(vi+1)],stream)
    signed=base.number(plain,start+64,8)
    original_plain,*_=base.self_plain(template)
    assert plain[signed:signed+42]==original_plain[signed:signed+42]
    assert result[nextoff:]==template[nextoff:] and len(result)==len(template)
    assert result[start:start+64]==template[start:start+64]
    assert result[end:off]==template[end:off], 'Preserve PRX metadata-to-payload alignment gap'
    return bytes(result)

def replace_flash(content,original,replacement):
    assert len(original)==len(replacement)
    with tarfile.open(fileobj=io.BytesIO(content),mode='r:') as t:
        members=t.getmembers()
        assert all(m.isfile() or m.isdir() for m in members)
        found=[m for m in members if m.name==MEMBER]
        assert len(found)==1 and found[0].isfile()
        member=found[0]
        assert member.size==len(original) and t.extractfile(member).read()==original
        offset=member.offset_data
    assert content[offset:offset+len(original)]==original
    result=content[:offset]+replacement+content[offset+len(original):]
    assert len(result)==len(content)
    return result,offset

def main(work,dest):
    assert base.sys.flags.optimize==0
    assert base.sha((ROOT/'tools/build_hdd2tb_p1.py').read_bytes())==P1_BUILDER_SHA
    for tool,digest in base.TOOL_PINS.items(): assert base.sha(tool.read_bytes())==digest
    work.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
    source=base.SOURCE.read_bytes();assert base.sha(source)==base.SOURCE_SHA
    entries={e['id']:e['data'] for e in base.pup_entries(source)}
    assert base.rebuild_pup(source,{})==source
    update=base.tar_members(entries[0x300]);heads=base.tar_members(entries[0x501])
    p1=(ROOT/'candidates/HDD2TB-P1/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();assert base.sha(p1)==P1_SHA
    p1entries={e['id']:e['data'] for e in base.pup_entries(p1)}
    p1update=base.tar_members(p1entries[0x300]);p1heads=base.tar_members(p1entries[0x501])
    p1core=p1update['CORE_OS_PACKAGE.pkg'];p1head=p1heads['CORE_OS_PACKAGE.pkg.spkg_hdr.1']
    oldcore=base.package_parts(update['CORE_OS_PACKAGE.pkg'])[2];newcore=base.package_parts(p1core)[2]
    oldfiles=dict(base.pkg_reader.cosunpkg_files(oldcore));newfiles=dict(base.pkg_reader.cosunpkg_files(newcore))
    assert [n for n in oldfiles if oldfiles[n]!=newfiles[n]]==['emer_init.self']
    assert base.sha(newfiles['emer_init.self'])=='0e47265423f2d041d2da770d451376f69667269f35fe4cd6e349e8e2c318c639'
    rawpkg=update[PKG_NAME]
    assert base.sha(rawpkg)=='6775bd8b028bebe7a169aa682de2aa85b68abd06ff0f91d482dc91cc8b1788b3'
    info0,info1,content=base.package_parts(rawpkg)
    with tarfile.open(fileobj=io.BytesIO(content),mode='r:') as t: original=t.extractfile(MEMBER).read()
    assert base.sha(original)==OLD_SELF_SHA
    (work/'sysconf-original.self').write_bytes(original)
    base.decode(work/'sysconf-original.self',work/'sysconf-original.elf')
    old=(work/'sysconf-original.elf').read_bytes();assert base.sha(old)==OLD_ELF_SHA
    target=bytearray(old)
    for off,before,after in PATCHES:
        assert target[off:off+4]==before
        target[off:off+4]=after
    target=bytes(target);assert [i for i,(a,b) in enumerate(zip(old,target)) if a!=b]==[0x4e37f,0x4e38e]
    (work/'sysconf-patched.elf').write_bytes(target)
    for label in ('original','patched'):
        base.run([base.SCETOOL,'-0','SELF','-1','TRUE','-s','TRUE','-7','TRUE',
                  '-t',work/'sysconf-original.self','-e',work/f'sysconf-{label}.elf',work/f'sysconf-{label}-native.self'],
                  work/f'sysconf-{label}-encode.log')
    control_stream=base.compressed_code((work/'sysconf-original-native.self').read_bytes())
    assert control_stream==base.compressed_code(original),'Native no-change segment compression differs'
    assert focused_prx(original,control_stream,old,old)==original
    stream=base.compressed_code((work/'sysconf-patched-native.self').read_bytes())
    plain,start,_,_=base.self_plain(original)
    available=base.number(plain,start+96+48,8)-base.number(plain,start+96,8)
    compression={'native_stream_size':len(stream),'available_slot':available,'method':'native scetool'}
    if len(stream)>available:
        poff,plen=first_load(old)
        encoder=zlib.compressobj(9,zlib.DEFLATED,15,8,zlib.Z_DEFAULT_STRATEGY)
        stream=encoder.compress(target[poff:poff+plen])+encoder.flush()
        compression.update(method='standard DEFLATE zlib-ng level9',runtime=zlib.ZLIB_RUNTIME_VERSION)
    compression['selected_size']=len(stream);assert len(stream)<=available
    candidate=focused_prx(original,stream,old,target)
    (work/'sysconf-candidate.self').write_bytes(candidate)
    base.decode(work/'sysconf-candidate.self',work/'sysconf-candidate-python.elf')
    base.run([base.SCETOOL,'-d',work/'sysconf-candidate.self',work/'sysconf-candidate-native.elf'],work/'sysconf-candidate-decode.log')
    assert (work/'sysconf-candidate-python.elf').read_bytes()==(work/'sysconf-candidate-native.elf').read_bytes()==target
    assert replace_flash(content,original,original)[0]==content
    changed_content,tar_offset=replace_flash(content,original,candidate)
    native_control,_=base.native_pkg(info0,info1,content,work/'flash-control-pkg')
    assert base.template_pkg(rawpkg,native_control)==rawpkg
    native_pkg,_=base.native_pkg(info0,info1,changed_content,work/'flash-candidate-pkg')
    newpkg=base.template_pkg(rawpkg,native_pkg)
    pkgpath=work/PKG_NAME;pkgpath.write_bytes(newpkg)
    base.run([base.SPKGTOOL,pkgpath],work/'flash-spkg.log')
    newhead=Path(str(pkgpath)+'.spkg_hdr.1').read_bytes()
    assert base.package_parts(newpkg)[2]==changed_content
    newupdate=base.replace_tar(entries[0x300],'CORE_OS_PACKAGE.pkg',p1core)
    newupdate=base.replace_tar(newupdate,PKG_NAME,newpkg)
    newheads=base.replace_tar(entries[0x501],'CORE_OS_PACKAGE.pkg.spkg_hdr.1',p1head)
    newheads=base.replace_tar(newheads,PKG_NAME+'.spkg_hdr.1',newhead)
    pup=base.rebuild_pup(source,{0x300:newupdate,0x501:newheads})
    path=dest/'PS3/UPDATE/PS3UPDAT.PUP';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(pup)
    manifest={'candidate':'HDD2TB-P3','stage':'built; separate parser/code/crypto audit pending',
        'source_sha256':base.SOURCE_SHA,'candidate_sha256':base.sha(pup),'candidate_md5':hashlib.md5(pup).hexdigest(),'candidate_size':len(pup),
        'purpose':'Native 2 TB admission experiment: emergency and sysconf limits both 1984 GiB',
        'gate_bytes':0x1f0<<32,'gate_GiB':1984,
        'emergency_component':'Exact reviewed P1 CoreOS PKG/SPKG; sole original ELF byte0x3619b 80->f0',
        'flash_package':PKG_NAME,'flash_member':MEMBER,'flash_member_content_offset':tar_offset,
        'sysconf_self_sha256':base.sha(candidate),'sysconf_elf_sha256':base.sha(target),
        'sysconf_patches':[{'elf_offset':o,'virtual_address':o-0xf0,'before':b.hex(),'after':a.hex()} for o,b,a in PATCHES],
        'actual_changed_sysconf_ELF_offsets':[0x4e37f,0x4e38e],
        'compression':compression,'changed_pup_entries':['0x300','0x501'],
        'changed_update_members':['CORE_OS_PACKAGE.pkg',PKG_NAME],
        'controls':{'no_change_PUP_identical':True,'native_no_change_PRX_compression_identical':True,
                    'focused_PRX_no_change_identical':True,'flash_tar_no_change_identical':True,
                    'flash_PKG_no_change_identical':True,'native_and_python_full_PRX_decode_equal':True},
        'self_signature_treatment':'Retain signature bytes; changed PRX signature validity must be separately audited; requires inherited CFW verifier overrides',
        'hardware_tested':False,'stable_storage_support':False,
        'tools':{str(p.relative_to(ROOT)):base.sha(p.read_bytes()) for p in [Path(__file__),ROOT/'tools/build_hdd2tb_p1.py',*base.TOOL_PINS]}}
    base.save_json(dest/'build-manifest.json',manifest)
    (dest/'SHA256SUMS.txt').write_text(base.sha(pup).upper()+'  PS3/UPDATE/PS3UPDAT.PUP\n',encoding='ascii')
    assert base.sha(base.SOURCE.read_bytes())==base.SOURCE_SHA
    print(json.dumps({k:manifest[k] for k in ['candidate','candidate_sha256','candidate_size','sysconf_elf_sha256','compression']},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,default=ROOT/'analysis/build-p3');ap.add_argument('--dest',type=Path,default=ROOT/'candidates/HDD2TB-P3');a=ap.parse_args()
    assert a.work.resolve().is_relative_to(ROOT/'analysis') and a.dest.resolve().is_relative_to(ROOT/'candidates')
    assert a.dest.resolve() not in (ROOT/'candidates/HDD2TB-P1',ROOT/'candidates/HDD2TB-P2D')
    main(a.work,a.dest)
