#ifdef _PROTOTYPE_

#include <allegro.h>
#include "../array.h"
#include "../font.h"
#include "../log.h"

land_type(LandFontAllegrogl)
{
    struct LandFont super;
    FONT *font;
};

#define LAND_FONT_ALLEGROGL(_x_) ((LandFontAllegrogl *)_x_)

#endif /* _PROTOTYPE_ */

#include "allegrogl/font.h"
#include <allegro/internal/aintern.h>

static LandFontInterface *vtable;

LandFont *land_font_allegrogl_load(char const *filename, float size)
{
    land_log_msg("land_font_allegrogl_load %s %.1f..", filename, size);
    LandFontAllegrogl *self = calloc(1, sizeof *self);
    PALETTE pal;
    int data = size;
    FONT *temp = load_font(filename, pal, &data);
    FONT_COLOR_DATA *fcd = temp->data;
    select_palette(pal);
    self->font = allegro_gl_convert_allegro_font_ex(temp,
         AGL_FONT_TYPE_TEXTURED, -1,
         bitmap_color_depth(fcd->bitmaps[0]) == 32 ? GL_RGBA8 : GL_ALPHA8);
    self->super.size = text_height(self->font);
    self->super.vt = vtable;
    if (self->font)
        land_log_msg_nostamp("%d success\n", text_height(temp));
    else
        land_log_msg_nostamp("failure\n");
    destroy_font(temp);
    return &self->super;
}

void land_font_allegrogl_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement)
{
    LandFontAllegrogl *self = LAND_FONT_ALLEGROGL(state->font);
    if (!self)
        return;

    int w = text_length(self->font, text);
    int h = state->font->size;

    float x = state->x_pos;
    float y = state->y_pos;
    if (alignement == 1) /* right */
        x -= w;
    else if (alignement == 2) /* center */
        x -= w / 2.0;
    /* To avoid extra anti-aliasing "smear" effect with default viewport. */
    x = (int)x;
    y = (int)y;
    if (!state->off)
    {
        glEnable(GL_TEXTURE_2D);
        allegro_gl_printf_ex(self->font, x, y, 0, "%s", text);
    }
    state->x = x;
    state->y = y;
    state->w = w;
    state->h = h;
}

void land_font_allegrogl_init(void)
{
    land_log_msg("land_font_allegrogl_init\n");
    land_alloc(vtable);
    vtable->print = land_font_allegrogl_print;
}

