import global land.land
import noise_dialog
import rivers

typedef unsigned char byte

LandImage *image
LandVector *normals
Dialog *dialog
global LandWidget *color_picker
LandVector light
LandTriangles *triangles
LandTriangles *triangles_debug
Camera *camera
LandFile *export_f
float export_dupl[11 * 12]
int export_dupl_i
LandRandom *rgen

LandFloat water_start_z
LandFloat water_end_z
LandFloat grass_start_z
LandFloat grass_end_z
LandFloat mountain_start_z
LandFloat mountain_end_z
LandFloat snow_start_z

LandColor water_c
LandColor shore_c
LandColor grass_c
LandColor hills_c
LandColor mountain_c
LandColor snow_c

def _export_dupl_add(float *v):
    memcpy(export_dupl + export_dupl_i * 11, v, 11 * 4)
    export_dupl_i++
    if export_dupl_i == 12: export_dupl_i = 0

def _export_dupl_get(int offset) -> float*:
    offset += export_dupl_i
    if offset < 0: offset += 12
    return export_dupl + offset * 11

def cb_gray(int x, y, byte *rgba, void *user):
    LandNoise **noises = user
    LandFloat v = land_noise_at(noises[0], x, y)
    land_constrain(&v, -1, 1)
    int c = (1 + v) / 2 * 255
    int r = c
    int g = c
    int b = c
    rgba[0] = r 
    rgba[1] = g
    rgba[2] = b 
    rgba[3] = 255

def _blend(LandColor c1, c2, float f) -> LandColor:
    return land_color_rgba(
        c2.r * f + c1.r * (1 - f),
        c2.g * f + c1.g * (1 - f),
        c2.b * f + c1.b * (1 - f), 1)

def get_type(float height) -> int:
    if height < grass_start_z: return 0
    if height < grass_end_z: return 1
    if height < mountain_end_z: return 2
    return 3

def get_color_for_height(LandFloat v) -> LandColor:
    """
    v is from -1 to +1
    """
    LandColor rgb
    if v < water_start_z:
        rgb = water_c
    elif v < water_end_z:
        v -= water_start_z
        v /= water_end_z - water_start_z
        rgb = _blend(water_c, shore_c, v)
    elif v < grass_start_z:
        v -= water_end_z
        v /= grass_start_z - water_end_z
        rgb = _blend(shore_c, grass_c, v)
    elif v < grass_end_z:
        v -= grass_start_z
        v /= grass_end_z - grass_start_z
        rgb = _blend(grass_c, hills_c, v)
    elif v < mountain_start_z:
        v -= grass_end_z
        v /= mountain_start_z - grass_end_z
        rgb = _blend(hills_c, mountain_c, v)
    elif v < mountain_end_z:
        rgb = mountain_c
    elif v < snow_start_z:
        v -= mountain_end_z
        v /= snow_start_z - mountain_end_z
        rgb = _blend(mountain_c, snow_c, v)
    else:
        rgb = snow_c
    return rgb

def cb_color(int x, y, byte *rgba, void *user):
    LandNoise **noises = user
    LandFloat v = land_noise_at(noises[0], x, y)

    LandColor rgb = get_color_for_height(v)
    if noises[1]:
        LandFloat r = land_noise_at(noises[1], x, y)
        if r > 0:
            rgb.r *= (1 - r)
            rgb.g *= (1 - r)
            rgb.b *= (1 - r)
            rgb.r += r * water_c.r
            rgb.g += r * water_c.g
            rgb.b += r * water_c.b

    float l = calculate_light(noises[0], x, y)
    l = (1 + l) / 2
    rgb.r *= l
    rgb.g *= l
    rgb.b *= l

    int a = 255
    rgba[0] = land_constrainf(rgb.r, 0, 1) * a 
    rgba[1] = land_constrainf(rgb.g, 0, 1) * a
    rgba[2] = land_constrainf(rgb.b, 0, 1) * a
    rgba[3] = a

