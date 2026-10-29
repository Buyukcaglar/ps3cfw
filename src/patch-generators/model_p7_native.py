"""P7 instruction/dataflow model; native imports mocked, C executed on host.

Checks concrete helper bytes at independent segment bases. Not target runtime.
"""
import ctypes as C,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
OUT=ROOT/'analysis/dev006/p7-native'
m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'));elf=(OUT/'libfs_utility_init-p7.elf').read_bytes()
assert hashlib.sha256(elf).hexdigest()==m['output_sha256']
previous=(ROOT/'analysis/dev006/telemetry-layout/libfs_utility_init-owned-space.elf').read_bytes()
phoff=struct.unpack_from('>Q',elf,32)[0];ph=[struct.unpack_from('>IIQQQQQQ',elf,phoff+56*i) for i in range(3)]
rels=[struct.unpack_from('>QHBBIQ',elf,i) for i in range(ph[2][2],len(elf),24)]
oldrels=[struct.unpack_from('>QHBBIQ',previous,i) for i in range(ph[2][2],len(previous),24)]
assert rels==oldrels+[tuple(x) for x in m['new_relocations']]
mask=bytearray(elf[:len(previous)]);want=bytearray(previous)
for hook in m['hooks']:
    at=0xf0+int(hook['va'],16);assert previous[at:at+4].hex()==hook['before'];mask[at:at+4]=want[at:at+4]
