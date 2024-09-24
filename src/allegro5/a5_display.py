import land.triangles
import a5_image, a5_main
static import global allegro5.allegro5
static import global allegro5.allegro_primitives
static import global assert, math

class LandDisplayPlatform:
    LandDisplay super
    ALLEGRO_DISPLAY *a5
    ALLEGRO_COLOR c
    ALLEGRO_STATE blend_state
    ALLEGRO_TRANSFORM transform
    ALLEGRO_SHADER *default_shader

def platform_display_init():
    pass

def platform_display_exit():
    pass

def platform_display_new() -> LandDisplay *:
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

def platform_display_desktop_size(int *w, *h):
    ALLEGRO_MONITOR_INFO info;
    al_get_monitor_info(0, &info)
    *w = info.x2 - info.x1
    *h = info.y2 - info.y1

def platform_display_title(char const *title):
    SELF
    al_set_window_title(self->a5, title)

def platform_display_icon(LandImage *icon):
    SELF
    al_set_display_icon(self->a5, ((LandImagePlatform *)icon)->a5)

def platform_display_move(int x, y):
    SELF
    al_set_window_position(self->a5, x, y)

def platform_display_position(int *x, *y):
    SELF
    al_get_window_position(self->a5, x, y)

def platform_display_initial_position(int x, y):
    al_set_new_window_position(x, y)

def platform_display_resize(int w, h):
    SELF
    al_resize_display(self->a5, w, h)

def land_a5_display_check_transform():
    LandDisplayPlatform *self = (void *)_land_active_display
    LandDisplay *super = &self.super

    if super.matrix_modified:
        self.transform.m[0][0] = super.matrix.v[0]
        self.transform.m[1][0] = super.matrix.v[1]
        self.transform.m[2][0] = super.matrix.v[2]
        self.transform.m[3][0] = super.matrix.v[3]
        self.transform.m[0][1] = super.matrix.v[4]
        self.transform.m[1][1] = super.matrix.v[5]
        self.transform.m[2][1] = super.matrix.v[6]
        self.transform.m[3][1] = super.matrix.v[7]
        self.transform.m[0][2] = super.matrix.v[8]
        self.transform.m[1][2] = super.matrix.v[9]
        self.transform.m[2][2] = super.matrix.v[10]
        self.transform.m[3][2] = super.matrix.v[11]
        self.transform.m[0][3] = super.matrix.v[12]
        self.transform.m[1][3] = super.matrix.v[13]
        self.transform.m[2][3] = super.matrix.v[14]
        self.transform.m[3][3] = super.matrix.v[15]
        al_use_transform(&self.transform)
        super.matrix_modified = False

def platform_check_blending_and_transform():
    SELF
    land_a5_display_check_transform()

    if super->blend:
        al_store_state(&self->blend_state, ALLEGRO_STATE_BLENDER)
        #ALLEGRO_COLOR c
        #if super->blend & LAND_BLEND_TINT:
        #    c = self->c
        if super->blend & LAND_BLEND_SOLID:
            al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_ZERO)
        elif super->blend & LAND_BLEND_ADD:
            al_set_blender(ALLEGRO_ADD, ALLEGRO_ALPHA, ALLEGRO_ONE)

def platform_uncheck_blending():
    SELF
    if super->blend:
        al_restore_state(&self->blend_state)

def check_blending_and_transform: platform_check_blending_and_transform()
def uncheck_blending: platform_uncheck_blending()

