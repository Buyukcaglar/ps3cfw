"""P9 bounded checker-array growth and calloc multiplication guards. Files only."""
import hashlib,json,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
O=R/'analysis/dev006/p9-safety';O.mkdir(exist_ok=False)
P='analysis/dev006/p8-native/libfs_utility_init-p8.elf';old=(R/P).read_bytes()
assert hashlib.sha256(old).hexdigest()=='b7e65e2dd7d82aa5c9957c2af7a192f475ed26f4140f3ab25ea18866bed53f01'
phoff=struct.unpack_from('>Q',old,32)[0];ph=[struct.unpack_from('>IIQQQQQQ',old,phoff+i*56) for i in range(3)]
def off(v):
    h=next(h for h in ph if h[0]==1 and h[3]<=v<h[3]+h[5]);return h[2]+v-h[3]
def d(op,rt,ra,n):return op<<26|rt<<21|ra<<16|(n&65535)
def ds(op,rt,ra,n,xo=0):assert n%4==0;return d(op,rt,ra,n)|xo
def mr(dst,src):return 31<<26|src<<21|dst<<16|src<<11|444<<1
def branch(pc,to,link=0):
    delta=to-pc;assert delta%4==0 and -(1<<25)<=delta<(1<<25)
    return 0x48000000|(delta&0x3fffffc)|link
def clear32(dst,src):return 30<<26|src<<21|dst<<16|32<<6
def slwi(dst,src,n):return 21<<26|src<<21|dst<<16|n<<11|(31-n)<<1
def compare(a,b,unsigned=False):return 31<<26|7<<23|a<<16|b<<11|(32<<1 if unsigned else 0)
class Asm:
    def __init__(self,base):self.base=base;self.words=[];self.labels={};self.fix=[]
    def pc(self):return self.base+4*len(self.words)
    def emit(self,w):self.words.append(w)
    def label(self,n):assert n not in self.labels;self.labels[n]=self.pc()
    def b(self,n):self.fix.append((len(self.words),'b',n));self.emit(0)
    def cond(self,n,kind='eq'):self.fix.append((len(self.words),kind,n));self.emit(0)
    def call(self,to):self.emit(branch(self.pc(),to,1))
    def jump(self,to):self.emit(branch(self.pc(),to))
    def li(self,r,n):
        if -32768<=n<=32767:self.emit(d(14,r,0,n))
        else:self.emit(d(15,r,0,n>>16));self.emit(d(24,r,r,n))
    def finish(self):
        for i,kind,label in self.fix:
            pc=self.base+4*i;to=self.labels[label]
            if kind=='b':self.words[i]=branch(pc,to)
            else:
                delta=to-pc;assert delta%4==0 and -32768<=delta<32768
                self.words[i]={'eq':0x419e0000,'ne':0x409e0000,'gt':0x419d0000}[kind]|(delta&65535)
        return b''.join(struct.pack('>I',w) for w in self.words)