def calculate_light(LandNoise *noise, int x, y) -> float:
    """
    #
    # 1           2
    #   .   a   .
    #     .   .
    #   d   5   b
    #     .   .
    #   .   c   .
    # 3           4
    #
    """
    LandFloat v1 = land_noise_at(noise, x, y)
    LandFloat v2 = land_noise_at(noise, x + 1, y)
    LandFloat v3 = land_noise_at(noise, x, y + 1)
    LandFloat v4 = land_noise_at(noise, x + 1, y + 1)
    LandFloat v5 = (v1 + v2 + v3 + v4) / 4

    LandFloat zs = 16
    LandVector l1 = land_vector(-.5, -.5, zs * (v1 - v5))
    LandVector l2 = land_vector(+.5, -.5, zs * (v2 - v5))
    LandVector l3 = land_vector(-.5, +.5, zs * (v3 - v5))
    LandVector l4 = land_vector(+.5, +.5, zs * (v4 - v5))
    
    l1 = land_vector_normalize(l1)
    l2 = land_vector_normalize(l2)
    l3 = land_vector_normalize(l3)
    l4 = land_vector_normalize(l4)

    LandVector upper = land_vector_cross(l1, l2)
    LandVector right = land_vector_cross(l2, l4)
    LandVector lower = land_vector_cross(l4, l3)
    LandVector left = land_vector_cross(l3, l1)

    #printf("%f/%f/%f . %f/%f/%f\n", light.x, light.y, light.z,
    #    upper.x, upper.y, upper.z)

    LandFloat upper_light = -land_vector_dot(light, upper)
    LandFloat right_light = -land_vector_dot(light, right)
    LandFloat lower_light = -land_vector_dot(light, lower)
    LandFloat left_light = -land_vector_dot(light, left)

    LandVector *normal = normals + y * noise.w * 4 + x * 4
    normal[0] = upper
    normal[1] = right
    normal[2] = lower
    normal[3] = left

    return (upper_light + lower_light + right_light + left_light) / 4

def color(byte *rgba, float *c):
    c[0] = rgba[0] / 255.0
    c[1] = rgba[1] / 255.0
    c[2] = rgba[2] / 255.0
    c[3] = rgba[3] / 255.0

def _export_v(LandVector p, LandVector n):
    float zs = 16
    LandColor c = get_color_for_height(p.z / zs * 2 - 1)

    float xa = 1
    float ya = 1
    int w = land_image_width(image)
    int h = land_image_height(image)
    if p.y < 10: ya = p.y * 1.0 / 10
    if p.x < 10: xa = p.x * 1.0 / 10
    if p.y > h - 10: ya = (h - p.y) * 1.0 / 10
    if p.x > w - 10: xa = (w - p.x) * 1.0 / 10
    float a = xa
    if ya < a: a = ya
    
    float fb[] = {p.x, p.y, p.z, n.x, n.y, n.z, c.r * a, c.g * a, c.b * a, a, 0}
    _export_dupl_add(fb)
    land_file_write(export_f, (char *)&fb, 44)         

def _export_v_dupl(int offset):
    float *fb = _export_dupl_get(offset)
    _export_dupl_add(fb)
    land_file_write(export_f, (char *)fb, 44)         

def _add_vertex(LandTriangles *t, LandVector v, float tu, tv, r, g, b, a, bool export):
    land_add_vertex(t, v.x, v.y, v.z, tu, tv, r, g, b, a)

def _duplicate_vertex(LandTriangles *t, int offset, bool export):
    land_duplicate_vertex(t, offset)

