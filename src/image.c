#ifdef _PROTOTYPE_

#include <allegro.h>
#include "array.h"
#include "log.h"

typedef struct LandImage LandImage;

#include "pixelmask.h"

land_type(LandImageInterface)
{
    land_method(void, prepare, (LandImage *self));
    land_method(void, draw_scaled_rotated_tinted, (LandImage *self,
        float x, float y, float sx, float sy, float angle, float r, float g, float b, float alpha));
    land_method(void, grab, (LandImage *self, int x, int y));
    land_method(void, grab_into, (LandImage *self, int x, int y, int tx, int ty, int tw, int th));
};

struct LandImage
{
    LandImageInterface *vt;
    char *filename;
    char *name;
    BITMAP *bitmap;
    BITMAP *memory_cache;

    LandPixelMask *mask; /* Bit-mask of the image. */

    float x, y; /* Offset to origin. */

    float l, t, r, b; /* Cut-away left, top, right, bottom. */
};

#endif /* _PROTOTYPE_ */

#include <string.h>
#include "display.h"
#include "image.h"
#include "allegro/image.h"
#include "allegrogl/image.h"

land_array(LandImage)

LandImage *land_image_load(char const *filename)
{
    land_log_msg("land_image_load %s..", filename);
    set_color_conversion(COLORCONV_NONE);
    BITMAP *bmp = load_bitmap(filename, NULL);
    if (bmp)
    {
        LandImage *self = land_display_new_image();
        self->filename = strdup(filename);
        self->name = strdup(filename);
        self->bitmap = bmp;
        self->memory_cache = bmp;
        land_image_prepare(self);
        land_log_msg_nostamp("success (%d x %d)\n", bmp->w, bmp->h);

        float red, green, blue, alpha;
        int n;
        n = land_image_color_stats(self, &red, &green, &blue, &alpha);
        land_log_msg(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n);
        return self;
    }
    else
    {
        land_log_msg_nostamp("failure\n");
    }
    return NULL;
}

LandImage *land_image_new(int w, int h)
{
    BITMAP *bmp = create_bitmap(w, h);
    LandImage *self = land_display_new_image();
    self->filename = NULL;
    self->name = NULL;
    self->bitmap = bmp;
    self->memory_cache = bmp;
    land_log_msg("land_image_new %d x %d x %d.\n", w, h, bitmap_color_depth(bmp));
    land_image_prepare(self);
    return self;
}

void land_image_del(LandImage *self)
{
    if (self->bitmap != self->memory_cache)
        destroy_bitmap(self->bitmap);
    destroy_bitmap(self->memory_cache);
    land_display_del_image(self);
}

void land_image_crop(LandImage *self, int x, int y, int w, int h)
{
    // TODO
}

LandImage *land_image_new_from(LandImage *copy, int x, int y, int w, int h)
{
    BITMAP *bmp = create_bitmap(w, h);
    LandImage *self = land_display_new_image();
    self->filename = NULL;
    self->name = NULL;
    self->bitmap = bmp;
    self->memory_cache = bmp;
    land_log_msg("land_image_new_from %d x %d x %d.\n", w, h, bitmap_color_depth(bmp));

    blit(copy->memory_cache, self->memory_cache, x, y, 0, 0, w, h);
    float red, green, blue, alpha;
    int n;
    n = land_image_color_stats(self, &red, &green, &blue, &alpha);
    land_log_msg(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n);
    land_image_prepare(self);
    return self;
}

/* Returns the number of pixels in the image, and the average red, green, blue
 * and alpha component.
 */
int land_image_color_stats(LandImage *self, float *red, float *green, float *blue, float *alpha)
{
    int n = 0;
    *red = 0;
    *green = 0;
    *blue = 0;
    *alpha = 0;
    int i, j;
    for (j = 0; j < land_image_height(self); j++)
    {
        for (i = 0; i < land_image_width(self); i++)
        {
            int rgba = getpixel(self->memory_cache, i, j);
            *red += getr(rgba) * 1.0 / 255.0;
            *green += getg(rgba) * 1.0 / 255.0;
            *blue += getb(rgba) * 1.0 / 255.0;
            *alpha += geta(rgba) * 1.0 / 255.0;
            n++;
        }
    }
    return n;
}

