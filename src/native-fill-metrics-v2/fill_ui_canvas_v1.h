#ifndef FILL_UI_CANVAS_V1_H
#define FILL_UI_CANVAS_V1_H
typedef struct {
 unsigned phase,status,simulated;
 unsigned long long written,target,verified,verify_target,available;
 unsigned eta_kind;
 unsigned long long eta_seconds,bytes_per_second;
} FillUiState;
unsigned fill_percent_tenths(unsigned long long done,unsigned long long total);
void fill_ui_canvas(unsigned *pixels,unsigned width,unsigned height,const FillUiState*state);
#endif
