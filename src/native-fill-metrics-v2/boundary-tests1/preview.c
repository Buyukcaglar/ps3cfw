#include <stdio.h>
#include <stdlib.h>
#include "fill_ui_canvas_v1.h"
#include "fill_eta_v1.h"
int main(int argc,char**argv){
 if(argc!=4)return 2;unsigned w=atoi(argv[1]),h=atoi(argv[2]),mode=atoi(argv[3]);
 if(w<640||w>1920||h<480||h>1080)return 2;unsigned*p=calloc((size_t)w*h,sizeof(unsigned));if(!p)return 2;
 FillUiState s={2,0,1,319243419648ULL,851315785728ULL,0,851315785728ULL,671659405312ULL,FILL_ETA_MEASURED,8183,64*1048576ULL};
 if(mode==4){s.phase=8;s.simulated=0;s.written=0;s.target=70613204992ULL;s.available=141480378368ULL;s.eta_kind=FILL_ETA_CALCULATING;}
 if(mode==5){s.phase=4;s.simulated=0;s.written=70613204992ULL;s.target=s.written;s.available=66ULL*1073741824;s.verified=400ULL*1073741824;s.verify_target=921512706048ULL;s.eta_kind=FILL_ETA_MEASURED;s.eta_seconds=36000;}
 if(mode==1){s.phase=4;s.written=s.target;s.verified=s.target*5/8;s.available=139587039232ULL;s.eta_seconds=3640;}
 if(mode==2)s.eta_kind=FILL_ETA_CALCULATING;
 if(mode==3)s.eta_kind=FILL_ETA_STALLED;
 fill_ui_canvas(p,w,h,&s);printf("P6\n%u %u\n255\n",w,h);
 for(unsigned i=0;i<w*h;i++){unsigned char b[3]={(unsigned char)(p[i]>>16),(unsigned char)(p[i]>>8),(unsigned char)p[i]};fwrite(b,1,3,stdout);}free(p);return 0;
}