#ifdef _PROTOTYPE_
#include "../image.h"
#endif /* _PROTOTYPE_ */

#include "allegro/image.h"
#include "allegro/display.h"

static LandImageInterface *vtable;

LandImage *land_image_allegro_new(void)
{
    LandImage *self;
    land_alloc(self);
    self->vt = vtable;
    return self;
}

void land_image_allegro_draw_scaled_rotated_tinted(LandImage *self,
    float x, float y, float sx, float sy, float a, float r, float g, float b)
{
    //set_alpha_blender();
    //draw_trans_sprite(land_display_bitmap(), self->bitmap, x, y);
    masked_stretch_blit(self->bitmap,
        ((LandDisplayAllegro *)_land_active_display)->back, 0, 0,
        self->bitmap->w, self->bitmap->h, x - self->x, y - self->y,
        self->bitmap->w * sx, self->bitmap->h * sy);
}

void land_image_allegro_init(void)
{
    land_log_msg("land_image_allegro_init\n");
    land_alloc(vtable);
    vtable->prepare = land_image_allegro_prepare;
    vtable->draw_scaled_rotated_tinted = land_image_allegro_draw_scaled_rotated_tinted;
}

void land_image_allegro_prepare(LandImage *self)
{
}
