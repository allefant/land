"""
Drawing Primitives in Land

# Positions

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
the upper left corner of a pixel, not the pixel as a whole, as in the method
before. To get the behavior of the previous method, you would do two things:

1. For rectangles, draw them with their full width.

2. For images, don't do anything.

To make clear why, let's compare a rectangle and an image. The rectangle is
drawn at pixel 0/0 with the pixel method, and 10x10
pixels big. So the pixels that are lit are from 0/0 to 9/9, inclusive. Doing the
same with the subpixel method, we would draw a rectangle from 0/0 to 10/10.

But what just happened? The rectangle of lit pixels before was 10x10 pixels big,
from pixel 0 to pixel 9 inclusive. The new subpixel rectangle also is 10x10
pixels big. Just now there is no more inclusive/exclusive pixels, the rectangle
coordinates are independent now.

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

# Primitives

## line

This draws a line from the first point to the second point.

## rectangle

This draws a rectangle from the first point to the second point.

## filled_rectangle

Like rectangle, but filled.

## circle/ellipse/oval

This draws a circle, inscribed into the given rectangle. The alternate names
"ellipse" and "oval" for this function actually fit better.

## filled_circle

Like circle, but filled.
"""

import global stdlib
import list, image, log, mem, font, main
import util3d
import color
static import global math

enum:
    LAND_WINDOWED = 1
    LAND_FULLSCREEN = 2
    LAND_OPENGL = 4
    LAND_CLOSE_LINES = 8
    LAND_ANTIALIAS = 16
    LAND_STENCIL = 32
    LAND_RESIZE = 64
    LAND_MULTISAMPLE = 128
    LAND_DEPTH = 256
    LAND_LANDSCAPE = 512

enum:
    LAND_BLEND_SOLID = 1
    LAND_BLEND_ADD = 2
    LAND_BLEND_TINT = 4

enum: LAND_MAX_CLIP_DEPTH = 64

enum:
    LAND_NEVER
    LAND_ALWAYS
    LAND_LESS
    LAND_EQUAL
    LAND_LESS_EQUAL
    LAND_GREATER
    LAND_NOT_EQUAL
    LAND_GREATER_EQUAL

enum:
    LAND_ALPHA_TEST
    LAND_ALPHA_FUNCTION
    LAND_ALPHA_VALUE
    LAND_WRITE_MASK
    LAND_DEPTH_TEST
    LAND_DEPTH_FUNCTION

enum:
    LAND_RED_MASK = 1
    LAND_GREEN_MASK = 2
    LAND_BLUE_MASK = 4
    LAND_ALPHA_MASK = 8
    LAND_DEPTH_MASK = 16
    LAND_RGB_MASK = 7
    LAND_RGBA_MASK = 15  

class LandDisplay:
    int w, h, flags

    float color_r, color_g, color_b, color_a

    int blend
    float thickness

    float cursor_x, cursor_y

    int clip_off
    float clip_x1, clip_y1, clip_x2, clip_y2
    int clip_stack_depth
    int clip_stack[LAND_MAX_CLIP_DEPTH * 5]
    
    LandFloat matrix[16]
    LandFloat matrix_stack[16][16]
    int matrix_stack_depth
    bool matrix_modified

class LandTriangles:
    int n, c
    LandImage *image

static import allegro5/a5_display
static import allegro5/a5_image
static import main

static int resize_event_counter
static int was_resized
static int switch_out_event_counter
static int was_switched_out

static LandList *_previous
global LandDisplay *_land_active_display

def land_display_new(int w, int h, int flags) -> LandDisplay *:
    LandDisplay *self = platform_display_new()
    
    self.w = w
    self.h = h
    self.flags = flags

    self.clip_x1 = 0
    self.clip_y1 = 0
    self.clip_x2 = w
    self.clip_y2 = h
    self.clip_off = 0

    land_display_select(self)
    
    land_reset_transform()

    return self

