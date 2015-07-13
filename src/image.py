import array, log, pixelmask, file, util, buffer
static import global assert

macro LAND_SUBIMAGE 1
macro LAND_LOADED 2
macro LAND_IMAGE_WAS_CENTERED 4 # Used in the level editor only.

static macro LOG_COLOR_STATS 0

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

    LandPixelMask *mask # Bit-mask of the image.

    int width, height
    float x, y # Offset to origin. 

    float l, t, r, b # Cut-away left, top, right, bottom. 

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

static int bitmap_count, bitmap_memory

def land_image_set_callback(void (*cb)(char const *path, LandImage *image)):
    _cb = cb

static LandImage *def _load(char const *filename, bool mem):
    char *path = land_path_with_prefix(filename)
    land_log_message("land_image_load %s..", path)

    LandImage *self = platform_image_load(path, mem)

    land_free(path)

    if self.flags & LAND_LOADED:
        int w = land_image_width(self)
        int h = land_image_height(self)
        land_log_message_nostamp("success (%d x %d)\n", w, h)

        if not mem:
            land_image_prepare(self)
            
        land_log_message("prepared\n")

        *** "ifdef" LOG_COLOR_STATS
        float red = 0, green = 0, blue = 0, alpha = 0
        int n = 1
        n = land_image_color_stats(self, &red, &green, &blue, &alpha)
        land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
        *** "endif"

        bitmap_count++
        bitmap_memory += w * h * 4
        land_log_message(" %d bitmaps (%.1fMB).\n", bitmap_count, bitmap_memory / 1024.0 / 1024.0)
    else:
        land_log_message_nostamp("failure\n")

    if _cb: _cb(filename, self)
    return self

LandImage *def land_image_load(char const *filename):
    return _load(filename, False)

LandImage *def land_image_load_memory(char const *filename):
    return _load(filename, True)

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
    self.width = w
    self.height = h
    if w or h:
        platform_image_empty(self)
    bitmap_count++
    bitmap_memory += w * h * 4
    return self

LandImage *def land_image_create(int w, int h):
    """
    Like land_image_new, but clears the image to all 0 initially.
    """
    LandImage *self = land_display_new_image()
    self.width = w
    self.height = h
    platform_image_empty(self)
    bitmap_count++
    bitmap_memory += w * h * 4
    return self

def land_image_del(LandImage *self):
    if not self: return
    # Sub-bitmaps have no own names or masks or anything. They are
    # just a reference with their own cut-out rectangle.
    if not (self.flags & LAND_SUBIMAGE):
        land_image_destroy_pixelmasks(self)
        if self.name: land_free(self->name)
        if self.filename and self->filename != self->name: land_free(self->filename)
        bitmap_count--
        bitmap_memory -= self.width * self->height * 4
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
    if self.width == w and self->height == h and x == 0 and y == 0:
        return
    platform_image_crop(self, x, y, w, h)

def land_image_auto_crop(LandImage *self):
    """
    This will optimize an image by cropping away any completely transparent
    borders it may have.
    """
    int w = land_image_width(self)
    int h = land_image_height(self)
    unsigned char *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba)
    int mini = w
    int maxi = -1
    int minj = h
    int maxj = -1
    for int j = 0 while j < h with j++:
        uint32_t *row = (void *)(rgba + j * w * 4)
        for int i = 0 while i < w with i++:
            if row[i] & 0xff000000:
                if i < mini: mini = i
                if i > maxi: maxi = i
                if j < minj: minj = j
                if j > maxj: maxj = j
    land_free(rgba)
    if maxi == -1:
        mini = maxi = minj = maxj = 0
    self.l = mini
    self.t = minj
    self.r = w - 1 - maxi
    self.b = h - 1 - maxj

