"""P8 native allocation diagnostic, offline only; P6 assets remain immutable.

Observe one callback export/heap. Bounded native prefix reads only after C
authorization. Coverage is explicitly partial (indirect reachability unproven).
"""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
OUT=ROOT/'analysis/dev006/p8-native';OUT.mkdir(exist_ok=True)
layout=json.loads((ROOT/'analysis/dev006/p8-telemetry-layout/layout-audit.json').read_text(encoding='utf-8'))
old=(ROOT/'analysis/dev006/p8-telemetry-layout/libfs_utility_init-owned-space.elf').read_bytes()
assert hashlib.sha256(old).hexdigest()==layout['output_sha256']
core=json.loads((ROOT/'analysis/dev006/p8-telemetry-core/validation.json').read_text(encoding='utf-8'));assert core['pass']
for p,h in core['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
coreva=int(layout['new_code_va'],16)
functions={x['name']:coreva+int(x['offset'],16) for x in core['target_functions']}
phoff=struct.unpack_from('>Q',old,32)[0]
ph=[struct.unpack_from('>IIQQQQQQ',old,phoff+56*i) for i in range(3)]
start=(coreva+core['target_text_bytes']+15)&~15
headeroff=int(layout['diagnostic_header_relative_offset'],16)
def d(op,rt,ra,imm):return op<<26|rt<<21|ra<<16|(imm&65535)
def ds(op,rt,ra,imm,xo=0):assert imm%4==0;return d(op,rt,ra,imm)|xo
def mr(dst,src):return 31<<26|src<<21|dst<<16|src<<11|444<<1
def branch(pc,target,link=0):
    delta=target-pc;assert delta%4==0 and -(1<<25)<=delta<(1<<25)
    return 0x48000000|(delta&0x3fffffc)|link
def cmpw(a,b):return 31<<26|7<<23|a<<16|b<<11
class Asm:
    def __init__(self,base):self.base=base;self.words=[];self.labels={};self.fix=[];self.reloc=[]
    def pc(self):return self.base+4*len(self.words)
    def emit(self,w):self.words.append(w)
    def label(self,n):assert n not in self.labels;self.labels[n]=self.pc()
    def b(self,n,link=0):self.fix.append((len(self.words),'b',n,link));self.emit(0)
    def cond(self,n,equal=True,cr7=True):self.fix.append((len(self.words),'bc',n,(equal,cr7)));self.emit(0)
    def call(self,n):self.emit(branch(self.pc(),functions[n],1))
    def native(self,target):self.emit(branch(self.pc(),target,1));self.emit(ds(58,2,1,0xb0))
    def address(self,reg,seg,value):
        self.reloc.extend([(self.pc()+2,0,seg,0,6,value),(self.pc()+6,0,seg,0,4,value)])
        value+=ph[seg][3];self.emit(d(15,reg,0,(value+0x8000)>>16));self.emit(d(14,reg,reg,value))
    def li(self,reg,value):
        if -32768<=value<=32767:self.emit(d(14,reg,0,value))
        else:self.emit(d(15,reg,0,value>>16));self.emit(d(24,reg,reg,value))
    def finish(self):
        for i,kind,n,arg in self.fix:
            pc=self.base+4*i;target=self.labels[n]
            if kind=='b':self.words[i]=branch(pc,target,arg)
            else:
                eq,cr7=arg;delta=target-pc;assert delta%4==0 and -32768<=delta<32768
                self.words[i]=((0x419e0000 if eq else 0x409e0000) if cr7 else (0x41820000 if eq else 0x40820000))|(delta&65535)
        return bytearray(b''.join(struct.pack('>I',w) for w in self.words))
a=Asm(start)
FRAME=0x100
def prolog(name):
    a.label(name)
    # Native import normally publishes caller TOC at caller+28; preserve that
    # side effect although our import call now executes in its own frame.
    a.emit(ds(62,2,1,0x28));a.emit(0x7c0802a6)
    a.emit(ds(62,1,1,-FRAME,1));a.emit(ds(62,0,1,FRAME+0x10))
    for r in range(3,11):a.emit(ds(62,r,1,0x70+8*(r-3)))
    a.emit(ds(62,2,1,0xb0))
    for r in range(28,32):a.emit(ds(62,r,1,0xc8+8*(r-28)))
    a.address(29,1,headeroff);a.emit(d(14,30,29,128))
    a.li(0,0);a.emit(d(36,0,1,0xf0)) # observer lock ownership
def args():
    for r in range(3,11):a.emit(ds(58,r,1,0x70+8*(r-3)))
def epilog(result=True):
    if result:a.emit(ds(58,3,1,0xb8))
    for r in range(28,32):a.emit(ds(58,r,1,0xc8+8*(r-28)))
    a.emit(ds(58,2,1,0xb0));a.emit(ds(58,0,1,FRAME+0x10))
    a.emit(0x7c0803a6);a.emit(d(14,1,1,FRAME));a.emit(0x4e800020)
def check_running(fallback,identity=True):
    for reg,off,value in ((9,4,1),(9,88,1)):
        a.emit(d(32,reg,29,off));a.emit(d(11,28,reg,value));a.cond(fallback,False)
    a.emit(d(32,9,30,36));a.emit(d(11,28,9,1));a.cond(fallback,False)
    if identity:
        a.emit(d(32,9,30,20));a.emit(d(32,10,1,0x74));a.emit(cmpw(9,10));a.cond(fallback,False)
def lock(fallback):
    a.emit(mr(3,30));a.call('tm_try_lock');a.emit(d(11,28,3,1));a.cond(fallback,False)
    a.li(0,1);a.emit(d(36,0,1,0xf0))
def unlock():a.emit(mr(3,30));a.call('tm_unlock');a.li(0,0);a.emit(d(36,0,1,0xf0))
def inc(off):a.emit(d(32,9,29,off));a.emit(d(14,9,9,1));a.emit(d(36,9,29,off))
def recargs():a.emit(mr(3,30));a.emit(d(32,4,30,20))

# One-shot claim before the original callback-capable heap setup.
a.label('entry');a.address(9,1,headeroff)
a.label('claim');a.emit(31<<26|10<<21|9<<11|20<<1)
a.emit(d(11,28,10,0));a.cond('entry_done',False)
a.emit(mr(10,1));a.emit(31<<26|10<<21|9<<11|150<<1|1);a.cond('claim',False,False);a.emit(0x7c2004ac)
a.li(10,1);a.emit(d(36,10,9,4));a.emit(d(36,28,9,8));a.emit(d(36,31,9,12))
a.emit(d(36,26,9,16));a.emit(d(36,10,9,20));a.emit(ds(62,24,9,24))
a.li(10,-1)
for off in (32,40,44):a.emit(d(36,10,9,off))
for off,w in zip((48,52,56,60),(0x48444432,0x54422d50,0x382d4e41,0x54490000)):
    a.li(10,w);a.emit(d(36,10,9,off))
a.emit(d(36,30,9,96));a.emit(d(36,29,9,100)) # argc/argv pointer, never dereferenced
a.label('entry_done');a.emit(0x7fde07b4);a.emit(0x4e800020)

# This exact create site uses an 8-byte local parameter structure at original
# SP+70, whose backing must match the claimed export's supplied buffer.
prolog('create');a.li(28,0)
a.emit(d(32,9,29,4));a.emit(d(11,28,9,1));a.cond('create_native',False)
a.emit(d(32,9,29,88));a.emit(d(11,28,9,0));a.cond('create_native',False)
a.emit(d(32,9,29,12));a.emit(d(32,10,1,0x7c));a.emit(cmpw(9,10));a.cond('create_native',False)
a.emit(d(14,9,1,FRAME+0x70));a.emit(cmpw(9,6));a.cond('create_native',False)
a.emit(d(32,9,6,0));a.emit(d(11,28,9,8));a.cond('create_native',False)
a.emit(d(32,9,6,4));a.emit(d(32,10,29,8));a.emit(cmpw(9,10));a.cond('create_native',False)
a.li(9,0x80150000);a.emit(cmpw(5,9));a.cond('create_native',False)
a.li(28,1)
a.label('create_native');args();a.native(0x215e8);a.emit(ds(62,3,1,0xb8))
a.emit(d(11,28,28,1));a.cond('create_done',False)
inc(64);a.emit(d(11,28,3,0));a.cond('create_done')
a.emit(mr(5,3));a.emit(mr(3,30));a.li(4,1);a.emit(d(32,6,29,8));a.emit(d(32,7,29,12))
a.li(8,0) # explicit incomplete indirect coverage; TM_INCOMPLETE_COVERAGE stays set
a.call('tm_init');a.li(9,1);a.emit(d(36,9,29,88))
a.label('create_done');epilog()

prolog('malloc');check_running('malloc_native');lock('malloc_native');inc(72)
a.label('malloc_native');args();a.native(0x214a8);a.emit(ds(62,3,1,0xb8))
a.emit(d(32,9,1,0xf0));a.emit(d(11,28,9,1));a.cond('malloc_done',False)
recargs();a.emit(d(32,5,1,0xbc));a.call('tm_header_address')
a.li(28,0);a.emit(d(11,28,3,0));a.cond('malloc_no_header')
a.emit(d(32,28,3,0)) # ONLY native heap read, C authorized address
a.label('malloc_no_header');recargs();a.emit(d(32,5,1,0x7c));a.emit(d(32,6,1,0xbc));a.emit(mr(7,28));a.call('tm_alloc');unlock()
a.label('malloc_done');epilog()

prolog('free');check_running('free_native');lock('free_native');inc(76)
recargs();a.emit(d(32,5,1,0x7c));a.call('tm_prepare_free')
a.li(28,0);a.emit(d(11,28,3,0));a.cond('free_native')
a.emit(d(32,28,3,0)) # known live chunk, saved BEFORE original native free
a.label('free_native');args();a.native(0x21568);a.emit(ds(62,3,1,0xb8))
a.emit(d(32,9,1,0xf0));a.emit(d(11,28,9,1));a.cond('free_done',False)
recargs();a.emit(d(32,5,1,0x7c));a.emit(mr(6,28));a.call('tm_free');unlock()
a.label('free_done');epilog()

# Freeze accounting before whole-heap deletion; no invented individual frees.
prolog('delete');check_running('delete_native');lock('delete_native');inc(68)
a.emit(mr(3,30));a.li(4,0);a.call('tm_finish');unlock()
a.label('delete_native');args();a.native(0x215c8);a.emit(ds(62,3,1,0xb8));epilog()

# The full-work scan call is reached only beyond the quick-check branch.
prolog('full_worker');check_running('worker_native',False);lock('worker_native');inc(104);unlock()
a.label('worker_native');args();a.native(0x1f230);a.emit(ds(62,3,1,0xb8));epilog()

# Snapshot only after original export returns, then fixed exclusive USB log.
prolog('finish');a.emit(d(32,9,29,0));a.emit(d(14,10,1,FRAME));a.emit(cmpw(9,10));a.cond('finish_done',False)
a.emit(d(32,9,29,4));a.emit(d(11,28,9,1));a.cond('finish_done',False)
a.li(9,2);a.emit(d(36,9,29,4));a.emit(d(36,27,29,32))
a.emit(d(32,9,29,88));a.emit(d(11,28,9,1));a.cond('logger',False)
a.emit(mr(3,30));a.call('tm_try_lock');a.emit(d(36,3,29,92));a.emit(d(11,28,3,1));a.cond('logger',False)
a.emit(d(32,9,30,36));a.emit(d(11,28,9,1));a.cond('already_finished',False)
a.emit(mr(3,30));a.emit(mr(4,27));a.call('tm_finish')
a.li(9,1);a.emit(d(36,9,29,84)) # missing observed native heap deletion
a.label('already_finished');a.emit(d(36,27,30,88));a.emit(mr(3,30));a.call('tm_unlock')
a.label('logger');path_fix=len(a.reloc);a.address(3,0,0)
a.li(4,0xc1);a.emit(d(14,5,1,0xe8));a.li(6,0x1b6);a.li(7,0);a.li(8,0);a.li(11,801);a.emit(0x44000002)
a.emit(d(36,3,29,40));a.emit(d(11,28,3,0));a.cond('finish_done',False)
a.li(0,0);a.emit(ds(62,0,1,0xf8));a.emit(d(32,3,1,0xe8));a.emit(mr(4,29));a.li(5,256);a.emit(d(14,6,1,0xf8));a.li(11,803);a.emit(0x44000002)
a.emit(d(36,3,29,44));a.emit(d(11,28,3,0));a.cond('close',False)
a.emit(ds(58,9,1,0xf8));a.emit(d(11,29,9,256));a.cond('close',False)
# Footer in argument spill slots no longer used by this return hook.
a.li(9,0x50384654);a.emit(d(36,9,1,0x70));a.emit(d(36,3,1,0x74));a.li(9,256);a.emit(ds(62,9,1,0x78))
a.emit(d(32,3,1,0xe8));a.emit(d(14,4,1,0x70));a.li(5,16);a.emit(d(14,6,1,0xf8));a.li(11,803);a.emit(0x44000002)
a.label('close');a.emit(d(32,3,1,0xe8));a.li(11,804);a.emit(0x44000002)
a.label('finish_done');epilog(False)
# epilog's BLR must instead return r0=0 for the overwritten li r0,0.
a.words[-1:-1]=[d(14,0,0,0)]
code=a.finish();pathva=(start+len(code)+15)&~15;path=b'/dev_usb000/HDD2TB-P8.bin\0'
for i in (path_fix,path_fix+1):
    row=list(a.reloc[i]);row[5]=pathva;a.reloc[i]=tuple(row)
for off,z,vi,ai,t,add in a.reloc:
    val=ph[vi][3]+add;struct.pack_into('>H',code,off-start,(val if t==4 else (val+0x8000)>>16)&65535)
assert pathva+len(path)<=ph[0][5]
new=bytearray(old);new[0xf0+start:0xf0+start+len(code)]=code;new[0xf0+pathva:0xf0+pathva+len(path)]=path
hooks=[(0x10ea0,'7fde07b4','entry'),(0x10ec8,'38000000','finish'),(0xea58,'48012b91','create'),(0xe6f8,'48012db1','malloc'),(0xe788,'48012de1','free'),(0xe9d8,'48012bf1','delete'),(0x186f0,'48006b41','full_worker')]
oldrels=[struct.unpack_from('>QHBBIQ',old,i) for i in range(ph[2][2],len(old),24)]
for va,expected,name in hooks:
    assert new[0xf0+va:0xf0+va+4].hex()==expected
    assert not any(r[3]==0 and va<=r[0]<va+4 for r in oldrels)
    struct.pack_into('>I',new,0xf0+va,branch(va,a.labels[name],1))
new.extend(b''.join(struct.pack('>QHBBIQ',*r) for r in a.reloc));struct.pack_into('>Q',new,phoff+112+32,ph[2][5]+24*len(a.reloc))
cs=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN);listing=list(cs.disasm(bytes(code),start));assert sum(x.size for x in listing)==len(code)
(OUT/'native-code.txt').write_text(''.join(f'{x.address:08x} {x.bytes.hex()} {x.mnemonic} {x.op_str}\n' for x in listing),encoding='utf-8')
(OUT/'libfs_utility_init-p8.elf').write_bytes(new)
report={'purpose':'One callback-export native heap observer; explicitly partial coverage, full-worker witness, bounded authorized chunk-prefix reads',
 'source_layout_sha256':layout['output_sha256'],'output_sha256':hashlib.sha256(new).hexdigest(),
 'hooks':[{'va':hex(v),'before':b,'target':hex(a.labels[n]),'name':n} for v,b,n in hooks],
 'labels':{n:hex(v) for n,v in a.labels.items()},'code_start':hex(start),'code_bytes':len(code),'path_va':hex(pathva),'path':path[:-1].decode(),
 'new_relocations':a.reloc,'header_offset':hex(headeroff),'record_offset':hex(headeroff+128),'record_size':131200,'output_file_bytes':272,
 'frame_bytes':FRAME,'coverage_complete':False,'coverage_policy':'tm_init coverage0 sets TM_INCOMPLETE_COVERAGE512; indirect calls and other heaps unproven; observed accounting peak is neither a certified native peak nor a guaranteed bound',
 'native_read_sites':[hex(x.address) for x in listing if x.mnemonic=='lwz' and x.op_str=='r28, 0(r3)'],
 'native_allocator_hooks_installed':True,'hardware_tested':False,'release_approved':False}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('output_sha256','code_bytes','native_read_sites','coverage_complete')}))
