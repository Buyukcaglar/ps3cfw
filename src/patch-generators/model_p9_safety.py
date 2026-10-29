"""Execute actual P9 helper/caller instructions against bounded memory/call oracles."""
import hashlib,json,random,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
O=R/'analysis/dev006/p9-safety-model-v3';O.mkdir(exist_ok=False)
M=json.loads((R/'analysis/dev006/p9-safety-v2/manifest.json').read_text('utf8'))
B=(R/'analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf').read_bytes()
OLD=(R/M['source']).read_bytes();assert hashlib.sha256(B).hexdigest()==M['output_sha256']
phoff=struct.unpack_from('>Q',B,32)[0];ph=[struct.unpack_from('>IIQQQQQQ',B,phoff+i*56) for i in range(3)]
def off(v):
    h=next(h for h in ph if h[0]==1 and h[3]<=v<h[3]+h[5]);return h[2]+v-h[3]
cs=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
MASK=(1<<64)-1
def sx(v,n):return (v&((1<<n)-1))-(1<<n) if v&(1<<(n-1)) else v&((1<<n)-1)
class MemoryFault(Exception):pass
class CPU:
    def __init__(self,blob=B,toc=0x102e7c0):
        self.code={i.address:(i.mnemonic,i.op_str) for lo,hi in ((0xe718,0xe770),(0xe7a4,0xe818),(0x16888,0x168ac),(0x26400,0x264fc))
                   for i in cs.disasm(blob[off(lo):off(lo)+hi-lo],lo)}
        self.g=[0x1234000000000000+i*0x101 for i in range(32)];self.g[1]=0x70000000;self.g[2]=toc
        self.cr={i:i*17+1 for i in range(8)};self.lr=0x77777700
        self.mem={};self.regions=[(0x6fffe000,0x70001000)]
        self.calls=[];self.writes=[];self.allocated=False;self.freed=False
        self.oldptr=0x11000000;self.newptr=0x12000000;self.oldbytes=0
        self.allocation_succeeds=True;self.newbytes=0;self.returned=False
        self.PG=0x23000000;self.CG=0x23000004;self.regions.append((self.PG,self.CG+4))
    def permitted(self,a,n):return n>=0 and any(lo<=a and a+n<=hi for lo,hi in self.regions)
    def read(self,a,n):
        if not self.permitted(a,n) or self.freed and self.oldptr<=a<self.oldptr+self.oldbytes:raise MemoryFault('Out-of-range or freed read')
        return bytes(self.mem.get(a+i,0) for i in range(n))
    def put(self,a,data,setup=False):
        if not self.permitted(a,len(data)):raise MemoryFault('Out-of-range write')
        if not setup:self.writes.append((a,len(data)))
        for i,v in enumerate(data):self.mem[a+i]=v
    def load(self,a,n):return int.from_bytes(self.read(a,n),'big')
    def store(self,a,v,n,setup=False):self.put(a,(v&((1<<(8*n))-1)).to_bytes(n,'big'),setup)
    def setup_old(self,cap,present=True):
        self.oldbytes=cap*4;self.g[3]=self.oldptr if present else 0
        if present:
            self.regions.append((self.oldptr,self.oldptr+self.oldbytes))
            if self.oldbytes<=262144:self.put(self.oldptr,bytes((i*73+19)&255 for i in range(self.oldbytes)),True)
    def clobber(self,ret=0,external=False):
        for i in (0,*range(3,13)):self.g[i]=(0xfeed000000000000+i)&MASK
        self.g[3]=ret&MASK
        for i in (0,1,5,6,7):self.cr[i]=0x5555
        if external:self.g[2]=0x99990000
    def call(self,target):
        g=self.g;args=g[3:12].copy();self.calls.append({'target':hex(target),'args':args})
        if target==0xe714:
            self.newbytes=g[3]&0xffffffff
            if self.allocation_succeeds:
                if self.newbytes>262144:raise MemoryFault('Model allocation budget')
                self.regions.append((self.newptr,self.newptr+self.newbytes));self.allocated=True
                self.put(self.newptr,b'\xa5'*self.newbytes,True);self.clobber(self.newptr)
            else:self.clobber(0)
        elif target==0x21508:
            dest,src,n=g[3:6]
            if not self.permitted(dest,n):raise MemoryFault('Out-of-range copy destination')
            payload=self.read(src,n)
            self.store(g[1]+0x28,g[2],8)
            self.put(dest,payload);self.clobber(dest,True)
        elif target==0xe7a0:
            assert (g[3]&0xffffffff)==self.oldptr and not self.freed
            self.freed=True;self.clobber()
        elif target==0x214e8:
            dest,value,n=g[3:6];self.store(g[1]+0x28,g[2],8)
            self.put(dest,bytes([value&255])*n);self.clobber(dest,True)
        else:raise AssertionError('Unexpected call '+hex(target))
    def run(self,start,ends=()):
        pc=start
        for _ in range(300):
            if pc in ends:return pc
            mn,ops=self.code[pc];a=ops.split(', ') if ops else [];nxt=pc+4
            def reg(t):return int(t[1:])
            def imm(t):return int(t,0)
            def address(t):
                d,r=t[:-1].split('(');return (self.g[reg(r)]+imm(d))&MASK
            if mn in ('li','lis'):self.g[reg(a[0])]=(imm(a[1])*(65536 if mn=='lis' else 1))&MASK
            elif mn=='ori':self.g[reg(a[0])]=self.g[reg(a[1])]|imm(a[2])
            elif mn=='addi':self.g[reg(a[0])]=(self.g[reg(a[1])]+imm(a[2]))&MASK
            elif mn=='mr':self.g[reg(a[0])]=self.g[reg(a[1])]
            elif mn=='clrldi':self.g[reg(a[0])]=self.g[reg(a[1])] & ((1<<(64-imm(a[2])))-1)
            elif mn=='rldicl':
                v=self.g[reg(a[1])];n=imm(a[2]);self.g[reg(a[0])]=((v<<n)|(v>>(64-n)))&((1<<(64-imm(a[3])))-1)
            elif mn=='slwi':self.g[reg(a[0])]=(self.g[reg(a[1])]<<imm(a[2]))&0xffffffff
            elif mn=='mullw':self.g[reg(a[0])]=sx(self.g[reg(a[1])]*self.g[reg(a[2])],32)&MASK
            elif mn=='mulld':self.g[reg(a[0])]=(self.g[reg(a[1])]*self.g[reg(a[2])])&MASK
            elif mn in ('lwz','ld','stw','std','stdu'):
                addr=address(a[1]);n=8 if mn in ('ld','std','stdu') else 4
                if mn in ('lwz','ld'):self.g[reg(a[0])]=self.load(addr,n)
                else:self.store(addr,self.g[reg(a[0])],n)
                if mn=='stdu':self.g[1]=addr
            elif mn in ('cmpwi','cmplw'):
                left=self.g[reg(a[1])]&0xffffffff
                right=(self.g[reg(a[2])]&0xffffffff) if mn=='cmplw' else imm(a[2])
                if mn=='cmpwi':left=sx(left,32)
                self.cr[int(a[0][2:])]=(left>right)-(left<right)
            elif mn in ('beq','bne','bgt'):
                c=self.cr[int(a[0][2:])];take=c==0 if mn=='beq' else c!=0 if mn=='bne' else c>0
                if take:nxt=imm(a[1])
            elif mn=='b':nxt=imm(a[0])
            elif mn=='bl':
                self.lr=pc+4;target=imm(a[0])
                if target>=0x26400 and target in self.code:nxt=target
                else:self.call(target)
            elif mn=='mflr':self.g[reg(a[0])]=self.lr
            elif mn=='mtlr':self.lr=self.g[reg(a[0])]
            elif mn=='blr':self.returned=True;return self.lr
            elif mn!='nop':raise AssertionError((mn,ops))
            pc=nxt
        raise AssertionError('Step bound')