def land_display_destroy(LandDisplay *self):
    if self == _land_active_display: land_display_unselect()

    if self.clip_stack_depth:
        land_log_message("Error: non-empty clip stack in display.\n")

    platform_display_del(self)
    land_free(self)

def land_display_del(LandDisplay *self):
    land_display_destroy(self)

# how = 0: keep stripes to have the complete wxh visible
# how = 1: zoom to fill the whole window
# how = 2: fit width
# how = 3: fit height
# how = 4: like 0 but keep 0/0 in top left corner
# how = 6: like 2 but keep 0/0 in top left corner
# how = 7: like 3 but keep 0/0 in top left corner
# how = 8: stretch (non-square pixels, not recommended)
# how = how + 256: do the inverse instead
def land_scale_to_fit(float w, h, int how) -> double:
    float dw = land_display_width()
    float dh = land_display_height()
    float sx, sy
    float ox = 0, oy = 0
    int back = how >> 8
    how &= 255
    if how == 0:
        how = 2
        if w * dh / dw < h:
            how = 3

    if how == 1:
        how = 2
        if w * h / dw < dh:
            how = 3

    if how == 4:
        how = 6
        if w * dh / dw < h:
            how = 7
    
    if how == 2 or how == 6:
        sx = sy = dw / w
        if how == 2:
            oy = (dh - h * sy) / 2
    elif how == 3 or how == 7:
        sx = sy = dh / h
        if how == 3:
            ox = (dw - w * sx) / 2
    else:
        sx = dw / w
        sy = dh / h
    land_reset_transform()
    if back:
        land_scale(1 / sx, 1 / sy)
        land_translate(-ox, -oy)
    else:
        land_translate(ox, oy)
        land_scale(sx, sy)
    return sx

def land_get_left -> LandFloat:
    LandFloat *m = _land_active_display->matrix
    return -m[3] / m[0]

def land_get_x_scale -> LandFloat:
    LandFloat *m = _land_active_display->matrix
    return m[0]

def land_get_top -> LandFloat:
    LandFloat *m = _land_active_display->matrix
    return -m[7] / m[5]

def land_get_y_scale -> LandFloat:
    LandFloat *m = _land_active_display->matrix
    return m[5]

def land_set_image_display(LandImage *image):
    """
    Change the display of the current thread to an internal display which draws
    to the specified image. This cannot be nested.
    """
    platform_set_image_display(image)

def land_unset_image_display():
    """
    Restore the display to what it was before the call to
    land_set_image_display.
    """
    platform_unset_image_display()

def land_display_set():
    """
    Make the active display of the current thread the active one. This may
    involve creating a new window. There is usually no need to call this
    function directly, as it will be called internally.
    """
    platform_display_set()
    platform_display_color()
    platform_display_clip()

def land_display_get() -> LandDisplay *:
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
    platform_display_init()

def land_display_exit():
    land_log_message("land_display_exit\n")
    land_list_destroy(_previous)
    platform_display_exit()

