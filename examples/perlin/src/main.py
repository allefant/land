import global land.land
import noise_dialog

typedef unsigned char byte

LandImage *image
LandRandom *gen
int seed
Dialog *dialog
LandVector light
LandTriangles *triangles
LandTriangles *triangles_debug
Camera *camera

LandFloat water_start_z = -0.1
LandFloat water_end_z = 0
LandFloat grass_start_z = 0.1
LandFloat grass_end_z = 0.5
LandFloat mountain_start_z = 0.6
LandFloat mountain_end_z = 0.9
LandFloat snow_start_z = 0.95

def cb_gray(int x, y, byte *rgba, void *user):
    LandNoise *noise = user
    LandFloat v = land_noise_at(noise, x, y)
    land_constrain(&v, -1, 1)
    int c = (1 + v) / 2 * 255
    int r = c
    int g = c
    int b = c
    rgba[0] = r 
    rgba[1] = g
    rgba[2] = b 
    rgba[3] = 255

def _blend(LandFloat r1, g1, b1, r2, g2, b2, f, *r, *g, *b):
    *r = r2 * f + r1 * (1 - f)
    *g = g2 * f + g1 * (1 - f)
    *b = b2 * f + b1 * (1 - f)

def get_type(float height) -> int:
    if height < grass_start_z: return 0
    if height < grass_end_z: return 1
    if height < mountain_end_z: return 2
    return 3

def cb_color(int x, y, byte *rgba, void *user):
    LandNoise *noise = user
    LandFloat v = land_noise_at(noise, x, y)
    v = (1 + v) / 2
    
    LandFloat r = 0
    LandFloat g = 0
    LandFloat b = 0

    if v < water_start_z:
        r = 0
        g = 0
        b = 1
    elif v < water_end_z:
        v -= water_start_z
        v /= water_end_z - water_start_z

        _blend(0, 0, 1,
            0.1, 0.5, 1,
            v, &r, &g, &b)
    elif v < grass_start_z:
        v -= water_end_z
        v /= grass_start_z - water_end_z

        _blend(0.1, 0.5, 1,
            0.55, 1, 0.3,
            v, &r, &g, &b)
    elif v < grass_end_z:
        r = 0.55
        g = 1
        b = 0.3
    elif v < mountain_start_z:
        v -= grass_end_z
        v /= mountain_start_z - grass_end_z

        _blend(0.55, 1, 0.3,
            1, 0.6, 0.3,
            v, &r, &g, &b)
    elif v < mountain_end_z:
        r = 1
        g = 0.6
        b = 0.3
    elif v < snow_start_z:
        v -= mountain_end_z
        v /= snow_start_z - mountain_end_z
        _blend(1, 0.6, 0.3,
            1, 1, 1,
            v, &r, &g, &b)
    else:
        r = 1
        g = 1
        b = 1

    float l = calculate_light(noise, x, y)
    l = (1 + l) / 2
    r *= l
    g *= l
    b *= l
    
    rgba[0] = land_constrain(&r, 0, 1) * 255 
    rgba[1] = land_constrain(&g, 0, 1) * 255
    rgba[2] = land_constrain(&b, 0, 1) * 255
    rgba[3] = 255

def calculate_light(LandNoise *noise, int x, y) -> float:
    """
    0     1     .
     \ upper
  lower \
    2     3     .


    .     .     .
    """
    LandFloat v0 = land_noise_at(noise, x, y)
    LandFloat v1 = land_noise_at(noise, x + 1, y)
    LandFloat v2 = land_noise_at(noise, x, y + 1)
    LandFloat v3 = land_noise_at(noise, x + 1, y + 1)

    LandFloat zs = 16
    LandVector l1 = land_vector(1, 0, zs * (v1 - v0))
    LandVector l2 = land_vector(0, 1, zs * (v2 - v0))
    LandVector l3 = land_vector(1, 1, zs * (v3 - v0))
    l1 = land_vector_normalize(l1)
    l2 = land_vector_normalize(l2)
    l3 = land_vector_normalize(l3)

    LandVector upper = land_vector_cross(l1, l3)
    LandVector lower = land_vector_cross(l3, l2)

    #printf("%f/%f/%f . %f/%f/%f\n", light.x, light.y, light.z,
    #    upper.x, upper.y, upper.z)

    LandFloat upper_light = -land_vector_dot(light, upper)
    LandFloat lower_light = -land_vector_dot(light, lower)

    return (upper_light + lower_light) / 2

def color(byte *rgba, float *c):
    c[0] = rgba[0] / 255.0
    c[1] = rgba[1] / 255.0
    c[2] = rgba[2] / 255.0
    c[3] = rgba[3] / 255.0

