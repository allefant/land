"""
Drawing Primitives in Land

= Positions =

The most basic information drawing primitives need is, where on the target
should they be drawn. There are several ways:

Relative screen coordinates. For example, 0/0 is the upper left screen edge, 1/1
the lower right screen edge. A rectangle from 0.1/0.1 to 0.9/0.9 would span 80%
of the width and the height of the screen, and leave a 10% border all around.
Obviously, using such coordinates is most useful if you don't want to care at
all about the actual resolution used.

Pixel coordinates. A coordinate is given in pixels. So, if you draw a line from
1/1 to 2/2, the pixels at 1/1 and at 2/2 would be lit. This is what Land
originally used in its first incarnation, a very long time ago. This has some
disadvantages. Besides positions relying on the current resolution, it is also
impossible to specify sub-pixel behavior, for example when anti-aliasing is
switched on.

Subpixel coordinates. This is what Land uses by default, but you can easily
change it. It is a mixture of the two modes above. You give coordinates in pixel
positions (so positions depend on the resolution), but each integer position is
the upper left corner of a pixel, not the pixel as the whole, as in the method
before. To get the behavior of the previous method, you would do two things:

1. Add 0.5 to all positions for drawing primitives, so they are drawn at pixel
centers.

2. For images, don't do this.

To make clear why, let's compare a rectangle
and an image. The rectangle is drawn at pixel 0/0 with the pixel method, and 10x10
pixels big. So the pixels that are lit are from 0/0 to 9/9, inclusive. Doing the
same with the subpixel method, we would shift this so pixel centers are used.
That is, we would start at 0.5/0.5, and draw to 9.5/9.5.

But what just happened? The rectangle of lit pixels before was 10x10 pixels big,
from pixel 0 to pixel 9 inclusive. The new subpixel rectangle however is only
9x9 pixels big. From 0.5 to 9.5. 

The problem is, that what we really want with subpixel coordinates is not just
an outline anymore, but a frame which is one pixel thick. Its outer rectangle
would actually start at 0/0, and end at 10/10. Its inner rectangle would start
at 1/1 and end at 9/9. Drawing a single rectangle from 0.5/0.5 to 9.5/9.5 just
works, because we assumed a line-thickness of 1.

But with images, there is no line thickness. So if we draw an image which is
10x10 pixels big, and we draw it to 0/0, it will exactly fit the same rectangle.
Would we draw it to 0.5/0.5, that just would be wrong.

Now, to make things easier, you don't have to use sub-pixel coordinates if you
absolutely don't want to. Call:

land_use_screen_positions()

to use the method which maps the screen to 0/0..1/1,

or

land_use_pixel_positions()

to use pixel positions. That is, Land will always lit the exact pixel you
specify, and also draw images correctly to full-pixel positions. In fact, this
mode just maps the coordinates like described above, so you still can use
non-integer positions (but there really is no reason to not use one of the other
two positioning modes then) and enable e.g. anti-aliasing.

= Primitives =

== line ==

This draws a line from the first point to the second point.

== rectangle ==

This draws a rectangle from the first point to the second point.

== filled_rectangle ==

Like rectangle, but filled.

== circle/ellipse/oval ==

This draws a circle, inscribed into the given rectangle. The alternate names
"ellipse" and "oval" for this function actually fit better.

== filled_circle ==

Like circle, but filled.
"""


import global allegro, alleggl, stdlib
import list, image, log, memory

macro LAND_WINDOWED 1
macro LAND_FULLSCREEN 2
macro LAND_OPENGL 4
macro LAND_CLOSE_LINES 8

class LandDisplayInterface:
    land_method(void, set, (LandDisplay *self))
    land_method(void, clear, (LandDisplay *self, float r, float g, float b, float a))
    land_method(void, flip, (LandDisplay *self))
    land_method(void, rectangle, (LandDisplay *self, float x, float y, float x_, float y_))
    land_method(void, filled_rectangle, (LandDisplay *self, float x, float y, float x_, float y_))
    land_method(void, line, (LandDisplay *self, float x, float y, float x_, float y_))
    land_method(void, filled_circle, (LandDisplay *self, float x, float y, float x_, float y_))
    land_method(void, circle, (LandDisplay *self, float x, float y, float x_, float y_))
    land_method(LandImage *, new_image, (LandDisplay *self))
    land_method(void, del_image, (LandDisplay *self, LandImage *image))
    land_method(void, color, (LandDisplay *self))
    land_method(void, clip, (LandDisplay *self))
    land_method(void, polygon, (LandDisplay *self, int n, float *x, float *y))
    land_method(void, filled_polygon, (LandDisplay *self, int n, float *x, float *y))
    land_method(void, plot, (LandDisplay *self, float x, float y))
    land_method(void, pick_color, (LandDisplay *self, float x, float y))

