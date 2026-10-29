/* Second populated-Lexar64GiB reserve stage; reviewed new-file-only writer; no firmware/raw operations. */
#include "sha256.h"
#include "session.h"
#include "fill_ui_ps3_v1.h"
#ifdef HOST_TEST
#undef BASE_AVAILABLE_BYTES
#define BASE_AVAILABLE_BYTES (66ULL*1024*1024*1024+5ULL*1048576)
#endif
typedef int s32;
#define CHUNK 1048576u
#define LOW (32ULL*CHUNK)
#define HIGH_OFFSET (4294967296ULL+4096ULL)
#define END_OFFSET (HIGH_OFFSET+CHUNK)
#define RESERVE (64ULL*1024*1024*1024)
#define ENOENT ((s32)0x80010006u)
static u8 buffer[CHUNK] __attribute__((aligned(128)));
static u8 rec[8192],readback[8192],small[128],statbuf[128];



static s32 hfd=-1,pfd=-1;static u32 writer_open;
typedef struct {u64 calls,bytes,time_us,min_us,max_us,errors;} PerfStat;
static PerfStat perf_read,perf_write;static u32 perf_active,perf_clock_error;
static u64 perf_origin_us,perf_space_us,perf_read_requested,perf_write_requested,perf_write_start_us;
static void perf_add(PerfStat*s,u64 bytes,u64 requested,s32 rc,u64 a,u64 b){
 u64 elapsed=b>=a?b-a:0;if(b<a)perf_clock_error=1;
 if(bytes>requested){bytes=0;perf_clock_error=1;}
 if(s->bytes>~0ULL-bytes||s->time_us>~0ULL-elapsed){perf_clock_error=1;return;}
 if(!s->calls||elapsed<s->min_us)s->min_us=elapsed;if(elapsed>s->max_us)s->max_us=elapsed;
 s->calls++;s->bytes+=bytes;s->time_us+=elapsed;if(rc)s->errors++;
}
static void perf_pack(u8*p,const PerfStat*s){
 u64 v[6]={s->calls,s->bytes,s->time_us,s->min_us,s->max_us,s->errors};
 for(u32 k=0;k<6;k++)for(u32 j=0;j<8;j++)p[8*k+j]=(u8)(v[k]>>(56-8*j));
}

static u32 last_call,fail_call; static s32 last_rc,fail_rc,cleanup_rc;
#ifndef HOST_TEST
static s32 raw6(u64 n,u64 a,u64 b,u64 c,u64 d,u64 e,u64 f){
 register u64 r3 __asm__("3")=a,r4 __asm__("4")=b,r5 __asm__("5")=c,r6 __asm__("6")=d,r7 __asm__("7")=e,r8 __asm__("8")=f;
 register u64 r9 __asm__("9")=0,r10 __asm__("10")=0,r11 __asm__("11")=n;
 __asm__ volatile("sc":"+r"(r3),"+r"(r4),"+r"(r5),"+r"(r6),"+r"(r7),"+r"(r8),"+r"(r9),"+r"(r10),"+r"(r11)::"r0","r12","lr","ctr","xer","cr0","cr1","cr5","cr6","cr7","memory");return (s32)r3;
}
#else
extern s32 mock_call6(u64,u64,u64,u64,u64,u64,u64);
#define raw6 mock_call6
#endif
static s32 call(u64 n,u64 a,u64 b,u64 c,u64 d,u64 e,u64 f){last_call=(u32)n;last_rc=raw6(n,a,b,c,d,e,f);return last_rc;}
static int equal(const u8 *a,const u8 *b,u32 n){for(u32 i=0;i<n;i++)if(a[i]!=b[i])return 0;return 1;}
static void put32(u8 *p,u32 v){for(u32 i=0;i<4;i++)p[i]=(u8)(v>>(24-8*i));}
static void put64(u8 *p,u64 v){for(u32 i=0;i<8;i++)p[i]=(u8)(v>>(56-8*i));}
static u64 get64(const u8 *p){u64 v=0;for(u32 i=0;i<8;i++)v=(v<<8)|p[i];return v;}
static int allowed_hdd_output(const char*);
static s32 openf(const char *p,u32 mode,s32 *fd){if(mode&&p[5]=='h'&&(mode!=(1|0100|0200)||!allowed_hdd_output(p)))return (s32)0x80010009u;return call(801,(u64)p,mode,(u64)fd,0600,0,0);}
static s32 closef(s32 fd){return call(804,(u64)fd,0,0,0,0,0);}
static s32 syncf(s32 fd){return call(820,(u64)fd,0,0,0,0,0);}
static s32 readf(s32 fd,u8 *p,u64 n,u64 *got){
 u32 measured=perf_active&&fd==hfd;u64 a=measured?fill_screen_now_us():0;
 s32 rc=call(802,(u64)fd,(u64)p,n,(u64)got,0,0);
 if(measured){perf_read_requested+=n;perf_add(&perf_read,*got,n,rc,a,fill_screen_now_us());}return rc;
}
static s32 writef(s32 fd,const u8 *p,u64 n,u64 *got){
 u32 measured=perf_active&&fd==hfd;u64 a=measured?fill_screen_now_us():0;
 s32 rc=call(803,(u64)fd,(u64)p,n,(u64)got,0,0);
 if(measured){perf_write_requested+=n;perf_add(&perf_write,*got,n,rc,a,fill_screen_now_us());}return rc;
}
/* Exact markers only. ENOENT is the only accepted absence. */
static int token(const char *path,const u8 *expected){
 s32 fd=-1,rc=openf(path,0,&fd);if(rc==ENOENT)return 0;if(rc)return -1;
 u64 got=0,extra=0;rc=readf(fd,small,64,&got);u8 tail=0;
 s32 er=rc?rc:readf(fd,&tail,1,&extra),cl=closef(fd);
 if(rc||er||cl||got!=64||extra||!equal(small,expected,64))return -1;return 1;
}
static int kat(void){Sha h;u8 d[32];sha_init(&h);sha_update(&h,(const u8*)"abc",3);sha_finish(&h,d);return equal(d,sha_abc,32);}

