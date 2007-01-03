import global allegro, jpgalleg, loadpng
import array, log, pixelmask, util

macro LAND_SUBIMAGE 1

class LandImageInterface:
    land_method(void, prepare, (LandImage *self))
    land_method(void, draw_scaled_rotated_tinted, (LandImage *self,
        float x, float y, float sx, float sy, float angle, float r, float g, float b, float alpha))
    land_method(void, grab, (LandImage *self, int x, int y))
    land_method(void, grab_into, (LandImage *self, int x, int y, int tx, int ty, int tw, int th))
    land_method(void, sub, (LandImage *self, LandImage *parent))

class LandImage:
    """
    An image is a rectangular area of pixels. Land will by default always keep a
    "memory cache" of the image, that is an uncompressed copy of all the R/G/B/A
    values of all pixels contained in it.
    Usually, output drivers will convert the image to a device dependent format
    (e.g. an OpenGL texture) which is much faster to display than sending all
    the single pixels to the screen each time the image is to be shown.
    """
    LandImageInterface *vt
    char *filename
    char *name

    BITMAP *bitmap; # FIXME: what for is this used?
    # We always keep a memory cache. FIXME: when is it updated? 
    BITMAP *memory_cache
    
    int flags

    LandPixelMask *mask; # Bit-mask of the image. 
    RGB *palette

    float x, y; # Offset to origin. 

    float l, t, r, b; # Cut-away left, top, right, bottom. 

import allegro/image, allegrogl/image

# TODO
class LandSubImage:
    """
    A sub-image is an image sharing all of its pixels with some other image. If
    the other image is changed, then also the sub-image changes.
    """
    LandImage super
    LandImage *parent
    float x, y, w, h

static import global string
static import display, data

extern LandDataFile *_land_datafile

static void (*_cb)(char const *path, LandImage *image)

static int active

def land_image_set_callback(void (*cb)(char const *path, LandImage *image)):
    _cb = cb

LandImage *def land_image_load(char const *filename):
    LandImage *self = NULL
    land_log_message("land_image_load %s..", filename)
    set_color_conversion(COLORCONV_NONE)
    BITMAP *bmp = NULL
    PALETTE pal
    if _land_datafile:
        int size
        char *buffer = land_datafile_read_entry(_land_datafile, filename,
            &size)
        if buffer:
            land_log_message_nostamp(" [memory %d] ", size)
            if !ustrcmp(get_extension(filename), "jpg"):
                bmp = load_memory_jpg(buffer, size, NULL)

            elif !strcmp(get_extension(filename), "png"):
                bmp = load_memory_png(buffer, size, NULL)

            land_free(buffer)


    if !bmp: bmp = load_bitmap(filename, pal)
    if bmp:
        self = land_display_new_image()
        self->filename = land_strdup(filename)
        self->name = land_strdup(filename)
        self->bitmap = bmp
        self->memory_cache = bmp
        if bitmap_color_depth(bmp) == 8:
            self->palette = land_malloc(sizeof(PALETTE))
            memcpy(self->palette, &pal, sizeof(PALETTE))

        land_log_message_nostamp("success (%d x %d)\n", bmp->w, bmp->h)
        land_image_prepare(self)
    
        float red, green, blue, alpha
        int n
        n = land_image_color_stats(self, &red, &green, &blue, &alpha)
        land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)

    else:
        land_log_message_nostamp("failure\n")

    if _cb: _cb(filename, self)
    return self

LandImage *def land_image_new(int w, int h):
    BITMAP *bmp = create_bitmap(w, h)
    LandImage *self = land_display_new_image()
    self->filename = NULL
    self->name = NULL
    self->bitmap = bmp
    self->memory_cache = bmp
    land_log_message("land_image_new %d x %d x %d.\n", w, h, bitmap_color_depth(bmp))
    land_image_prepare(self)
    return self

LandImage *def land_image_create(int w, int h):
    BITMAP *bmp = create_bitmap(w, h)
    clear_to_color(bmp, 0)
    LandImage *self = land_display_new_image()
    self->filename = NULL
    self->name = NULL
    self->bitmap = bmp
    self->memory_cache = bmp
    land_log_message("land_image_create %d x %d x %d.\n", w, h, bitmap_color_depth(bmp))
    land_image_prepare(self)
    return self

def land_image_del(LandImage *self):
    #FIXME!
    # if self->bitmap != self->memory_cache: #    destroy_bitmap(self->bitmap)
    land_image_destroy_pixelmasks(self)
    destroy_bitmap(self->memory_cache)
    if self->name: land_free(self->name)
    if self->filename && self->filename != self->name: land_free(self->filename)
    if self->palette: land_free(self->palette)
    land_display_del_image(self)

