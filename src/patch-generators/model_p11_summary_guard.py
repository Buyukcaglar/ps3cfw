"""Differential actual instructions for P11 flush rejection and setup cleanup."""
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf, ROOT
from p10_partial_setup_cpu import CPU, MASK, signed

BASES = ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000))
DRIVES = (('PNY', 'observations/HW002W/private/native-pny-capture-v1'),
          ('Lexar', 'observations/HW002Z/private/native-lexar-capture-v1'))


def make(elf, bases, patched, raw, write_fd):
    cpu = CPU(elf, bases)
    if patched: cpu.code.update({i.address: i for i in elf.instructions(0x26540, 0x2658c)})
    cpu.invalid_buffer_returns_error = True
    header = cpu.slot(-0x7b88)
    cpu.g[30] = header
    cpu.g[25] = cpu.slot(-0x7430)
    assert cpu.g[25] == cpu.slot(-0x7b38)
    cpu.store(cpu.g[25], write_fd, 4)
    cpu.store(cpu.slot(-0x7ab4), 17, 4)
    cpu.store(header+8, 160, 8)
    cpu.store(header+0x10, 8192, 4)
    cpu.store(header+0x14, 0, 4)
    cpu.store(header+0x1c, 0x06001000, 4)
    cpu.store(header+0x20, 0, 1)
    for n, byte in enumerate(raw): cpu.store(0x06001000+n, byte, 1)
    cpu.store(cpu.g[26], struct.unpack_from('>q', raw, 0x438)[0], 8)
    cpu.store(cpu.slot(-0x7420)+0x20, 0, 1)
    cpu.store(cpu.slot(-0x7b4c)+4, 0, 4)
    cpu.store(cpu.slot(-0x7b4c)+0x10, 0, 4)
    cpu.store(cpu.slot(-0x7b50)+0x20, 0, 1)
    cpu.store(cpu.slot(-0x7b50)+0x1c, 0, 4)
    cpu.cr.update({2: 1, 3: -1, 4: 0})
    return cpu, header


def observation(cpu, header):
    return {'writes': cpu.writes, 'seeks': cpu.seeks, 'messages': cpu.messages,
        'dirty': cpu.load(header+0x20, 1), 'IO_success_flag': cpu.load(cpu.slot(-0x7b2c), 1),
        'modified_flag': cpu.load(cpu.slot(-0x7b00), 4), 'closes': cpu.cleanup_closes,
        'frees': cpu.cleanup_frees, 'result': cpu.g[3]}


