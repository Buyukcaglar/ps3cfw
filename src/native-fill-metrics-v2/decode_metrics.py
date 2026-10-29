"""Strict saved-byte decoder and capacity/performance exporter. No device/network access."""
import argparse,csv,hashlib,json,re,struct
from pathlib import Path
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
G=1024**3;DEV=2048408248320;RAW=1982012665856;CAP=70613204992
NONCE=bytes.fromhex('bab693d274eed6a07a2a6a91b4e1732e0d50fe0ad0fc139cd6cc2fdc4cacfb98')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def u32(b,o):return struct.unpack_from('>I',b,o)[0]
def u64(b,o):return struct.unpack_from('>Q',b,o)[0]
def zeros(b,a,z):need(not any(b[a:z]),f'Nonzero reserved bytes {a}:{z}')
def perf(b,o):
 names=('calls','bytes','time_us','min_us','max_us','errors');s=dict(zip(names,struct.unpack_from('>6Q',b,o)))
 need(s['errors']<=s['calls'],'Error count exceeds calls')
 if s['calls']:need(s['min_us']<=s['max_us'] and s['min_us']*s['calls']<=s['time_us']<=s['max_us']*s['calls'],'Invalid timing range')
 else:need(not any(s.values()),'Counters without calls')
 return s
def capacity(first,available):
 need(0<=available<=first<=DEV,'Invalid capacity')
 used=first-available
 return {'available_bytes':available,'available_GB':available/1e9,'available_GiB':available/G,
  'native_space_first_output_bytes':first,'native_space_first_output_GB':first/1e9,'native_space_first_output_GiB':first/G,
  'reported_used_or_unavailable_bytes':used,'reported_used_or_unavailable_GB':used/1e9,'reported_used_or_unavailable_GiB':used/G,
  'reported_fill_percent_of_native_first_output':100*used/first if first else None,
  'device_bytes':DEV,'device_GB':DEV/1e9,'device_GiB':DEV/G,
  'device_capacity_not_native_available_bytes':DEV-available,'device_capacity_not_native_available_percent':100*(DEV-available)/DEV}
def references(host):
 if host:
  text=(P/'retained-host.h').read_text();rows=[]
  for n,index,sha in re.findall(r'\{"[^"]+",(\d+)ULL,(\d+)u,\{([^}]+)\}\}',text):rows.append((int(index),int(n),bytes(map(int,sha.split(',')))))
  need(len(rows)==3,'Host references missing');return rows
 m=json.loads((R/'observations/HW002BF/final-v16/native-file-manifest.json').read_text())
 return [(x['index'],x['bytes'],bytes.fromhex(x['sha256'])) for x in m['files']]
