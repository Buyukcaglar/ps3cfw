"""One approved fixed-E USB stage/capture; inspect is entirely offline. Never firmware access."""
import argparse,ctypes,hashlib,json,os,re
from pathlib import Path
from decode_metrics import need,export,NONCE
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;O=R/'observations/HW002BH/metrics-v2'
PLAN=O/'release-proposal.json';CHECKPOINT='analysis/dev006/hw002bh-64-reserve-prepared-checkpoint.json'
PREFIX='HDD2TB-BH-bab693d274eed6a0'
NAMES={'package':'HDD2TB-BH-FILL-v2.pkg','ready':PREFIX+'.READY','source':PREFIX+'-STOP-SOURCE.bin','stop':PREFIX+'.STOP','result':PREFIX+'-FILL.bin','progress':PREFIX+'-PROGRESS.bin','wait':PREFIX+'-WAIT.bin','done':PREFIX+'-DONE.bin'}
USB={'volume_guid':'\\\\?\\Volume{00000000-0000-0000-0000-000000000000}\\','volume_serial':'<volume-serial>','filesystem':'FAT32','volume_bytes':125129687040}
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(p):return (json.dumps(p,sort_keys=True,separators=(',',':'))+'\n').encode()
def new(p,b):
 p=Path(p);b=b if isinstance(b,bytes) else (json.dumps(b,indent=2)+'\n').encode()
 with p.open('xb') as f:need(f.write(b)==len(b),'Short evidence write');f.flush();os.fsync(f.fileno())
def bound(path,h):
 p=(R/path).resolve();need(p.is_relative_to(R) and 'private' not in p.parts and 'eid_root_key' not in str(p).lower(),'Invalid binding path')
 need(p.is_file() and sha(p.read_bytes())==h,'Changed binding '+path);return p.read_bytes()
def admitted(plan,approval,expected):
 need(plan['schema']=='HW002BH-64-reserve-release-v2' and plan['hardware_authorized'] is False and plan['reviewed'] is True,'Unreviewed proposal')
 need(sha(canonical(plan))==expected,'Exact approved plan hash')
 need(approval.get('schema')=='HW002BH-native-authorization-v2' and approval.get('plan_sha256')==expected and approval.get('nonce')==NONCE.hex(),'Missing exact human approval')
 need(approval.get('actions')==['stage_once','launch_once','capture_once'] and approval.get('human_answer_exact','').strip(),'Approval scope')
 need(approval.get('protocol_sha256')==plan['bindings']['observations/HW002BH/metrics-v2/PROTOCOL.txt'],'Approval protocol')
 need(plan['names']==NAMES and plan['usb_identity']==USB,'Namespace/USB policy')
 need(plan['limits']=={'new_payload_bytes':70613204992,'new_files':8,'file_bytes':17179869184,'reserve_bytes':68719476736,'metadata_margin_bytes':2147483648,'next_chunk_bytes':1048576,'progress_bytes':4194304},'Bounded limits changed')
 for path,h in plan['bindings'].items():bound(path,h)
 status=json.loads((R/'plan/STATUS.json').read_text());need(status['current_checkpoint']==CHECKPOINT,'Current authority changed')
 cp=json.loads((R/CHECKPOINT).read_text());need(cp['id']=='HW002BH-64GiB-prepared-metrics-v2-unreleased','Wrong authority checkpoint')
 for path in ('README.md','plan/STATUS.json','plan/ROADMAP.md','plan/INITIAL_TASK_PROMPT.txt',PLAN.relative_to(R).as_posix()):bound(path,cp['bindings'][path])
 pkg=bound(plan['package']['path'],plan['package']['sha256']);need(pkg[:4]==b'\x7fPKG' and len(pkg)==36720,'Package length/shape')
 return pkg
def volume_identity():
 need(os.name=='nt','Windows only');k=ctypes.WinDLL('kernel32',use_last_error=True);root=ctypes.c_wchar_p('E:\\')
 volume=ctypes.create_unicode_buffer(1024);label=ctypes.create_unicode_buffer(261);fs=ctypes.create_unicode_buffer(261)
 serial,maximum,flags=ctypes.c_ulong(),ctypes.c_ulong(),ctypes.c_ulong()
 need(k.GetDriveTypeW(root)==2,'E: must be removable')
 need(k.GetVolumeNameForVolumeMountPointW(root,volume,1024),'Volume GUID unavailable')
 need(k.GetVolumeInformationW(root,label,261,ctypes.byref(serial),ctypes.byref(maximum),ctypes.byref(flags),fs,261),'Volume identity unavailable')
 total,available,free=ctypes.c_ulonglong(),ctypes.c_ulonglong(),ctypes.c_ulonglong()
 need(k.GetDiskFreeSpaceExW(root,ctypes.byref(available),ctypes.byref(total),ctypes.byref(free)),'Volume space unavailable')
 return {'volume_guid':volume.value,'volume_serial':f'{serial.value:08X}','filesystem':fs.value,'volume_bytes':total.value},available.value