def platform_display_set():
    SELF
    int f = 0
    if self->a5:
        # FIXME: check for changed parameters
        if super->flags & LAND_FULLSCREEN:
            al_set_display_flag(self->a5, ALLEGRO_FULLSCREEN_WINDOW, True)
        else:
            al_set_display_flag(self->a5, ALLEGRO_FULLSCREEN_WINDOW, False)
        super->w = al_get_display_width(self->a5)
        super->h = al_get_display_height(self->a5)
        land_resize_event(super->w, super->h)
        platform_trigger_redraw()
        return
    if super->flags & LAND_FULLSCREEN:
        f |= ALLEGRO_FULLSCREEN_WINDOW
    if super->flags & LAND_RESIZE:
        f |= ALLEGRO_RESIZABLE
    if super->flags & LAND_OPENGL:
        f |= ALLEGRO_OPENGL | ALLEGRO_PROGRAMMABLE_PIPELINE
    if super->flags & LAND_MULTISAMPLE:
        al_set_new_display_option(ALLEGRO_SAMPLE_BUFFERS, 1, ALLEGRO_SUGGEST);
        al_set_new_display_option(ALLEGRO_SAMPLES, 4, ALLEGRO_SUGGEST);
    if super->flags & LAND_DEPTH:
        al_set_new_display_option(ALLEGRO_DEPTH_SIZE, 16, ALLEGRO_SUGGEST)
    if super->flags & LAND_DEPTH32:
        al_set_new_display_option(ALLEGRO_DEPTH_SIZE, 32, ALLEGRO_SUGGEST)
    if super->flags & LAND_LANDSCAPE:
        al_set_new_display_option(ALLEGRO_SUPPORTED_ORIENTATIONS,
            ALLEGRO_DISPLAY_ORIENTATION_LANDSCAPE, ALLEGRO_SUGGEST)
    if super->flags & LAND_FRAMELESS:
        f |= ALLEGRO_FRAMELESS;

    if super->flags & LAND_ANTIALIAS:
        al_set_new_bitmap_flags(ALLEGRO_MAG_LINEAR | ALLEGRO_MIN_LINEAR)

    f |= ALLEGRO_DRAG_AND_DROP

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

    *** "ifdef" ANDROID
    f |= ALLEGRO_OPENGL | ALLEGRO_PROGRAMMABLE_PIPELINE
    *** "endif"

    #f |= ALLEGRO_OPENGL_ES_PROFILE;
    
    if f:
        al_set_new_display_flags(f)
        
    #al_set_new_display_option(ALLEGRO_COLOR_SIZE, 32, ALLEGRO_SUGGEST)
    #al_set_new_display_option(ALLEGRO_DEPTH_SIZE, 16, ALLEGRO_SUGGEST)
    
    land_log_message("Calling al_create_display(%d, %d).\n", super->w,
        super->h)
    self->a5 = al_create_display(super->w, super->h)
    if self->a5:
        land_log_message("    Success!\n")
    else:
        land_log_message("    Failed activating Allegro display.\n")

    if super->flags & LAND_FULLSCREEN:
        super->w = al_get_display_width(self->a5)
        super->h = al_get_display_height(self->a5)
        super->clip_x2 = super->w
        super->clip_y2 = super->h
        land_log_message("Using actual size of %dx%d.\n",
            super->w, super->h)

    if f & ALLEGRO_PROGRAMMABLE_PIPELINE:
        land_display_set_default_shaders()
        land_render_state(LAND_ALPHA_TEST, False)

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

def platform_display_clear_depth(LandDisplay *self, float z):
    al_clear_depth_buffer(z)

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

def platform_filled_pieslice(float x, y, x_, y_, a, a_):
    SELF
    float cx = (x + x_) * 0.5
    float cy = (y + y_) * 0.5
    float rx = (x_ - x) * 0.5
    #float ry = (y_ - y) * 0.5
    check_blending_and_transform()
    al_draw_filled_pieslice(cx, cy, rx, a, (a_ - a), self->c)
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

