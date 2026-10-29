/* Shared second-stage writer UI; all rates use actual cumulative I/O and time. */
#include "fill_ui_ps3_v1.h"
#include "fill_eta_v1.h"
static FillEta ui_eta;static FillUiState ui_state;
static u64 ui_last,ui_updates,global_read_base,control_read_base;
static u32 ui_active,ui_error,ui_previous_phase=0xffffffffu,ui_start_confirmed,ui_last_button;
static u32 poll_stop(void);
static u32 ui_tick(u32 force){
 if(!ui_active)return 0;
 if(phase!=6&&phase!=7){ui_last_button=(u32)fill_screen_buttons();if(ui_last_button==2){fill_flags|=4096;outcome=3;return 61;}}
 u64 now=fill_screen_now_us();
 if(!force&&ui_previous_phase==phase&&now-ui_last<250000ULL)return 0;
 u64 done=0,target=0;u32 operation=phase<<16;
 if(phase==2){done=written;target=NEW_LIMIT;}
 if(phase==3&&file_count){FileRecord*f=files+file_count-1;done=f->verified;target=f->bytes;operation|=file_count;}
 if(phase==4){done=payload_read-global_read_base+retained_global_read;target=written+OLD_TOTAL;}
 if(phase==9){done=retained_sample_read;target=(u64)OLD_COUNT*3*65536;}
 if(phase==1||phase==5){done=control_read-control_read_base;for(u32 i=0;i<16;i++)target+=assets[i].size;}
 ui_state.phase=phase;ui_state.simulated=0;ui_state.written=written;ui_state.target=(phase==4||phase==5||phase==6)?written:NEW_LIMIT;ui_state.available=avail1;
 ui_state.verified=(phase==3||phase==4||phase==5||phase==9)?done:0;ui_state.verify_target=(phase==3||phase==4||phase==5||phase==9)?target:written;
 fill_eta_update(&ui_eta,operation,now,done,target);ui_state.eta_kind=ui_eta.kind;ui_state.eta_seconds=ui_eta.seconds;ui_state.bytes_per_second=ui_eta.bytes_per_second;
 if(phase==6){ui_state.verified=ui_state.verify_target=written+OLD_TOTAL;ui_state.eta_kind=FILL_ETA_COMPLETE;ui_state.eta_seconds=0;}
 int rc=fill_screen_update(&ui_state);if(rc){ui_error=(u32)rc;return (u32)rc;}
 ui_updates++;ui_last=now;ui_previous_phase=phase;return 0;
}
static u32 ui_wait_start(void){
 phase=8;u32 rc=ui_tick(1);if(rc)return rc;rc=publish_progress(0);if(rc)return rc;u32 released=0;
 /* Require a fresh X press after release; a held launch button cannot arm I/O. */
 for(u32 i=0;i<6000;i++){
  rc=poll_stop();if(rc)return rc;u32 button=ui_last_button;
  if(button!=1)released=1;if(button==1&&released){ui_start_confirmed=1;fill_flags|=8192;phase=2;perf_write_start_us=fill_screen_now_us()-perf_origin_us;rc=publish_progress(0);if(rc)return rc;return ui_tick(1);}
  if(call(141,100000,0,0,0,0,0))return 91;
 }return 62;
}
