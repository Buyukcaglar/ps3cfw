"""P12/P13 actual-instruction differential reader/setup cases, all kernel I/O mocked."""
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf, ROOT
from p12_read_seek_cpu import CPU as ReadCPU, verify_return, observe
from model_p12_setup_abort import make, observe as setup_observe, BASES, DRIVES, Abort


class CPU(ReadCPU):
    def __init__(self, elf, bases, patched):
        super().__init__(elf, bases, ((0x26640, 0x26670),) if patched else ())
        self.events = []

    def external(self, address):
        if address in (0xf7e8, 0xf5d8, 0x10b74):
            self.events.append({'callee': hex(address), 'seek_index': len(self.seeks),
                                'read_index': len(self.reads)})
        super().external(address)


def run_reader(elf, bases, patched, count, bulk, failed_seek=None, error=-1, sector_kind='full', sector_index=0):
    cpu = CPU(elf, bases, patched)
    buffer = 0x06010000
    cpu.g[3:7] = [17, buffer, 37, count]
    cpu.store(cpu.slot(-0x7adc), 512, 4)
    cpu.memory.update(dict.fromkeys(range(buffer, buffer + max(count, 1)), 0x5a))
    cpu.cr.update({2: 1, 3: -1, 4: 0})
    saved = {'stack': cpu.g[1], 'toc': cpu.g[2], 'lr': cpu.lr,
             'nonvolatile': cpu.g[14:].copy(), 'cr2_4': [cpu.cr[r] for r in (2, 3, 4)]}
    cpu.bulk_result = bulk
    cpu.failed_seek_indices = set() if failed_seek is None else {failed_seek}
    cpu.seek_error = error
    if sector_kind == 'negative':
        cpu.failed_sector_indices = {sector_index}
    elif sector_kind == 'short':
        cpu.short_sector_indices = {sector_index}
    result = cpu.run(0x14aec)
    assert result['returned']
    verify_return(cpu, saved)
    return cpu, observe(cpu, buffer, count)


