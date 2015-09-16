class LandColor:
   float r, g, b, a

static import land/allegro5/a5_misc
static import global ctype

def land_color_hsv(float hue, sat, val) -> LandColor:
    return platform_color_hsv(hue, sat, val)

def land_color_rgba(float r, g, b, a) -> LandColor:
    LandColor c = {r, g, b, a}
    return c

def land_color_premul(float r, g, b, a) -> LandColor:
    LandColor c = {r * a, g * a, b * a, a}
    return c

static int hexval(char c):
    c = tolower(c)
    if c >= '0' and c <= '9': return (c - '0')
    if c >= 'a' and c <= 'f': return 10 + (c - 'a')
    return 0

def land_color_name(char const *name) -> LandColor:
    if name and name[0] == '#':
        LandColor c
        c.r = (hexval(name[1]) * 16 + hexval(name[2])) / 255.0
        c.g = (hexval(name[3]) * 16 + hexval(name[4])) / 255.0
        c.b = (hexval(name[5]) * 16 + hexval(name[6])) / 255.0
        c.a = 1
        return c
    return platform_color_name(name)

def land_color_lerp(LandColor a, b, float t) -> LandColor:
    return land_color_rgba(
        a.r + t * (b.r - a.r),
        a.g + t * (b.g - a.g),
        a.b + t * (b.b - a.b),
        a.a + t * (b.a - a.a))