def make_triangles(LandNoise *noise, int w, h, bool debug_grid,
        bool export):
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

    if export:
        land_file_put32le(export_f, 1) # frames

        land_file_put32le(export_f, w * h * 12) # vertices
        land_file_put32le(export_f, 3 + 3 + 4 + 1) # stride

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

            LandVector v1 = land_vector(x, y, z1)
            LandVector v2 = land_vector(x + 1, y, z2)
            LandVector v3 = land_vector(x, y + 1, z3)
            LandVector v4 = land_vector(x + 1, y + 1, z4)
            LandVector v5 = land_vector(x + 0.5, y + 0.5, z5)

            _add_vertex(t, v5, 0, 0, c5[0], c5[1], c5[2], c5[3], export)
            _add_vertex(t, v1, 0, 0, c1[0], c1[1], c1[2], c1[3], export)
            _add_vertex(t, v2, 0, 0, c2[0], c2[1], c2[2], c2[3], export)
            
            _duplicate_vertex(t, -3, export)
            _duplicate_vertex(t, -2, export)
            _add_vertex(t, v4, 0, 0, c4[0], c4[1], c4[2], c4[3], export)
            
            _duplicate_vertex(t, -3, export)
            _duplicate_vertex(t, -2, export)
            _add_vertex(t, v3, 0, 0, c3[0], c3[1], c3[2], c3[3], export)
            
            _duplicate_vertex(t, -3, export)
            _duplicate_vertex(t, -2, export)
            _duplicate_vertex(t, -10, export)

            if export:
                LandVector n[36]
                #.-------.-------.-------.
                #| \ 0 / | \ 4 / | \ 8 / |
                #| 3 X 1 | 7 X 5 |11 X 9 |
                #| / 2 \ | / 6 \ | /10 \ |
                #.-------*-------*-------.
                #| \ 12/ | \ 16/ | \ 20/ |
                #|15 X 13|19 X 17|23 X 21|
                #| /14 \ | /18 \ | /22 \ |
                #.-------*-------*-------.
                #| \ 24/ | \ 28/ | \ 32/ |
                #|27 X 25|31 X 29|35 X 33|
                #| /26 \ | /30 \ | /34 \ |
                #.-------.-------.-------.
                for int nj in range(3):
                    for int ni in range(3):
                        int yn = (y + nj + h - 1) % h
                        int xn = (x + ni + w - 1) % w
                        int nc = ni + 3 * nj
                        for int nk in range(4):
                            n[nc * 4 + nk] = normals[yn * noise.w * 4 +
                                xn * 4 + nk]
                LandVector n1 = land_vector_add8(n[1], n[2], n[6], n[7], n[16], n[19], n[12], n[13])
                LandVector n2 = land_vector_add8(n[5], n[6], n[10], n[11], n[20], n[23], n[16], n[17])
                LandVector n3 = land_vector_add8(n[13], n[14], n[18], n[19], n[28], n[31], n[24], n[25])
                LandVector n4 = land_vector_add8(n[17], n[18], n[22], n[23], n[32], n[35], n[28], n[29])
                LandVector n5 = land_vector_add4(n[16], n[17], n[18], n[19])
                _export_v(v5, land_vector_normalize(n5))
                _export_v(v1, land_vector_normalize(n1))
                _export_v(v2, land_vector_normalize(n2))
                _export_v_dupl(-3)
                _export_v_dupl(-2)
                _export_v(v4, land_vector_normalize(n4))
                _export_v_dupl(-3)
                _export_v_dupl(-2)
                _export_v(v3, land_vector_normalize(n3))
                _export_v_dupl(-3)
                _export_v_dupl(-2)
                _export_v_dupl(-10)

            if debug_grid:
                land_add_vertex(td, x + 0.05, y + 0.05, z1 + 1, 0, 0, 1, 0, 0, 1)
                land_add_vertex(td, x, y, z1 + 1, 0, 0, 1, 0, 0, 1)
                land_add_vertex(td, x + 1, y, z2 + 1, 0, 0, 1, 0, 0, 1)

                land_duplicate_vertex(td, -2)
                land_duplicate_vertex(td, -4)
                land_add_vertex(td, x, y + 1, z3 + 1, 0, 0, 1, 0, 0, 1)

            p += 4
            
    land_free(rgba)

    if export:
        land_file_put32le(export_f, 0) # markers

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

    light = land_vector_normalize(land_vector(1, 1, -1))

    land_set_prefix(None)

    main_heightmap()

    land_alloc(camera)
    camera_init(camera)

