"""Independent ELF/import/postprocessing/receipt and source-boundary checks."""
import datetime,hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];P=R/'analysis/dev006/native-fill-64-metrics-v2';A=R/'observations/HW002BH/metrics-v2';SDK=R/'tools/psl1ght-reference-20261014/source'
sys.path.insert(0,str(R/'tools/python_packages'))
from capstone import Cs,CS_ARCH_PPC,CS_MODE_64,CS_MODE_BIG_ENDIAN
def load(n,p):
 s=importlib.util.spec_from_file_location(n,R/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sdk=load('sdk','analysis/dev006/audit_au_sdk_layout_v2.py');reader=load('reader','tools/Read-HW002BF-Fill.py')
b,ph,sections,named=sdk.readelf(P/'display.elf');raw=(P/'attempt-second/display-gnu.elf').read_bytes();expected=bytearray(raw);expected[7]=102
assert b==(P/'display-repro.elf').read_bytes()
assert (P/'start.S').read_bytes()==(R/'analysis/dev006/native-io-smoke-exit-v7/start.S').read_bytes()
assert (P/'lv2.ld').read_bytes()==(SDK/'ppu/crt/lv2.ld').read_bytes()
loads=[h for h in ph if h[0]==1]
def get(addr,size):
 h=next(h for h in loads if h[3]<=addr and addr+size<=h[3]+h[5]);return b[h[2]+addr-h[3]:h[2]+addr-h[3]+size]
symtab=named['.symtab'];strings=sections[symtab[6]];st=b[strings[4]:strings[4]+strings[5]];symbols={}
for i in range(0,symtab[5],24):
 n,info,other,sh,value,size=struct.unpack_from('>IBBHQQ',b,symtab[4]+i);name=st[n:].split(b'\0')[0].decode();symbols[name]=(value,size,sh)
assert not [n for n,(v,size,sh) in symbols.items() if n and not sh]
imports=[];stub=named['.lib.stub'];fnid=named['.rodata.sceFNID'];starts=[struct.unpack_from('>I',b,stub[4]+i+20)[0] for i in range(0,stub[5],44)]
libs=['libgcm_sys','libsysutil','libio'];assert stub[5]==44*len(libs)
for index,lib in enumerate(libs):
 q=P/'imports'/lib;primary=SDK/'ppu/sprx'/lib
 for n in ('config.h',):assert (q/n).read_bytes()==(primary/n).read_bytes()
 for n in ('exports.S','libexport.c'):assert (q/n).read_bytes()==(SDK/'ppu/sprx/common'/n).read_bytes()
 selected=(q/'exports.h').read_text().splitlines();all_lines=(primary/'exports.h').read_text().splitlines();assert all(x in all_lines for x in selected)
 tuples=[re.fullmatch(r'EXPORT\((\w+),\s*(0x[0-9a-fA-F]+)\);',x).groups() for x in selected]
 off=stub[4]+44*index;count=struct.unpack_from('>H',b,off+6)[0];nameptr,ids,funcs=struct.unpack_from('>3I',b,off+16)
 lname=re.search(r'LIBRARY_NAME\s+"([^"]+)"',(q/'config.h').read_text()).group(1);assert get(nameptr,len(lname)+1)==lname.encode()+b'\0'
 assert count==len(tuples) and ids==starts[index]
 stop=min([fnid[3]+fnid[5]]+[x for x in starts if x>ids]);assert stop-ids==count*4
 struct.pack_into('>H',expected,off+6,count)
 for j,(name,nid) in enumerate(tuples):
  assert struct.unpack('>I',get(ids+4*j,4))[0]==int(nid,16)
  assert struct.unpack('>I',get(funcs+4*j,4))[0]==symbols['__'+name][0]
 imports.append({'library':lname,'functions':count})
code=[s for s in sections if s[1]==1 and s[2]&4];md=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN);md.skipdata=True;instructions=[i for s in code for i in md.disasm(b[s[4]:s[4]+s[5]],s[3])]
assert sum(i.size for i in instructions)==sum(s[5] for s in code)
assert all(int.from_bytes(i.bytes,"big") in (0,1,3,0x20000) for i in instructions if not i.id)
for x in instructions:
 if not x.id and int.from_bytes(x.bytes,"big")==0x20000:assert get(x.address-12,16)==struct.pack(">4I",0x4e800020,0,0,0x20000) # GCC PPC64 traceback words
