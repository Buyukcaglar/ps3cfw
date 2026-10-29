"""Demonstrate conditional negative-seek/stale-read continuation in P12, offline."""
import hashlib
import json
from pathlib import Path
from pinned_binary import PinnedElf, ROOT
from p12_read_seek_cpu import reader, verify_return, observe


def main():
    output = ROOT / 'analysis/dev006/p12-read-seek-failure-v1'
    output.mkdir(exist_ok=False)
    for source in (Path(__file__), ROOT / 'analysis/dev006/p12_read_seek_cpu.py'):
        (output / source.name).write_bytes(source.read_bytes())
    elf = PinnedElf('analysis/dev006/p12-setup-abort-v1/libfs_utility_init-p12.elf',
                    '82b27194b4eb15094ed187267472e46a47dd820691c0fa4157652eea40830f85')
    captures = [elf.capture(output, name, lo, hi) for name, lo, hi in (
        ('reader-entry-seek', 0x14b6c, 0x14b90),
        ('reader-retry-seek', 0x14bc0, 0x14bf8),
        ('reader-sector-reseek', 0x14c10, 0x14c64),
        ('reader-seek-error-continuation', 0x14d88, 0x14e68),
        ('setup-summary-reader-result', 0x1f6bc, 0x1f758))]
    try:
        rows = []
        for bases in ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000)):
            for count in (512, 16384):
                for error in (-1, -2147418110):
                    cpu, buffer, state = reader(elf, bases, count)
                    cpu.failed_seek_indices = {0, 1}
                    cpu.seek_error = error
                    result = cpu.run(0x14aec)
                    verify_return(cpu, state)
                    seen = observe(cpu, buffer, count)
                    assert result['returned'] and seen['result'] == 0 and seen['IO_flag'] == 1
                    assert seen['seeks'][0]['result'] == seen['seeks'][1]['result'] == error
                    assert seen['reads'][0]['byte_offset'] == 123456 != 37 * 512
                    assert all(x['callee'] == '0x10b74' for x in seen['reads'])
                    assert cpu.load(buffer, 1) != (37 & 255)
                    rows.append({'bases': [hex(v) for v in bases], 'request_bytes': count,
                                 'negative_seek_result': error, 'passed': True,
                                 'mock_reads_from_stale_cursor': len(cpu.reads),
                                 'returned_success_and_IO_flag_one': True,
                                 'first_actual_mock_read_offset': 123456,
                                 'requested_read_offset': 37 * 512})
        with (output / 'result.json').open('x', encoding='utf8') as stream:
            json.dump({'pass': True, 'case_count': len(rows), 'cases': rows,
                       'source_ELF_sha256': elf.sha256, 'captures': captures,
                       'source_CPU_sha256': hashlib.sha256((ROOT / 'analysis/dev006/p12_read_seek_cpu.py').read_bytes()).hexdigest(),
                       'kernel_seek_read_memset_warning_prompt_are_mocks': True,
                       'ordinary_unmounted_yes_mode_only': True,
                       'real_device_fault_or_corruption_observed': False,
                       'all_callers_or_all_IO_error_policies_proven': False}, stream, indent=2)
            stream.write('\n')
        print(json.dumps({'P12_conditional_stale_position_read_demonstrated': True,
                          'actual_instruction_cases': len(rows), 'hardware_IO': False}))
    except BaseException as error:
        with (output / 'failure.json').open('x', encoding='utf8') as stream:
            json.dump({'pass': False, 'error': repr(error), 'hardware_IO': False}, stream, indent=2)
        raise


if __name__ == '__main__':
    main()
