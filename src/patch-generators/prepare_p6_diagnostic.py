"""Offline P6 route witness and synthetic target-component selftest.

No native allocator hooks, heap-prefix reads or live operations. All diagnostic
stores target newly owned PRX BSS. The original checker runs unchanged.
"""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
OUT=ROOT/'analysis/dev006/p6-diagnostic';OUT.mkdir(exist_ok=True)
layout=json.loads((ROOT/'analysis/dev006/telemetry-layout/layout-audit.json').read_text())
old=(ROOT/'analysis/dev006/telemetry-layout/libfs_utility_init-owned-space.elf').read_bytes()
assert hashlib.sha256(old).hexdigest()==layout['output_sha256']
core=json.loads((ROOT/'analysis/dev006/telemetry-core/validation.json').read_text());assert core['pass']
coreva=int(layout['new_code_va'],16);functions={r['name']:coreva+int(r['offset'],16) for r in core['target_functions']}
phoff=struct.unpack_from('>Q',old,32)[0]
ph=[list(struct.unpack_from('>IIQQQQQQ',old,phoff+i*56)) for i in range(3)]
start=(coreva+core['target_text_bytes']+15)&~15
headeroff=int(layout['diagnostic_header_relative_offset'],16)
def d(op,rt,ra,imm):return (op<<26)|(rt<<21)|(ra<<16)|(imm&65535)
def ds(op,rt,ra,imm,xo=0):assert imm%4==0;return d(op,rt,ra,imm)|xo
def mr(dst,src):return (31<<26)|(src<<21)|(dst<<16)|(src<<11)|(444<<1)
def branch(pc,target,link=0):
 delta=target-pc;assert delta%4==0 and -(1<<25)<=delta<(1<<25)
 return 0x48000000|(delta&0x3fffffc)|link
def cmpw(a,b):return (31<<26)|(7<<23)|(a<<16)|(b<<11)
class Asm:
 def __init__(self,base):self.base=base;self.words=[];self.labels={};self.fix=[];self.reloc=[]
 def pc(self):return self.base+len(self.words)*4
 def emit(self,w):self.words.append(w)
 def label(self,n):assert n not in self.labels;self.labels[n]=self.pc()
 def b(self,n,link=0):self.fix.append((len(self.words),'b',n,link));self.emit(0)
 def cond(self,n,equal=True,cr7=True):self.fix.append((len(self.words),'bc',n,(equal,cr7)));self.emit(0)
 def call(self,n):self.emit(branch(self.pc(),functions[n],1))
 def address(self,reg,seg,value):
  self.reloc.extend([(self.pc()+2,0,seg,0,6,value),(self.pc()+6,0,seg,0,4,value)])
  base=ph[seg][3]+value
  self.emit(d(15,reg,0,(base+0x8000)>>16));self.emit(d(14,reg,reg,base))
 def li(self,reg,value):
  if -32768<=value<=32767:self.emit(d(14,reg,0,value))
  else:self.emit(d(15,reg,0,value>>16));self.emit(d(24,reg,reg,value))
 def finish(self):
  for i,kind,n,arg in self.fix:
   target=self.labels[n];pc=self.base+i*4
   if kind=='b':self.words[i]=branch(pc,target,arg)
   else:
    equal,cr7=arg;delta=target-pc;assert -32768<=delta<32768 and delta%4==0
    self.words[i]=(0x419e0000 if equal else 0x409e0000) if cr7 else (0x41820000 if equal else 0x40820000)
    self.words[i]|=delta&65535
  return b''.join(struct.pack('>I',x) for x in self.words)
