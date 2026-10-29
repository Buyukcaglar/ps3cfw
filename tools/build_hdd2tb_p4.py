"""P3 plus bounded LV2 mount aggregate ceiling; regular-file firmware build only.

SPDX-License-Identifier: GPL-2.0-only. No physical disk, key, or USB access.
"""
import argparse, hashlib, json, struct, zlib
from pathlib import Path
import build_hdd2tb_p1 as base
ROOT=base.ROOT
P3_SHA='9197335b04b6cdf8c40393d6375dd6ee77d2f62fc85da5cac0989d012ed00eaa'
LV2_SHA='3aaab44f55c2187864e758d84e9db022f1a9e40465addf06d95b15b0723122a9'
PATCH_OFFSET=0x2dac74

def plain_lv2(blob):
    start,end=0x20+base.number(blob,12,4),base.number(blob,16,8)
    app=base.number(blob,0x28,8)
    assert base.number(blob,app+12,4)==3
    matches=[]
    for k in base.keysets(ROOT/'tools/scetool_keys/PS3/data/keys'):
        if k.get('self_type',k.get('program_type'))!='LV2': continue
        m=base.AES.new(bytes.fromhex(k['erk']),base.AES.MODE_CBC,bytes.fromhex(k['riv'])).decrypt(blob[start:start+64])
        if m[16:32]==m[48:64]==bytes(16): matches.append(m)
    assert matches and len(set(matches))==1
    m=matches[0];p=bytearray(blob);p[start:start+64]=m
    p[start+64:end]=base.ctr(m[:16],m[32:48],blob[start+64:end])
    count=base.number(p,start+76,4); assert count==3
    return p,start,end,start+96+48*count

def code(blob):
    p,s,e,t=plain_lv2(blob);sec=s+96
    off,n=base.number(p,sec,8),base.number(p,sec+8,8)
    assert [base.number(p,sec+i,4) for i in [16,20,24,32,44]]==[2,0,2,3,2]
    ki,vi=base.number(p,sec+36,4),base.number(p,sec+40,4)
    return base.ctr(p[t+16*ki:t+16*(ki+1)],p[t+16*vi:t+16*(vi+1)],blob[off:off+n])

def focused_lv2(template,stream,old,new):
    p,s,e,t=plain_lv2(template); original=bytes(p);sec=s+96
    off,n=base.number(p,sec,8),base.number(p,sec+8,8)
    nextoff=base.number(p,sec+48,8)
    assert off==e and len(stream)<=nextoff-off and len(old)==len(new)
    ph=base.number(old,32,8);assert base.number(old,ph,4)==1
    poff,plen=base.number(old,ph+8,8),base.number(old,ph+32,8)
    assert poff==0x10000 and zlib.decompress(code(template))==old[poff:poff+plen]
    assert zlib.decompress(stream)==new[poff:poff+plen]
    ci=base.number(p,0x58,8);end=ci+base.number(p,0x60,8);digests=0
    while ci<end:
        kind,size=base.number(p,ci,4),base.number(p,ci+4,4)
        assert size>=16 and ci+size<=end
        if kind==2:
            assert size==64 and p[ci+36:ci+56]==hashlib.sha1(old).digest()
            p[ci+36:ci+56]=hashlib.sha1(new).digest();digests+=1
        ci+=size
    assert ci==end and digests==1
    struct.pack_into('>Q',p,sec+8,len(stream))
    si=base.number(p,0x48,8)
    assert base.number(p,si,8)==off and base.number(p,si+8,8)==n
    struct.pack_into('>Q',p,si+8,len(stream))
    hi,ki,vi=[base.number(p,sec+i,4) for i in [28,36,40]]
    at=t+16*hi;p[at:at+32]=base.hmac.digest(p[at+32:at+96],stream,'sha1')+bytes(12)
    result=bytearray(template);result[:s]=p[:s]
    result[s+64:e]=base.ctr(p[s:s+16],p[s+32:s+48],p[s+64:e])
    result[off:off+len(stream)]=base.ctr(p[t+16*ki:t+16*(ki+1)],p[t+16*vi:t+16*(vi+1)],stream)
    sig=base.number(p,s+64,8)
    assert p[sig:sig+42]==original[sig:sig+42]
    assert len(result)==len(template) and result[nextoff:]==template[nextoff:]
    assert result[s:s+64]==template[s:s+64]
    return bytes(result)

