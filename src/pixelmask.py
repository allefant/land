import global stdio, stdint
import image

class LandPixelMask:
    int w, h, x, y
    int n
    SinglePixelMask *rotation[0]

static import font, global math

#*** "define" DEBUG_MASK

# TODO: 64bit version
# TODO: Defer creation of masks?
#       E.g. if a bitmap is used with 256 rotations, but it only ever is
#       rotated 5 degree left/right.. then that would only cache the necessary
#       masks.

class SinglePixelMask:
    int w, h
    uint32_t data[0]

static macro BB(x1, y1, x2, y2, x3, y3, x4, y4):
    *bl = x1 * cos(angle) + y1 * sin(angle)
    *bt = y2 * cos(angle) - x2 * sin(angle)
    *br = x3 * cos(angle) + y3 * sin(angle)
    *bb = y4 * cos(angle) - x4 * sin(angle)

static def get_bounding_box(float l, float t, float r, float b, float angle,
    float *bl, float *bt, float *br, float *bb):
    if angle < LAND_PI / 2:
        BB(l, t, r, t, r, b, l, b)
    elif angle < LAND_PI:
        BB(r, t, r, b, l, b, l, t)
    elif angle < 3 * LAND_PI / 2:
        BB(r, b, l, b, l, t, r, t)
    else:
        BB(l, b, l, t, r, t, r, b)

*** "ifdef" DEBUG_MASK
static def printout_mask(SinglePixelMask *mask):
    int i
    int mask_w = mask->w
    for i = 0 while i < mask->h with i++:
        int j
        for j = 0 while j < mask_w with j++:
            int m = mask->data[mask_w * i + j]
            int b
            for b = 0 while b < 32 with b++:
                printf("%c", m & (1 << b) ? '1' : '0')

        printf("\n")
*** "endif"

# Creates n prerotated bitmasks for the given bitmap. A single bit
# represents one pixel.
static LandPixelMask *def pixelmask_create(LandImage *image,
    int n, int threshold):
    LandPixelMask *mask
    int j
    mask = land_malloc(sizeof *mask + sizeof(SinglePixelMask *) * n)
    mask->n = n
    int bmpw = land_image_width(image)
    int bmph = land_image_height(image)
    mask->w = bmpw
    mask->h = bmph
    mask->x = 0
    mask->y = 0
    for j = 0 while j < n with j++:
        float angle = j * LAND_PI * 2 / n
        float w, h
        if angle < LAND_PI / 2:
            w = bmpw * cos(angle) + bmph * sin(angle)
            h = bmph * cos(angle) + bmpw * sin(angle)

        elif angle < LAND_PI:
            w = bmpw * -cos(angle) + bmph * sin(angle)
            h = bmph * -cos(angle) + bmpw * sin(angle)

        elif angle < 3 * LAND_PI / 2:
            w = bmpw * -cos(angle) + bmph * -sin(angle)
            h = bmph * -cos(angle) + bmpw * -sin(angle)

        else:
            w = bmpw * cos(angle) + bmph * -sin(angle)
            h = bmph * cos(angle) + bmpw * -sin(angle)

        int tw = ceil(w)
        int th = ceil(h)
        LandImage *temp = land_image_create(tw, th)
        land_set_image_display(temp)
        land_image_draw_rotated(image, w / 2.0, h / 2.0, angle)
        land_unset_image_display()

        int mask_w = 1 + (w + 31) / 32

        mask->rotation[j] = land_malloc(sizeof *mask->rotation[j] +
            mask_w * th * sizeof(uint32_t))
        mask->rotation[j]->w = mask_w
        mask->rotation[j]->h = th
        
        unsigned char rgba[tw * th * 4]
        land_image_get_rgba_data(temp, rgba)
        land_image_destroy(temp)

        for int y = 0 while y < th with y++:
            int x
            for x = 0 while x < tw with x += 32:
                int bits = 0

                for int i = 0 while i < 32 && x + i < tw with i++:
                    if rgba[y * tw * 4 + (x + i) * 4 + 3] >= threshold:
                        bits += 1 << i
                
                mask->rotation[j]->data[y * mask_w + x / 32] = bits

            # Extra 0 padding, so if *pos is valid, *(pos + 1) will point to
            # all 0 - useful to not need special case the right border. 
            mask->rotation[j]->data[y * mask_w + x / 32] = 0

        *** "ifdef" DEBUG_MASK
        printout_mask(mask->rotation[j])
        *** "endif"

    return mask

static def pixelmask_destroy(LandPixelMask *mask):
    int j
    for j = 0 while j < mask->n with j++:
        land_free(mask->rotation[j])

    land_free(mask)

static int def mask_get_rotation_frame(LandPixelMask *mask, float angle):
    float r = mask->n * angle / (2 * LAND_PI)
    if r > 0: r += 0.5
    else: r -= 0.5
    int i = (int)(r) % mask->n
    if i < 0: i += mask->n
    return i