LandImage *def land_image_new_from(LandImage *copy, int x, int y, int w, int h):
    """
    Create a new image, copying pixel data from a rectangle in an existing
    image.
    """
    land_log_message("land_image_new_from %s..", copy->name)

    LandImage *self = land_image_new(w, h)
    land_set_image_display(self)

    # blending changes only for image display which is destroyed a line later
    land_blend(LAND_BLEND_SOLID)

    land_image_draw_partial(copy, copy->x, copy->y, x, y, w, h)
    land_unset_image_display()
    
    land_log_message_nostamp("success (%d x %d)\n", w, h)

    *** "ifdef" LOG_COLOR_STATS
    float red, green, blue, alpha
    int n
    n = land_image_color_stats(self, &red, &green, &blue, &alpha)
    land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
    *** "endif"

    land_log_message(" %d bitmaps (%.1fMB).\n", bitmap_count, bitmap_memory / 1024.0 / 1024.0)
    
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
    unsigned char *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba)
    int p = 0
    for int j = 0 while j < h with j++:
        for int i = 0 while i < w with i++:
            *red += rgba[p++] * 1.0 / 255.0
            *green += rgba[p++] * 1.0 / 255.0
            *blue += rgba[p++] * 1.0 / 255.0
            *alpha += rgba[p++] * 1.0 / 255.0
            n++
    land_free(rgba)
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

    The first rgb triplet has a special meaning - it determines the image color
    which is mapped to the current color. All matching colors with a larger
    rgb sum then are mapped to a color between the first color and pure weight,
    depending on their rgb sum. All colors with a smaller rgb sum are mapped
    to a range from total black to the first color.
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

    for int y = 0 while y < h with y++:
        for int x = 0 while x < w with x++:
            int r = *(p + 0)
            int g = *(p + 1)
            int b = *(p + 2)
            for int i = 0 while i < n with i++:
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
                        int isum = 255 * 3 - sum
                        int ibase_sum = 255 * 3 - base_sum
                        nr = 255 - (255 - red) * isum / ibase_sum
                        ng = 255 - (255 - green) * isum / ibase_sum
                        nb = 255 - (255 - blue) * isum / ibase_sum
                    *(p + 0) = nr
                    *(p + 1) = ng
                    *(p + 2) = nb
            p += 4

    land_image_set_rgba_data(self, rgba)
    land_image_prepare(self)

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
    return strcmp(an, bn)

static int def filter(char const *name, bool is_dir, void *data):
    char const *pattern = data
    if is_dir:
        return 2
    if land_fnmatch(pattern, name):
        return 1
    return 0

LandArray *def land_load_images_cb(char const *pattern,
    void (*cb)(LandImage *image, void *data), void *data):
    """
    Load all images matching the file name pattern, and create an array
    referencing them all, in alphabetic filename order. The callback function
    is called on each image along the way.
    """

    LandBuffer *dirbuf = land_buffer_new()
    int j = 0
    for int i = 0 while pattern[i] with i++:
        if pattern[i] == '/' or pattern[i] == '\\':
            land_buffer_add(dirbuf, pattern + j, i - j + 1)
            j = i + 1
        if pattern[i] == '?' or pattern[i] == '*': break
    char *dir = land_buffer_finish(dirbuf)

    LandArray *filenames = None
    int count = 0
    if _land_datafile:
        count = land_datafile_for_each_entry(_land_datafile, pattern, callback,
            &filenames)

    if not count:
        filenames = land_filelist(dir, filter, LAND_FULL_PATH, (void *)pattern)
        if filenames:
            count = filenames->count
        else:
            land_log_message("No files at all match %s.\n", pattern)

    land_free(dir)

    if not filenames: return None

    qsort(filenames->data, count, sizeof (void *), compar)

    LandArray *array = None
    int i
    for i = 0 while i < filenames->count with i++:
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
    if data[1]: land_image_auto_crop(image)

LandArray *def land_load_images(char const *pattern, int center, int auto_crop):
    """
    Load all images matching the file name pattern, and create an array
    referencing them all.
    """
    int data[2] = {center, auto_crop}
    return land_load_images_cb(pattern, defcb, data)