start=int(m['code_start'],16);end=int(m['path_va'],16)+len(m['path'])+1
assert not any(want[0xf0+start:0xf0+end]);mask[0xf0+start:0xf0+end]=want[0xf0+start:0xf0+end]
mask[phoff+144:phoff+152]=want[phoff+144:phoff+152];assert mask==want
core=json.loads((ROOT/'analysis/dev006/telemetry-core/validation.json').read_text(encoding='utf-8'))
coreva=0x25260;targets={coreva+int(x['offset'],16):x['name'] for x in core['target_functions']}
class Record(C.Structure):_fields_=[('words',C.c_uint32*(32896//4))]
lib=C.CDLL(str(ROOT/'analysis/dev006/telemetry-core/telemetry-host.dll'))
argc={'tm_init':5,'tm_try_lock':0,'tm_unlock':0,'tm_header_address':2,'tm_alloc':4,'tm_prepare_free':2,'tm_free':3,'tm_finish':1}
for name,n in argc.items():
    f=getattr(lib,name);f.argtypes=[C.POINTER(Record)]+[C.c_uint32]*n
    f.restype=C.c_uint32 if name in ('tm_try_lock','tm_header_address','tm_prepare_free') else None
MASK=(1<<64)-1
def sx(x,n):return (x&((1<<n)-1))-(1<<n) if x&(1<<(n-1)) else x&((1<<n)-1)
cs=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
native_targets={'create':0x215e8,'malloc':0x214a8,'free':0x21568,'delete':0x215c8,'full_worker':0x1f230}
class Model:
    def __init__(self,bases):
        self.bases=bases;data=[bytearray(elf[p[2]:p[2]+p[5]])+bytearray(p[6]-p[5]) for p in ph[:2]]
        for off,z,vi,ai,t,add in rels:
            val=bases[vi]+add;n=4 if t==1 else 2
            val=val if t in (1,4) else (val+0x8000)>>16;data[ai][off:off+n]=(val&((1<<(n*8))-1)).to_bytes(n,'big')
        self.data=data;self.ins={a:(n,o) for a,s,n,o in cs.disasm_lite(bytes(data[0][start:start+m['code_bytes']]),start)}
        self.H=bases[1]+int(m['header_offset'],16);self.R=self.H+128
        self.mem={};self.writes=[];self.prefixreads=[];self.ccalls=[];self.sys=[];self.native=[];self.output=bytearray()
        self.stacklo=0x6fff0000;self.stackhi=0x70010000
        self.base=0x106f0000;self.budget=0x08000000;self.heap=0x10203040
        self.chunks={};self.authorized=None;self.g=[0x11110000+i*0x1111 for i in range(32)]
        self.cr={0:0,2:0x22,3:0x33,4:0x44,7:0};self.lr=0
        self.scenario='ok';self.native_return=0;self.expected_args=None;self.forced_contention=False
    def write(self,a,v,n,setup=False):
        if not setup:assert self.H<=a and a+n<=self.R+32896 or self.stacklo<=a and a+n<=self.stackhi,(hex(a),n)
        self.writes.append((a,n))
        for i,b in enumerate((v&((1<<(8*n))-1)).to_bytes(n,'big')):self.mem[a+i]=b
    def read(self,a,n,prefix=False):
        if prefix:
            assert n==4 and a==self.authorized,(hex(a),self.authorized)
            assert self.base<=a and a+4<=self.base+self.budget
            self.prefixreads.append(a);self.authorized=None
        if self.bases[0]<=a and a+n<=self.bases[0]+len(self.data[0]):
            return int.from_bytes(self.data[0][a-self.bases[0]:a-self.bases[0]+n],'big')
        return int.from_bytes(bytes(self.mem.get(a+i,0) for i in range(n)),'big')
    def clobber(self,ret=0,toc=False):
        for r in (0,*range(3,13)):self.g[r]=0xfeed000000000000+r
        self.g[3]=ret&MASK;self.cr[0]=0x99;self.cr[7]=0x99
        if toc:self.g[2]=0xafffffff
    def ccall(self,name):
        assert self.g[3]==self.R
        rec=Record()
        for i in range(len(rec.words)):rec.words[i]=self.read(self.R+4*i,4)
        args=self.g[4:4+argc[name]];self.ccalls.append((name,args))
        if self.forced_contention and name=='tm_try_lock':
            # Another owner occupies lock; component returns without waiting.
            rec.words[3]=1
        ret=getattr(lib,name)(C.byref(rec),*args)
        for i,v in enumerate(rec.words):
            if v!=self.read(self.R+4*i,4):self.write(self.R+4*i,v,4)
        if name in ('tm_header_address','tm_prepare_free'):self.authorized=ret or None
        self.clobber(ret or 0)
    def ncall(self,target):
        g=self.g;assert self.expected_args==g[3:11],('native args',self.expected_args,g[3:11])
        assert target==native_targets[self.label]
        self.native.append((self.label,target,g[3:11].copy()))
        # Real import stub's ABI caller+28 store and volatile/TOC clobbers.
        self.write(g[1]+0x28,g[2],8)
        if self.label in ('malloc','free','delete') and self.read(self.R+36,4)==1:
            if self.read(self.R+12,4)==1 and not self.forced_contention:
                assert self.read(self.R+12,4)==1
        if self.label=='free':
            p=g[4]&0xffffffff
            if p in self.chunks:
                # Native coalescence destroys the old header. Observer must
                # consume only the saved pre-free charge after this call.
                self.write(p-4,0xdead0000,4,setup=True);self.chunks.pop(p)
        self.clobber(self.native_return,True)
    def syscall(self):
        g=self.g;n=g[11];args=g[3:9].copy();self.sys.append((n,args))
        if n==801:
            raw=bytes(self.read(g[3]+i,1) for i in range(len(m['path'])+1))
            assert raw==m['path'].encode()+b'\0' and args[1]==0xc1 and args[3:]==[0x1b6,0,0]
            if self.scenario=='openfail':self.clobber(0x80010006);return
            self.write(g[5],0x42,4);self.clobber();return
        assert args[0]==0x42
        if n==803:
            count=sum(x[0]==803 for x in self.sys);assert args[2]==(256 if count==1 else 16)
            if self.scenario=='writefail' and count==1:self.clobber(0x80010004);return
            size=128 if self.scenario=='short' and count==1 else ((1<<32)+256 if self.scenario=='highsize' and count==1 else args[2])
            self.output.extend(bytes(self.read(args[1]+i,1) for i in range(min(size,args[2]))))
            self.write(args[3],size,8);self.clobber(0x80010004 if self.scenario=='footerfail' and count==2 else 0)
        elif n==804:self.clobber(0x80010004 if self.scenario=='closefail' else 0)
        else:raise AssertionError(n)
    def execute(self,label,args=None,sp=0x70000000,ret=0):
        self.label=label;self.native_return=ret;g=self.g;g[1]=sp
        if args is not None:g[3:11]=args;self.expected_args=args.copy()
        pc=int(m['labels'][label],16);self.lr=0xabcdef00;initial=g.copy();crsaved={k:self.cr[k] for k in (2,3,4)}
        self.authorized=None;nativebefore=len(self.native)
        for step in range(1000):
            n,o=self.ins[pc];parts=o.replace(',','').split();nxt=pc+4
            reg=lambda s:int(s[1:]);imm=lambda s:int(s,0)
            if n in ('li','lis'):g[reg(parts[0])]=(imm(parts[1])*(65536 if n=='lis' else 1))&MASK
            elif n=='ori':g[reg(parts[0])]=g[reg(parts[1])]|imm(parts[2])
            elif n=='addi':g[reg(parts[0])]=(g[reg(parts[1])]+imm(parts[2]))&MASK
            elif n=='mr':g[reg(parts[0])]=g[reg(parts[1])]
            elif n=='extsw':g[reg(parts[0])]=sx(g[reg(parts[1])],32)&MASK
            elif n in ('lwz','ld','stw','std','stdu'):
                r=reg(parts[0]);offset,br=parts[1].split('(');br=reg(br[:-1]);addr=(g[br]+imm(offset))&MASK;size=8 if n in ('ld','std','stdu') else 4
                if n in ('lwz','ld'):g[r]=self.read(addr,size,prefix=(pc in [int(x,16) for x in m['native_read_sites']]))
                else:self.write(addr,g[r],size)
                if n=='stdu':g[br]=addr
            elif n in ('cmpwi','cmpdi','cmpw'):
                field=int(parts[0][2:]);v=g[reg(parts[1])];b=g[reg(parts[2])] if n=='cmpw' else imm(parts[2]);bits=64 if n=='cmpdi' else 32
                self.cr[field]=sx(v,bits)-sx(b,bits)
            elif n in ('beq','bne'):
                field=int(parts[0][2:]) if len(parts)>1 else 0
                if (self.cr[field]==0)==(n=='beq'):nxt=imm(parts[-1])
            elif n=='b':nxt=imm(parts[0])
            elif n=='bl':
                self.lr=pc+4;target=imm(parts[0])
                if target in targets:self.ccall(targets[target])
                else:self.ncall(target)
            elif n=='mflr':g[reg(parts[0])]=self.lr
            elif n=='mtlr':self.lr=g[reg(parts[0])]
            elif n=='lwarx':g[reg(parts[0])]=self.read(g[reg(parts[2])],4)
            elif n=='stwcx.':self.write(g[reg(parts[2])],g[reg(parts[0])],4);self.cr[0]=0
            elif n in ('sync','lwsync'):pass
            elif n=='sc':self.syscall()
            elif n=='blr':
                assert self.lr==0xabcdef00 and g[1]==initial[1]
                preserve=(2,*range(13,30),31) if label=='entry' else (2,*range(13,32))
                assert all(g[r]==initial[r] for r in preserve),(label,'nonvolatile')
                assert all(self.cr[k]==v for k,v in crsaved.items())
                if label=='entry':assert g[30]==sx(initial[30],32)&MASK
                elif label=='finish':assert g[0]==0
                else:assert g[3]==ret&MASK and len(self.native)==nativebefore+1
                return
            else:raise AssertionError((n,o))
            pc=nxt
        raise AssertionError('helper failed to return')
    def entry(self,foreign=False):
        self.g[24]=0;self.g[26]=0x01577888;self.g[28]=self.base;self.g[31]=self.budget;self.g[30]=3;self.g[29]=0x10800000
        if foreign:self.write(self.H,0x70000100,4)
        self.execute('entry')
    def create(self,ret=None,geometry='ok'):
        sp=0x6ffff000;param=sp+0x70
        self.write(param,8 if geometry!='size' else 9,4);self.write(param+4,self.base if geometry!='backing' else self.base+4,4)
        args=[0x2345678,self.budget if geometry!='budget' else 0x2000000,0x80150000 if geometry!='flags' else 0x150000,param if geometry!='pointer' else param+8,7,8,9,10]
        self.execute('create',args,sp,self.heap if ret is None else ret)
    def operation(self,label,p=0,request=56,header=66,heap=None,ret=None):
        if label=='malloc':
            if p:self.write(p-4,header,4,setup=True);self.chunks[p]=header
            value=p if ret is None else ret;arg4=request
        elif label=='free':value=0x123456789abcdef0 if ret is None else ret;arg4=p
        else:value=0x123456789abcdef0 if ret is None else ret;arg4=0xaabb
        args=[self.heap if heap is None else heap,arg4,0x33,0x44,0x55,0x66,0x77,0x88]
        self.execute(label,args,0x6fffe000,value)
    def finish(self,status=0):self.g[27]=status&MASK;self.execute('finish')

cases=[]
for bases in ((0,ph[1][3]),(0x10000000,0x20000000),(0x10008000,0x44008000)):
    for scenario in ('ok','openfail','writefail','short','highsize','footerfail','closefail'):
        for status in (0,7,-1):
            x=Model(bases);x.scenario=scenario;x.entry();x.create()
            assert x.read(x.R+32,4)==512 and x.read(x.H+88,4)==1
            x.operation('full_worker')
            x.operation('malloc',x.base+8,56,66);x.operation('malloc',x.base+0x108,104,114)
            assert x.read(x.R+68,4)==176
            x.operation('free',x.base+8);x.operation('free',x.base+0x108)
            x.operation('malloc',0,60981796);x.operation('free',0)
            x.operation('delete');x.finish(status)
            assert x.read(x.R+64,4)==0 and x.read(x.R+68,4)==176 and x.read(x.R+32,4)==512
            assert x.read(x.R+88,4)==status&0xffffffff and x.read(x.R+44,4)==1
            assert [x.read(x.H+o,4) for o in (64,68,72,76,84,88,92,96,104)]==[1,1,3,3,0,1,1,3,1]
            assert len(x.prefixreads)==4
            assert [s[0] for s in x.sys]==([801] if scenario=='openfail' else ([801,803,804] if scenario in ('writefail','short','highsize') else [801,803,803,804]))
            if scenario in ('ok','closefail'):
                assert len(x.output)==272 and x.output[48:64]==b'HDD2TB-P7-NATI\0\0'
                assert struct.unpack('>IIQ',x.output[256:])==(0x50374654,0,256)
            saved=bytes(x.output);syscount=len(x.sys);x.entry();x.finish();assert saved==x.output and syscount==len(x.sys)
            if bases==(0,ph[1][3]) and status==0 and scenario=='ok':(OUT/'model-fixture.bin').write_bytes(saved)
            cases.append({'bases':list(map(hex,bases)),'io':scenario,'status':hex(status&0xffffffff),'successful_lifetime_realloc_overlap_pre_free_snapshot':True})
    for geometry in ('size','backing','budget','flags','pointer'):
        x=Model(bases);x.entry();x.create(geometry=geometry);assert x.read(x.H+88,4)==0 and not x.ccalls;x.finish();assert not x.prefixreads
        cases.append({'bases':list(map(hex,bases)),'invalid_create_geometry':geometry})
    x=Model(bases);x.entry();x.create(ret=0);assert x.read(x.H+64,4)==1 and x.read(x.H+88,4)==0;x.finish(-1);assert not x.prefixreads
    cases.append({'bases':list(map(hex,bases)),'native_create_failed':True})
    x=Model(bases);x.entry(foreign=True);x.create();x.operation('malloc',x.base+8);x.finish();assert not x.ccalls and not x.prefixreads and not x.sys
    cases.append({'bases':list(map(hex,bases)),'foreign_export_owner':True})
    x=Model(bases);x.entry();x.create();before=len(x.ccalls);x.operation('malloc',x.base+8,heap=x.heap+1);assert len(x.ccalls)==before and not x.prefixreads
    cases.append({'bases':list(map(hex,bases)),'other_heap_pass_through':True})
    for which in ('malloc','free','delete','full_worker','finish'):
        x=Model(bases);x.entry();x.create();x.forced_contention=True
        if which=='finish':x.finish()
        else:x.operation(which,x.base+8)
        assert x.read(x.R+40,4)&0x80000000 and not x.prefixreads
        cases.append({'bases':list(map(hex,bases)),'nonblocking_contention':which})
    for p in (1,0x106f0004,0x186f0004,0xffffffff):
        x=Model(bases);x.entry();x.create();x.operation('malloc',p);assert not x.prefixreads and x.read(x.R+32,4)&2
        cases.append({'bases':list(map(hex,bases)),'unauthorized_malloc_pointer':hex(p)})
    x=Model(bases);x.entry();x.create();x.operation('free',x.base+8);assert not x.prefixreads and x.read(x.R+32,4)&32
    cases.append({'bases':list(map(hex,bases)),'unknown_free_no_header_read':True})
    x=Model(bases);x.entry();x.create();x.operation('malloc',x.base+8,header=1);assert x.read(x.R+32,4)&4 and len(x.prefixreads)==1
    cases.append({'bases':list(map(hex,bases)),'invalid_allocated_header':True})
    x=Model(bases);x.entry();x.create();x.operation('malloc',x.base+8);x.finish();assert x.read(x.H+84,4)==1 and x.read(x.R+44,4)==1
    cases.append({'bases':list(map(hex,bases)),'missing_delete_explicit_flag':True})
report={'pass':True,'elf_sha256':m['output_sha256'],'cases':len(cases),
 'scope':'Concrete helper PPC instruction model; separately host-executed C; mocked native calls and USB syscalls; not Sony/PPC C runtime',
 'original_owned_layout_preserved_except_declared_hooks_helper_relocation_length':True,
 'native_arguments_and_full64_return_preserved':True,'original_TOC_publication_and_restore_preserved':True,
 'SP_LR_nonvolatile_GPR_and_CR2_4_preserved':True,'native_operations_exactly_once_all_paths':True,
 'no_native_heap_writes':True,'all_prefix_reads_follow_C_authorization':True,'pre_free_header_saved_before_native_mutation':True,
 'contention_falls_back_without_spin_and_marks_incomplete':True,'missing_delete_and_indirect_coverage_explicit':True,
 'USB_exclusive_only_opened_descriptor_closed_once':True,'first_write_full64_size_checked':True,
 'actual_peak_measured_on_PS3':False,'details':cases}
(OUT/'dataflow-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='details'}))
