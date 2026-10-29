"""Build two identical graphics-smoke ELFs and a normal free-NPDRM application."""
import argparse,datetime,hashlib,importlib.util,json,shutil,sys,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[3];P=R/'analysis/dev006/native-fill-64-metrics-v2';A=R/'observations/HW002BH/metrics-v2';D=R/'diagnostics/HDD2TB-BH-FILL-v2'
V=R/'analysis/dev006/native-io-smoke-exit-v7';SDK=R/'tools/psl1ght-reference-20261014/source/ppu/include'
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,R/p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
b=load('builder','analysis/dev006/build_av_exit_fix.py');linker=load('sprx','analysis/dev006/sprxlink_python_v1.py')
CID='UP0001-HD2TB0001_00-HDD2TBBHLONGFILL';assert len(CID)==36
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True);args=ap.parse_args();assert args.attempt.isalnum()
 Q=P/('attempt-'+args.attempt);Q.mkdir(exist_ok=False);snap=Q/'source';snap.mkdir()
 assert not D.exists() and not (A/'build-result.json').exists()
 for n in ('main.c','retained.h','retained-host.h','controls.h','host-controls.h','host-controls-digest.h','fill_io_ui_v1.h','fill_eta_v1.c','fill_eta_v1.h','fill_ui_ps3_v1.c','fill_ui_canvas_v1.c','fill_ui_ps3_v1.h','fill_ui_canvas_v1.h','session.h','start.S','lv2.ld','sha256.h'):shutil.copyfile(P/n,snap/n)
 shutil.copytree(P/'imports',snap/'imports');(Q/'repro').mkdir()
 flags=[b.G/'ppu-gcc.exe','-m64','-mcpu=cell','-std=gnu99','-Os','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-asynchronous-unwind-tables','-nostdlib','-Wall','-Wextra','-Werror','-I'+str(SDK),'-I'+str(snap)]
 reports=[]
 for folder in [Q,Q/'repro']:
  objects=[]
  for name in ('main','fill_ui_ps3_v1','fill_ui_canvas_v1','fill_eta_v1'):
   native_flags=flags+(['-fhosted'] if name=='fill_ui_ps3_v1' else [])
   b.run('compile-'+name,native_flags+['-c',snap/(name+'.c'),'-o',folder/(name+'.o')],folder);objects.append(folder/(name+'.o'))
  b.run('compile-start',flags+['-c',snap/'start.S','-o',folder/'start.o'],folder);objects.insert(0,folder/'start.o')
  for lib in ('libgcm_sys','libsysutil','libio'):
   q=snap/'imports'/lib;inc=['-I'+str(SDK),'-iquote'+str(q)]
   b.run('compile-'+lib+'-exports',[b.G/'ppu-gcc.exe','-m64','-mregnames','-mcpu=cell','-D__ASSEMBLY__']+inc+['-c',q/'exports.S','-o',folder/(lib+'-exports.o')],folder)
   b.run('emit-'+lib+'-header',[b.G/'ppu-gcc.exe','-m32']+inc+['-S',q/'libexport.c','-o',folder/(lib+'-header.S')],folder)
   b.run('compile-'+lib+'-header',[b.G/'ppu-gcc.exe','-m64','-c',folder/(lib+'-header.S'),'-o',folder/(lib+'-header.o')],folder)
   objects.extend([folder/(lib+'-exports.o'),folder/(lib+'-header.o')])
  b.run('link',[b.G/'ppu-ld.exe','-m','elf64ppc','-T',snap/'lv2.ld']+objects+['-o',folder/'display-gnu.elf'],folder)
  data,report=linker.transform(folder/'display-gnu.elf');(folder/'display.elf').write_bytes(data);reports.append(report)
 assert (Q/'display.elf').read_bytes()==(Q/'repro/display.elf').read_bytes()
 shutil.copyfile(Q/'display.elf',P/'display.elf');shutil.copyfile(Q/'repro/display.elf',P/'display-repro.elf')
 b.run('disassembly',[b.G/'ppu-objdump.exe','-d',P/'display.elf'],Q)
 pkg=P/'packagefiles';(pkg/'USRDIR').mkdir(parents=True)
 recipe=['--category','SELF','--compress-data','TRUE','--skip-sections','FALSE','--key-revision','0A','--program-auth-id','1010000001000003','--program-vendor-id','01000002',
 '--program-type','NPDRM','--self-app-version','0001000000000000','--self-fw-version','0003005500000000','--self-add-shdrs','TRUE',
 '--self-ctrl-flags','4000000000000000000000000000000000000000000000000000000000000002',
 '--self-cap-flags','00000000000000000000000000000000000000000000007B0000000100000000','--np-license-type','FREE','--np-app-type','EXEC',
 '--np-content-id',CID,'--np-real-fname','EBOOT.BIN','--encrypt',P/'display.elf',pkg/'USRDIR/EBOOT.BIN']
 b.run('retail-wrapper',[R/'tools/scetool_keys/Release/scetool.exe']+recipe,Q)
 b.run('native-roundtrip',[R/'tools/scetool_keys/Release/scetool.exe','--decrypt',pkg/'USRDIR/EBOOT.BIN',P/'native-roundtrip.elf'],Q)
 xml=ET.parse(V/'sfo.xml')
 for v in xml.getroot().findall('value'):
  if v.get('name')=='APP_VER':v.text='01.16'
  if v.get('name')=='TITLE':v.text='HDD2TB Lexar 64 GiB reserve stage'
 xml.write(P/'sfo.xml',encoding='utf-8',xml_declaration=True)
 b.run('sfo',[sys.executable,'-B',R/'tools/psl1ght-reference-20261014/source/tools/ps3py/sfo.py','--fromxml',P/'sfo.xml',pkg/'PARAM.SFO'],Q)
 shutil.copyfile(V/'packagefiles/ICON0.PNG',pkg/'ICON0.PNG');D.mkdir()
 b.run('pkg',[R/'analysis/dev006/native-io-packager-v1/pkg-relative.exe','--contentid',CID,pkg,D/'HDD2TB-BH-FILL.pkg'],Q)
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'two_GNU_links_and_postprocessing_identical':True,'APP_VER':'01.16','content_id':CID,
 'HDD_new_payload_cap_bytes':70613204992,'simulated_display_check_not_a_fill':False,'sustained_writer_released':False,'accepted_startup_exit3_and_SDK_linker_unchanged':True,
 'new_primary_reference_import_stubs':reports[0],'package_bytes':(D/'HDD2TB-BH-FILL.pkg').stat().st_size,
 'package_sha256':hashlib.sha256((D/'HDD2TB-BH-FILL.pkg').read_bytes()).hexdigest(),'native_display_and_return_pending':True}
 with (A/'build-result.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
if __name__=='__main__':main()