LandImage *def land_image_sub(LandImage *parent, float x, float y, float w, float h):
    LandImage *self = platform_image_sub(parent, x, y, w, h)
    return self

# Loads an image, and returns a list of sub-images out of it. 
LandArray *def land_image_load_sheet(char const *filename, int offset_x, int offset_y,
    int grid_w, int grid_h, int x_gap, int y_gap, int x_count, int y_count,
    int auto_crop):
    # FIXME: how can the sheet be destroyed again?
    LandArray *array = NULL
    LandImage *sheet = land_image_load(filename)
    if not sheet: return NULL
    int x, y, i, j
    for j = 0 while j < y_count with j++:
        for i = 0 while i < x_count with i++:
            x = offset_x + i * (grid_w + x_gap)
            y = offset_y + j * (grid_h + y_gap)
            LandImage *sub = land_image_sub(sheet, x, y, grid_w, grid_h)
            if auto_crop:
                land_image_auto_crop(sub)
            land_array_add_data(&array, sub)

    if _cb: _cb(filename, sheet)
    return array

# Loads multiple images out of a single file. 
LandArray *def land_image_load_split_sheet(char const *filename, int offset_x,
    int offset_y, int grid_w, int grid_h, int x_gap, int y_gap, int x_count,
    int y_count, int auto_crop):
    LandArray *array = NULL
    LandImage *sheet = land_image_load_memory(filename)
    if not sheet: return NULL
    int x, y, i, j
    for j = 0 while j < y_count with j++:
        for i = 0 while i < x_count with i++:
            x = offset_x + i * (grid_w + x_gap)
            y = offset_y + j * (grid_h + y_gap)
            LandImage *sub = land_image_new_from(sheet, x, y, grid_w, grid_h)
            land_array_add_data(&array, sub)

    land_image_del(sheet)
    return array

def land_image_draw_scaled_rotated_tinted_flipped(LandImage *self, float x,
    float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha, int flip):
    platform_image_draw_scaled_rotated_tinted_flipped(self, x, y, sx, sy,
        angle, r, g, b, alpha, flip)

def land_image_draw_scaled_rotated_tinted(LandImage *self, float x,
    float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha):
    land_image_draw_scaled_rotated_tinted_flipped(self, x, y, sx, sy,
        angle, r, g, b, alpha, 0)

def land_image_draw_scaled_rotated(LandImage *self, float x, float y, float sx, float sy,
    float angle):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, angle, 1, 1, 1, 1)

def land_image_draw_scaled(LandImage *self, float x, float y, float sx, float sy):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, 1, 1, 1, 1)

def land_image_draw_rotated(LandImage *self, float x, float y, float a):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, a, 1, 1, 1, 1)

def land_image_draw_rotated_flipped(LandImage *self, float x, float y, float a):
    land_image_draw_scaled_rotated_tinted_flipped(self, x, y, 1, 1, a, 1, 1, 1, 1, 1)

def land_image_draw_rotated_tinted(LandImage *self, float x, y, a, r, g, b, alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, a, r, g, b, alpha)

def land_image_draw_scaled_tinted(LandImage *self, float x, float y, float sx, float sy,
    float r, float g, float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, sx, sy, 0, r, g, b, alpha)

def land_image_draw(LandImage *self, float x, float y):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, 1, 1, 1, 1)

def land_image_draw_flipped(LandImage *self, float x, float y):
    land_image_draw_scaled_rotated_tinted_flipped(self, x, y, 1, 1, 0, 1, 1, 1, 1, 1)

def land_image_draw_tinted(LandImage *self, float x, float y, float r, float g,
    float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, r, g, b, alpha)

def land_image_grab(LandImage *self, int x, int y):
    platform_image_grab_into(self, x, y, 0, 0, self.width, self->height)

def land_image_grab_into(LandImage *self, float x, y, tx, ty, tw, th):
    platform_image_grab_into(self, x, y, tx, ty, tw, th)

