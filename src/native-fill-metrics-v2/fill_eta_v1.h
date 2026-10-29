#ifndef FILL_ETA_V1_H
#define FILL_ETA_V1_H
enum { FILL_ETA_CALCULATING=0,FILL_ETA_MEASURED=1,FILL_ETA_STALLED=2,FILL_ETA_COMPLETE=3 };
typedef struct { unsigned long long time_us,done; } FillEtaPoint;
typedef struct {
 unsigned initialized,operation,head,count,kind;
 unsigned long long target,last_time,last_done,seconds,bytes_per_second;
 FillEtaPoint point[32];
} FillEta;
/* Monotonic microseconds, cumulative bytes for this operation, <=1 TiB. */
void fill_eta_update(FillEta*e,unsigned operation,unsigned long long now_us,
 unsigned long long done,unsigned long long target);
unsigned long long fill_eta_minutes(unsigned long long seconds);
#endif
