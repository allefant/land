import land/display
import a5_image
static import global allegro5/allegro5
static import global allegro5/allegro_primitives
static import global assert, math

class LandDisplayPlatform:
    LandDisplay super
    ALLEGRO_DISPLAY *a5
    ALLEGRO_COLOR c
    ALLEGRO_STATE blend_state
    ALLEGRO_TRANSFORM transform

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

static def check_blending_and_transform():
    SELF

    if super->matrix_modified:
        memcpy(self->transform.m, super->matrix, sizeof(super->matrix))
        al_use_transform(&self->transform)
        super->matrix_modified = False

    if super->blend:
        al_store_state(&self->blend_state, ALLEGRO_STATE_BLENDER)
        #ALLEGRO_COLOR c
        #if super->blend & LAND_BLEND_TINT:
        #    c = self->c
        if super->blend & LAND_BLEND_SOLID:
            al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_ZERO)
        elif super->blend & LAND_BLEND_ADD:
            al_set_blender(ALLEGRO_ADD, ALLEGRO_ALPHA, ALLEGRO_ONE)

static def uncheck_blending():
    SELF
    if super->blend:
        al_restore_state(&self->blend_state)

def platform_display_set():
    SELF
    int f = 0
    if self->a5:
        # FIXME: check for changed parameters
        return
    if super->flags & LAND_FULLSCREEN:
        f |= ALLEGRO_FULLSCREEN_WINDOW
    if super->flags & LAND_RESIZE:
        f |= ALLEGRO_RESIZABLE
    if super->flags & LAND_OPENGL:
        f |= ALLEGRO_OPENGL
    if super->flags & LAND_MULTISAMPLE:
        al_set_new_display_option(ALLEGRO_SAMPLE_BUFFERS, 1, ALLEGRO_SUGGEST);
        al_set_new_display_option(ALLEGRO_SAMPLES, 4, ALLEGRO_SUGGEST);
    if super->flags & LAND_DEPTH:
        al_set_new_display_option(ALLEGRO_DEPTH_SIZE, 16, ALLEGRO_SUGGEST)

    ALLEGRO_MONITOR_INFO info;
    al_get_monitor_info(0, &info);
    land_log_message("Monitor resolution: %d %d %d %d\n", info.x1, info.y1, info.x2, info.y2);

    int monw = info.x2 - info.x1
    int monh = info.y2 - info.y1
    
    if super->flags & LAND_RESIZE:
        if super->w > monw: super->w = monw
        if super->h > monh: super->h = monh
    
    if super->w == monw and super->h == monh:
        f |= ALLEGRO_FULLSCREEN_WINDOW

    if super->w == 0:
        super->w = monw
        super->clip_x2 = super->w
    if super->h == 0:
        super->h = monh
        super->clip_y2 = super->h
    
    if f:
        al_set_new_display_flags(f)
    al_set_new_display_option(ALLEGRO_DEPTH_SIZE, 16, ALLEGRO_SUGGEST)
    land_log_message("Calling al_create_display(%d, %d).\n", super->w,
        super->h)
    self->a5 = al_create_display(super->w, super->h)
    if self->a5:
        land_log_message("    Success!\n")
    else:
        land_log_message("    Failed activating Allegro display.\n")

def platform_display_scale_to_fit(float w, h, int how):
    SELF
    float dw = al_get_display_width(self->a5)
    float dh = al_get_display_height(self->a5)
    float sx, sy
    if how == 0:
        sx = sy = 1
        assert(0) # FIXME
    elif how == 1:
        sx = sy = dw / w
        if h * sy < dh:
            sx = sy = dh / h
    elif how == 2: sx = sy = dw / w
    elif how == 3: sx = sy = dh / h
    else: sx = dw / w; sy = dh / h
    ALLEGRO_TRANSFORM t
    al_identity_transform(&t)
    al_scale_transform(&t, sx, sy)
    al_use_transform(&t)

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
    check_blending_and_transform()
    al_draw_rectangle(x, y, x_, y_, self->c, self->super.thickness)
    uncheck_blending()

def platform_filled_rectangle(float x, y, x_, y_):
    SELF
    check_blending_and_transform()
    al_draw_filled_rectangle(x, y, x_, y_, self->c)
    uncheck_blending()

def platform_filled_circle(float x, y, x_, y_):
    SELF
    float cx = (x + x_) * 0.5
    float cy = (y + y_) * 0.5
    float rx = (x_ - x) * 0.5
    float ry = (y_ - y) * 0.5
    check_blending_and_transform()
    al_draw_filled_ellipse(cx, cy, rx, ry, self->c)
    uncheck_blending()

def platform_circle(float x, y, x_, y_):
    SELF
    float cx = (x + x_) * 0.5
    float cy = (y + y_) * 0.5
    float rx = (x_ - x) * 0.5
    float ry = (y_ - y) * 0.5
    check_blending_and_transform()
    al_draw_ellipse(cx, cy, rx, ry, self->c, self->super.thickness)
    uncheck_blending()