class LandDisplay:
    LandDisplayInterface *vt
    int w, h, bpp, hz, flags

    float color_r, color_g, color_b, color_a

    int clip_off
    float clip_x1, clip_y1, clip_x2, clip_y2
    LandList *clip_stack

import image/display, allegro/display, allegrogl/display

static import main

static LandList *_previous
global LandDisplay *_land_active_display

static LandDisplay *_global_image_shortcut_display
static LandImage *_global_image
static int nested

LandDisplay *def land_display_new(int w, int h, int bpp, int hz, int flags):
    LandDisplay *self
    if flags & LAND_OPENGL:
        LandDisplayAllegroGL *allegrogl = land_display_allegrogl_new(
            w, h, bpp, hz, flags)
        self = &allegrogl->super

    else:
        LandDisplayAllegro *allegro = land_display_allegro_new(
            w, h, bpp, hz, flags)
        self = &allegro->super

    self->clip_x1 = 0
    self->clip_y1 = 0
    self->clip_x2 = w
    self->clip_y2 = h
    self->clip_off = 0

    land_display_select(self)

    return self

def land_display_destroy(LandDisplay *self):
    if self == _land_active_display: land_display_unselect()

    if self->clip_stack:
        if self->clip_stack->count: land_log_message("Error: non-empty clip stack in display.\n")
        land_list_destroy(self->clip_stack)

    land_free(self)

def land_display_del(LandDisplay *self):
    land_display_destroy(self)

def land_set_image_display(LandImage *image):
    """
    Change the display of the current thread to an internal display which draws
    to the specified image. This cannot be nested.
    """
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(_global_image_shortcut_display)
    if nested:
        land_exception("land_set_image_display cannot be nested")

    if not _global_image_shortcut_display:
        _global_image_shortcut_display = land_display_image_new(image, 0)

    else:
        self->bitmap = image->memory_cache
        self->super.w = land_image_width(image)
        self->super.h = land_image_height(image)
        self->super.bpp = bitmap_color_depth(image->memory_cache)

    _global_image = image
    land_display_select(_global_image_shortcut_display)

def land_unset_image_display():
    """
    Restore the display to what it was before the call to
    land_set_image_display.
    """
    land_display_unselect()
    land_image_prepare(_global_image)
    _global_image = NULL

def land_display_set():
    """
    Make the active display of the current thread the active one. This may
    involve creating a new window. There is usually no need to call this
    function directly, as it will be called internally.
    """
    _land_active_display->vt->set(_land_active_display)
    _land_active_display->vt->color(_land_active_display)
    _land_active_display->vt->clip(_land_active_display)
    
    if set_display_switch_mode(SWITCH_BACKGROUND):
        set_display_switch_mode(SWITCH_BACKAMNESIA)

LandDisplay *def land_display_get():
    """
    Retrieve a handle to the currently active display of the calling thread.
    """
    return _land_active_display

def land_display_unset():
    """
    Make the current display invalid. Usually there is no need for this.
    """
    _land_active_display = NULL

def land_display_init():
    land_log_message("land_display_init\n")
    _previous = land_list_new()
    land_display_allegro_init()
    land_display_allegrogl_init()
    land_display_image_init()

def land_display_exit():
    land_log_message("land_display_exit\n")
    land_list_destroy(_previous)
    if _global_image_shortcut_display:
        land_display_destroy(_global_image_shortcut_display)
    land_display_image_exit()
    land_display_allegrogl_exit()
    land_display_allegro_exit()

double def land_display_time_flip_speed(double howlong):
    """
    This function is dangerous! It will completely halt Land for the passed
    time in seconds.
    The function will try to determine how long flipping of the display takes.
    This can be used to see if the refresh rate is honored (usually because
    vsync is enabled).
    """
    land_flip()
    double t = land_get_time()
    double t2
    int i = 0
    while (t2 = land_get_time()) < t + howlong:
        land_flip()
        i += 1

    return i / (t2 - t)

def land_display_toggle_fullscreen():
    """
    Toggle the current thread's display between windowed and fullscreen mode,
    if possible.
    """
    LandDisplay *d = _land_active_display
    d->flags ^= LAND_FULLSCREEN
    if d->flags & LAND_FULLSCREEN: d->flags &= ~LAND_WINDOWED
    else: d->flags |= LAND_WINDOWED
    land_display_set()

def land_display_resize(int w, h):
    """
    Resize the current display to the given dimensions.
    """
    LandDisplay *d = _land_active_display
    d->w = w
    d->h = h
    land_display_set()

def land_clear(float r, float g, float b, float a):
    """
    Clear the current thread's display to the specified color. Always set
    '''a''' to 1, or you may get a transparent background.
    """
    LandDisplay *d = _land_active_display
    _land_active_display->vt->clear(d, r, g, b, a)

def land_color(float r, float g, float b, float a):
    """
    Change the color of the current thread's active display. This is the color
    which will be used for subsequent graphics commands.
    """
    LandDisplay *d = _land_active_display
    d->color_r = r
    d->color_g = g
    d->color_b = b
    d->color_a = a
    _land_active_display->vt->color(d)