a=Asm(0x26400)
FRAME=0xb0
a.label('grow_array')
a.emit(0x7c0802a6);a.emit(ds(62,1,1,-FRAME,1));a.emit(ds(62,0,1,FRAME+0x10))
for reg,at in ((28,0x80),(29,0x88),(30,0x90),(31,0x98)):a.emit(ds(62,reg,1,at))
# Local call contract at16888: r9=current capacity, r11=capacity global,
# r3=old pointer, r4=(capacity+100)*4. No raw heap-header reads.
a.emit(clear32(31,3));a.emit(clear32(29,4));a.emit(clear32(30,9));a.emit(clear32(28,11))
a.li(9,0x3fffff9b);a.emit(compare(30,9,True));a.cond('grow_fail','gt')
a.emit(d(14,9,30,100));a.emit(slwi(9,9,2));a.emit(compare(9,29,True));a.cond('grow_fail','ne')
a.emit(d(11,28,30,0));a.cond('grow_allocate')
a.emit(d(11,28,31,0));a.cond('grow_fail')
a.label('grow_allocate');a.emit(mr(3,29));a.call(0xe714)
a.emit(d(11,28,3,0));a.cond('grow_fail');a.emit(ds(62,3,1,0x70))
a.emit(d(11,28,31,0));a.cond('grow_success')
a.emit(d(11,28,30,0));a.cond('grow_free_old')
a.emit(mr(4,31));a.emit(slwi(5,30,2));a.call(0x21508);a.emit(ds(58,2,1,0x28))
a.label('grow_free_old');a.emit(mr(3,31));a.call(0xe7a0)
a.label('grow_success');a.emit(ds(58,3,1,0x70));a.b('grow_exit')
a.label('grow_fail');a.emit(d(36,30,28,0));a.li(3,0)
a.label('grow_exit')
for reg,at in ((28,0x80),(29,0x88),(30,0x90),(31,0x98)):a.emit(ds(58,reg,1,at))
a.emit(ds(58,0,1,FRAME+0x10));a.emit(0x7c0803a6);a.emit(d(14,1,1,FRAME));a.emit(0x4e800020)

a.label('store_if_success')
# Preserve CR7 from original16890 cmpwi, and the original failure branch.
a.cond('store_done');a.emit(d(36,3,29,0));a.label('store_done');a.jump(0x16898)

a.label('calloc_product')
a.emit(clear32(9,3));a.emit(clear32(10,4))
a.emit(31<<26|9<<21|9<<16|10<<11|233<<1) # mulld r9,r9,r10
# srdi r10,r9,32 == rldicl r10,r9,32,32
a.emit(30<<26|9<<21|10<<16|32<<6|2)
a.emit(d(11,28,10,0));a.cond('calloc_valid')
a.li(29,0);a.jump(0xe758)
a.label('calloc_valid');a.emit(0x7fa321d6);a.jump(0xe72c)
code=a.finish();end=a.base+len(code)
assert end<=ph[0][5] and not any(old[off(a.base):off(a.base)+len(code)])
rels=old[ph[2][2]:ph[2][2]+ph[2][5]]
for at,z,vi,ai,t,add in (struct.unpack_from('>QHBBIQ',rels,k) for k in range(0,len(rels),24)):
    assert not (ai==0 and a.base<=at<end)
new=bytearray(old);new[off(a.base):off(a.base)+len(code)]=code
hooks=[(0x16888,'4bff7f1d','grow_array',1),(0x16894,'907d0000','store_if_success',0),(0xe728,'7fa321d6','calloc_product',0)]
rows=[]
for va,expected,label,link in hooks:
    at=off(va);assert old[at:at+4].hex()==expected
    new[at:at+4]=struct.pack('>I',branch(va,a.labels[label],link))
    rows.append({'va':hex(va),'before':expected,'after':new[at:at+4].hex(),'target':hex(a.labels[label]),'label':label,'link':bool(link)})
target=O/'libfs_utility_init-p9.elf'
with target.open('xb') as f:f.write(new)
cs=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
with (O/'helpers.txt').open('x',encoding='utf8') as f:
    f.write(''.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}\n' for i in cs.disasm(code,a.base)))
with (O/'manifest.json').open('x',encoding='utf8') as f:
    json.dump({'source':P,'source_sha256':hashlib.sha256(old).hexdigest(),'output_sha256':hashlib.sha256(new).hexdigest(),
      'code_start':hex(a.base),'code_bytes':len(code),'labels':{k:hex(v) for k,v in a.labels.items()},'hooks':rows,
      'program_headers_and_relocations_unchanged':True,'new_module_data_bytes':0,'new_relocations':[],
      'known_resize_caller_replaced':True,'generic_resize_helper_unmodified':True,
      'P8_observer_and_incomplete_flags_unchanged':True,'hardware_tested':False,'stable_support':False},f,indent=2)
print(json.dumps({'code_bytes':len(code),'hooks':rows,'output_sha256':hashlib.sha256(new).hexdigest()}))
