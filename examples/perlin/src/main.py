import global land.land
import noise_dialog
import presets
import rivers
import global complex, fftw3

typedef unsigned char byte

LandImage *image
LandVector *normals
LandFont *font
global Presets *global_presets
global Dialog *global_dialog
global LandWidget *color_picker
LandVector light
LandTriangles *triangles
LandTriangles *triangles_debug
Camera *camera
LandFile *export_f
float export_dupl[11 * 12]
int export_dupl_i
LandRandom *rgen
bool had_text_input

class CallbackInfo:
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

    LandNoise *noise
    LandNoise *river
    LandNoise *stitched

    int n
    CallbackInfo *components
    bool want_color

class Game:
    int last_type

Game _game
Game *game = &_game

def message(str text, LandColor c):
    land_widget_button_set_color(global_dialog.message, c)
    land_widget_button_set_text(global_dialog.message, text)

def _export_dupl_add(float *v):
    memcpy(export_dupl + export_dupl_i * 11, v, 11 * 4)
    export_dupl_i++
    if export_dupl_i == 12: export_dupl_i = 0

def _export_dupl_get(int offset) -> float*:
    offset += export_dupl_i
    if offset < 0: offset += 12
    return export_dupl + offset * 11

def cb_gray(int x, y, byte *rgba, void *user):
    CallbackInfo *info = user
    LandFloat v = land_noise_at(info.noise, x, y)
    land_constrain(&v, -1, 1)
    int c = (1 + v) / 2 * 255
    int r = c
    int g = c
    int b = c
    rgba[0] = r 
    rgba[1] = g
    rgba[2] = b 
    rgba[3] = 255

def cb_compound(int x, y, byte *rgba, void *user):
    CallbackInfo *info = user
    LandVoronoi *v = land_array_get_nth(info.noise.noise, 0)
    int i = land_voronoi_owner(v, x, y)
    i = i % info.n
    CallbackInfo *component = info.components + i
    if info.want_color:
        cb_color(x, y, rgba, component)
    else:
        cb_gray(x, y, rgba, component)

def _blend(LandColor c1, c2, float f) -> LandColor:
    return land_color_rgba(
        c2.r * f + c1.r * (1 - f),
        c2.g * f + c1.g * (1 - f),
        c2.b * f + c1.b * (1 - f), 1)

def get_type(CallbackInfo *info, float height) -> int:
    if height < info.grass_start_z: return 0
    if height < info.grass_end_z: return 1
    if height < info.mountain_end_z: return 2
    return 3

def get_color_for_height(CallbackInfo *info, LandFloat v) -> LandColor:
    """
    v is from -1 to +1
    """
    LandColor rgb
    if v < info.water_start_z:
        rgb = info.water_c
    elif v < info.water_end_z:
        v -= info.water_start_z
        v /= info.water_end_z - info.water_start_z
        rgb = _blend(info.water_c, info.shore_c, v)
    elif v < info.grass_start_z:
        v -= info.water_end_z
        v /= info.grass_start_z - info.water_end_z
        rgb = _blend(info.shore_c, info.grass_c, v)
    elif v < info.grass_end_z:
        v -= info.grass_start_z
        v /= info.grass_end_z - info.grass_start_z
        rgb = _blend(info.grass_c, info.hills_c, v)
    elif v < info.mountain_start_z:
        v -= info.grass_end_z
        v /= info.mountain_start_z - info.grass_end_z
        rgb = _blend(info.hills_c, info.mountain_c, v)
    elif v < info.mountain_end_z:
        rgb = info.mountain_c
    elif v < info.snow_start_z:
        v -= info.mountain_end_z
        v /= info.snow_start_z - info.mountain_end_z
        rgb = _blend(info.mountain_c, info.snow_c, v)
    else:
        rgb = info.snow_c
    return rgb

