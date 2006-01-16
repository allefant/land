#ifdef _PROTOTYPE_
#include "../image.h"
#endif /* _PROTOTYPE_ */

#include "display.h"
#include "allegro/image.h"
#include "allegro/display.h"

static LandImageInterface *vtable;

LandImage *land_image_allegro_new(LandDisplay *display)
{
    LandImage *self;
    land_alloc(self);
    self->vt = vtable;
    return self;
}

void land_image_allegro_del(LandDisplay *display, LandImage *self)
{
    land_free(self);
}

void land_image_allegro_draw_scaled_rotated_tinted(LandImage *self,
    float x, float y, float sx, float sy, float angle, float r, float g, float b, float alpha)
{
    //set_alpha_blender();
    //draw_trans_sprite(land_display_bitmap(), self->bitmap, x, y);
    if (angle == 0)
    {
        masked_stretch_blit(self->bitmap,
            LAND_DISPLAY_IMAGE(_land_active_display)->bitmap, 0, 0,
            self->bitmap->w, self->bitmap->h, x - self->x, y - self->y,
            self->bitmap->w * sx, self->bitmap->h * sy);
    }
    else
    {
        pivot_sprite(LAND_DISPLAY_IMAGE(_land_active_display)->bitmap,
            self->bitmap, x, y, self->x, self->y, ftofix(angle * 128 / AL_PI));
    }
}

void land_image_allegro_grab(LandImage *self, int x, int y)
{
    blit(LAND_DISPLAY_IMAGE(_land_active_display)->bitmap, self->bitmap,
        x, y, 0, 0, self->bitmap->w, self->bitmap->h);
}

void land_image_allegro_init(void)
{
    land_log_msg("land_image_allegro_init\n");
    land_alloc(vtable);
    vtable->prepare = land_image_allegro_prepare;
    vtable->draw_scaled_rotated_tinted = land_image_allegro_draw_scaled_rotated_tinted;
    vtable->grab = land_image_allegro_grab;
}

void land_image_allegro_prepare(LandImage *self)
{
}