def land_display_time_flip_speed(double howlong) -> double:
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
    Toggle the current thread's display between windowed and fullscreen
    mode, if possible.
    """
    LandDisplay *d = _land_active_display
    d->flags ^= LAND_FULLSCREEN
    if d->flags & LAND_FULLSCREEN: d->flags &= ~LAND_WINDOWED
    else: d->flags |= LAND_WINDOWED
    land_display_set()

def land_clear(float r, float g, float b, float a):
    """
    Clear the current thread's display to the specified color. Always set
    '''a''' to 1, or you may get a transparent background.
    """
    LandDisplay *d = _land_active_display
    platform_display_clear(d, r, g, b, a)

def land_clear_depth(float z):
    LandDisplay *d = _land_active_display
    platform_display_clear_depth(d, z)

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
    platform_display_color()

def land_premul(float r, g, b, a):
    land_color_set(land_color_premul(r, g, b, a))

def land_color_set(LandColor c):
    land_color(c.r, c.g, c.b, c.a)

def land_color_get -> LandColor:
    LandColor c
    land_get_color(&c.r, &c.g, &c.b, &c.a)
    return c

def land_thickness(float t):
    LandDisplay *d = _land_active_display
    d->thickness = t

def land_get_color(float *r, float *g, float *b, float *a):
    """
    Retrieve the current color.
    """
    LandDisplay *d = _land_active_display
    *r = d->color_r
    *g = d->color_g
    *b = d->color_b
    *a = d->color_a

def land_blend(int state) -> int:
    LandDisplay *d = _land_active_display
    int prev = d->blend
    d->blend = state
    return prev

def land_clip(float x, float y, float x_, float y_):
    LandDisplay *d = _land_active_display
    d->clip_x1 = x
    d->clip_y1 = y
    d->clip_x2 = x_
    d->clip_y2 = y_
    platform_display_clip()

def land_clip_intersect(float x, float y, float x_, float y_):
    LandDisplay *d = _land_active_display
    d->clip_x1 = max(d->clip_x1, x)
    d->clip_y1 = max(d->clip_y1, y)
    d->clip_x2 = min(d->clip_x2, x_)
    d->clip_y2 = min(d->clip_y2, y_)
    platform_display_clip()

def land_clip_push():
    LandDisplay *d = _land_active_display
    if d->clip_stack_depth > LAND_MAX_CLIP_DEPTH:
        return
    int *clip = d->clip_stack + d->clip_stack_depth * 5
    clip[0] = d->clip_x1
    clip[1] = d->clip_y1
    clip[2] = d->clip_x2
    clip[3] = d->clip_y2
    clip[4] = d->clip_off
    d->clip_stack_depth++

def land_clip_pop():
    LandDisplay *d = _land_active_display
    if d->clip_stack_depth < 1:
        return
    d->clip_stack_depth--
    int *clip = d->clip_stack + d->clip_stack_depth * 5
    d->clip_x1 = clip[0]
    d->clip_y1 = clip[1]
    d->clip_x2 = clip[2]
    d->clip_y2 = clip[3]
    d->clip_off = clip[4]
    platform_display_clip()

def land_clip_on():
    LandDisplay *d = _land_active_display
    d->clip_off = 0
    platform_display_clip()

def land_clip_off():
    LandDisplay *d = _land_active_display
    d->clip_off = 1
    platform_display_clip()

def land_unclip():
    LandDisplay *d = _land_active_display
    d->clip_x1 = 0
    d->clip_y1 = 0
    d->clip_x2 = land_display_width()
    d->clip_y2 = land_display_height()
    platform_display_clip()

def land_get_clip(float *cx1, float *cy1, float *cx2, float *cy2) -> int:
    LandDisplay *d = _land_active_display
    *cx1 = d->clip_x1
    *cy1 = d->clip_y1
    *cx2 = d->clip_x2
    *cy2 = d->clip_y2
    return not d->clip_off

def land_flip():
    platform_display_flip()

def land_rectangle(float x, y, x_, y_):
    platform_rectangle(x, y, x_, y_)

def land_filled_rectangle(float x, y, x_, y_):
    platform_filled_rectangle(x, y, x_, y_)

def land_filled_circle(float x, y, x_, y_):
    platform_filled_circle(x, y, x_, y_)

def land_circle(float x, y, x_, y_):
    platform_circle(x, y, x_, y_)

def land_arc(float x, y, x_, y_, a, a_):
    platform_arc(x, y, x_, y_, a, a_)

def land_line(float x, y, x_, y_):
    platform_line(x, y, x_, y_)

def land_move_to(float x, y):
    LandDisplay *d = _land_active_display
    d.cursor_x = x
    d.cursor_y = y

def land_line_to(float x, y):
    LandDisplay *d = _land_active_display
    land_line(d.cursor_x, d.cursor_y, x, y)
    d.cursor_x = x
    d.cursor_y = y

def land_ribbon(int n, float *xy):
    platform_ribbon(n, xy)

def land_ribbon_loop(int n, float *xy):
    platform_ribbon_loop(n, xy)

def land_filled_ribbon(int n, float *xy):
    platform_filled_ribbon(n, xy)

def land_polygon(int n, float *xy):
    platform_polygon(n, xy)

def land_filled_polygon(int n, float *xy):
    platform_filled_polygon(n, xy)

def land_filled_triangle(float x0, y0, x1, y1, x2, y2):
    float xy[6] = {x0, y0, x1, y1, x2, y2}
    platform_filled_polygon(3, xy)

def land_3d_triangles(int n, LandFloat *xyzrgb):
    platform_3d_triangles(n, xyzrgb)

def land_textured_polygon(LandImage *image, int n, float *xy, *uv):
    platform_textured_polygon(image, n, xy, uv):

def land_textured_colored_polygon(LandImage *image, int n, float *xy, *uv, *rgba):
    platform_textured_colored_polygon(image, n, xy, uv, rgba):

def land_filled_polygon_with_holes(int n, float *xy, int *holes):
    platform_filled_polygon_with_holes(n, xy, holes)

def land_filled_colored_polygon(int n, float *xy, *rgba):
    platform_filled_colored_polygon(n, xy, rgba):

def land_plot(float x, y):
    platform_plot(x, y)
    
def land_pick_color(float x, y):
    platform_pick_color(x, y)

def land_display_width() -> int:
    LandDisplay *self = _land_active_display
    return self.w

def land_display_height() -> int:
    LandDisplay *self = _land_active_display
    return self.h

def land_display_resize(int w, h):
    """
    Resize the current display to the given dimensions.
    """
    LandDisplay *d = _land_active_display
    d->w = w
    d->h = h
    platform_display_resize(w, h)

def land_display_move(int x, y):
    platform_display_move(x, y)

def land_display_desktop_size(int *w, *h):
    platform_display_desktop_size(w, h)

def land_display_title(char const *title):
    platform_display_title(title)

def land_display_icon(LandImage *icon):
    platform_display_icon(icon)

def land_display_flags() -> int:
    LandDisplay *self = _land_active_display
    return self.flags

def land_display_new_image() -> LandImage *:
    LandImage *image = platform_new_image()
    return image

def land_display_del_image(LandImage *image):
    return platform_del_image(image)

def land_display_select(LandDisplay *display):
    if _land_active_display:
        land_add_list_data(&_previous, _land_active_display)

    _land_active_display = display

def land_display_unselect():
    if _previous and _previous->count:
        LandListItem *last = _previous->last
        _land_active_display = last->data
        land_list_remove_item(_previous, last)
        land_listitem_destroy(last)

    else:
        _land_active_display = NULL

def land_screenshot(char const *filename):
    int w = land_display_width()
    int h = land_display_height()
    LandImage *screenshot = land_image_new(w, h)
    land_image_grab(screenshot, 0, 0)
    land_image_save(screenshot, filename)
    land_image_destroy(screenshot)

def land_screenshot_autoname(char const *name):
    LandBuffer *b = land_buffer_new()
    time_t t = time(None)
    land_buffer_cat(b, name)
    land_buffer_cat(b, "_")
    land_buffer_cat(b, ctime(&t))
    land_buffer_strip(b, " \n")
    land_buffer_cat(b, ".jpg")
    char *path = land_buffer_finish(b)
    land_screenshot(path)
    land_free(path)

def land_resize_event(int w, h):
    resize_event_counter++
    _land_active_display->w = w
    _land_active_display->h = h
    _land_active_display->clip_x2 = w
    _land_active_display->clip_y2 = h

def land_switch_out_event:
    switch_out_event_counter++

def land_switched_out -> int:
    return was_switched_out

def land_was_resized() -> int:
    return was_resized

def land_display_tick():
    was_resized = resize_event_counter
    resize_event_counter = 0
    was_switched_out = switch_out_event_counter
    switch_out_event_counter = 0

def land_rotate(LandFloat angle):
    """
    Pre-rotate the current transformation.
    """
    LandFloat *m = _land_active_display->matrix
    LandFloat c = cosf(angle)
    LandFloat s = sinf(angle)
    LandFloat x, y
        
    x = m[0]
    y = m[1]
    m[0] = x * +c + y * +s
    m[1] = x * -s + y * +c
    
    x = m[4]
    y = m[5]
    m[4] = x * +c + y * +s
    m[5] = x * -s + y * +c
    
    _land_active_display->matrix_modified = True

def land_scale(LandFloat x, y):
    """
    Pre-scale the current transformation.
    """
    LandFloat *m = _land_active_display->matrix
    m[0] *= x
    m[1] *= y
    m[4] *= x
    m[5] *= y

    _land_active_display->matrix_modified = True

def land_translate(LandFloat x, y):
    """
    Pre-translate the current transformation. That is, any transformations in
    effect prior to this call will be applied afterwards. And transformations
    after this call until before the next drawing command will be applied
    before.
    """
    LandFloat *m = _land_active_display->matrix
    m[3] += x * m[0] + y * m[1]
    m[7] += x * m[4] + y * m[5]
    _land_active_display->matrix_modified = True

def land_z(LandFloat z):
    LandFloat *m = _land_active_display->matrix
    m[3] += z * m[2]
    m[7] += z * m[6]
    m[11] += z * m[10]
    _land_active_display->matrix_modified = True

def land_push_transform():
    if _land_active_display->matrix_stack_depth < 16:
        int i = _land_active_display->matrix_stack_depth++
        memcpy(_land_active_display->matrix_stack[i],
            _land_active_display->matrix, sizeof _land_active_display->matrix)

def land_pop_transform():
    if _land_active_display->matrix_stack_depth > 0:
        int i = --_land_active_display->matrix_stack_depth
        memcpy(_land_active_display->matrix,
            _land_active_display->matrix_stack[i],
            sizeof _land_active_display->matrix)
        _land_active_display->matrix_modified = True

def land_reset_transform():
    LandFloat *m = _land_active_display->matrix
    
    LandFloat i[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    }
    memcpy(m, i, sizeof i)

    _land_active_display->matrix_modified = True

def land_transform(LandFloat *x, *y, *z):
    Land4x4Matrix m
    memcpy(m.v, _land_active_display->matrix, sizeof m.v)
    LandVector v = land_vector_matmul(land_vector(*x, *y, *z), &m)
    *x = v.x
    *y = v.y
    *z = v.z

def land_display_transform_4x4(Land4x4Matrix *matrix):
    LandFloat *m = _land_active_display->matrix
    for int i in range(16):
        m[i] = matrix->v[i]
    _land_active_display->matrix_modified = True

def land_render_state(int state, value):
    platform_render_state(state, value)

def land_display_set_default_shaders():
    """
    When using custom shaders, use this to restore the shader expected by the
    builtin functions.
    """
    platform_set_default_shaders()

def land_triangles_new -> LandTriangles*:
    return platform_triangles_new()

def land_triangles_clear(LandTriangles *self):
    self.n = 0

def land_triangles_texture(LandTriangles *self, LandImage *texture):
    self.image = texture

def land_add_vertex(LandTriangles *self, float x, y, z, u, v, r, g, b, a):
    platform_add_vertex(self, x, y, z, u, v, r, g, b, a)

def land_duplicate_vertex(LandTriangles *self, int i):
    platform_duplicate_vertex(self, i)

def land_triangles_draw(LandTriangles *self):
    platform_triangles_draw(self)
