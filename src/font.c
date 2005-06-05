#ifdef _PROTOTYPE_

#include <allegro.h>
#define GLYPH_TARGET GLYPH_TARGET_ALLEGGL
#include <glyph.h>
#include "array.h"

land_type(LandFont)
{
    GLYPH_FACE *face;
    GLYPH_REND *rend;
    GLYPH_TEXTURE *texture;

    FONT *allegro_font;

    int size;
};

#endif /* _PROTOTYPE_ */

#include <stdio.h>
#include "font.h"
#include "exception.h"

static float text_x_pos = 0;
static float text_y_pos = 0;
static LandFont *text_font = NULL;
static float text_x = 0;
static float text_y = 0;
static float text_w = 0;
static float text_h = 0;
static int text_off = 0;

static float workaround_bug_size = 16;

land_array(LandFont)

LandFont *land_load_font(char const *filename, int size)
{
    land_new(LandFont, self);
    self->face = gk_load_face_from_file(filename, 0);
    self->rend = gk_create_renderer(self->face, NULL);
    gk_rend_set_size_pixels(self->rend, size, size);
    gk_rend_set_text_color_rgb(self->rend, 0, 0, 0);
    gk_rend_set_text_alpha(self->rend, 255);
    text_font = self;

    self->size = size;

    self->texture = gk_create_texture(self->rend, 32, 96);
    return self;
}

void land_set_font(LandFont *self)
{
    text_font = self;
}

void land_text_size(float sx, float sy)
{
    land_exception("Text sizing currently not implemented, use different fonts instead.");
    //LandFont *self = land_pointer(LandFont, text_font);
    //gk_rend_set_size_pixels(self->rend, sx, sy);

    //workaround_bug_size = sy;
}

void land_text_color(float r, float g, float b, float a)
{
    LandFont *self = text_font;
    gk_rend_set_text_color_rgb(self->rend, r * 255, g * 255, b * 255);
    gk_rend_set_text_alpha(self->rend, a * 255);
}

void land_text_pos(float x, float y)
{
    text_x_pos = x;
    text_y_pos = y;
}

float land_text_x_pos(void)
{
    return text_x_pos;
}

float land_text_y_pos(void)
{
    return text_y_pos;
}

float land_text_x(void)
{
    return text_x;
}

float land_text_y(void)
{
    return text_y;
}

float land_text_width(void)
{
    return text_w;
}

float land_text_height(void)
{
    return text_h;
}

int land_text_state(void)
{
    return text_off;
}

int land_font_height(LandFont *self)
{
    return self->size;
}

void land_text_off(void)
{
    text_off = 1;
}

void land_text_on(void)
{
    text_off = 0;
}

void _print(char const *text, int newline, int alignement)
{
    LandFont *self = text_font;
    if (!self)
        return;
    text_x = text_x_pos;
    text_y = text_y_pos;
    int w = gk_text_width_utf8(self->rend, text);
    int h = gk_text_height_utf8(self->rend, text);
    int a = (gk_face_ascender(self->face) >> 6) * h / workaround_bug_size;
    //int d = gk_face_descender(self->face) >> 6;
    if (alignement == 1) /* right */
        text_x -= w;
    else if (alignement == 2) /* center */
        text_x -= w / 2;
    if (!text_off)
        gk_render_line_gl_utf8(self->texture, text, text_x, text_y + a);
    if (newline)
    {
        text_y_pos = text_y + h;
    }
    else
    {
        text_x_pos = text_x + w;
    }
    text_w = w;
    text_h = h;
}

#define VPRINT \
    char str[1024]; \
    va_list args; \
    va_start(args, text); \
    vsnprintf(str, sizeof str, text, args); \
    va_end(args); \

void land_print(char const *text, ...)
{
    VPRINT
    _print(str, 1, 0);
}

void land_print_right(char const *text, ...)
{
    VPRINT
    _print(str, 1, 1);
}

void land_print_center(char const *text, ...)
{
    VPRINT
    _print(str, 1, 2);
}

void land_write(char const *text, ...)
{
    VPRINT
    _print(str, 0, 0);
}

void land_write_right(char const *text, ...)
{
    VPRINT
    _print(str, 0, 1);
}

void land_write_center(char const *text, ...)
{
    VPRINT
    _print(str, 0, 2);
}
