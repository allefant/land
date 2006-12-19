import land

cdef extern from "land.h":
    LandImage *land_image_load(char *filename)
    LandImage *land_image_new(int w, int h)
    void land_image_del(LandImage *self)
    void land_image_crop(LandImage *self, int x, int y, int w, int h)
    LandImage *land_image_new_from(LandImage *copy, int x, int y, int w, int h)
    int land_image_color_stats(LandImage *self, float *red, float *green,
        float *blue, float *alpha)
    void land_image_colorize(LandImage *self, LandImage *colormask)
    int land_image_colorize_replace(LandImage *self, int n, int *rgb)
    void land_image_prepare(LandImage *self)
#    int land_load_images(char *pattern)
#    LandImage *land_find_image(char *name)
    void land_image_draw_scaled_rotated_tinted(LandImage *self, float x,
        float y, float sx, float sy, float a, float r, float g, float b,
        float a)
#    void land_image_draw_scaled_rotated(LandImage *self, float x, float y,
#       float sx, float sy, float a)
#    void land_image_draw_scaled(LandImage *self, float x, float y, float sx,
#       float sy)
#    void land_image_draw_rotated(LandImage *self, float x, float y, float a)
#    void land_image_draw_scaled_tinted(LandImage *self, float x, float y,
#       float sx, float sy, float r, float g, float b)
#    void land_image_draw(LandImage *self, float x, float y)
    void land_image_offset(LandImage *self, int x, int y)
    void land_image_center(LandImage *self)
#    void land_image_init()
    void land_image_clip(LandImage *self, float x, float y, float x_, float y_)
    void land_image_unclip(LandImage *self)
    int land_image_height(LandImage *self)
    int land_image_width(LandImage *self)
    void land_image_optimize(LandImage *self)
    void land_image_grab(LandImage *self, int x, int y)
    void land_image_grab_into(LandImage *self, int x, int y, int tx, int ty,
        int w, int h)
    unsigned int land_image_allegrogl_texture(LandImage *self)

def load_all(pattern):
    pass
    # return land_load_images(pattern)
    # TODO: Wrap all of them and put into a python dictionary, probably not
    # using the C function at all

def find(name):
    pass
    #land_find_image(name)
    #TODO: Return from dictionary, not using the C function

cdef class Image:
    def __init__(self, *args):
        if len(args) == 0:
            self.wrapped = NULL
        elif len(args) == 1:

            if isinstance(args[0], Image):
                other = args[0]
                w = other.width()
                h = other.height()
                self.wrapped = land_image_new_from((<Image>args[0]).wrapped, 0,
                        0, w, h)
            else:
                text = args[0]
                self.wrapped = land_image_load(text)
        elif len(args) == 2:
            self.wrapped = land_image_new(args[0], args[1])
        elif len(args) == 5:
            other = args[0]
            self.wrapped = land_image_new_from((<Image>args[0]).wrapped,
                args[1], args[2], args[3], args[4])
        else:
            raise land.LandException("Check parameters to Image().")

    def __del__(self):
        print "Reference count of image", self, "is 0."
        land_image_del(self.wrapped)

    def crop(self, x, y, w, h): land_image_crop(self.wrapped, x, y, w, h)
    def color_stats(self):
        cdef float red, green, blue, alpha
        land_image_color_stats(self.wrapped, &red, &green, &blue, &alpha)
        return (red, green, blue, alpha)
    def colorize(self, mask = None, replace = []):
        cdef int rgb[256 * 3]
        if mask:
            land_image_colorize(self.wrapped, (<Image>mask).wrapped)
            return 1
        else:
            for i, c in enumerate(replace):
                rgb[i] = c
            m = land_image_colorize_replace(self.wrapped, len(replace) / 3, rgb)
            return m
    def prepare(self): land_image_prepare(self.wrapped)
    def draw(self, x = 0, y = 0, sx = 1, sy = 1, angle = 0, r = 1, g = 1, b = 1, a = 1):
        land_image_draw_scaled_rotated_tinted(self.wrapped, x, y, sx, sy, angle,
                r, g, b, a)
    def grab(self, x = 0, y = 0, into = None):
        if into:
            if len(into) == 2:
                w = self.width()
                h = self.height()
                into = (into[0], into[1], w - into[0], h - into[1])
            land_image_grab_into(self.wrapped, x, y, into[0], into[1], into[2],
                    into[3])
        else:
            land_image_grab(self.wrapped, x, y)
    def offset(self, x, y): land_image_offset(self.wrapped, x, y)
    def center(self): land_image_center(self.wrapped)
    def clip(self, x, y, x_, y_): land_image_clip(self.wrapped, x, y, x_, y_)
    def unclip(self): land_image_unclip(self.wrapped)
    def height(self): return land_image_height(self.wrapped)
    def width(self): return land_image_width(self.wrapped)
    def optimize(self): land_image_optimize(self.wrapped)
    def resize(self, w, h):
        land_image_del(self.wrapped)
        self.wrapped = land_image_new(w, h)
    def reload(self, path):
        if self.wrapped: land_image_del(self.wrapped)
        self.wrapped = land_image_load(path)
    def exists(self):
        if self.wrapped: return True
        return False
    def debug(self):
        print self, "wrapping %x" % <int>self.wrapped
    
    def gl_texture(self):
        return land_image_allegrogl_texture(self.wrapped)