cases=[]
for toc in (0x2e7c0,0x102e7c0,0x4402e7c0):
    for cap in (0,1,99,100,6777,8193,16384,32768):
        for succeeds in (False,True):
            for present in ((False,True) if cap==0 else (True,)):
                c=CPU(toc=toc);c.setup_old(cap,present);oldptr=c.g[3]
                before=c.read(c.oldptr,c.oldbytes) if present else b''
                c.g[4]=(cap+100)*4;c.g[9]=cap;c.g[11]=c.CG;c.g[29]=c.PG
                c.store(c.PG,oldptr,4,True);c.store(c.CG,cap+100,4,True)
                c.allocation_succeeds=succeeds;initial=c.g.copy();cr=c.cr.copy()
                end=c.run(0x16888,{0x1680c,0x1689c})
                # Caller BLR in the helper returns to1688c. Resume real caller.
                if end==0x1688c:end=c.run(end,{0x1680c,0x1689c})
                assert end==(0x1680c if succeeds else 0x1689c)
                assert c.g[1]==initial[1] and c.g[2]==toc
                assert all(c.g[i]==initial[i] for i in range(13,32))
                assert all(c.cr[i]==cr[i] for i in (2,3,4))
                assert c.load(c.PG,4)==(c.newptr if succeeds else oldptr)
                assert c.load(c.CG,4)==(cap+100 if succeeds else cap)
                assert c.freed==(succeeds and present)
                assert sum(x['target']=='0xe714' for x in c.calls)==1
                assert sum(x['target']=='0x21508' for x in c.calls)==int(succeeds and present and cap>0)
                if succeeds and cap>0:assert c.read(c.newptr,cap*4)==before
                if succeeds:assert c.read(c.newptr+cap*4,400)==b'\xa5'*400
                if not succeeds and present:assert c.read(c.oldptr,cap*4)==before
                assert all(0x6fffe000<=a and a+n<=0x70001000 or
                           a in (c.PG,c.CG) and n==4 or
                           succeeds and a==c.newptr and n==cap*4 for a,n in c.writes)
                cases.append({'kind':'grow','toc':hex(toc),'capacity':cap,'old_pointer_present':present,'allocation_succeeds':succeeds})
    for cap,present,request in ((10,False,440),(0x3fffff9c,True,0),(100,True,804)):
        c=CPU(toc=toc);c.setup_old(cap,present);oldptr=c.g[3]
        c.g[4]=request;c.g[9]=cap;c.g[11]=c.CG;c.g[29]=c.PG
        c.store(c.PG,oldptr,4,True);c.store(c.CG,(cap+100)&0xffffffff,4,True)
        end=c.run(0x16888,{0x1680c,0x1689c})
        if end==0x1688c:end=c.run(end,{0x1680c,0x1689c})
        assert end==0x1689c and not c.calls and not c.freed
        assert c.load(c.PG,4)==oldptr and c.load(c.CG,4)==cap
        cases.append({'kind':'invalid-growth-contract','capacity':cap,'present':present,'request':request,'toc':hex(toc)})

