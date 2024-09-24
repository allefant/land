class LandColor:
   float r, g, b, a

import global stdint
static import land.external.google_material_design
static import land/allegro5/a5_misc
static import global ctype
static import global string
static import land.util
static import land.array
static import land.buffer
static import land.mem
static import land.hash
static import global math

static LandHash *cache

static double const Xn = 0.95047
static double const Yn = 1.00000
static double const Zn = 1.08883
static double const delta = 6.0 / 29
static double const delta2 = 6.0 / 29 * 6.0 / 29
static double const delta3 = 6.0 / 29 * 6.0 / 29 * 6.0 / 29
static double const tf7 = 1.0 / 4 / 4 / 4 / 4 / 4 / 4 / 4

def land_color_alpha(float a) -> LandColor:
    LandColor c = {0, 0, 0, a}
    return c

def land_color_hsv(float hue, sat, val) -> LandColor:
    return platform_color_hsv(hue, sat, val)

def land_color_rgba(float r, g, b, a) -> LandColor:
    LandColor c = {r, g, b, a}
    return c

def land_rgba(float r, g, b, a) -> LandColor:
    LandColor c = {r, g, b, a}
    return c

def land_rgb(float r, g, b) -> LandColor:
    LandColor c = {r, g, b, 1}
    return c

def land_color_bytes(uint8_t *b) -> LandColor:
    return land_color_rgba(b[0] / 255.0, b[1] / 255.0, b[2] / 255.0, b[3] / 255.0)

def srgba_gamma_to_linear(double x) -> double:
    double const a = 0.055
    if x < 0.04045: return x / 12.92
    return pow((x + a) / (1 + a), 2.4)

def srgba_linear_to_gamma(double x) -> double:
    double const a = 0.055
    if x < 0.0031308: return x * 12.92
    return pow(x, 1 / 2.4) * (1 + a) - a

def land_color_xyz(double x, y, z) -> LandColor:
    LandColor c
    double r =  3.2406 * x + -1.5372 * y + -0.4986 * z
    double g = -0.9689 * x +  1.8758 * y +  0.0415 * z
    double b =  0.0557 * x + -0.2040 * y +  1.0570 * z
    c.r = srgba_linear_to_gamma(r)
    c.g = srgba_linear_to_gamma(g)
    c.b = srgba_linear_to_gamma(b)
    c.a = 1
    return c

def land_color_to_xyz(LandColor c, double *x, *y, *z):
    double r = srgba_gamma_to_linear(c.r)
    double g = srgba_gamma_to_linear(c.g)
    double b = srgba_gamma_to_linear(c.b)
    *x = r * 0.4124 + g * 0.3576 + b * 0.1805
    *y = r * 0.2126 + g * 0.7152 + b * 0.0722
    *z = r * 0.0193 + g * 0.1192 + b * 0.9505

def land_color_oklab(double l, a, b) -> LandColor:
    LandColor c

    float l_ = l + 0.3963377774f * a + 0.2158037573f * b
    float m_ = l - 0.1055613458f * a - 0.0638541728f * b
    float s_ = l - 0.0894841775f * a - 1.2914855480f * b

    float l3 = l_*l_*l_
    float m3 = m_*m_*m_
    float s3 = s_*s_*s_

    float r3 = +4.0767416621f * l3 - 3.3077115913f * m3 + 0.2309699292f * s3
    float g3 = -1.2684380046f * l3 + 2.6097574011f * m3 - 0.3413193965f * s3
    float b3 = -0.0041960863f * l3 - 0.7034186147f * m3 + 1.7076147010f * s3

    c.r = srgba_linear_to_gamma(r3)
    c.g = srgba_linear_to_gamma(g3)
    c.b = srgba_linear_to_gamma(b3)
    c.a = 1
    return c

def land_color_to_oklab(LandColor c, double *l, *a, *b):
    double lr = srgba_gamma_to_linear(c.r)
    double lg = srgba_gamma_to_linear(c.g)
    double lb = srgba_gamma_to_linear(c.b)

    float ol = 0.4122214708f * lr + 0.5363325363f * lg + 0.0514459929f * lb
    float om = 0.2119034982f * lr + 0.6806995451f * lg + 0.1073969566f * lb
    float os = 0.0883024619f * lr + 0.2817188376f * lg + 0.6299787005f * lb

    float l_ = cbrtf(ol)
    float m_ = cbrtf(om)
    float s_ = cbrtf(os)
    
    *l = 0.2104542553f*l_ + 0.7936177850f*m_ - 0.0040720468f*s_
    *a = 1.9779984951f*l_ - 2.4285922050f*m_ + 0.4505937099f*s_
    *b = 0.0259040371f*l_ + 0.7827717662f*m_ - 0.8086757660f*s_

