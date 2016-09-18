class LandColor:
   float r, g, b, a

static import land/allegro5/a5_misc
static import global ctype
static import global string
static import land.util
static import land.array
static import land.buffer
static import land.mem
static import land.hash

static LandHash *cache

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

def color_bash(char const *x) -> char const *:
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
    LandArray *a = land_split(x, ' ')
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
        
   
