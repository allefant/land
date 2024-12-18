import common
import array, log, pixelmask, file, util, buffer
static import global assert

macro LAND_SUBIMAGE 1
macro LAND_LOADED 2
macro LAND_IMAGE_WAS_CENTERED 4 # Used in the level editor only.
macro LAND_IMAGE_MEMORY 8
macro LAND_AUTOCROP 16
macro LAND_FAILED 32
macro LAND_IMAGE_CENTER 64 # center on load
macro LAND_IMAGE_DEPTH 128 # image has depth buffer
macro LAND_LOADING 256 # async loading in progress
macro LAND_LOADING_COMPLETE 512 # async loading complete
macro LAND_NO_PREMUL 1024
macro LAND_IMAGE_DEPTH32 2048 # image has 32-bit depth buffer
macro LAND_IMAGE_WANT_CACHE 4096 # image should be cached
macro LAND_IMAGE_FROM_CACHE 8192 # image is in the cache

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

LandHash *_loaded_cache

static import global string
static import display, data

static import allegro5/a5_image
static import land.thread

static void (*_cb)(char const *path, LandImage *image)

static int bitmap_count, bitmap_memory
LandThread *_loader_thread
LandLock *_loader_event
LandLock *_loader_mutex
LandArray *_loader_queue

def land_image_set_callback(void (*cb)(char const *path, LandImage *image)):
    _cb = cb

def _load_prep(str filename) -> LandImage*:
    char *path = land_path_with_prefix(filename)
    if _loaded_cache and land_hash_has(_loaded_cache, path):
        LandImage *self = land_hash_get(_loaded_cache, path)
        self.flags |= LAND_IMAGE_FROM_CACHE
        land_log_message("land_image_load %s: CACHED\n", path)
        return self
    land_log_message("land_image_load %s..\n", path)
    LandImage *self = land_display_new_image()
    self.filename = land_strdup(path)
    land_free(path)
    bitmap_count++
    return self

def _load(char const *filename, bool mem) -> LandImage *:
    auto self = _load_prep(filename)
    _load2(self)
    return self

def _cache(LandImage *self):
    if not _loaded_cache:
        _loaded_cache = land_hash_new()
    land_hash_insert(_loaded_cache, self.filename, self)
    self.flags |= LAND_IMAGE_FROM_CACHE # it's also a cached image now

def _load2(LandImage *self):
    if self.flags & LAND_IMAGE_FROM_CACHE:
        # it's already loaded
        # Note: we ignore different flags etc. - when using the cache
        # each filename gets an entry, loading the same name with
        # different flags is not supported.
        return
    platform_image_load_on_demand(self)

    if self.flags & LAND_LOADED:
        int w = land_image_width(self)
        int h = land_image_height(self)
        land_log_message("loading %s success (%d x %d)\n",
            self.filename, w, h)

        if self.flags & LAND_IMAGE_CENTER:
            land_image_center(self)

        if self.flags & LAND_AUTOCROP:
            land_image_auto_crop(self)
            
        land_log_message(" crop l=%.0f, t=%.0f, r=%.0f, b=%.0f\n",
            self.l, self.t, self.r, self.b)

        *** "ifdef" LOG_COLOR_STATS
        float red = 0, green = 0, blue = 0, alpha = 0
        int n = 1
        n = land_image_color_stats(self, &red, &green, &blue, &alpha)
        land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
        *** "endif"

        bitmap_memory += w * h * 4
        land_log_message(" %d bitmaps (%.1fMB).\n", bitmap_count, bitmap_memory / 1024.0 / 1024.0)
        if self.flags & LAND_IMAGE_WANT_CACHE:
            _cache(self)
    else:
        land_log_message_nostamp("failure\n")

    if _cb: _cb(self.filename, self)

def land_image_load(char const *filename) -> LandImage *:
    return _load(filename, False)

def land_image_was_loaded(LandImage *self) -> bool:
    return (self.flags & LAND_LOADED) != 0

def land_image_load_memory(char const *filename) -> LandImage *:
    return _load(filename, True)

def land_image_load_no_premul(str filename) -> LandImage*:
    auto image = _load_prep(filename)
    image.flags |= LAND_NO_PREMUL
    _load2(image)
    return image

def land_image_load_cached(str filename) -> LandImage*:
    auto image = _load_prep(filename)
    image.flags |= LAND_IMAGE_WANT_CACHE
    _load2(image)
    return image