def cb_color(int x, y, byte *rgba, void *user):
    CallbackInfo *info = user
    LandFloat v = land_noise_at(info.noise, x, y)

    LandColor rgb = get_color_for_height(info, v)
    if info.river:
        LandFloat r = land_noise_at(info.river, x, y)
        if r > 0:
            rgb.r *= (1 - r)
            rgb.g *= (1 - r)
            rgb.b *= (1 - r)
            rgb.r += r * info.water_c.r
            rgb.g += r * info.water_c.g
            rgb.b += r * info.water_c.b

    float l = calculate_light(info.noise, x, y)
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
    float r = 1
    LandFloat v1 = land_noise_at(noise, x, y)
    LandFloat v2 = land_noise_at(noise, x + r, y)
    LandFloat v3 = land_noise_at(noise, x, y + r)
    LandFloat v4 = land_noise_at(noise, x + r, y + r)
    LandFloat v5 = (v1 + v2 + v3 + v4) / 4

    LandFloat zs = 16
    LandVector l1 = land_vector(-r, -r, zs * (v1 - v5))
    LandVector l2 = land_vector(+r, -r, zs * (v2 - v5))
    LandVector l3 = land_vector(-r, +r, zs * (v3 - v5))
    LandVector l4 = land_vector(+r, +r, zs * (v4 - v5))
    
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

def _export_v(CallbackInfo *info, LandVector p, LandVector n):
    float zs = 16
    LandColor c = get_color_for_height(info, p.z / zs * 2 - 1)

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

def make_triangles(LandNoise *noise, CallbackInfo *info, int w, h, bool debug_grid,
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
                _export_v(info, v5, land_vector_normalize(n5))
                _export_v(info, v1, land_vector_normalize(n1))
                _export_v(info, v2, land_vector_normalize(n2))
                _export_v_dupl(-3)
                _export_v_dupl(-2)
                _export_v(info, v4, land_vector_normalize(n4))
                _export_v_dupl(-3)
                _export_v_dupl(-2)
                _export_v(info, v3, land_vector_normalize(n3))
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
    int dpi = land_display_dpi()
    int pixels = 12 * dpi / 72
    int w, h
    land_display_desktop_size(&w, &h)
    int dialog_size = 250 * dpi / 72

    land_find_data_prefix("data/")
    font = land_font_load("DejaVuSans.ttf", pixels)
    LandWidgetTheme* theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)

    global_dialog = dialog_new(dialog_size, h, True)
    global_presets = presets_new()
    presets_update(global_presets, global_dialog)

    light = land_vector_normalize(land_vector(1, 1, -1))

    land_set_prefix(None)

    main_heightmap()

    land_alloc(camera)
    main_reset_camera()

def main_reset_camera:
    camera_init(camera)

def cb_inv(float x) -> float: return -x
def cb_sqr(float x) -> float: return ((1 + x) / 2) * ((1 + x) / 2) * 2 - 1
def cb_sqr_inv(float x) -> float: return ((1 + x) / 2) * ((1 + x) / 2) * -2 + 1
def cb_sqrt(float x) -> float: return sqrt((1 + x) / 2) * 2 - 1
def cb_sqrt_inv(float x) -> float: return sqrt((1 + x) / 2) * -2 + 1

def _blur_fftw(LandNoise *self, LandFloat *noise, int w, h, LandFloat blur_size,
        LandFloat compensate, bool wrap):

    # 1. create filter and fourier transform to filtero
    double sigma = blur_size
    if sigma < 0.5: sigma = 0.5
    double sigma2 = sigma * sigma
    double f = 1.0 / (2 * LAND_PI * sigma2)
    int fw = w
    int fh = h
    fftw_complex *filteri = fftw_malloc(sizeof *filteri * fw * fh)
    fftw_complex *filtero = fftw_malloc(sizeof *filtero * fw * fh)
    for int y in range(fh):
        for int x in range(fw):
            int y2 = ((y + fh / 2) % (fh)) - fh / 2
            int x2 = ((x + fw / 2) % (fw)) - fw / 2
            filteri[y * fw + x] = f * exp((x2 * x2 + y2 * y2) / sigma2 / -2)
    fftw_plan p = fftw_plan_dft_2d(fh, fw, filteri, filtero, FFTW_FORWARD, FFTW_ESTIMATE)
    fftw_execute(p)
    fftw_destroy_plan(p)

    # 2. create input i and fourier transform to o
    fftw_complex *i = fftw_malloc(sizeof *i * w * h)
    fftw_complex *o = fftw_malloc(sizeof *o * w * h)
    for int y in range(h):
        for int x in range(w):
            i[y * w + x] = noise[y * w + x]
    fftw_plan p2 = fftw_plan_dft_2d(h, w, i, o, FFTW_FORWARD, FFTW_ESTIMATE)
    fftw_execute(p2)
    fftw_destroy_plan(p2)

    # 3. multiply both in fourier space
    for int y in range(h):
        for int x in range(w):
            o[y * w + x] *= filtero[y * fw + x]

    # 4. back transform from fourier space
    fftw_plan p3 = fftw_plan_dft_2d(h, w, o, i, FFTW_BACKWARD, FFTW_ESTIMATE)
    fftw_execute(p3)
    fftw_destroy_plan(p3)

    double scale = compensate / (w * h)
    for int y in range(h):
        for int x in range(w):
            noise[y * w + x] = i[y * w + x] * scale

    fftw_free(filteri)
    fftw_free(filtero)
    fftw_free(i)
    fftw_free(o)

