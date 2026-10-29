
#define main integrated_main
#include "host-return-fixture.c"
#undef main
int main(void){
 reset(0);s32 fd=-1;
 for(u32 i=0;i<OLD_COUNT;i++)insist(openf(retained_specs[i].path,193,&fd)==(s32)0x80010009u&&fd==-1);
 insist(openf("/dev_hdd0/home/savedata/x",193,&fd)==(s32)0x80010009u);
 insist(openf("/dev_hdd0/tmp/other.bin",193,&fd)==(s32)0x80010009u);
 path_for(8);insist(openf(file_path,193,&fd)==(s32)0x80010009u);
 path_for(0);insist(openf(file_path,2,&fd)==(s32)0x80010009u);
 ui_start_confirmed=1;insist(!openf(file_path,193,&fd));insist(!closef(fd));
 u32 ids[]={0,4,7};u64 offsets[]={0,4294967288ULL,4294967296ULL,17179869176ULL};
 for(u32 seedcase=0;seedcase<2;seedcase++)for(u32 i=0;i<3;i++)for(u32 k=0;k<4;k++){
  u64 seed=seedcase?retained_seed:pattern_seed;u64 v=seeded_word(seed,ids[i],offsets[k]);
  printf("%u %u %llu %016llx\n",seedcase,ids[i],offsets[k],v);
 }return 0;
}
