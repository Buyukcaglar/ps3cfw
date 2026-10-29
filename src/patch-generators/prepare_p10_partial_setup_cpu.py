"""Extend the retained import-safe instruction interpreter; parents remain unchanged."""
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]


def main():
    parent = R / 'analysis/dev006/model_p10_setup_cleanup.py'
    source = parent.read_text('utf8').split('\ndef main():', 1)[0]
    source = source.replace(source[:source.index('import argparse')],
        '"""P10 partial-setup instruction CPU; kernel I/O/allocator callees remain mocks."""\n')
    source = source.replace('(0x1f694, 0x1f6bc)', '(0x1f64c, 0x1f6bc), (0x1fad0, 0x1fb14)')
    source = source.replace("elif mnemonic in ('cmpwi', 'cmpdi', 'cmpw', 'cmpd'):",
        "elif mnemonic == 'cmplwi':\n"
        "                field, left, right = args if len(args) == 3 else ('cr0', *args)\n"
        "                a, b = self.g[reg(left)] & 0xffffffff, imm(right) & 0xffff\n"
        "                self.cr[int(field[2:])] = (a > b) - (a < b)\n"
        "            elif mnemonic in ('cmpwi', 'cmpdi', 'cmpw', 'cmpd'):")
    source = source.replace('range(30000)', 'range(200000)')
    output = R / 'analysis/dev006/p10_partial_setup_cpu.py'
    with output.open('x', encoding='utf8') as stream:
        stream.write(source)
    with (R / 'analysis/dev006/p10-partial-setup-cpu-provenance.json').open('x', encoding='utf8') as stream:
        json.dump({'parent': str(parent.relative_to(R)).replace('\\', '/'),
            'parent_sha256': hashlib.sha256(parent.read_bytes()).hexdigest(),
            'new_CPU_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'changes': 'Additional captured minfree correction/entry spans, unsigned cmplwi, larger bounded host step count; no firmware changes',
            'parent_modified': False}, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'host_CPU_prepared': True, 'firmware_or_hardware_changed': False}))


if __name__ == '__main__': main()
