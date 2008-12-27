import global allegro
import ../array, ../display, ../log
static import ../allegro/image

class LandDisplayImage:
    struct LandDisplay super
    BITMAP *bitmap

macro LAND_DISPLAY_IMAGE(x) ((LandDisplayImage *)(x))

static LandDisplayInterface *vtable

static inline int def color(LandDisplay *display):
    return makeacol(display->color_r * 255, display->color_g * 255,
        display->color_b * 255, display->color_a * 255)

LandDisplay *def land_display_image_new(LandImage *target, int flags):
    LandDisplayImage *self
    land_alloc(self)
    LandDisplay *super = &self->super
    BITMAP *bitmap = target->memory_cache
    super->w = land_image_width(target)
    super->h = land_image_height(target)
    super->bpp = bitmap_color_depth(bitmap)
    super->hz = 0
    super->flags = flags
    super->vt = vtable

    self->bitmap = bitmap

    return super

int def land_display_image_check(LandDisplay *self):
    return self->vt == vtable

def land_display_image_clear(LandDisplay *super, float r, float g, float b, float a):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(super)
    clear_to_color(self->bitmap, makeacol(r * 255, g * 255, b * 255, a * 255))

def land_display_image_clip(LandDisplay *super):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(super)
    set_clip_state(self->bitmap, 1)
    if super->clip_off: set_clip_rect(self->bitmap, 0, 0,
            self->bitmap->w - 1, self->bitmap->h - 1)
    else:
        set_clip_rect(self->bitmap, super->clip_x1 + 0.5, super->clip_y1 + 0.5,
            super->clip_x2 - 0.5, super->clip_y2 - 0.5)

def land_display_image_color(LandDisplay *super):
    pass

def land_display_image_set(LandDisplay *self):
    land_log_message("land_display_image_set\n")
    # Nothing to set up for a memory bitmap. 

def land_display_image_flip(LandDisplay *self):
    # No need to flip a memory bitmap.
    pass

def land_display_image_rectangle(LandDisplay *display,
    float x, float y, float x_, float y_):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display)
    rect(self->bitmap, x, y, x_, y_, color(display))

def land_display_image_filled_rectangle(LandDisplay *display,
    float x, float y, float x_, float y_):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display)
    rectfill(self->bitmap, x, y, x_, y_, color(display))

def land_display_image_line(LandDisplay *display,
    float x, float y, float x_, float y_):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display)
    line(self->bitmap, x, y, x_, y_, color(display))

def land_display_image_filled_circle(LandDisplay *display,
    float x, float y, float x_, float y_):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display)
    ellipsefill(self->bitmap, (x + x_) / 2, (y + y_) / 2,
        (x_ - x) / 2, (y_ - y) / 2, color(display))

def land_display_image_plot(LandDisplay *display, float x, y):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display)
    putpixel(self->bitmap, x, y, color(display))

def land_display_image_pick_color(LandDisplay *display, float x, y):
    LandDisplayImage *self = LAND_DISPLAY_IMAGE(display)
    int rgb = getpixel(self->bitmap, x, y)
    display->color_r = getr(rgb) / 255.0
    display->color_g = getg(rgb) / 255.0
    display->color_b = getb(rgb) / 255.0
    display->color_a = geta(rgb) / 255.0

def land_display_image_init():
    land_log_message("land_display_image_init\n")
    land_alloc(vtable)
    vtable->clear = land_display_image_clear
    vtable->clip = land_display_image_clip
    vtable->color = land_display_image_color
    vtable->rectangle = land_display_image_rectangle
    vtable->filled_rectangle = land_display_image_filled_rectangle
    vtable->line = land_display_image_line
    vtable->filled_circle = land_display_image_filled_circle
    vtable->plot = land_display_image_plot
    vtable->pick_color = land_display_image_pick_color

    vtable->set = land_display_image_set
    vtable->flip = land_display_image_flip
    vtable->del_image = land_image_allegro_del
    vtable->new_image = land_image_allegro_new

def land_display_image_exit():
    land_log_message("land_display_image_exit\n")
    land_free(vtable)
