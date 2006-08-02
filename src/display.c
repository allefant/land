#ifdef _PROTOTYPE_
#include <allegro.h>
#include <alleggl.h>
#include <stdlib.h>

typedef struct LandDisplayInterface LandDisplayInterface;
typedef struct LandDisplay LandDisplay;

#include "list.h"
#include "image.h"
#include "log.h"
#include "memory.h"

#define LAND_WINDOWED 1
#define LAND_FULLSCREEN 2
#define LAND_OPENGL 4
#define LAND_CLOSE_LINES 8

struct LandDisplayInterface
{
    land_method(void, set, (LandDisplay *self));
    land_method(void, clear, (LandDisplay *self, float r, float g, float b, float a));
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
    land_method(void, polygon, (LandDisplay *self, int n, float *x, float *y));
    land_method(void, filled_polygon, (LandDisplay *self, int n, float *x, float *y));
    land_method(void, plot, (LandDisplay *self, float x, float y));
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

#include "allegro/display.h"
#include "allegrogl/display.h"
#include "image/display.h"

extern LandDisplay *_land_active_display;

#endif /* _PROTOTYPE_ */

#include "display.h"
#include "main.h"

static LandList *_previous = NULL;
LandDisplay *_land_active_display = NULL;

static LandDisplay *_global_image_shortcut_display = NULL;
static LandImage *_global_image = NULL;
static int nested = 0;

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
        self = &allegro->super.super;
    }

    self->clip_x1 = 0;
    self->clip_y1 = 0;
    self->clip_x2 = w;
    self->clip_y2 = h;
    self->clip_off = 0;

    land_display_select(self);

    return self;
}

void land_display_destroy(LandDisplay *self)
{
    if (self == _land_active_display)
        land_display_unselect();

    if (self->clip_stack)
    {
        if (self->clip_stack->count)
            land_log_message("Error: non-empty clip stack in display.\n");
        land_list_destroy(self->clip_stack);
    }
    land_free(self);
}

void land_display_del(LandDisplay *self)
{
    land_display_destroy(self);
}

void land_set_image_display(LandImage *image)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(_global_image_shortcut_display);
    if (nested)
    {
        land_exception("land_set_image_display cannot be nested");
    }
    if (!_global_image_shortcut_display)
    {
        _global_image_shortcut_display = land_display_image_new(image, 0);
    }
    else
    {
        self->bitmap = image->memory_cache;
        self->super.w = land_image_width(image);
        self->super.h = land_image_height(image);
        self->super.bpp = bitmap_color_depth(image->memory_cache);
    }
    _global_image = image;
    land_display_select(_global_image_shortcut_display);
}

void land_unset_image_display(void)
{
    land_display_unselect();
    land_image_prepare(_global_image);
    _global_image = NULL;
}

void land_display_set(void)
{
    _land_active_display->vt->set(_land_active_display);
    _land_active_display->vt->color(_land_active_display);
    _land_active_display->vt->clip(_land_active_display);
    
    if (set_display_switch_mode(SWITCH_BACKGROUND))
        set_display_switch_mode(SWITCH_BACKAMNESIA);
}

LandDisplay *land_display_get(void)
{
    return _land_active_display;
}

void land_display_unset(void)
{
    _land_active_display = NULL;
}

void land_display_init(void)
{
    land_log_message("land_display_init\n");
    _previous = land_list_new();
    land_display_allegro_init();
    land_display_allegrogl_init();
    land_display_image_init();
}

void land_display_exit(void)
{
    land_log_message("land_display_exit\n");
    land_list_destroy(_previous);
    if (_global_image_shortcut_display)
        land_display_destroy(_global_image_shortcut_display);
    land_display_image_exit();
    land_display_allegrogl_exit();
    land_display_allegro_exit();
}

/* This function is dangerous! It will completely halt Land for the passed
 * time in seconds.
 * The function will try to determine how long flipping of the display takes.
 * This can be used to see if the refresh rate is honored (usually because
 * vsync is enabled).
 */
double land_display_time_flip_speed(double howlong)
{
    land_flip();
    double t = land_get_time();
    double t2;
    int i = 0;
    while ((t2 = land_get_time()) < t + howlong)
    {
        land_flip();
        i += 1;
    }
    return i / (t2 - t);
}

void land_display_toggle_fullscreen(void)
{
    LandDisplay *d = _land_active_display;
    d->flags ^= LAND_FULLSCREEN;
    if (d->flags & LAND_FULLSCREEN)
        d->flags &= ~LAND_WINDOWED;
    else
        d->flags |= LAND_WINDOWED;
    land_display_set();
}

void land_clear(float r, float g, float b, float a)
{
    LandDisplay *d = _land_active_display;
    _land_active_display->vt->clear(d, r, g, b, a);
}

void land_color(float r, float g, float b, float a)
{
    LandDisplay *d = _land_active_display;
    d->color_r = r;
    d->color_g = g;
    d->color_b = b;
    d->color_a = a;
    _land_active_display->vt->color(d);
}

void land_get_color(float *r, float *g, float *b, float *a)
{
    LandDisplay *d = _land_active_display;
    *r = d->color_r;
    *g = d->color_g;
    *b = d->color_b;
    *a = d->color_a;
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
    int *clip = land_malloc(5 * sizeof *clip);
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
    land_free(clip);
    land_free(item);
    _land_active_display->vt->clip(_land_active_display);
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

int land_get_clip(float *cx1, float *cy1, float *cx2, float *cy2)
{
    LandDisplay *d = _land_active_display;
    *cx1 = d->clip_x1;
    *cy1 = d->clip_y1;
    *cx2 = d->clip_x2;
    *cy2 = d->clip_y2;
    return !d->clip_off;
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

void land_polygon(int n, float *x, float *y)
{
    _land_active_display->vt->polygon(_land_active_display, n, x, y);
}

void land_filled_polygon(int n, float *x, float *y)
{
    _land_active_display->vt->filled_polygon(_land_active_display, n, x, y);
}

void land_plot(float x, float y)
{
    _land_active_display->vt->plot(_land_active_display, x, y);
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
    LandImage *image = _land_active_display->vt->new_image(_land_active_display);
    return image;
}

void land_display_del_image(LandImage *image)
{
    return _land_active_display->vt->del_image(_land_active_display, image);
}

void land_display_select(LandDisplay *display)
{
    if (_land_active_display)
    {
        land_add_list_data(&_previous, _land_active_display);
    }
    _land_active_display = display;
}

void land_display_unselect(void)
{
    if (_previous && _previous->count)
    {
        LandListItem *last = _previous->last;
        _land_active_display = last->data;
        land_list_remove_item(_previous, last);
        land_listitem_destroy(last);
    }
    else
        _land_active_display = NULL;
}

