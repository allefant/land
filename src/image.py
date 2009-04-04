import array, log, pixelmask, util
static import global assert

macro LAND_SUBIMAGE 1
macro LAND_LOADED 2

class LandImage:
    """
    An image is a rectangular area of pixels. The actual representation
    of the pixel data is completely left to the plaform specific layer.
    An OpenGL driver most likely will have a memory buffer with the
    raw RGBA data of the image attached to each LandImage, along with
    a texture id for displaying it and an FBO id for drawing to it.
    """
    char *filename
    char *name

    int flags

    LandPixelMask *mask; # Bit-mask of the image.

    int width, height
    float x, y; # Offset to origin. 

    float l, t, r, b; # Cut-away left, top, right, bottom. 

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

static import allegro5/a5_image

extern LandDataFile *_land_datafile

static void (*_cb)(char const *path, LandImage *image)

def land_image_set_callback(void (*cb)(char const *path, LandImage *image)):
    _cb = cb

LandImage *def land_image_load(char const *filename):
    land_log_message("land_image_load %s..", filename)

    LandImage *self = platform_image_load(filename)

    if self->flags & LAND_LOADED:
        int w = land_image_width(self)
        int h = land_image_height(self)
        land_log_message_nostamp("success (%d x %d)\n", w, h)
        land_image_prepare(self)

        float red, green, blue, alpha
        int n
        n = land_image_color_stats(self, &red, &green, &blue, &alpha)
        land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
    else:
        land_log_message_nostamp("failure\n")

    if _cb: _cb(filename, self)
    return self

LandImage *def land_image_memory_new(int w, int h):
    """
    Creates a new image. If w or h are 0, the image will have no contents at
    all (this can be useful if the contents are to be added later).
    The image will always be a simple memory rectangle of pixels, with no
    driver specific optimizations.
    """
    assert(0)
    return None

LandImage *def land_image_new(int w, int h):
    """
    Creates a new image. If w and h are 0, the image will have no contents at
    all (this can be useful if the contents are to be added later).
    """
    LandImage *self = land_display_new_image()
    self->width = w
    self->height = h
    if w or h:
        platform_image_empty(self)
    return self

LandImage *def land_image_create(int w, int h):
    """
    Like land_image_new, but clears the image to all 0 initially.
    """
    LandImage *self = land_display_new_image()
    self->width = w
    self->height = h
    platform_image_empty(self)
    return self

def land_image_del(LandImage *self):
    land_image_destroy_pixelmasks(self)
    if self->name: land_free(self->name)
    if self->filename && self->filename != self->name: land_free(self->filename)
    land_display_del_image(self)

def land_image_destroy(LandImage *self):
    land_image_del(self)

def land_image_crop(LandImage *self, int x, y, w, h):
    """
    Crops an image to the specified rectangle. All image contents outside the
    rectangle will be lost. You can also use this to make an image larger, in
    which case the additional borders are filled with transparency. The offset
    need not lie within the image.
    """
    if self->width == w and self->height == h and x == 0 and y == 0:
        return
    platform_image_crop(self, x, y, w, h)

def land_image_auto_crop(LandImage *self):
    """
    This will optimize an image by cropping away any completely transparent
    borders it may have.
    """
    assert(0)

LandImage *def land_image_new_from(LandImage *copy, int x, int y, int w, int h):
    """
    Create a new image, copying pixel data from a rectangle in an existing
    image.
    """
    land_log_message("land_image_new_from %s..", copy->name)

    LandImage *self = land_image_new(w, h)
    land_set_image_display(self)
    land_image_draw_partial(copy, 0, 0, x, y, w, h)
    land_unset_image_display()
    
    land_log_message_nostamp("success (%d x %d)\n", w, h)

    float red, green, blue, alpha
    int n
    n = land_image_color_stats(self, &red, &green, &blue, &alpha)
    land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
    
    return self

int def land_image_color_stats(LandImage *self,
    float *red, *green, *blue, *alpha):
    """
    Returns the number of pixels in the image, and the average red, green, blue
    and alpha component. 
    """
    int n = 0
    int w = land_image_width(self)
    int h = land_image_height(self)
    *red = 0
    *green = 0
    *blue = 0
    *alpha = 0
    unsigned char rgba[w * h * 4]
    land_image_get_rgba_data(self, rgba)
    int p = 0
    for int j = 0; j < h; j++:
        for int i = 0; i < w; i++:
            *red += rgba[p++] * 1.0 / 255.0
            *green += rgba[p++] * 1.0 / 255.0
            *blue += rgba[p++] * 1.0 / 255.0
            *alpha += rgba[p++] * 1.0 / 255.0
            n++

    return n

