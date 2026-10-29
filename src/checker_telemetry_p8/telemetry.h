/* P8 diagnostic component: expanded table, target qualification pending. */
#ifndef HDD2TB_TELEMETRY_H
#define HDD2TB_TELEMETRY_H
typedef unsigned int u32;
#define TM_SLOTS 16384u
#define TM_MAGIC 0x4832544du /* H2TM */
#define TM_VERSION 1u
#define TM_CONTENTION 0x80000000u /* sticky bit in coverage, not owner flags */
enum {
 TM_BAD_GEOMETRY=1u, TM_BAD_POINTER=2u, TM_BAD_HEADER=4u,
 TM_DUPLICATE=8u, TM_TABLE_FULL=16u, TM_UNKNOWN_FREE=32u,
 TM_ACCOUNTING=64u, TM_NOT_LOCKED=128u, TM_NOT_ACTIVE=256u,
 TM_INCOMPLETE_COVERAGE=512u, TM_IDENTITY=1024u
};
typedef struct {volatile u32 pointer,charge;} tm_slot;
typedef struct {
 volatile u32 magic,version,bytes,lock;
 volatile u32 epoch,heap,base,budget;
 volatile u32 flags,active,coverage,finished;
 volatile u32 alloc_calls,free_calls,failed_allocs,null_frees;
 volatile u32 live_bytes,peak_bytes,live_count,peak_count;
 volatile u32 largest_request,largest_failed_request,utility_status,events;
 volatile u32 route,backing_status,log_open_status,log_write_status;
 volatile u32 log_close_status,log_bytes_hi,log_bytes_lo,reserved;
 tm_slot slots[TM_SLOTS];
} tm_record;
/* Caller owns the complete record, initializes it before publishing it, and
 * holds this lock across the ORIGINAL native allocator mutation and observer.
 * Helpers never dereference a console heap pointer or call the allocator. */
void tm_init(tm_record*,u32 epoch,u32 heap,u32 base,u32 budget,u32 coverage);
/* Contention returns immediately: wrapper runs the original operation without
 * observing it and the sticky coverage bit forbids a complete-peak claim. */
u32 tm_try_lock(tm_record*);
void tm_unlock(tm_record*);
u32 tm_header_address(tm_record*,u32 heap,u32 pointer);
void tm_alloc(tm_record*,u32 heap,u32 request,u32 pointer,u32 header);
u32 tm_prepare_free(tm_record*,u32 heap,u32 pointer);
void tm_free(tm_record*,u32 heap,u32 pointer,u32 saved_header);
void tm_finish(tm_record*,u32 status);
#endif