/* Integrated first-stage fill. Every HDD output is new and nonce-owned. */
#define GIB (1024ULL*1024*1024)
#define MARGIN (2ULL*GIB)
#define RESERVE_BB (64ULL*GIB)
#define POLL_BYTES (16ULL*CHUNK)
#define PROGRESS_BYTES (256ULL*CHUNK)
#ifdef HOST_TEST
#include "host-controls.h"
#include "host-controls-digest.h"
#define CONTROL_EXPECTED host_controls_digest
#define FILE_LIMIT (2ULL*CHUNK)
#define NEW_LIMIT (5ULL*CHUNK)
#else
#include "controls.h"
#define CONTROL_EXPECTED controls_digest
#define FILE_LIMIT (16ULL*GIB)
#define NEW_LIMIT MAX_NEW_BYTES
#endif
typedef struct {u64 bytes,verified;u8 write_sha[32],read_sha[32];u64 state;u32 status;} FileRecord;
#define MAX_NEW_FILES 8u
static FileRecord files[MAX_NEW_FILES];
#ifdef HOST_TEST
#include "retained-host.h"
#else
#include "retained.h"
#endif
typedef struct {u64 verified;u8 digest[32];u32 state,status;} RetainedRecord;
static RetainedRecord retained_records[OLD_COUNT];
static u64 retained_sample_read,retained_global_read;
static u32 retained_complete,retained_current;

static u64 written,payload_read,control_read,raw0,avail0,raw1,avail1,polls;
static u64 fill_flags;
static u32 file_count,complete_files,phase,sequence,outcome;

static Sha write_hash;static u8 wanted[CHUNK] __attribute__((aligned(128)));
static u8 progress_record[512],control_before[32],control_after[32];
static char file_path[128];
static u32 publish_progress(u32);
#include "fill_io_ui_v1.h"