def platform_arc(float x, y, x_, y_, a, a_):
    SELF
    float cx = (x + x_) * 0.5
    float cy = (y + y_) * 0.5
    float rx = (x_ - x) * 0.5
    #float ry = (y_ - y) * 0.5
    check_blending_and_transform()
    al_draw_arc(cx, cy, rx, a, (a_ - a), self->c, self->super.thickness)
    uncheck_blending()

def platform_ribbon(int n, float *xy):
    SELF
    check_blending_and_transform()
    
    for int i = 0 while i < n - 1 with i++:
        float xy8[8]
        xy8[2] = xy[i * 2 + 0]
        xy8[3] = xy[i * 2 + 1]

        xy8[0] = xy[i * 2 + 0]
        xy8[1] = xy[i * 2 + 1]
        xy8[6] = xy[i * 2 + 2]
        xy8[7] = xy[i * 2 + 3]

        xy8[4] = xy[i * 2 + 2]
        xy8[5] = xy[i * 2 + 3]
        
        float ex = xy8[0] - xy8[6]
        float ey = xy8[1] - xy8[7]
        float e = sqrt(ex * ex + ey * ey)
        
        e *= 0.33
        
        if i > 0:
            float dx = xy[i * 2 + 2] - xy[(i - 1) * 2 + 0]
            float dy = xy[i * 2 + 3] - xy[(i - 1) * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[2] += e * dx / d
            xy8[3] += e * dy / d
        
        if i < n - 2:
            float dx = xy[i * 2 + 0] - xy[i * 2 + 4]
            float dy = xy[i * 2 + 1] - xy[i * 2 + 5]
            float d = sqrt(dx * dx + dy * dy)
            xy8[4] += e * dx / d
            xy8[5] += e * dy / d
        
        #ALLEGRO_COLOR c = al_map_rgba_f(0, 1, 0, 0.25)
        #al_draw_line(xy8[2], xy8[3], xy8[4], xy8[5], c, 0)
        #c = al_map_rgba_f(1, 0, 0, 0.25)
        #al_draw_circle(xy8[0], xy8[1], 5, c, 0)
        al_draw_spline(xy8, self->c, self->super.thickness)

    uncheck_blending()

def platform_line(float x, y, x_, y_):
    SELF
    check_blending_and_transform()
    al_draw_line(x, y, x_, y_, self->c, self->super.thickness)
    uncheck_blending()

def platform_polygon(int n, float *xy):
    SELF
    ALLEGRO_VERTEX v[n]
    memset(v, 0, n * sizeof(ALLEGRO_VERTEX))
    int j = 0
    for int i = 0 while i < n with i++:
        v[i].x = xy[j++]
        v[i].y = xy[j++]
        v[i].color = self->c
    check_blending_and_transform()
    al_draw_prim(v, None, None, 0, n, ALLEGRO_PRIM_LINE_LOOP)
    uncheck_blending()

def platform_filled_polygon(int n, float *xy):
    SELF
    ALLEGRO_VERTEX v[n]
    memset(v, 0, n * sizeof(ALLEGRO_VERTEX))
    int j = 0
    for int i = 0 while i < n with i++:
        v[i].x = xy[j++]
        v[i].y = xy[j++]
        v[i].color = self->c
    check_blending_and_transform()
    al_draw_prim(v, None, None, 0, n, ALLEGRO_PRIM_TRIANGLE_FAN)
    uncheck_blending()

def platform_textured_polygon(LandImage *image, int n, float *xy, float *uv):
    SELF
    
    LandImagePlatform *pim = (void *)image;
    
    ALLEGRO_VERTEX v[n]
    memset(v, 0, n * sizeof(ALLEGRO_VERTEX))
    int j = 0
    int k = 0
    for int i = 0 while i < n with i++:
        v[i].x = xy[j++]
        v[i].y = xy[j++]
        v[i].u = uv[k++]
        v[i].v = uv[k++]
        v[i].color = self->c
    check_blending_and_transform()
    al_draw_prim(v, None, pim->a5, 0, n, ALLEGRO_PRIM_TRIANGLE_FAN)
    uncheck_blending()

def platform_filled_polygon_with_holes(int n, float *xy,
    int holes_count, int *holes):
    SELF

    check_blending_and_transform()
    al_draw_filled_polygon_with_holes(xy, n,
        holes, holes_count, self->c)
    uncheck_blending()

def platform_plot(float x, y):
    SELF
    check_blending_and_transform()
    al_draw_pixel(x, y, self->c)
    uncheck_blending()
    
def platform_pick_color(float x, y):
    SELF
    self->c = al_get_pixel(al_get_target_bitmap(), x, y)
    al_unmap_rgba_f(self->c,
        &super->color_r,
        &super->color_g,
        &super->color_b,
        &super->color_a)
