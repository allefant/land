cimport image

cdef extern from "land.h":
    ctypedef enum:
        LAND_WINDOWED
        LAND_FULLSCREEN
        LAND_OPENGL
        LAND_CLOSE_LINES

    cdef struct LandDisplay:
        pass

    LandDisplay *land_display_new(int w, int h, int bpp, int hz, int flags)
    void land_display_set()
    void land_display_unset()
    void land_display_init()
    void land_clear(float r, float g, float b, float a)
    void land_color(float r, float g, float b, float a)
    void land_clip(float x, float y, float x_, float y_)
    void land_clip_intersect(float x, float y, float x_, float y_)
    void land_clip_push()
    void land_clip_pop()
    void land_clip_on()
    void land_clip_off()
    void land_unclip()
    void land_flip()
    void land_rectangle(float x, float y, float x_, float y_)
    void land_filled_rectangle(float x, float y, float x_, float y_)
    void land_filled_circle(float x, float y, float x_, float y_)
    void land_circle(float x, float y, float x_, float y_)
    void land_line(float x, float y, float x_, float y_)
    void land_plot(float x, float y)
    void land_polygon(int n, float *x, float *y)
    void land_filled_polygon(int n, float *x, float *y)
    int land_display_width()
    int land_display_height()
    int land_display_flags()
    image.LandImage *land_display_new_image()
    void land_display_del_image(image.LandImage *image)
    void land_display_select(LandDisplay *display)
    void land_display_unselect()
    void land_display_del(LandDisplay *self)
    void land_set_image_display(image.LandImage *image)
    void land_unset_image_display()
    void land_display_toggle_fullscreen()
    void land_display_resize(int w, int h)

WINDOWED = LAND_WINDOWED
FULLSCREEN = LAND_FULLSCREEN
OPENGL = LAND_OPENGL
CLOSE_LINES = LAND_CLOSE_LINES

def c(color):
    if color:
        land_color(color[0], color[1], color[2], color[3])

def clear(r, g, b, a): land_clear(r, g, b, a)
def color(r, g, b, a): land_color(r, g, b, a)
def clip(x, y, x_, y_): land_clip(x, y, x_, y_)
def clip_intersect(x, y, x_, y_): land_clip_intersect(x, y, x_, y_)
def clip_push(): land_clip_push()
def clip_pop(): land_clip_pop()
def clip_on(): land_clip_on()
def clip_off(): land_clip_off()
def unclip(): land_unclip()
def flip(): land_flip()
def rectangle(x, y, x_ = None, y_ = None, color = None, w = None, h = None):
    c(color)
    if x_ == None: x_ = x + w
    if y_ == None: y_ = y + h
    land_rectangle(x, y, x_, y_)
def filled_rectangle(x, y, x_, y_, color = None): c(color); land_filled_rectangle(x, y, x_, y_)
def filled_circle(x, y, x_, y_): land_filled_circle(x, y, x_, y_)
def circle(x, y, x_, y_): land_circle(x, y, x_, y_)
def line(x, y, x_, y_): land_line(x, y, x_, y_)
def plot(x, y): land_plot(x, y)
def polygon(l):
    cdef int n
    n = len(l)
    cdef float x[1024]
    cdef float y[1024]
    i = 0
    for pos in l:
        x[i] = pos[0]
        y[i] = pos[1]
        i = i + 1
    land_polygon(n, x, y)

def filled_polygon(l):
    cdef int n
    n = len(l)
    cdef float x[1024]
    cdef float y[1024]
    i = 0
    for pos in l:
        x[i] = pos[0]
        y[i] = pos[1]
        i = i + 1
    land_filled_polygon(n, x, y)

def width(): return land_display_width()
def height(): return land_display_height()
def flags(): return land_display_flags()
#def new_image(): return land_display_new_image()
#def del_image(image): return land_display_del_image(image)
#def select(display): land_display_select(display)
#def unselect(): land_display_unselect()
#def del(display): land_display_del(display)
def select_image(image.Image image): land_set_image_display(image.wrapped)
def unselect_image(): land_unset_image_display()
def toggle_fullscreen(): land_display_toggle_fullscreen()
def resize(w, h): land_display_resize(w, h)