def land_image_uncache(LandImage *self):
    if _loaded_cache and land_hash_has(_loaded_cache, self.filename):
        land_hash_remove(_loaded_cache, self.filename)

def land_image_new_deferred(char const *filename) -> LandImage *:
    LandImage *self = land_image_new(0, 0)
    self.filename = land_path_with_prefix(filename)
    return self

def land_image_load_on_demand(LandImage *self) -> bool:
    """
    Load an image that was previously declared "on demand".
    """

    if self.flags & LAND_LOADING:
        # TODO: wait until it is done...
        # TODO: technically we don't support mixing async and on-demand though
        return True

    if self.flags & LAND_LOADING_COMPLETE:
        land_image_load_async(self)
        return True
    
    if self.flags & LAND_LOADED:
        return False
    if self.flags & LAND_FAILED:
        return False
    land_log_message("land_image_load_on_demand %s..\n", self.filename)
    platform_image_load_on_demand(self)
    bitmap_count += 1
    _load2(self)
    return True

def _thread_func(void *data):
    while not _land_quit:
        while not _land_quit:
            land_thread_lock(_loader_mutex)
        
            LandArray *copy = land_array_copy(_loader_queue)
            land_array_clear(_loader_queue)
            
            land_thread_unlock(_loader_mutex)

            bool empty = land_array_is_empty(copy)
            land_log_message("image queue has %d images\n", land_array_count(copy))

            for LandImage* image in copy:
                land_log_message("queing %s\n", image.filename)
                platform_image_preload_memory(image)
                bitmap_count += 1
                _load2(image)
                image.flags |= LAND_LOADING_COMPLETE
                image.flags &= ~LAND_LOADING
                if _land_quit: break
            land_array_destroy(copy)

            if empty: break

        land_thread_wait_lock(_loader_event)

def land_image_load_async(LandImage* self) -> bool:
    if self.flags & LAND_LOADING:
        return True

    if self.flags & LAND_LOADING_COMPLETE:
        self.flags &= ~LAND_LOADING_COMPLETE
        platform_image_transfer_from_memory(self)
        return True

    if self.flags & LAND_LOADED:
        return False
    if self.flags & LAND_FAILED:
        return False

    if not _loader_thread:
        _loader_event = land_thread_new_waitable_lock()
        _loader_mutex = land_thread_new_lock()
        _loader_queue = land_array_new()
        _loader_thread = land_thread_new(_thread_func, None)

    land_log_message("Asynchronously loading %s\n", self.filename)
    land_thread_lock(_loader_mutex)
    self.flags |= LAND_LOADING
    land_array_add(_loader_queue, self)
    land_thread_unlock(_loader_mutex)
    land_thread_trigger_lock(_loader_event)

    return True

def land_image_exists(LandImage *self) -> bool:
    return platform_image_exists(self)

def land_image_memory_new(int w, int h) -> LandImage *:
    """
    Creates a new image. If w or h are 0, the image will have no contents at
    all (this can be useful if the contents are to be added later).
    The image will always be a simple memory rectangle of pixels, with no
    driver specific optimizations.
    """
    return land_image_new_flags(w, h, LAND_IMAGE_MEMORY)

def land_image_new_flags(int w, h, flags) -> LandImage *:
    """
    Creates a new image. If w and h are 0, the image will have no contents at
    all (this can be useful if the contents are to be added later).
    """
    LandImage *self = land_display_new_image()
    self.flags = flags
    self.width = w
    self.height = h
    if w or h:
        platform_image_empty(self)
    bitmap_count++
    bitmap_memory += w * h * 4
    return self

def land_image_new(int w, int h) -> LandImage *:
    return land_image_new_flags(w, h, 0)

def land_image_create(int w, int h) -> LandImage *:
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
    # remove it from the cache first with land_image_uncache
    if self.flags & LAND_IMAGE_FROM_CACHE: return
    # Sub-bitmaps have no own names or masks or anything. They are
    # just a reference with their own cut-out rectangle.
    if not (self.flags & LAND_SUBIMAGE):
        land_image_destroy_pixelmasks(self)
        if self.name: land_free(self->name)
        if self.filename and self->filename != self->name:
            land_free(self->filename)
        bitmap_count--
        bitmap_memory -= self.width * self->height * 4
    land_display_del_image(self)

def land_image_destroy(LandImage *self):
    land_image_del(self)

def land_image_destroy_and_null(LandImage **self):
    if *self:
        land_image_del(*self)
        *self = None

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

