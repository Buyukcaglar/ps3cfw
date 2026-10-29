"""P8 plus bounded checker allocation-failure guards; no device access.

Repack growing SELF and flash PKG with explicit size fields. Original CFW
signature policy is inherited; this does not create Sony authenticity.
"""
import argparse,hashlib,io,json,struct,tarfile,zlib
from pathlib import Path
import build_hdd2tb_p1 as b
import build_hdd2tb_p5 as p5
ROOT=b.ROOT
PACKAGE='dev_flash_022.tar.aa.2026_01_08_191610'
MEMBER='dev_flash/sys/internal/libfs_utility_init.sprx'
PARENT='d0260ed27fb2a9fa50b140c7f439ef5653ec231c0fc983fce51e3b054aa1a47a'
def flash_reflow(data,replacement):
 parts=[];at=0;found=0
 while any(data[at:at+512]):
  h=bytearray(data[at:at+512]);assert len(h)==512 and not any(h[345:500])
  assert int(h[148:156].strip(b'\0 ') or b'0',8)==sum(h[:148])+256+sum(h[156:])
  assert h[156:157] in (b'0',b'5',b'\0')
  name=h[:100].split(b'\0')[0].decode();size=int(h[124:136].strip(b'\0 ') or b'0',8)
  end=at+512+((size+511)//512)*512;assert end<=len(data)
  if name==MEMBER:
   found+=1;assert h[156:157]!=b'5'
   if data[at+512:at+512+size]==replacement:parts.append(data[at:end])
   else:
    h[124:136]=f'{len(replacement):011o}\0'.encode();h[148:156]=b'        ';h[148:156]=f'{sum(h):06o}\0 '.encode()
    parts.extend((bytes(h),replacement,bytes((-len(replacement))%512)))
  else:parts.append(data[at:end])
  at=end
 assert found==1 and len(data)-at>=1024 and not any(data[at:]);parts.append(data[at:])
 return b''.join(parts)
def repack_self(template,old,new):
 if old==new:return template
 p,s,end,t=b.self_plain(template);original=bytes(p)
 assert b.number(p,0x18,8)==len(old)
 struct.pack_into('>Q',p,0x18,len(new))
 n=b.number(new,56,2);ph=b.number(new,32,8);copy=b.number(p,0x38,8);assert n==3
 assert p[copy:copy+56*n]==old[ph:ph+56*n]
 p[copy:copy+56*n]=new[ph:ph+56*n]
 ci=b.number(p,0x58,8);ce=ci+b.number(p,0x60,8);dig=0
 while ci<ce:
  kind,size=b.number(p,ci,4),b.number(p,ci+4,4);assert size>=16 and ci+size<=ce
  if kind==2:
   assert p[ci+36:ci+56]==hashlib.sha1(old).digest()
   p[ci+36:ci+56]=hashlib.sha1(new).digest();dig+=1
  ci+=size
 assert ci==ce and dig==1
 result=bytearray(template[:end]);stats=[]
 for i,seg in enumerate(p5.segments(new)):
  q=s+96+i*48;assert b.number(p,q+16,4)==2 and b.number(p,q+20,4)==i
  assert b.number(p,q+32,4)==3 and b.number(p,q+44,4)==2
  stream=zlib.compress(seg,9)
  result.extend(bytes((-len(result))%16));off=len(result)
  struct.pack_into('>QQ',p,q,off,len(stream))
  si=b.number(p,0x48,8)+i*32;struct.pack_into('>QQ',p,si,off,len(stream))
  hi,ki,vi=[b.number(p,q+x,4) for x in (28,36,40)];at=t+16*hi
  p[at:at+32]=b.hmac.digest(p[at+32:at+96],stream,'sha1')+bytes(12)
  result.extend(b.ctr(p[t+16*ki:t+16*(ki+1)],p[t+16*vi:t+16*(vi+1)],stream))
  stats.append({'segment':i,'offset':off,'compressed_size':len(stream),'decoded_size':len(seg)})
 sig=b.number(p,s+64,8);assert p[sig:sig+42]==original[sig:sig+42]
 result[:s]=p[:s];result[s+64:end]=b.ctr(p[s:s+16],p[s+32:s+48],p[s+64:end])
 assert result[s:s+64]==template[s:s+64]
 return bytes(result)
def repack_pkg(template,native,content_bytes):
 p=bytearray(template);assert b.pkg_reader.sce_decrypt_header(p)>=0;b.pkg_reader.sce_decrypt_data(p)
 g=bytearray(native);assert b.pkg_reader.sce_decrypt_header(g)>=0;b.pkg_reader.sce_decrypt_data(g)
 assert b.number(p,16,8)==640 and b.number(p,0x6c,4)==3 and b.number(p,0x70,4)==20
 off,size=b.number(g,0xe0,8),b.number(g,0xe8,8);assert off==0x300
 stream=bytes(g[off:off+size]);assert len(zlib.decompress(stream))==content_bytes
 result=bytearray(p[:0x300])+stream
 struct.pack_into('>Q',result,0x18,content_bytes+0x80)
 for at in (0x298,0x2d8):struct.pack_into('>Q',result,at,content_bytes)
 for at in (0xe8,0x2a0):struct.pack_into('>Q',result,at,len(stream))
 assert b.number(result,0x2e0,8)==1
 table=0x110
 for i in range(3):
  q=0x80+48*i;off,size,hi=[b.number(result,q+x,8 if x<16 else 4) for x in (0,8,28)];at=table+16*hi
  result[at:at+32]=b.hmac.digest(result[at+32:at+96],result[off:off+size],'sha1')+bytes(12)
 siglen=b.number(result,0x60,8);assert siglen==0x250
 if result[:siglen]!=p[:siglen]:result[siglen:siglen+42]=b.sign_pkg_header(result,siglen)
 for i in range(3):
  q=0x80+48*i
  if b.number(result,q+32,4)==3:
   off,size=b.number(result,q,8),b.number(result,q+8,8);ki,vi=b.number(result,q+36,4),b.number(result,q+40,4)
   result[off:off+size]=b.ctr(result[table+16*ki:table+16*(ki+1)],result[table+16*vi:table+16*(vi+1)],result[off:off+size])
 result[0x60:0x280]=b.ctr(result[0x20:0x30],result[0x40:0x50],result[0x60:0x280]);result[0x20:0x60]=template[0x20:0x60]
 return bytes(result)
def main(work,dest):
 assert b.sys.flags.optimize==0
 for p,h in b.TOOL_PINS.items():assert b.sha(p.read_bytes())==h
 work.mkdir(parents=True,exist_ok=False);dest.mkdir(parents=True,exist_ok=False)
 source=(ROOT/'candidates/HDD2TB-P8/PS3/UPDATE/PS3UPDAT.PUP').read_bytes();assert b.sha(source)==PARENT
 entries={e['id']:e['data'] for e in b.pup_entries(source)};update=b.tar_members(entries[0x300])
 raw=update[PACKAGE];info0,info1,content=b.package_parts(raw)
 with tarfile.open(fileobj=io.BytesIO(content)) as archive:oldself=archive.extractfile(MEMBER).read()
 assert b.sha(oldself)=='5c1b2c1a9b894e6a091869fa30a5254f3191c45c2781485b82d5c73414a82153'
 (work/'original.self').write_bytes(oldself);b.decode(work/'original.self',work/'original.elf');old=(work/'original.elf').read_bytes()
 assert b.sha(old)=='b7e65e2dd7d82aa5c9957c2af7a192f475ed26f4140f3ab25ea18866bed53f01'
 new=(ROOT/'analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf').read_bytes()
 model=json.loads((ROOT/'analysis/dev006/p9-safety-model-v3/result.json').read_text());assert model['pass'] and model['elf_sha256']==b.sha(new)
 candidate=repack_self(oldself,old,new);assert repack_self(oldself,old,old)==oldself
 (work/'candidate.self').write_bytes(candidate);b.decode(work/'candidate.self',work/'candidate.python.elf')
 b.run([b.SCETOOL,'-d',work/'candidate.self',work/'candidate.native.elf'],work/'native-decode.log')
 assert (work/'candidate.python.elf').read_bytes()==(work/'candidate.native.elf').read_bytes()==new
 changed=flash_reflow(content,candidate);assert flash_reflow(content,oldself)==content
 control,_=b.native_pkg(info0,info1,content,work/'control-pkg');assert repack_pkg(raw,control,len(content))==raw
 i0,i1=bytearray(info0),bytearray(info1)
 for z in (i0,i1):struct.pack_into('>Q',z,0x18,len(changed))
 native,_=b.native_pkg(i0,i1,changed,work/'candidate-pkg');pkg=repack_pkg(raw,native,len(changed))
 assert b.package_parts(pkg)[2]==changed
 p=work/PACKAGE;p.write_bytes(pkg);b.run([b.SPKGTOOL,p],work/'spkg.log');head=Path(str(p)+'.spkg_hdr.1').read_bytes()
 updated=b.replace_tar(entries[0x300],PACKAGE,pkg);heads=b.replace_tar(entries[0x501],PACKAGE+'.spkg_hdr.1',head)
 assert b.rebuild_pup(source,{})==source
 pup=b.rebuild_pup(source,{0x300:updated,0x501:heads});target=dest/'PS3/UPDATE/PS3UPDAT.PUP';target.parent.mkdir(parents=True);target.write_bytes(pup)
 manifest={'candidate':'HDD2TB-P9','candidate_sha256':b.sha(pup),'candidate_size':len(pup),'parent_sha256':PARENT,
  'purpose':'Bounded checker array-growth failure/overread fix and calloc multiplication-overflow rejection; P8 storage/observer retained',
  'flash_package':PACKAGE,'flash_member':MEMBER,'self_sha256':b.sha(candidate),'elf_sha256':b.sha(new),
  'tar_bytes_before':len(content),'tar_bytes_after':len(changed),'self_bytes_before':len(oldself),'self_bytes_after':len(candidate),
  'controls':{'no_change_SELF_identical':True,'no_change_tar_identical':True,'no_change_PKG_identical':True,'no_change_PUP_identical':True,'native_python_whole_ELF_equal':True},
  'actual_heap_instrumentation':True,'actual_peak_measured':False,'hardware_tested':False,'stable_support':False,
  'signature_policy':'Inherited CFW SELF signature override; retained original signature bytes do not authenticate new contents',
  'sources':{str(p.relative_to(ROOT)).replace('\\','/'):b.sha(p.read_bytes()) for p in [Path(__file__),ROOT/'analysis/dev006/prepare_p9_safety_v2.py',ROOT/'analysis/dev006/p9-safety-v2/manifest.json',ROOT/'analysis/dev006/model_p9_safety.py',ROOT/'analysis/dev006/p9-safety-model-v3/result.json',ROOT/'analysis/dev006/p9-safety-delta/review.json',ROOT/'tools/build_hdd2tb_p1.py',ROOT/'tools/build_hdd2tb_p5.py',ROOT/'analysis/dev006/p8-native/manifest.json',ROOT/'analysis/dev006/p8-native/dataflow-audit.json',ROOT/'analysis/dev006/prepare_p8_native.py',ROOT/'analysis/dev006/model_p8_native.py',ROOT/'analysis/dev006/p8-telemetry-core/validation.json',ROOT/'development/checker_telemetry_p8/telemetry.c',ROOT/'development/checker_telemetry_p8/telemetry.h',*b.TOOL_PINS]}}
 b.save_json(dest/'build-manifest.json',manifest);(dest/'SHA256SUMS.txt').write_text(b.sha(pup).upper()+'  PS3/UPDATE/PS3UPDAT.PUP\n')
 assert b.sha(b.SOURCE.read_bytes())==b.SOURCE_SHA
 print(json.dumps({'candidate_sha256':b.sha(pup),'candidate_bytes':len(pup),'self_bytes':len(candidate),'tar_growth':len(changed)-len(content)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--dest',type=Path,required=True);a=p.parse_args()
 assert a.work.resolve().is_relative_to(ROOT/'analysis')
 assert a.dest.resolve().is_relative_to(ROOT/'analysis') or a.dest.resolve()==ROOT/'candidates/HDD2TB-P9'
 main(a.work,a.dest)