def main(work,dest):
    assert base.sys.flags.optimize==0
    for p,h in base.TOOL_PINS.items(): assert base.sha(p.read_bytes())==h
    assert base.sha((ROOT/'tools/build_hdd2tb_p1.py').read_bytes())=='fe4cde05884e5dcf8f9b399ee85c7835801d17c3cd390d187e749fbb20d75499'
    work.mkdir(parents=True,exist_ok=False)
    if dest.exists(): assert not any(dest.iterdir()), 'Candidate destination must be empty'
    else: dest.mkdir(parents=True)
    original=base.SOURCE.read_bytes();assert base.sha(original)==base.SOURCE_SHA
    p3=(ROOT/'candidates/HDD2TB-P3/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();assert base.sha(p3)==P3_SHA
    entries={e['id']:e['data'] for e in base.pup_entries(p3)}
    assert base.rebuild_pup(p3,{})==p3
    update=base.tar_members(entries[0x300]);heads=base.tar_members(entries[0x501])
    rawpkg=update['CORE_OS_PACKAGE.pkg'];info0,info1,content=base.package_parts(rawpkg)
    files=dict(base.pkg_reader.cosunpkg_files(content));assert len(files)==25
    source=files['lv2_kernel.self'];(work/'lv2-original.self').write_bytes(source)
    base.decode(work/'lv2-original.self',work/'lv2-original.elf')
    old=(work/'lv2-original.elf').read_bytes();assert base.sha(old)==LV2_SHA
    assert old[PATCH_OFFSET:PATCH_OFFSET+12].hex()=='3c0000027f9d0040419d0270'
    target=bytearray(old);target[PATCH_OFFSET+3]=3;target=bytes(target)
    assert [i for i,(a,b) in enumerate(zip(old,target)) if a!=b]==[PATCH_OFFSET+3]
    (work/'lv2-patched.elf').write_bytes(target)
    native_template=bytearray(source)
    app=base.number(native_template,0x28,8)
    assert base.number(native_template,app+16,8)==0x0004009300000000
    struct.pack_into('>Q',native_template,app+16,0x0004008200000000)
    (work/'lv2-native-template.self').write_bytes(native_template)
    for label in ['original','patched']:
        # Native encoder's key database stops at4.82 for LV2. This version is
        # used ONLY in a scratch native template to obtain DEFLATE streams.
        # CLI version flags are overridden by the template in this encoder.
        # focused_lv2 retains every original4.93 public version/loader field.
        base.run([base.SCETOOL,'-0','SELF','-1','TRUE','-s','TRUE','-7','TRUE',
                  '-t',work/'lv2-native-template.self','-e',work/f'lv2-{label}.elf',work/f'lv2-{label}-native.self'],
                 work/f'lv2-{label}-encode.log')
    control=code((work/'lv2-original-native.self').read_bytes())
    assert control==code(source) and focused_lv2(source,control,old,old)==source
    stream=code((work/'lv2-patched-native.self').read_bytes())
    p,s,e,t=plain_lv2(source);available=base.number(p,s+144,8)-base.number(p,s+96,8)
    compression={'native_size':len(stream),'available_slot':available,'method':'native scetool'}
    if len(stream)>available:
        ph=base.number(old,32,8);off,n=base.number(old,ph+8,8),base.number(old,ph+32,8)
        stream=zlib.compress(target[off:off+n],9)
        compression.update(method='zlib level9',runtime=zlib.ZLIB_RUNTIME_VERSION)
    compression['selected_size']=len(stream);assert len(stream)<=available
    candidate=focused_lv2(source,stream,old,target);(work/'lv2-candidate.self').write_bytes(candidate)
    base.decode(work/'lv2-candidate.self',work/'lv2-python.elf')
    base.run([base.SCETOOL,'-d',work/'lv2-candidate.self',work/'lv2-native.elf'],work/'lv2-decode.log')
    assert (work/'lv2-native.elf').read_bytes()==(work/'lv2-python.elf').read_bytes()==target
    changes=[];newcontent=bytearray(content)
    for i in range(base.pkg_reader.be32(content,4)):
        entry=0x10+0x30*i
        name=content[entry+16:entry+48].rstrip(bytes(1)).decode('ascii')
        if name=='lv2_kernel.self':
            off,n=base.pkg_reader.be64(content,entry),base.pkg_reader.be64(content,entry+8)
            assert n==len(source)==len(candidate) and content[off:off+n]==source
            newcontent[off:off+n]=candidate;changes.append(name)
    assert changes==['lv2_kernel.self']
    check=dict(base.pkg_reader.cosunpkg_files(newcontent))
    assert [n for n in files if files[n]!=check[n]]==['lv2_kernel.self']
    native,_=base.native_pkg(info0,info1,content,work/'control-pkg')
    assert base.template_pkg(rawpkg,native)==rawpkg
    native,_=base.native_pkg(info0,info1,newcontent,work/'candidate-pkg')
    pkg=base.template_pkg(rawpkg,native);pkgpath=work/'CORE_OS_PACKAGE.pkg';pkgpath.write_bytes(pkg)
    base.run([base.SPKGTOOL,pkgpath],work/'spkg.log');head=Path(str(pkgpath)+'.spkg_hdr.1').read_bytes()
    assert base.package_parts(pkg)[2]==newcontent
    u=base.replace_tar(entries[0x300],'CORE_OS_PACKAGE.pkg',pkg)
    h=base.replace_tar(entries[0x501],'CORE_OS_PACKAGE.pkg.spkg_hdr.1',head)
    pup=base.rebuild_pup(p3,{0x300:u,0x501:h});path=dest/'PS3/UPDATE/PS3UPDAT.PUP'
    path.parent.mkdir(parents=True);path.write_bytes(pup)
    manifest=dict(candidate='HDD2TB-P4',stage='built; separate audit/review pending',
                  source_sha256=base.SOURCE_SHA,parent_candidate_sha256=P3_SHA,
                  candidate_sha256=base.sha(pup),candidate_size=len(pup),candidate_md5=hashlib.md5(pup).hexdigest(),
                  purpose='P3 admission plus LV2 aggregate mount ceiling192KiB; preserved formatted Crucial boot experiment',
                  lv2_original_elf_sha256=LV2_SHA,lv2_patched_elf_sha256=base.sha(target),
                  lv2_candidate_self_sha256=base.sha(candidate),
                  patch=dict(virtual_address='0x80000000002cac74',elf_offset=PATCH_OFFSET,
                             before='3c000002',after='3c000003',actual_changed_offset=PATCH_OFFSET+3,
                             aggregate_limit_before=131072,aggregate_limit_after=196608),
                  compression=compression,changed_from_P3=['lv2_kernel.self'],
                  controls=dict(no_change_PUP_identical=True,no_change_SELF_identical=True,
                                no_change_PKG_identical=True,native_python_full_ELF_equal=True),
                  self_signature_treatment='Retain already-invalid supplied LV2 signature; inherited CFW loader acceptance required',
                  stable_storage_support=False,hardware_tested=False,
                  tools={str(p.relative_to(ROOT)):base.sha(p.read_bytes()) for p in [Path(__file__),ROOT/'tools/build_hdd2tb_p1.py',*base.TOOL_PINS]})
    base.save_json(dest/'build-manifest.json',manifest)
    (dest/'SHA256SUMS.txt').write_text(base.sha(pup).upper()+'  PS3/UPDATE/PS3UPDAT.PUP\n')
    assert base.sha(base.SOURCE.read_bytes())==base.SOURCE_SHA
    print(json.dumps({k:manifest[k] for k in ['candidate','candidate_sha256','candidate_size','lv2_patched_elf_sha256','compression']},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,default=ROOT/'analysis/build-p4');ap.add_argument('--dest',type=Path,default=ROOT/'candidates/HDD2TB-P4');a=ap.parse_args()
    assert a.work.resolve().is_relative_to(ROOT/'analysis') and a.dest.resolve().is_relative_to(ROOT/'candidates')
    main(a.work,a.dest)