static u32 length(const char*p){u32 n=0;while(p[n])n++;return n;}
static void path_for(u32 index){
 u32 n=length(owned_prefix);for(u32 i=0;i<n;i++)file_path[i]=owned_prefix[i];
 file_path[n++]=(char)('0'+index/10);file_path[n++]=(char)('0'+index%10);
 const char suffix[]=".bin";for(u32 i=0;i<sizeof suffix;i++)file_path[n+i]=suffix[i];
}
static u64 seeded_word(u64 seed,u32 index,u64 offset){
 u64 x=seed^(((u64)index<<32)|(offset>>3));x+=0x9e3779b97f4a7c15ULL;
 x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);
}
static void pattern(u8*p,u32 size,u32 index,u64 offset){
 for(u32 j=0;j<size;j+=8){u64 x=seeded_word(pattern_seed,index,offset+j);for(u32 k=0;k<8;k++)p[j+k]=(u8)(x>>(56-8*k));}
}
static u32 poll_stop(void){
 u32 ui=ui_tick(0);if(ui)return ui;polls++;int state=token("/dev_usb000/HDD2TB-BH-bab693d274eed6a0.STOP",stop_marker);
 if(state<0)return 60;if(state==1){fill_flags|=4096;outcome=3;return 61;}return 0;
}
static u32 space_bb(u64*first,u64*available){
 *first=*available=0;if(call(840,(u64)"/dev_hdd0",(u64)first,(u64)available,0,0,0))return 40;
 if(*first!=BASE_RAW_BYTES||*first>2048408248320ULL||*available>*first)return 41;
 if(*available<RESERVE_BB)return 43;return 0;
}
static u32 publish_progress(u32 status){
 u32 ui=ui_tick(1);if(ui&&!status)return ui;
 if(sequence>=8192)return 51;
 if(perf_active){u64 rr=0,aa=0;u32 rc=space_bb(&rr,&aa);if(rc&&!status)return rc;if(!rc){raw1=rr;avail1=aa;perf_space_us=fill_screen_now_us()-perf_origin_us;}}
 for(u32 i=0;i<512;i++)progress_record[i]=0;
 const char magic[]="HDD2TB-BH-PROGRESS-v2";for(u32 i=0;i<sizeof magic-1;i++)progress_record[i]=(u8)magic[i];
 for(u32 i=0;i<32;i++)progress_record[32+i]=session_marker[32+i];
 put32(progress_record+64,2);put32(progress_record+68,phase);put64(progress_record+72,written);
 put64(progress_record+80,payload_read);put64(progress_record+88,file_count?files[file_count-1].bytes:0);
 put64(progress_record+96,avail1);put32(progress_record+104,sequence);put32(progress_record+108,file_count?file_count-1:0xffffffffu);
 put32(progress_record+112,complete_files);put32(progress_record+116,status);put64(progress_record+120,NEW_LIMIT);
 put64(progress_record+128,RESERVE_BB);put64(progress_record+136,MARGIN);put64(progress_record+144,fill_flags);
 put32(progress_record+152,last_call);put32(progress_record+156,(u32)last_rc);
 put32(progress_record+160,ui_state.eta_kind);put32(progress_record+164,phase);put64(progress_record+168,ui_state.eta_seconds);put64(progress_record+176,ui_state.bytes_per_second);put64(progress_record+184,ui_updates);put32(progress_record+192,ui_start_confirmed);put32(progress_record+196,ui_error);put64(progress_record+200,retained_global_read);put32(progress_record+208,retained_complete);put32(progress_record+212,retained_current);put64(progress_record+216,retained_sample_read);
 put64(progress_record+224,perf_active?fill_screen_now_us()-perf_origin_us:0);put64(progress_record+232,raw1);put64(progress_record+240,perf_space_us);
 put32(progress_record+248,2);put32(progress_record+252,perf_clock_error);perf_pack(progress_record+256,&perf_read);perf_pack(progress_record+304,&perf_write);
 put64(progress_record+352,2048408248320ULL);put64(progress_record+368,perf_read_requested);put64(progress_record+376,perf_write_requested);put64(progress_record+392,perf_write_start_us);put64(progress_record+400,1000000ULL);
 Sha hash;sha_init(&hash);sha_update(&hash,progress_record,480);sha_finish(&hash,progress_record+480);
 u64 got=0;s32 rc=writef(pfd,progress_record,512,&got),sy=syncf(pfd);
 if(rc||sy||got!=512)return 50;sequence++;return 0;
}
static u32 close_hdd(void){
 u32 status=0;if(hfd<0)return 0;
 if(writer_open){
  s32 sy=syncf(hfd);if(sy){cleanup_rc=sy;status=26;}
  sha_finish(&write_hash,files[file_count-1].write_sha);
 }
 s32 cl=closef(hfd);if(cl){cleanup_rc=cl;if(!status)status=27;}
 if(writer_open&&!status)files[file_count-1].state|=1;
 hfd=-1;writer_open=0;return status;
}
static u32 verify_file(u32 index,u32 global){
 FileRecord*f=files+index;path_for(index);if(openf(file_path,0,&hfd))return 20;writer_open=0;
 for(u32 i=0;i<128;i++)statbuf[i]=0xa5;
 if(call(809,(u64)hfd,(u64)statbuf,0,0,0,0)||get64(statbuf+36)!=f->bytes)return 21;
 for(u32 i=52;i<128;i++)if(statbuf[i]!=0xa5)return 21;
 u64 at=0,got=0;Sha hash;u8 digest[32];sha_init(&hash);f->verified=0;
 while(at<f->bytes){
  if(!(at&(POLL_BYTES-1))){u32 rc=poll_stop();if(rc)return rc;}
  u32 request=(u32)(f->bytes-at>CHUNK?CHUNK:f->bytes-at);got=0;
  if(readf(hfd,buffer,request,&got)||got!=request)return 22;
  pattern(wanted,request,index,at);if(!equal(buffer,wanted,request))return 24;
  sha_update(&hash,buffer,request);at+=request;payload_read+=request;f->verified=at;u32 ui=ui_tick(0);if(ui)return ui;
  if(!(payload_read&(PROGRESS_BYTES-1))){u32 rc=publish_progress(0);if(rc)return rc;}
 }
 got=~0ULL;if(readf(hfd,buffer,1,&got)||got)return 23;
 sha_finish(&hash,digest);if(!equal(digest,f->write_sha,32))return 24;
 for(u32 i=0;i<32;i++)f->read_sha[i]=digest[i];
 u32 closed=close_hdd();if(closed)return closed;f->state|=global?4:2;return 0;
}

