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

# TODO
class LandSubImage:
    LandImage super
    LandImage *parent
    float x, y, w, h

static import global string
static import display, data, allegro/image, allegrogl/image

extern LandDataFile *_land_datafile

static void (*_cb)(char const *path, LandImage *image)

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

# Returns the number of pixels in the image, and the average red, green, blue
# and alpha component.
# 
int def land_image_color_stats(LandImage *self, float *red, float *green, float *blue, float *alpha):
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

# Colorizes the part of the image specified by the mask with the current color. 
def land_image_colorize(LandImage *self, LandImage *colormask):
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




def land_image_prepare(LandImage *self):
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

def land_image_exit():
    land_image_allegrogl_exit()
    land_image_allegro_exit()

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