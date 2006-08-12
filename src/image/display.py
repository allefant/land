#ifdef _PROTOTYPE_

#include <allegro.h>
#include "../array.h"
#include "../display.h"
#include "../log.h"

typedef struct LandDisplayImage LandDisplayImage;

struct LandDisplayImage
{
    struct LandDisplay super;
    BITMAP *bitmap;
};

#define LAND_DISPLAY_IMAGE(x) ((LandDisplayImage *)(x))

#endif /* _PROTOTYPE_ */

#include "display.h"
#include "allegro/image.h"

static LandDisplayInterface *vtable;

static inline int color(LandDisplay *display)
{
    return makeacol(display->color_r * 255, display->color_g * 255,
        display->color_b * 255, display->color_a * 255);
}

LandDisplay *land_display_image_new(LandImage *target, int flags)
{
    LandDisplayImage *self;
    land_alloc(self);
    LandDisplay *super = &self->super;
    BITMAP *bitmap = target->memory_cache;
    super->w = land_image_width(target);
    super->h = land_image_height(target);
    super->bpp = bitmap_color_depth(bitmap);
    super->hz = 0;
    super->flags = flags;
    super->vt = vtable;

    self->bitmap = bitmap;

    return super;
}

void land_display_image_clear(LandDisplay *super, float r, float g, float b, float a)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(super);
    clear_to_color(self->bitmap, makeacol(r * 255, g * 255, b * 255, a * 255));
}

void land_display_image_clip(LandDisplay *super)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(super);
    set_clip_state(self->bitmap, 1);
    if (super->clip_off)
        set_clip_rect(self->bitmap, 0, 0,
            self->bitmap->w - 1, self->bitmap->h - 1);
    else
        set_clip_rect(self->bitmap, super->clip_x1 + 0.5, super->clip_y1 + 0.5,
            super->clip_x2 - 0.5, super->clip_y2 - 0.5);
}

void land_display_image_color(LandDisplay *super)
{
}

void land_display_image_set(LandDisplay *self)
{
    land_log_message("land_display_image_set\n");
    /* Nothing to set up for a memory bitmap. */
}

void land_display_image_flip(LandDisplay *self)
{
    /* No need to flip a memory bitmap. */
}

void land_display_image_rectangle(LandDisplay *display,
    float x, float y, float x_, float y_)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display);
    rect(self->bitmap, x, y, x_, y_, color(display));
}

void land_display_image_filled_rectangle(LandDisplay *display,
    float x, float y, float x_, float y_)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display);
    rectfill(self->bitmap, x, y, x_, y_, color(display));
}

void land_display_image_line(LandDisplay *display,
    float x, float y, float x_, float y_)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display);
    line(self->bitmap, x, y, x_, y_, color(display));
}

void land_display_image_filled_circle(LandDisplay *display,
    float x, float y, float x_, float y_)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display);
    ellipsefill(self->bitmap, (x + x_) / 2, (y + y_) / 2,
        (x_ - x) / 2, (y_ - y) / 2, color(display));
}

void land_display_image_plot(LandDisplay *display,
    float x, float y)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display);
    putpixel(self->bitmap, x, y, color(display));
}

void land_display_image_init(void)
{
    land_log_message("land_display_image_init\n");
    land_alloc(vtable);
    vtable->clear = land_display_image_clear;
    vtable->clip = land_display_image_clip;
    vtable->color = land_display_image_color;
    vtable->rectangle = land_display_image_rectangle;
    vtable->filled_rectangle = land_display_image_filled_rectangle;
    vtable->line = land_display_image_line;
    vtable->filled_circle = land_display_image_filled_circle;
    vtable->plot = land_display_image_plot;

    vtable->set = land_display_image_set;
    vtable->flip = land_display_image_flip;
    vtable->del_image = land_image_allegro_del;
    vtable->new_image = land_image_allegro_new;
};

void land_display_image_exit(void)
{
    land_log_message("land_display_image_exit\n");
    land_free(vtable);
}
