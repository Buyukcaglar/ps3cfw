"""Execute actual minfree correction -> first allocation failure -> ordinary cleanup."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf, ROOT
from p10_partial_setup_cpu import CPU, MASK, signed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', choices=('v1', 'v2', 'v3'), default='v1')
    args = parser.parse_args()
    output = ROOT / ('analysis/dev006/p10-partial-setup-model-' + args.revision)
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    (output / 'CPU.py').write_bytes((ROOT / 'analysis/dev006/p10_partial_setup_cpu.py').read_bytes())
    try:
        elf = PinnedElf('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf',
            'daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688')
        rows = []
        for bases in ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000)):
            for drive, folder in (('PNY', 'observations/HW002W/private/native-pny-capture-v1'),
                                  ('Lexar', 'observations/HW002Z/private/native-lexar-capture-v1')):
                raw = (ROOT / folder / 'primary-superblock.decoded.bin').read_bytes()
                for write_fd in (-1, 42):
                    cpu = CPU(elf, bases)
                    cpu.fail_at = 0
                    cpu.invalid_buffer_returns_error = True
                    header = cpu.slot(-0x7b88)
                    cpu.g[30] = header
                    cpu.g[25] = cpu.slot(-0x7430)
                    assert cpu.g[25] == cpu.slot(-0x7b38)
                    cpu.store(cpu.g[25], write_fd, 4)
                    cpu.store(cpu.slot(-0x7ab4), 17, 4)
                    cpu.store(header + 8, 160, 8)
                    cpu.store(header + 0x10, 8192, 4)
                    cpu.store(header + 0x14, 0, 4)
                    cpu.store(header + 0x1c, 0x06001000, 4)
                    cpu.store(header + 0x20, 0, 1)
                    for n, byte in enumerate(raw): cpu.store(0x06001000+n, byte, 1)
                    cpu.store(0x06001000+0x3c, 100, 4)  # Synthetic invalid minfree, prompt answer yes.
                    cpu.store(0x06001000+0x34c, 0, 4)
                    cpu.store(cpu.g[26], struct.unpack_from('>q', raw, 0x438)[0], 8)
                    # Alternate buffer clean; synthetic queue empty; ordinary non-mounted mode.
                    cpu.store(cpu.slot(-0x7420)+0x20, 0, 1)
                    cpu.store(cpu.slot(-0x7b4c)+4, 0, 4)
                    cpu.store(cpu.slot(-0x7b4c)+0x10, 0, 4)
                    cpu.store(cpu.slot(-0x7b50)+0x20, 0, 1)
                    cpu.store(cpu.slot(-0x7b50)+0x1c, 0, 4)
                    cpu.cr.update({2: 1, 3: -1, 4: 0})
                    state = cpu.run(0x1f64c, {0x1f6bc})
                    assert state['returned'] and cpu.g[3] == signed(0x80010004, 32) & MASK
                    assert cpu.g[1] == 0x700006b0 and all(cpu.g[r] == v for r,v in cpu.saved.items())
                    assert '0x1f6a0' in cpu.trace
                    bad = [row for row in cpu.writes if not row['buffer_valid']]
                    if write_fd < 0:
                        assert not cpu.writes and not cpu.seeks
                        assert cpu.load(0x06001000+0x3c, 4) == 100
                        assert '0x1fb04' not in cpu.trace  # Actual prompt declines without write access.
                    else:
                        assert cpu.load(0x06001000+0x3c, 4) == 10 and '0x1fb04' in cpu.trace
                        assert '0x1fb0c' in cpu.trace and bad
                        assert cpu.writes[0]['buffer_valid'] and cpu.writes[0]['count'] == 8192
                        assert cpu.writes[0]['byte_offset'] == 81920 and cpu.writes[0]['result'] == 8192
                        assert bad[0]['pointer'] == 0
                        assert cpu.load(header+0x20, 1) == 0 and cpu.load(cpu.slot(-0x7b2c), 1) == 0
                    rows.append({'drive': drive, 'segment_bases': [hex(x) for x in bases],
                        'write_FD': write_fd, 'returned_original_OOM_status': True,
                        'actual_warning_prompt_and_setup_failure_executed': True,
                        'minfree_correction_executed': write_fd >= 0,
                        'mock_write_count': len(cpu.writes), 'invalid_buffer_mock_write_count': len(bad),
                        'first_two_write_observations': cpu.writes[:2],
                        'dirty_at_return': cpu.load(header+0x20, 1),
                        'IO_success_flag': cpu.load(cpu.slot(-0x7b2c), 1),
                        'actual_hardware_or_disk_IO': False})
        result = {'passed': True, 'case_count': len(rows), 'cases': rows,
            'finding': 'Actual ordinary yes-mode minfree correction can dirty the primary buffer; failed first summary allocation then ordinary cleanup writes the superblock and attempts null/offset summary-buffer writes.',
            'kernel_invalid_buffer_returns_error_is_mocked': True,
            'no_actual_hardware_corruption_or_fault_injection': True,
            'empty_queue_clean_alternate_buffer_valid_geometry_and_descriptor_preconditions': True,
            'whole_failure_state_reachability_or_kernel_side_effects_proven': False}
        with (output / 'result.json').open('x', encoding='utf8') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
        print(json.dumps({'conditional_failure_cases': len(rows), 'null_summary_write_attempt_reproduced': True,
                          'hardware_IO': False}))
    except BaseException as error:
        with (output / 'failure.json').open('x', encoding='utf8') as stream:
            json.dump({'passed': False, 'error': repr(error), 'hardware_IO': False}, stream, indent=2)
        raise


if __name__ == '__main__': main()