static def cielab_f(double x) -> double:
    if x > delta3:
        return pow(x, 1.0 / 3)
    return 4.0 / 29 + x / delta2 / 3

static def cielab_f_inv(double x) -> double:
    if x > delta:
        return pow(x, 3)
    return (x - 4.0 / 29) * 3 * delta2

def land_color_to_cielab(LandColor c, double *L, *a, *b):
    double x, y, z
    land_color_to_xyz(c, &x, &y, &z)
    x /= Xn
    y /= Yn
    z /= Zn
    *L = 1.16 * cielab_f(y) - 0.16
    *a = 5.00 * (cielab_f(x) - cielab_f(y))
    *b = 2.00 * (cielab_f(y) - cielab_f(z))

def land_color_cielab(double L, a, b) -> LandColor:
    double x = Xn * cielab_f_inv((L + 0.16) / 1.16 + a / 5.00)
    double y = Yn * cielab_f_inv((L + 0.16) / 1.16)
    double z = Zn * cielab_f_inv((L + 0.16) / 1.16 - b / 2.00)
    return land_color_xyz(x, y, z)

def land_color_to_lch(LandColor col, double *l, *c, *h):
    double a, b
    land_color_to_cielab(col, l, &a, &b)

    *h = atan2(b, a)
    if *h < 0: *h += 2 * pi

    *c = sqrt(a * a + b * b)

def land_color_lch(double l, c, h) -> LandColor:
    double a = c * cos(h)
    double b = c * sin(h)
    return land_color_cielab(l, a, b)

def land_color_to_oklch(LandColor col, double *l, *c, *h):
    double a, b
    land_color_to_oklab(col, l, &a, &b)
    *c = sqrt(a * a + b * b) / 0.25 # why the 0.25?
    *h = atan2(b, a)
    if *h < 0: *h += 2 * pi

def land_color_oklch(double l, c, h) -> LandColor:
    c *= 0.25
    double a = c * cos(h)
    double b = c * sin(h)
    return land_color_oklab(l, a, b)

def land_color_xyy(double x, y, Y) -> LandColor:
    # x = X / (X + Y + Z)
    # y = Y / (X + Y + Z)
    #
    # xX + xY + xZ = X
    # yX + yY + yZ = Y
    # 
    # X + Z = X/x - Y
    # X + Z = Y/y - Y
    #
    # X/x = Y/y
    # X = x * Y/y
    # Z = Y/y - Y - X

    double X = x * Y / y
    double Z = (1 - y - x) * Y / y

    return land_color_xyz(X, Y, Z)

def land_color_to_xyy(LandColor c, double *x, *y, *Y):
    double X, Z
    land_color_to_xyz(c, &X, Y, &Z)
    *x = X / (X + *Y + Z)
    *y = *Y / (X + *Y + Z)

def land_color_distance_cie94(LandColor color, other) -> double:
    double l1, a1, b1
    double l2, a2, b2
    land_color_to_cielab(color, &l1, &a1, &b1)
    land_color_to_cielab(other, &l2, &a2, &b2)
    return land_color_distance_cie94_lab(l1, a1, b1, l2, a2, b2)
    
def land_color_distance_cie94_lab(double l1, a1, b1, l2, a2, b2) -> double:
    double dl = l1 - l2
    double da = a1 - a2
    double db = b1 - b2
    double c1 = sqrt(a1 * a1 + b1 * b1)
    double c2 = sqrt(a2 * a2 + b2 * b2)
    double dc = c1 - c2
    double dh = da * da + db * db - dc * dc
    dh = dh < 0 ? 0 : sqrt(dh)
    dc /= 1 + 0.045 * c1
    dh /= 1 + 0.015 * c1
    return sqrt(dl * dl + dc * dc + dh * dh)

def land_color_distance_ciede2000(LandColor color, other) -> double:
    double l1, a1, b1
    double l2, a2, b2
    land_color_to_cielab(color, &l1, &a1, &b1)
    land_color_to_cielab(other, &l2, &a2, &b2)
    return land_color_distance_ciede2000_lab(l1, a1, b1, l2, a2, b2)

