#include <string.h>
#include "display.h"

#ifdef _PROTOTYPE_

#include <allegro.h>
#include "array.h"
#include "log.h"

typedef struct LandImage LandImage;

land_type(LandImageInterface)
{
    land_method(void, prepare, (LandImage *self));
    land_method(void, draw_scaled_rotated_tinted, (LandImage *self,
        float x, float y, float sx, float sy, float a, float r, float g, float b));
};

struct LandImage
{
    LandImageInterface *vt;
    char *filename;
    char *name;
    BITMAP *bitmap;
    BITMAP *memory_cache;
    int gl_texture;

    int x, y;
};

#endif /* _PROTOTYPE_ */

#include "image.h"
#include "allegro/image.h"
#include "allegrogl/image.h"

land_array(LandImage)

LandImage *land_load_image(char const *filename)
{
    land_log_msg("land_load_image %s..", filename);
    set_color_conversion(COLORCONV_NONE);
    BITMAP *bmp = load_bitmap(filename, NULL);
    if (bmp)
    {
        LandImage *self = land_display_new_image();
        land_add(LandImage, self);
        self->filename = strdup(filename);
        self->name = strdup(filename);
        self->bitmap = bmp;
        self->memory_cache = bmp;
        land_image_prepare(self);
        land_log_msg_nostamp("success (%d x %d)\n", bmp->w, bmp->h);
        return self;
    }
    else
    {
        land_log_msg_nostamp("failure\n");
    }
    return NULL;
}

void land_image_prepare(LandImage *self)
{
    self->vt->prepare(self);
}

static int callback(const char *filename, int attrib, void *param)
{
    land_load_image(filename);
    return 0;
}

int land_load_images(char const *pattern)
{
    int id = LandImage_count;
    int count = for_each_file_ex(pattern, 0, 0, callback, NULL);
    if (count)
        return id;
    return 0;
}

LandImage *land_find_image(char const *name)
{
    int i;
    land_foreach(LandImage, i)
    {
        LandImage *self = land_pointer(LandImage, i);
        if (!strcmp(self->name, name))
            return self;
    }
    return NULL;
}


void land_image_draw_scaled_rotated_tinted(LandImage *self, float x, float y, float sx, float sy,
    float a, float r, float g, float b)
{
    self->vt->draw_scaled_rotated_tinted(self, x, y, sx, sy, a, r, g, b);
}

void land_image_draw_scaled_rotated(LandImage *self, float x, float y, float sx, float sy,
    float a)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, a, 1, 1, 1);
}

void land_image_draw_scaled(LandImage *self, float x, float y, float sx, float sy)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, 1, 1, 1);
}

void land_image_draw_scaled_tinted(LandImage *self, float x, float y, float sx, float sy,
    float r, float g, float b)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, r, g, b);
}

void land_image_draw(LandImage *self, float x, float y)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, 1, 1, 1);
}

void land_image_offset(LandImage *self, int x, int y)
{
    self->x = x;
    self->y = y;
}

void land_image_center(LandImage *self)
{
    self->x = self->bitmap->w / 2;
    self->y = self->bitmap->h / 2;
}

void land_image_init(void)
{
    land_image_allegro_init();
    land_image_allegrogl_init();
}