def main():
    output = ROOT / 'analysis/dev006/p11-summary-guard-model-v1'
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    try:
        before = PinnedElf('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf',
            'daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688')
        after = PinnedElf('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf',
            '904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e')
        cases = []
        for bases in BASES:
            for drive, folder in DRIVES:
                raw = (ROOT / folder / 'primary-superblock.decoded.bin').read_bytes()
                original_summary = struct.unpack_from('>i', raw, 0x9c)[0]
                for dirty in (0, 1):
                    for primary in (False, True):
                        for present in (False, True):
                            for summary_size in (-1, 0, original_summary):
                                for fd in (-1, 42):
                                    for initial_flag in (0, 1):
                                        observations = []
                                        for patched, elf in ((False, before), (True, after)):
                                            cpu, main_header = make(elf, bases, patched, raw, fd)
                                            header = main_header if primary else 0x06000000
                                            cpu.store(header+8, 160, 8)
                                            cpu.store(header+0x10, 8192, 4)
                                            cpu.store(header+0x14, 0, 4)
                                            cpu.store(header+0x1c, 0x06001000, 4)
                                            cpu.store(header+0x20, dirty, 1)
                                            cpu.store(0x06001000+0x9c, summary_size, 4)
                                            cpu.store(0x06001000+0x34c, 0x06010000 if present else 0, 4)
                                            cpu.store(cpu.slot(-0x7b2c), initial_flag, 1)
                                            cpu.g[3:5] = [fd & MASK, header]
                                            saved = {r:cpu.g[r] for r in (1,2,*range(14,32))}
                                            saved_cr = {r:cpu.cr[r] for r in (2,3,4)}
                                            state = cpu.run(0x1558c)
                                            assert state['returned'] and cpu.lr == 0x76543210
                                            assert all(cpu.g[r] == v for r,v in saved.items())
                                            assert all(cpu.cr[r] == v for r,v in saved_cr.items())
                                            observations.append(observation(cpu, header))
                                        original, corrected = observations
                                        reject = dirty and primary and not present and summary_size > 0 and fd >= 0
                                        if reject:
                                            assert original['writes'] and not corrected['writes'] and not corrected['seeks']
                                            assert corrected['dirty'] == 1 and corrected['IO_success_flag'] == 0
                                            assert corrected['modified_flag'] == 0
                                        else:
                                            assert original == corrected
                                        cases.append({'family':'flush', 'drive':drive,
                                            'bases':[hex(x) for x in bases], 'dirty':dirty, 'primary':primary,
                                            'summary_present':present, 'summary_size':summary_size,
                                            'write_FD':fd, 'initial_IO_flag':initial_flag, 'passed':True,
                                            'rejection_expected':bool(reject),
                                            'P10_write_calls':len(original['writes']), 'P11_write_calls':len(corrected['writes'])})
                # Real ordinary prompt/correction -> first calloc failure -> actual cleanup.
                for fd in (-1, 42):
                    observations = []
                    for patched, elf in ((False,before), (True,after)):
                        cpu, header = make(elf, bases, patched, raw, fd)
                        cpu.fail_at = 0
                        cpu.store(0x06001000+0x3c, 100, 4)
                        cpu.store(0x06001000+0x34c, 0, 4)
                        state = cpu.run(0x1f64c, {0x1f6bc})
                        assert state['returned'] and cpu.g[3] == signed(0x80010004,32)&MASK
                        assert cpu.g[1] == 0x700006b0 and all(cpu.g[r] == v for r,v in cpu.saved.items())
                        assert [a['request'] for a in cpu.setup_allocations] == [original_summary]
                        observations.append(observation(cpu, header))
                    original, corrected = observations
                    if fd < 0:
                        assert original == corrected and not corrected['writes']
                    else:
                        assert original['writes'] and not corrected['writes'] and not corrected['seeks']
                        assert corrected['dirty'] == 1 and corrected['IO_success_flag'] == 0
                        assert original['closes'] == corrected['closes'] == [17,42]
                    cases.append({'family':'actual-dirty-partial-setup', 'drive':drive,
                        'bases':[hex(x) for x in bases], 'write_FD':fd, 'passed':True,
                        'P10_write_calls':len(original['writes']), 'P11_write_calls':len(corrected['writes'])})
                # Retain earlier clean-buffer matrix for all five modeled failure positions.
                for directories in (0,139):
                    for failed in range(5):
                        for fd in (-1,42):
                            observations = []
                            for patched, elf in ((False,before),(True,after)):
                                cpu, header = make(elf,bases,patched,raw,fd)
                                cpu.fail_at = failed
                                cpu.store(0x06001000+0x3f0,directories,8)
                                state = cpu.run(0x1f694,{0x1f6bc})
                                if not state['returned']:
                                    assert state['end'] == 0x1f6bc
                                    state = cpu.run(0x1f798,{0x1f87c})
                                assert state['returned'] and cpu.g[3] == signed(0x80010004,32)&MASK
                                assert cpu.g[1] == 0x700006b0 and all(cpu.g[r] == v for r,v in cpu.saved.items())
                                observations.append(observation(cpu,header))
                            assert observations[0] == observations[1] and not observations[1]['writes']
                            cases.append({'family':'clean-partial-setup','drive':drive,
                                'bases':[hex(x) for x in bases], 'directories':directories,
                                'failed_allocation':failed,'write_FD':fd,'passed':True})
        result = {'pass':True,'case_count':len(cases),'cases':cases,'elf_sha256':after.sha256,
            'parent_elf_sha256':before.sha256,
            'null_summary_rejected_before_superblock_and_summary_write_calls':True,
            'dirty_byte_preserved_and_existing_IO_success_flag_cleared':True,
            'ordinary_nonreject_flush_and_clean_setup_paths_differentially_identical':True,
            'GPR_nonvolatile_TOC_stack_LR_and_modeled_CR2_4_preserved':True,
            'allocator_kernel_IO_descriptor_close_free_and_format_strcmp_are_mocks':True,
            'summary_reads_later_setup_nonempty_queue_native_teardown_and_whole_error_propagation_not_proven':True,
            'hardware_execution_or_fault_injection':False,'stable_support':False}
        with (output/'result.json').open('x',encoding='utf8') as stream:
            json.dump(result,stream,indent=2);stream.write('\n')
        print(json.dumps({'P11_instruction_model_passed':True,'cases':len(cases),'hardware_IO':False}))
    except BaseException as error:
        with (output/'failure.json').open('x',encoding='utf8') as stream:
            json.dump({'passed':False,'error':repr(error),'hardware_IO':False},stream,indent=2)
        raise


if __name__=='__main__':main()