a=Asm(start)
a.label('entry');a.address(9,1,headeroff)
a.label('claim');a.emit((31<<26)|(10<<21)|(9<<11)|(20<<1)) # lwarx r10,0,r9
a.emit(d(11,28,10,0));a.cond('entry_done',False)
a.emit(mr(10,1));a.emit((31<<26)|(10<<21)|(9<<11)|(150<<1)|1) # stwcx.
a.cond('claim',False,False);a.emit(0x7c2004ac)
a.li(10,1);a.emit(d(36,10,9,4));a.emit(d(36,28,9,8));a.emit(d(36,31,9,12))
a.emit(d(36,26,9,16));a.emit(d(36,10,9,20));a.emit(ds(62,24,9,24))
a.li(10,-1)
for off in (32,40,44):a.emit(d(36,10,9,off))
for off,w in zip((48,52,56,60),(0x48444432,0x54422d50,0x362d4449,0x41470000)):
 a.li(10,w);a.emit(d(36,10,9,off))
a.label('entry_done');a.emit(0x7fde07b4);a.emit(0x4e800020) # original extsw r30
a.label('finish');a.address(9,1,headeroff);a.emit(d(32,10,9,0));a.emit(cmpw(10,1));a.cond('return_zero',False)
a.emit(d(32,10,9,4));a.emit(d(11,28,10,1));a.cond('return_zero',False)
a.li(10,2);a.emit(d(36,10,9,4)) # permanently consumed before selftest/logger
a.emit(0x7c0802a6);a.emit(ds(62,1,1,-0xc0,1));a.emit(ds(62,0,1,0xd0))
for r,off in ((29,0xa0),(30,0xa8),(31,0xb0),(2,0xb8)):a.emit(ds(62,r,1,off))
a.emit(mr(29,9));a.emit(d(14,30,29,128));a.emit(d(36,27,29,32))
a.li(0,0);a.emit(d(36,0,1,0x70)) # selftest lock ownership
a.emit(mr(3,30));a.li(4,1);a.li(5,0x101);a.li(6,0x10000000);a.li(7,0x08000000);a.li(8,1);a.call('tm_init')
a.emit(mr(3,30));a.call('tm_try_lock');a.emit(d(11,28,3,1));a.cond('test_fail',False)
a.li(0,1);a.emit(d(36,0,1,0x70))
def invoke(name,heap,*args):
 a.emit(mr(3,30));a.li(4,heap)
 for reg,v in enumerate(args,5):a.li(reg,v)
 a.call(name)
invoke('tm_header_address',0x101,0x10000008)
a.li(9,0x10000004);a.emit(cmpw(3,9));a.cond('test_fail',False)
invoke('tm_alloc',0x101,56,0x10000008,66)
invoke('tm_alloc',0x101,104,0x10000108,114)
invoke('tm_prepare_free',0x101,0x10000008)
a.li(9,0x10000004);a.emit(cmpw(3,9));a.cond('test_fail',False)
invoke('tm_free',0x101,0x10000008,66)
invoke('tm_free',0x101,0x10000108,114)
invoke('tm_alloc',0x101,60981796,0,0)
invoke('tm_free',0x101,0,0)
for off,expected in ((32,0),(48,3),(52,3),(56,1),(60,1),(64,0),(68,176),(72,0),(76,2),(92,6)):
 a.emit(d(32,9,30,off));a.emit(d(11,28,9,expected));a.cond('test_fail',False)