def land_color_distance_ciede2000_lab(double l1, a1, b1, l2, a2, b2) -> double:
    """
    http://www.ece.rochester.edu/~gsharma/ciede2000/ciede2000noteCRNA.pdf
    """
    double dl = l1 - l2
    double ml = (l1 + l2) / 2
    double c1 = sqrt(a1 * a1 + b1 * b1)
    double c2 = sqrt(a2 * a2 + b2 * b2)
    double mc = (c1 + c2) / 2
    double fac = sqrt(pow(mc, 7) / (pow(mc, 7) + tf7))
    double g = 0.5 * (1 - fac)
    a1 *= 1 + g
    a2 *= 1 + g
    c1 = sqrt(a1 * a1 + b1 * b1)
    c2 = sqrt(a2 * a2 + b2 * b2)
    double dc = c2 - c1
    mc = (c1 + c2) / 2
    fac = sqrt(pow(mc, 7) / (pow(mc, 7) + tf7))
    double h1 = fmod(2 * pi + atan2(b1, a1), 2 * pi)
    double h2 = fmod(2 * pi + atan2(b2, a2), 2 * pi)
    double dh = 0
    double mh = h1 + h2
    if c1 * c2 != 0:
        dh = h2 - h1
        if dh > pi: dh -= 2 * pi
        if dh < -pi: dh += 2 * pi
        if fabs(h1 - h2) <= pi: mh = (h1 + h2) / 2
        elif h1 + h2 < 2 * pi: mh = (h1 + h2 + 2 * pi) / 2
        else: mh = (h1 + h2 - 2 * pi) / 2
    dh = 2 * sqrt(c1 * c2) * sin(dh / 2)

    double t = 1 - 0.17 * cos(mh - pi / 6) + 0.24 * cos(2 * mh) +\
            0.32 * cos(3 * mh + pi / 30) - 0.2 * cos(4 * mh - pi * 7 / 20)
    double mls = pow(ml - 0.5, 2)
    double sl = 1 + 1.5 * mls / sqrt(0.002 + mls)
    double sc = 1 + 4.5 * mc
    double sh = 1 + 1.5 * mc * t
    double rt = -2 * fac * sin(pi / 3 * exp(-pow(mh / pi * 36 / 5 - 11, 2)))
    return sqrt(pow(dl / sl, 2) + pow(dc / sc, 2) + pow(dh / sh, 2) +
            rt * dc / sc * dh / sh)

static class TestData:
    double l1, a1, b1, l2, a2, b2, e

static TestData test_data[] = {
    {50.0000, 2.6772, -79.7751, 50.0000, 0.0000, -82.7485, 2.0425},
    {50.0000, 3.1571, -77.2803, 50.0000, 0.0000, -82.7485, 2.8615},
    {50.0000, 2.8361, -74.0200, 50.0000, 0.0000, -82.7485, 3.4412},
    {50.0000, -1.3802, -84.2814, 50.0000, 0.0000, -82.7485, 1.0000},
    {50.0000, -1.1848, -84.8006, 50.0000, 0.0000, -82.7485, 1.0000},
    {50.0000, -0.9009, -85.5211, 50.0000, 0.0000, -82.7485, 1.0000},
    {50.0000, 0.0000, 0.0000, 50.0000, -1.0000, 2.0000, 2.3669},
    {50.0000, -1.0000, 2.0000, 50.0000, 0.0000, 0.0000, 2.3669},
    {50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0009, 7.1792},
    {50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0010, 7.1792},
    {50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0011, 7.2195},
    {50.0000, 2.4900, -0.0010, 50.0000, -2.4900, 0.0012, 7.2195},
    {50.0000, -0.0010, 2.4900, 50.0000, 0.0009, -2.4900, 4.8045},
    {50.0000, -0.0010, 2.4900, 50.0000, 0.0010, -2.4900, 4.8045},
    {50.0000, -0.0010, 2.4900, 50.0000, 0.0011, -2.4900, 4.7461},
    {50.0000, 2.5000, 0.0000, 50.0000, 0.0000, -2.5000, 4.3065},
    {50.0000, 2.5000, 0.0000, 73.0000, 25.0000, -18.0000, 27.1492},
    {50.0000, 2.5000, 0.0000, 61.0000, -5.0000, 29.0000, 22.8977},
    {50.0000, 2.5000, 0.0000, 56.0000, -27.0000, -3.0000, 31.9030},
    {50.0000, 2.5000, 0.0000, 58.0000, 24.0000, 15.0000, 19.4535},
    {50.0000, 2.5000, 0.0000, 50.0000, 3.1736, 0.5854, 1.0000},
    {50.0000, 2.5000, 0.0000, 50.0000, 3.2972, 0.0000, 1.0000},
    {50.0000, 2.5000, 0.0000, 50.0000, 1.8634, 0.5757, 1.0000},
    {50.0000, 2.5000, 0.0000, 50.0000, 3.2592, 0.3350, 1.0000},
    {60.2574, -34.0099, 36.2677, 60.4626, -34.1751, 39.4387, 1.2644},
    {63.0109, -31.0961, -5.8663, 62.8187, -29.7946, -4.0864, 1.2630},
    {61.2901, 3.7196, -5.3901, 61.4292, 2.2480, -4.9620, 1.8731},
    {35.0831, -44.1164, 3.7933, 35.0232, -40.0716, 1.5901, 1.8645},
    {22.7233, 20.0904, -46.6940, 23.0331, 14.9730, -42.5619, 2.0373},
    {36.4612, 47.8580, 18.3852, 36.2715, 50.5065, 21.2231, 1.4146},
    {90.8027, -2.0831, 1.4410, 91.1528, -1.6435, 0.0447, 1.4441},
    {90.9257, -0.5406, -0.9208, 88.6381, -0.8985, -0.7239, 1.5381},
    {6.7747, -0.2908, -2.4247, 5.8714, -0.0985, -2.2286, 0.6377},
    {2.0776, 0.0795, -1.1350, 0.9033, -0.0636, -0.5514, 0.9082}
}

