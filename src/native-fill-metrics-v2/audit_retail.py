"""Independent free-NPDRM decode/MAC audit and exact display loadable-byte comparison."""
import datetime,hashlib,hmac,importlib.util,json,struct,sys,zlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];P=R/'analysis/dev006/native-fill-64-metrics-v2';A=R/'observations/HW002BH/metrics-v2'
sys.path[:0]=[str(R/'tools/python_packages'),str(R/'tools')]
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from decrypt_self import keysets,ctr
def load(name,path):
 s=importlib.util.spec_from_file_location(name,R/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pa=load('pa','analysis/dev006/audit_aq_metadata_fix.py')
sig=load('sig','analysis/rebuild-review/audit_sce.py')
def mac(key,data):
 c=CMAC.new(key,ciphermod=AES);c.update(data);return c.digest()
def main():
 b=(P/'packagefiles/USRDIR/EBOOT.BIN').read_bytes();original=(P/'display.elf').read_bytes()
 assert original==(P/'display-repro.elf').read_bytes()
 assert b[:8]==b'SCE\0\0\0\0\2' and struct.unpack_from('>H',b,8)[0]==10
 base=32+struct.unpack_from('>I',b,12)[0];end=struct.unpack_from('>Q',b,16)[0]
 co,cs=struct.unpack_from('>QQ',b,88);at=co;np=None
 while at<co+cs:
  k,n,nxt=struct.unpack_from('>IIQ',b,at);assert n>=16 and at+n<=co+cs
  if k==3:np=b[at+16:at+n]
  at+=n
 assert np is not None and len(np)==128 and struct.unpack_from('>4I',np)==(0x4e504400,1,3,1)
 cid=b'UP0001-HD2TB0001_00-HDD2TBBHLONGFILL';assert len(cid)==36 and np[16:64]==cid+bytes(12)
 keys=list(keysets(R/'tools/scetool_keys/PS3/data/keys'));named={k['name']:k for k in keys}
 free=bytes.fromhex(named['NP_klic_free']['key'])
 assert hmac.compare_digest(mac(bytes.fromhex(named['NP_tid']['key']),np[16:64]+b'EBOOT.BIN'),np[80:96])
 assert hmac.compare_digest(mac(bytes(x^y for x,y in zip(bytes.fromhex(named['NP_ci']['key']),free)),np[:96]),np[96:112])
 # Remove the free-license NPDRM layer before the ordinary SELF metadata layer.
 nk=AES.new(bytes.fromhex(named['NP_klic_key']['key']),AES.MODE_ECB).decrypt(free)
 outer=AES.new(nk,AES.MODE_CBC,bytes(16)).decrypt(b[base:base+64]);matches=[]
 for key in keys:
  if key.get('program_type',key.get('self_type'))!='NPDRM' or 'erk' not in key or 'riv' not in key:continue
  meta=AES.new(bytes.fromhex(key['erk']),AES.MODE_CBC,bytes.fromhex(key['riv'])).decrypt(outer)
  if meta[16:32]==bytes(16) and meta[48:64]==bytes(16):matches.append((key,meta))
 assert matches and len({m for _,m in matches})==1
 meta=matches[0][1];header=ctr(meta[:16],meta[32:48],b[base+64:end])
 siglen,count,keycount=struct.unpack_from('>Q4xII',header)
 assert count<=32 and keycount<=512 and 32+48*count+16*keycount<=len(header)
 table=header[32+48*count:32+48*count+16*keycount]
 eo,po=struct.unpack_from('>QQ',b,48);assert b[eo:eo+64]==original[:64]
 nph=struct.unpack_from('>H',original,56)[0];phoff=struct.unpack_from('>Q',original,32)[0]
 phbytes=b[po:po+56*nph];assert phbytes==original[phoff:phoff+56*nph]
 ph=[struct.unpack_from('>IIQQQQQQ',phbytes,56*i) for i in range(nph)]
 checked=[];load_seen=set();plain=bytearray(b[:end]);plain[base:base+64]=meta;plain[base+64:end]=header
 for i in range(count):
  off,size,typ,pidx,hashed,hi,enc,ki,vi,compressed=struct.unpack_from('>QQ8I',header,32+48*i)
  assert off+size<=len(b);blob=b[off:off+size]
  if enc==3:
   assert ki<keycount and vi<keycount;blob=ctr(table[16*ki:16*(ki+1)],table[16*vi:16*(vi+1)],blob)
  else:assert enc==1
  if hashed==2:
   assert hi+6<=keycount
   assert hmac.compare_digest(hmac.digest(table[(hi+2)*16:(hi+6)*16],blob,'sha1'),table[hi*16:hi*16+20])
  else:assert hashed==1
  if compressed==2:
   z=zlib.decompressobj();decoded=z.decompress(blob,2097153);assert z.eof and len(decoded)<=2097152;blob=decoded
  else:assert compressed==1
  if typ==2:
   assert pidx<nph;h=ph[pidx];assert blob==original[h[2]:h[2]+h[5]]
   if h[0]==1 and h[5]>0:load_seen.add(pidx)
  checked.append({'index':i,'type':typ,'phdr_index':pidx,'HMAC_checked':hashed==2,'decoded_bytes':len(blob)})
 assert load_seen=={i for i,h in enumerate(ph) if h[0]==1 and h[5]>0}
 signatures=[sig.signature_check(plain,siglen,plain[siglen:siglen+42],k)['signature_valid'] for k,_ in matches if k.get('pub')]
 pkg=R/'diagnostics/HDD2TB-BH-FILL-v2/HDD2TB-BH-FILL.pkg';files=pa.decode_pkg(pkg)
 assert set(files)=={'PARAM.SFO','ICON0.PNG','USRDIR','USRDIR/EBOOT.BIN'}
 packaged=files['USRDIR/EBOOT.BIN']['payload']
 assert files['USRDIR/EBOOT.BIN']['flags']&255==1 and packaged[:len(b)]==b and not any(packaged[len(b):])
 assert pkg.read_bytes()[48:96]==cid+bytes(12)
 for name in ['PARAM.SFO','ICON0.PNG']:assert files[name]['payload']==(P/'packagefiles'/name).read_bytes()
 sf=pa.sfo(files['PARAM.SFO']['payload']);assert len(sf)==12 and sf['APP_VER']['value']=='01.16' and sf['TITLE_ID']['value']=='HD2TB0001'
 assert sf['TITLE']['capacity']==128 and sf['TITLE_ID']['capacity']==16 and sf['LICENSE']['capacity']==512
 native=(P/'native-roundtrip.elf').read_bytes()
 assert native[:64]==original[:64]
 for h in ph:
  if h[0]==1:assert native[h[2]:h[2]+h[5]]==original[h[2]:h[2]+h[5]]
 report={'passed':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'ELF_input_two_standard_SDK_links_identical':True,'all_native_loadable_bytes_equal_display_linked_input':True,
  'native_scetool_and_independent_Python_decodes_agree_on_every_loadable_byte':True,
  'NPDRM_free_license_and_EXEC_fields_valid':True,'content_id_filename_CMAC_valid':True,
  'NPDRM_control_info_CMAC_valid':True,'metadata_zero_padding_and_every_section_HMAC_valid':True,
  'sections':checked,'ECDSA_valid_under_matching_public_tool_database_keys':signatures,
  'authentic_Sony_signature_not_claimed':True,'retail_attribute':10,
  'packager_did_not_modify_signed_wrapper_except_zero_file_padding':True,
  'native_launch_or_read_proven':False,'native_result_must_still_be_absent':True,
  'package_bytes':pkg.stat().st_size,'package_sha256':hashlib.sha256(pkg.read_bytes()).hexdigest(),
  'SELF_bytes':len(b),'SELF_sha256':hashlib.sha256(b).hexdigest(),
  'console_unique_material_accessed_hashed_or_exported':False,'crypto_material_not_exported_in_report':True}
 with (A/'retail-independent-audit.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'passed':True,'package_bytes':report['package_bytes'],'all_loadable_bytes_match_input':True,'NPDRM_CMACs_valid':True,'section_HMACs_valid':True,'native_pending':True}))
if __name__=='__main__':main()