def callback_pyramid(LandNoise *noise, int x, int y, void *user) -> float:
    float vx = (double)x / noise.w * noise.count
    vx = vx - floor(vx)
    if vx < 0.5: vx = -1 + vx * 4
    else: vx = 1 - (vx - 0.5) * 4

    float vy = (double)y / noise.h * noise.count
    vy = vy - floor(vy)
    if vy < 0.5: vy = -1 + vy * 4
    else: vy = 1 - (vy - 0.5) * 4
    return min(vx, vy)

def callback_dome(LandNoise *noise, int x, int y, void *user) -> float:
    double vx = (double)x / noise.w * noise.count
    double vy = (double)y / noise.h * noise.count
    vx = vx - floor(vx)
    vy = vy - floor(vy)

    vx = -1 + vx * 2
    vy = -1 + vy * 2

    double vz = 1 - vx * vx - vy * vy
    if vz < 0:
        vz = 0
    vz = -1 + sqrt(vz) * 2

    return vz

def cb_noise_compound(LandNoise *noise, int x, int y, void *user) -> float:
    CallbackInfo *info = user
    int i = land_voronoi_owner(land_array_get_nth(info.noise.noise, 0), x, y)
    i = i % info.n
    CallbackInfo *component = info.components + i
    return land_noise_at(component.noise, x, y)

