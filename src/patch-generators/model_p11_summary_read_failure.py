"""Actual correction/read/fallback/continue/bitmap-OOM/cleanup with fake kernel I/O."""
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf,ROOT
from p11_summary_read_cpu import CPU,MASK,signed


def main():
    output=ROOT/'analysis/dev006/p11-summary-read-failure-model-v1';output.mkdir(exist_ok=False)
    (output/'source.py').write_bytes(Path(__file__).read_bytes())
    (output/'CPU.py').write_bytes((ROOT/'analysis/dev006/p11_summary_read_cpu.py').read_bytes())
    try:
        elf=PinnedElf('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf',
            '904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e')
        rows=[]
        for bases in ((0x1000000,0x2000000),(0x23000000,0x45000000),(0x50000000,0x12000000)):
            for drive,folder in (('PNY','observations/HW002W/private/native-pny-capture-v1'),
                                 ('Lexar','observations/HW002Z/private/native-lexar-capture-v1')):
                raw=(ROOT/folder/'primary-superblock.decoded.bin').read_bytes()
                summary=struct.unpack_from('>i',raw,0x9c)[0]
                block=struct.unpack_from('>i',raw,0x30)[0]
                for failed_block in (0,(summary-1)//block):
                    cpu=CPU(elf,bases);cpu.fail_at=1;cpu.fail_read_block=failed_block
                    head=cpu.slot(-0x7b88);cpu.g[30]=head
                    cpu.g[25]=cpu.slot(-0x7430);cpu.g[27]=cpu.slot(-0x7418)
                    assert cpu.g[25]==cpu.slot(-0x7b38) and cpu.g[27]==cpu.slot(-0x7ab4)
                    cpu.store(cpu.g[25],42,4);cpu.store(cpu.g[27],17,4)
                    cpu.store(cpu.slot(-0x7adc),512,4)
                    cpu.store(head+8,160,8);cpu.store(head+0x10,8192,4)
                    cpu.store(head+0x14,0,4);cpu.store(head+0x1c,0x06001000,4);cpu.store(head+0x20,0,1)
                    for n,byte in enumerate(raw):cpu.store(0x06001000+n,byte,1)
                    cpu.store(0x06001000+0x3c,100,4);cpu.store(0x06001000+0x34c,0,4)
                    cpu.store(cpu.g[26],struct.unpack_from('>q',raw,0x438)[0],8)
                    cpu.store(cpu.slot(-0x7420)+0x20,0,1)
                    cpu.store(cpu.slot(-0x7b4c)+4,0,4);cpu.store(cpu.slot(-0x7b4c)+0x10,0,4)
                    cpu.store(cpu.slot(-0x7b50)+0x20,0,1);cpu.store(cpu.slot(-0x7b50)+0x1c,0,4)
                    state=cpu.run(0x1f64c,{0x1f87c})
                    assert state['returned'] and cpu.g[3]==signed(0x80010004,32)&MASK
                    assert cpu.g[1]==0x700006b0 and all(cpu.g[r]==v for r,v in cpu.saved.items())
                    assert '0x1f744' in cpu.trace and '0x1f76c' in cpu.trace
                    assert len(cpu.setup_allocations)==2 and cpu.setup_allocations[1]['result']==0
                    assert cpu.writes and all(w['buffer_valid'] for w in cpu.writes)
                    assert cpu.writes[0]['count']==8192 and cpu.writes[0]['byte_offset']==81920
                    pointer=cpu.setup_allocations[0]['result']
                    bad_offset=failed_block*block
                    bad_sector=bytes(cpu.load(pointer+bad_offset+n,1) for n in range(512))
                    assert bad_sector==bytes(512)
                    assert cpu.load(pointer+(512 if failed_block==0 else 0),1)==0xa5
                    assert sum(w['count'] for w in cpu.writes[1:])==summary
                    rows.append({'drive':drive,'bases':[hex(x) for x in bases],
                        'failed_read_block':failed_block,'summary_bytes':summary,
                        'returned_original_OOM_status':True,'actual_CONTINUE_prompt_reached':True,
                        'mocked_read_calls':len(cpu.reads),'mocked_write_calls':len(cpu.writes),
                        'summary_bytes_presented_to_mock_writes':sum(w['count'] for w in cpu.writes[1:]),
                        'failed_sector_remains_zero_and_is_in_flushed_summary':True,
                        'before_delete_IO_flag':cpu.load(cpu.slot(-0x7b2c),1),
                        'dirty_at_return':cpu.load(head+0x20,1),'hardware_IO':False})
        with (output/'result.json').open('x',encoding='utf8') as stream:
            json.dump({'passed':True,'case_count':len(rows),'cases':rows,
                'finding':'Nonnull partially read summary can be flushed after CONTINUE plus later bitmap allocation failure',
                'actual_warning_prompt_read_fallback_and_cleanup_instructions_executed':True,
                'kernel_reads_memset_alloc_free_close_format_strcmp_are_mocks':True,
                'valid_geometry_empty_queue_clean_alternate_and_successful_mock_seeks_preconditions':True,
                'hardware_corruption_or_fault_injection':False,'whole_read_failure_handling_proven':False},stream,indent=2)
            stream.write('\n')
        print(json.dumps({'partial_summary_failure_cases':len(rows),'nonnull_partial_summary_write_reproduced':True,'hardware_IO':False}))
    except BaseException as error:
        with (output/'failure.json').open('x',encoding='utf8') as stream:
            json.dump({'passed':False,'error':repr(error),'hardware_IO':False},stream,indent=2)
        raise


if __name__=='__main__':main()
