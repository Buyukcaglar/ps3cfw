"""Independent new pattern oracle, protected-write admission, high-offset vectors and UI previews."""
from pathlib import Path
import subprocess,json,hashlib,struct,zlib,shutil
R=Path(__file__).resolve().parents[3];P=R/'analysis/dev006/native-fill-64-metrics-v2';O=R/'observations/HW002BH/metrics-v2';Q=P/'boundary-tests1';Q.mkdir(exist_ok=False)
cc=R/'tools/toolchains/zig-x86_64-windows-0.15.2/zig.exe';budget=json.loads((O/'budget.json').read_text())
def run(cmd):
 p=subprocess.run(list(map(str,cmd)),capture_output=True,timeout=60)
 assert p.returncode==0,p.stderr.decode(errors='replace');return p.stdout
code=r'''
#define main integrated_main
#include "host-return-fixture.c"
#undef main
int main(void){
 reset(0);s32 fd=-1;
 for(u32 i=0;i<OLD_COUNT;i++)insist(openf(retained_specs[i].path,193,&fd)==(s32)0x80010009u&&fd==-1);
 insist(openf("/dev_hdd0/home/savedata/x",193,&fd)==(s32)0x80010009u);
 insist(openf("/dev_hdd0/tmp/other.bin",193,&fd)==(s32)0x80010009u);
 path_for(8);insist(openf(file_path,193,&fd)==(s32)0x80010009u);
 path_for(0);insist(openf(file_path,2,&fd)==(s32)0x80010009u);
 ui_start_confirmed=1;insist(!openf(file_path,193,&fd));insist(!closef(fd));
 u32 ids[]={0,4,7};u64 offsets[]={0,4294967288ULL,4294967296ULL,17179869176ULL};
 for(u32 seedcase=0;seedcase<2;seedcase++)for(u32 i=0;i<3;i++)for(u32 k=0;k<4;k++){
  u64 seed=seedcase?retained_seed:pattern_seed;u64 v=seeded_word(seed,ids[i],offsets[k]);
  printf("%u %u %llu %016llx\n",seedcase,ids[i],offsets[k],v);
 }return 0;
}
'''
host_fixture=(P/'host.c').read_text(); at=host_fixture.rfind('}'); (Q/'host-return-fixture.c').write_text(host_fixture[:at]+'return 0;'+host_fixture[at:],encoding='utf8',newline='\n')
(Q/'guard-pattern.c').write_text(code,encoding='utf8',newline='\n')
stdout=run([cc,'cc','-target','x86_64-windows-gnu','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-Wno-unused-function','-I'+str(P),Q/'guard-pattern.c',P/'fill_eta_v1.c','-o',Q/'guard-pattern.exe'])
stdout=run([Q/'guard-pattern.exe']);(Q/'guard-pattern.stdout').write_bytes(stdout)
mask=(1<<64)-1
def word(seed,index,at):
 x=((seed^((index<<32)|(at>>3)))+0x9e3779b97f4a7c15)&mask;x=((x^(x>>30))*0xbf58476d1ce4e5b9)&mask;x=((x^(x>>27))*0x94d049bb133111eb)&mask;return x^(x>>31)
seen=set()
for line in stdout.decode().splitlines():
 seedcase,index,at,value=line.split();seed=budget['retained_pattern_seed'] if int(seedcase) else budget['new_pattern_seed'];value=int(value,16)
 assert value==word(seed,int(index),int(at)) and value not in seen;seen.add(value)
raw=bytes.fromhex(json.loads((O/'host-contract.json').read_text())['success_record_hex'])
for index,n in enumerate((2097152,2097152,1048576)):
 data=b''.join(struct.pack('>Q',word(budget['new_pattern_seed'],index,at)) for at in range(0,n,8))
 assert hashlib.sha256(data).digest()==raw[512+96*index+24:512+96*index+56]
# Compile the actual modified canvas and unchanged ETA implementation.
preview=(R/'analysis/dev006/native-display-memory-v14/host-tests/preview.c').read_text()
preview=preview.replace(' if(mode==1)', ' if(mode==4){s.phase=8;s.simulated=0;s.written=0;s.target='+str(budget['new_payload_upper_bound_bytes'])+'ULL;s.available='+str(budget['baseline_native_available_bytes'])+'ULL;s.eta_kind=FILL_ETA_CALCULATING;}\n if(mode==5){s.phase=4;s.simulated=0;s.written='+str(budget['new_payload_upper_bound_bytes'])+'ULL;s.target=s.written;s.available=66ULL*1073741824;s.verified=400ULL*1073741824;s.verify_target=921512706048ULL;s.eta_kind=FILL_ETA_MEASURED;s.eta_seconds=36000;}\n if(mode==1)')
(Q/'preview.c').write_text(preview,encoding='utf8',newline='\n');run([cc,'cc','-target','x86_64-windows-gnu','-O2','-I'+str(P),Q/'preview.c',P/'fill_ui_canvas_v1.c',P/'fill_eta_v1.c','-o',Q/'preview.exe'])
def png(w,h,rgb):
 def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b))
 rows=b''.join(b'\0'+rgb[y*w*3:(y+1)*w*3] for y in range(h));return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
paths=[]
for w,h,mode in [(720,480,4),(1920,1080,4),(1920,1080,5)]:
 img=run([Q/'preview.exe',w,h,mode]).replace(b'\r\n',b'\n');head=f'P6\n{w} {h}\n255\n'.encode();assert img.startswith(head);rgb=img[len(head):];assert len(rgb)==w*h*3
 path=Q/f'phase{mode}-{w}x{h}.png';path.write_bytes(png(w,h,rgb));paths.append(str(path))
report={'passed':True,'protected_write_negative_cases':7,'new_owned_write_positive_case':1,
 'actual_C_high_offset_vectors':len(seen),'cross_seed_high_bits_disjoint':bool((budget['new_pattern_seed']^budget['retained_pattern_seed'])>>40),
 'independent_new_payload_SHA_bytes':5242880,'previews':paths,'ETA_source_unchanged':(P/'fill_eta_v1.c').read_bytes()==(R/'analysis/dev006/native-fill-final-v16/fill_eta_v1.c').read_bytes(),
 'native_execution':False,'real_storage_USB_console_access':False}
(O/'boundary-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

