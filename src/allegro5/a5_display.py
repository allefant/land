import land/display
static import global allegro5/allegro5
static import global allegro5/a5_primitives
static import global assert

static class LandDisplayPlatform:
    LandDisplay super
    ALLEGRO_DISPLAY *a5
    ALLEGRO_COLOR c

def platform_display_init():
    pass

def platform_display_exit():
    pass

LandDisplay *def platform_display_new():
    LandDisplayPlatform *self
    land_alloc(self)

    return &self->super

def platform_display_del(LandDisplay *super):
    LandDisplayPlatform *self = (void *)super
    al_destroy_display(self->a5)

static macro SELF:
    LandDisplayPlatform *self = (void *)_land_active_display
    LandDisplay *super = &self->super
    (void)super

def platform_display_set():
    SELF
    if self->a5:
        # FIXME: check for changed parameters
        return
    if super->flags & LAND_FULLSCREEN:
        al_set_new_display_flags(ALLEGRO_FULLSCREEN)
    self->a5 = al_create_display(super->w, super->h)
    if not self->a5:
        land_log_message("Failed activating Allegro display.\n");

def platform_display_color():
    SELF
    self->c = al_map_rgba_f(
        super->color_r, super->color_g, super->color_b, super->color_a)

def platform_display_clip():
    SELF
    al_set_clipping_rectangle(super->clip_x1, super->clip_y1,
        super->clip_x2 - super->clip_x1, super->clip_y2 - super->clip_y1)

def platform_display_clear(LandDisplay *self, float r, g, b, a):
    al_clear_to_color(al_map_rgba_f(r, g, b, a))

def platform_display_flip():
    al_flip_display()

def platform_rectangle(float x, y, x_, y_):
    SELF
    al_draw_rectangle(x, y, x_, y_, self->c, 0)

def platform_filled_rectangle(float x, y, x_, y_):
    SELF
    al_draw_filled_rectangle(x, y, x_, y_, self->c)

def platform_filled_circle(float x, y, x_, y_):
    SELF
    float cx = (x + x_) * 0.5
    float cy = (y + y_) * 0.5
    float rx = (x_ - x) * 0.5
    float ry = (y_ - y) * 0.5
    al_draw_filled_ellipse(cx, cy, rx, ry, self->c)

def platform_circle(float x, y, x_, y_):
    SELF
    float cx = (x + x_) * 0.5
    float cy = (y + y_) * 0.5
    float rx = (x_ - x) * 0.5
    float ry = (y_ - y) * 0.5
    al_draw_ellipse(cx, cy, rx, ry, self->c, 0)

def platform_line(float x, y, x_, y_):
    SELF
    al_draw_line(x, y, x_, y_, self->c, 0)

def platform_polygon(int n, float *x, *y):
    SELF
    assert(0)

def platform_filled_polygon(int n, float *x, *y):
    SELF
    assert(0)

def platform_plot(float x, y):
    SELF
    al_draw_pixel(x, y, self->c)
    
def platform_pick_color(float x, y):
    SELF
    self->c = al_get_pixel(al_get_backbuffer(), x, y)
    al_unmap_rgba_f(self->c,
        &super->color_r,
        &super->color_g,
        &super->color_b,
        &super->color_a)

LandFont *def platform_new_font():
    return None



def platform_del_font(LandFont *self):
    pass