def test_ciede2000:
    for int i in range(34):
        TestData data = test_data[i]
        double e = land_color_distance_ciede2000_lab(data.l1 / 100, data.a1 / 100,
            data.b1 / 100, data.l2 / 100, data.a2 / 100, data.b2 / 100)
        double e94 = land_color_distance_cie94_lab(data.l1 / 100, data.a1 / 100,
            data.b1 / 100, data.l2 / 100, data.a2 / 100, data.b2 / 100)
        double d = e * 100 - data.e
        bool ok = d * d < 0.0001 * 0.0001
        printf("%s%d: %.4f == %.4f (%.4f)%s\n",
            land_color_bash(ok ? "green" : "red"),
            1 + i, e * 100, data.e, e94 * 100,
            land_color_bash("end"))

def land_color_premul(float r, g, b, a) -> LandColor:
    LandColor c = {r * a, g * a, b * a, a}
    return c

def land_color_alphamul(LandColor c, float a) -> LandColor:
    LandColor c2 = {c.r * a, c.g * a, c.b * a, c.a * a}
    return c2

static int hexval(char c):
    c = tolower(c)
    if c >= '0' and c <= '9': return (c - '0')
    if c >= 'a' and c <= 'f': return 10 + (c - 'a')
    return 0

def land_color_name(char const *name) -> LandColor:
    if not name:
        return land_color_rgba(0, 0, 0, 0)
    if name[0] == '#':
        LandColor c
        c.r = (hexval(name[1]) * 16 + hexval(name[2])) / 255.0
        c.g = (hexval(name[3]) * 16 + hexval(name[4])) / 255.0
        c.b = (hexval(name[5]) * 16 + hexval(name[6])) / 255.0
        c.a = 1
        return c

    # check for something like:
    # red/2 red*3/4 red*9/2/5
    int i1 = land_find(name, "*")
    int i2 = land_find(name, "/")
    if i1 >= 0 or i2 >= 0:
        int i = i1
        if i < 0 or i2 < i: i = i2
        char *name2 = land_substring(name, 0, i)
        LandColor c = platform_color_name(name2)
        char prev = 0
        while True:
            if name[i] == 0: break
            if name[i] >= '1' and name[i] <= '9':
                float d = name[i] - '0'
                if prev == '*':
                    c.r *= d
                    c.g *= d
                    c.b *= d
                elif prev == '/':
                    c.r /= d
                    c.g /= d
                    c.b /= d
            prev = name[i]
            i++
        return c

    return platform_color_name(name)