def land_image_debug_pixelmask(LandImage *self, float x, float y, float angle):
    int i
    int k = mask_get_rotation_frame(self->mask, angle)
    int mask_w = self->mask->rotation[k]->w

    int w = land_image_width(self)
    int h = land_image_height(self)
    float ml, mt, mr, mb
    get_bounding_box(-self->x, -self->y, w - self->x, h - self->y,
        k * 2.0 * LAND_PI / self->mask->n, &ml, &mt, &mr, &mb)

    land_color(1, 0, 0, 1)
    land_rectangle(x + ml, y + mt, x + mr, y + mb)

    land_color(1, 1, 1, 1)
    for i = 0 while i < self->mask->rotation[k]->h with i++:
        int j
        for j = 0 while j < mask_w with j++:
            int m = self->mask->rotation[k]->data[mask_w * i + j]
            int b
            for b = 0 while b < 32 with b++:
                if m & (1 << b):
                    land_plot(x + ml + j * 32 + b, y + mt + i)

# Compare two rectangles of two bit masks, using efficient bit checking. 
static int def pixelmask_part_collision(SinglePixelMask *mask, int x, int y,
                                    SinglePixelMask *mask_, int x_, int y_,
                                    int w, int h):
    int mask_w = mask->w
    int mask_w_ = mask_->w
    unsigned int *li = mask->data + mask_w * y
    unsigned int *li_ = mask_->data + mask_w_ * y_
    unsigned int bit = x & 31
    unsigned int bit_ = x_ & 31
    int j

    for j = 0 while j < h with j++:
        int lw
        int i = x >> 5
        int i_ = x_ >> 5

        for lw = w while lw > 0 with lw -= 32:
            unsigned int m, m_
            if bit == 0: m = li[i]
            else: m = (li[i] >> bit) + (li[i + 1] << (32 - bit))

            if bit_ == 0: m_ = li_[i_]
            else: m_ = (li_[i_] >> bit_) + (li_[i_ + 1] << (32 - bit_))

            # Compare 32 pixels in one go. 
            if m & m_: return 1

            i++
            i_++

        li += mask_w
        li_ += mask_w_

    return 0

# Compare a bit mask on x/y and size w/h with another on x_/y_ and size w_/h_.
# This is very efficient, only doing bit-checks if there is overlap at all.
# 
static int def pixelmask_collision(
    SinglePixelMask *mask, int x, y, w, h,
    SinglePixelMask *mask_, int x_, y_, w_, h_):
    if x >= x_ + w_ or x_ >= x + w or y >= y_ + h_ or y_ >= y + h: return 0

    if x <= x_:
        if y <= y_:
            return pixelmask_part_collision(mask, x_ - x, y_ - y,
                mask_, 0, 0, min(x + w - x_, w_), min(y + h - y_, h_))

        else:
            return pixelmask_part_collision(mask, x_ - x, 0, mask_, 0,
                y - y_, min(x + w - x_, w_), min(y_ + h_ - y, h))


    else:
        if y <= y_:
            return pixelmask_part_collision(mask, 0, y_ - y, mask_,
                x - x_, 0, min(x_ + w_ - x, w), min(y + h - y_, h_))

        else:
            return pixelmask_part_collision(mask, 0, 0, mask_, x - x_,
                y - y_, min(x_ + w_ - x, w), min(y_ + h_ - y, h))

# Create pixelmasks for the given amount of rotations (starting with angle 0).
# The source offset and source clipping are considered for this.
# 
def land_image_create_pixelmasks(LandImage *self, int n, int threshold):
    self->mask = pixelmask_create(self, n, threshold)

def land_image_destroy_pixelmasks(LandImage *self):
    if self->mask: pixelmask_destroy(self->mask)

# Returns 1 if non-transparent pixels overlap, 0 otherwise. 
int def land_image_overlaps(LandImage *self, float x, float y, float angle,
    LandImage *other, float x_, float y_, float angle_):
    if not self->mask: return 0
    if not other->mask: return 0

    int w = self->mask->w
    int h = self->mask->h
    int w_ = other->mask->w
    int h_ = other->mask->h

    int i = mask_get_rotation_frame(self->mask, angle)
    int i_ = mask_get_rotation_frame(other->mask, angle_)
    
    int mx = self->mask->x - self->x
    int my = self->mask->y - self->y
    int mx_ = other->mask->x - other->x
    int my_ = other->mask->y - other->y

    float ml, mt, mr, mb, ml_, mt_, mr_, mb_
    get_bounding_box(mx, my, mx + w, my + h, i * 2.0 * LAND_PI / self->mask->n,
        &ml, &mt, &mr, &mb)
    get_bounding_box(mx_, my_, mx_ + w_, my_ + h_, i_ * 2.0 * LAND_PI / other->mask->n,
        &ml_, &mt_, &mr_, &mb_)

    return pixelmask_collision(
        self->mask->rotation[i], x + ml, y + mt, mr - ml, mb - mt,
        other->mask->rotation[i_], x_ + ml_, y_ + mt_, mr_ - ml_, mb_ - mt_)
