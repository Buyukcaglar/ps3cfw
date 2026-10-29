/* Standard app-owned GCM framebuffer; no VSH/kernel/process-memory inspection. */
#include <rsx/gcm_sys.h>
#include <sysutil/video.h>
#include <sysutil/sysutil.h>
#include <io/pad.h>
#include <ppu-asm.h>
#include <sys/memory.h>
#include "fill_ui_ps3_v1.h"
extern s32 gcmInitBodyEx(gcmContextData* ATTRIBUTE_PRXPTR*,u32,u32,const void*);
extern s32 sysUtilRegisterCallbackEx(s32,opd32*,void*);
/* SDK sample-sized IO backed by real 1 MiB pages, not aligned ELF BSS. */
#define HOST_IO_BYTES (32u*1048576u)
#define COMMAND_BYTES 1048576u
static sys_mem_addr_t host_io_addr;static unsigned char*host_io;
static gcmContextData*context;static gcmControlRegister*control;
static unsigned *buffers[2],offsets[2],width,height,current,pending,pad_ready,callback_ready;
static volatile unsigned exit_requested;
static u64 timebase_frequency,timebase_origin;
unsigned long long fill_screen_now_us(void){
 u64 ticks;__asm__ volatile("mftb %0":"=r"(ticks));
 if(!timebase_frequency)return 0;ticks-=timebase_origin;
 return (ticks/timebase_frequency)*1000000ULL+(ticks%timebase_frequency)*1000000ULL/timebase_frequency;
}
void fill_screen_sleep(unsigned us){
 register u64 a __asm__("3")=us;register u64 n __asm__("11")=141;
 __asm__ volatile("sc":"+r"(a),"+r"(n)::"r0","r4","r5","r6","r7","r8","r9","r10","r12","lr","ctr","xer","cr0","cr1","cr5","cr6","cr7","memory");
}
static void sysutil_event(u64 status,u64 param,void*user){(void)param;(void)user;if(status==SYSUTIL_EXIT_GAME)exit_requested=1;}
static int wait_flip(void){
 if(!pending)return 0;
 for(unsigned i=0;i<3000;i++){
  if(!gcmGetFlipStatus()){gcmResetFlipStatus();pending=0;return 0;}
  sysUtilCheckCallback();fill_screen_sleep(1000);
 }
 return 81;
}
static unsigned init_step,pre_state,post_state;static int init_rc;
static int checked(unsigned step,int rc){init_step=step;init_rc=rc;return rc;}
void fill_screen_status(unsigned*step,int*rc,unsigned*pre,unsigned*post){*step=init_step;*rc=init_rc;*pre=pre_state;*post=post_state;}
void fill_screen_io(unsigned*addr,unsigned*bytes,unsigned*cmd,unsigned*flags){*addr=host_io_addr;*bytes=host_io_addr?HOST_IO_BYTES:0;*cmd=COMMAND_BYTES;*flags=(unsigned)SYS_MEMORY_PAGE_SIZE_1M;}
int fill_screen_init(void){
 init_step=1;init_rc=0;pre_state=post_state=0xffffffffu;
 register u64 frequency __asm__("3")=0;register u64 number __asm__("11")=147;
 __asm__ volatile("sc":"+r"(frequency),"+r"(number)::"r0","r4","r5","r6","r7","r8","r9","r10","r12","lr","ctr","xer","cr0","cr1","cr5","cr6","cr7","memory");
 if(!frequency||frequency>1000000000ULL){init_rc=-1;return 84;}timebase_frequency=frequency;
 __asm__ volatile("mftb %0":"=r"(timebase_origin));
 /* One bounded app allocation. It stays mapped until process_exit(3), so
    no GPU command can reference an explicitly freed buffer during teardown. */
 host_io_addr=0;if(checked(15,sysMemoryAllocate(HOST_IO_BYTES,SYS_MEMORY_PAGE_SIZE_1M,&host_io_addr)))return 86;
 if(!host_io_addr||(host_io_addr&0xfffffu)){checked(16,-1);return 86;}
 host_io=(unsigned char*)(u64)host_io_addr;
 gcmContextData*ctx ATTRIBUTE_PRXPTR=0;
 if(checked(2,gcmInitBodyEx(&ctx,COMMAND_BYTES,HOST_IO_BYTES,host_io)))return 80;if(!ctx){init_rc=-1;return 80;}context=ctx;
 gcmConfiguration configuration;videoState state;videoResolution resolution;
 /* Primary librsx/mm.c treats this accessor as output-only, with no rc. */
 unsigned char*cfg=(unsigned char*)&configuration;for(unsigned i=0;i<sizeof configuration;i++)cfg[i]=0;
 gcmGetConfiguration(&configuration);checked(3,0);
 if(checked(4,videoGetState(0,0,&state)))return 80;pre_state=state.state;
 /* SDK videoTest accepts state 0 here; do not assume ENABLED==1 before config. */
 if(checked(5,videoGetResolution(state.displayMode.resolution,&resolution)))return 80;
 width=resolution.width;height=resolution.height;checked(6,0);
 if(width<640||width>1920||height<480||height>1080){init_rc=-1;return 80;}
 u32 bytes=width*height*4,aligned=(bytes+63)&~63u;checked(7,0);
 if(configuration.localSize<2*aligned||!configuration.localAddress){init_rc=-1;return 80;}
 videoConfiguration config;unsigned char*p=(unsigned char*)&config;for(unsigned i=0;i<sizeof config;i++)p[i]=0;
 config.resolution=state.displayMode.resolution;config.format=VIDEO_BUFFER_FORMAT_XRGB;config.pitch=width*4;config.aspect=state.displayMode.aspect;
 if(checked(8,videoConfigure(0,&config,0,0)))return 80;
 if(checked(9,videoGetState(0,0,&state)))return 80;post_state=state.state;
 /* Follow SDK sample ordering; flip wait checks actual display progress. */
 for(unsigned i=0;i<2;i++){
  offsets[i]=i*aligned;buffers[i]=(unsigned*)((u64)(unsigned)configuration.localAddress+offsets[i]);
  if(checked(10,gcmSetDisplayBuffer((u8)i,offsets[i],width*4,width,height)))return 80;
 }
 init_step=11;control=gcmGetControlRegister();if(!control){init_rc=-1;return 80;}
 gcmSetFlipMode(GCM_FLIP_VSYNC);gcmResetFlipStatus();current=pending=0;
 if(checked(12,ioPadInit(7))==0)pad_ready=1;else return 82;
 opd32*callback=(opd32*)((u64)sysutil_event+16);
 if(checked(13,sysUtilRegisterCallbackEx(0,callback,0))==0)callback_ready=1;else return 83;
 checked(14,0);return 0;
}
int fill_screen_update(const FillUiState*s){
 if(!context||!control)return 80;int rc=wait_flip();if(rc)return rc;
 fill_ui_canvas(buffers[current],width,height,s);__asm__ volatile("sync":::"memory");
 if(gcmSetFlip(context,(u8)current))return 81;
 u32 offset=0;if(gcmAddressToOffset(context->current,&offset))return 81;
 __asm__ volatile("sync":::"memory");control->put=offset;gcmSetWaitFlip(context);
 pending=1;current^=1;sysUtilCheckCallback();return 0;
}
int fill_screen_buttons(void){
 sysUtilCheckCallback();if(exit_requested)return 2;if(!pad_ready)return 0;
 padInfo2 info;if(ioPadGetInfo2(&info))return 0;
 for(unsigned i=0;i<7;i++)if(info.port_status[i]&1){padData data;if(!ioPadGetData(i,&data)&&data.len>0){
  if(data.button[3]&PAD_CTRL_CIRCLE)return 2;if(data.button[3]&PAD_CTRL_CROSS)return 1;
 }}return 0;
}
int fill_screen_end(void){
 int rc=wait_flip();if(callback_ready){sysUtilUnregisterCallback(0);callback_ready=0;}
 if(pad_ready){ioPadEnd();pad_ready=0;}return rc;
}
unsigned fill_screen_width(void){return width;}
unsigned fill_screen_height(void){return height;}
