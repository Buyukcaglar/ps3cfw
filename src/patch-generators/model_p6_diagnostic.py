"""Bounded helper instruction model, host C oracle, and independent ELF scope.

This does not execute the PPC C component or Sony code. Hardware is a gate.
"""
import ctypes as C,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
O=ROOT/'analysis/dev006/p6-diagnostic'
m=json.loads((O/'manifest.json').read_text());elf=(O/'libfs_utility_init-p6.elf').read_bytes()
assert hashlib.sha256(elf).hexdigest()==m['output_sha256']
layout=json.loads((ROOT/'analysis/dev006/telemetry-layout/layout-audit.json').read_text())
previous=(ROOT/'analysis/dev006/telemetry-layout/libfs_utility_init-owned-space.elf').read_bytes()
phoff=struct.unpack_from('>Q',elf,32)[0]
ph=[struct.unpack_from('>IIQQQQQQ',elf,phoff+56*i) for i in range(3)]
rels=[struct.unpack_from('>QHBBIQ',elf,i) for i in range(ph[2][2],len(elf),24)]
oldrels=[struct.unpack_from('>QHBBIQ',previous,i) for i in range(ph[2][2],len(previous),24)]
assert rels==oldrels+[tuple(r) for r in m['new_relocations']]
masked=bytearray(elf[:len(previous)]);want=bytearray(previous)
for hook in m['hooks']:
 va=int(hook['va'],16);at=0xf0+va
 assert previous[at:at+4]==bytes.fromhex(hook['before'])
 masked[at:at+4]=want[at:at+4]