def parse_receipt(b,host=False):
 need(len(b)==8192 and b[:32]==b'HDD2TB-BH-FILL-v1'.ljust(32,b'\0') and b[32:64]==NONCE,'Receipt identity/length')
 need(hashlib.sha256(b[:8128]).digest()==b[8128:8160],'Receipt checksum');zeros(b,8160,8192)
 need(u32(b,64)==1 and u32(b,424)==8,'Receipt policy version')
 status=u32(b,68);written=u64(b,80);read=u64(b,88);control=u64(b,96);count=u64(b,112);complete=u64(b,104)
 cap=5*1048576 if host else CAP;limit=2*1048576 if host else 16*G;baseline=66*G+5*1048576 if host else 141480378368
 need(tuple(u64(b,x) for x in (120,128,136,144,152))==(64*G,2*G,cap,limit,1024*G),'Wrong reserve/caps')
 need(count<=8 and complete<=count and written<=cap and read<=2*written and u64(b,200)<=8192,'Receipt counters out of bounds')
 need(not written or u32(b,364)==1,'Missing fresh X')
 zeros(b,388,392);zeros(b,428,432);zeros(b,448,512)
 rows=[]
 for i in range(count):
  o=512+96*i;size=u64(b,o+8);verified=u64(b,o+16);state=u64(b,o+88)
  need(u32(b,o)==i and size<=limit and verified<=size and state<=7,'New file bounds')
  rows.append({'index':i,'status':u32(b,o+4),'bytes':size,'verified_bytes':verified,'state':state,'write_sha256':b[o+24:o+56].hex(),'read_sha256':b[o+56:o+88].hex()})
 need(sum(x['bytes'] for x in rows)==written,'New file total');zeros(b,512+96*count,1536)
 refs=references(host);oldtotal=sum(x[1] for x in refs);oldcomplete=u32(b,420)
 need(u32(b,416)==len(refs) and u64(b,408)==oldtotal and oldcomplete<=len(refs),'Retained manifest bounds')
 need(u64(b,392)<=len(refs)*3*65536 and u64(b,400)<=oldtotal,'Retained byte bounds')
 need((u64(b,432),u64(b,440))==(13454103468930160288,14012737469117632661),'Pattern domain')
 old=[]
 for i,(index,size,sha) in enumerate(refs):
  o=1536+64*i;verified=u64(b,o+16);state=u64(b,o+56)
  need(u32(b,o)==index and u64(b,o+8)==size and verified<=size and state<=3,'Retained record bounds')
  old.append({'index':index,'bytes':size,'verified_bytes':verified,'status':u32(b,o+4),'state':state,'sha256':b[o+24:o+56].hex()})
  if not status:need(verified==size and not u32(b,o+4) and state==3 and b[o+24:o+56]==sha,'Retained full hash mismatch')
 zeros(b,1536+64*len(refs),4800)
 need(u32(b,4800)==2 and u32(b,4804)<=1 and u64(b,4816)==u64(b,176) and u64(b,4824)==DEV,'Metrics policy')
 rp=perf(b,4832);wp=perf(b,4880);elapsed=u64(b,4808);write_start=u64(b,4944)
 need(rp['bytes']<=u64(b,4928) and wp['bytes']<=u64(b,4936) and write_start<=elapsed and u64(b,4952)<=elapsed,'Metrics bounds')
 need(wp['bytes']==written,'Write telemetry differs')
 zeros(b,4960,8128)
 if not status:
  need(u64(b,72)==61439 and 0<count<=5 and complete==count and written and not written%1048576 and read==2*written,'Success flags/counts')
  expected=2*sum((2*1048576+7 if i==0 else 32768+i*29) for i in range(16)) if host else 218179456
  need(control==expected and tuple(u32(b,x) for x in (208,212,216))==(840,0,0),'Control/cleanup counters')
  need(u32(b,220) in (1,2) and (u32(b,220)!=2 or written==cap),'Stop reason')
  need(u64(b,160)==RAW==u64(b,176) and abs(u64(b,168)-baseline)<=64*1048576 and 64*G<=u64(b,184)<=u64(b,168),'Space policy')
  if u32(b,220)==1:need(u64(b,184)<66*G+1048576,'Reserve stop missing')
  need(b[224:256]==b[256:288]==b[288:320],'Control hashes differ')
  if not host:need(b[224:256].hex()==json.loads((R/'observations/HW002BA/controls-digest.json').read_text())['digest'],'Wrong control manifest')
  need(oldcomplete==len(refs) and u64(b,400)==oldtotal and u64(b,392)==len(refs)*3*65536,'Incomplete retained reads')
  for i,x in enumerate(rows):
   need(x['status']==0 and x['state']==7 and x['verified_bytes']==x['bytes'] and x['bytes']%1048576==0 and x['write_sha256']==x['read_sha256'],'New full verification')
   if i<count-1:need(x['bytes']==limit,'Short nontail')
  need(not u32(b,4804) and not rp['errors'] and not wp['errors'] and rp['bytes']==read+control+u64(b,392)+u64(b,400),'Read telemetry differs')
  need(u32(b,320)==0 and u32(b,324)==14 and u64(b,328)>0 and u32(b,336)==0 and tuple(u32(b,x) for x in (352,356,360,364))==(33554432,1048576,1024,1),'Graphics teardown')
  need(u64(b,368)==0 and u64(b,376)==0 and u32(b,384)==6 and u64(b,192)>0 and u64(b,200)>0,'Final UI/progress')
 return {'valid_record':True,'passed':status==0,'native_status':status,'host_model':host,'written_bytes':written,'new_payload_read_bytes':read,
  'control_read_bytes':control,'retained_sample_bytes':u64(b,392),'retained_full_read_bytes':u64(b,400),'files':rows,'retained_files':old,
  'progress_records':u64(b,200),'read_syscalls':rp,'write_syscalls':wp,'elapsed_us':elapsed,'write_start_elapsed_us':write_start,
  'metrics_clock_error':u32(b,4804),'read_requested_bytes':u64(b,4928),'write_requested_bytes':u64(b,4936),
  'before_capacity':capacity(u64(b,160),u64(b,168)),'after_capacity':capacity(u64(b,176),u64(b,184))}
