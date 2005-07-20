#ifdef _PROTOTYPE_

#include <allegro.h>
#include "image.h"

#endif /* _PROTOTYPE_ */

#include "pixelmask.h"

/* Creates a bit mask of the given bitmap. The width of the mask is stored in
 * the first int of the returned array, then follow 32-bit ints, each bit
 * of an int representing a pixel.
 */
static unsigned int *pixelmask_create(BITMAP *bmp)
{
    unsigned int *mask;
    int mask_w = 2 + (bmp->w + 31) / 32;

    mask = malloc((1 + mask_w * bmp->h) * sizeof *mask);
    int y;

    for (y = 0; y < bmp->h; y++)
    {
        int x;

        for (x = 0; x < bmp->w; x += 32)
        {
            int i;
            int bits = 0;

            for (i = 0; i < 32 && x + i < bmp->w; i++)
            {
                if (getpixel(bmp, x + i, y) != bitmap_mask_color(bmp))
                {
                    bits += 1 << i;
                }
            }
            mask[1 + y * mask_w + x / 32] = bits;
        }
        /* Extra 0 padding. */
        mask[1 + y * mask_w + x / 32] = 0;
    }
    mask[0] = mask_w;
    return mask;
}

/* Compare two rectangles of two bit masks, using efficient bit checking. */
static int pixelmask_part_collision(unsigned int *mask, int x, int y,
                                    unsigned int *mask_, int x_, int y_,
                                    int w, int h)
{
    int mask_w = mask[0];
    int mask_w_ = mask_[0];
    unsigned int *li = mask + 1 + mask_w * y;
    unsigned int *li_ = mask_ + 1 + mask_w_ * y_;
    int bit = x & 31;
    int bit_ = x_ & 31;
    int j;

    for (j = 0; j < h; j++)
    {
        int lw;
        int i = x >> 5;
        int i_ = x_ >> 5;

        for (lw = w; lw > 0; lw -= 32)
        {
            int m = (li[i] >> bit) + (li[i + 1] << (32 - bit));
            int m_ = (li_[i_] >> bit_) + (li_[i_ + 1] << (32 - bit_));

            /* Compare 32 pixels in one go. */
            if (m & m_)
                return 1;
            i++;
            i_++;
        }
        li += mask_w;
        li_ += mask_w_;
    }
    return 0;
}

/* Compare a bit mask on x/y and size w/h with another on x_/y_ and size w_/h_.
 * This is very efficient, only doing bit-checks if there is overlap at all.
 */
static int pixelmask_collision(unsigned int *mask, int x, int y, int w, int h,
                        unsigned int *mask_, int x_, int y_, int w_, int h_)
{
    if (x >= x_ + w_ || x_ >= x + w || y >= y_ + h_ || y_ >= y + h)
        return 0;

    if (x <= x_)
    {
        if (y <= y_)
        {
            return pixelmask_part_collision(mask, x_ - x, y_ - y,
                                            mask_, 0, 0, MIN(x + w - x_, w_),
                                            MIN(y + h - y_, h_));
        }
        else
        {
            return pixelmask_part_collision(mask, x_ - x, 0,
                                            mask_, 0, y - y_, MIN(x + w - x_,
                                                                  w_),
                                            MIN(y_ + h_ - y, h));
        }
    }
    else
    {
        if (y <= y_)
        {
            return pixelmask_part_collision(mask, 0, y_ - y,
                                            mask_, x - x_, 0, MIN(x_ + w_ - x,
                                                                  w),
                                            MIN(y + h - y_, h_));
        }
        else
        {
            return pixelmask_part_collision(mask, 0, 0,
                                            mask_, x - x_, y - y_,
                                            MIN(x_ + w_ - x, w),
                                            MIN(y_ + h_ - y, h));
        }
    }
}

int land_image_overlaps(LandImage *self, float x, float y, LandImage *other, float x_, float y_)
{
    int w = land_image_width(self);
    int h = land_image_height(self);
    int w_ = land_image_width(other);
    int h_ = land_image_height(other);
    if (!self->mask)
        self->mask = pixelmask_create(self->memory_cache);
    if (!other->mask)
        other->mask = pixelmask_create(other->memory_cache);
    return pixelmask_collision(
        self->mask, x - self->x, y - self->y, w, h,
        other->mask, x_ - other->x, y_ - other->y, w_, h_);
}

