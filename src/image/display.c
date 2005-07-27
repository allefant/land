#ifdef _PROTOTYPE_

#include <allegro.h>
#include "../array.h"
#include "../display.h"
#include "../log.h"

land_type(LandDisplayImage)
{
    struct LandDisplay super;
    LandImage *target;
};

#define LAND_DISPLAY_IMAGE(x) ((LandDisplayImage *)(x))

#endif /* _PROTOTYPE_ */

#include "image/display.h"

static LandDisplayInterface *vtable;

static inline int color(LandDisplay *display)
{
    return makeacol(display->color_r * 255, display->color_g * 255,
        display->color_b * 255, display->color_a * 255);
}

LandDisplay *land_display_image_new(LandImage *target, int flags)
{
    LandDisplayImage *self = calloc(1, sizeof *self);
    LandDisplay *super = &self->super;
    super->w = land_image_width(target);
    super->h = land_image_height(target);
    super->bpp = bitmap_color_depth(target->memory_cache);
    super->hz = 0;
    super->flags = flags;
    super->vt = vtable;

    self->target = target;

    return super;
}

void land_display_image_set(LandDisplay *self)
{
    land_log_msg("land_display_image_set\n");
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
    rect(self->target->memory_cache, x, y, x_, y_, color(display));
}

void land_display_image_line(LandDisplay *display,
    float x, float y, float x_, float y_)
{
    land_log_msg("land_display_image_line\n");
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display);
    line(self->target->memory_cache, x, y, x_, y_, color(display));
}

void land_display_image_color(LandDisplay *super)
{
}

void land_display_image_clip(LandDisplay *super)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(super);
    set_clip_rect(self->target->memory_cache,
        (int)(super->clip_x1 + 0.5), (int)(super->clip_y1 + 0.5),
        (int)(super->clip_x2 - 0.5), (int)(super->clip_y2 - 0.5));
    set_clip_state(self->target->memory_cache, !super->clip_off);
}

void land_display_image_clear (LandDisplay *super, float r, float g, float b)
{
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(super);
    clear_to_color(self->target->memory_cache, makecol(r * 255, g * 255, b * 255));
}

void land_display_image_init(void)
{
    land_log_msg("land_display_image_init\n");
    land_alloc(vtable);
    vtable->set = land_display_image_set;
    vtable->flip = land_display_image_flip;
    vtable->rectangle = land_display_image_rectangle;
    vtable->line = land_display_image_line;
    vtable->color = land_display_image_color;
    vtable->clip = land_display_image_clip;
    vtable->clear = land_display_image_clear;
};
