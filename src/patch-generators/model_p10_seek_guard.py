"""Differential actual-instruction checks for the three P10 seek-error stops."""
import hashlib
import json
import struct
from pathlib import Path
from model_p9_write_flush_v2 import CPU, Abort, MASK
from pinned_binary import PinnedElf, ROOT


def make_cpu(elf, bases, patched):
    cpu = CPU(elf, bases)
    if patched:
        cpu.code.update({i.address: i for i in elf.instructions(0x26500, 0x26520)})
    return cpu


def main():
    output = ROOT / 'analysis/dev006/p10-seek-guard-model-v1'
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    try:
        before = PinnedElf('analysis/dev006/p9-safety-v2/libfs_utility_init-p9.elf',
            '1f96019830843f76999383a2369af9b9628aefa61a9bfdb20379698a025b52a2')
        after = PinnedElf('analysis/dev006/p10-seek-guard-v1/libfs_utility_init-p10.elf',
            'daba75f996232fb7fa1166247549b2bd0a807bc2dcd9ab17168d6c111306b688')
        assert before.headers == after.headers and len(before.data) == len(after.data)
        allowed = [(at, at + 4) for at in (0x14ad8, 0x14ae8, 0x14a28)] + [(0x26500, 0x26520)]
        for header in before.loads:
            lo, off, length = header[3], header[2], header[5]
            for n in range(length):
                if before.data[off + n] != after.data[off + n]:
                    assert any(a <= lo + n < b for a, b in allowed)
        for header in after.headers:
            if header[0] == 0x700000a4:
                for off in range(header[2], header[2] + header[5], 24):
                    site, reserved, vi, ai, kind, addend = struct.unpack_from('>QHBBIQ', after.data, off)
                    assert not (vi == 0 and 0x26500 <= addend < 0x26520)
        cases = []
        for bases in ((0x1000000, 0x2000000), (0x23000000, 0x45000000), (0x50000000, 0x12000000)):
            for sector in (0, 4000, 2147483664, 4000797296):
                at = sector * 512
                for count in (512, 4096, 16384):
                    for mode in ('success', 'initial-seek-fail', 'retry-seek-fail',
                                 'sector-reseek-fail', 'bulk-short-retry-success',
                                 'sector-write-fail-reseek-success', 'forced-abort', 'negative-FD'):
                        observations = []
                        for patched, elf in ((False, before), (True, after)):
                            cpu = make_cpu(elf, bases, patched)
                            cpu.g[3:7] = [MASK if mode == 'negative-FD' else 42,
                                          0x06010000, sector, count]
                            if mode in ('initial-seek-fail', 'forced-abort'):
                                cpu.seek_results = [-1]
                            elif mode == 'retry-seek-fail':
                                cpu.seek_results, cpu.write_results = [at, -1], [0]
                            elif mode == 'sector-reseek-fail':
                                cpu.seek_results, cpu.write_results = [at, at, -1], [-1, -1]
                            elif mode == 'bulk-short-retry-success': cpu.write_results = [0]
                            elif mode == 'sector-write-fail-reseek-success': cpu.write_results = [-1, -1]
                            if mode == 'forced-abort': cpu.store(cpu.slot(-0x7b10), 1, 4)
                            saved = {reg: cpu.g[reg] for reg in (1, 2, *range(14, 32))}
                            saved_cr = {reg: cpu.cr[reg] for reg in (2, 3, 4)}
                            aborted = False
                            try:
                                cpu.run(0x14918)
                            except Abort:
                                aborted = True
                            if not aborted:
                                assert cpu.lr == 0x76543210
                                assert all(cpu.g[reg] == value for reg, value in saved.items())
                                assert all(cpu.cr[reg] == value for reg, value in saved_cr.items())
                            row = {'writes': cpu.writes, 'seeks': cpu.seeks, 'aborted': aborted,
                                   'result': cpu.g[3], 'IO_success_flag': cpu.load(cpu.slot(-0x7b2c), 1),
                                   'modified_flag': cpu.load(cpu.slot(-0x7b00), 4)}
                            observations.append(row)
                        original, corrected = observations
                        if mode == 'initial-seek-fail':
                            assert corrected['seeks'][0]['result'] == -1 and not corrected['writes']
                            assert len(corrected['seeks']) == 1 and corrected['result'] == MASK
                            assert corrected['IO_success_flag'] == 0
                        elif mode == 'retry-seek-fail':
                            assert len(corrected['writes']) == 1 and corrected['writes'][0]['result'] == 0
                            assert len(corrected['seeks']) == 2 and corrected['result'] == MASK
                            assert corrected['IO_success_flag'] == 0
                        elif mode == 'sector-reseek-fail':
                            assert len(corrected['writes']) == 2 and all(w['result'] == -1 for w in corrected['writes'])
                            assert len(corrected['seeks']) == 3 and corrected['result'] == MASK
                            assert corrected['IO_success_flag'] == 0
                            if count > 512:
                                assert original['writes'][2]['byte_offset'] == at
                                assert original['writes'][2]['pointer'] == 0x06010000 + 512
                        else:
                            assert original == corrected, mode
                        if mode == 'success':
                            assert len(corrected['writes']) == 1 and corrected['writes'][0]['byte_offset'] == at
                            assert corrected['modified_flag'] == 1
                        if mode == 'negative-FD': assert not corrected['writes'] and not corrected['seeks']
                        if mode == 'forced-abort': assert corrected['aborted'] and not corrected['writes']
                        cases.append({'case': mode, 'segment_bases': [hex(x) for x in bases],
                                      'sector': sector, 'bytes': count, 'passed': True,
                                      'P9_write_calls': len(original['writes']),
                                      'P10_write_calls': len(corrected['writes']),
                                      'P10_IO_success_flag': corrected['IO_success_flag']})
            for drive, folder in (('PNY', 'observations/HW002W/private/native-pny-capture-v1'),
                                  ('Lexar', 'observations/HW002Z/private/native-lexar-capture-v1')):
                raw = (ROOT / folder / 'primary-superblock.decoded.bin').read_bytes()
                for dirty, present in ((0, True), (1, True), (0, False), (1, False)):
                    observations = []
                    for patched, elf in ((False, before), (True, after)):
                        cpu = make_cpu(elf, bases, patched)
                        head = cpu.slot(-0x7b88)
                        for n, byte in enumerate(raw): cpu.store(0x06001000 + n, byte, 1)
                        cpu.store(head + 8, 160, 8)
                        cpu.store(head + 0x10, 8192, 4)
                        cpu.store(head + 0x14, 0, 4)
                        cpu.store(head + 0x1c, 0x06001000, 4)
                        cpu.store(head + 0x20, dirty, 1)
                        cpu.store(0x06001000 + 0x34c, 0x06010000 if present else 0, 4)
                        cpu.g[3:5] = [42, head]
                        cpu.invalid_buffer_returns_error = True
                        cpu.run(0x1558c)
                        observations.append({'writes': cpu.writes, 'seeks': cpu.seeks,
                                             'IO_success': cpu.load(cpu.slot(-0x7b2c), 1),
                                             'dirty_at_return': cpu.load(head + 0x20, 1)})
                    assert observations[0] == observations[1]
                    cases.append({'case': 'inherited-flush-' + drive, 'segment_bases': [hex(x) for x in bases],
                                  'dirty': dirty, 'summary_present': present, 'passed': True})
        result = {'pass': True, 'case_count': len(cases), 'cases': cases,
            'elf_sha256': after.sha256, 'parent_elf_sha256': before.sha256,
            'three_seek_error_paths_stop_before_further_write_calls': True,
            'ordinary_success_and_successful_reseek_paths_differentially_unchanged': True,
            'GPR_nonvolatile_TOC_stack_LR_and_CR2_4_preserved_on_returns': True,
            'normal_warning_and_prompt_instructions_executed': True,
            'kernel_IO_strcmp_format_and_nonlocal_exit_callees_mocked': True,
            'exact_three_hook_words_and32_helper_bytes_only': True,
            'hardware_fault_injection_or_execution': False,
            'whole_checker_failure_cleanup_integrity_or_stability_proven': False}
        with (output / 'result.json').open('x', encoding='utf8') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        print(json.dumps({'P10_instruction_model_passed': True, 'cases': len(cases),
                          'seek_failure_paths': 3, 'hardware_IO': False}))
    except BaseException as error:
        with (output / 'failure.json').open('x', encoding='utf8') as f:
            json.dump({'passed': False, 'error': repr(error), 'hardware_IO': False}, f, indent=2)
        raise


if __name__ == '__main__':
    main()