def land_image_color_replace(LandImage *self, int r255, int g255, int b255,
    int a255, int _r255, int _g255, int _b255, int _a255):
    """
    Replaces a color with another.
    """
    assert(0)

def land_image_colorkey(LandImage *self, int r255, int g255, int b255):
    """
    Replaces all pixels in the image matching the given RGB triplet (in 0..255
    format) with full transparency.
    """
    assert(0)

def land_image_colorkey_hack(LandImage *self, int allegro_color):
    """
    Like land_image_colorkey, but even more hackish, you directly specify
    the color in Allegro's format. The only use for this is if you load
    paletted pictures and want to colorkey by index.
    """
    assert(0)

def land_image_colorize(LandImage *self, LandImage *colormask):
    """
    Colorizes the part of the image specified by the mask with the current
    color. The mask uses (1, 0, 1) for transparent, and the intensity is
    otherwise used as intensity of the replacement color.
    """
    assert(0)

def land_image_colorize_replace(LandImage *self, int n, int *rgb):
    """
    This takes a list of colors and replaces all colors in the image
    corresponding to one of them with the current color.

    The colors use integer 0..255 format, since exact comparison with
    the usual floating point colors would be difficult otherwise. The
    array ''rgb'' should have 3 * n integers, consisting of consecutive
    R, G, B triplets to replace.
    """
    int w = land_image_width(self)
    int h = land_image_height(self)
    unsigned char rgba[w * h * 4]
    land_image_get_rgba_data(self, rgba)
    unsigned char *p = rgba
    
    float fr, fg, fb, fa
    land_get_color(&fr, &fg, &fb, &fa)
    int red = fr * 255
    int green = fg * 255
    int blue = fb * 255
    
    int base_red = rgb[0]
    int base_green = rgb[1]
    int base_blue = rgb[2]
    int base_sum = base_red + base_green + base_blue

    for int y = 0; y < h; y++:
        for int x = 0; x < w; x++:
            int r = *(p + 0)
            int g = *(p + 1)
            int b = *(p + 2)
            for int i = 0; i < n; i++:
                if rgb[i * 3 + 0] == r and \
                    rgb[i * 3 + 1] == g and \
                    rgb[i * 3 + 2] == b:
                    int sum = r + g + b
                    int nr, ng, nb
                    if sum <= base_sum:
                        nr = red * sum / base_sum
                        ng = green * sum / base_sum
                        nb = blue * sum / base_sum
                    else:
                        nr = 255 - (255 - red) * base_sum / sum
                        ng = 255 - (255 - green) * base_sum / sum
                        nb = 255 - (255 - blue) * base_sum / sum
                    *(p + 0) = r
                    *(p + 1) = g
                    *(p + 2) = b
            p += 4

    land_image_set_rgba_data(self, rgba)

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
    assert(0)

def land_image_prepare(LandImage *self):
    """
    This is used to convert image data into a device dependent format, which
    is used to display the image (instead of the raw R/G/B/A values). Usually
    this is not needed, but it can be useful for certain optimizations, where
    the automatic synchronization is circumvented.
    """
    platform_image_prepare(self)

static int def callback(const char *filename, int attrib, void *param):
    LandArray **filenames = param
    land_array_add_data(filenames, land_strdup(filename))
    return 0

static int def compar(void const *a, void const *b):
    char *an = *(char **)a
    char *bn = *(char **)b
    return ustrcmp(an, bn)

LandArray *def land_load_images_cb(char const *pattern,
    void (*cb)(LandImage *image, void *data), void *data):
    """
    Load all images matching the file name pattern, and create an array
    referencing them all, in alphabetic filename order. The callback function
    is called on each image along the way.
    """
    assert(0)
    LandArray *filenames = None
    int count = 0
    if _land_datafile:
        count = land_datafile_for_each_entry(_land_datafile, pattern, callback,
            &filenames)

    # if !count:
    #    count = for_each_file_ex(pattern, 0, 0, callback, &filenames)

    if not filenames: return None

    qsort(filenames->data, count, sizeof (void *), compar)
    
    LandArray *array = None
    int i
    for i = 0; i < filenames->count; i++:
        char *filename = land_array_get_nth(filenames, i)
        LandImage *image = land_image_load(filename)
        land_free(filename)
        if image:
            if cb: cb(image, data)
            land_array_add_data(&array, image)

    land_array_destroy(filenames)
    return array