def main():
    output = ROOT / 'analysis/dev006/p13-read-seek-model-v3'
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    try:
        parent = PinnedElf('analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf',
                           '82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85')
        candidate = PinnedElf('analysis/dev006/p13-read-seek-v1/libfs_utility_init-p13.elf',
                              'e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86')
        rows = []
        for bases in BASES:
            for count in (0, 512, 1024, 16384):
                scenarios = [('full', None, 'full', 0), ('bulk-negative', -1, 'full', 0),
                             ('bulk-short', max(0, count - 1), 'full', 0)]
                if count:
                    for at in (0, count // 512 - 1):
                        for kind in ('negative', 'short'):
                            scenarios.append((f'sector-{at}-{kind}', -1, kind, at))
                for name, bulk, kind, at in scenarios:
                    old_cpu, old = run_reader(parent, bases, False, count, bulk, sector_kind=kind, sector_index=at)
                    new_cpu, new = run_reader(candidate, bases, True, count, bulk, sector_kind=kind, sector_index=at)
                    assert old == new and old_cpu.events == new_cpu.events
                    assert not new_cpu.writes
                    rows.append({'family': 'reader-successful-seeks-differential', 'count': count,
                                 'scenario': name, 'bases': [hex(x) for x in bases], 'passed': True})
                for error in (-1, -2147418110):
                    failure_cases = [('initial-seek', 0, bulk, 'full', 0) for bulk in (None, -1, max(0, count - 1))]
                    failure_cases += [('retry-seek', 1, bulk, 'full', 0) for bulk in ((-1, max(0, count - 1)) if count else (-1,))]
                    if count:
                        for at in (0, count // 512 - 1):
                            for kind in ('negative', 'short'):
                                failure_cases.append(('sector-reseek', 2, -1, kind, at))
                    for family, failed_seek, bulk, kind, failed_sector in failure_cases:
                        cpu, result = run_reader(candidate, bases, True, count, bulk, failed_seek, error, kind, failed_sector)
                        assert result['result'] == 1 and result['IO_flag'] == 0 and not cpu.writes
                        assert len(cpu.seeks) == failed_seek + 1 and cpu.seeks[-1]['result'] == error
                        assert cpu.events[-1]['callee'] == '0xf7e8'
                        assert cpu.events[-1]['seek_index'] == failed_seek
                        if failed_seek == 0:
                            assert not cpu.reads and not cpu.memsets
                            assert result['buffer'] == '5a' * count
                        rows.append({'family': family, 'count': count, 'failed_seek': failed_seek,
                                     'bulk_result': bulk, 'sector_result_kind': kind, 'failed_sector': failed_sector, 'error': error,
                                     'bases': [hex(x) for x in bases], 'passed': True,
                                     'no_read_or_seek_after_failed_seek': True})
            # Existing P12 setup/OOM/summary-read-error behavior must stay exact.
            for drive, folder in DRIVES:
                raw = (ROOT / folder / 'primary-superblock.decoded.bin').read_bytes()
                size = struct.unpack_from('>i', raw, 0x9c)[0]
                block = struct.unpack_from('>i', raw, 0x30)[0]
                scenarios = []
                for dirty in (0, 1):
                    for fd in (-1, 42):
                        for directories in (0, 139):
                            for failure in (*range(5), None):
                                scenarios.append(('setup-success' if failure is None else 'setup-OOM', dirty, fd, directories, failure, None))
                        for read_failure in (0, (size - 1) // block):
                            scenarios.append(('summary-read-failure', dirty, fd, 139, 1, read_failure))
                for family, dirty, fd, directories, failure, read_failure in scenarios:
                    states = []
                    for patched, elf in ((False, parent), (True, candidate)):
                        cpu, head = make(elf, bases, True, raw, fd, dirty, directories, failure, read_failure)
                        if patched:
                            cpu.code.update({i.address: i for i in elf.instructions(0x26640, 0x26670)})
                        aborted = False
                        try:
                            result = cpu.run(0x1f694, {0x1f87c})
                        except Abort as error:
                            assert str(error) == 'Modeled nonlocal exit 8'
                            aborted = True
                            result = {'aborted8': True}
                        state = setup_observe(cpu, head)
                        state['exit'] = {key: value for key, value in result.items() if key != 'steps'}
                        state['stack'] = cpu.g[1]
                        state['CR2_4'] = [cpu.cr[r] for r in (2, 3, 4)]
                        if family == 'summary-read-failure':
                            assert aborted and not cpu.writes and len(cpu.setup_allocations) == 1
                        elif family == 'setup-success':
                            assert result['end'] == 0x1f87c
                        else:
                            assert result['returned'] and not cpu.writes
                            assert all(cpu.g[r] == value for r, value in cpu.saved.items())
                        states.append(state)
                    assert states[0] == states[1]
                    rows.append({'family': 'P12-regression-' + family, 'drive': drive,
                                 'bases': [hex(x) for x in bases], 'dirty': dirty, 'fd': fd,
                                 'directories': directories, 'failed_alloc': failure,
                                 'failed_read_block': read_failure, 'passed': True})
        families = {name: sum(row['family'] == name for row in rows) for name in sorted({r['family'] for r in rows})}
        with (output / 'result.json').open('x', encoding='utf8') as stream:
            json.dump({'pass': True, 'case_count': len(rows), 'families': families, 'cases': rows,
                       'elf_sha256': candidate.sha256, 'parent_elf_sha256': parent.sha256,
                       'successful_seek_reader_observations_and_P12_setup_differentially_identical': True,
                       'negative_seek_return_stops_reads_and_reseeks_and_returns_nonzero_IO_failure': True,
                       'nonvolatile_GPR_stack_TOC_LR_and_modeled_CR2_4_checked_on_reader_returns': True,
                       'kernel_IO_allocator_free_close_memset_warning_prompt_nonlocal_exit_are_mocks': True,
                       'ordinary_unmounted_yes_mode_only': True,
                       'complete_call_graph_native_unwind_full_IO_policies_or_real_fault_not_proven': True,
                       'native_hardware_fault_injection_or_execution': False, 'stable_support': False}, stream, indent=2)
            stream.write('\n')
        print(json.dumps({'P13_instruction_model_passed': True, 'cases': len(rows), 'families': families,
                          'hardware_IO': False}))
    except BaseException as error:
        with (output / 'failure.json').open('x', encoding='utf8') as stream:
            json.dump({'pass': False, 'error': repr(error), 'hardware_IO': False,
                       'context': {k: repr(v) for k, v in locals().items() if k in ('bases', 'count', 'family', 'failed_seek', 'bulk', 'kind', 'failed_sector')}}, stream, indent=2)
        raise


if __name__ == '__main__':
    main()
