#include "fill_eta_v1.h"
#define WINDOW_US 30000000ULL
#define MIN_US 3000000ULL
#define MAX_BYTES 1099511627776ULL
unsigned long long fill_eta_minutes(unsigned long long seconds){return seconds/60+(seconds%60!=0);}
static void reset(FillEta*e,unsigned op,unsigned long long now,unsigned long long done,unsigned long long target){
 e->initialized=1;e->operation=op;e->target=target;e->last_time=now;e->last_done=done;
 e->head=0;e->count=1;e->point[0].time_us=now;e->point[0].done=done;
 e->kind=FILL_ETA_CALCULATING;e->seconds=e->bytes_per_second=0;
}
void fill_eta_update(FillEta*e,unsigned op,unsigned long long now,unsigned long long done,unsigned long long target){
 if(!e)return;
 if(!e->initialized||e->operation!=op||e->target!=target||now<e->last_time||done<e->last_done){reset(e,op,now,done,target);}
 e->last_time=now;e->last_done=done;e->seconds=e->bytes_per_second=0;e->kind=FILL_ETA_CALCULATING;
 if(!target||target>MAX_BYTES||done>target)return;
 if(done==target){e->kind=FILL_ETA_COMPLETE;return;}
 /* Drop obsolete speed history; a long pause cannot retain an old fast rate. */
 while(e->count>1&&now-e->point[e->head].time_us>WINDOW_US){e->head=(e->head+1)%32;e->count--;}
 FillEtaPoint*old=&e->point[e->head];
 unsigned long long elapsed=now-old->time_us,bytes=done-old->done;
 if(elapsed>=MIN_US&&elapsed<=WINDOW_US){
  if(!bytes)e->kind=FILL_ETA_STALLED;
  else if(bytes>=1048576ULL){
   /* bytes <=1 TiB: bytes*1e6 fits u64. Ceil division avoids 0-minute promises. */
   unsigned long long rate=bytes*1000000ULL/elapsed;
   if(rate){unsigned long long left=target-done;e->bytes_per_second=rate;e->seconds=left/rate+(left%rate!=0);e->kind=FILL_ETA_MEASURED;}
  }
 }
 /* One sample per second; 32 slots cover the rolling 30-second window. */
 unsigned last=(e->head+e->count-1)%32;
 if(now-e->point[last].time_us>=1000000ULL){
  if(e->count==32){e->head=(e->head+1)%32;e->count--;}
  unsigned next=(e->head+e->count)%32;e->point[next].time_us=now;e->point[next].done=done;e->count++;
 }
}
