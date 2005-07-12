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
#define LAND_CLOSE_LINES 8

struct LandDisplayInterface
{
    land_method(void, set, (LandDisplay *self));
    land_method(void, clear, (LandDisplay *self));
    land_method(void, flip, (LandDisplay *self));
    land_method(void, rectangle, (LandDisplay *self, float x, float y, float x_, float y_));
    land_method(void, filled_rectangle, (LandDisplay *self, float x, float y, float x_, float y_));
    land_method(void, line, (LandDisplay *self, float x, float y, float x_, float y_));
    land_method(void, filled_circle, (LandDisplay *self, float x, float y, float x_, float y_));
    land_method(void, circle, (LandDisplay *self, float x, float y, float x_, float y_));
    land_method(LandImage *, new_image, (LandDisplay *self));
    land_method(void, del_image, (LandDisplay *self, LandImage *image));
    land_method(void, color, (LandDisplay *self));
    land_method(void, clip, (LandDisplay *self));
};

struct LandDisplay
{
    LandDisplayInterface *vt;
    int w, h, bpp, hz, flags;

    float color_r, color_g, color_b, color_a;

    int clip_off;
    float clip_x1, clip_y1, clip_x2, clip_y2;
    LandList *clip_stack;
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
    _land_active_display->vt->color(_land_active_display);
    _land_active_display->vt->clip(_land_active_display);
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

void land_color(float r, float g, float b)
{
    LandDisplay *d = _land_active_display;
    d->color_r = r;
    d->color_g = g;
    d->color_b = b;
    _land_active_display->vt->color(_land_active_display);
}

void land_transparency(float a)
{
    LandDisplay *d = _land_active_display;
    d->color_a = a;
    _land_active_display->vt->color(_land_active_display);
}

void land_clip(float x, float y, float x_, float y_)
{
    LandDisplay *d = _land_active_display;
    d->clip_x1 = x;
    d->clip_y1 = y;
    d->clip_x2 = x_;
    d->clip_y2 = y_;
    _land_active_display->vt->clip(_land_active_display);
}

void land_clip_intersect(float x, float y, float x_, float y_)
{
    LandDisplay *d = _land_active_display;
    d->clip_x1 = MAX(d->clip_x1, x);
    d->clip_y1 = MAX(d->clip_y1, y);
    d->clip_x2 = MIN(d->clip_x2, x_);
    d->clip_y2 = MIN(d->clip_y2, y_);
    _land_active_display->vt->clip(_land_active_display);
}

void land_clip_push(void)
{
    LandDisplay *d = _land_active_display;
    int *clip = malloc(5 * sizeof *clip);
    clip[0] = d->clip_x1;
    clip[1] = d->clip_y1;
    clip[2] = d->clip_x2;
    clip[3] = d->clip_y2;
    clip[4] = d->clip_off;
    land_add_list_data(&d->clip_stack, clip);
}

void land_clip_pop(void)
{
    LandDisplay *d = _land_active_display;
    LandListItem *item = d->clip_stack->last;
    land_list_remove_item(d->clip_stack, item);
    int *clip = item->data;
    d->clip_x1 = clip[0];
    d->clip_y1 = clip[1];
    d->clip_x2 = clip[2];
    d->clip_y2 = clip[3];
    d->clip_off = clip[4];
    free(clip);
    free(item);
}

void land_clip_on(void)
{
    LandDisplay *d = _land_active_display;
    d->clip_off = 0;
    _land_active_display->vt->clip(_land_active_display);
}

void land_clip_off(void)
{
    LandDisplay *d = _land_active_display;
    d->clip_off = 1;
    _land_active_display->vt->clip(_land_active_display);
}

void land_unclip(void)
{
    LandDisplay *d = _land_active_display;
    d->clip_x1 = 0;
    d->clip_y1 = 0;
    d->clip_x2 = land_display_width();
    d->clip_y2 = land_display_height();
    d->vt->clip(d);
}

void land_flip(void)
{
    _land_active_display->vt->flip(_land_active_display);
}

void land_rectangle(
    float x, float y, float x_, float y_)
{
    _land_active_display->vt->rectangle(_land_active_display, x, y, x_, y_);
}

void land_filled_rectangle(
    float x, float y, float x_, float y_)
{
    _land_active_display->vt->filled_rectangle(_land_active_display, x, y, x_, y_);
}

void land_filled_circle(
    float x, float y, float x_, float y_)
{
    _land_active_display->vt->filled_circle(_land_active_display, x, y, x_, y_);
}

void land_circle(
    float x, float y, float x_, float y_)
{
    _land_active_display->vt->circle(_land_active_display, x, y, x_, y_);
}

void land_line(
    float x, float y, float x_, float y_)
{
    _land_active_display->vt->line(_land_active_display, x, y, x_, y_);
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

void land_display_del_image(LandImage *image)
{
    return _land_active_display->vt->del_image(_land_active_display, image);
}

