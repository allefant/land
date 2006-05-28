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
    land_method(void, destroy, (LandFont *self));
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

static LandFontState *land_font_state;

void land_font_init(void)
{
    land_alloc(land_font_state);
    land_font_allegrogl_init();
    land_font_allegro_init();
}

void land_font_exit(void)
{
    land_free(land_font_state);
    land_font_allegro_exit();
    land_font_allegrogl_exit();
}

LandFont *land_font_load(char const *filename, float size)
{
    LandFont *self;
    if (land_get_flags() & LAND_OPENGL)
    {
        self = land_font_allegrogl_load(filename, size);
    }
    else
        self = land_font_allegro_load(filename, size);

    land_font_state->font = self;
    return self;
}

void land_font_destroy(LandFont *self)
{
    self->vt->destroy(self);
}

void land_font_set(LandFont *self)
{
    land_font_state->font = self;
}

//__attribute__((noreturn))
void land_text_size(float sx, float sy)
{
    land_exception("Text sizing currently not implemented, use different fonts instead.");
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

LandFont *land_font_current(void)
{
    return land_font_state->font;
}

void land_text_off(void)
{
    land_font_state->off = 1;
}

void land_text_on(void)
{
    land_font_state->off = 0;
}

static void _print(char const *str, int newline, int alignement)
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

int land_text_get_width(char const *str)
{
    int onoff = land_font_state->off;
    land_font_state->off = 1;
    land_font_state->font->vt->print(land_font_state, NULL, str, 0);
    land_font_state->off = onoff;
    return land_font_state->w;
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
