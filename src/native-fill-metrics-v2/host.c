/* Actual integrated writer against bounded in-memory HDD/USB/UI models. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define HOST_TEST 1
#include "main.c"
static u8 data[3][2*CHUNK],result_data[8192],done_data[64],wait_data[64];
static u64 size[3],pos[64],issued,clock_us;static int active[64],kind[64],idx[64],exists_file[3];
static int fault,out_exists,done_exists,wait_exists,progress_exists,control_opens,ready_buttons,ui_calls;
static u64 baseline_available;
static void insist(int v){if(!v){fprintf(stderr,"Invariant fault%d phase%u call%u written%llu\n",fault,phase,last_call,written);exit(2);}}
static s32 error(void){return (s32)0x80010005u;}
static int same(u64 a,const char*b){return !strcmp((const char*)a,b);}
static int admit(int id,int k,int index,u64 fd){insist(!active[id]);active[id]=1;kind[id]=k;idx[id]=index;pos[id]=0;*(s32*)fd=id;return 0;}
int fill_screen_init(void){return fault==8?80:0;}
int fill_screen_update(const FillUiState*s){ui_calls++;insist(!s->simulated&&s->written<=NEW_LIMIT&&s->verified<=s->verify_target);return fault==48&&written?81:0;}
int fill_screen_buttons(void){
 if(phase==8){ready_buttons++;if(fault==27)return 2;if(fault==28)return 1;return ready_buttons<=5?0:1;}
 if(fault==79&&phase==9)return 2;if(fault==80&&phase==4&&retained_global_read>=CHUNK)return 2;
 if(fault==47&&written>=CHUNK)return 2;return 0;
}
int fill_screen_end(void){return fault==49?81:0;}
unsigned long long fill_screen_now_us(void){return clock_us;}
void fill_screen_status(unsigned*s,int*r,unsigned*pre,unsigned*post){*s=14;*r=0;*pre=*post=0;}
void fill_screen_io(unsigned*a,unsigned*b,unsigned*c,unsigned*d){*a=0x20000000;*b=33554432;*c=1048576;*d=1024;}
void fill_screen_sleep(unsigned us){(void)us;insist(0);}
s32 mock_call6(u64 n,u64 a,u64 b,u64 c,u64 d,u64 e,u64 f){
 (void)e;(void)f;
 if(n==141){insist(a==100000||a==2000000);clock_us+=a;return fault==63?error():0;}
 if(n==801){
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0.READY")){insist(!b);if(fault==1)return ENOENT;return admit(1,1,0,c);}
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0-STOP-SOURCE.bin")){insist(!b);return admit(18,2,0,c);}
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0.STOP")){insist(!b);if(fault==5||(written>=CHUNK&&(fault==46||fault==62))||(phase==8&&(fault==67||fault==68)))return admit(19,2,1,c);return ENOENT;}
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0-DONE.bin")){
   if(!b){if(!done_exists)return ENOENT;return admit(26,3,0,c);}insist(b==193);if(fault==55)return error();insist(!done_exists);done_exists=1;return admit(25,3,0,c);
  }
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0-FILL.bin")){
   if(b==193){if(fault==6||out_exists)return error();out_exists=1;return admit(20,4,0,c);}insist(!b&&out_exists);if(fault==53)return error();return admit(21,4,0,c);
  }
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0-PROGRESS.bin")){insist(b==193&&!progress_exists);if(fault==7)return error();progress_exists=1;return admit(22,5,0,c);}
  if(same(a,"/dev_usb000/HDD2TB-BH-bab693d274eed6a0-WAIT.bin")){
   if(b==193){if(fault==22)return error();insist(!wait_exists);wait_exists=1;return admit(23,6,0,c);}insist(!b&&wait_exists);return admit(24,6,0,c);
  }
  for(int i=0;i<16;i++)if(same(a,assets[i].path)){insist(!b);control_opens++;if(fault==14)return error();return admit(i+2,7,i,c);}
  for(u32 i=0;i<OLD_COUNT;i++)if(same(a,retained_specs[i].path)){insist(!b);if(fault==69||(fault==77&&phase==4))return error();return admit(40+(int)i,9,(int)i,c);}
  char saved_path[128];insist(strlen((const char*)a)<sizeof saved_path);strcpy(saved_path,(const char*)a);
  for(int i=0;i<3;i++){path_for((u32)i);if(!strcmp(saved_path,file_path)){
   if(b==193){if(fault==29||exists_file[i])return error();insist(ui_start_confirmed);exists_file[i]=1;return admit(30+i,8,i,c);}
   insist(!b&&exists_file[i]);if(fault==38)return error();return admit(30+i,8,i,c);
  }}insist(0);
 }
 if(n==840){
  insist(same(a,"/dev_hdd0"));*(u64*)b=BASE_RAW_BYTES;*(u64*)c=baseline_available-issued;
  if(fault==9||(fault==33&&issued))return error();if(fault==10)*(u64*)b-=512;
  if(fault==11)*(u64*)c=BASE_RAW_BYTES+1;if(fault==12)*(u64*)c=RESERVE_BB-1;
  if(fault==13)*(u64*)c=BASE_AVAILABLE_BYTES+65ULL*CHUNK;
  if(fault==34&&issued)*(u64*)c-=18ULL*CHUNK;
  if(fault==35&&issued)*(u64*)c=RESERVE_BB-1;
  if(fault==66){u64 metadata=0;for(int i=0;i<3;i++)metadata+=exists_file[i]?4096:0;*(u64*)c-=metadata;}
  return 0;
 }
 if(n==804){insist(a<64&&active[a]);active[a]=0;if((fault==25&&a==23)||(fault==37&&kind[a]==8)||(fault==52&&a==20)||(fault==58&&a==25)||(fault==61&&a==22))return error();return 0;}
 if(n==820){insist(a<64&&active[a]);if((fault==24&&a==23)||(fault==36&&kind[a]==8)||(fault==51&&a==20)||(fault==57&&a==25)||(fault==60&&a==22))return error();return 0;}
 if(n==818){insist(a<64&&active[a]&&kind[a]==9);if(fault==71)return error();pos[a]=b;*(u64*)d=b;return 0;}
 if(n==809){
  insist(a<64&&active[a]&&(kind[a]==7||kind[a]==8||kind[a]==9));u8*p=(u8*)b;memset(p,0,52);int control=kind[a]==7;if(kind[a]==9){put32(p,0100600);put64(p+36,retained_specs[idx[a]].bytes+(fault==70?1:0));put64(p+44,16384);return 0;}
  if((fault==15&&control)||(fault==39&&!control))return error();put32(p,0100600);put64(p+36,control?assets[idx[a]].size:size[idx[a]]);put64(p+44,16384);
  if(fault==16&&control)put64(p+36,assets[idx[a]].size+1);if((fault==17&&control)||(fault==65&&!control&&phase==4))p[52]=0;return 0;
 }
 if(n==803){
  insist(a<64&&active[a]);*(u64*)d=0;clock_us+=1000000;
  if(a==20){insist(c==8192);memcpy(result_data,(void*)b,8192);*(u64*)d=fault==50?8191:8192;return 0;}
  if(a==22){insist(c==512);if(fault==59)return error();pos[a]+=c;*(u64*)d=c;return 0;}
  if(a==23||a==25){insist(c==64);memcpy(a==23?wait_data:done_data,(void*)b,64);*(u64*)d=((fault==23&&a==23)||(fault==56&&a==25))?63:64;return 0;}
  insist(kind[a]==8&&c==CHUNK&&ui_start_confirmed&&pos[a]==size[idx[a]]);int i=idx[a];insist(pos[a]+c<=2*CHUNK);
  if(fault==30)return error();u64 count=fault==31?c-8:c;memcpy(data[i]+pos[a],(void*)b,(size_t)count);pos[a]+=count;size[i]+=count;issued+=count;*(u64*)d=fault==32?c+1:count;return 0;
 }
 if(n==802){
  insist(a<64&&active[a]);u8*p=(u8*)b;u64 count=0,limit=0;const u8*src=0;clock_us+=100000;
  if(kind[a]<=3||kind[a]==6){limit=64;src=kind[a]==1?session_marker:kind[a]==2?stop_marker:kind[a]==3?done_data:wait_data;}
  else if(kind[a]==4){limit=8192;src=result_data;}
  else if(kind[a]==7){limit=assets[idx[a]].size;if(fault==18)return error();}
  else if(kind[a]==9){limit=retained_specs[idx[a]].bytes;if(fault==72)return error();}
  else{insist(kind[a]==8);limit=size[idx[a]];src=data[(fault==44&&phase==4&&idx[a]>0)?0:idx[a]];if(fault==40)return error();}
  count=pos[a]<limit?limit-pos[a]:0;if(count>c)count=c;
  if(kind[a]==9){retained_pattern(p,(u32)count,retained_specs[idx[a]].index,pos[a]);if(count&&(fault==73||((fault==75||fault==78)&&phase==4)))p[0]^=1;}
  else if(src)memcpy(p,src+(pos[a]<limit?pos[a]:limit),(size_t)count);else for(u64 j=0;j<count;j++)p[j]=(u8)((pos[a]+j)*13+idx[a]*7);
  if(count&&((fault==2&&a==1)||(fault==3&&a==18)||(fault==26&&a==24)||((fault==62||fault==68)&&a==19)||(fault==54&&a==21)||(fault==20&&kind[a]==7)||(fault==45&&kind[a]==7&&phase==5)||(fault==42&&kind[a]==8)))p[0]^=1;
  if(count&&((fault==19&&kind[a]==7)||(fault==41&&kind[a]==8)||(fault==64&&a==21)))count--;
  if(!count&&((fault==21&&kind[a]==7)||(fault==43&&kind[a]==8))){count=1;p[0]=1;}
  if(kind[a]==9&&fault==74&&!count){count=1;p[0]=1;}
  pos[a]+=count;*(u64*)d=count;return 0;
 }insist(0);return error();
}
static void reset(int f){
 memset(&perf_read,0,sizeof perf_read);memset(&perf_write,0,sizeof perf_write);perf_active=perf_clock_error=0;perf_origin_us=perf_space_us=perf_read_requested=perf_write_requested=perf_write_start_us=0;
 fault=f;memset(data,0,sizeof data);memset(size,0,sizeof size);memset(pos,0,sizeof pos);memset(active,0,sizeof active);memset(exists_file,0,sizeof exists_file);
 memset(retained_records,0,sizeof retained_records);retained_sample_read=retained_global_read=0;retained_complete=retained_current=0;retained_specs[0].sha[0]=72;if(f==76)retained_specs[0].sha[0]^=1;
 memset(files,0,sizeof files);memset(rec,0,sizeof rec);memset(readback,0,sizeof readback);memset(&ui_eta,0,sizeof ui_eta);memset(&ui_state,0,sizeof ui_state);memset(control_before,0,32);memset(control_after,0,32);
 written=payload_read=control_read=raw0=avail0=raw1=avail1=polls=fill_flags=0;file_count=complete_files=phase=sequence=outcome=0;hfd=pfd=-1;writer_open=0;
 ui_last=ui_updates=global_read_base=control_read_base=0;ui_active=ui_error=ui_start_confirmed=ui_last_button=0;ui_previous_phase=0xffffffffu;
 issued=clock_us=0;out_exists=wait_exists=progress_exists=control_opens=ready_buttons=ui_calls=0;done_exists=fault==4;if(done_exists)memcpy(done_data,done_marker,64);
 last_call=fail_call=0;last_rc=fail_rc=cleanup_rc=0;baseline_available=BASE_AVAILABLE_BYTES;
}
int main(void){
 int expected[]={0,11,11,11,12,12,12,12,80,40,41,41,43,42,30,31,31,31,32,32,34,33,52,52,52,52,52,61,62,45,47,47,46,40,48,43,26,27,20,21,22,22,24,23,24,34,61,61,81,81,70,70,70,71,72,73,74,74,74,50,50,53,60,91,72,21,0,61,60,92,93,94,95,96,97,96,98,92,96,61,61};
 printf("{\"passed\":true,\"cases\":[");
 for(int f=0;f<81;f++){
  reset(f);int status=native_main();if(status!=expected[f])fprintf(stderr,"Expected%d actual%d fault%d\n",expected[f],status,f);insist(status==expected[f]);for(int j=0;j<64;j++)insist(!active[j]);insist(issued<=5ULL*CHUNK);
  if(!f)insist(written==5ULL*CHUNK&&payload_read==10ULL*CHUNK&&complete_files==3&&file_count==3&&ui_start_confirmed&&ui_updates&&fill_flags==61439&&done_exists&&perf_write.bytes==written&&perf_write.calls==5&&perf_write.time_us==5000000ULL&&perf_read.bytes==control_read+payload_read+retained_sample_read+retained_global_read&&retained_complete==OLD_COUNT&&retained_global_read==OLD_TOTAL);
  if(f==27||f==28||f==29)insist(!issued);
  printf("%s{\"fault\":%d,\"status\":%d,\"written\":%llu}",f?",":"",f,status,issued);
 }
 reset(0);insist(native_main()==0);printf("],\"case_count\":81,\"success_record_hex\":\"");for(unsigned i=0;i<8192;i++)printf("%02x",rec[i]);puts("\",\"memory_only\":true,\"all_handles_closed\":true,\"maximum_HDD_payload_bytes\":5242880}");
}