def make_triangles(LandNoise *noise, int w, h, bool debug_grid):
    #
    # 1           2
    #   .       .
    #     .   .
    #       5
    #     .   .
    #   .       .
    # 3           4
    #
    byte *rgba = land_calloc(w * h * 4)
    land_image_get_rgba_data(image, rgba)

    LandTriangles *t = land_triangles_new()
    LandTriangles *td = None
    if debug_grid:
        td = land_triangles_new()
    float c1[4], c2[4], c3[4], c4[4], c5[4]
    byte *p = rgba
    float zs = 16
    for int y in range(h):
        for int x in range(w):
            float z1 = land_noise_at(noise, x, y) * zs
            float z2 = land_noise_at(noise, x + 1, y) * zs
            float z3 = land_noise_at(noise, x, y + 1) * zs
            float z4 = land_noise_at(noise, x + 1, y + 1) * zs
            
            float z5 = (z1 + z2 + z3 + z4) / 4

            color(p, c1)
            int right = x < w - 1 ? 4 : 4 - w * 4
            int bottom = y < h - 1 ? w * 4 : w * 4 - h * w * 4
            color(p + right, c2)
            color(p + bottom, c3)
            color(p + right + bottom, c4)
            for int i in range(4):
                c5[i] = (c1[i] + c2[i] + c3[i] + c4[i]) / 4

            land_add_vertex(t, x + 0.5, y + 0.5, z5, 0, 0, c5[0], c5[1], c5[2], c5[3])
            land_add_vertex(t, x, y, z1, 0, 0, c1[0], c1[1], c1[2], c1[3])
            land_add_vertex(t, x + 1, y, z2, 0, 0, c2[0], c2[1], c2[2], c2[3])
            
            land_duplicate_vertex(t, -3)
            land_duplicate_vertex(t, -2)
            land_add_vertex(t, x + 1, y + 1, z4, 0, 0, c4[0], c4[1], c4[2], c4[3])
            
            land_duplicate_vertex(t, -3)
            land_duplicate_vertex(t, -2)
            land_add_vertex(t, x, y + 1, z3, 0, 0, c3[0], c3[1], c3[2], c3[3])
            
            land_duplicate_vertex(t, -3)
            land_duplicate_vertex(t, -2)
            land_duplicate_vertex(t, -10)

            if debug_grid:
                land_add_vertex(td, x + 0.05, y + 0.05, z1 + 1, 0, 0, 1, 0, 0, 1)
                land_add_vertex(td, x, y, z1 + 1, 0, 0, 1, 0, 0, 1)
                land_add_vertex(td, x + 1, y, z2 + 1, 0, 0, 1, 0, 0, 1)

                land_duplicate_vertex(td, -2)
                land_duplicate_vertex(td, -4)
                land_add_vertex(td, x, y + 1, z3 + 1, 0, 0, 1, 0, 0, 1)

            p += 4
            
    land_free(rgba)

    triangles = t
    if triangles_debug:
        land_triangles_destroy(triangles_debug)
        triangles_debug = None
    if debug_grid:
        triangles_debug = td

def init(LandRunner *self):

    land_find_data_prefix("data/")
    land_font_load("DejaVuSans.ttf", 12)
    LandWidgetTheme* theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)

    dialog = dialog_new()

    gen = land_random_new(0)

    light = land_vector_normalize(land_vector(1, 1, -1))

    main_heightmap()

    land_alloc(camera)
    camera_init(camera)

def main_generate(bool want_color, bool want_triangles, bool debug):
    int w = 0
    int h = 0
    if image:
        w = land_image_width(image)
        h = land_image_height(image)
    int s = 1 << dialog.size->v
    if s != w or s != h:
        w = h = s
        if image: land_image_destroy(image)
        image = land_image_new(w, h)

    if triangles:
        land_triangles_destroy(triangles)
        triangles = None

    LandNoiseType x[] = {LandNoiseVoronoi, LandNoisePerlinMulti,
        LandNoisePlasma, LandNoiseWhite}
    LandNoiseType t = x[dialog.noise->v]

    LandPerlinLerp lerp = dialog.lerp->v

    land_seed(seed)
    LandNoise *noise = land_noise_new(t)
    land_noise_set_size(noise, w, h)
    land_noise_set_count(noise, dialog.count->v)
    land_noise_set_levels(noise, dialog.levels->v)
    land_noise_set_lerp(noise, lerp)
    land_noise_set_randomness(noise, dialog.randomness->v)
    land_noise_set_amplitude(noise, dialog.amplitude->v / 8.0)
    land_noise_set_power_modifier(noise, dialog.power_modifier->v / 8.0)

    if dialog.warp->v:
        float s = w / 256.0 * 4.0
        float wox = dialog.warp_offset_x->v * s * 4
        float woy = dialog.warp_offset_y->v * s * 4
        float wsx = dialog.warp_scale_x->v * s
        float wsy = dialog.warp_scale_y->v * s
        LandNoise *n2 = land_noise_new(t)
        land_noise_set_warp(n2, noise, wox, woy, wsx, wsy)
        noise = n2

    if dialog.blur->v:
        int s = dialog.blur_size->v
        LandNoise *n2 = land_noise_new(t)
        land_noise_set_blur(n2, noise, s)
        noise = n2

    land_noise_z_transform(noise, pow(2, dialog.z_scale->v / 8.0),
        dialog.z_offset->v / 16.0)
    land_noise_z_ease(noise, dialog.z_ease->v / 16.0)
    land_noise_prepare(noise)

    land_image_write_callback(image, want_color ? cb_color : cb_gray, noise)

    if want_triangles:
        make_triangles(noise, w, h, debug)

    land_noise_destroy(noise)  

