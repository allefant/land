#ifdef _PROTOTYPE_
#include <allegro.h>
#include <alleggl.h>
#include <loadpng.h>
#include <stdlib.h>

typedef struct LandDisplayInterface LandDisplayInterface;
typedef struct LandDisplay LandDisplay;

#include "array.h"
#include "image.h"
#include "log.h"

#define LAND_WINDOWED 1
#define LAND_FULLSCREEN 2
#define LAND_OPENGL 4

struct LandDisplayInterface
{
    land_method(void, set, (LandDisplay *self));
    land_method(void, clear, (LandDisplay *self, float r, float g, float b));
    land_method(void, flip, (LandDisplay *self));
    land_method(void, rectangle, (LandDisplay *self, float x, float y, float x_, float y_,
        float r, float g, float b));
    land_method(void, line, (LandDisplay *self, float x, float y, float x_, float y_,
        float r, float g, float b));
    land_method(void, filled_circle, (LandDisplay *self, float x, float y, float x_, float y_,
        float r, float g, float b));
    land_method(void, circle, (LandDisplay *self, float x, float y, float x_, float y_,
        float r, float g, float b));
    land_method(LandImage *, new_image, (LandDisplay *self));
};

struct LandDisplay
{
    LandDisplayInterface *vt;
    int w, h, bpp, hz, flags;
};

#endif /* _PROTOTYPE_ */

#include "display.h"
#include "allegro/display.h"
#include "allegrogl/display.h"

land_array(LandDisplay)

LandDisplay *_land_active_display = NULL;

LandDisplay *land_display_new(int w, int h, int bpp, int hz, int flags)
{
    LandDisplay *self;
    if (flags & LAND_OPENGL)
    {
        LandDisplayAllegroGL *allegrogl = land_display_allegrogl_new(
            w, h, bpp, hz, flags);
        self = &allegrogl->super;
    }
    else
    {
        LandDisplayAllegro *allegro = land_display_allegro_new(
            w, h, bpp, hz, flags);
        self = &allegro->super;
    }

    _land_active_display = self;
    return self;
}

void land_display_set(void)
{
    _land_active_display->vt->set(_land_active_display);
}

void land_display_init(void)
{
    land_log_msg("land_display_init\n");
    land_display_allegro_init();
    land_display_allegrogl_init();
}

void land_clear(float r, float g, float b)
{
    glClearColor(r, g, b, 0);
    glClear(GL_COLOR_BUFFER_BIT);
}

void land_flip(void)
{
    _land_active_display->vt->flip(_land_active_display);
}

void land_rectangle(
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    _land_active_display->vt->rectangle(_land_active_display, x, y, x_, y_, r, g, b);
}

void land_filled_circle(
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    _land_active_display->vt->filled_circle(_land_active_display, x, y, x_, y_, r, g, b);
}

void land_circle(
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    _land_active_display->vt->circle(_land_active_display, x, y, x_, y_, r, g, b);
}

void land_line(
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    _land_active_display->vt->line(_land_active_display, x, y, x_, y_, r, g, b);
}

int land_display_width(void)
{
    LandDisplay *self = _land_active_display;
    return self->w;
}

int land_display_height(void)
{
    LandDisplay *self = _land_active_display;
    return self->h;
}

int land_display_flags(void)
{
    LandDisplay *self = _land_active_display;
    return self->flags;
}

LandImage *land_display_new_image(void)
{
    return _land_active_display->vt->new_image(_land_active_display);
}

