"""Extend import-safe modeled CPU through actual summary reads and failed-read fallback."""
import hashlib
import json
from pathlib import Path
from pinned_binary import PinnedElf,ROOT


def main():
    parent=ROOT/'analysis/dev006/p10_partial_setup_cpu.py'
    source=parent.read_text('utf8')
    source=source.replace('P10 partial-setup instruction CPU','P11 summary-read instruction CPU')
    source=source.replace('(0x1f64c, 0x1f6bc)', '(0x1f64c, 0x1f798), (0x14aec, 0x14e80), (0x1fd34, 0x1fd4c), (0x26540, 0x2658c)')
    source=source.replace('self.setup_allocations = []','self.setup_allocations = []\n        self.reads = []\n        self.fail_read_block = None\n        self.read_block_index = 0\n        self.failed_sector_pointer = None\n        self.memsets = []')
    old="        elif address == 0xe7a0:"
    new='''        elif address in (0xf5d8, 0x10b74):
            pointer, count = self.g[4], self.g[5]
            self.access(pointer, count)
            if address == 0xf5d8:
                failed = self.read_block_index == self.fail_read_block
                self.read_block_index += 1
                if failed: self.failed_sector_pointer = pointer
            else:
                failed = pointer == self.failed_sector_pointer
            result = -1 if failed else count
            if not failed:
                for n in range(count): self.store(pointer+n, 0xa5, 1)
            self.reads.append({'callee':hex(address), 'pointer':pointer, 'count':count,
                'result':result, 'byte_offset':self.cursor})
            if result > 0: self.cursor += result
            self.clobber(result)
        elif address == 0x214e8:
            pointer, value, count = self.g[3], self.g[4] & 255, self.g[5]
            self.access(pointer,count)
            for n in range(count): self.store(pointer+n,value,1)
            self.memsets.append({'pointer':pointer,'value':value,'count':count})
            self.store(self.g[1]+0x28,self.g[2],8)
            self.clobber(pointer)
        elif address == 0xe7a0:'''
    assert old in source;source=source.replace(old,new)
    output=ROOT/'analysis/dev006/p11_summary_read_cpu.py'
    with output.open('x',encoding='utf8') as stream:stream.write(source)
    folder=ROOT/'analysis/dev006/p11-summary-read-source-extra-v1';folder.mkdir(exist_ok=False)
    elf=PinnedElf('analysis/dev006/p11-summary-guard-v2/libfs_utility_init-p11.elf',
        '904be1b7aa71f365a8e1b3c936cbf794082c664c4405929a5be5ed7b4d2a253e')
    rows=[elf.capture(folder,'summary-decline-abort',0x1fd34,0x1fd4c)]
    with (folder/'provenance.json').open('x',encoding='utf8') as stream:
        json.dump({'parent':str(parent.relative_to(ROOT)).replace('\\','/'),
            'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),
            'new_CPU_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'changes':'Actual read/summary/abort/P11 helper spans plus explicit kernel read/memset mocks; ordinary nonmounted mode',
            'parent_modified':False,'new_captures':rows,'device_IO':False},stream,indent=2);stream.write('\n')
    print(json.dumps({'actual_read_CPU_ready':True,'disk_IO':False}))


if __name__=='__main__':main()