rng=random.Random(0x5039)
pairs=[(0,0),(0,0xffffffff),(1,0),(1,60981796),(1,0xffffffff),(0x40000000,4),
       (0xffffffff,0xffffffff),(0x3fffffff,4),(0x10000,0x10000),(6777,4),(8193,8)]
pairs += [(rng.randrange(0,300),rng.randrange(0,64)) for _ in range(96)]
pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(96)]
for n,size in pairs:
    c=CPU();c.g[3]=n|0xabcdef0000000000;c.g[4]=size|0x1234560000000000
    total=n*size;overflow=total>0xffffffff
    c.allocation_succeeds=(not overflow and total<=262144)
    initial=c.g.copy();cr=c.cr.copy();ret=c.run(0xe718)
    assert ret==0x77777700 and c.g[1]==initial[1] and c.g[2]==initial[2]
    assert all(c.g[i]==initial[i] for i in range(13,32)) and all(c.cr[i]==cr[i] for i in (2,3,4))
    alloc=[x for x in c.calls if x['target']=='0xe714']
    assert len(alloc)==int(not overflow)
    if alloc:assert alloc[0]['args'][0]==total
    if overflow or not c.allocation_succeeds:assert c.g[3]==0 and not c.allocated
    else:assert c.g[3]==c.newptr and c.read(c.newptr,total)==bytes(total)
    cases.append({'kind':'calloc','count':n,'element_bytes':size,'overflow':overflow,'allocation_succeeds':c.allocation_succeeds})

regressions=[]
for succeeds in (False,True):
    c=CPU(OLD);c.setup_old(100);c.g[4]=800;c.allocation_succeeds=succeeds
    try:c.run(0xe7a4)
    except MemoryFault as ex:regressions.append({'original_allocation_succeeds':succeeds,'memory_fault_detected':str(ex)})
    else:raise AssertionError('Original null-copy/overread regression not detected')
report={'pass':True,'elf_sha256':M['output_sha256'],'cases':len(cases),'case_details':cases,
 'original_resize_faults_reproduced':regressions,'actual_helper_bytes_interpreted':True,
 'callee_and_allocator_calls_mocked':True,'hardware_execution':False,'native_peak_or_storage_stability_proven':False,
 'limits':'Bounded actual-instruction model of new helpers, real immediate caller and calloc wrapper. No PowerPC hardware, full checker, liblv2 implementation or disk writes executed.'}
with (O/'result.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k not in ('case_details',)}))