calls=0
for i in instructions:
 if i.mnemonic in ('b','bl'):
  target=int(i.op_str,16);assert any(s[3]<=target<s[3]+s[5] for s in code);calls+=i.mnemonic=='bl'
opd=named['.opd'];assert opd[5]%24==0
for off in range(opd[4],opd[4]+opd[5],24):
 pc,toc,packed=struct.unpack_from('>3Q',b,off);assert pc<2**32 and toc<2**32 and packed==(pc<<32)|toc
 assert any(s[3]<=pc<s[3]+s[5] for s in code);struct.pack_into('>Q',expected,off+16,(pc<<32)|toc)
assert b==expected # No other postprocessing or hidden mutations.
entry=get(struct.unpack_from('>Q',b,24)[0],8);assert struct.unpack('>2I',entry)==(named['.text'][3],named['.text'][3])
assert any(i.mnemonic=='mftb' for i in instructions)

main=(P/'main.c').read_text();ui=(P/'fill_io_ui_v1.h').read_text();budget=json.loads((A/'budget.json').read_text())
snapshot=P/'attempt-second/source'
for n in ('main.c','retained.h','retained-host.h','session.h','fill_io_ui_v1.h','controls.h','fill_ui_ps3_v1.c','fill_ui_canvas_v1.c','fill_eta_v1.c'):
 assert (P/n).read_bytes()==(snapshot/n).read_bytes(),n
assert set(map(int,re.findall(r'call\((\d+),',main)))=={141,801,802,803,804,809,818,820,840}
assert 'MAX_NEW_FILES 8u' in main and 'if(file_count>=MAX_NEW_FILES)' in main
assert 'if(written>NEW_LIMIT-CHUNK)return 44' in main and 'RESERVE_BB+MARGIN+CHUNK' in main
assert 'RESERVE_BB (64ULL*GIB)' in main and 'MARGIN (2ULL*GIB)' in main
assert main.count('openf(file_path,1|0100|0200,&hfd)')==1 and main.count('writef(hfd,buffer,CHUNK,&got)')==1
assert main.count('openf(a->path,0,&hfd)')==2 and 'mode!=(1|0100|0200)||!allowed_hdd_output(p)' in main
assert 'fd==hfd' in main and 'perf_pack(progress_record+256,&perf_read)' in main and 'perf_pack(progress_record+304,&perf_write)' in main
assert 'sequence>=8192' in main and 'sha_update(&hash,progress_record,480)' in main
assert 'perf_space_us=fill_screen_now_us()-perf_origin_us' in main and 'perf_write_start_us' in ui
assert 'OLD_COUNT;i++){status=verify_retained(i,0)' in main and 'OLD_COUNT;i++){status=verify_retained(i,1)' in main
assert 'if(!equal(digest,a->sha,32))return 98' in main and 'retained_seed' in main
assert 'if(button==1&&released)' in ui and 'now-ui_last<250000ULL' in ui
assert budget['new_payload_upper_bound_bytes']==70613204992 and budget['retained_full_verification_bytes']==850899501056
for n in ('fill_ui_ps3_v1.c','fill_ui_ps3_v1.h','fill_eta_v1.c','fill_eta_v1.h','sha256.h','controls.h'):
 assert (P/n).read_bytes()==(R/'analysis/dev006/native-fill-final-v16'/n).read_bytes(),n
assert json.loads((A/'integrated-host-tests.json').read_text())['integrated_actual_C_cases']==81
assert json.loads((A/'metrics-tests.json').read_text())['passed']
report={'passed':True,'exact_build_source_snapshot_matches':True,'two_linked_ELFs_byte_identical':True,'imports':imports,
 'OPD32_descriptors':opd[5]//24,'direct_calls_checked':calls,'only_three_primary_linker_transforms':True,
 'graphics_clock_ETA_reused_byte_exact':True,'raw_console_memory_or_device_IO':False,'HDD_write_guard_new_nonce_only':True,
 'retained_and_game_paths_read_only':True,'fresh_X_admission_and_Circle_cancel':True,'capacity_correlated_HDD_syscall_metrics':True,
 'native_execution':False,'host_cases':81,'retained_full_read_expected_bytes':850899501056}
with (A/'source-ELF-independent-audit.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))