def land_image_destroy(LandImage *self):
    land_image_del(self)

def land_image_crop(LandImage *self, int x, int y, int w, int h):
    # TODO
    pass

LandImage *def land_image_new_from(LandImage *copy, int x, int y, int w, int h):
    """
    Create a new image, copying pixel data from a rectangle in an existing
    image.
    """
    BITMAP *bmp = create_bitmap_ex(bitmap_color_depth(copy->memory_cache),
        w, h)
    LandImage *self = land_display_new_image()
    self->filename = NULL
    self->name = NULL
    self->bitmap = bmp
    self->memory_cache = bmp
    land_log_message("land_image_new_from %d x %d x %d.\n", w, h, bitmap_color_depth(bmp))

    blit(copy->memory_cache, self->memory_cache, x, y, 0, 0, w, h)
    float red, green, blue, alpha
    int n
    n = land_image_color_stats(self, &red, &green, &blue, &alpha)
    land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
    land_image_prepare(self)
    return self

int def land_image_color_stats(LandImage *self,
    float *red, *green, *blue, *alpha):
    """
    Returns the number of pixels in the image, and the average red, green, blue
    and alpha component. 
    """
    int n = 0
    *red = 0
    *green = 0
    *blue = 0
    *alpha = 0
    int i, j
    for j = 0; j < land_image_height(self); j++:
        for i = 0; i < land_image_width(self); i++:
            int rgba = getpixel(self->memory_cache, i, j)
            *red += getr32(rgba) * 1.0 / 255.0
            *green += getg32(rgba) * 1.0 / 255.0
            *blue += getb32(rgba) * 1.0 / 255.0
            *alpha += geta32(rgba) * 1.0 / 255.0
            n++


    return n

def land_image_colorize(LandImage *self, LandImage *colormask):
    """
    Colorizes the part of the image specified by the mask with the current
    color. The mask uses (1, 0, 1) for transparent, and the intensity is
    otherwise used as intensity of the replacement color.
    """
    int allegro_pink = bitmap_mask_color(colormask->bitmap)
    int x, y
    float ch, cs, v
    int r, g, b
    r = _land_active_display->color_r * 255
    g = _land_active_display->color_g * 255
    b = _land_active_display->color_b * 255
    rgb_to_hsv(r, g, b, &ch, &cs, &v)

    for x = 0; x < self->bitmap->w; x++:
        for y = 0; y < self->bitmap->h; y++:
            int col = getpixel(colormask->bitmap, x, y)
            if col != allegro_pink:
                float h, s
                rgb_to_hsv(getr(col), getg(col), getb(col), &h, &s, &v)
                hsv_to_rgb(ch, cs, v, &r, &g, &b)
                putpixel(self->bitmap, x, y, makecol(r, g, b))

int def land_image_colorize_replace(LandImage *self, int n, int *rgb):
    """
    Like land_image_colorize, but instead of a mask, a list of colors to
    colorize is given (and intensity is taken from those colors). The colors use
    integer 0..255 format, since exact comparison with the usual floating point
    colors would be difficult otherwise. The array ''rgb'' should have 3 * n
    integers, consisting of consecutive R, G, B triplets to replace.
    """
    int modified = 0
    int x, y
    float ch, cs, v
    int r, g, b
    r = _land_active_display->color_r * 255
    g = _land_active_display->color_g * 255
    b = _land_active_display->color_b * 255
    rgb_to_hsv(r, g, b, &ch, &cs, &v)

    for x = 0; x < self->bitmap->w; x++:
        for y = 0; y < self->bitmap->h; y++:
            int col = getpixel(self->bitmap, x, y)
            int cr = getr(col)
            int cg = getg(col)
            int cb = getb(col)
            int a = geta(col)
            for int i = 0; i < n; i++:
                if rgb[i * 3] == cr and rgb[i * 3 + 1] == cg and\
                    rgb[i * 3 + 2] == cb:
                    modified += 1
                    float h, s
                    rgb_to_hsv(cr, cg, cb, &h, &s, &v)
                    hsv_to_rgb(ch, cs, v, &r, &g, &b)
                    putpixel(self->bitmap, x, y, makeacol(r, g, b, a))
                    break
    if modified: land_image_prepare(self)
    return modified

