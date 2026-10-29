"""Correct the retained v1 audit's original-layout address assumption; saved source only."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];O=R/'observations/HW002BJ/closure-v1'
failure={'attempt':'analysis/dev006/audit_p13_heap_interface_inheritance_v1.py',
 'error':'AssertionError at target==0x4ba44 after four slice and five D-form use comparisons',
 'fixture_error':'Original-data virtual addresses were applied to the expanded P9/P13 text/data layout. The old slot VA lies in their zero-filled text cave, not their data segment.',
 'source_or_firmware_changed_by_failure':False,'failed_attempt_preserved':True,
 'correction':'Translate the original data-segment-relative slot offset, then check its actual relocation site/target in both exact candidates; do not treat an unrelocated file word as the loaded pointer.'}
with (O/'heap-inheritance-v1-failure.json').open('x',encoding='utf8') as f:json.dump(failure,f,indent=2);f.write('\n')
s=(R/'analysis/dev006/audit_p13_heap_interface_inheritance_v1.py').read_text()
anchor="assert current==(R/'analysis/build-p13-first/candidate.python.elf').read_bytes()"
s=s.replace(anchor,anchor+"\noriginal,rp=load('analysis/fs-review/libfs_utility_init.sprx.elf','6fdcb1ab4a25c29230dbd5fdf0f2594ee8c9c5187ee3c13dbd384128c2504b9a')\nslot_offset=0x26a08-rp[1][3];target_offset=0x4ba44-rp[1][3]\nassert slot_offset==0x17a8 and op[1][3]==np[1][3]\nslot=np[1][3]+slot_offset;target=np[1][3]+target_offset\nassert np[1][3]+np[1][5]<=target<np[1][3]+np[1][6]\n")
s=s.replace("('heap_global_pointer_slot',0x26a08,0x26a0c)","('heap_global_pointer_slot',slot,slot+4),('observer_code',0x25b90,0x25b90+2124)")
s=s.replace("target=int.from_bytes(region(current,np,0x26a08,0x26a0c),'big');assert target==0x4ba44", "raw_slot_word=int.from_bytes(region(current,np,slot,slot+4),'big')")
s=s.replace("if ph[vi][3]+add in (0x26a08,target):", "if ph[ai][3]+off==slot:")
s=s.replace("[{'site':0x26a08,'target':target,'type':1}]", "[{'site':slot,'target':target,'type':1}]")
s=s.replace("'slot_target':target", "'translated_slot_VA':slot,'unrelocated_file_word':raw_slot_word,'slot_relocation_target':target,'target_in_BSS':True")
s=s.replace("'complete_observer_or_allocator_internals_compared':False", "'observer_code_slice_P9_P13_identical':True,'complete_allocator_internals_compared':False")
s=s.replace("O/'P13-heap-interface-inheritance.json'", "O/'P13-heap-interface-inheritance-v2.json'")
p=R/'analysis/dev006/audit_p13_heap_interface_inheritance_v2.py'
with p.open('x',encoding='utf8') as f:f.write(s)
print(json.dumps({'fresh_audit_v2_prepared':True,'v1_preserved':True}))
