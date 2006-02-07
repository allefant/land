#ifdef _PROTOTYPE_

#include <allegro.h>
#include "../array.h"
#include "../font.h"
#include "../log.h"

#define GLYPH_TARGET GLYPH_TARGET_ALLEGGL
#include <glyph.h>

land_type(LandFontGlyphKeeper)
{
    struct LandFont super;
    GLYPH_FACE *face;
    GLYPH_REND *rend;
    GLYPH_TEXTURE *texture;
};

#define LAND_FONT_GLYPHKEEPER(_x_) ((LandFontGlyphKeeper *)_x_)

#endif /* _PROTOTYPE_ */

#include "glyphkeeper-alleggl/font.h"

static LandFontInterface *vtable;

LandFont *land_font_glyphkeeper_load(char const *filename, float size)
{
    land_log_msg("land_font_glyphkeeper_load %s %.1f..", filename, size);
    LandFontGlyphKeeper *self = calloc(1, sizeof *self);    
    self->face = gk_load_face_from_file(filename, 0);
    if (self->face)
        land_log_msg_nostamp("success.\n");
    self->rend = gk_create_renderer(self->face, NULL);
    gk_rend_set_size_pixels(self->rend, size, size);
    gk_rend_set_text_color_rgb(self->rend, 0, 0, 0);
    gk_rend_set_text_alpha(self->rend, 255);
    self->texture = gk_create_texture(self->rend, 32, 96);
    self->super.size = size;
    self->super.vt = vtable;
    return &self->super;
}

void land_font_glyphkeeper_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement)
{
    LandFontGlyphKeeper *self = LAND_FONT_GLYPHKEEPER(state->font);
    if (!self)
        return;

    int h = gk_text_height_utf8(self->rend, text);
    int w = gk_text_width_utf8(self->rend, text);

    float x = state->x_pos;
    float y = state->y_pos;
    if (alignement == 1) /* right */
        x -= w;
    else if (alignement == 2) /* center */
        x -= w / 2;
    if (!state->off)
    {
        int red = _land_active_display->color_r * 255;
        int green = _land_active_display->color_g * 255;
        int blue = _land_active_display->color_b * 255;
        int alpha = _land_active_display->color_a * 255;
        gk_rend_set_text_color(self->rend, red, green, blue);
        gk_rend_set_text_alpha(self->rend, alpha);
        int a = gk_rend_height_pixels(self->rend);
        gk_render_line_gl_utf8(self->texture, text, x, y + a);
    }
    state->x = x;
    state->y = y;
    state->w = w;
    state->h = h;
}

void land_font_glyphkeeper_init(void)
{
    land_log_msg("land_font_glyphkeeper_init\n");
    land_alloc(vtable);
    vtable->print = land_font_glyphkeeper_print;
}
