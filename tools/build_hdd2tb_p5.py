"""P4 plus experimental fail-closed128MiB full-checker caller. Files only."""
import argparse,hashlib,json,struct,zlib
from pathlib import Path
import build_hdd2tb_p1 as base
import build_hdd2tb_p3 as flash
ROOT=base.ROOT
P4_SHA='d5dd8c6e34a1ac02f1e7706308df7f8c55bbcd882cd3447363aa97f17c7c67af'
OLD_SELF_SHA='29433c592e19906b316ebc63e3b6e6ea5b97b40ed8e8abb0480ac0358a5a1891'
OLD_ELF_SHA='48edc374dc3a113582445ec5964c562a934c5258b6a8b040d25126317aa25af9'
NEW_ELF_SHA='4e2cec9db3f1a50d99adadb62c8bf0f499aea65dea6fea6af29918f32e1d3e4e'
def segments(elf):
    ph=base.number(elf,32,8);n=base.number(elf,56,2)
    return [elf[base.number(elf,ph+i*56+8,8):base.number(elf,ph+i*56+8,8)+base.number(elf,ph+i*56+32,8)] for i in range(n)]
def streams(blob):
    p,s,e,t=base.self_plain(blob);result=[]
    for i in range(base.number(p,s+76,4)):
        q=s+96+i*48;off,n=base.number(p,q,8),base.number(p,q+8,8)
        assert base.number(p,q+32,4)==3 and base.number(p,q+44,4)==2
        ki,vi=base.number(p,q+36,4),base.number(p,q+40,4)
        result.append(base.ctr(p[t+16*ki:t+16*(ki+1)],p[t+16*vi:t+16*(vi+1)],blob[off:off+n]))
    return result
def focused(template,encoded,old,new):
    p,s,e,t=base.self_plain(template);original=bytes(p)
    assert base.number(p,0x18,8)==len(old)
    struct.pack_into('>Q',p,0x18,len(new))
    ph=base.number(new,32,8);n=base.number(new,56,2);assert n==3
    copy=base.number(p,0x38,8)
    assert p[copy:copy+56*n]==old[ph:ph+56*n]
    p[copy:copy+56*n]=new[ph:ph+56*n]
    ci=base.number(p,0x58,8);ciend=ci+base.number(p,0x60,8);digests=0
    while ci<ciend:
        kind,size=base.number(p,ci,4),base.number(p,ci+4,4)
        assert size>=16 and ci+size<=ciend
        if kind==2:
            assert p[ci+36:ci+56]==hashlib.sha1(old).digest()
            p[ci+36:ci+56]=hashlib.sha1(new).digest();digests+=1
        ci+=size
    assert digests==1
    result=bytearray(template);stats=[];oldseg,newseg=segments(old),segments(new)
    for i,stream in enumerate(encoded):
        q=s+96+i*48;off=base.number(p,q,8);oldsize=base.number(p,q+8,8)
        limit=base.number(p,q+48,8) if i<2 else len(template)
        assert zlib.decompress(stream)==newseg[i]
        method='native scetool'
        if len(stream)>limit-off:
            stream=zlib.compress(newseg[i],9);method='zlib level9'
        assert len(stream)<=limit-off
        struct.pack_into('>Q',p,q+8,len(stream))
        si=base.number(p,0x48,8)+i*32
        assert base.number(p,si,8)==off and base.number(p,si+8,8)==oldsize
        struct.pack_into('>Q',p,si+8,len(stream))
        hi,ki,vi=[base.number(p,q+x,4) for x in (28,36,40)]
        at=t+16*hi;p[at:at+32]=base.hmac.digest(p[at+32:at+96],stream,'sha1')+bytes(12)
        result[off:off+len(stream)]=base.ctr(p[t+16*ki:t+16*(ki+1)],p[t+16*vi:t+16*(vi+1)],stream)
        stats.append({'segment':i,'selected_size':len(stream),'slot':limit-off,'method':method})
    sig=base.number(p,s+64,8)
    assert p[sig:sig+42]==original[sig:sig+42]
    result[:s]=p[:s]
    result[s+64:e]=base.ctr(p[s:s+16],p[s+32:s+48],p[s+64:e])
    assert result[s:s+64]==template[s:s+64] and len(result)==len(template)
    return bytes(result),stats
