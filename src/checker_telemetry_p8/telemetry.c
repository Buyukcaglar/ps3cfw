#include "telemetry.h"
_Static_assert(sizeof(u32)==4,"u32 width");
_Static_assert(sizeof(tm_record)==128+TM_SLOTS*8,"record ABI");
static u32 gate(tm_record *r,u32 heap) {
 if(!r->lock){r->flags|=TM_NOT_LOCKED;return 0;}
 if(!r->active||r->finished){r->flags|=TM_NOT_ACTIVE;return 0;}
 if(heap!=r->heap){r->flags|=TM_IDENTITY;return 0;}
 return 1;
}
static void count(tm_record *r,volatile u32 *v) {
 if(*v==0xffffffffu)r->flags|=TM_ACCOUNTING;else ++*v;
}
void tm_init(tm_record *r,u32 epoch,u32 heap,u32 base,u32 budget,u32 coverage) {
 u32 i;
 /* Initialization is exclusive, before any allocator wrapper can see r. */
 for(i=0;i<sizeof(*r)/sizeof(u32);++i)((volatile u32*)r)[i]=0;
 r->magic=TM_MAGIC;r->version=TM_VERSION;r->bytes=sizeof(*r);
 r->epoch=epoch;r->heap=heap;r->base=base;r->budget=budget;
 r->coverage=coverage;
 r->backing_status=r->log_open_status=r->log_write_status=r->log_close_status=0xffffffffu;
 if(!coverage)r->flags|=TM_INCOMPLETE_COVERAGE;
 if(!heap||!base||(base&3)||budget<8||budget>0xffffffffu-base)
  r->flags|=TM_BAD_GEOMETRY;
 else r->active=1;
}
u32 tm_try_lock(tm_record *r) {
 u32 expected=0;
 if(__atomic_compare_exchange_n(&r->lock,&expected,1u,0,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED))return 1;
 /* Only the contention observer writes coverage after exclusive init. Keeping
  * it separate avoids racing a non-atomic owner update of r->flags. */
 __atomic_fetch_or(&r->coverage,TM_CONTENTION,__ATOMIC_RELAXED);
 return 0;
}
void tm_unlock(tm_record *r) {
 __atomic_store_n(&r->lock,0u,__ATOMIC_RELEASE);
}
u32 tm_header_address(tm_record *r,u32 heap,u32 p) {
 if(!gate(r,heap))return 0;
 /* Difference comparisons avoid p+N / base+budget overflow. A nonzero result
  * authorizes ONLY one four-byte read; it does not validate the chunk body. */
 if(!p)return 0;
 if((p&3)||p<r->base||p-r->base<8||p-r->base>r->budget) {
  r->flags|=TM_BAD_POINTER;return 0;
 }
 return p-4;
}
static u32 charge(tm_record *r,u32 p,u32 header) {
 u32 n=header&0xfffffffcu;
 if(!tm_header_address(r,r->heap,p))return 0;
 /* Retail free inspects bit1 (allocated) and clears bits0..1 for chunk size.
  * No assumption about malloc usable-byte rounding or a peak field is made. */
 if(!(header&2)||n<8||n>r->budget-(p-r->base-8)) {
  r->flags|=TM_BAD_HEADER;return 0;
 }
 return n;
}
static u32 find(tm_record *r,u32 p,u32 *empty) {
 u32 i,index=(p>>3)&(TM_SLOTS-1);
 *empty=TM_SLOTS;
 for(i=0;i<TM_SLOTS;++i) {
  u32 k=(index+i)&(TM_SLOTS-1),key=r->slots[k].pointer;
  if(key==p)return k;
  if(key==1&&*empty==TM_SLOTS)*empty=k;
  if(!key){if(*empty==TM_SLOTS)*empty=k;break;}
 }
 return TM_SLOTS;
}
void tm_alloc(tm_record *r,u32 heap,u32 request,u32 p,u32 header) {
 u32 size,k,empty;
 if(!gate(r,heap))return;
 count(r,&r->alloc_calls);count(r,&r->events);
 if(request>r->largest_request)r->largest_request=request;
 if(!p){count(r,&r->failed_allocs);
  if(request>r->largest_failed_request)r->largest_failed_request=request;return;}
 size=charge(r,p,header);if(!size)return;
 k=find(r,p,&empty);
 if(k!=TM_SLOTS){r->flags|=TM_DUPLICATE;return;}
 if(empty==TM_SLOTS){r->flags|=TM_TABLE_FULL;return;}
 if(size>r->budget-r->live_bytes){r->flags|=TM_ACCOUNTING;return;}
 r->slots[empty].pointer=p;r->slots[empty].charge=size;
 r->live_bytes+=size;++r->live_count;
 if(r->live_bytes>r->peak_bytes)r->peak_bytes=r->live_bytes;
 if(r->live_count>r->peak_count)r->peak_count=r->live_count;
}
u32 tm_prepare_free(tm_record *r,u32 heap,u32 p) {
 u32 empty,k;
 if(!gate(r,heap)||!p)return 0;
 if(!tm_header_address(r,heap,p))return 0;
 k=find(r,p,&empty);
 if(k==TM_SLOTS){r->flags|=TM_UNKNOWN_FREE;return 0;}
 return p-4;
}
void tm_free(tm_record *r,u32 heap,u32 p,u32 saved_header) {
 u32 empty,k,size;
 if(!gate(r,heap))return;
 count(r,&r->free_calls);count(r,&r->events);
 if(!p){count(r,&r->null_frees);return;}
 k=find(r,p,&empty);
 if(k==TM_SLOTS){r->flags|=TM_UNKNOWN_FREE;return;}
 size=charge(r,p,saved_header);
 if(!size||size!=r->slots[k].charge){r->flags|=TM_BAD_HEADER;return;}
 if(!r->live_count||size>r->live_bytes){r->flags|=TM_ACCOUNTING;return;}
 r->live_bytes-=size;--r->live_count;
 r->slots[k].pointer=1;r->slots[k].charge=0;
}
void tm_finish(tm_record *r,u32 status) {
 if(!gate(r,r->heap))return;
 r->utility_status=status;r->finished=1;r->active=0;
 /* Live chunks may legitimately be reclaimed by whole-heap deletion. Keep
  * their end count/bytes rather than inventing individual free observations. */
}