def land_color_mix(LandColor c, LandColor mix, float p) -> LandColor:
    float q = 1 - p
    c.r = c.r * q + mix.r * p
    c.g = c.g * q + mix.g * p
    c.b = c.b * q + mix.b * p
    c.a = c.a * q + mix.a * p
    return c

def land_color_mix_current(LandColor mix, float p):
    LandColor c = land_color_get()
    land_color_set(land_color_mix(c, mix, p))

def land_color_to_html(LandColor c, char html[8]):
    int r = land_constraini(c.r * 255, 0, 255)
    int g = land_constraini(c.g * 255, 0, 255)
    int b = land_constraini(c.b * 255, 0, 255)
    sprintf(html, "#%02x%02x%02x", r, g, b)

def land_color_int(int i) -> LandColor:
    int r = i & 255
    int g = (i >> 8) & 255
    int b = (i >> 16) & 255
    int a = (i >> 24) & 255
    return land_color_rgba(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

def land_color_to_int(LandColor c) -> uint32_t:
    int r = c.r * 255
    int g = c.g * 255
    int b = c.b * 255
    int a = c.a * 255
    return r + (g << 8) + (b << 16) + (a << 24)

def land_color_lerp(LandColor a, b, float t) -> LandColor:
    return land_color_rgba(
        a.r + t * (b.r - a.r),
        a.g + t * (b.g - a.g),
        a.b + t * (b.b - a.b),
        a.a + t * (b.a - a.a))

def land_color_bash(char const *x) -> char const *:
    """
    bash("bright red")
    bash("back white")
    bash("bold blue back bright green")
    bash("end")

    Note: The return value remains property of the color module and is
    not to be freed.
    """
    return bash_mode(x, "3")

static macro CAT(X, Y1, Y2):
    if land_equals(c, X):
        land_concatenate_with_separator(&m, Y1, ";")
        land_concatenate(&m, Y2)

static def bash_mode(char const *x, char const *mode) -> char const *:

    if cache == None:
        cache = land_hash_new()

    char *cached = land_hash_get(cache, x)
    if cached:
        return cached
    
    char const *back = strstr(x, "back")
    if back:
        if back == x:
            return bash_mode(x + 4, "4")
        char *x2 = land_substring(x, 0, back - x)
        char const *fg = bash_mode(x2, "3")
        char const *bg = bash_mode(back, "4")
        char *r = land_strdup(fg)
        land_concatenate(&r, bg)
        land_free(x2)
        land_hash_insert(cache, x, r)
        return r

    char *m = land_strdup("")
    LandArray *a = land_split(x, " ")
    for char *c in LandArray *a:
        if land_equals(c, "bright"):
            if land_equals(mode, "3"):
                mode = "9"
            else:
                mode = "10"
        CAT("bold", "", "1")
        CAT("black", mode, "0")
        CAT("red", mode, "1")
        CAT("green", mode, "2")
        CAT("yellow", mode, "3")
        CAT("blue", mode, "4")
        CAT("magenta", mode, "5")
        CAT("cyan", mode, "6")
        CAT("white", mode, "7")
    land_array_destroy_with_strings(a)

    land_prepend(&m, "\x1b[")
    land_concatenate(&m, "m")

    land_hash_insert(cache, x, m)

    return m
        
def land_premul_alpha(LandColor c, float a) -> LandColor:
    return land_color_premul(c.r, c.g, c.b, a)

def land_color_copy_to_bytes(LandColor c, uint8_t *rgba):
    rgba[0] = land_constrainf(c.r, 0, 1) * 255
    rgba[1] = land_constrainf(c.g, 0, 1) * 255
    rgba[2] = land_constrainf(c.b, 0, 1) * 255
    rgba[3] = land_constrainf(c.a, 0, 1) * 255

def land_color_copy_to_floats(LandColor c, float *rgba):
    rgba[0] = c.r
    rgba[1] = c.g
    rgba[2] = c.b
    rgba[3] = c.a

def land_black -> LandColor: return land_color_rgba(0, 0, 0, 1)
def land_white -> LandColor: return land_color_rgba(1, 1, 1, 1)
def land_transparent -> LandColor: return land_color_rgba(0, 0, 0, 0)
def land_set_black: land_color_set(land_black())
def land_set_white: land_color_set(land_white())
def land_set_transparent: land_color_set(land_transparent())

str _palette_14_x_11_names[14 * 11] = {
    "maroon/2", "maroon", "saddlebrown/2", "dark goldenrod/2",
    "moccasin/2", "dark olivegreen/2", "dark green/2", "teal",
    "dark slategray/2", "deepskyblue/2", "midnightblue/2", "indigo/2",
    "purple/2", "black", "rosybrown/2", "dark red", "saddlebrown",
    "dark goldenrod", "olive", "dark green", "green", "dark cyan", "teal/2",
    "royalblue", "navy", "indigo", "medium violetred/2", "dimgray/2",
    "brown", "firebrick", "peru", "gold", "goldenrod", "dark olivegreen",
    "forestgreen", "medium seagreen", "dark slategray", "steelblue",
    "midnightblue", "dark violet", "purple", "dimgray", "crimson",
    "sienna", "dark orange", "wheat", "dark khaki", "olivedrab",
    "seagreen", "light seagreen", "cadetblue", "slategray", "medium blue",
    "thistle/2", "dark magenta", "gray", "indianred", "red", "sandybrown",
    "navajowhite", "khaki", "yellowgreen", "dark seagreen",
    "dark turquoise", "skyblue", "light slategray", "dark slateblue",
    "blueviolet", "sequoia", "dark gray", "rosybrown", "chocolate",
    "orange", "moccasin", "palegoldenrod", "chartreuse", "limegreen",
    "medium aquamarine", "light blue", "dodgerblue", "blue", "dark orchid",
    "medium violetred", "silver", "light coral", "orangered", "tan",
    "antiquewhite", "banana", "citron", "light green", "medium turquoise",
    "powderblue", "cornflowerblue", "rebeccapurple", "medium orchid",
    "deeppink", "light gray", "salmon", "tomato", "burlywood",
    "blanchedalmond", "beige", "greenyellow", "lime", "turquoise",
    "paleturquoise", "deepskyblue", "slateblue", "orchid", "magenta",
    "gainsboro", "light pink", "coral", "peachpuff", "papayawhip",
    "yellow", "light goldenrodyellow", "springgreen", "medium springgreen",
    "cyan", "light steelblue", "medium slateblue", "violet",
    "palevioletred", "whitesmoke", "pink", "dark salmon", "bisque",
    "oldlace", "cornsilk", "light yellow", "palegreen", "aquamarine",
    "light cyan", "light skyblue", "medium purple", "plum", "hotpink",
    "ghostwhite", "mistyrose", "light salmon", "seashell", "floralwhite",
    "lemonchiffon", "ivory", "honeydew", "mintcream", "azure", "aliceblue",
    "lavender", "thistle", "lavenderblush", "white"
    }
LandHash *_palettes
def _get_palette(str name) -> LandArray*:
    if not _palettes:
        _palettes = land_hash_new()
    LandArray *pal = land_hash_get(_palettes, name)
    if pal:
        return pal
    if land_equals(name, "14x11"):
        pal = land_array_new()
        for int i in range(14 * 11):
            LandColor *c; land_alloc(c)
            *c = land_color_name(_palette_14_x_11_names[i])
            land_array_add(pal, c)
        land_hash_insert(_palettes, "14x11", pal)
        return pal
    if land_equals(name, "light"):
        pal = land_array_new()
        for int i in range(14 * 11):
            LandColor col = land_palette_color("14x11", i)
            (double l, a, b) = land_color_to_oklab(col)
            if l > 0.92:
                LandColor *cp; land_alloc(cp)
                *cp = col
                land_array_add(pal, cp)
        _sort(pal)
        land_hash_insert(_palettes, "light", pal)
        return pal
    if land_equals(name, "dark"):
        pal = land_array_new()
        for int i in range(14 * 11):
            LandColor col = land_palette_color("14x11", i)
            (double l, a, b) = land_color_to_oklab(col)
            if l < 0.33:
                LandColor *cp; land_alloc(cp)
                *cp = col
                land_array_add(pal, cp)
        _sort(pal)
        land_hash_insert(_palettes, "dark", pal)
        return pal
    if land_equals(name, "greys"):
        pal = land_array_new()
        for int i in range(14 * 11):
            LandColor col = land_palette_color("14x11", i)
            (double l, c, h) = land_color_to_oklch(col)
            if c < 0.01:
                LandColor *cp; land_alloc(cp)
                *cp = col
                land_array_add(pal, cp)
        _sort(pal)
        land_hash_insert(_palettes, "greys", pal)
        return pal
    if land_equals(name, "reds"): return _make_palette_hue("reds", 0.1, 0.75)
    if land_equals(name, "browns"): return _make_palette_hue("browns", 0.75, 1.33)
    if land_equals(name, "yellows"): return _make_palette_hue("yellows", 1.33, 2.1)
    if land_equals(name, "greens"): return _make_palette_hue("greens", 2.1, 3)
    if land_equals(name, "blues"): return _make_palette_hue("blues", 3, 4.9)
    if land_equals(name, "purples"): return _make_palette_hue("purples", 4.9, 0.1)
    if land_equals(name, "colorless"):
        pal = land_array_new()
        for int i in range(14 * 11):
            LandColor col = land_palette_color("14x11", i)
            (double l, c, h) = land_color_to_oklch(col)
            if c >= 0.1: continue
            LandColor *cp; land_alloc(cp)
            *cp = col
            land_array_add(pal, cp)
        _sort(pal)
        land_hash_insert(_palettes, "colorless", pal)
        return pal
    if land_equals(name, "colorful"):
        pal = land_array_new()
        for int i in range(14 * 11):
            LandColor col = land_palette_color("14x11", i)
            (double l, c, h) = land_color_to_oklch(col)
            if c < 0.7: continue
            if l < 0.5: continue
            LandColor *cp; land_alloc(cp)
            *cp = col
            land_array_add(pal, cp)
        _sort(pal)
        land_hash_insert(_palettes, "colorful", pal)
        return pal
    if land_equals(name, "material-red"): return _material(name)
    if land_equals(name, "material-pink"): return _material(name)
    if land_equals(name, "material-purple"): return _material(name)
    if land_equals(name, "material-deep purple"): return _material(name)
    if land_equals(name, "material-indigo"): return _material(name)
    if land_equals(name, "material-blue"): return _material(name)
    if land_equals(name, "material-light blue"): return _material(name)
    if land_equals(name, "material-cyan"): return _material(name)
    if land_equals(name, "material-teal"): return _material(name)
    if land_equals(name, "material-green"): return _material(name)
    if land_equals(name, "material-light green"): return _material(name)
    if land_equals(name, "material-lime"): return _material(name)
    if land_equals(name, "material-yellow"): return _material(name)
    if land_equals(name, "material-amber"): return _material(name)
    if land_equals(name, "material-orange"): return _material(name)
    if land_equals(name, "material-deep orange"): return _material(name)
    if land_equals(name, "material-brown"): return _material(name)
    if land_equals(name, "material-grey"): return _material(name)
    if land_equals(name, "material-blue grey"): return _material(name)
    return None

def _material(str palname) -> LandArray *:
    LandArray *pal = google_material_palette(palname + strlen("material-"))
    land_hash_insert(_palettes, palname, pal)
    return pal

def _make_palette_hue(str name, float h1, h2) -> LandArray *:
    LandArray *pal = land_array_new()
    for int i in range(14 * 11):
        LandColor col = land_palette_color("14x11", i)
        (double l, c, h) = land_color_to_oklch(col)
        if c < 0.1: continue
        if (h2 > h1 and h > h1 and h < h2) or (h2 < h1 and (h > h1 or h < h2)):
            LandColor *cp; land_alloc(cp)
            *cp = col
            land_array_add(pal, cp)
    _sort(pal)
    land_hash_insert(_palettes, name, pal)
    return pal

def _cmp_lum(void const *a, void const *b) -> int:
    LandColor *const*ac = a
    LandColor *const *bc = b
    (double la, aa, ba) = land_color_to_oklab(**ac)
    (double lb, ab, bb) = land_color_to_oklab(**bc)
    if la < lb: return -1
    if la > lb: return 1
    return 0

def _sort(LandArray *pal):
    land_array_sort(pal, _cmp_lum)

def land_palette_color(char const * name, int p) -> LandColor:
    auto pal = _get_palette(name)
    if not pal:
        return land_transparent()
    LandColor *col = land_array_get_wrap(pal, p)
    return *col

def land_palette_close(char const * name, LandColor orig) -> LandColor:
    auto pal = _get_palette(name)
    double cd = 1000
    LandColor found
    for LandColor *c in pal:
        double d = land_color_distance_ciede2000(*c, orig)
        if d < cd:
            cd = d
            found = *c
    return found

def land_palette_length(char const* name) -> int:
    auto pal = _get_palette(name)
    if not pal:
        return 0
    return land_array_count(pal)