class UsbFiles:
 def identity(self):return volume_identity()
 def path(self,name):
  need(name in NAMES.values(),'USB basename outside exact allowlist');p=Path('E:/')/name
  need(not p.is_symlink(),'USB symlink')
  if p.exists():need(not p.stat().st_file_attributes&0x400,'USB reparse point')
  return p
 def exists(self,n):return self.path(n).exists()
 def create(self,n,b):new(self.path(n),b)
 def read(self,n,maximum):
  p=self.path(n);need(p.is_file() and p.stat().st_size<=maximum,'USB bounds')
  with p.open('rb') as f:b=f.read(maximum+1)
  need(len(b)<=maximum,'USB file grew');return b
def stage(plan,approval,expected,io,out):
 pkg=admitted(plan,approval,expected);before,available=io.identity();need(before==USB and available>=67108864+len(pkg)+128,'USB identity/headroom')
 need(not any(io.exists(n) for n in NAMES.values()),'Nonce namespace exists; no replay')
 out=Path(out);out.mkdir(exist_ok=False);new(out/'intent.json',{'action':'stage_once','plan_sha256':expected,'replay_forbidden':True})
 values={'package':pkg,'source':(P/'STOP-SOURCE.bin').read_bytes(),'ready':(P/'READY.bin').read_bytes()}
 for kind in ('package','source','ready'):
  b=values[kind];io.create(NAMES[kind],b);need(io.read(NAMES[kind],len(b))==b,'Staging readback '+kind)
 need(io.identity()[0]==before,'USB identity changed');result={'passed':True,'staged_files':[NAMES[k] for k in values],'USB_identity':before,'no_firmware_access':True,'native_execution':False}
 new(out/'result.json',result);return result
def capture(plan,approval,expected,io,out,owner_xmb):
 admitted(plan,approval,expected);need(owner_xmb is True,'Owner XMB/USB return required')
 before,_=io.identity();need(before==USB,'USB identity');out=Path(out);out.mkdir(exist_ok=False)
 new(out/'intent.json',{'action':'capture_once','plan_sha256':expected,'replay_forbidden':True,'owner_XMB_return':True})
 caps={'ready':64,'source':64,'wait':64,'done':64,'stop':64,'result':8192,'progress':4194304};data={}
 for kind,limit in caps.items():
  if io.exists(NAMES[kind]):data[kind]=io.read(NAMES[kind],limit);new(out/NAMES[kind],data[kind])
 need(io.identity()[0]==before,'USB identity changed')
 for kind,b in data.items():need(io.read(NAMES[kind],caps[kind])==b,'Evidence changed '+kind)
 for kind,local in (('ready','READY.bin'),('source','STOP-SOURCE.bin'),('done','expected-DONE.bin'),('wait','expected-WAIT.bin')):need(data.get(kind)==(P/local).read_bytes(),'Marker missing/differs '+kind)
 need('result' in data and 'progress' in data,'Result/progress absent')
 result=export(data['result'],data['progress'],out/'performance');result.update(capture_read_only=True,USB_identity=before,firmware_access=False)
 new(out/'result.json',result);return result
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['inspect','stage','capture']);a.add_argument('--approval',type=Path);a.add_argument('--approved-plan-sha256');a.add_argument('--owner-xmb-confirmed',action='store_true');x=a.parse_args();plan=json.loads(PLAN.read_text())
 if x.action=='inspect':print(json.dumps({'state':'AWAITING_EXACT_NATIVE_RELEASE_APPROVAL','plan_sha256':sha(canonical(plan)),'USB_or_console_access':False}));return
 need(x.approval and x.approved_plan_sha256,'Exact approval required before USB access');approval=json.loads(x.approval.read_text());admitted(plan,approval,x.approved_plan_sha256)
 out=O/('authorized-stage-v1' if x.action=='stage' else 'native-receipt-v1');io=UsbFiles()
 result=stage(plan,approval,x.approved_plan_sha256,io,out) if x.action=='stage' else capture(plan,approval,x.approved_plan_sha256,io,out,x.owner_xmb_confirmed)
 print(json.dumps(result))
if __name__=='__main__':main()