def parse_progress(raw,host=False):
 need(len(raw)>0 and len(raw)%512==0 and len(raw)<=4194304,'Progress length');out=[];cap=5*1048576 if host else CAP
 oldtotal=6*1048576 if host else 850899501056
 for i in range(len(raw)//512):
  b=raw[i*512:(i+1)*512]
  need(b[:32]==b'HDD2TB-BH-PROGRESS-v2'.ljust(32,b'\0') and b[32:64]==NONCE and hashlib.sha256(b[:480]).digest()==b[480:],'Progress identity/checksum')
  need(u32(b,64)==2 and u32(b,104)==i and u32(b,248)==2 and u32(b,252)<=1,'Progress version/sequence')
  phase=u32(b,68);need(phase in range(1,10) and u32(b,164)==phase and u32(b,160)<=3,'Progress phase/ETA')
  need((u64(b,120),u64(b,128),u64(b,136))==(cap,64*G,2*G) and u64(b,72)<=cap and u64(b,80)<=2*u64(b,72) and u64(b,200)<=oldtotal,'Progress budget')
  need(u64(b,352)==DEV and u64(b,400)==1000000 and u64(b,240)<=u64(b,224) and u64(b,392)<=u64(b,224),'Progress time units')
  for a,z in ((360,368),(384,392),(408,480)):zeros(b,a,z)
  rp=perf(b,256);wp=perf(b,304)
  need(rp['bytes']<=u64(b,368) and wp['bytes']<=u64(b,376) and wp['bytes']==u64(b,72),'Progress metric bounds')
  control=rp['bytes']-u64(b,80)-u64(b,200)-u64(b,216);need(control>=0,'Read decomposition')
  r={'sequence':i,'phase':phase,'native_status':u32(b,116),'file_index':u32(b,108),'elapsed_us':u64(b,224),
   'elapsed_seconds':u64(b,224)/1e6,'space_sample_elapsed_us':u64(b,240),'written_bytes':u64(b,72),
   'new_payload_read_bytes':u64(b,80),'retained_full_read_bytes':u64(b,200),'retained_sample_bytes':u64(b,216),'control_read_bytes':control,
   'read_requested_bytes':u64(b,368),'write_requested_bytes':u64(b,376),'write_start_elapsed_us':u64(b,392),
   'ETA_kind':u32(b,160),'ETA_seconds':u64(b,168),'UI_recent_operation_bytes_per_second':u64(b,176),'metrics_clock_error':u32(b,252),
   **capacity(u64(b,232),u64(b,96))}
  for key,s in (('read',rp),('write',wp)):
   r.update({key+'_'+k:v for k,v in s.items()});r[key+'_GB']=s['bytes']/1e9;r[key+'_GiB']=s['bytes']/G;r[key+'_cumulative_syscall_MB_per_second']=s['bytes']/s['time_us'] if s['time_us'] else None
  r['written_GB']=r['written_bytes']/1e9;r['written_GiB']=r['written_bytes']/G
  if out:
   prev=out[-1];dt=r['elapsed_us']-prev['elapsed_us'];need(dt>=0,'Clock regression')
   for k in ('written_bytes','new_payload_read_bytes','retained_full_read_bytes','retained_sample_bytes','read_bytes','read_calls','read_time_us','write_bytes','write_calls','write_time_us'):
    need(r[k]>=prev[k],'Counter regression '+k)
   r['window_elapsed_seconds']=dt/1e6;r['window_same_phase']=phase==prev['phase']
   for k in ('read','write'):
    db=r[k+'_bytes']-prev[k+'_bytes'];du=r[k+'_time_us']-prev[k+'_time_us']
    r[k+'_window_application_MB_per_second']=db/dt if dt and r['window_same_phase'] else None
    r[k+'_window_syscall_MB_per_second']=db/du if du and r['window_same_phase'] else None
  else:
   r.update(window_elapsed_seconds=None,window_same_phase=False)
   for k in ('read','write'):r[k+'_window_application_MB_per_second']=r[k+'_window_syscall_MB_per_second']=None
  out.append(r)
 return out
LIMITATIONS=['Filesystem-call timing is not raw SSD throughput; returned bytes include HDD EOF calls in call timing.',
 'Application window rates include pattern generation, SHA, space guards, UI, USB receipts and waits; phase-transition windows are unreported.',
 'Fill percentage uses native first-space-output minus available; includes reserved/unavailable space, not NAND occupancy or exact allocated blocks.',
 'GB=1000000000 bytes; GiB=1073741824 bytes; MB/s=1000000 bytes/second.',
 'Cache state, flash garbage collection and temperature are uncontrolled; no causal optimization claim. Samples are checkpoints, not continuous trace.',
 'Final metrics stop before result receipt publication. Raw monotonic times are elapsed, not UTC.']
def export(receipt,progress,destination,host=False):
 d=parse_receipt(receipt,host);rows=parse_progress(progress,host)
 need(len(rows)==d['progress_records'],'Receipt/progress count differs');last=rows[-1]
 need(last['written_bytes']==d['written_bytes'] and last['new_payload_read_bytes']==d['new_payload_read_bytes'] and last['retained_full_read_bytes']==d['retained_full_read_bytes'],'Final progress counters differ')
 for key in ('read','write'):
  for k,v in d[key+'_syscalls'].items():need(last[key+'_'+k]==v,'Final performance counters differ')
 if d['passed']:need(last['phase']==6 and not last['native_status'] and last['available_bytes']==d['after_capacity']['available_bytes'],'Final success progress missing')
 destination=Path(destination);destination.mkdir(exist_ok=False)
 for n,b in (('result.bin',receipt),('progress.bin',progress)):
  with (destination/n).open('xb') as f:f.write(b)
 data={'schema':'HDD2TB-BH-performance-v2','host_model_not_native':host,'disk':{'model':'Lexar NQ100 2TB','ATA_serial':'<serial>','device_bytes':DEV},
  'limitations':LIMITATIONS,'raw_sha256':{'result.bin':hashlib.sha256(receipt).hexdigest(),'progress.bin':hashlib.sha256(progress).hexdigest()},'receipt':d,'samples':rows}
 with (destination/'performance.json').open('x',encoding='utf8') as f:json.dump(data,f,indent=2);f.write('\n')
 with (destination/'performance.csv').open('x',newline='',encoding='utf8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 with (destination/'UNITS-AND-LIMITATIONS.txt').open('x',encoding='utf8') as f:f.write('\n'.join(LIMITATIONS)+'\n')
 return {'passed':d['passed'],'samples':len(rows),'destination':str(destination),'host_model':host}
def main():
 a=argparse.ArgumentParser();a.add_argument('--receipt',type=Path,required=True);a.add_argument('--progress',type=Path,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args()
 print(json.dumps(export(x.receipt.read_bytes(),x.progress.read_bytes(),x.output)))
if __name__=='__main__':main()
