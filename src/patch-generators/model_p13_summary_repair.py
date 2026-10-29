"""Bounded actual-instruction model of P13's final summary comparison/copy.

memcmp, memmove and the answer helper are explicit host mocks. This does not
model passes 1-5, native I/O/flush, allocator behavior or a console checker.
"""
import hashlib
import json
import struct
from pathlib import Path
from pinned_binary import PinnedElf, ROOT


def main():
    output = ROOT / 'analysis/dev006/p13-summary-repair-model-v1'
    output.mkdir(exist_ok=False)
    (output / 'source.py').write_bytes(Path(__file__).read_bytes())
    elf = PinnedElf('analysis/dev006/p13-read-seek-v1/libfs_utility_init-p13.elf',
                    'e34e18aed90eecf11fe311137b0c6e1054689fd5b019fb27a001a57542973c86')
    imports = json.loads((ROOT / 'analysis/checker-audit/libfs_utility_init.sprx.elf.imports.json').read_text('utf8'))
    salt = bytes.fromhex('6759659904250490566427499489741a')
    resolved = {}
    for name, stub in [('_sys_memcmp', 0x21688), ('_sys_memmove', 0x21468)]:
        nid = int.from_bytes(hashlib.sha1(name.encode() + salt).digest()[:4], 'little')
        row = next(row for row in imports if int(row['stub'], 16) == stub)
        assert int(row['nid'], 16) == nid and row['library'] == 'sysPrxForUser'
        resolved[hex(stub)] = name
    code = {x.address: x for lo, hi in [(0x1e590, 0x1e5c4), (0x1e690, 0x1e6e4)]
            for x in elf.instructions(lo, hi)}
    captures = [elf.capture(output, 'compare', 0x1e590, 0x1e5c4),
                elf.capture(output, 'repair-copy-dirty', 0x1e690, 0x1e6e4)]
    cache = ROOT / 'observations/HW002AO/private/pny-post-recovery-diagnostic-v1/decoded-read-cache.bin'
    with cache.open('rb') as f:
        while header := f.read(44):
            at, count = struct.unpack_from('<qi', header)
            raw = f.read(count)
            if (at, count) == (81920, 8192):
                assert hashlib.sha256(header[:12] + raw).digest() == header[12:]
                superblock = raw
                break
        else:
            raise AssertionError('Missing primary superblock')
    expected = superblock[0x3f0:0x430]
    assert len(expected) == 64 and struct.unpack_from('>q', expected, 16)[0] == 244216362
    rows = []
    mask = (1 << 64) - 1
    for base in (0x06000000, 0x08000000):
        for delta in (0, -1, 1):
            for answer in (0, 1):
                for descriptor in (0, 42):
                    stack, toc, fs, computed, dirty, fd = 0x70000000, 0x317c0, base, base+0x2000, base+0x3000, base+0x3100
                    g, cr, memory, events, trace = [0]*32, {}, {}, [], []
                    g[1], g[2], g[29], g[31] = stack, toc, fs, 0
                    def put(at, value, size):
                        payload = value.to_bytes(size, 'big') if isinstance(value, int) else value
                        assert len(payload) == size
                        memory.update({at+i: b for i, b in enumerate(payload)})
                    def get(at, size):
                        return bytes(memory.get(at+i, 0) for i in range(size))
                    original = bytearray(expected)
                    struct.pack_into('>q', original, 16, 244216362+delta)
                    put(fs+0x3f0, bytes(original), 64)
                    put(computed, expected, 64)
                    put(stack+0x10190, fs, 4); put(stack+0x101ec, computed, 4)
                    put(toc-0x74f4, fd, 4); put(fd, descriptor, 4)
                    put(toc-0x750c, dirty, 4); put(dirty+0x20, 0, 1)
                    put(toc-0x7480, 0x24698, 4)
                    put(fs+0xd0, 1, 1); put(fs+0xd2, 1, 1)
                    pc = 0x1e590
                    for steps in range(100):
                        if pc == 0x1e5c4:
                            break
                        ins = code[pc]; trace.append(hex(pc))
                        op, args, nxt = ins.mnemonic, ins.op_str.split(', '), pc+4
                        reg = lambda s: int(s[1:])
                        imm = lambda s: int(s, 0)
                        def address(s):
                            off, register = s[:-1].split('(')
                            return g[reg(register)]+imm(off)
                        if op in ('addi', 'addis'):
                            g[reg(args[0])] = (g[reg(args[1])]+imm(args[2])*(65536 if op=='addis' else 1)) & mask
                        elif op in ('lwz', 'ld'):
                            g[reg(args[0])] = int.from_bytes(get(address(args[1]), 4 if op=='lwz' else 8), 'big')
                        elif op in ('std', 'stb'):
                            size = 8 if op=='std' else 1
                            put(address(args[1]), g[reg(args[0])] & ((1 << (size*8))-1), size)
                        elif op == 'clrldi':
                            g[reg(args[0])] = g[reg(args[1])] & ((1 << (64-imm(args[2])))-1)
                        elif op == 'mr':
                            g[reg(args[0])] = g[reg(args[1])]
                        elif op == 'li':
                            g[reg(args[0])] = imm(args[1]) & mask
                        elif op == 'cmpwi':
                            value = g[reg(args[1])] & 0xffffffff
                            if value & 0x80000000:
                                value -= 1 << 32
                            cr[args[0]] = (value > imm(args[2])) - (value < imm(args[2]))
                        elif op in ('bne', 'beq', 'blt'):
                            if {'bne': cr[args[0]]!=0, 'beq': cr[args[0]]==0, 'blt': cr[args[0]]<0}[op]:
                                nxt = imm(args[1])
                        elif op == 'b':
                            nxt = imm(args[0])
                        elif op == 'bl':
                            target = imm(args[0])
                            if target == 0x21688:
                                assert g[5] == 64
                                result = 0 if get(g[3],64) == get(g[4],64) else 1
                                put(stack+0x28,toc,8); events.append('memcmp')
                            elif target == 0x14784:
                                result = answer; events.append('modeled-answer')
                            elif target == 0x21468:
                                assert (g[3],g[4],g[5]) == (fs+0x3f0,computed,64)
                                put(g[3],get(g[4],64),64); result = g[3]
                                put(stack+0x28,toc,8); events.append('memmove')
                            else:
                                raise AssertionError(('Unexpected external', hex(target)))
                            g[3] = result
                        elif op != 'nop':
                            raise AssertionError((hex(pc), op, args))
                        pc = nxt
                    else:
                        raise AssertionError('Step bound')
                    repaired = delta != 0 and answer == 1
                    assert get(fs+0x3f0,64) == (expected if repaired else bytes(original))
                    assert get(dirty+0x20,1) == bytes([int(repaired)])
                    assert get(fs+0xd0,1) == get(fs+0xd2,1) == bytes([0 if repaired else 1])
                    assert events == (['memcmp'] if delta == 0 else
                                      ['memcmp','modeled-answer','memmove'] if repaired else
                                      ['memcmp','modeled-answer'])
                    rows.append({'base':hex(base),'counter_delta':delta,'modeled_answer':answer,
                                 'modeled_write_descriptor':descriptor,'repaired_in_memory':repaired,
                                 'passed':True,'instruction_trace':trace})
    result = {
        'passed':True,'cases':len(rows),'source_sha256':elf.sha256,
        'resolved_imports':resolved,'captures':captures,'rows':rows,
        'conditional_summary_copy_and_dirty_mark_only':True,
        'passes_1_to_5_recomputation_answer_internals_native_flush_and_IO_modeled':False,
        'memcmp_memmove_and_answer_are_host_mocks':True,
        'physical_device_key_console_or_firmware_access':False,
    }
    with (output/'result.json').open('x',encoding='utf8') as f:
        json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'P13_actual_instruction_summary_model_passed':True,'cases':len(rows),
                      'native_repair_or_IO_proven':False}))


if __name__ == '__main__':
    main()
