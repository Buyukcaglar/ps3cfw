"""Offline PRX owned-space prototype, not an installable firmware release."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/python_packages'))
sys.path.insert(0,str(ROOT/'tools'))
from elftools.elf.elffile import ELFFile
import build_hdd2tb_p1 as base
OUT=ROOT/'analysis/dev006/p8-telemetry-layout';OUT.mkdir(exist_ok=True)
source=ROOT/'analysis/fs-review/libfs_utility_init.sprx.elf';old=source.read_bytes()
assert hashlib.sha256(old).hexdigest()=='6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a'
validation=json.loads((ROOT/'analysis/dev006/p8-telemetry-core/validation.json').read_text());assert validation['pass']
obj=ROOT/'analysis/dev006/p8-telemetry-core/telemetry-ppc64.o'
assert hashlib.sha256(obj.read_bytes()).hexdigest()==validation['sources'][str(obj.relative_to(ROOT)).replace('\\','/')]
with obj.open('rb') as f:
 e=ELFFile(f);code=e.get_section_by_name('.text').data()
 assert not e.get_section_by_name('.rela.text')
offset=struct.unpack_from('>Q',old,32)[0]
ph=[list(struct.unpack_from('>IIQQQQQQ',old,offset+i*56)) for i in range(3)]
assert struct.unpack_from('>Q',old,40)[0]==0 and struct.unpack_from('>H',old,60)[0]==0
assert ph[0][0]==ph[1][0]==1 and ph[2][0]==0x700000a4
assert ph[0][2]+ph[0][5]==ph[1][2] and ph[1][3]==ph[0][5]
assert ph[2][2]+ph[2][5]==len(old)
rels=[struct.unpack_from('>QHBBIQ',old,i) for i in range(ph[2][2],len(old),24)]
assert all(r[1]==0 and r[2]<2 and r[3]<2 and r[4] in (1,4,6) for r in rels)
grow=0x3000;codeva=(ph[0][5]+15)&~15
assert codeva-ph[0][5]+len(code)<grow
new=bytearray(old[:ph[1][2]]+bytes(grow)+old[ph[1][2]:])
new[ph[0][2]+codeva:ph[0][2]+codeva+len(code)]=code
np=[r.copy() for r in ph];np[0][5]+=grow;np[0][6]+=grow
np[1][2]+=grow;np[1][3]+=grow;np[2][2]+=grow
recordoff=(ph[1][6]+63)&~63
np[1][6]=recordoff+128+validation['record_bytes']
for i,row in enumerate(np):struct.pack_into('>IIQQQQQQ',new,offset+i*56,*row)
def value(v,t):return v&0xffffffff if t==1 else (v&65535 if t==4 else ((v+0x8000)>>16)&65535)
changes=[]
for off,unused,vi,ai,t,add in rels:
 n=4 if t==1 else 2;oldoff=ph[ai][2]+off;newoff=np[ai][2]+off
 assert off+n<=ph[ai][5]
 assert int.from_bytes(old[oldoff:oldoff+n],'big')==value(ph[vi][3]+add,t)
 expected=value(np[vi][3]+add,t)
 new[newoff:newoff+n]=expected.to_bytes(n,'big')
 if ph[vi][3]!=np[vi][3]:changes.append({'segment':ai,'offset':hex(off),'type':t})
assert new[np[2][2]:]==old[ph[2][2]:], 'Keep all original relocation records byte-identical'
def loaded(blob,headers,bases):
 data=[bytearray(blob[h[2]:h[2]+h[5]]) for h in headers[:2]]
 for off,z,vi,ai,t,add in rels:
  n=4 if t==1 else 2
  data[ai][off:off+n]=value(bases[vi]+add,t).to_bytes(n,'big')
 return data
cases=[]
for bases in ((0,ph[1][3]),(0x10000000,0x20000000),(0x10008000,0x44008000),(0x17fff000,0x29fff000)):
 a,b=loaded(old,ph,bases),loaded(new,np,bases)
 assert all(a[i]==b[i][:len(a[i])] for i in (0,1))
 assert b[0][codeva:codeva+len(code)]==code
 cases.append({'bases':[hex(x) for x in bases],'all_original_loaded_bytes_equal':True})
(OUT/'libfs_utility_init-owned-space.elf').write_bytes(new)
template=(ROOT/'analysis/flash/dev_flash/sys/internal/libfs_utility_init.sprx').read_bytes()
p,s,end,table=base.self_plain(template);compression=[]
for i,h in enumerate(np):
 q=s+96+i*48;start=base.number(p,q,8);limit=base.number(p,q+48,8) if i<2 else len(template)
 stream=zlib.compress(new[h[2]:h[2]+h[5]],9)
 compression.append({'segment':i,'selected_zlib9_bytes':len(stream),'existing_slot_bytes':limit-start,
                     'fits_original_slot':len(stream)<=limit-start})
report={'scope':'Offline unhooked owned-space/layout prototype; not Sony loading/execution or released firmware',
 'source':str(source.relative_to(ROOT)).replace('\\','/'),'source_sha256':hashlib.sha256(old).hexdigest(),
 'output_sha256':hashlib.sha256(new).hexdigest(),'text_growth':grow,'new_code_va':hex(codeva),
 'record_segment':1,'diagnostic_header_relative_offset':hex(recordoff),'diagnostic_header_bytes':128,
 'record_relative_offset':hex(recordoff+128),'record_bytes':validation['record_bytes'],
 'old_program_headers':ph,'new_program_headers':np,'adjusted_static_relocation_values':len(changes),
 'all_original_relocation_records_unchanged':True,'load_model_cases':cases,
 'compiler_core_has_no_text_relocations':True,'compression':compression,
 'allocator_hooks_installed':False,'runtime_tested':False,
 'loader_model_reference':'analysis/dev006/loader-reference/provenance.json',
 'loader_model_limit':'Independent format reference/model; Sony loader behavior remains unqualified'}
(OUT/'layout-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('output_sha256','record_bytes','adjusted_static_relocation_values','compression','allocator_hooks_installed')},indent=2))
