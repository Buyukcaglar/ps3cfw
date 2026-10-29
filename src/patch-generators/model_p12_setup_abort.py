"""Actual P11/P12 setup/read-failure/cleanup differential model; all kernel I/O fake."""
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf,ROOT
from p11_summary_read_cpu import CPU as ParentCPU,Abort,MASK,signed

BASES=((0x1000000,0x2000000),(0x23000000,0x45000000),(0x50000000,0x12000000))
DRIVES=(('PNY','observations/HW002W/private/native-pny-capture-v1'),
        ('Lexar','observations/HW002Z/private/native-lexar-capture-v1'))


class CPU(ParentCPU):
    def __init__(self,elf,bases,patched):
        super().__init__(elf,bases)
        if patched:self.code.update({i.address:i for i in elf.instructions(0x265c0,0x26600)})

    def external(self,address):
        # Same explicit read/memset mocks, with bounded byte-dictionary updates.
        if address in (0xf5d8,0x10b74):
            pointer,count=self.g[4],self.g[5];self.access(pointer,count)
            if address==0xf5d8:
                failed=self.read_block_index==self.fail_read_block;self.read_block_index+=1
                if failed:self.failed_sector_pointer=pointer
            else:failed=pointer==self.failed_sector_pointer
            result=-1 if failed else count
            if not failed:self.memory.update(dict.fromkeys(range(pointer,pointer+count),0xa5))
            self.reads.append({'callee':hex(address),'pointer':pointer,'count':count,
                'result':result,'byte_offset':self.cursor})
            if result>0:self.cursor+=result
            self.clobber(result)
        elif address==0x214e8:
            pointer,value,count=self.g[3],self.g[4]&255,self.g[5];self.access(pointer,count)
            self.memory.update(dict.fromkeys(range(pointer,pointer+count),value))
            self.memsets.append({'pointer':pointer,'value':value,'count':count})
            self.store(self.g[1]+0x28,self.g[2],8);self.clobber(pointer)
        else:super().external(address)


def make(elf,bases,patched,raw,fd,dirty,directories,failed,read_failure=None):
    cpu=CPU(elf,bases,patched);cpu.fail_at=failed;cpu.fail_read_block=read_failure
    head=cpu.slot(-0x7b88);cpu.g[30]=head
    cpu.g[25]=cpu.slot(-0x7430);cpu.g[27]=cpu.slot(-0x7418)
    assert cpu.g[25]==cpu.slot(-0x7b38) and cpu.g[27]==cpu.slot(-0x7ab4)
    cpu.store(cpu.g[25],fd,4);cpu.store(cpu.g[27],17,4);cpu.store(cpu.slot(-0x7adc),512,4)
    cpu.store(head+8,160,8);cpu.store(head+0x10,8192,4);cpu.store(head+0x14,0,4)
    cpu.store(head+0x1c,0x06001000,4);cpu.store(head+0x20,dirty,1)
    cpu.memory.update({0x06001000+n:byte for n,byte in enumerate(raw)})
    cpu.store(0x06001000+0x34c,0,4);cpu.store(0x06001000+0x3f0,directories,8)
    cpu.store(cpu.g[26],struct.unpack_from('>q',raw,0x438)[0],8)
    cpu.store(cpu.slot(-0x7420)+0x20,0,1)
    cpu.store(cpu.slot(-0x7b4c)+4,0,4);cpu.store(cpu.slot(-0x7b4c)+0x10,0,4)
    cpu.store(cpu.slot(-0x7b50)+0x20,0,1);cpu.store(cpu.slot(-0x7b50)+0x1c,0,4)
    cpu.cr.update({2:1,3:-1,4:0})
    return cpu,head


def observe(cpu,head):
    return {'writes':cpu.writes,'seeks':cpu.seeks,'reads':cpu.reads,'allocs':cpu.setup_allocations,
        'closes':cpu.cleanup_closes,'frees':cpu.cleanup_frees,'result':cpu.g[3],
        'dirty':cpu.load(head+0x20,1),'aux_dirty':cpu.load(cpu.slot(-0x7b50)+0x20,1),
        'IO_flag':cpu.load(cpu.slot(-0x7b2c),1)}