/* Colorizes the part of the image specified by the mask with the current color. */
void land_image_colorize(LandImage *self, LandImage *colormask)
{
    int allegro_pink = bitmap_mask_color(colormask->bitmap);
    int x, y;
    float ch, cs, v;
    int r, g, b;
    r = _land_active_display->color_r * 255;
    g = _land_active_display->color_g * 255;
    b = _land_active_display->color_b * 255;
    rgb_to_hsv(r, g, b, &ch, &cs, &v);

    for (x = 0; x < self->bitmap->w; x++)
    {
        for (y = 0; y < self->bitmap->h; y++)
        {
            int col = getpixel(colormask->bitmap, x, y);
            if (col != allegro_pink)
            {
                float h, s;
                rgb_to_hsv(getr(col), getg(col), getb(col), &h, &s, &v);
                hsv_to_rgb(ch, cs, v, &r, &g, &b);
                putpixel(self->bitmap, x, y, makecol(r, g, b));
            }
        }
    }
}

void land_image_prepare(LandImage *self)
{
    self->vt->prepare(self);
}

static int callback(const char *filename, int attrib, void *param)
{
    land_image_load(filename);
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
    float angle, float r, float g, float b, float alpha)
{
    self->vt->draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, r, g, b, alpha);
}

void land_image_draw_scaled_rotated(LandImage *self, float x, float y, float sx, float sy,
    float angle)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, 1, 1, 1, 1);
}

void land_image_draw_scaled(LandImage *self, float x, float y, float sx, float sy)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, 1, 1, 1, 1);
}

void land_image_draw_rotated(LandImage *self, float x, float y, float a)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, a, 1, 1, 1, 1);
}

void land_image_draw_scaled_tinted(LandImage *self, float x, float y, float sx, float sy,
    float r, float g, float b, float alpha)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, r, g, b, alpha);
}

void land_image_draw(LandImage *self, float x, float y)
{
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, 1, 1, 1, 1);
}

void land_image_grab(LandImage *self, int x, int y)
{
    self->vt->grab(self, x, y);
}

void land_image_grab_into(LandImage *self, int x, int y, int tx, int ty, int tw, int th)
{
    self->vt->grab_into(self, x, y, tx, ty, tw, th);
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

/* Set's a source clip rectangle for the image. That is, only the specified
 * rectangle out of the image will actually be used when this image is drawn
 * somewhere.
 */
void land_image_clip(LandImage *self, float x, float y, float x_, float y_)
{
    self->l = x;
    self->t = y;
    self->r = self->bitmap->w - x_;
    self->b = self->bitmap->h - y_;
}

/* Just a shortcut for land_image_clip(image, 0, 0, 0, 0); */
void land_image_unclip(LandImage *self)
{
    self->l = 0;
    self->t = 0;
    self->r = 0;
    self->b = 0;
}

int land_image_height(LandImage *self)
{
    return self->bitmap->h;
}

int land_image_width(LandImage *self)
{
    return self->bitmap->w;
}

/* Optimizes a bitmap to take only as little space as necesary, whilst
 * maintaining the correct offset.
 */
static BITMAP *optimize_bitmap(BITMAP *bmp, int *x, int *y)
{
    int l = bmp->w;
    int r = -1;
    int t = bmp->h;
    int b = -1;
    int i, j;
    for (j = 0; j < bmp->h; j++)
    {
        for (i = 0; i < bmp->w; i++)
        {
            if (getpixel(bmp, i, j) != bitmap_mask_color(bmp))
            {
                if (i < l)
                        l = i;
                if (j < t)
                        t = j;
                if (i > r)
                        r = i;
                if (j > b)
                        b = j;
            }
        }
    }
    BITMAP *optimized = create_bitmap(1 + r - l, 1 + b - t);
    blit(bmp, optimized, l, t, 0, 0, optimized->w, optimized->h);
    *x -= l;
    *y -= t;
    return optimized;
}

void land_image_optimize(LandImage *self)
{
    int offx = 0, offy = 0;
    BITMAP *opt = optimize_bitmap(self->memory_cache, &offx, &offy);
    // FIXME: self->bitmap
    destroy_bitmap(self->memory_cache);
    self->memory_cache = opt;

    self->x += offx;
    self->y += offy;

    // FIXME: source clip rect?

    self->vt->prepare(self);
}