LandImage *def land_image_split_mask_from_colors(LandImage *self, int n_rgb,
    int *rgb):
    """
    Takes the same parameters as land_image_colorize_replace - but instead of
    recoloring the image itself, creates a separate image of the same size,
    which is transparent except where mask colors have been found in the
    given image. Here, it is colored in graylevels with the intensity
    corresponding to the mask colors. In the original image, all mask colors
    are replaced by transparency.
    The use of this function is to always draw the mask over the original
    image, but tint the white mask to other colors.
    """
    LandImage *mask = land_display_new_image()
    mask->filename = None
    mask->name = None
    mask->x = self->x
    mask->y = self->y
    mask->l = self->l
    mask->t = self->t
    mask->r = self->r
    mask->b = self->b

    int w = self->bitmap->w
    int h = self->bitmap->h
    BITMAP *bmp = create_bitmap_ex(32, w, h)
    clear_to_color(bmp, makeacol(0, 0, 0, 0))
    mask->memory_cache = bmp
    mask->bitmap = bmp
    land_log_message("land_image_split_mask_from_colors %d x %d x %d.\n", w, h,
        bitmap_color_depth(bmp))
    
    for int x = 0; x < self->bitmap->w; x++:
        for int y = 0; y < self->bitmap->h; y++:
            int col = getpixel(self->bitmap, x, y)
            int cr = getr(col)
            int cg = getg(col)
            int cb = getb(col)
            int a = geta(col)
            for int i = 0; i < n_rgb; i++:
                if rgb[i * 3] == cr and rgb[i * 3 + 1] == cg and\
                    rgb[i * 3 + 2] == cb:
                    float hue, sat, val
                    rgb_to_hsv(cr, cg, cb, &hue, &sat, &val)
                    int r, g, b
                    hsv_to_rgb(hue, 0, val, &r, &g, &b)
                    putpixel(self->memory_cache, x, y, makeacol(cr, cg, cb, 0))
                    putpixel(mask->memory_cache, x, y, makeacol(r, g, b, a))
                    break

    float red, green, blue, alpha
    int n = land_image_color_stats(mask, &red, &green, &blue, &alpha)
    land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
    land_image_prepare(self)
    land_image_prepare(mask)
    return mask

def land_image_prepare(LandImage *self):
    """
    This is used to convert image data into a device dependent format, which
    is used to display the image (instead of the raw R/G/B/A values). Usually
    this is not needed, but it can be useful for certain optimizations, where
    the automatic synchronization is circumvented.
    """
    self->vt->prepare(self)

static int def callback(const char *filename, int attrib, void *param):
    LandArray **filenames = param
    land_array_add_data(filenames, land_strdup(filename))
    return 0

static int def compar(void const *a, void const *b):
    char *an = *(char **)a
    char *bn = *(char **)b
    return ustrcmp(an, bn)

LandArray *def land_load_images(char const *pattern, int center, int optimize):
    """
    Load all images matching the file name pattern, and create an array
    referencing them all.
    """
    LandArray *filenames = NULL
    int count = 0
    if _land_datafile:
        count = land_datafile_for_each_entry(_land_datafile, pattern, callback,
            &filenames)

    if !count:
        count = for_each_file_ex(pattern, 0, 0, callback, &filenames)

    qsort(filenames->data, count, sizeof (void *), compar)
    
    LandArray *array = NULL
    int i
    for i = 0; i < filenames->count; i++:
        char *filename = land_array_get_nth(filenames, i)
        LandImage *image = land_image_load(filename)
        land_free(filename)
        if center: land_image_center(image)
        if optimize: land_image_optimize(image)
        land_array_add_data(&array, image)

    land_array_destroy(filenames)
    return array

LandImage *def land_image_sub(LandImage *parent, float x, float y, float w, float h):
    LandImage *self = land_display_new_image()
    self->flags |= LAND_SUBIMAGE
    self->vt->sub(self, parent)
    self->bitmap = parent->bitmap
    self->memory_cache = parent->memory_cache
    self->l = x
    self->t = y
    self->r = land_image_width(parent) - x - w
    self->b = land_image_height(parent) - y - h
    self->x = x
    self->y = y
    return self

# Loads an image, and returns a list of sub-images out of it. 
LandArray *def land_image_load_sheet(char const *filename, int offset_x, int offset_y,
    int grid_w, int grid_h, int x_gap, int y_gap, int x_count, int y_count,
    int auto_crop):
    # FIXME: how can the sheet be destroyed again?
    LandArray *array = NULL
    LandImage *sheet = land_image_load(filename)
    if !sheet: return NULL
    int x, y, i, j
    for j = 0; j < y_count; j++:
        for i = 0; i < x_count; i++:
            x = offset_x + i * (grid_w + x_gap)
            y = offset_y + j * (grid_h + y_gap)
            LandImage *sub = land_image_sub(sheet, x, y, grid_w, grid_h)
            land_array_add_data(&array, sub)

    if _cb: _cb(filename, sheet)
    return array

