"""Actual saved instructions with explicit external-call mocks; no native execution."""
import itertools, json
from pinned_binary import PinnedElf, ROOT

O=ROOT/'analysis/dev006/p13-offline-finalization-v1/cleanup-model-v1'
MASK=(1<<64)-1
def signed(v,bits=32):
    v &= (1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

class CPU:
    def __init__(self, elf, spans, hook):
        self.code={i.address:i for lo,hi in spans for i in elf.instructions(lo,hi)}
        self.g=[0x4400000000000000+i for i in range(32)]
        self.g[1]=0x70000000;self.g[2]=0x5001c620
        self.lr=0x60001000;self.mem={};self.cr={};self.trace=[];self.calls=[];self.hook=hook
        self.regions=[(0x6ffff000,0x70001000),(0x10890000,0x10892000),
                      (0x60000000,0x60002000),(0x50014000,0x5001d000),(0x15f000,0x160000)]
    def access(self,a,n):
        assert any(lo<=a and a+n<=hi for lo,hi in self.regions),hex(a)
    def load(self,a,n):
        self.access(a,n);return int.from_bytes(bytes(self.mem.get(a+j,0) for j in range(n)),'big')
    def store(self,a,v,n):
        self.access(a,n)
        for j,b in enumerate((v&((1<<(8*n))-1)).to_bytes(n,'big')):self.mem[a+j]=b
    def result(self,v):
        for j in (0,*range(3,13)):self.g[j]=0xabcdef0000000000+j
        self.g[3]=v&MASK
    def run(self,pc,limit=350):
        for step in range(limit):
            i=self.code[pc];self.trace.append(hex(pc));mn=i.mnemonic.rstrip('+-');a=i.op_str.split(', ') if i.op_str else [];nxt=pc+4
            def r(t):return int(t[1:])
            def num(t):return int(t,0)
            def ea(t):
                d,b=t[:-1].split('(');return (self.g[r(b)]+num(d))&MASK
            if mn=='blr':return self.g[3]
            if mn=='mr':self.g[r(a[0])]=self.g[r(a[1])]
            elif mn=='mflr':self.g[r(a[0])]=self.lr
            elif mn=='mtlr':self.lr=self.g[r(a[0])]
            elif mn in ('li','lis'):self.g[r(a[0])]=(num(a[1])<<(16 if mn=='lis' else 0))&MASK
            elif mn in ('addi','addis'):self.g[r(a[0])]=(self.g[r(a[1])]+(num(a[2])<<(16 if mn=='addis' else 0)))&MASK
            elif mn=='clrldi':self.g[r(a[0])]=self.g[r(a[1])]&((1<<(64-num(a[2])))-1)
            elif mn=='extsw':self.g[r(a[0])]=signed(self.g[r(a[1])])&MASK
            elif mn in ('lwz','ld','stw','std','stdu'):
                at=ea(a[1]);width=4 if mn in ('lwz','stw') else 8
                if mn in ('lwz','ld'):self.g[r(a[0])]=self.load(at,width)
                else:
                    self.store(at,self.g[r(a[0])],width)
                    if mn=='stdu':self.g[r(a[1][a[1].index('(')+1:-1])]=at
            elif mn in ('cmpwi','cmpw'):
                field,left,right=a if len(a)==3 else ('cr0',*a)
                lv=signed(self.g[r(left)]);rv=num(right) if mn=='cmpwi' else signed(self.g[r(right)])
                self.cr[field]=(lv>rv)-(lv<rv)
            elif mn in ('beq','bne','blt','bge'):
                field,to=a if len(a)==2 else ('cr0',a[0]);v=self.cr[field]
                if {'beq':v==0,'bne':v!=0,'blt':v<0,'bge':v>=0}[mn]:nxt=num(to)
            elif mn=='b':nxt=num(a[0])
            elif mn=='bl':
                target=num(a[0]);self.lr=pc+4
                self.calls.append({'pc':hex(pc),'target':hex(target),'args':self.g[3:9].copy()})
                self.hook(self,target)
            elif mn=='sc':
                self.calls.append({'pc':hex(pc),'syscall':self.g[11],'args':self.g[3:9].copy()})
                self.hook(self,'sc')
            elif mn!='nop':raise AssertionError((hex(pc),mn,a))
            pc=nxt
        raise AssertionError('Bounded instruction model exceeded step limit')

def verify_frame(c,sp,lr,nonvolatile):
    assert c.g[1]==sp and c.lr==lr
    assert c.g[14:]==nonvolatile

def main():
    O.mkdir(exist_ok=False)
    lib=PinnedElf('analysis/checker-audit/liblv2.elf','aac69540830b4a6673b93331bf52266f360551a2732adcbb3c7a808daddf09c5')
    caller=PinnedElf('analysis/dev006/caller-prototype/sysconf-patched.elf','4e2cec9db3f1a50d99adadb62c8bf0f499aea65dea6fea6af29918f32e1d3e4e')
    util=PinnedElf('analysis/build-p13-first/candidate.native.elf','e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86')
    native=[];outer=[];wrappers=[]
    # This model deliberately injects status returns. It does not assert they
    # are reachable with a valid, already initialized heap on actual firmware.
    for flags,init,lock,destroy,raw,unlock,freerc in itertools.product(
            (0x80150000,0x00150000),(0,-12),(0,-7),(0,-8),(0,-9),(0,-10),(0,-11)):
        def hook(c,t):
            if t==0x7974:c.run(t)  # actual ownership/backing getter
            elif t==0x6fe0:c.result(init)
            elif t==0x7ac4:c.result(0x108901c8) # valid mutex accessor, external to this model
            elif t==0x562c:c.result(lock)
            elif t==0x51b8:c.result(destroy)
            elif t==0x7fb4:c.result(raw) # raw delete assumed returned
            elif t==0x512c:c.result(unlock)
            elif t=='sc':assert c.g[11]==349;c.result(freerc)
            else:raise AssertionError(t)
        c=CPU(lib,[(0x784c,0x7944),(0x7974,0x7990)],hook)
        c.g[3]=0x10890010
        c.store(c.g[2]-0x7ebc,0x60000100,4);c.store(c.g[2]-0x7ec4,0x60000200,4);c.store(0x60000200,18,4)
        c.store(c.g[3]+0x1d0,flags,4);c.store(c.g[3]+0x10,0x10890000,4)
        sp,lr,nv=c.g[1],c.lr,c.g[14:].copy();rc=signed(c.run(0x784c));verify_frame(c,sp,lr,nv)
        frees=sum(x.get('syscall')==349 for x in c.calls)
        unlocks=sum(x.get('target')=='0x512c' for x in c.calls)
        assert rc==(init if init<0 else 0)
        assert frees==int(init==0 and not flags&0x80000000)
        assert unlocks==int(init==0)
        assert c.load(0x60000200,4)==(18 if init<0 else 17)
        native.append({'flags':hex(flags),'init_return':init,'lock_return':lock,'destroy_return':destroy,
            'raw_delete_return':raw,'unlock_return':unlock,'owned_free_return':freerc,'returned':rc,
            'backing_free_calls':frees,'global_unlock_calls':unlocks,'trace':c.trace,'calls':c.calls})
    for alloc,outptr,utility,free in itertools.product((0,-12),(0,0x10890000),(0,1,-5),(0,-11)):
        seen={}
        def hook(c,t):
            if t==0x12cd50:assert c.g[3]==1;c.result(0x44332211)
            elif t==0x1d4d4:
                assert c.g[3:6]==[134217728,0x44332211,0x200]
                c.store(c.g[6],outptr,4);c.result(alloc)
            elif t==0x12f868:
                assert c.g[3]==3 and c.g[5]==outptr and c.g[6]==134217728
                seen['utility']=True;c.result(utility)
            elif t=='sc':assert c.g[11]==349 and c.g[3]==outptr;c.result(free)
            elif t==0x12f718:seen['exit_status']=signed(c.g[3]);c.result(0)
            else:raise AssertionError(t)
        c=CPU(caller,[(0x30058,0x30110)],hook)
        sp,lr,nv=c.g[1],c.lr,c.g[14:].copy();c.run(0x30058);verify_frame(c,sp,lr,nv)
        success=alloc==0 and outptr!=0
        assert seen.get('utility',False)==success
        assert sum(x.get('syscall')==349 for x in c.calls)==int(success)
        expected=alloc if alloc else utility if outptr else -1
        assert seen['exit_status']==expected
        outer.append({'allocation_return':alloc,'out_pointer':outptr,'utility_return':utility,
            'backing_free_return':free,'utility_called':success,'thread_exit_status':seen['exit_status'],
            'free_return_propagated':False,'trace':c.trace,'calls':c.calls})
    for delete_rc in (0,-12,-33):
        def hook(c,t):
            assert t in (0xe818,0xf9d8,0xe9b4)
            c.result(delete_rc)
        c=CPU(util,[(0xfa38,0xfa64)],hook)
        sp,lr,nv=c.g[1],c.lr,c.g[14:].copy();ret=c.run(0xfa38);verify_frame(c,sp,lr,nv);assert ret==0
        wrappers.append({'route':'top-level-fa38','injected_cleanup_return':delete_rc,'return':ret,'calls':c.calls,'trace':c.trace})
        def hook2(c,t):assert t==0x26020;c.result(delete_rc)
        c=CPU(util,[(0xe9b4,0xe9fc)],hook2)
        c.g[2]=0x317c0;c.regions.append((0x29a08,0x29a10))
        c.store(0x29a08,0x60000400,4);c.store(0x60000400,0x10890010,4)
        c.store(c.g[1]+0x28,c.g[2],8)
        sp,lr,nv=c.g[1],c.lr,c.g[14:].copy();ret=signed(c.run(0xe9b4));verify_frame(c,sp,lr,nv)
        assert ret==delete_rc and c.load(0x60000400,4)==0
        wrappers.append({'route':'heap-delete-wrapper-e9b4','injected_native_delete_return':delete_rc,'return':ret,
            'global_handle_cleared_even_on_failure':True,'calls':c.calls,'trace':c.trace})
    report={'passed':True,'native_delete_cases':native,'outer_caller_cases':outer,'utility_teardown_cases':wrappers,
        'counts':{'native_delete':len(native),'outer_caller':len(outer),'utility_teardown':len(wrappers)},
        'scope':'Saved exact instruction execution with explicit status mocks, bounded memory and volatile clobbers; not hardware or complete fsck',
        'confirmed_status_channels':{'native_normal_delete_masks_destroy_raw_delete_unlock_owned_free_status':True,
            'utility_delete_wrapper_clears_handle_after_return_even_if_error':True,
            'utility_top_teardown_returns_zero':True,'outer_caller_preserves_utility_status_and_ignores_backing_free_status':True},
        'conditional_only':'Native initialization-error path skips unlock in these instructions. Reachability after a successful create/already-initialized runtime is not established; no new hardware deadlock or P13 regression claimed.',
        'no_OS_device_or_firmware_execution':True}
    with (O/'result.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'passed':True,**report['counts'],'hardware_test':False}),flush=True)

if __name__=='__main__':main()