def main_generate(bool want_color, bool want_triangles, bool debug, bool export):

    water_start_z = dialog.pos0->v / 31.0 * 2 - 1
    water_end_z = dialog.pos1->v / 31.0 * 2 - 1
    grass_start_z = dialog.pos2->v / 31.0 * 2 - 1
    grass_end_z = dialog.pos3->v / 31.0 * 2 - 1
    mountain_start_z = dialog.pos4->v / 31.0 * 2 - 1
    mountain_end_z = dialog.pos5->v / 31.0 * 2 - 1
    snow_start_z = dialog.pos6->v / 31.0 * 2 - 1

    water_c = land_color_int(dialog.color1->v)
    shore_c = land_color_int(dialog.color2->v)
    grass_c = land_color_int(dialog.color3->v)
    hills_c = land_color_int(dialog.color4->v)
    mountain_c = land_color_int(dialog.color5->v)
    snow_c = land_color_int(dialog.color6->v)
    
    int w = 0
    int h = 0
    if image:
        w = land_image_width(image)
        h = land_image_height(image)
    int sw = 1 << dialog.width->v
    int sh = 1 << dialog.height->v
    if sw != w or sh != h:
        w = sw
        h = sh
        if image: land_image_destroy(image)
        image = land_image_new(w, h)

        if normals: land_free(normals)
        normals = land_calloc(4 * w * h * sizeof *normals)

    if triangles:
        land_triangles_destroy(triangles)
        triangles = None

    LandNoiseType x[] = {LandNoiseVoronoi, LandNoisePerlin,
        LandNoisePlasma, LandNoiseWhite, LandNoiseWaves}
    LandNoiseType t = x[dialog.noise->v]

    LandPerlinLerp lerp = dialog.lerp->v

    if rgen: land_random_del(rgen)
    rgen = land_random_new(dialog.seed->v)
    LandNoise *noise = land_noise_new(t, 0)
    land_noise_set_random(noise, rgen)
    land_noise_set_size(noise, w, h)
    land_noise_set_wrap(noise, dialog.wrap->v)
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
        LandNoise *n2 = land_noise_new(t, 0)
        land_noise_set_random(n2, rgen)
        land_noise_set_wrap(n2, dialog.wrap->v)
        land_noise_set_warp(n2, noise, wox, woy, wsx, wsy)
        noise = n2

    if dialog.blur->v:
        int s = dialog.blur_size->v
        LandNoise *n2 = land_noise_new(t, 0)
        land_noise_set_random(n2, rgen)
        land_noise_set_wrap(n2, dialog.wrap->v)
        land_noise_set_blur(n2, noise, s)
        noise = n2

    land_noise_z_transform(noise, pow(2, dialog.z_scale->v / 8.0),
        dialog.z_offset->v / 16.0)
    land_noise_z_ease(noise, dialog.z_ease->v / 16.0)
    land_noise_prepare(noise)

    if dialog.plateau->v:
        land_noise_set_minmax(noise, -1 + dialog.plateau->v / 32.0, 1000)

    LandNoise* rn = None
    if dialog.river->v:
        rn = rivers(noise, water_end_z, mountain_end_z)

    void *blah[2] = {noise, rn}

    land_image_write_callback(image, want_color ? cb_color : cb_gray,
        blah)

    if want_triangles:
        make_triangles(noise, w, h, debug, export)

    land_noise_destroy(noise)  

def main_seed:
    dialog.seed->v = land_rand(0, 0xfffffff)
    main_generate(False, False, False, False)

def main_color:
    main_generate(True, False, False, False)
    
def main_heightmap:
    main_generate(False, False, False, False)

def main_triangles(bool debug):
    main_generate(True, True, debug, False)

def _add_split(LandHash *sets, str key, int size, char *v):
    LandBuffer *b = land_hash_get(sets, key)
    if not b:
        printf("split for %s\n", key)
        b = land_buffer_new()
        land_hash_insert(sets, key, b)
    land_buffer_add(b, v, size)

def main_export(int (*split_cb)(float x, float y, float z), bool debug):
    export_f = land_file_new("perlin.mesh", "wb")
    main_generate(True, True, debug, True)
    land_file_destroy(export_f)

    if split_cb:
        LandHash *sets = land_hash_new()
        LandFile *f = land_file_new("perlin.mesh", "rb")
        int fn = land_file_get32le(f)
        for int fi in range(fn):
            int vn = land_file_get32le(f)
            int stride = land_file_get32le(f)
            for int vi in range(0, vn, 12):
                char b[stride * 4 * 12]
                land_file_read(f, b, stride * 4 * 12)
                float *x = (void *)b
                float *y = (void *)(b + 4)
                float *z = (void *)(b + 8)
                int s = split_cb(*x, *y, *z)
                char key[10]
                sprintf(key, "%05d", s)
                _add_split(sets, key, stride * 4 * 12, b)
            int mn = land_file_get32le(f)
            for int im in range(mn):
                int sn = land_file_get32le(f)
                land_file_skip(f, sn)
        land_file_destroy(f)

        f = land_file_new("perlin.mesh", "wb")
        land_file_put32le(f, sets.count)
        LandArray *a = land_hash_keys(sets, False)
        land_array_sort_alphabetical(a)
        for str key in a:
            LandBuffer *b = land_hash_get(sets, key)
            land_file_put32le(f, b.n / (11 * 4))
            land_file_put32le(f, 11)
            land_file_write(f, b.buffer, b.n)
            land_file_put32le(f, 0) # no markers
        land_file_destroy(f)

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

    if color_picker:
        land_widget_tick(color_picker)
    else:
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

    if land_mouse_x() >= 1024: return

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
        land_image_draw_scaled(image, 0, 0, 1024.0 / w, 1024.0 / w)

    land_render_state(LAND_DEPTH_TEST, False)
    land_projection(land_4x4_matrix_orthographic(0, land_display_height(), 1, land_display_width(), 0, -1))
    if color_picker:
        land_widget_draw(color_picker)
    else:
        land_widget_draw(dialog.view)

land_begin_shortcut(1024 + 250, 1024, 60, LAND_OPENGL | LAND_WINDOWED,
    init, NULL, tick, draw, NULL, NULL)