def land_image_offset(LandImage *self, int x, int y):
    self.x = x
    self.y = y

def land_image_memory_draw(LandImage *self, float x, float y):
    assert(0)

def land_image_center(LandImage *self):
    self.x = 0.5 * self->width
    self.y = 0.5 * self->height
    self.flags |= LAND_IMAGE_WAS_CENTERED

def land_image_init():
    pass

def land_image_exit():
    pass

# Set's a source clip rectangle for the image. That is, only the specified
# rectangle out of the image will actually be used when this image is drawn
# somewhere.
# 
def land_image_clip(LandImage *self, float x, float y, float x_, float y_):
    self.l = x
    self.t = y
    self.r = self->width - x_
    self.b = self->height - y_

# Just a shortcut for land_image_clip(image, 0, 0, 0, 0); 
def land_image_unclip(LandImage *self):
    self.l = 0
    self.t = 0
    self.r = 0
    self.b = 0

def land_image_draw_partial(LandImage *self, float x, y, sx, sy, sw, sh):
    float l = self.l
    float t = self.t
    float r = self.r
    float b = self.b
    land_image_clip(self, sx, sy, sx + sw, sy + sh)
    land_image_draw(self, x - sx, y - sy)
    self.l = l
    self.t = t
    self.r = r
    self.b = b

int def land_image_height(LandImage *self):
    return self.height

int def land_image_width(LandImage *self):
    return self.width

def land_image_get_rgba_data(LandImage *self, unsigned char *rgba):
    platform_image_get_rgba_data(self, rgba)

def land_image_set_rgba_data(LandImage *self, unsigned char const *rgba):
    """
    Copies the rgba data, overwriting the image contents. Since data are copied
    rgba can be safely deleted after returning from the function.
    """
    platform_image_set_rgba_data(self, rgba)

def land_image_save(LandImage *self, char const *filename):
    platform_image_save(self, filename)

int def land_image_opengl_texture(LandImage *self):
    return platform_image_opengl_texture(self)

# FIXME: for odd width
def land_image_flip(LandImage *self):
    int w = land_image_width(self)
    int h = land_image_height(self)
    unsigned char *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba)
    for int j = 0 while j < h with j++:
        uint32_t *row = (void *)(rgba + j * w * 4)
        for int i = 0 while i < w / 2 with i++:
            uint32_t temp = row[i]
            row[i] = row[w - 1 - i]
            row[w - 1 - i] = temp

    land_image_set_rgba_data(self, rgba)
    land_free(rgba)
   
LandImage *def land_image_clone(LandImage *self):
    int w = land_image_width(self)
    int h = land_image_height(self)
    LandImage *clone = land_image_new(w, h)
    unsigned char *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba)
    land_image_set_rgba_data(clone, rgba)
    land_free(rgba)
    clone->x = self.x
    clone->y = self.y
    return clone

def land_image_fade_to_color(LandImage *self):
    int w = land_image_width(self)
    int h = land_image_height(self)
    unsigned char *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba)
    
    float fr, fg, fb, fa
    land_get_color(&fr, &fg, &fb, &fa)
    int red = fr * 255
    int green = fg * 255
    int blue = fb * 255
    int alpha = fa * 255
    
    for int j = 0 while j < h with j++:
        unsigned char *row = rgba + j * w * 4
        for int i = 0 while i < w with i++:
            int a = row[i * 4 + 3]
            if not a: continue
            int ar = row[i * 4 + 0]
            int ag = row[i * 4 + 1]
            int ab = row[i * 4 + 2]
            row[i * 4 + 0] = (red * alpha * a + ar * (255 - alpha) * 255) / (255 * 255)
            row[i * 4 + 1] = (green * alpha * a + ag * (255 - alpha) * 255) / (255 * 255)
            row[i * 4 + 2] = (blue * alpha * a + ab * (255 - alpha) * 255) / (255 * 255)

    land_image_set_rgba_data(self, rgba)
    land_free(rgba)
    
