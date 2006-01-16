#ifdef _PROTOTYPE_

typedef struct LandFontInterface LandFontInterface;
typedef struct LandFont LandFont;
typedef struct LandFontState LandFontState;

#include "array.h"
#include "display.h"

struct LandFontInterface
{
    land_method(void, print, (LandFontState *state, LandDisplay *display, char const *text,
        int alignement));
};

struct LandFont
{
    LandFontInterface *vt;
    int size;
};

struct LandFontState
{
    float x_pos, y_pos;
    LandFont *font;
    float x, y, w, h;
    float off;
};

#endif /* _PROTOTYPE_ */

#include <allegro.h>
#include <stdio.h>
#include "font.h"
#include "exception.h"
#include "main.h"

#include "allegro/font.h"
#include "allegrogl/font.h"
#include "glyphkeeper-alleggl/font.h"

static LandFontState *land_font_state;
static int land_use_glyphkeeper = 1;

void land_font_init(void)
{
    land_font_state = calloc(1, sizeof *land_font_state);
    land_font_allegrogl_init();
    land_font_allegro_init();
    land_font_glyphkeeper_init();
}

void land_set_glyphkeeper(int onoff)
{
    land_log_msg("land_set_glyphkeeper %d\n", onoff);
    land_use_glyphkeeper = onoff;
}

LandFont *land_font_load(char const *filename, float size)
{
    LandFont *self;
    if (land_get_flags() & LAND_OPENGL)
    {
        if (land_use_glyphkeeper && !ustrcmp(get_extension(filename), "ttf"))
            self = land_font_glyphkeeper_load(filename, size);
        else
            self = land_font_allegrogl_load(filename, size);
    }
    else
        self = land_font_allegro_load(filename, size);

    land_font_state->font = self;
    return self;
}

void land_set_font(LandFont *self)
{
    land_font_state->font = self;
}

void land_text_size(float sx, float sy)
{
    land_exception("Text sizing currently not implemented, use different fonts instead.");
    //LandFont *self = land_pointer(LandFont, text_font);
    //gk_rend_set_size_pixels(self->rend, sx, sy);

    //workaround_bug_size = sy;
}

void land_text_pos(float x, float y)
{
    land_font_state->x_pos = x;
    land_font_state->y_pos = y;
}

float land_text_x_pos(void)
{
    return land_font_state->x_pos;
}

float land_text_y_pos(void)
{
    return land_font_state->y_pos;
}

float land_text_x(void)
{
    return land_font_state->x;
}

float land_text_y(void)
{
    return land_font_state->y;
}

float land_text_width(void)
{
    return land_font_state->w;
}

float land_text_height(void)
{
    return land_font_state->h;
}

int land_text_state(void)
{
    return land_font_state->off;
}

int land_font_height(LandFont *self)
{
    return self->size;
}

void land_text_off(void)
{
    land_font_state->off = 1;
}

void land_text_on(void)
{
    land_font_state->off = 0;
}

void _print(char const *str, int newline, int alignement)
{
    land_font_state->font->vt->print(land_font_state, _land_active_display, str, alignement);
    if (newline)
    {
        land_font_state->y_pos = land_font_state->y + land_font_state->h;
    }
    else
    {
        land_font_state->x_pos = land_font_state->x + land_font_state->w;
    }
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
