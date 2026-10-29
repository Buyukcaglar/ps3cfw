"""Fresh offline-only finalization review authority; no firmware/device operations."""
from pathlib import Path
import datetime,hashlib,json,time
R=Path(__file__).resolve().parents[2];O=R/'analysis/dev006/p13-offline-finalization-v1'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def new(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2);f.write('\n')
status=json.loads((R/'plan/STATUS.json').read_text());parent_path=R/status['current_checkpoint']
assert parent_path.name=='hw002bj-capacity-branch-closed-v2-checkpoint.json'
assert sha(parent_path)=='3e546cc0a79ac9461bfd2f84f9096c5dc3dd12e566f32501cdef09d11e8ef3f7'
parent=json.loads(parent_path.read_text());O.mkdir(exist_ok=False)
new(O/'owner-authorization.json',{'source':'Direct owner current message','quote':'Go ahead with the remaining offline checker memory/cleanup and recovery/update reviews. Keep P13 unchanged for now and continue toward finalizing the 2TB firmware.',
 'client_date':'2026-10-19','client_timezone':'UTC+3','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'offline_checker_coverage_budget_cleanup_review':True,'offline_recovery_update_release_scope_review':True,
 'P13_must_remain_unchanged':True,'no_console_network_or_USB_or_physical_device_or_unique_key_access':True})
start=last=time.monotonic();diff=[]
for i,(n,h) in enumerate(parent['bindings'].items(),1):
 p=(R/n).resolve();assert p.is_relative_to(R) and 'eid_root_key' not in n.lower()
 if sha(p)!=h:diff.append(n)
 if time.monotonic()-last>25:
  print(json.dumps({'authority_checked':i,'total':len(parent['bindings']),'differences':len(diff)}),flush=True);last=time.monotonic()
large=[{'path':x['path'],'bytes':x['bytes'],'actual_bytes':(R/x['path']).stat().st_size,'SIZE_ONLY':True} for x in parent['large_artifacts_not_whole_hashed_here']]
passed=not diff and all(x['bytes']==x['actual_bytes'] for x in large)
new(O/'authority-audit.json',{'passed':passed,'checkpoint':parent_path.relative_to(R).as_posix(),'checkpoint_sha256':sha(parent_path),
 'bindings_checked':len(parent['bindings']),'differences':diff,'large_artifacts_SIZE_ONLY':large,'elapsed_seconds':time.monotonic()-start})
assert passed
for n in ('README.md','plan/ROADMAP.md','plan/STATUS.json','plan/INITIAL_TASK_PROMPT.txt','plan/backlog/PERF001.json'):
 p=O/'initial-roots'/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write((R/n).read_bytes())
new(O/'scope.json',{'offline_only':True,'P13_unchanged':True,'owned_new_namespace':O.relative_to(R).as_posix(),
 'root_edit_allowlist':['README.md','plan/ROADMAP.md','plan/STATUS.json','plan/INITIAL_TASK_PROMPT.txt'],
 'shared_PS3HDDTool_and_PERF001_DR1_untouched':True,'old_consumed_review_generators_not_replayed':True,
 'new_evidence_from_hash_pinned_saved_binaries_and_records_only':True})
print(json.dumps({'admitted':True,'protected_bindings':len(parent['bindings']),'differences':diff,'offline_only':True}),flush=True)