def land_get_color(float *r, float *g, float *b, float *a):
    """
    Retrieve the current color.
    """
    LandDisplay *d = _land_active_display
    *r = d->color_r
    *g = d->color_g
    *b = d->color_b
    *a = d->color_a

def land_clip(float x, float y, float x_, float y_):
    LandDisplay *d = _land_active_display
    d->clip_x1 = x
    d->clip_y1 = y
    d->clip_x2 = x_
    d->clip_y2 = y_
    _land_active_display->vt->clip(_land_active_display)

def land_clip_intersect(float x, float y, float x_, float y_):
    LandDisplay *d = _land_active_display
    d->clip_x1 = MAX(d->clip_x1, x)
    d->clip_y1 = MAX(d->clip_y1, y)
    d->clip_x2 = MIN(d->clip_x2, x_)
    d->clip_y2 = MIN(d->clip_y2, y_)
    _land_active_display->vt->clip(_land_active_display)

def land_clip_push():
    LandDisplay *d = _land_active_display
    int *clip = land_malloc(5 * sizeof *clip)
    clip[0] = d->clip_x1
    clip[1] = d->clip_y1
    clip[2] = d->clip_x2
    clip[3] = d->clip_y2
    clip[4] = d->clip_off
    land_add_list_data(&d->clip_stack, clip)

def land_clip_pop():
    LandDisplay *d = _land_active_display
    LandListItem *item = d->clip_stack->last
    land_list_remove_item(d->clip_stack, item)
    int *clip = item->data
    d->clip_x1 = clip[0]
    d->clip_y1 = clip[1]
    d->clip_x2 = clip[2]
    d->clip_y2 = clip[3]
    d->clip_off = clip[4]
    land_free(clip)
    land_free(item)
    _land_active_display->vt->clip(_land_active_display)

def land_clip_on():
    LandDisplay *d = _land_active_display
    d->clip_off = 0
    _land_active_display->vt->clip(_land_active_display)

def land_clip_off():
    LandDisplay *d = _land_active_display
    d->clip_off = 1
    _land_active_display->vt->clip(_land_active_display)

def land_unclip():
    LandDisplay *d = _land_active_display
    d->clip_x1 = 0
    d->clip_y1 = 0
    d->clip_x2 = land_display_width()
    d->clip_y2 = land_display_height()
    d->vt->clip(d)

int def land_get_clip(float *cx1, float *cy1, float *cx2, float *cy2):
    LandDisplay *d = _land_active_display
    *cx1 = d->clip_x1
    *cy1 = d->clip_y1
    *cx2 = d->clip_x2
    *cy2 = d->clip_y2
    return !d->clip_off

def land_flip():
    _land_active_display->vt->flip(_land_active_display)

def land_rectangle(
    float x, float y, float x_, float y_):
    _land_active_display->vt->rectangle(_land_active_display, x, y, x_, y_)

def land_filled_rectangle(
    float x, float y, float x_, float y_):
    _land_active_display->vt->filled_rectangle(_land_active_display, x, y, x_, y_)

def land_filled_circle(
    float x, float y, float x_, float y_):
    _land_active_display->vt->filled_circle(_land_active_display, x, y, x_, y_)

def land_circle(
    float x, float y, float x_, float y_):
    _land_active_display->vt->circle(_land_active_display, x, y, x_, y_)

def land_line(
    float x, float y, float x_, float y_):
    _land_active_display->vt->line(_land_active_display, x, y, x_, y_)

def land_polygon(int n, float *x, float *y):
    _land_active_display->vt->polygon(_land_active_display, n, x, y)

def land_filled_polygon(int n, float *x, float *y):
    _land_active_display->vt->filled_polygon(_land_active_display, n, x, y)

def land_plot(float x, float y):
    _land_active_display->vt->plot(_land_active_display, x, y)
    
def land_pick_color(float x, float y):
    _land_active_display->vt->pick_color(_land_active_display, x, y)

int def land_display_width():
    LandDisplay *self = _land_active_display
    return self->w

int def land_display_height():
    LandDisplay *self = _land_active_display
    return self->h

int def land_display_flags():
    LandDisplay *self = _land_active_display
    return self->flags

LandImage *def land_display_new_image():
    LandImage *image = _land_active_display->vt->new_image(_land_active_display)
    return image

def land_display_del_image(LandImage *image):
    return _land_active_display->vt->del_image(_land_active_display, image)

def land_display_select(LandDisplay *display):
    if _land_active_display:
        land_add_list_data(&_previous, _land_active_display)

    _land_active_display = display

def land_display_unselect():
    if _previous && _previous->count:
        LandListItem *last = _previous->last
        _land_active_display = last->data
        land_list_remove_item(_previous, last)
        land_listitem_destroy(last)

    else:
        _land_active_display = NULL