# Loads multiple images out of a single file. 
LandArray *def land_image_load_split_sheet(char const *filename, int offset_x, int offset_y,
    int grid_w, int grid_h, int x_gap, int y_gap, int x_count, int y_count,
    int auto_crop):
    LandArray *array = NULL
    LandImage *sheet = land_image_load(filename)
    if !sheet: return NULL
    int x, y, i, j
    for j = 0; j < y_count; j++:
        for i = 0; i < x_count; i++:
            x = offset_x + i * (grid_w + x_gap)
            y = offset_y + j * (grid_h + y_gap)
            LandImage *sub = land_image_new_from(sheet, x, y, grid_w, grid_h)
            land_array_add_data(&array, sub)


    land_image_del(sheet)
    return array

def land_image_draw_scaled_rotated_tinted(LandImage *self, float x, float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha):
    # FIXME
    # We cannot just use the image's vtable here. And we also cannot just use
    # the display's vtable. In fact, we might need another method for any
    # display/image combination. For now, if the display is an ImageDisplay,
    # we draw the image as if it were an LandImageAllegro, no matter what type
    # of image it is. In all other cases, we let the image vtable do whateve
    # it sees fit.
    if land_display_image_check(_land_active_display):
        land_image_allegro_draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, r, g, b, alpha)
    else:
        self->vt->draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, r, g, b, alpha)

def land_image_draw_scaled_rotated(LandImage *self, float x, float y, float sx, float sy,
    float angle):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, 1, 1, 1, 1)

def land_image_draw_scaled(LandImage *self, float x, float y, float sx, float sy):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, 1, 1, 1, 1)

def land_image_draw_rotated(LandImage *self, float x, float y, float a):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, a, 1, 1, 1, 1)

def land_image_draw_scaled_tinted(LandImage *self, float x, float y, float sx, float sy,
    float r, float g, float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, r, g, b, alpha)

def land_image_draw(LandImage *self, float x, float y):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, 1, 1, 1, 1)

def land_image_draw_tinted(LandImage *self, float x, float y, float r, float g,
    float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, r, g, b, alpha)

def land_image_grab(LandImage *self, int x, int y):
    self->vt->grab(self, x, y)

def land_image_grab_into(LandImage *self, int x, int y, int tx, int ty, int tw, int th):
    self->vt->grab_into(self, x, y, tx, ty, tw, th)

def land_image_offset(LandImage *self, int x, int y):
    self->x = x
    self->y = y

def land_image_center(LandImage *self):
    self->x = self->bitmap->w / 2
    self->y = self->bitmap->h / 2

def land_image_init():
    land_image_allegro_init()
    land_image_allegrogl_init()
    active = 1

def land_image_exit():
    land_image_allegrogl_exit()
    land_image_allegro_exit()
    active = 0

int def land_image_active():
    return active

# Set's a source clip rectangle for the image. That is, only the specified
# rectangle out of the image will actually be used when this image is drawn
# somewhere.
# 
def land_image_clip(LandImage *self, float x, float y, float x_, float y_):
    self->l = x
    self->t = y
    self->r = self->bitmap->w - x_
    self->b = self->bitmap->h - y_

# Just a shortcut for land_image_clip(image, 0, 0, 0, 0); 
def land_image_unclip(LandImage *self):
    self->l = 0
    self->t = 0
    self->r = 0
    self->b = 0

int def land_image_height(LandImage *self):
    return self->bitmap->h

int def land_image_width(LandImage *self):
    return self->bitmap->w

# Optimizes a bitmap to take only as little space as necesary, whilst
# maintaining the correct offset.
# 
static BITMAP *def optimize_bitmap(BITMAP *bmp, int *x, int *y):
    int l = bmp->w
    int r = -1
    int t = bmp->h
    int b = -1
    int i, j
    for j = 0; j < bmp->h; j++:
        for i = 0; i < bmp->w; i++:
            if getpixel(bmp, i, j) != bitmap_mask_color(bmp):
                if i < l: l = i
                if j < t: t = j
                if i > r: r = i
                if j > b: b = j



    BITMAP *optimized = create_bitmap(1 + r - l, 1 + b - t)
    blit(bmp, optimized, l, t, 0, 0, optimized->w, optimized->h)
    # E.g. our image is 20x20, and x/y is 10/10, if now l/t is 10/10,
    # then x/y becomes 0/0.
    *x -= l
    *y -= t
    return optimized

def land_image_optimize(LandImage *self):
    printf("FIXME: land_image_optimize\n")
    int offx = 0, offy = 0
    BITMAP *opt = optimize_bitmap(self->memory_cache, &offx, &offy)
    # FIXME: self->bitmap
    destroy_bitmap(self->memory_cache)
    self->memory_cache = opt

    self->x += offx
    self->y += offy

    # FIXME: source clip rect?

    self->vt->prepare(self)