macro LandImageFit 1
    
def land_image_resize(LandImage *self, int new_w, new_h, int flags):
    """
    Resizes the image to the given dimensions. If the new aspect ratio
    is different by default the contents will get distorted.

    flags:
    LandImageFit - Never enlarge the original and if the aspect ratio
                   changes center the picture.
    """
    float old_w = self.width - self.l - self.r
    float old_h = self.height - self.t - self.b
    if new_w == 0: new_w = old_w
    if new_h == 0: new_h = old_h
    float xs = 1.0 * new_w / old_w
    float ys = 1.0 * new_h / old_h
    float xo = 0
    float yo = 0
    if flags & LandImageFit:
        if xs > 1: xs = 1
        if ys > 1: ys = 1
        if xs < ys:
            ys = xs
        else:
            xs = ys
        xo = new_w * 0.5 - old_w * xs * 0.5
        yo = new_h * 0.5 - old_h * ys * 0.5
    LandImage *resized = land_image_new(new_w, new_h)
    land_set_image_display(resized)
    land_blend(LAND_BLEND_SOLID)
    land_image_draw_scaled(self, xo - self.l * xs, yo - self.t * ys, xs, ys)
    land_unset_image_display()
    platform_image_merge(self, resized)

def land_image_new_from(LandImage *copy, int x, int y, int w, int h) -> LandImage *:
    """
    Create a new image, copying pixel data from a rectangle in an existing
    image.
    """
    land_log_message("land_image_new_from %s..", copy->name)

    LandImage *self = land_image_new(w, h)
    self.name = land_strdup("from ")
    if copy.filename: land_append(&self.name, copy.filename)
    land_set_image_display(self)

    # blending changes only for image display which is destroyed a line later
    land_blend(LAND_BLEND_SOLID)

    land_image_draw_partial(copy, copy->x, copy->y, x, y, w, h)
    land_unset_image_display()
    
    land_log_message_nostamp(" success (%d x %d)\n", w, h)

    *** "ifdef" LOG_COLOR_STATS
    float red, green, blue, alpha
    int n
    n = land_image_color_stats(self, &red, &green, &blue, &alpha)
    land_log_message(" (%.2f|%.2f|%.2f|%.2f).\n", red / n, green / n, blue / n, alpha / n)
    *** "endif"

    land_log_message(" %d bitmaps (%.1fMB).\n", bitmap_count, bitmap_memory / 1024.0 / 1024.0)
    
    return self

def land_image_color_stats(LandImage *self,
    float *red, *green, *blue, *alpha) -> int:
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

def land_image_split_mask_from_colors(LandImage *self, int n_rgb,
    int *rgb) -> LandImage *:
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

static def callback(const char *filename, int attrib, void *param) -> int:
    LandArray **filenames = param
    land_array_add_data(filenames, land_strdup(filename))
    return 0

static def compar(void const *a, void const *b) -> int:
    char *an = *(char **)a
    char *bn = *(char **)b
    return strcmp(an, bn)

static def filter(char const *name, bool is_dir, void *data) -> int:
    char const *pattern = data
    if is_dir:
        return 2
    if land_fnmatch(pattern, name):
        return 1
    return 0

def land_load_images_cb(char const *pattern,
    void (*cb)(LandImage *image, void *data), void *data) -> LandArray *:
    """
    Load all images matching the file name pattern, and create an array
    referencing them all, in alphabetic filename order. The callback function
    is called on each image along the way.
    """

    LandBuffer *dirbuf = land_buffer_new()
    int j = 0
    for int i = 0 while pattern[i] with i++:
        if pattern[i] == '/' or pattern[i] == '\\':
            land_buffer_add(dirbuf, pattern + j, i - j)
            j = i
        if pattern[i] == '?' or pattern[i] == '*': break
    char *dir = land_buffer_finish(dirbuf)

    LandArray *filenames = None
    int count = 0
    if land_datafile:
        count = land_datafile_for_each_entry(land_datafile, pattern, callback,
            &filenames)

    if not count:
        filenames = land_filelist(dir, filter, LAND_RELATIVE_PATH, (void *)pattern)
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

def land_load_images(char const *pattern, int center, int auto_crop) -> LandArray *:
    """
    Load all images matching the file name pattern, and create an array
    referencing them all.
    """
    int data[2] = {center, auto_crop}
    return land_load_images_cb(pattern, defcb, data)