def main():
    output=ROOT/'analysis/dev006/p12-setup-abort-model-v1';output.mkdir(exist_ok=False)
    (output/'source.py').write_bytes(Path(__file__).read_bytes())
    try:
        parent=PinnedElf('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf',
            '904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e')
        candidate=PinnedElf('analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf',
            '82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85')
        rows=[]
        for bases in BASES:
            for drive,folder in DRIVES:
                raw=(ROOT/folder/'primary-superblock.decoded.bin').read_bytes()
                size=struct.unpack_from('>i',raw,0x9c)[0];block=struct.unpack_from('>i',raw,0x30)[0]
                for dirty in (0,1):
                    for fd in (-1,42):
                        for directories in (0,139):
                            for failed in range(5):
                                states=[]
                                for patched,elf in ((False,parent),(True,candidate)):
                                    cpu,head=make(elf,bases,patched,raw,fd,dirty,directories,failed)
                                    result=cpu.run(0x1f694,{0x1f87c})
                                    assert result['returned'] and cpu.g[3]==signed(0x80010004,32)&MASK
                                    assert cpu.g[1]==0x700006b0 and all(cpu.g[r]==v for r,v in cpu.saved.items())
                                    assert [cpu.cr[r] for r in (2,3,4)]==[1,-1,0]
                                    states.append(observe(cpu,head))
                                old,new=states
                                assert old['reads']==new['reads'] and old['allocs']==new['allocs']
                                assert old['closes']==new['closes']==([17] if fd<0 else [17,42])
                                assert old['frees']==new['frees']
                                assert not new['writes'] and new['dirty']==new['aux_dirty']==new['IO_flag']==0
                                rows.append({'family':'setup-OOM','drive':drive,'bases':[hex(x) for x in bases],
                                    'dirty':dirty,'write_FD':fd,'directories':directories,'failed_allocation':failed,
                                    'passed':True,'P11_write_calls':len(old['writes']),'P12_write_calls':0})
                            # Successful summary reads/all allocations reach original buffer initialization unchanged.
                            states=[]
                            for patched,elf in ((False,parent),(True,candidate)):
                                cpu,head=make(elf,bases,patched,raw,fd,dirty,directories,None)
                                result=cpu.run(0x1f694,{0x1f87c})
                                assert not result['returned'] and result['end']==0x1f87c
                                states.append(observe(cpu,head))
                            assert states[0]==states[1] and not states[1]['writes']
                            rows.append({'family':'setup-success','drive':drive,'bases':[hex(x) for x in bases],
                                'dirty':dirty,'write_FD':fd,'directories':directories,'passed':True})
                        for failed_block in (0,(size-1)//block):
                            states=[]
                            for patched,elf in ((False,parent),(True,candidate)):
                                cpu,head=make(elf,bases,patched,raw,fd,dirty,139,1,failed_block)
                                aborted=False
                                try:result=cpu.run(0x1f694,{0x1f87c})
                                except Abort as error:
                                    aborted=True
                                    assert str(error)=='Modeled nonlocal exit 8'
                                state=observe(cpu,head);state['aborted8']=aborted
                                state['continued_prompt']='0x1f76c' in cpu.trace
                                if patched:
                                    assert aborted and not state['continued_prompt']
                                    assert len(cpu.setup_allocations)==1 and cpu.read_block_index==failed_block+1
                                    assert not cpu.writes and state['dirty']==state['aux_dirty']==state['IO_flag']==0
                                    assert cpu.cleanup_closes==([17] if fd<0 else [17,42])
                                    assert cpu.g[1]==0x70000000 and [cpu.cr[r] for r in (2,3,4)]==[1,-1,0]
                                states.append(state)
                            old,new=states
                            if fd>=0 and dirty:
                                assert old['writes'] and old['continued_prompt'] and not old['aborted8']
                            rows.append({'family':'summary-read-failure','drive':drive,'bases':[hex(x) for x in bases],
                                'dirty':dirty,'write_FD':fd,'failed_read_block':failed_block,'passed':True,
                                'P11_write_calls':len(old['writes']),'P12_write_calls':0,
                                'P12_original_exit8_route':True,'P12_later_allocations':len(new['allocs'])-1})
        result={'pass':True,'case_count':len(rows),'cases':rows,'elf_sha256':candidate.sha256,
            'parent_elf_sha256':parent.sha256,'all_summary_read_errors_abort_before_CONTINUE_or_bitmap_allocation':True,
            'setup_failure_cleanup_has_zero_mock_writes_under_empty_queue_preconditions':True,
            'successful_summary_reads_and_all_setup_allocations_differentially_unchanged':True,
            'original_OOM_status_and_cleanup_descriptor_free_routes_preserved':True,
            'kernel_IO_alloc_free_close_memset_format_strcmp_nonlocal_exit_are_mocks':True,
            'GPR_nonvolatile_stack_TOC_LR_and_modeled_CR2_4_checked_on_setup_returns':True,
            'native_nonlocal_unwinding_bulk_teardown_and_all_other_error_paths_not_proven':True,
            'native_hardware_fault_injection_or_execution':False,'stable_support':False}
        with (output/'result.json').open('x',encoding='utf8') as stream:
            json.dump(result,stream,indent=2);stream.write('\n')
        print(json.dumps({'P12_instruction_model_passed':True,'cases':len(rows),'hardware_IO':False}))
    except BaseException as error:
        with (output/'failure.json').open('x',encoding='utf8') as stream:
            json.dump({'passed':False,'error':repr(error),'hardware_IO':False},stream,indent=2)
        raise


if __name__=='__main__':main()