def main_generate_noise_info(Dialog *dialog, bool use_seed) -> CallbackInfo:

    int w = 1 << dialog.width->v
    int h = 1 << dialog.height->v

    LandNoiseType x[] = {LandNoiseVoronoi, LandNoisePerlin,
        LandNoisePlasma, LandNoiseWhite, LandNoiseWaves,
        LandNoiseValue, LandNoiseValue, LandNoiseVoronoi}
    LandNoiseType t = x[dialog.noise->v]

    LandPerlinLerp lerp = dialog.lerp->v

    LandNoise *noise = land_noise_new(t, 0)
    if use_seed:
        if rgen: land_random_del(rgen)
        rgen = land_random_new(dialog.seed->v)
        noise.external_blur = _blur_fftw
    land_noise_set_random(noise, rgen)
    land_noise_set_size(noise, w, h)
    land_noise_set_wrap(noise, dialog.wrap->v)
    land_noise_set_count(noise, dialog.count->v)
    land_noise_set_levels(noise, dialog.levels->v)
    land_noise_set_first_level(noise, dialog.first_level->v)
    land_noise_set_lerp(noise, lerp)
    land_noise_set_randomness(noise, dialog.randomness->v)
    land_noise_set_amplitude(noise, dialog.amplitude->v / 8.0)
    land_noise_set_power_modifier(noise, dialog.power_modifier->v / 8.0)
    land_noise_set_distance(noise, dialog.distance->v)
    if dialog.noise->v == 5:
        land_noise_value_callback(noise, callback_pyramid, None)
    if dialog.noise->v == 6:
        land_noise_value_callback(noise, callback_dome, None)
    noise.modulo = dialog.modulo->v

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
        land_noise_set_size(n2, w, h)
        noise = n2

    if dialog.blur->v:
        int s = dialog.blur_size->v
        LandNoise *n2 = land_noise_new(t, 0)
        n2.external_blur = _blur_fftw
        land_noise_set_random(n2, rgen)
        land_noise_set_wrap(n2, dialog.wrap->v)
        land_noise_set_blur(n2, noise, s)
        land_noise_set_size(n2, w, h)
        noise = n2

    land_noise_z_transform(noise, pow(2, dialog.z_scale->v / 8.0),
        dialog.z_offset->v / 16.0)
    land_noise_z_ease(noise, dialog.z_ease->v / 16.0)

    land_noise_prepare(noise)

    if dialog.transfer->v == 1: land_noise_transfer_callback(noise, cb_inv)
    if dialog.transfer->v == 2: land_noise_transfer_callback(noise, cb_sqr)
    if dialog.transfer->v == 3: land_noise_transfer_callback(noise, cb_sqr_inv)
    if dialog.transfer->v == 4: land_noise_transfer_callback(noise, cb_sqrt)
    if dialog.transfer->v == 5: land_noise_transfer_callback(noise, cb_sqrt_inv)

    if dialog.plateau->v:
        land_noise_set_minmax(noise, -1 + dialog.plateau->v / 32.0, 1000)

    CallbackInfo info
    info.water_start_z = dialog.pos0->v / 31.0 * 2 - 1
    info.water_end_z = dialog.pos1->v / 31.0 * 2 - 1
    info.grass_start_z = dialog.pos2->v / 31.0 * 2 - 1
    info.grass_end_z = dialog.pos3->v / 31.0 * 2 - 1
    info.mountain_start_z = dialog.pos4->v / 31.0 * 2 - 1
    info.mountain_end_z = dialog.pos5->v / 31.0 * 2 - 1
    info.snow_start_z = dialog.pos6->v / 31.0 * 2 - 1

    info.water_c = land_color_int(dialog.color1->v)
    info.shore_c = land_color_int(dialog.color2->v)
    info.grass_c = land_color_int(dialog.color3->v)
    info.hills_c = land_color_int(dialog.color4->v)
    info.mountain_c = land_color_int(dialog.color5->v)
    info.snow_c = land_color_int(dialog.color6->v)

    LandNoise* rn = None
    if dialog.river->v:
        rn = rivers(noise, info.water_end_z, info.mountain_end_z)

    info.noise = noise
    info.river = rn

    return info

