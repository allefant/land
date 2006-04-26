#ifdef _PROTOTYPE_

#include <allegro.h>
#include "../array.h"
#include "../font.h"
#include "../log.h"

land_type(LandFontAllegro)
{
    struct LandFont super;
    FONT *font;
};

#define LAND_FONT_ALLEGRO(_x_) ((LandFontAllegro *)_x_)

#endif /* _PROTOTYPE_ */

#include "allegro/font.h"

static LandFontInterface *vtable;

LandFont *land_font_allegro_load(char const *filename, int size)
{
    land_log_msg("land_font_allegr_load %s %d..", filename, size);
    LandFontAllegro *self = calloc(1, sizeof *self);
    self->font = load_font(filename, NULL, NULL);
    self->super.size = text_height(self->font);
    self->super.vt = vtable;
    land_log_msg_nostamp(self->font ? "success\n" : "failure\n"); 
    return &self->super;
}

void land_font_allegro_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement)
{
    LandFontAllegro *self = LAND_FONT_ALLEGRO(state->font);
    if (!self)
        return;

    int w = text_length(self->font, text);
    int h = state->font->size;

    float x = state->x_pos;
    float y = state->y_pos;
    if (alignement == 1) /* right */
        x -= w;
    else if (alignement == 2) /* center */
        x -= w / 2;
    if (!state->off)
        textout_ex(LAND_DISPLAY_ALLEGRO(display)->back, self->font, text, x, y, -1, -1);
    state->x = x;
    state->y = y;
    state->w = w;
    state->h = h;
}

void land_font_allegro_init(void)
{
    land_log_msg("land_font_allegro_init\n");   
    land_alloc(vtable);
    vtable->print = land_font_allegro_print;
}