start=int(m['code_start'],16);end=int(m['path_va'],16)+len(m['path'])+1
assert not any(previous[0xf0+start:0xf0+end])
masked[0xf0+start:0xf0+end]=want[0xf0+start:0xf0+end]
masked[phoff+112+32:phoff+112+40]=want[phoff+112+32:phoff+112+40]
assert masked==want,'Only declared helper/path/hooks/relocation length differ'
core=json.loads((ROOT/'analysis/dev006/telemetry-core/validation.json').read_text())
coreva=int(layout['new_code_va'],16)
targets={coreva+int(f['offset'],16):f['name'] for f in core['target_functions']}
class Record(C.Structure):_fields_=[('words',C.c_uint32*(m['record_size']//4))]
lib=C.CDLL(str(ROOT/'analysis/dev006/telemetry-core/telemetry-host.dll'))
argc={'tm_init':5,'tm_try_lock':0,'tm_unlock':0,'tm_header_address':2,'tm_alloc':4,'tm_prepare_free':2,'tm_free':3,'tm_finish':1}
for n,count in argc.items():
 f=getattr(lib,n);f.argtypes=[C.POINTER(Record)]+[C.c_uint32]*count
 f.restype=C.c_uint32 if n in ('tm_try_lock','tm_header_address','tm_prepare_free') else None
MASK=(1<<64)-1
def sx(x,n):return (x&((1<<n)-1))-(1<<n) if x&(1<<(n-1)) else x&((1<<n)-1)
cs=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
def run(bases,status,scenario,failcore=False,owner=False,reused=False):
 data=[bytearray(elf[p[2]:p[2]+p[5]])+bytearray(p[6]-p[5]) for p in ph[:2]]
 for off,z,vi,ai,typ,add in rels:
  val=bases[vi]+add
  if typ==1:struct.pack_into('>I',data[ai],off,val)
  else:struct.pack_into('>H',data[ai],off,(val if typ==4 else (val+0x8000)>>16)&65535)
 ins={a:(n,o) for a,s,n,o in cs.disasm_lite(bytes(data[0][start:start+m['code_bytes']]),start)}
 H=bases[1]+int(m['header_offset'],16);R=H+128;sp=0x70000000
 mem={};writes=[];events=[];output=bytearray();cr={0:0,7:0};lr=0
 g=[0x11000000+i*0x1111 for i in range(32)];g[1]=sp;g[24]=0x123456789abcdef0
 g[26]=0x20123456;g[28]=0x10780000;g[31]=0x08000000;g[30]=0xffffffff
 def write(a,v,n):
  assert H<=a and a+n<=H+128+m['record_size'] or sp-0xc0<=a and a+n<=sp+0x18,(hex(a),n)
  writes.append((a,n))
  for i,b in enumerate((v&((1<<(n*8))-1)).to_bytes(n,'big')):mem[a+i]=b
 def read(a,n):
  if bases[0]<=a and a+n<=bases[0]+len(data[0]):return int.from_bytes(data[0][a-bases[0]:a-bases[0]+n],'big')
  return int.from_bytes(bytes(mem.get(a+i,0) for i in range(n)),'big')
 def clobber(ret=0):
  for r in (0,*range(3,13)):g[r]=0xfeed0000+r
  g[3]=ret&MASK;cr[0]=99;cr[7]=99
 def ccall(name):
  assert g[3]==R
  rec=Record()
  for i in range(len(rec.words)):rec.words[i]=read(R+4*i,4)
  args=g[4:4+argc[name]];ret=getattr(lib,name)(C.byref(rec),*args)
  for i,v in enumerate(rec.words):
   if v!=read(R+4*i,4):write(R+4*i,v,4)
  if failcore and name=='tm_try_lock':ret=0
  clobber(ret or 0)
 def syscall():
  n=g[11];args=g[3:9].copy();events.append((n,args))
  if n==801:
   raw=bytes(read(g[3]+i,1) for i in range(len(m['path'])+1))
   assert raw==m['path'].encode()+b'\0' and args[1]==0xc1 and args[3:]==[0x1b6,0,0]
   if scenario=='openfail':clobber(0x80010006);return
   write(g[5],0x42,4);clobber();return
  assert args[0]==0x42
  if n==803:
   count=sum(e[0]==803 for e in events)
   assert args[2]==(256 if count==1 else 16)
   if scenario=='writefail' and count==1:clobber(0x80010004);return
   size=(128 if scenario=='short' and count==1 else ((1<<32)+256 if scenario=='highsize' and count==1 else args[2]))
   output.extend(bytes(read(args[1]+i,1) for i in range(min(size,args[2]))))
   write(args[3],size,8)
   clobber(0x80010004 if scenario=='footerfail' and count==2 else 0)
  elif n==804:clobber(0x80010004 if scenario=='closefail' else 0)
  else:raise AssertionError(n)
 def execute(label):
  nonlocal lr
  pc=int(m['labels'][label],16);lr=0xabcdef00;initial=g.copy()
  for step in range(1000):
   n,o=ins[pc];parts=o.replace(',','').split();nxt=pc+4
   reg=lambda s:int(s[1:]);imm=lambda s:int(s,0)
   if n in ('li','lis'):g[reg(parts[0])]=(imm(parts[1])*(65536 if n=='lis' else 1))&MASK
   elif n=='ori':g[reg(parts[0])]=g[reg(parts[1])]|imm(parts[2])
   elif n=='addi':g[reg(parts[0])]=(g[reg(parts[1])]+imm(parts[2]))&MASK
   elif n=='mr':g[reg(parts[0])]=g[reg(parts[1])]
   elif n=='extsw':g[reg(parts[0])]=sx(g[reg(parts[1])],32)&MASK
   elif n in ('lwz','ld','stw','std','stdu'):
    r=reg(parts[0]);offset,base=parts[1].split('(');base=reg(base[:-1]);a=(g[base]+imm(offset))&MASK;size=8 if n in ('ld','std','stdu') else 4
    if n in ('lwz','ld'):g[r]=read(a,size)
    else:write(a,g[r],size)
    if n=='stdu':g[base]=a
   elif n in ('cmpwi','cmpdi','cmpw'):
    field=int(parts[0][2:]);a=g[reg(parts[1])];b=g[reg(parts[2])] if n=='cmpw' else imm(parts[2]);cr[field]=sx(a,64 if n=='cmpdi' else 32)-b
   elif n in ('beq','bne'):
    field=int(parts[0][2:]) if len(parts)>1 else 0
    if (cr[field]==0)==(n=='beq'):nxt=imm(parts[-1])
   elif n=='b':nxt=imm(parts[0])
   elif n=='bl':
    lr=pc+4;target=imm(parts[0]);assert target in targets;ccall(targets[target])
   elif n=='mflr':g[reg(parts[0])]=lr
   elif n=='mtlr':lr=g[reg(parts[0])]
   elif n=='lwarx':g[reg(parts[0])]=read(g[reg(parts[2])],4)
   elif n=='stwcx.':write(g[reg(parts[2])],g[reg(parts[0])],4);cr[0]=0
   elif n in ('lwsync','sync'):pass
   elif n=='sc':syscall()
   elif n=='blr':
    assert lr==0xabcdef00 and g[1]==initial[1]
    if label=='entry':assert g[30]==sx(initial[30],32)&MASK and all(g[r]==initial[r] for r in (2,*range(13,30),31))
    else:assert g[0]==0 and all(g[r]==initial[r] for r in (2,*range(13,32)))
    return
   else:raise AssertionError((n,o))
   pc=nxt
  raise AssertionError('helper did not terminate')
 if owner:write(H,sp+0x100,4)
 execute('entry');g[27]=status&MASK;execute('finish')
 if owner:assert not events
 else:
  assert read(H+4,4)==2 and read(H+32,4)==status&0xffffffff
  assert read(H+36,4)==(0xffffffff if failcore else 1)
  assert [e[0] for e in events]==([801] if scenario=='openfail' else ([801,803,804] if scenario in ('writefail','short','highsize') else [801,803,803,804]))
  if scenario in ('ok','closefail'):
   assert len(output)==272 and output[48:64]==b'HDD2TB-P6-DIAG\0\0'
   assert struct.unpack('>IIQ',output[256:])==(0x50364654,0,256)
   assert struct.unpack_from('>I',output,44)[0]==0xffffffff
   if scenario=='ok' and status==0 and bases==(0,ph[1][3]) and not failcore:
    (O/'synthetic-model-fixture.bin').write_bytes(output)
  if reused:
   saved=bytes(output);ev=len(events);execute('entry');execute('finish');assert ev==len(events) and saved==output
 return {'bases':[hex(b) for b in bases],'utility_status':hex(status&0xffffffff),'io':scenario,'selftest_failure':failcore,'foreign_owner':owner,'reused_frame':reused,'syscalls':[e[0] for e in events]}
cases=[]
for bases in ((0,ph[1][3]),(0x10000000,0x20000000),(0x10008000,0x44008000)):
 for status in (0,7,-1):
  for scenario in ('ok','openfail','writefail','short','highsize','footerfail','closefail'):
   cases.append(run(bases,status,scenario,reused=True))
 cases.append(run(bases,0,'ok',True));cases.append(run(bases,0,'ok',owner=True))
report={'pass':True,'cases':len(cases),'scope':'Helper PPC instruction model with separately host-executed C calls, not Sony or PPC C execution',
 'elf_sha256':m['output_sha256'],'original_owned_layout_outside_declared_edits_preserved':True,
 'stack_LR_and_nonvolatile_registers_preserved':True,'writes_only_new_owned_BSS_or_helper_stack':True,
 'exclusive_fixed_USB_path_only':True,'opened_descriptor_closed_once_on_all_write_paths':True,
 'full64_first_write_size_checked':True,'one_shot_even_reused_frame':True,'details':cases}
(O/'dataflow-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='details'}))
