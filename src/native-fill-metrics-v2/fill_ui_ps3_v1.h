#ifndef FILL_UI_PS3_V1_H
#define FILL_UI_PS3_V1_H
#include "fill_ui_canvas_v1.h"
int fill_screen_init(void);
int fill_screen_update(const FillUiState*state);
int fill_screen_buttons(void);
int fill_screen_end(void);
unsigned fill_screen_width(void);
unsigned fill_screen_height(void);
void fill_screen_sleep(unsigned microseconds);
unsigned long long fill_screen_now_us(void);
void fill_screen_status(unsigned*step,int*rc,unsigned*pre,unsigned*post);
void fill_screen_io(unsigned*addr,unsigned*bytes,unsigned*cmd,unsigned*flags);
#endif
