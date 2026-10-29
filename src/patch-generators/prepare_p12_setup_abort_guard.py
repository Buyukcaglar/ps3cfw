"""Fail closed on summary-read error and discard uncommitted dirty setup buffers on OOM."""
import hashlib
import json
import struct
from pinned_binary import PinnedElf,ROOT


def branch(source,target,link=False):
    delta=target-source
    assert delta%4==0 and -(1<<25)<=delta<(1<<25)
    return 0x48000000|(delta&0x3fffffc)|int(link)


def main():
    output=ROOT/'analysis/dev006/p12-setup-abort-v1';output.mkdir(exist_ok=False)
    elf=PinnedElf('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf',
        '904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e')
    assert elf.bytes_at(0x265c0,64)==bytes(64)
    hooks={0x1f754:(0x2f9c0000,0x265c0,False),0x1fb6c:(0x4bff5315,0x265e0,True)}
    clear=[0x38000000,0x81228478,0x98090020,0x812284b0,0x98090020,0x812284d4,0x98090000]
    words=clear+[branch(0x265dc,0x1fd34)]+clear+[branch(0x265fc,0x14e80)]
    helper=b''.join(struct.pack('>I',word) for word in words)
    decoded=list(elf.decoder.disasm(helper,0x265c0))
    expected=[('li','r0, 0'),('lwz','r9, -0x7b88(r2)'),('stb','r0, 0x20(r9)'),
        ('lwz','r9, -0x7b50(r2)'),('stb','r0, 0x20(r9)'),('lwz','r9, -0x7b2c(r2)'),('stb','r0, 0(r9)')]
    assert [(i.mnemonic,i.op_str) for i in decoded]==expected+[('b','0x1fd34')]+expected+[('b','0x14e80')]
    def offset(address):
        segment=next(h for h in elf.loads if h[3]<=address< h[3]+h[5])
        return segment[2]+address-segment[3]
    new=bytearray(elf.data)
    for at,(old,target,link) in hooks.items():
        assert elf.word(at)==old
        struct.pack_into('>I',new,offset(at),branch(at,target,link))
    new[offset(0x265c0):offset(0x265c0)+64]=helper
    restored=bytearray(new)
    for at in hooks:restored[offset(at):offset(at)+4]=elf.bytes_at(at,4)
    restored[offset(0x265c0):offset(0x265c0)+64]=bytes(64)
    assert restored==elf.data
    with (output/'libfs_utility_init-p12.elf').open('xb') as stream:stream.write(new)
    with (output/'helper.txt').open('x',encoding='utf8') as stream:
        stream.write(''.join(f'{i.address:08x} {i.bytes.hex()} {i.mnemonic} {i.op_str}\n' for i in decoded))
    with (output/'manifest.json').open('x',encoding='utf8') as stream:
        json.dump({'source':elf.relative,'source_sha256':elf.sha256,'elf_sha256':hashlib.sha256(new).hexdigest(),
            'file_bytes_unchanged':len(new),'hooks':{hex(at):{'old':hex(old),'new':hex(branch(at,target,link))}
                for at,(old,target,link) in hooks.items()},'helper_virtual_address':'0x265c0','helper_bytes':64,
            'purpose':'Any nonzero summary read result clears uncommitted setup-buffer dirty bytes/IO-success and takes original cleanup+exit8; common setup-OOM cleanup also discards those uncommitted buffers and preserves original OOM return',
            'successful_summary_read_and_setup_paths_intended_unchanged':True,
            'no_new_calls_syscalls_allocations_imports_relocations_memory_sizes_or_observer_changes':True,
            'whole_failure_cleanup_or_stability_proven':False,'packaged_or_hardware_tested':False},stream,indent=2)
        stream.write('\n')
    print(json.dumps({'P12_decoded_draft':True,'hooks':2,'owned_helper_bytes':64,
        'elf_sha256':hashlib.sha256(new).hexdigest(),'hardware_IO':False}))


if __name__=='__main__':main()
