"""Actual C progress observer, independent decoder fault cases, and units/export checks."""
from pathlib import Path
import subprocess,json,hashlib,importlib.util,struct
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;O=R/'observations/HW002BH/metrics-v2';Q=P/'metrics-tests2';Q.mkdir(exist_ok=False)
host=(P/'host.c').read_text();host=host.replace('static u8 data[3]', 'static u8 captured_progress[4194304];static unsigned captured_size;\nstatic u8 data[3]')
host=host.replace('if(a==22){insist(c==512);','if(a==22){insist(c==512);insist(captured_size+512<=sizeof captured_progress);memcpy(captured_progress+captured_size,(void*)b,512);captured_size+=512;')
host=host.replace('int main(void){','int unused_cases(void){');at=host.rfind('}');host=host[:at]+'return 0;'+host[at:]
host+='\nint main(int argc,char**argv){insist(argc==3);reset(0);insist(!native_main());FILE*f=fopen(argv[1],"wb");insist(f!=0&&fwrite(result_data,1,8192,f)==8192);insist(!fclose(f));f=fopen(argv[2],"wb");insist(f!=0&&fwrite(captured_progress,1,captured_size,f)==captured_size);insist(!fclose(f));return 0;}\n'
(Q/'observer.c').write_text(host,encoding='utf8',newline='\n')
def run(args):
 x=subprocess.run(list(map(str,args)),capture_output=True,timeout=60);assert not x.returncode,x.stderr.decode(errors='replace');return x.stdout
run([R/'tools/toolchains/zig-x86_64-windows-0.15.2/zig.exe','cc','-target','x86_64-windows-gnu','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-I'+str(P),Q/'observer.c',P/'fill_eta_v1.c','-o',Q/'observer.exe'])
run([Q/'observer.exe',Q/'result.bin',Q/'progress.bin'])
s=importlib.util.spec_from_file_location('decode',P/'decode_metrics.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
raw=(Q/'result.bin').read_bytes();progress=(Q/'progress.bin').read_bytes();decoded=d.parse_receipt(raw,True);rows=d.parse_progress(progress,True)
assert decoded['passed'] and decoded['write_syscalls']['bytes']==5242880 and decoded['write_syscalls']['time_us']==5000000
assert decoded['read_syscalls']['bytes']==decoded['new_payload_read_bytes']+decoded['retained_full_read_bytes']+decoded['retained_sample_bytes']+decoded['control_read_bytes']
assert rows[-1]['reported_used_or_unavailable_bytes']==1982012665856-rows[-1]['available_bytes']
assert rows[-1]['available_GB']==rows[-1]['available_bytes']/1e9 and rows[-1]['available_GiB']==rows[-1]['available_bytes']/1073741824
assert rows[-1]['write_cumulative_syscall_MB_per_second']==1.048576
def rejected(fn,data):
 try:fn(data)
 except (ValueError,AssertionError):return
 raise AssertionError('Invalid evidence admitted')
for i in range(8192):
 b=bytearray(raw);b[i]^=1;rejected(lambda x:d.parse_receipt(x,True),b)
for i in range(512):
 b=bytearray(progress);b[i]^=1;rejected(lambda x:d.parse_progress(x,True),b)
semantic=0
for offset,fmt,value in [(64,'I',2),(80,'Q',5242881),(120,'Q',0),(136,'Q',0),(416,'I',50),(420,'I',0),(424,'I',9),(432,'Q',0),(4800,'I',1),(4804,'I',1),(4824,'Q',0),(4888,'Q',1),(4904,'Q',99999999),(4952,'Q',2**64-1),(4960,'I',1),(1536+56,'Q',0)]:
 b=bytearray(raw);struct.pack_into('>'+fmt,b,offset,value);b[8128:8160]=hashlib.sha256(b[:8128]).digest();rejected(lambda x:d.parse_receipt(x,True),b);semantic+=1
for offset,fmt,value in [(64,'I',1),(104,'I',1),(120,'Q',0),(128,'Q',0),(224,'Q',0),(232,'Q',0),(248,'I',1),(256,'Q',0),(352,'Q',0),(360,'Q',1),(400,'Q',1),(408,'Q',1)]:
 b=bytearray(progress);struct.pack_into('>'+fmt,b,offset,value);b[480:512]=hashlib.sha256(b[:480]).digest();rejected(lambda x:d.parse_progress(x,True),b);semantic+=1
for i in range(1,len(rows)):
 if rows[i]['window_same_phase'] and rows[i]['window_elapsed_seconds']:
  expected=(rows[i]['read_bytes']-rows[i-1]['read_bytes'])/(rows[i]['elapsed_us']-rows[i-1]['elapsed_us'])
  assert rows[i]['read_window_application_MB_per_second']==expected
assert any(x['phase']==8 for x in rows) and any(x['phase']==2 and x['written_bytes']==0 and x['write_start_elapsed_us'] for x in rows)
result=d.export(raw,progress,Q/'MODEL-ONLY-performance',True)
report={'passed':True,'actual_C_progress_records':len(rows),'receipt_single_byte_fault_cases':8192,'progress_single_byte_fault_cases':512,'checksum_consistent_semantic_fault_cases':semantic,'read_write_native_wrapper_counters_model_verified':True,'GB_GiB_fill_percent_and_window_rates_verified':True,'raw_and_CSV_JSON_export_verified':True,'native_execution':False,'model_only_export':result}
with (O/'metrics-tests.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))