def main_seed:
    seed = land_random(gen, 0, 1000000)
    main_generate(False, False, False)

def main_color:
    main_generate(True, False, False)
    
def main_heightmap:
    main_generate(False, False, False)

def main_triangles(bool debug):
    main_generate(True, True, debug)


class Camera:
    LandVector p, x, y, z
    LandFloat zoom

def camera_change_locked(Camera *self, float x, z):
    LandVector xaxis = self.x
    self.x = land_vector_rotate(self.x, xaxis, x)
    self.y = land_vector_rotate(self.y, xaxis, x)
    self.z = land_vector_rotate(self.z, xaxis, x)
    
    LandVector zaxis = land_vector(0, 0, 1)
    self.x = land_vector_rotate(self.x, zaxis, z)
    self.y = land_vector_rotate(self.y, zaxis, z)
    self.z = land_vector_rotate(self.z, zaxis, z)

def camera_move(Camera *self, float x, y, z):
    land_vector_iadd(&self.p, land_vector_mul(self.x, x))
    LandVector up = land_vector(0, 0, 1)
    LandVector back = land_vector_cross(self.x, up)
    back = land_vector_normalize(back)
    land_vector_iadd(&self.p, land_vector_mul(back, -y))
    land_vector_iadd(&self.p, land_vector_mul(up, z))

Land4x4Matrix def camera_matrix(Camera *camera):
    Land4x4Matrix m = land_4x4_matrix_inverse_from_vectors(
        &camera.p, &camera.x, &camera.y, &camera.z)

    # apply zoom
    LandFloat s = pow(2, camera.zoom)
    for int i in range(8):
        m.v[i] *= s

    return m

def camera_init(Camera *c):
    memset(c, 0, sizeof *c)
    c.x.x = 1
    c.y.y = 1
    c.z.z = 1

    c.zoom = 2

def tick(LandRunner *self):

    dialog_hide_show(dialog)
    land_widget_tick(dialog.view)
    
    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

    if land_key_pressed(' ') or land_key_pressed(LandKeyEnter):
        main_heightmap()

    if land_key_pressed('s'):
        main_seed()

    if land_key_pressed('c'):
        main_color()

    if land_key_pressed('t'):
        main_triangles(False)

    float dx = 0
    float dy = 0
    float dz = land_mouse_delta_z()
    camera.zoom += dz * 0.1

    if land_key(LandKeyLeft):
        dx = -1
    if land_key(LandKeyRight):
        dx = 1
    if land_key(LandKeyUp):
        dy = -1
    if land_key(LandKeyDown):
        dy = 1

    if land_key(LandKeyRightShift) or\
            land_key(LandKeyLeftShift):
        dx *= 10
        dy *= 10

    camera_move(camera, -dx, -dy, 0)

    if land_mouse_button(1):
        dx = land_mouse_delta_x() * 0.01
        dy = land_mouse_delta_y() * 0.01
        camera_change_locked(camera, -dy, -dx)

    if land_mouse_button(0):
        dx = land_mouse_delta_x() * 1.0 * pow(2, -camera.zoom)
        dy = land_mouse_delta_y() * 1.0 * pow(2, -camera.zoom)
        camera_move(camera, -dx, -dy, 0)

def draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_clear_depth(1)
    
    int w = land_image_width(image)
    int h = land_image_height(image)

    land_projection(land_4x4_matrix_orthographic(0, land_display_height(), 1, land_display_width(), 0, -1))
    
    if triangles:
        land_render_state(LAND_DEPTH_TEST, True)
        float ds = 1024
        Land4x4Matrix m = land_4x4_matrix_translate(-w / 2, -h / 2, 0)

        m = land_4x4_matrix_mul(camera_matrix(camera), m)

        m = land_4x4_matrix_mul(land_4x4_matrix_orthographic(
            -ds / 2, ds / 2, 1000, ds / 2 + 200, -ds / 2, -1000), m)
        
        land_projection(m)
        land_triangles_draw(triangles)
        if triangles_debug: land_triangles_draw(triangles_debug)
    else:
        land_image_draw_scaled(image, 0, 0, 1024.0 / w, 1024.0 / h)

    land_render_state(LAND_DEPTH_TEST, False)
    land_projection(land_4x4_matrix_orthographic(0, land_display_height(), 1, land_display_width(), 0, -1))
    land_widget_draw(dialog.view)

land_begin_shortcut(1024 + 200, 1024, 60, LAND_OPENGL | LAND_WINDOWED,
    init, NULL, tick, draw, NULL, NULL)