def land_image_sub(LandImage *parent, float x, float y, float w, float h) -> LandImage *:
    LandImage *self = platform_image_sub(parent, x, y, w, h)
    return self

# Loads an image, and returns a list of sub-images out of it. 
def land_image_load_sheet(char const *filename, int offset_x, int offset_y,
    int grid_w, int grid_h, int x_gap, int y_gap, int x_count, int y_count,
    int auto_crop) -> LandArray *:
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
def land_image_load_split_sheet(char const *filename, int offset_x,
    int offset_y, int grid_w, int grid_h, int x_gap, int y_gap, int x_count,
    int y_count, int auto_crop) -> LandArray *:
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

def land_image_draw_into(LandImage *self, float x, y, w, h):
    land_image_draw_scaled_rotated_tinted(self, x, y, w / self.width, h / self.height, 0, 1, 1, 1, 1)

def land_image_draw_flipped(LandImage *self, float x, float y):
    land_image_draw_scaled_rotated_tinted_flipped(self, x, y, 1, 1, 0, 1, 1, 1, 1, 1)

def land_image_draw_tinted(LandImage *self, float x, float y, float r, float g,
    float b, float alpha):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, r, g, b, alpha)

def land_image_draw_color(LandImage *self, float x, y, LandColor color):
    land_image_draw_scaled_rotated_tinted(self, x, y, 1, 1, 0, color.r, color.g, color.b, color.a)

def land_image_grab(LandImage *self, int x, int y):
    platform_image_grab_into(self, x, y, 0, 0, self.width, self->height)

def land_image_grab_into(LandImage *self, float x, y, tx, ty, tw, th):
    platform_image_grab_into(self, x, y, tx, ty, tw, th)

def land_image_offset(LandImage *self, int x, int y):
    self.x = x
    self.y = y

def land_image_shift(LandImage *self, float x, y):
    self.x += x
    self.y += y

def land_image_memory_draw(LandImage *self, float x, float y):
    assert(0)

def land_image_center(LandImage *self):
    self.x = 0.5 * self->width
    self.y = 0.5 * self->height
    self.flags |= LAND_IMAGE_WAS_CENTERED | LAND_IMAGE_CENTER

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

def land_image_draw_partial_into(LandImage *self, float sx, sy, sw, sh, dx, dy, dw, dh):
    float l = self.l
    float t = self.t
    float r = self.r
    float b = self.b
    land_image_clip(self, sx, sy, sx + sw, sy + sh)
    land_image_draw_scaled(self, dx - sx * dw / sw, dy - sy * dh / sh, dw / sw, dh / sh)
    self.l = l
    self.t = t
    self.r = r
    self.b = b

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

def land_image_height(LandImage *self) -> int:
    return self.height

def land_image_width(LandImage *self) -> int:
    return self.width

def land_image_size(LandImage *self, int *w, *h):
    *w = self.width
    *h = self.height

def land_image_get_rgba_data(LandImage *self, unsigned char *rgba):
    """
    Copies rgba data into the specified buffer. It has to be large
    enough (w * h * 4 bytes) to hold all the data.
    """
    platform_image_get_rgba_data(self, rgba)

def land_image_allocate_rgba_data(LandImage *self) -> byte*:
    (int w, h) = land_image_size(self)
    byte *rgba = land_calloc(w * h * 4)
    platform_image_get_rgba_data(self, rgba)
    return rgba

def land_image_set_rgba_data(LandImage *self, unsigned char const *rgba):
    """
    Copies the rgba data, overwriting the image contents. Since data are copied
    rgba can be safely deleted after returning from the function.
    """
    platform_image_set_rgba_data(self, rgba)

def land_image_clear(LandImage *self, LandColor color):
    land_set_image_display(self)
    land_color_set(color)
    land_clear_color()
    land_unset_image_display()

def land_image_save(LandImage *self, char const *filename):
    platform_image_save(self, filename)

def land_image_opengl_texture(LandImage *self) -> int:
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
 
def land_image_clone(LandImage *self) -> LandImage *:
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