static int allowed_hdd_output(const char*p){
 u32 n=length(owned_prefix);for(u32 i=0;i<n;i++)if(p[i]!=owned_prefix[i])return 0;
 if(p[n]<'0'||p[n]>'9'||p[n+1]<'0'||p[n+1]>'9')return 0;
 u32 index=(u32)(p[n]-'0')*10+(u32)(p[n+1]-'0');
 const char*tail=".bin";for(u32 i=0;i<5;i++)if(p[n+2+i]!=tail[i])return 0;return index<MAX_NEW_FILES;
}
static void retained_pattern(u8*p,u32 n,u32 index,u64 at){
 for(u32 j=0;j<n;j+=8){u64 x=seeded_word(retained_seed,index,at+j);for(u32 k=0;k<8;k++)p[j+k]=(u8)(x>>(56-8*k));}
}
static u32 retained_seek(u64 at){u64 actual=~0ULL;if(call(818,(u64)hfd,at,0,(u64)&actual,0,0)||actual!=at)return 94;return 0;}
static u32 verify_retained(u32 index,u32 full){
 if(index>=OLD_COUNT)return 92;retained_current=index;const RetainedSpec*a=retained_specs+index;
 RetainedRecord*f=retained_records+index;u32 status=poll_stop();if(status)return status;
 if(openf(a->path,0,&hfd))return 92;writer_open=0;
 for(u32 i=0;i<128;i++)statbuf[i]=0xa5;
 if(call(809,(u64)hfd,(u64)statbuf,0,0,0,0)||get64(statbuf+36)!=a->bytes)return 93;
 for(u32 i=52;i<128;i++)if(statbuf[i]!=0xa5)return 93;
 Sha hash;sha_init(&hash);u8 digest[32];u64 got=0;
 if(full){
  if(retained_seek(0))return 94;f->verified=0;
  for(u64 at=0;at<a->bytes;){
   if(!(at&(POLL_BYTES-1))){status=poll_stop();if(status)return status;}
   u32 n=(u32)(a->bytes-at>CHUNK?CHUNK:a->bytes-at);got=0;
   if(readf(hfd,buffer,n,&got)||got!=n)return 95;
   retained_pattern(wanted,n,a->index,at);if(!equal(buffer,wanted,n))return 96;
   sha_update(&hash,buffer,n);at+=n;f->verified=at;retained_global_read+=n;
   status=ui_tick(0);if(status)return status;
   if(!(retained_global_read&(PROGRESS_BYTES-1))){status=publish_progress(0);if(status)return status;}
  }
  sha_finish(&hash,digest);if(!equal(digest,a->sha,32))return 98;
  for(u32 i=0;i<32;i++)f->digest[i]=digest[i];f->state|=2;retained_complete++;
 }else{
  u64 offsets[3]={0,4294967296ULL-32768,a->bytes-65536};
#ifdef HOST_TEST
  offsets[1]=CHUNK/2-32768;
#endif
  for(u32 k=0;k<3;k++){
   if(offsets[k]>a->bytes-65536)return 93;
   if(retained_seek(offsets[k]))return 94;got=0;
   if(readf(hfd,buffer,65536,&got)||got!=65536)return 95;
   retained_pattern(wanted,65536,a->index,offsets[k]);if(!equal(buffer,wanted,65536))return 96;
   retained_sample_read+=65536;status=ui_tick(0);if(status)return status;
  }f->state|=1;
 }
 if(retained_seek(a->bytes))return 94;got=~0ULL;if(readf(hfd,buffer,1,&got)||got)return 97;
 return close_hdd();
}