static def defcb(LandImage *image, void *p):
    int *data = p
    if data[0]: land_image_center(image)
    if data[1]: land_image_optimize(image)

LandArray *def land_load_images(char const *pattern, int center, int optimize):
    """
    Load all images matching the file name pattern, and create an array
    referencing them all.
    """
    int data[2] = {center, optimize}
    return land_load_images_cb(pattern, defcb, data)

LandImage *def land_image_sub(LandImage *parent, float x, float y, float w, float h):
    LandImage *self = land_display_new_image()
    self->flags |= LAND_SUBIMAGE
    
    assert(0)
    
    #self->vt->sub(self, parent)

    #self->bitmap = parent->bitmap
    #self->memory_cache = parent->memory_cache
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
LandArray *def land_image_load_split_sheet(char const *filename, int offset_x,
    int offset_y, int grid_w, int grid_h, int x_gap, int y_gap, int x_count,
    int y_count, int auto_crop):
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

def land_image_draw_scaled_rotated_tinted(LandImage *self, float x,
    float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha):
    platform_image_draw_scaled_rotated_tinted(self, x, y, sx, sy,
        angle, r, g, b, alpha)

def land_image_draw_scaled_rotated(LandImage *self, float x, float y, float sx, float sy,
    float angle):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, 1, 1, 1, 1)

def land_image_draw_scaled(LandImage *self, float x, float y, float sx, float sy):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, 1, 1, 1, 1)

def land_image_draw_rotated(LandImage *self, float x, float y, float a):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, a, 1, 1, 1, 1)

def land_image_draw_rotated_tinted(LandImage *self, float x, y, a, r, g, b, alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, a, r, g, b, alpha)

def land_image_draw_scaled_tinted(LandImage *self, float x, float y, float sx, float sy,
    float r, float g, float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, r, g, b, alpha)

def land_image_draw(LandImage *self, float x, float y):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, 1, 1, 1, 1)

def land_image_draw_tinted(LandImage *self, float x, float y, float r, float g,
    float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, r, g, b, alpha)

def land_image_grab(LandImage *self, int x, int y):
    platform_image_grab_into(self, x, y, 0, 0, self->width, self->height)

def land_image_grab_into(LandImage *self, float x, y, tx, ty, tw, th):
    platform_image_grab_into(self, x, y, tx, ty, tw, th)

def land_image_offset(LandImage *self, int x, int y):
    self->x = x
    self->y = y

def land_image_memory_draw(LandImage *self, float x, float y):
    assert(0)

def land_image_center(LandImage *self):
    self->x = 0.5 * self->width
    self->y = 0.5 * self->height

def land_image_init():
    pass

def land_image_exit():
    pass

# Set's a source clip rectangle for the image. That is, only the specified
# rectangle out of the image will actually be used when this image is drawn
# somewhere.
# 
def land_image_clip(LandImage *self, float x, float y, float x_, float y_):
    self->l = x
    self->t = y
    self->r = self->width - x_
    self->b = self->height - y_

# Just a shortcut for land_image_clip(image, 0, 0, 0, 0); 
def land_image_unclip(LandImage *self):
    self->l = 0
    self->t = 0
    self->r = 0
    self->b = 0

def land_image_draw_partial(LandImage *self, float x, y, sx, sy, sw, sh):
    float l = self->l
    float t = self->t
    float r = self->r
    float b = self->b
    land_image_clip(self, sx, sy, sx + sw, sy + sh)
    land_image_draw(self, x - sx, y - sy)
    self->l = l
    self->t = t
    self->r = r
    self->b = b

int def land_image_height(LandImage *self):
    return self->height

int def land_image_width(LandImage *self):
    return self->width

# Optimizes a bitmap to take only as little space as necesary, whilst
# maintaining the correct offset.
static LandImage *def optimize_bitmap(LandImage *self, int *x, int *y):
    assert(0)

def land_image_optimize(LandImage *self):
    assert(0)

def land_image_get_rgba_data(LandImage *self, unsigned char *rgba):
    platform_image_get_rgba_data(self, rgba)

def land_image_set_rgba_data(LandImage *self, unsigned char const *rgba):
    platform_image_set_rgba_data(self, rgba)

def land_image_save(LandImage *self, char const *filename):
    platform_image_save(self, filename)

int def land_image_opengl_texture(LandImage *self):
    return platform_image_opengl_texture(self)