def land_image_thumbnail(LandImage *self, int w, h) -> LandImage *:
    LandImage *clone = land_image_new(w, h)
    clone.name = land_strdup("thumbnail of ")
    if self.filename: land_append(&clone.name, self.filename)

    land_set_image_display(clone)
    # blending changes only for image display which is destroyed a line later
    land_blend(LAND_BLEND_SOLID)
    int cx = w // 2
    int cy = h // 2
    (int ow, oh) = land_image_size(self)
    float s1 = w * 1.0f / ow
    float s2 = h * 1.0f / oh
    float s = max(s1, s2)
    int nw = ow * s
    int nh = oh * s
    land_image_draw_scaled(self, cx - nw // 2, cy - nh // 2, s, s)
    land_unset_image_display()

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
    
def land_image_from_xpm(char const **xpm) -> LandImage*:
    int w, h, palette_size, pixel_size
    sscanf(xpm[0], "%d %d %d %d", &w, &h, &palette_size, &pixel_size)
    LandColor palette[65536]
    for int i in range(palette_size):
        char const *entry = xpm[1 + i]
        int p = 0
        for int j in range(pixel_size):
            p *= 256
            p += (unsigned char)entry[j]
        palette[p] = land_color_name(entry + pixel_size + 3)
    LandImage *self = land_image_new(w, h)
    unsigned char *rgba = land_malloc(w * h * 4)
    for int y in range(h):
        for int x in range(w):
            char const *pos = xpm[1 + palette_size + y] + x * pixel_size
            int p = 0
            for int j in range(pixel_size):
                p *= 256
                p += (unsigned char)pos[j]
            LandColor c = palette[p] 
            rgba[y * w * 4 + x * 4 + 0] = c.r * 255
            rgba[y * w * 4 + x * 4 + 1] = c.g * 255
            rgba[y * w * 4 + x * 4 + 2] = c.b * 255
            rgba[y * w * 4 + x * 4 + 3] = c.a * 255
    land_image_set_rgba_data(self, rgba)
    land_free(rgba)
    return self

def land_image_write_callback(LandImage *self, void (*cb)(int x, int y,
        unsigned char *rgba, void *user), void *user):
    """
    Run a callback for each pixel of a picture. The pointer passed to
    the callback must be assigned 4 8-bit values in the range 0..255.
    It must not be read from.
    """
    int w = self.width
    int h = self.height
    unsigned char *rgba = land_malloc(w * h * 4)
    unsigned char *p = rgba
    for int y in range(h):
        for int x in range(w):
            cb(x, y, p, user)
            p += 4
    land_image_set_rgba_data(self, rgba)
    land_free(rgba)

def land_image_read_write_callback(LandImage *self, void (*cb)(int x, int y,
        unsigned char *rgba, void *user), void *user):
    """
    Run a callback for each pixel of a picture. The rgba pointer passed
    to the callback will contain the current color as 4 consecutive
    bytes and may be modified.
    """
    int w = self.width
    int h = self.height
    unsigned char *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba)
    unsigned char *p = rgba
    for int y in range(h):
        for int x in range(w):
            cb(x, y, p, user)
            p += 4
    land_image_set_rgba_data(self, rgba)
    land_free(rgba)

def _remove_transparency_cb(int x, int y, unsigned char *rgba, void *user):
    LandColor *c = user
    if rgba[3] < 255:
        float a = rgba[3]
        rgba[3] = 255
        rgba[0] = rgba[0] + c.r * (255 - a)
        rgba[1] = rgba[1] + c.g * (255 - a)
        rgba[2] = rgba[2] + c.b * (255 - a)

def land_image_remove_transparency(LandImage *self, LandColor c):
    land_image_read_write_callback(self, _remove_transparency_cb, &c)

def land_image_read_backup_write_callback(LandImage *self, void (*cb)(int x, int y,
        int w, int h,
        unsigned char *rgba_in, unsigned char *rgba_out, void *user), void *user):
    """
    Same as land_image_read_write_callback but the previous image is
    kept in a backup buffer and a separate pointer for reading is
    provided. This is useful if you also want to read from neighboring
    pixels. As a convenience the width and height of the buffers is
    also passed to the callback to allow handling border conditions.
    """
    int w = self.width
    int h = self.height
    unsigned char *rgba_in = land_malloc(w * h * 4)
    land_image_get_rgba_data(self, rgba_in)
    unsigned char *p_in = rgba_in
    unsigned char *rgba_out = land_malloc(w * h * 4)
    unsigned char *p_out = rgba_out
    for int y in range(h):
        for int x in range(w):
            cb(x, y, w, h, p_in, p_out, user)
            p_in += 4
            p_out += 4
    land_image_set_rgba_data(self, rgba_out)
    land_free(rgba_in)
    land_free(rgba_out)