def main(work,dest):
    assert base.sys.flags.optimize==0
    for p,h in base.TOOL_PINS.items():assert base.sha(p.read_bytes())==h
    work.mkdir(parents=True,exist_ok=False);dest.mkdir(parents=True,exist_ok=False)
    source=(ROOT/'candidates/HDD2TB-P4/PS3/UPDATE/PS3UPDAT.PUP').read_bytes()
    assert base.sha(source)==P4_SHA
    entries={e['id']:e['data'] for e in base.pup_entries(source)}
    update,heads=base.tar_members(entries[0x300]),base.tar_members(entries[0x501])
    rawpkg=update[flash.PKG_NAME];info0,info1,content=base.package_parts(rawpkg)
    import io,tarfile
    with tarfile.open(fileobj=io.BytesIO(content),mode='r:') as tar:oldself=tar.extractfile(flash.MEMBER).read()
    assert base.sha(oldself)==OLD_SELF_SHA
    (work/'sysconf-original.self').write_bytes(oldself)
    base.decode(work/'sysconf-original.self',work/'sysconf-original.elf')
    old=(work/'sysconf-original.elf').read_bytes();assert base.sha(old)==OLD_ELF_SHA
    new=(ROOT/'analysis/dev006/caller-prototype/sysconf-patched.elf').read_bytes();assert base.sha(new)==NEW_ELF_SHA
    audit=json.loads((ROOT/'analysis/dev006/caller-prototype/dataflow-audit.json').read_text())
    assert audit['pass'] and audit['cases']==42
    (work/'sysconf-patched.elf').write_bytes(new)
    for name in ('original','patched'):
        base.run([base.SCETOOL,'-0','SELF','-1','TRUE','-s','TRUE','-7','TRUE','-t',work/'sysconf-original.self',
                  '-e',work/f'sysconf-{name}.elf',work/f'sysconf-{name}-native.self'],work/f'sysconf-{name}-encode.log')
    control=streams((work/'sysconf-original-native.self').read_bytes())
    assert control==streams(oldself),'All native no-change PRX streams must match'
    assert focused(oldself,control,old,old)[0]==oldself
    candidate,compression=focused(oldself,streams((work/'sysconf-patched-native.self').read_bytes()),old,new)
    (work/'sysconf-candidate.self').write_bytes(candidate)
    base.decode(work/'sysconf-candidate.self',work/'sysconf-candidate-python.elf')
    base.run([base.SCETOOL,'-d',work/'sysconf-candidate.self',work/'sysconf-candidate-native.elf'],work/'sysconf-candidate-decode.log')
    assert (work/'sysconf-candidate-python.elf').read_bytes()==(work/'sysconf-candidate-native.elf').read_bytes()==new
    assert flash.replace_flash(content,oldself,oldself)[0]==content
    changed,offset=flash.replace_flash(content,oldself,candidate)
    controlpkg,_=base.native_pkg(info0,info1,content,work/'flash-control-pkg')
    assert base.template_pkg(rawpkg,controlpkg)==rawpkg
    native,_=base.native_pkg(info0,info1,changed,work/'flash-candidate-pkg')
    pkg=base.template_pkg(rawpkg,native);p=work/flash.PKG_NAME;p.write_bytes(pkg)
    base.run([base.SPKGTOOL,p],work/'flash-spkg.log');head=Path(str(p)+'.spkg_hdr.1').read_bytes()
    updated=base.replace_tar(entries[0x300],flash.PKG_NAME,pkg)
    header=base.replace_tar(entries[0x501],flash.PKG_NAME+'.spkg_hdr.1',head)
    assert base.rebuild_pup(source,{})==source
    pup=base.rebuild_pup(source,{0x300:updated,0x501:header})
    target=dest/'PS3/UPDATE/PS3UPDAT.PUP';target.parent.mkdir(parents=True);target.write_bytes(pup)
    manifest={'candidate':'HDD2TB-P5','stage':'built; independent-parser/crypto/scope review pending',
      'parent_sha256':P4_SHA,'candidate_sha256':base.sha(pup),'candidate_size':len(pup),
      'purpose':'Experimental128MiB full-checker backing/heap with nonzero allocation-status and zero-address rejection',
      'sysconf_self_sha256':base.sha(candidate),'sysconf_elf_sha256':base.sha(new),
      'flash_package':flash.PKG_NAME,'flash_member':flash.MEMBER,'flash_member_content_offset':offset,
      'compression':compression,'caller_patch_manifest':'analysis/dev006/caller-prototype/manifest.json',
      'caller_patch_manifest_sha256':base.sha((ROOT/'analysis/dev006/caller-prototype/manifest.json').read_bytes()),
      'controls':{'all_native_no_change_PRX_streams_identical':True,'focused_no_change_SELF_identical':True,
          'no_change_flash_tar_identical':True,'no_change_PKG_identical':True,'no_change_PUP_identical':True,
          'native_python_full_ELF_readback_equal':True},
      'hardware_tested':False,'actual_checker_peak_measured':False,'stable_storage_support':False,
      'self_signature_treatment':'Retain inherited CFW signature bytes; changed digest does not claim Sony authenticity',
      'tools':{str(p.relative_to(ROOT)):base.sha(p.read_bytes()) for p in [Path(__file__),ROOT/'tools/build_hdd2tb_p1.py',ROOT/'tools/build_hdd2tb_p3.py',*base.TOOL_PINS]}}
    base.save_json(dest/'build-manifest.json',manifest)
    (dest/'SHA256SUMS.txt').write_text(base.sha(pup).upper()+'  PS3/UPDATE/PS3UPDAT.PUP\n')
    assert base.sha(base.SOURCE.read_bytes())==base.SOURCE_SHA
    print(json.dumps({'candidate_sha256':base.sha(pup),'size':len(pup),'compression':compression},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--dest',type=Path,required=True);a=p.parse_args()
    assert a.work.resolve().is_relative_to(ROOT/'analysis')
    assert a.dest.resolve().is_relative_to(ROOT/'analysis') or a.dest.resolve()==ROOT/'candidates/HDD2TB-P5'
    main(a.work,a.dest)