static u32 check_controls(u8*aggregate){
 Sha manifest;sha_init(&manifest);
 for(u32 index=0;index<16;index++){
  const Asset*a=assets+index;u32 stop=poll_stop();if(stop)return stop;
  if(openf(a->path,0,&hfd))return 30;writer_open=0;
  for(u32 i=0;i<128;i++)statbuf[i]=0xa5;
  if(call(809,(u64)hfd,(u64)statbuf,0,0,0,0)||get64(statbuf+36)!=a->size)return 31;
  for(u32 i=52;i<128;i++)if(statbuf[i]!=0xa5)return 31;
  Sha hash;u8 digest[32],size[8];u64 at=0,got=0;sha_init(&hash);
  while(at<a->size){
   if(!(at&(POLL_BYTES-1))){stop=poll_stop();if(stop)return stop;}
   u32 request=(u32)(a->size-at>CHUNK?CHUNK:a->size-at);got=0;
   if(readf(hfd,buffer,request,&got)||got!=request)return 32;
   sha_update(&hash,buffer,request);at+=request;control_read+=request;u32 ui=ui_tick(0);if(ui)return ui;
  }
  got=~0ULL;if(readf(hfd,buffer,1,&got)||got)return 33;
  sha_finish(&hash,digest);if(!equal(digest,a->sha,32))return 34;
  u32 closed=close_hdd();if(closed)return closed;
  put64(size,a->size);sha_update(&manifest,(const u8*)a->path,length(a->path)+1);sha_update(&manifest,size,8);sha_update(&manifest,digest,32);
 }
 sha_finish(&manifest,aggregate);return equal(aggregate,CONTROL_EXPECTED,32)?0:35;
}
static u32 wait_receipt(void){
 s32 fd=-1;if(openf("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-WAIT.bin",1|0100|0200,&fd))return 52;
 u64 got=0;s32 rc=writef(fd,wait_marker,64,&got),sy=syncf(fd),cl=closef(fd);
 if(rc||sy||cl||got!=64)return 52;
 return token("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-WAIT.bin",wait_marker)==1?0:52;
}
static u32 work_bb(void){
 if(!kat())return 10;fill_flags|=2;
 u32 status=space_bb(&raw0,&avail0);if(status)return status;
 if(avail0+64ULL*CHUNK<BASE_AVAILABLE_BYTES||avail0>BASE_AVAILABLE_BYTES+64ULL*CHUNK)return 42;
 raw1=raw0;avail1=avail0;fill_flags|=4;phase=1;control_read_base=control_read;
 status=check_controls(control_before);if(status)return status;fill_flags|=8;
 phase=9;for(u32 i=0;i<OLD_COUNT;i++){status=verify_retained(i,0);if(status){retained_records[i].status=status;return status;}}
 phase=1;
 status=publish_progress(0);if(status)return status;status=wait_receipt();if(status)return status;fill_flags|=16;
 status=ui_wait_start();if(status)return status;
 while(written<NEW_LIMIT){
  status=poll_stop();if(status)return status;
  u64 available_before=0,first=0;status=space_bb(&first,&available_before);if(status)return status;
  if(available_before<RESERVE_BB+MARGIN+CHUNK){outcome=1;break;}
  if(written>NEW_LIMIT-CHUNK)return 44;
  if(hfd<0){
   if(file_count>=MAX_NEW_FILES){outcome=2;break;}
   path_for(file_count);if(openf(file_path,1|0100|0200,&hfd))return 45;
   writer_open=1;file_count++;sha_init(&write_hash);phase=2;
   status=space_bb(&first,&available_before);if(status)return status;
   if(available_before<RESERVE_BB+MARGIN+CHUNK){outcome=1;break;}
  }
  FileRecord*f=files+file_count-1;if(f->bytes>FILE_LIMIT-CHUNK)return 44;
  pattern(buffer,CHUNK,file_count-1,f->bytes);u64 got=0;s32 rc=writef(hfd,buffer,CHUNK,&got);
  if(got>CHUNK)return 46;
  if(got){sha_update(&write_hash,buffer,(u32)got);f->bytes+=got;written+=got;}
  if(rc||got!=CHUNK)return 47;
  status=space_bb(&raw1,&avail1);if(status)return status;
  if(available_before>avail1&&available_before-avail1>CHUNK+16ULL*CHUNK)return 48;
  if(!(written&(PROGRESS_BYTES-1))){status=publish_progress(0);if(status)return status;}
  if(f->bytes==FILE_LIMIT){
   status=close_hdd();if(status)return status;phase=3;status=publish_progress(0);if(status)return status;
   status=verify_file(file_count-1,0);if(status)return status;complete_files++;phase=2;
  }
 }
 if(!outcome)outcome=2;fill_flags|=32;
 if(hfd>=0){
  status=close_hdd();if(status)return status;phase=3;status=publish_progress(0);if(status)return status;
  status=verify_file(file_count-1,0);if(status)return status;complete_files++;
 }
 fill_flags|=64;phase=4;global_read_base=payload_read;status=publish_progress(0);if(status)return status;
 for(u32 i=0;i<file_count;i++){status=verify_file(i,1);if(status){files[i].status=status;return status;}}
 for(u32 i=0;i<OLD_COUNT;i++){status=verify_retained(i,1);if(status){retained_records[i].status=status;return status;}}
 fill_flags|=128;phase=5;control_read_base=control_read;status=check_controls(control_after);if(status)return status;fill_flags|=256;
 status=space_bb(&raw1,&avail1);if(status)return status;fill_flags|=512|1024;
 if(avail1<RESERVE_BB)return 43;phase=6;return 0;
}
int native_main(void){
 if(token("/dev_usb000/HDD2TB-BH-bab693d274eed6a0.READY",session_marker)!=1)return 11;fill_flags|=1;
 if(token("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-STOP-SOURCE.bin",stop_marker)!=1)return 11;
 if(token("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-DONE.bin",done_marker)!=0||token("/dev_usb000/HDD2TB-BH-bab693d274eed6a0.STOP",stop_marker)!=0)return 12;
 s32 out=-1;if(openf("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-FILL.bin",1|0100|0200,&out))return 12;
 u32 status=0;if(openf("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-PROGRESS.bin",1|0100|0200,&pfd))status=12;
 else{status=(u32)fill_screen_init();if(!status){ui_active=1;perf_active=1;perf_origin_us=fill_screen_now_us();fill_flags|=16384;status=work_bb();}}
 fail_call=last_call;fail_rc=last_rc;
 u32 closed=close_hdd();if(closed&&!status)status=closed;
 ui_state.status=status;
 if(pfd>=0){phase=status?7:6;u32 progress=publish_progress(status);if(progress&&!status)status=progress;
  s32 rc=closef(pfd);pfd=-1;if(rc){cleanup_rc=rc;if(!status)status=53;}else fill_flags|=2048;}
 if(ui_active){if(!status&&call(141,2000000,0,0,0,0,0))status=91;u32 ended=(u32)fill_screen_end();if(ended&&!status)status=ended;if(!ended)fill_flags|=32768;ui_active=0;}
 put32(rec+4800,2);put32(rec+4804,perf_clock_error);put64(rec+4808,perf_active?fill_screen_now_us()-perf_origin_us:0);put64(rec+4816,raw1);put64(rec+4824,2048408248320ULL);
 perf_pack(rec+4832,&perf_read);perf_pack(rec+4880,&perf_write);put64(rec+4928,perf_read_requested);put64(rec+4936,perf_write_requested);put64(rec+4944,perf_write_start_us);put64(rec+4952,perf_space_us);
 const char magic[]="HDD2TB-BH-FILL-v1";for(u32 i=0;i<sizeof magic-1;i++)rec[i]=(u8)magic[i];
 for(u32 i=0;i<32;i++){rec[32+i]=session_marker[32+i];rec[224+i]=CONTROL_EXPECTED[i];rec[256+i]=control_before[i];rec[288+i]=control_after[i];}
 put32(rec+64,1);put32(rec+68,status);put64(rec+72,fill_flags);put64(rec+80,written);put64(rec+88,payload_read);put64(rec+96,control_read);
 put64(rec+104,complete_files);put64(rec+112,file_count);put64(rec+120,RESERVE_BB);put64(rec+128,MARGIN);put64(rec+136,NEW_LIMIT);
 put64(rec+144,FILE_LIMIT);put64(rec+152,1024ULL*GIB);put64(rec+160,raw0);put64(rec+168,avail0);put64(rec+176,raw1);put64(rec+184,avail1);
 put64(rec+192,polls);put64(rec+200,sequence);put32(rec+208,fail_call);put32(rec+212,(u32)fail_rc);put32(rec+216,(u32)cleanup_rc);put32(rec+220,outcome);
 for(u32 i=0;i<file_count;i++){
  u8*p=rec+512+96*i;FileRecord*f=files+i;put32(p,i);put32(p+4,f->status);put64(p+8,f->bytes);put64(p+16,f->verified);
  for(u32 k=0;k<32;k++){p[24+k]=f->write_sha[k];p[56+k]=f->read_sha[k];}put64(p+88,f->state);
 }

 put64(rec+392,retained_sample_read);put64(rec+400,retained_global_read);put64(rec+408,OLD_TOTAL);put32(rec+416,OLD_COUNT);put32(rec+420,retained_complete);put32(rec+424,MAX_NEW_FILES);
 put64(rec+432,pattern_seed);put64(rec+440,retained_seed);
 for(u32 i=0;i<OLD_COUNT;i++){u8*p=rec+1536+64*i;RetainedRecord*f=retained_records+i;put32(p,retained_specs[i].index);put32(p+4,f->status);put64(p+8,retained_specs[i].bytes);put64(p+16,f->verified);for(u32 j=0;j<32;j++)p[24+j]=f->digest[j];put64(p+56,f->state);}
 u32 gs=0,pre=0,post=0,io=0,ios=0,cmd=0,page=0;int gr=0;fill_screen_status(&gs,&gr,&pre,&post);fill_screen_io(&io,&ios,&cmd,&page);put32(rec+320,ui_error);put32(rec+324,gs);put64(rec+328,ui_updates);put32(rec+336,(u32)gr);put32(rec+340,pre);put32(rec+344,post);put32(rec+348,io);put32(rec+352,ios);put32(rec+356,cmd);put32(rec+360,page);put32(rec+364,ui_start_confirmed);put64(rec+368,ui_state.eta_seconds);put64(rec+376,ui_state.bytes_per_second);put32(rec+384,phase);
 Sha hash;sha_init(&hash);sha_update(&hash,rec,8128);sha_finish(&hash,rec+8128);
 u64 got=0;s32 rc=writef(out,rec,8192,&got),sy=syncf(out),cl=closef(out);out=-1;
 if(rc||sy||cl||got!=8192)return 70;
 if(openf("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-FILL.bin",0,&out))return 71;
 got=0;rc=readf(out,readback,8192,&got);cl=closef(out);out=-1;
 if(rc||cl||got!=8192||!equal(rec,readback,8192))return 72;
 if(openf("/dev_usb000/HDD2TB-BH-bab693d274eed6a0-DONE.bin",1|0100|0200,&out))return 73;
 got=0;rc=writef(out,done_marker,64,&got);sy=syncf(out);cl=closef(out);
 if(rc||sy||cl||got!=64)return 74;return (int)status;
}
