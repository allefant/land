#ifdef _PROTOTYPE_

#include <allegro.h>
#include "array.h"
#include "../display.h"
#include "log.h"

land_type(LandDisplayAllegro)
{
    struct LandDisplay super;
    BITMAP *screen;
    BITMAP *pages[3];
    BITMAP *back, *front, *triple;
};

#endif /* _PROTOTYPE_ */

#include "allegro/display.h"

static LandDisplayInterface *vtable;

LandDisplayAllegro *land_display_allegro_new(int w, int h, int bpp, int hz,
    int flags)
{
    LandDisplayAllegro *self = calloc(1, sizeof *self);
    LandDisplay *super = &self->super;
    super->w = w;
    super->h = h;
    super->bpp = bpp;
    super->hz = hz;
    super->flags = flags;
    super->vt = vtable;

    return self;
}

void land_display_allegro_set(LandDisplayAllegro *self)
{
    land_log_msg("land_display_allegro_set\n");
    LandDisplay *super = &self->super;
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
}

void land_display_allegro_flip(LandDisplayAllegro *self)
{
    BITMAP *page = self->back;
    if (self->triple)
    {
        request_video_bitmap(self->back);
        self->back = self->front;
        self->front = self->triple;
        self->triple = page;
    }
    else if (self->front)
    {
        show_video_bitmap(self->back);
        self->back = self->front;
        self->front = page;
    }
    else
    {
        blit(self->back, self->screen, 0, 0, 0, 0, self->super.w, self->super.h);
    }
}

void land_display_allegro_rectangle(LandDisplayAllegro *self,
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    rect(self->back, x, y, x_, y_, makecol(r * 255, g * 255, b * 255));
}

void land_display_allegro_line(LandDisplayAllegro *self,
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    line(self->back, x, y, x_, y_, makecol(r * 255, g * 255, b * 255));
}

void land_display_allegro_init(void)
{
    land_log_msg("land_display_allegro_init\n");
    land_alloc(vtable);
    vtable->set = (void *)land_display_allegro_set;
    vtable->flip = (void *)land_display_allegro_flip;
    vtable->rectangle = (void *)land_display_allegro_rectangle;
    vtable->line = (void *)land_display_allegro_line;
};
