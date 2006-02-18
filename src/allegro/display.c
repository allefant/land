#ifdef _PROTOTYPE_

#include <allegro.h>
#include "../array.h"
#include "../display.h"
#include "../log.h"
#include "../image/display.h"

land_type(LandDisplayAllegro)
{
    struct LandDisplayImage super;
    BITMAP *screen;
    BITMAP *pages[3];
    BITMAP *back, *front, *triple;
};

#define LAND_DISPLAY_ALLEGRO(_x_) ((LandDisplayAllegro *)_x_)

#endif /* _PROTOTYPE_ */

#include "allegro/display.h"
#include "allegro/image.h"

static LandDisplayInterface *vtable;

LandDisplayAllegro *land_display_allegro_new(int w, int h, int bpp, int hz,
    int flags)
{
    LandDisplayAllegro *self = calloc(1, sizeof *self);
    LandDisplay *super = &self->super.super;
    super->w = w;
    super->h = h;
    super->bpp = bpp;
    super->hz = hz;
    super->flags = flags;
    super->vt = vtable;

    return self;
}

void land_display_allegro_set(LandDisplay *super)
{
    land_log_msg("land_display_allegro_set\n");
    LandDisplayAllegro *self = LAND_DISPLAY_ALLEGRO(super);
    int mode = GFX_AUTODETECT;

    int cd = desktop_color_depth();
    if (super->bpp)
        cd = super->bpp;

    if (super->flags & LAND_WINDOWED)
        mode = GFX_AUTODETECT_WINDOWED;
    else if (super->flags & LAND_FULLSCREEN)
        mode = GFX_AUTODETECT_FULLSCREEN;

    set_color_depth(cd);
    if (super->hz)
        request_refresh_rate(super->hz);
    set_gfx_mode(mode, super->w, super->h, 0, 0);

    self->screen = screen;

    self->back = create_video_bitmap(SCREEN_W, SCREEN_H);
    if (self->back)
    {
        self->front = create_video_bitmap(SCREEN_W, SCREEN_H);
        if (self->front)
        {
            self->triple = create_video_bitmap(SCREEN_W, SCREEN_H);
        }
        else
        {
            destroy_bitmap(self->back);
            self->back = create_bitmap(SCREEN_W, SCREEN_H);
        }
    }
    else
    {
        self->back = create_bitmap(SCREEN_W, SCREEN_H);
    }
    self->super.bitmap = self->back;
}

void land_display_allegro_flip(LandDisplay *self)
{
    LandDisplayAllegro *sub = LAND_DISPLAY_ALLEGRO(self);
    BITMAP *page = sub->back;
    if (sub->triple)
    {
        request_video_bitmap(sub->back);
        sub->back = sub->front;
        sub->front = sub->triple;
        sub->triple = page;
    }
    else if (sub->front)
    {
        show_video_bitmap(sub->back);
        sub->back = sub->front;
        sub->front = page;
    }
    else
    {
        blit(sub->back, sub->screen, 0, 0, 0, 0, self->w, self->h);
    }
    sub->super.bitmap = sub->back;
}

void land_display_allegro_init(void)
{
    land_log_msg("land_display_allegro_init\n");
    land_alloc(vtable);
    vtable->clear = land_display_image_clear;
    vtable->clip = land_display_image_clip;
    vtable->color = land_display_image_color;
    vtable->rectangle = land_display_image_rectangle;
    vtable->filled_rectangle = land_display_image_filled_rectangle;
    vtable->line = land_display_image_line;
    vtable->filled_circle = land_display_image_filled_circle;
    vtable->plot = land_display_image_plot;

    vtable->set = land_display_allegro_set;
    vtable->flip = land_display_allegro_flip;
    vtable->del_image = land_image_allegro_del;
    vtable->new_image = land_image_allegro_new;
};