def platform_ribbon_loop(int n, float *xy):
    SELF
    check_blending_and_transform()
    
    for int i = 0 while i < n with i++:
        float xy8[8]
        xy8[2] = xy[i * 2 + 0]
        xy8[3] = xy[i * 2 + 1]

        int i_n = (i + 1) % n

        xy8[0] = xy[i * 2 + 0]
        xy8[1] = xy[i * 2 + 1]
        xy8[6] = xy[i_n * 2 + 0]
        xy8[7] = xy[i_n * 2 + 1]

        xy8[4] = xy[i_n * 2 + 0]
        xy8[5] = xy[i_n * 2 + 1]
        
        float ex = xy8[0] - xy8[6]
        float ey = xy8[1] - xy8[7]
        float e = sqrt(ex * ex + ey * ey)
        
        e *= 0.33

        if true:
            int i_p = (i + n - 1) % n
            float dx = xy[i_n * 2 + 0] - xy[i_p * 2 + 0]
            float dy = xy[i_n * 2 + 1] - xy[i_p * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[2] += e * dx / d
            xy8[3] += e * dy / d

        if true:
            int i_nn = (i_n + 1) % n
            float dx = xy[i * 2 + 0] - xy[i_nn * 2 + 0]
            float dy = xy[i * 2 + 1] - xy[i_nn * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[4] += e * dx / d
            xy8[5] += e * dy / d

        al_draw_spline(xy8, self->c, self->super.thickness)

    uncheck_blending()

def platform_filled_ribbon(int n, float *xy):
    SELF
    check_blending_and_transform()

    int q = 8

    # For n points we get to draw n spline segments. For example if we
    # have 3 points there is 3 spline segments.
    # For each spline segment we add (q - 1) polygon points. For example if
    # q is 2 then we add 1 point for each segment. 
    # So in total: n * (q - 1)

    int points = n * (q - 1)
    float v[points * 2]

    for int i = 0 while i < n with i++:
        float xy8[8]
        xy8[2] = xy[i * 2 + 0]
        xy8[3] = xy[i * 2 + 1]

        int i_n = (i + 1) % n

        xy8[0] = xy[i * 2 + 0]
        xy8[1] = xy[i * 2 + 1]
        xy8[6] = xy[i_n * 2 + 0]
        xy8[7] = xy[i_n * 2 + 1]

        xy8[4] = xy[i_n * 2 + 0]
        xy8[5] = xy[i_n * 2 + 1]
        
        float ex = xy8[0] - xy8[6]
        float ey = xy8[1] - xy8[7]
        float e = sqrt(ex * ex + ey * ey)
        
        e *= 0.33

        if true:
            int i_p = (i + n - 1) % n
            float dx = xy[i_n * 2 + 0] - xy[i_p * 2 + 0]
            float dy = xy[i_n * 2 + 1] - xy[i_p * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[2] += e * dx / d
            xy8[3] += e * dy / d

        if true:
            int i_nn = (i_n + 1) % n
            float dx = xy[i * 2 + 0] - xy[i_nn * 2 + 0]
            float dy = xy[i * 2 + 1] - xy[i_nn * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[4] += e * dx / d
            xy8[5] += e * dy / d

        al_calculate_spline(v + (i * (q - 1)) * 2, 2 * sizeof(float), xy8, 0, q)

    int holes[2] = {points, 0}
    platform_filled_polygon_with_holes(points, v, holes)

    uncheck_blending()

def platform_colored_ribbon(LandRibbon *ribbon):
    SELF
    check_blending_and_transform()

    if not ribbon.pos:
        land_ribbon_color(ribbon, land_color_get())

    if not ribbon.filled and not ribbon.w:
        land_ribbon_width(ribbon, super->thickness if super->thickness > 0 else 1)

    if not ribbon.calculated:
        land_ribbon_calculate(ribbon)

    int how = ALLEGRO_PRIM_TRIANGLE_STRIP
    if ribbon.fan: how = ALLEGRO_PRIM_TRIANGLE_FAN
    _polygon(None, ribbon.vertex_count, ribbon.v, None, ribbon.vcol, how)

    # for int i in range(1, segments + 1):
        # int j = i - 1
        # float x1 = (v[j * 4 + 0] + v[j * 4 + 2]) / 2
        # float y1 = (v[j * 4 + 1] + v[j * 4 + 3]) / 2
        # float x2 = (v[i * 4 + 0] + v[i * 4 + 2]) / 2
        # float y2 = (v[i * 4 + 1] + v[i * 4 + 3]) / 2
        # al_draw_line(x1, y1, (x1 + x2) / 2, (y1 + y2) / 2, al_map_rgb_f(1, 1, 0), 0)

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

def platform_filled_strip(int n, float *xy):
    SELF
    ALLEGRO_VERTEX v[n]
    memset(v, 0, n * sizeof(ALLEGRO_VERTEX))
    int j = 0
    for int i = 0 while i < n with i++:
        v[i].x = xy[j++]
        v[i].y = xy[j++]
        v[i].color = self->c
    check_blending_and_transform()
    al_draw_prim(v, None, None, 0, n, ALLEGRO_PRIM_TRIANGLE_STRIP)
    uncheck_blending()

def _polygon(LandImage *image, int n, const float *xy, *uv, *rgba, int arrangement):
    SELF
    
    LandImagePlatform *pim = (void *)image;
    
    ALLEGRO_VERTEX v[n]
    memset(v, 0, n * sizeof(ALLEGRO_VERTEX))
    int j = 0
    int k = 0
    int l = 0
    for int i = 0 while i < n with i++:
        v[i].x = xy[j++]
        v[i].y = xy[j++]
        if uv:
            v[i].u = uv[k++]
            v[i].v = uv[k++]
        else:
            v[i].u = 0
            v[i].v = 0
        if rgba:
            v[i].color.r = rgba[l++]
            v[i].color.g = rgba[l++]
            v[i].color.b = rgba[l++]
            v[i].color.a = rgba[l++]
        else:
            v[i].color = self->c
    check_blending_and_transform()
    al_draw_prim(v, None, pim ? pim->a5 : None, 0, n, arrangement)
    uncheck_blending()

def platform_textured_colored_polygon(LandImage *image, int n, float *xy, *uv, *rgba):
    _polygon(image, n, xy, uv, rgba, ALLEGRO_PRIM_TRIANGLE_FAN)

def platform_textured_polygon(LandImage *image, int n, float *xy, float *uv):
    platform_textured_colored_polygon(image, n, xy, uv, None)

def platform_filled_colored_polygon(int n, float *xy, *rgba):
    platform_textured_colored_polygon(None, n, xy, None, rgba)

def platform_filled_polygon_with_holes(int n, float *xy, int *holes):
    SELF

    check_blending_and_transform()
    al_draw_filled_polygon_with_holes(xy,
        holes, self->c)
    uncheck_blending()

def platform_3d_triangles(int n, LandFloat *xyzrgb):
    ALLEGRO_VERTEX v[n]
    for int i in range(n):
        LandFloat *f = xyzrgb + i * 6
        v[i].x = f[0]
        v[i].y = f[1]
        v[i].z = f[2]
        v[i].u = 0
        v[i].v = 0
        v[i].color.r = f[3]
        v[i].color.g = f[4]
        v[i].color.b = f[5]
        v[i].color.a = 1
    check_blending_and_transform()
    al_draw_prim(v, None, None, 0, n, ALLEGRO_PRIM_TRIANGLE_LIST)
    uncheck_blending()

def platform_plot(float x, y):
    SELF
    check_blending_and_transform()
    al_draw_pixel(x, y, self->c)
    uncheck_blending()
    
def platform_pick_color(float x, y):
    SELF
    float32_t r, g, b, a
    self->c = al_get_pixel(al_get_target_bitmap(), x, y)
    al_unmap_rgba_f(self->c, &r, &g, &b, &a)
    super->color_r = r
    super->color_g = g
    super->color_b = b
    super->color_a = a

static int a5state[] = {
    ALLEGRO_ALPHA_TEST,
    ALLEGRO_ALPHA_FUNCTION,
    ALLEGRO_ALPHA_TEST_VALUE,
    ALLEGRO_WRITE_MASK,
    ALLEGRO_DEPTH_TEST,
    ALLEGRO_DEPTH_FUNCTION
    }

static int a5func[] = {
    ALLEGRO_RENDER_NEVER,
    ALLEGRO_RENDER_ALWAYS,
    ALLEGRO_RENDER_LESS,
    ALLEGRO_RENDER_EQUAL,
    ALLEGRO_RENDER_LESS_EQUAL,
    ALLEGRO_RENDER_GREATER,
    ALLEGRO_RENDER_NOT_EQUAL,
    ALLEGRO_RENDER_GREATER_EQUAL
    }

def platform_render_state(int state, value):
    int value2 = value
    if state == LAND_ALPHA_FUNCTION or state == LAND_DEPTH_FUNCTION:
        value2 = a5func[value]
    elif state == LAND_WRITE_MASK:
        value2 = 0
        if value & LAND_RED_MASK: value2 |= ALLEGRO_MASK_RED
        if value & LAND_GREEN_MASK: value2 |= ALLEGRO_MASK_GREEN
        if value & LAND_BLUE_MASK: value2 |= ALLEGRO_MASK_BLUE
        if value & LAND_ALPHA_MASK: value2 |= ALLEGRO_MASK_ALPHA
        if value & LAND_DEPTH_MASK: value2 |= ALLEGRO_MASK_DEPTH
    al_set_render_state(a5state[state], value2)

def platform_set_default_shaders():
    SELF
    if not self->default_shader:
        ALLEGRO_SHADER *shader
        shader = al_create_shader(ALLEGRO_SHADER_GLSL)
        str vs = al_get_default_shader_source(ALLEGRO_SHADER_AUTO,
            ALLEGRO_VERTEX_SHADER)
        str fs = al_get_default_shader_source(ALLEGRO_SHADER_AUTO,
            ALLEGRO_PIXEL_SHADER)
        #print("vertex shader: %s", vs)
        #print("fragment shader: %s", fs)
        al_attach_shader_source(shader, ALLEGRO_VERTEX_SHADER, vs)
        al_attach_shader_source(shader, ALLEGRO_PIXEL_SHADER, fs)
        al_build_shader(shader)
        self->default_shader = shader
    al_use_shader(self->default_shader)

def platform_reset_projection:
    ALLEGRO_TRANSFORM trans
    al_identity_transform(&trans)
    al_orthographic_transform(&trans, 0, 0, -1.0,
        land_display_width(), land_display_height(), 1.0)
    al_use_projection_transform(&trans)
    
def platform_projection(Land4x4Matrix m):
    ALLEGRO_TRANSFORM t
    t.m[0][0] = m.v[0]
    t.m[1][0] = m.v[1]
    t.m[2][0] = m.v[2]
    t.m[3][0] = m.v[3]
    t.m[0][1] = m.v[4]
    t.m[1][1] = m.v[5]
    t.m[2][1] = m.v[6]
    t.m[3][1] = m.v[7]
    t.m[0][2] = m.v[8]
    t.m[1][2] = m.v[9]
    t.m[2][2] = m.v[10]
    t.m[3][2] = m.v[11]
    t.m[0][3] = m.v[12]
    t.m[1][3] = m.v[13]
    t.m[2][3] = m.v[14]
    t.m[3][3] = m.v[15]
    al_use_projection_transform(&t)

def platform_get_dpi -> int:
    return al_get_monitor_dpi(0)
