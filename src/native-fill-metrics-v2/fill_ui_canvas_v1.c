/* Original fixed-size CPU renderer, shared by host previews and native display. */
#include "fill_ui_canvas_v1.h"
#include "fill_eta_v1.h"
static const unsigned char glyphs[36][7]={
 {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},
 {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
 {14,17,16,23,17,17,15},{17,17,17,31,17,17,17},{14,4,4,4,4,4,14},
 {7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
 {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
 {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
 {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
 {17,17,17,17,17,10,4},{17,17,17,21,21,21,10},{17,17,10,4,10,17,17},
 {17,17,10,4,4,4,4},{31,1,2,4,8,16,31},
 {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
 {30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
 {14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},
 {14,17,17,15,1,1,14}
};
unsigned fill_percent_tenths(unsigned long long done,unsigned long long total){
 if(!total)return 0;if(done>=total)return 1000;
 /* Admitted payload <=1 TiB; this multiplication cannot overflow. */
 if(total>1099511627776ULL)return 0;return (unsigned)(done*1000ULL/total);
}
static void rect(unsigned*p,unsigned w,unsigned h,unsigned x,unsigned y,unsigned rw,unsigned rh,unsigned color){
 if(x>=w||y>=h)return;if(rw>w-x)rw=w-x;if(rh>h-y)rh=h-y;
 for(unsigned j=0;j<rh;j++)for(unsigned i=0;i<rw;i++)p[(y+j)*w+x+i]=color;
}
static unsigned row(char c,unsigned r){
 if(c>='a'&&c<='z')c=(char)(c-'a'+'A');
 if(c>='A'&&c<='Z')return glyphs[c-'A'][r];if(c>='0'&&c<='9')return glyphs[26+c-'0'][r];
 if(c=='.')return r==6?4:0;if(c==':')return r==2||r==5?4:0;
 if(c=='-')return r==3?14:0;if(c=='/')return 1u<<(r<5?r:4);
 if(c=='%'){static const unsigned char percent[7]={25,25,2,4,8,19,19};return percent[r];}
 if(c=='(')return r==0||r==6?2:r==1||r==5?4:8;
 if(c==')')return r==0||r==6?8:r==1||r==5?4:2;return 0;
}
static void draw_text(unsigned*p,unsigned w,unsigned h,unsigned x,unsigned y,unsigned scale,const char*s,unsigned color){
 while(*s){for(unsigned r=0;r<7;r++){unsigned bits=row(*s,r);for(unsigned k=0;k<5;k++)if(bits&(16u>>k))rect(p,w,h,x+k*scale,y+r*scale,scale,scale,color);}x+=6*scale;s++;}
}
static unsigned add(char*p,unsigned at,const char*s){while(*s)p[at++]=*s++;p[at]=0;return at;}
static unsigned number(char*p,unsigned at,unsigned long long value){
 char reverse[24];unsigned n=0;do{reverse[n++]=(char)('0'+value%10);value/=10;}while(value);
 while(n)p[at++]=reverse[--n];p[at]=0;return at;
}
static unsigned decimal(char*p,unsigned at,unsigned long long tenths){at=number(p,at,tenths/10);p[at++]='.';p[at++]=(char)('0'+tenths%10);p[at]=0;return at;}
static unsigned gib(char*p,unsigned at,unsigned long long bytes){at=decimal(p,at,bytes*10ULL/1073741824ULL);return add(p,at," GIB");}
void fill_ui_canvas(unsigned*p,unsigned w,unsigned h,const FillUiState*s){
 if(!p||w<320||h<240||w>1920||h>1080)return;
 unsigned scale=w/400;if(scale<2)scale=2;if(scale>4)scale=4;
 unsigned left=w/12,bw=w-2*left,bh=h/22;if(bh<16)bh=16;
 unsigned white=0xeaf1ff,muted=0xa8bad2,green=0x36d7b7,blue=0x69aaff,bg=0x0b1220,track=0x28364b;
 rect(p,w,h,0,0,w,h,bg);char line[128];unsigned at=0;
 draw_text(p,w,h,left,h/9,scale,"HDD2TB 64 GIB RESERVE TEST",white);
 const char*phase="CHECKING BASELINE";
 if(s->phase==2)phase="WRITING NEW TEST FILES";
 if(s->phase==3)phase="VERIFYING CURRENT FILE";
 if(s->phase==4)phase="VERIFYING ALL TEST FILES";
 if(s->phase==5)phase="CHECKING GAME FILE HASHES";
 if(s->phase==6)phase=s->simulated?"DISPLAY CHECK COMPLETE":"ALL CHECKS COMPLETE";
 if(s->phase==9)phase="CHECKING RETAINED FILLER";
 if(s->phase==8)phase="READY - PRESS X TO START";
 if(s->phase==7)phase=s->status==61?"CANCELLED - FILES RETAINED":"STOPPED - CHECK RESULT";
 draw_text(p,w,h,left,h/5,scale,phase,s->status?0xffc16d:green);
 at=add(line,0,"WRITTEN ");at=gib(line,at,s->written);at=add(line,at," / ");gib(line,at,s->target);
 draw_text(p,w,h,left,h*3/10,scale,line,white);
 unsigned percent=fill_percent_tenths(s->written,s->target);
 rect(p,w,h,left,h*4/10,bw,bh,track);rect(p,w,h,left,h*4/10,bw*percent/1000,bh,green);
 at=decimal(line,0,percent);add(line,at,"% OF CURRENT WRITE TARGET");
 draw_text(p,w,h,left,h*4/10+bh+scale*3,scale,line,white);
 if(s->eta_kind==FILL_ETA_MEASURED||s->eta_kind==FILL_ETA_COMPLETE){
  unsigned long long minutes=fill_eta_minutes(s->eta_seconds);
  at=add(line,0,"REMAINING ");at=number(line,at,minutes/60);at=add(line,at," H ");
  if(minutes%60<10)at=add(line,at,"0");at=number(line,at,minutes%60);add(line,at," MIN");
 }else add(line,0,s->eta_kind==FILL_ETA_STALLED?"REMAINING - WAITING FOR DATA":"REMAINING - CALCULATING...");
 draw_text(p,w,h,left,h*55/100,scale,line,white);
 at=add(line,0,"AVAILABLE ");gib(line,at,s->available);draw_text(p,w,h,left,h*64/100,scale,line,muted);
 unsigned verified=fill_percent_tenths(s->verified,s->verify_target);
 at=add(line,0,"VERIFICATION ");at=decimal(line,at,verified);add(line,at,"%");
 draw_text(p,w,h,left,h*7/10,scale,line,white);rect(p,w,h,left,h*8/10,bw,bh,track);rect(p,w,h,left,h*8/10,bw*verified/1000,bh,blue);
 const char*footer=s->phase==8?"X: START / CIRCLE: CANCEL":s->simulated?"SIMULATED DISPLAY TEST - NO HDD WRITES":"CIRCLE: STOP SAFELY / FILES ARE RETAINED";
 draw_text(p,w,h,left,h*9/10,scale,footer,muted);
}
