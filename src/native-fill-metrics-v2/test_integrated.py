"""Actual second-stage C with memory-only HDD/USB/graphics and retained-file faults."""
from pathlib import Path
import json,subprocess,shutil,hashlib,struct
R=Path(__file__).resolve().parents[3];P=R/'analysis/dev006/native-fill-64-metrics-v2';O=R/'observations/HW002BH/metrics-v2'
Q=P/'host-attempt1';Q.mkdir(exist_ok=False);S=Q/'source';S.mkdir()
for p in P.iterdir():
 if p.is_file() and p.suffix in ('.c','.h'):shutil.copyfile(p,S/p.name)
cmd=[str(R/'tools/toolchains/zig-x86_64-windows-0.15.2/zig.exe'),'cc','-target','x86_64-windows-gnu','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function',str(S/'host.c'),str(S/'fill_eta_v1.c'),'-o',str(Q/'contract.exe')]
c=subprocess.run(cmd,capture_output=True,timeout=60);(Q/'compile.log').write_bytes(c.stdout+c.stderr)
assert c.returncode==0,c.stderr.decode(errors='replace')
p=subprocess.run([str(Q/'contract.exe')],capture_output=True,timeout=90);(Q/'contract.log').write_bytes(p.stdout+p.stderr)
assert p.returncode==0,p.stderr.decode(errors='replace')
j=json.loads(p.stdout);assert j['passed'] and j['case_count']==81
(O/'host-contract.json').write_text(json.dumps(j,indent=2)+'\n')
raw=bytes.fromhex(j['success_record_hex']);assert hashlib.sha256(raw[:8128]).digest()==raw[8128:8160]
assert struct.unpack_from('>I',raw,68)[0]==0
assert struct.unpack_from('>Q',raw,120)[0]==64*1024**3
assert struct.unpack_from('>Q',raw,400)[0]==6*1048576 and struct.unpack_from('>I',raw,420)[0]==3
assert struct.unpack_from('>Q',raw,392)[0]==3*3*65536
for i in range(3):
 row=raw[1536+64*i:1536+64*(i+1)];assert struct.unpack_from('>I',row,4)[0]==0 and struct.unpack_from('>Q',row,56)[0]==3
report={'passed':True,'integrated_actual_C_cases':81,'host_only':True,'all_HDD_USB_syscalls_mocked':True,
 'retained_model_full_verification_bytes':6*1048576,'protected_retained_files_never_writable':True,
 'new_payload_model_cap_bytes':5*1048576,'all_handles_closed':j['all_handles_closed'],
 'requested_performance_counters_tested':True,'scope':'Includes inherited69writer/UI/cancel/error cases plus12retained preflight/full-verification/alias/hash/cancel cases. Native execution remains pending.'}
(O/'integrated-host-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