a.emit(mr(3,30));a.li(4,0);a.call('tm_finish');a.li(31,1);a.b('test_cleanup')
a.label('test_fail');a.li(31,-1)
a.label('test_cleanup');a.emit(d(32,0,1,0x70));a.emit(d(11,28,0,0));a.cond('no_unlock')
a.emit(mr(3,30));a.call('tm_unlock')
a.label('no_unlock');a.emit(d(36,31,29,36))
# All filesystem activity is after original checker return, on a new USB file.
# EXCL prevents replacing any prior evidence. Logger failure preserves result.
a.label('logger');path_fix=len(a.reloc);a.address(3,0,0) # fixed after labels/path known
a.li(4,0xc1);a.emit(d(14,5,1,0x78));a.li(6,0x1b6);a.li(7,0);a.li(8,0);a.li(11,801);a.emit(0x44000002)
a.emit(d(36,3,29,40));a.emit(d(11,28,3,0));a.cond('logged',False)
a.li(0,0);a.emit(ds(62,0,1,0x80));a.emit(d(32,3,1,0x78));a.emit(mr(4,29));a.li(5,256);a.emit(d(14,6,1,0x80));a.li(11,803);a.emit(0x44000002)
a.emit(d(36,3,29,44));a.emit(d(11,28,3,0));a.cond('close',False)
a.emit(ds(58,9,1,0x80));a.emit(d(11,29,9,256));a.cond('close',False) # full64 nwrite compare
a.li(9,0x50364654);a.emit(d(36,9,1,0x90));a.emit(d(36,3,1,0x94))
a.li(9,256);a.emit(ds(62,9,1,0x98))
a.emit(d(32,3,1,0x78));a.emit(d(14,4,1,0x90));a.li(5,16);a.emit(d(14,6,1,0x80));a.li(11,803);a.emit(0x44000002)
a.label('close');a.emit(d(32,3,1,0x78));a.li(11,804);a.emit(0x44000002)
a.label('logged')
for r,off in ((29,0xa0),(30,0xa8),(31,0xb0),(2,0xb8)):a.emit(ds(58,r,1,off))
a.emit(ds(58,0,1,0xd0));a.emit(0x7c0803a6);a.emit(d(14,1,1,0xc0))
a.label('return_zero');a.li(0,0);a.emit(0x4e800020)
code=a.finish();pathva=(start+len(code)+15)&~15
path=b'/dev_usb000/HDD2TB-P6.bin\0'
for i in (path_fix,path_fix+1):
 row=list(a.reloc[i]);row[5]=pathva;a.reloc[i]=tuple(row)
code=bytearray(code)
for off,z,vi,ai,t,add in a.reloc:
 val=ph[vi][3]+add;struct.pack_into('>H',code,off-start,(val if t==4 else (val+0x8000)>>16)&65535)
assert pathva+len(path)<=ph[0][5]
new=bytearray(old);new[0xf0+start:0xf0+start+len(code)]=code
new[0xf0+pathva:0xf0+pathva+len(path)]=path
hooks=[(0x10ea0,bytes.fromhex('7fde07b4'),a.labels['entry']),
       (0x10ec8,bytes.fromhex('38000000'),a.labels['finish'])]
for va,expected,target in hooks:
 assert new[0xf0+va:0xf0+va+4]==expected
 assert not any(r[3]==0 and va<=r[0]<va+4 for r in [struct.unpack_from('>QHBBIQ',old,i) for i in range(ph[2][2],len(old),24)])
 new[0xf0+va:0xf0+va+4]=struct.pack('>I',branch(va,target,1))
new.extend(b''.join(struct.pack('>QHBBIQ',*r) for r in a.reloc))
struct.pack_into('>Q',new,phoff+2*56+32,ph[2][5]+24*len(a.reloc))
cs=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
listing=list(cs.disasm(bytes(code),start));assert sum(i.size for i in listing)==len(code)
(OUT/'diagnostic-code.txt').write_text(''.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}\n' for i in listing))
(OUT/'libfs_utility_init-p6.elf').write_bytes(new)
report={'purpose':'Callback-capable full-checker route witness and synthetic compiled telemetry selftest; no native allocator hooks/peak measurement',
 'source_layout_sha256':layout['output_sha256'],'output_sha256':hashlib.sha256(new).hexdigest(),
 'hooks':[{'va':hex(v),'before':b.hex(),'target':hex(t)} for v,b,t in hooks],
 'labels':{n:hex(v) for n,v in a.labels.items()},'code_start':hex(start),'code_bytes':len(code),
 'path_va':hex(pathva),'path':path[:-1].decode(),'new_relocations':a.reloc,
 'header_offset':hex(headeroff),'record_offset':hex(headeroff+128),'record_size':core['record_bytes'],
 'output_file_bytes':272,'logging':'USB only, create exclusive, first256 bytes plus16-byte first-write status/size footer; close outcome not serialized',
 'allocator_hooks_installed':False,'native_heap_pointer_reads':False,
 'console_or_firmware_operations_performed':False,'release_approved':False}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('output_sha256','code_start','code_bytes','output_file_bytes','allocator_hooks_installed')},indent=2))
