"""Memory-only fixed USB staging/capture fault tests; never touches E:."""
from pathlib import Path
import json,tempfile,copy
import release as r
import decode_metrics as d
P=Path(__file__).resolve().parent;Q=P/'helper-tests1';Q.mkdir(exist_ok=False)
pkg=(r.R/'diagnostics/HDD2TB-BH-FILL-v2/HDD2TB-BH-FILL.pkg').read_bytes();count=0
class Fake:
 def __init__(self,fail=''):self.data={};self.fail=fail;self.identities=0;self.creates=[];self.reads={}
 def identity(self):
  self.identities+=1;identity=copy.deepcopy(r.USB)
  if self.fail=='identity' or self.fail=='identity_late' and self.identities>1:identity['volume_serial']='BAD'
  return identity,0 if self.fail=='space' else 10**9
 def exists(self,n):return n in self.data
 def create(self,n,b):
  assert n in r.NAMES.values() and n not in self.data
  if self.fail=='create_'+n:raise OSError('mock failure')
  self.data[n]=b;self.creates.append(n)
 def read(self,n,maximum):
  self.reads[n]=self.reads.get(n,0)+1;b=self.data[n]
  if self.fail=='readback' or self.fail=='changed' and self.reads[n]>1:b=b[:-1]
  if len(b)>maximum:raise ValueError('mock bounds')
  return b
def rejects(fn):
 global count
 try:fn()
 except (ValueError,FileExistsError,OSError,KeyError):count+=1;return
 raise AssertionError('Invalid helper state admitted')
admit=r.admitted;io=Fake();rejects(lambda:r.stage({}, {},'bad',io,Q/'unapproved'));assert io.identities==0 and not io.creates
r.admitted=lambda *args:pkg
for i,fail in enumerate(('identity','space','identity_late','readback',*('create_'+r.NAMES[k] for k in ('package','source','ready')))):
 io=Fake(fail);rejects(lambda:r.stage({}, {},'model',io,Q/f'stage-fault{i}'))
io=Fake();io.data[r.NAMES['result']]=b'x';rejects(lambda:r.stage({}, {},'model',io,Q/'existing-namespace'))
io=Fake();result=r.stage({}, {},'model',io,Q/'stage-good');assert result['passed'] and io.creates==[r.NAMES[k] for k in ('package','source','ready')]
rejects(lambda:r.stage({}, {},'model',Fake(),Q/'stage-good'))
base={r.NAMES[k]:(P/f).read_bytes() for k,f in [('ready','READY.bin'),('source','STOP-SOURCE.bin'),('done','expected-DONE.bin'),('wait','expected-WAIT.bin')]}
base[r.NAMES['result']]=(P/'metrics-tests2/result.bin').read_bytes();base[r.NAMES['progress']]=(P/'metrics-tests2/progress.bin').read_bytes()
for i,fault in enumerate(('noowner','identity','changed','missing_done','bad_ready','missing_progress','overcap')):
 io=Fake(fault);io.data=copy.deepcopy(base)
 if fault=='missing_done':del io.data[r.NAMES['done']]
 if fault=='bad_ready':io.data[r.NAMES['ready']]=bytes(64)
 if fault=='missing_progress':del io.data[r.NAMES['progress']]
 if fault=='overcap':io.data[r.NAMES['progress']]=bytes(4194305)
 rejects(lambda:r.capture({}, {},'model',io,Q/f'capture-fault{i}',fault!='noowner'))
io=Fake();io.data=copy.deepcopy(base);r.export=lambda a,b,c:d.export(a,b,c,True)
result=r.capture({}, {},'model',io,Q/'capture-good',True);assert result['passed'] and not io.creates
data=json.loads((Q/'capture-good/performance/performance.json').read_text());last=data['samples'][-1]
assert last['write_GB']==5242880/1e9 and last['written_GiB']==5242880/1073741824 and last['read_GiB']==last['read_bytes']/1073741824
assert 'write_GB' in (Q/'capture-good/performance/performance.csv').read_text().splitlines()[0]
r.admitted=admit
report={'passed':True,'negative_helper_cases':count,'successful_model_stage_and_capture':True,'READY_created_last':True,'stage_replay_refused':True,'capture_read_only':True,'unauthorized_USB_queries':0,'CSV_GB_GiB_columns_verified':True,'all_USB_operations_mocked':True,'native_execution':False}
with (r.O/'release-helper-tests.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))