def main_generate(bool want_color, bool want_triangles, bool debug, bool export):
    LandTimings *t = land_timing_new()
    int w = 0
    int h = 0
    if image:
        w = land_image_width(image)
        h = land_image_height(image)
    
    if not global_dialog.noise: return

    LandArray* compounds = noise_dialog_get_compound_components(global_dialog)
    int n = land_array_count(compounds)
    if global_dialog.noise->v == 7: # compound
        global_dialog.modulo->v = n
    else:
        global_dialog.modulo->v = 0

    CallbackInfo info = main_generate_noise_info(global_dialog, True)

    land_timing_add(t, "main noise")
    int sw = info.noise->w
    int sh = info.noise->h
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

    if global_dialog.noise->v == 7: # compound
        
        CallbackInfo component_info[n]
        info.components = component_info
        info.n = n
        info.want_color = want_color

        # load each of the presets, create a full map with each
        int ci = 0
        for str name in compounds:
            Dialog *component = dialog_new(100, 100, False)
            preset_fill_in(global_presets, component, name)
            dialog_load(component)
            component.width->v = global_dialog.width->v
            component.height->v = global_dialog.height->v
            component_info[ci] = main_generate_noise_info(component, False)
            dialog_destroy(component)
            ci++
            land_timing_add(t, name)

        # stich the height data together to a new noise
        LandNoise *a = land_noise_new(LandNoiseValue, 0)
        land_noise_set_size(a, w, h)
        land_noise_value_callback(a, cb_noise_compound, &info)
        land_noise_prepare(a)

        land_timing_add(t, "stitch")

        # blur the height data
        LandNoise *b = land_noise_new(LandNoiseValue, 0)
        b.external_blur = _blur_fftw
        land_noise_set_blur(b, a, info.noise->distance / 2)
        land_noise_set_size(b, w, h)
        land_noise_prepare(b)

        land_timing_add(t, "blur")

        info.stitched = b

        if info.noise->distance > 0:
            LandVoronoi *vor = land_array_get(info.noise->noise, 0)
            for int y in range(h):
                for int x in range(w):
                    float h = land_noise_at(a, x, y)
                    float hblur = land_noise_at(b, x, y)
                    float vd = land_noise_at(info.noise, x, y)
                    int oa = land_voronoi_owner(vor, x, y)
                    int ob = land_voronoi_neighbor(vor, x, y)
                    if oa % n != ob % n:
                        float p = (vd + 1) / 2
                        info.stitched->cache[y * w + x] = h * p + hblur * (1 - p)
                    else:
                        info.stitched->cache[y * w + x] = h

            land_timing_add(t, "boundary")

        # use same height map also for presets
        #LandVoronoi *vor = land_array_get(info.noise->noise, 0)
        for int i in range(n):
            component_info[i].noise->cache = info.stitched->cache
            # these are already baked into the heightmap now
            component_info[i].noise->z_scale = 1
            component_info[i].noise->z_offset = 0
            component_info[i].noise->z_ease = 0

        land_image_write_callback(image, cb_compound, &info)

        land_timing_add(t, "image")

        # blur colors
        if info.noise->distance > 0:
            LandImage* blurred_image = land_image_clone(image)
            # heightmap blur is distance/2, for color half of that looks good
            land_image_blur(blurred_image, info.noise->distance / 4)
            land_timing_add(t, "color blur")
            LandVoronoi *vor = land_array_get(info.noise->noise, 0)
            uint8_t *rgba = land_malloc(w * h * 4)
            uint8_t *rgba2 = land_malloc(w * h * 4)
            land_image_get_rgba_data(image, rgba)
            land_image_get_rgba_data(blurred_image, rgba2)

            for int y in range(h):
                for int x in range(w):
                    float vd = land_noise_at(info.noise, x, y)
                    int oa = land_voronoi_owner(vor, x, y)
                    int ob = land_voronoi_neighbor(vor, x, y)
                    if ob >= 0 and oa % n != ob % n:
                        float p = (vd + 1) / 2
                        for int c in range(3):
                            float orig_c = rgba[y * w * 4 + x * 4 + c]
                            float blur_c = rgba2[y * w * 4 + x * 4 + c]
                            rgba[y * w * 4 + x * 4 + c] = orig_c * p + blur_c * (1 - p)
                   
            land_image_set_rgba_data(image, rgba)
            land_free(rgba)
            land_free(rgba2)
            land_image_destroy(blurred_image)

            land_timing_add(t, "color blur boundary")
        
        if want_triangles:
            make_triangles(info.stitched, &info, w, h, debug, export)

            land_timing_add(t, "triangles")
    else:
        land_image_write_callback(image, want_color ? cb_color : cb_gray,
            &info)

        if want_triangles:
            make_triangles(info.noise, &info, w, h, debug, export)

    if info.noise: land_noise_destroy(info.noise)  
    if info.river: land_noise_destroy(info.river)

    land_timing_print(t)
    global_dialog.dt = land_timing_total(t)
    land_timing_destroy(t)

def recreate:
    if game.last_type == 0: main_heightmap()
    if game.last_type == 1: main_color()
    if game.last_type == 2: main_triangles(False)

def main_seed:
    global_dialog.seed->v = land_rand(0, 0xfffffff)
    recreate()

def main_color:
    main_generate(True, False, False, False)
    game.last_type = 1
    
def main_heightmap:
    main_generate(False, False, False, False)
    game.last_type = 0

def main_triangles(bool debug):
    main_generate(True, True, debug, False)
    game.last_type = 2

def _add_split(LandHash *sets, str key, int size, char *v):
    LandBuffer *b = land_hash_get(sets, key)
    if not b:
        printf("split for %s\n", key)
        b = land_buffer_new()
        land_hash_insert(sets, key, b)
    land_buffer_add(b, v, size)

def main_export_mesh(int (*split_cb)(float x, float y, float z), bool debug):
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

def main_export_map:

    main_generate_noise_info(global_dialog, True)

    land_image_save(image, "perlin.png")

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
    auto dialog = global_dialog

    if color_picker:
        land_widget_tick(color_picker)
    elif dialog:
        dialog_hide_show(dialog)
        land_widget_tick(dialog.view)

    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

    bool text_input = had_text_input
    bool mouse_in_ui = False
    had_text_input = False
    if dialog:
        if land_widget_container_get_keyboard_focus(dialog.view):
            had_text_input = text_input = True
        if land_mouse_x() >= land_display_width() - dialog.size:
            mouse_in_ui = True

    if not text_input:
        float dx = 0
        float dy = 0

        if land_key_pressed(' ') or land_key_pressed(LandKeyEnter):
            main_heightmap()

        if land_key_pressed('s'):
            main_seed()

        if land_key_pressed('c'):
            main_color()

        if land_key_pressed('t'):
            main_triangles(False)

        if land_key_pressed('d'):
            main_triangles(True)

        if land_key_pressed('r'):
            main_reset()

        if land_key_pressed('l'):
            if dialog: dialog_load(dialog)
            recreate()

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

    if not mouse_in_ui:
        float dx, dy
        float dz = land_mouse_delta_z()
        camera.zoom += dz * 0.1

        if land_mouse_button(1):
            dx = land_mouse_delta_x() * 0.01
            dy = land_mouse_delta_y() * 0.01
            camera_change_locked(camera, -dy, -dx)

        if land_mouse_button(0):
            dx = land_mouse_delta_x() * 1.0 * pow(2, -camera.zoom)
            dy = land_mouse_delta_y() * 1.0 * pow(2, -camera.zoom)
            camera_move(camera, -dx, -dy, 0)

def main_reset:
    Dialog *dialog = global_dialog
    
    main_reset_camera()
    for Value *value in LandArray* dialog.values:
        if value.is_string:
            value_set_string(value, value.initial_string)
        else:
            value_set(value, value.initial)

def draw(LandRunner *self):
    auto dialog = global_dialog
    int dw = land_display_width()
    int dh = land_display_height()

    if land_was_resized() and dialog:
        land_widget_move_to(dialog.view, land_display_width() - dialog.size, 0)

    land_unclip()
    land_clear(0, 0, 0, 1)
    land_clear_depth(1)

    if image:
        draw_image()

    land_render_state(LAND_DEPTH_TEST, False)
    land_projection(land_4x4_matrix_orthographic(0, dh, 1, dw, 0, -1))
    if color_picker:
        land_widget_draw(color_picker)
    elif dialog:
        land_widget_draw(dialog.view)

        land_text_pos(0, 0)
        land_color(1, 0, 0, 1)
        land_print("%.2f", dialog.dt)

def draw_image:
    auto dialog = global_dialog

    int w = land_image_width(image)
    int h = land_image_height(image)
    int dw = land_display_width()
    int dh = land_display_height()
    int vw = dw - dialog.size
    int vh = dh
    float size = min(vw, vh)
    int ps = max(w, h)

    if triangles:
        land_render_state(LAND_DEPTH_TEST, True)
        Land4x4Matrix m = land_4x4_matrix_identity()

        m = land_4x4_matrix_mul(land_4x4_matrix_translate(-w / 2, -h / 2, 0), m)

        float s = size / 4.0 / ps
        m = land_4x4_matrix_mul(land_4x4_matrix_scale(s, s, s), m)

        m = land_4x4_matrix_mul(camera_matrix(camera), m)

        m = land_4x4_matrix_mul(land_4x4_matrix_translate(vw / 2 - dw / 2, 0, 0), m)

        m = land_4x4_matrix_mul(land_4x4_matrix_orthographic(
            -dw / 2, dh / 2, 1000, dw / 2, -dh / 2, -1000), m)
        
        land_projection(m)
        land_triangles_draw(triangles)
        if triangles_debug: land_triangles_draw(triangles_debug)
    else:
        land_image_draw_scaled(image, (vw - w * size / ps) / 2, (vh - h * size / ps) / 2, size / ps, size / ps)

def begin():
    land_debug(1)
    land_init()

    int dpi = land_display_dpi()
    if dpi == 0: dpi = 72
    int w, h
    land_display_desktop_size(&w, &h)
    int s = h * 0.75
    int dialog_size = 250 * dpi / 72

    land_set_display_parameters(s + dialog_size, s, LAND_OPENGL | LAND_WINDOWED | LAND_RESIZE | LAND_DEPTH)
    LandRunner* runner = land_runner_new("game", init, None, tick, draw, None, None)
    land_runner_register(runner)
    land_set_initial_runner(runner)
    land_mainloop()

land_use_main(begin)
