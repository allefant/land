import global assert
import array, display, hash
import land.color

class LandFont:
    int size
    double xscaling
    double yscaling
    double rotation
    int flags
    char *filename

typedef void (PrintFunc)(char const *s, int alignment)

class LandFontState:
    float x_pos, y_pos
    float adjust_width
    LandFont *font
    float x, y, w, h
    float multi_w, multi_h
    bool off
    float wordwrap_width, wordwrap_height
    bool in_paragraph
    float paragraph_x
    float paragraph_wrap
    PrintFunc *print_override
    bool background
    float background_radius
    LandColor background_color
    bool confine_hor, confine_ver
    float confine_x, confine_y, confine_w, confine_h

    LandTextCache *cache

class LandTextCacheEntry:
    LandFont *font
    LandColor color
    LandFloat x, y, w, h
    char *text

class LandTextCache:
    LandFloat x, y
    LandArray *texts

enum:
    LandAlignRight = 1
    LandAlignCenter = 2
    LandAlignAdjust = 4
    LandAlignMiddle = 8
    LandAlignBottom = 16

static import global stdio
static import font, exception, main

static import allegro5/a5_font

static LandFontState *land_font_state
static LandFont *initial
static int active

static def line(int x1, y1, x2, y2):
    float px = x1
    float py = y1
    int dx = x2 - x1
    int dy = y2 - y1
    int d = abs(dx) > abs(dy) ? abs(dx) : abs(dy)

    if x1 == x2 and y1 == y2:
         land_filled_rectangle(x1, y1, x1 + 1, y1 + 1)
         return

    for int i in range(d + 1):
        float fx = px + i * dx / (float)d
        float fy = py + i * dy / (float)d
        int x = fx
        int y = fy
        land_filled_rectangle(x, y, x + 1, y + 1)

static def letter(char glyph, str code):
    #            _______
    # |         |        
    # |         |
    # |         |
    # |_______  |
    # |         |        
    # |         |        
    # |         |         
    # |         |_______
    #
    int x = glyph * 16
    int y = 0
    int n = strlen(code)
    int v[2] = {0, 0}
    int vi = 0
    int vc = 0
    int vs = 0
    int vn = 0
    land_color(0, 0, 0, 0)
    land_unclip()
    land_blend(LAND_BLEND_SOLID)
    land_filled_rectangle(x + 1, y + 1, x + 11, y + 12)
    land_clip(x + 1, y + 1, x + 11, y + 11)
    land_color(1, 1, 1, 1)
    for int i in range(n):
        char c = code[i]
        if c >= '0' and c <= '9':
            vc = vc * 10
            vc += c - '0'
            vn++
        elif c == '-':
            vs = -1
        else:
            if vn:
                if vs: vc = -vc
                if vi < 2:
                    v[vi] = vc
                else:
                    print("ERROR: can only have two parameters")
                vi++
            vc = vs = vn = 0

        if c == 'm':
            x += v[0]
            y += v[1]
            vi = 0
        elif c == 'l':
            line(1 + x, 1 + y, 1 + x + v[0], 1 + y + v[1])
            x += v[0]
            y += v[1]
            vi = 0
        elif c == 'c':
            int dx = sgn(v[0])
            int dy = sgn(v[1])
            line(1 + x, 1 + y, 1 + x + v[0] - dx, 1 + y)
            line(1 + x + v[0], 1 + y + dy, 1 + x + v[0], 1 + y + v[1])
            x += v[0]
            y += v[1]
            vi = 0
        elif c == 'd':
            int dx = sgn(v[0])
            int dy = sgn(v[1])
            line(1 + x, 1 + y, 1 + x, 1 + y + v[1] - dy)
            line(1 + x + dx, 1 + y + v[1], 1 + x + v[0], 1 + y + v[1])
            x += v[0]
            y += v[1]
            vi = 0
        elif c == '>' or c == '<':
            int dx = v[0] // 2
            int dy = v[1] // 2
            int nx = dy
            int ny = -dx
            if c == '<':
                nx = -nx
                ny = -ny
            line(1 + x, 1 + y, 1 + x + dx + nx, 1 + y + dy + ny)
            line(1 + x + dx + nx, 1 + y + dy + ny, 1 + x + v[0], 1 + y + v[1])
            x += v[0]
            y += v[1]
            vi = 0

static def initial_font:
    LandImage *i = land_image_new(128 * 16, 16)
    land_set_image_display(i)
    land_blend(LAND_BLEND_SOLID) # applies only to the current image
    land_clear(1, 1, 0, 1)
    for int i in range(128): letter(i, "")
    letter('A', "0 8 m 0 -8 l 8 0 l 0 8 l 0 -3 m -8 0 l")
    letter('B', "0 8 l 6 0 l 0 -4 < 0 -4 < -6 0 l 0 4 m 6 0 l")
    letter('C', "8 0 m -8 0 l 0 8 l 8 0 l")
    letter('D', "0 8 l 4 0 l 0 -8 < -4 0 l")
    letter('E', "0 8 l 8 0 l -8 -4 m 8 0 l -8 -4 m 8 0 l")
    letter('F', "0 8 l 0 -4 m 8 0 l -8 -4 m 8 0 l")
    letter('G', "8 0 m -8 0 l 0 8 l 8 0 l 0 -4 l -4 0 l")
    letter('H', "0 8 l 8 0 m 0 -8 l -8 4 m 8 0 l")
    letter('I', "8 0 l -4 0 m 0 8 l -4 0 m 8 0 l")
    letter('J', "0 8 m 8 0 l 0 -8 l")
    letter('K', "0 8 l 0 -4 m 4 0 l 4 -4 l -4 4 m 4 4 l")
    letter('L', "0 8 l 8 0 l")
    letter('M', "0 8 m 0 -8 l 8 0 l 0 8 l -4 0 m 0 -8 l")
    letter('N', "0 8 m 0 -8 l 8 0 l 0 8 l")
    letter('O', "8 0 l 0 8 l -8 0 l 0 -8 l")
    letter('P', "0 8 l 0 -8 m 6 0 l 0 4 > -6 0 l")
    letter('Q', "8 0 l 0 8 l -8 0 l 0 -8 l 4 4 m 4 4 l")
    letter('R', "0 8 l 0 -8 m 6 0 l 0 4 > -6 0 l 4 0 m 4 4 l")
    letter('S', "8 0 m -8 0 l 0 4 l 8 0 l 0 4 l -8 0 l")
    letter('T', "8 0 l -4 0 m 0 8 l")
    letter('U', "0 8 l 8 0 l 0 -8 l")
    letter('V', "0 4 l 4 4 l 4 -4 l 0 -4 l")
    letter('W', "0 8 l 8 0 l 0 -8 l -4 0 m 0 8 l")
    letter('X', "8 8 l -8 0 m 8 -8 l")
    letter('Y', "4 4 l 0 4 l 0 -4 m 4 -4 l")
    letter('Z', "8 0 l -8 8 l 8 0 l")
    letter('a', "1 2 m 6 0 l 0 6 l -6 0 l 0 -3 l 6 0 l")
    letter('b', "1 0 m 0 8 l 3 0 l 3 -3 l -3 -3 l -3 0 l")
    letter('c', "7 8 m -3 0 l -3 -3 l 3 -3 l 3 0 l")
    letter('d', "7 0 m 0 8 l -3 0 l -3 -3 l 3 -3 l 3 0 l")
    letter('e', "7 8 m -3 0 l -3 -3 l 3 -3 l 3 0 l 0 3 l -4 0 l")
    letter('f', "3 0 m 0 8 l -2 -4 m 4 0 l -2 -4 m 4 0 l")
    letter('g', "1 2 m 6 0 l 0 6 l -6 0 l 0 -2 m 6 0 l -6 0 m 0 -4 l")
    letter('h', "1 0 m 0 8 l 0 -6 m 6 0 l 0 6 l")
    letter('i', "1 2 m 3 0 l 0 6 l 3 0 l -3 -8 m 0 0 l")
    letter('j', "5 2 m 0 6 l -4 0 l 4 -8 m 0 0 l")
    letter('k', "1 0 m 0 8 l 0 -3 m 3 0 l 3 3 l -3 -3 m 3 -3 l")
    letter('l', "1 0 m 3 0 l 0 8 l 3 0 l")
    letter('m', "1 8 m 0 -6 l 6 0 l 0 6 l -3 0 m 0 -6 l")
    letter('n', "1 8 m 0 -6 l 6 0 l 0 6 l")
    letter('o', "1 2 m 6 0 l 0 6 l -6 0 l 0 -6 l")
    letter('p', "1 2 m 6 0 l 0 4 l -6 0 l 0 2 m 0 -6 l")
    letter('q', "1 2 m 6 0 l 0 6 l 0 -2 m -6 0 l 0 -4 l")
    letter('r', "1 2 m 0 6 l 0 -3 m 3 -3 l 3 0 l")
    letter('s', "7 2 m -3 0 l -3 3 l 6 0 l -3 3 l -3 0 l")
    letter('t', "4 0 m 0 8 l -3 -6 m 6 0 l")
    letter('u', "1 2 m 0 6 l 6 0 l 0 -6 l")
    letter('v', "1 2 m 0 3 l 3 3 l 3 -3 l 0 -3 l")
    letter('w', "1 2 m 0 6 l 6 0 l 0 -6 l -3 0 m 0 6 l")
    letter('x', "1 2 m 6 6 l -6 0 m 6 -6 l")
    letter('y', "1 2 m 3 3 l 3 -3 m -6 6 l")
    letter('z', "1 2 m 6 0 l -6 6 l 6 0 l")
    letter('.', "4 8 m 0 0 l")
    letter(':', "4 4 m 0 0 l 0 4 m 0 0 l")
    letter('/', "0 8 m 8 -8 l")
    letter('%', "0 8 m 8 -8 l -8 0 m 2 0 l 0 2 l -2 0 l 0 -2 l 6 6 m 2 0 l 0 2 l -2 0 l 0 -2 l")
    letter('\\', "8 8 l")
    letter('-', "1 4 m 6 0 l")
    letter('=', "1 3 m 6 0 l 0 3 m -6 0 l")
    letter('+', "1 4 m 6 0 l -3 -3 m 0 6 l")
    letter('0', "2 0 m 4 0 l 2 2 l 0 4 l -2 2 l -4 0 l -2 -2 l 0 -4 l 2 -2 l")
    letter('1', "2 0 m 2 0 l 0 8 l -4 0 m 8 0 l")
    letter('2', "0 1 m 1 -1 l 6 0 l 1 1 l 0 3 l -8 4 l 8 0 l")
    letter('3', "6 0 l 2 2 l -2 2 l -6 0 l 6 0 m 2 2 l -2 2 l -6 0 l")
    letter('4', "6 0 m -6 6 l 8 0 l -1 -6 m 0 8 l")
    letter('5', "7 0 m -7 0 l 0 4 l 6 0 l 2 2 l -2 2 l -6 0 l")
    letter('6', "7 1 m -1 -1 l -4 0 l -2 2 l 0 4 l 2 2 l 4 0 l 2 -2 l -2 -2 l -5 0 l")
    letter('7', "8 0 l -4 8 l")
    letter('8', "2 4 m -2 2 l 2 2 l 4 0 l 2 -2 l -2 -2 l 2 -2 l -2 -2 l -4 0 l -2 2 l 2 2 l 4 0 l")
    letter('9', "7 4 m -5 0 l -2 -2 l 2 -2 l 4 0 l 2 2 l 0 4 l -2 2 l -4 0 l")
    letter('(', "6 0 m -1 0 l -2 2 l 0 4 l 2 2 l 1 0 l")
    letter(')', "2 0 m 1 0 l 2 2 l 0 4 l -2 2 l -1 0 l")
    letter('[', "6 0 m -2 0 l 0 8 l 2 0 l")
    letter(']', "4 0 m 2 0 l 0 8 l -2 0 l")
    letter('<', "6 8 m 0 -8 >")
    letter('>', "2 0 m 0 8 >")
    letter('{', "6 0 m -2 2 c 0 4 < 2 2 d")
    letter('}', "4 0 m 2 2 c 0 4 > -2 2 d")
    letter('#', "2 0 m 0 8 l 4 0 m 0 -8 l 2 2 m -8 0 l 0 4 m 8 0 l")
    letter('*', "4 4 m 0 -3 m 0 6 l 3 -1 m -2 -2 l 2 -2 l -6 0 m 2 2 l -2 2 l")
    letter('"', "2 0 m 0 2 l 4 0 m 0 -2 l")
    letter('\'', "4 0 m 0 2 l")
    letter(',', "4 6 m 0 2 l")
    letter('_', "0 8 m 8 0 l")
    letter('&', "2 4 m -2 2 l 2 2 l 2 0 l 4 -4 l 0 4 m -4 -4 l 2 -2 l -2 -2 l -2 0 l -2 2 l 2 2 l 2 0 l")
    letter('?', "4 8 m 0 0 l 0 -2 m 0 -1 l 3 -3 l -2 -2 l -3 0 l -2 2 l")
    letter('!', "4 8 m 0 0 l 0 -2 m 0 -6 l")
    letter('|', "4 0 m 0 8 l")
    land_unset_image_display()

    int r[] = {0, 127}
    LandFont *f = land_font_from_image(i, 1, r)
    land_font_state.font = initial = f
    land_image_destroy(i)

def land_initial_font -> LandFont*:
    return initial

def land_font_init():
    if active: return
    land_log_message("land_font_init\n");
    land_alloc(land_font_state)
    platform_font_init()
    active = 1
    initial_font()

def land_font_exit():
    if not active: return
    land_free(land_font_state)
    platform_font_exit()
    active = 0

def land_font_reset:
    land_font_state.off = False
    land_font_state.in_paragraph = False
    land_font_state.print_override = None
    land_font_state.background = False
    land_font_state.background = False
    land_font_state.confine_hor = False
    land_font_state.confine_ver = False

def land_font_active() -> int:
    return active

def land_font_load(char const *filename, float size) -> LandFont *:
    """
    Load the given font file, with the given size. The size usually is the pixel
    height of a line in the font. But some fonts, e.g. bitmap fonts, will
    ignore it. The font also us made the current font if successfully loaded.
    """
    char *path = land_path_with_prefix(filename)
    LandFont *self = platform_font_load(path, size)
    self.filename = path
    if self.flags & LAND_LOADED:
        land_font_state.font = self
    return self

def land_font_load_zoom(str filename, float size) -> LandFont *:
    double s = land_display_width() / 64.0 * size
    return land_font_load(filename, s)

def land_font_check_loaded(LandFont *self):
    if self.flags & LAND_LOADED:
        return
    land_exception("Could not load font %s. Aborting.", self.filename)

def land_font_load_or_abort(str filename, float size) -> LandFont *:
    auto font = land_font_load(filename, size)
    land_font_check_loaded(font)
    return font

def land_font_destroy(LandFont *self):
    if self.filename:
        land_free(self.filename)
    platform_font_destroy(self)
    if land_font_state.font == self:
        land_font_state.font = initial
    
def land_font_new() -> LandFont *:
    LandFont *f = platform_font_new()
    return f

def land_font_scale(LandFont *f, double scaling):
    f.xscaling = f.yscaling = scaling

def land_font_yscale(LandFont *f, double scaling):
    f.yscaling = scaling

def land_font_rotation(LandFont *f, double rotation):
    f.rotation = rotation

def land_font_set(LandFont *self):
    if not self: self = initial
    land_font_state.font = self

def land_text_pos(float x, float y):
    land_font_state.x_pos = x
    land_font_state.y_pos = y

def land_text_set_x(float x):
    land_font_state.x_pos = x

def land_text_set_y(float y):
    land_font_state.y_pos = y

def land_text_set_width(float w):
    land_font_state.adjust_width = w

def land_text_pos_add(float xa, ya):
    land_font_state.x_pos += xa
    land_font_state.y_pos += ya

def land_text_pos_x(float x):
    land_font_state.x_pos = x

def land_newline:
    land_font_state.y_pos += land_line_height()

# Confine text drawing to inside the given column
def land_text_confine(float x, w):
    if w <= 0:
        land_font_state.confine_hor = False
        return
    land_font_state.confine_hor = True
    land_font_state.confine_x = x
    land_font_state.confine_w = w

def land_text_confine_vertical(float y, h):
    if h <= 0:
        land_font_state.confine_ver = False
        return
    land_font_state.confine_ver = True
    land_font_state.confine_y = y
    land_font_state.confine_h = h

# Current cursor X coordinate.
def land_text_x_pos() -> float:
    return land_font_state.x_pos

# Current cursor Y coordinate.
def land_text_y_pos() -> float:
    return land_font_state.y_pos

# Left edge of last printed text.
def land_text_x() -> float:
    return land_font_state.x

# Top edge of last printed text.
def land_text_y() -> float:
    return land_font_state.y

# Right edge of last printed text.
def land_text_x2() -> float:
    return land_font_state.x + land_font_state.w

# Bottom edge of last printed text.
def land_text_y2() -> float:
    return land_font_state.y + land_font_state.h

# Width of last printed text.
def land_text_width() -> float:
    return land_font_state.w

# Height of last printed text.
def land_text_height() -> float:
    return land_font_state.h

def land_text_state() -> int:
    return land_font_state.off

def land_font_height(LandFont *self) -> float:
    return self.size * self.yscaling

def land_font_current() -> LandFont *:
    return land_font_state.font

def land_line_height -> float:
    return land_font_height(land_font_current())

def land_text_off():
    land_font_state.off = 1

def land_text_on():
    land_font_state.off = 0

def land_text_is_on -> bool:
    return land_font_state.off == 0

def land_paragraph_start(float wrap_width):
    land_font_state.in_paragraph = True
    land_font_state.paragraph_x = land_font_state.x_pos
    land_font_state.paragraph_wrap = wrap_width

def land_text_background(LandColor color, float radius):
    land_font_state.background = True
    land_font_state.background_color = color
    land_font_state.background_radius = radius

def land_text_background_off:
    land_font_state.background = False

def land_paragraph_end:
    land_font_state.in_paragraph = False

def land_print_string(char const *s, int newline, int alignment):
    auto lfs = land_font_state
    if lfs.in_paragraph and lfs.paragraph_wrap > 0:
        float w = land_text_get_width(s)
        if lfs.x_pos + w > lfs.paragraph_x + lfs.paragraph_wrap:
            lfs.x_pos = lfs.paragraph_x
            lfs.y_pos += lfs.h

    if lfs.background:
        float ew, eh
        land_text_get_extents(s, &ew, &eh)
        float r = lfs.background_radius
        LandColor backup = land_color_get()
        land_color_set(lfs.background_color)
        float xo = 0, yo = 0
        if alignment & LandAlignMiddle:
            yo = eh / 2
        if alignment & LandAlignBottom:
            yo = eh
        if alignment & LandAlignCenter:
            xo = ew / 2
        if alignment & LandAlignRight:
            xo = ew
        float x0 = lfs.x_pos - xo - r
        float y0 = lfs.y_pos - r - yo
        float x1 = lfs.x_pos - xo + ew + r
        float y1 = lfs.y_pos - yo + eh + r
        if lfs.confine_hor:
            float over = lfs.confine_x - x0
            if over > 0:
                x0 += over
                x1 += over
        if lfs.confine_ver:
            float over = lfs.confine_y - y0
            if over > 0:
                y0 += over
                y1 += over
    
        land_filled_rounded_rectangle(x0, y0,
            x1, y1, r)
        land_color_set(backup)

    if lfs.print_override:
        PrintFunc *backup = lfs.print_override
        lfs.print_override = None
        backup(s, alignment)
        lfs.print_override = backup
    else:
        platform_font_print(land_font_state, s, alignment)
        if lfs.cache:
            land_text_cache_add(lfs.cache, s)

    if newline:
        lfs.y_pos = lfs.y + lfs.h
        if lfs.w > lfs.multi_w:
            lfs.multi_w = lfs.w
        lfs.multi_h += lfs.h
        if lfs.in_paragraph:
            lfs.x_pos = lfs.paragraph_x
    else:
        lfs.x_pos = lfs.x + lfs.w

def land_print_space(int x):
   land_font_state.x_pos += x

def land_font_set_print_override(PrintFunc print_override):
    land_font_state.print_override = print_override

def land_text_get_width(str s) -> float:
    return platform_text_width(land_font_state, s)

def land_text_get_extents(char const *str, float *w, *h):
    int onoff = land_font_state.off
    land_font_state.off = 1
    platform_font_print(land_font_state, str, 0)
    land_font_state.off = onoff
    *w = land_font_state.w
    *h = land_font_state.h

def land_text_get_multiline_size(char const *s, float *w, *h):
    int onoff = land_font_state.off
    land_font_state.off = 1
    float x_pos = land_font_state.x_pos
    float y_pos = land_font_state.y_pos

    auto a = land_text_splitlines(s)
    land_print_lines(a, 0)
    land_array_destroy_with_strings(a)

    land_font_state.off = onoff
    *w = land_font_state.multi_w
    *h = land_font_state.multi_h
    land_font_state.x_pos = x_pos
    land_font_state.y_pos = y_pos

def land_text_get_char_offset(char const *s, int nth) -> float:
    """
    Get the position at which the nth character is drawn. 
    """
    # fixme: can we avoid memory allocation in this function?
    if nth <= 0: return 0
    char *u = land_strdup(s)
    char *p = u
    int c = 0
    for int i = 0 while i < nth with i++:
        c = land_utf8_char(&p)
        if c == 0: break
    if c != 0: *p = 0
    float x = land_text_get_width(u)
    land_free(u)
    return x

# Get the character index which is under the given pixel position, so that
# the following j always is i:
# x = land_text_get_char_offset(str, i)
# j = land_text_get_char_index(str, x)
def land_text_get_char_index(char const *str, int x) -> int:
    if x < 0: return 0
    int l = 0
    char *p = (char *)str
    while land_utf8_char(&p): l++
    for int i = 0 while i <= l with i++:
        if land_text_get_char_offset(str, i) > x: return i - 1
    return l

macro VPRINT:
    va_list args
    va_start(args, text)
    int n = vsnprintf(None, 0, text, args)
    va_end(args)
    if n < 0: n = 1023
    char s[n + 1]
    va_start(args, text)
    vsnprintf(s, n + 1, text, args)
    va_end(args) 

def land_print(char const *text, ...):
    VPRINT
    land_print_string(s, 1, 0)

def land_print_right(char const *text, ...):
    VPRINT
    land_print_string(s, 1, LandAlignRight)

def land_print_bottom(char const *text, ...):
    VPRINT
    land_print_string(s, 1, LandAlignBottom)

def land_print_bottom_right(char const *text, ...):
    VPRINT
    land_print_string(s, 1, LandAlignRight | LandAlignBottom)

def land_print_bottom_center(char const *text, ...):
    VPRINT
    land_print_string(s, 1, LandAlignCenter | LandAlignBottom)

def land_print_center(char const *text, ...):
    VPRINT
    land_print_string(s, 1, LandAlignCenter)

def land_print_middle(char const *text, ...):
    VPRINT
    land_print_string(s, 1, LandAlignCenter | LandAlignMiddle)

def land_write(char const *text, ...):
    VPRINT
    land_print_string(s, 0, 0)

def land_write_right(char const *text, ...):
    VPRINT
    land_print_string(s, 0, LandAlignRight)

def land_write_center(char const *text, ...):
    VPRINT
    land_print_string(s, 0, LandAlignCenter)

def land_write_middle(char const *text, ...):
    VPRINT
    land_print_string(s, 0, LandAlignCenter | LandAlignMiddle)

def land_printv(char const *text, va_list args):
    va_list args2
    va_copy(args2, args)
    int n = vsnprintf(None, 0, text, args2)
    va_end(args2)
    if n < 0: n = 1023
    char s[n + 1]
    vsnprintf(s, n + 1, text, args)

    land_print_string(s, 1, 0)

def land_writev(char const *text, va_list args):
    va_list args2
    va_copy(args2, args)
    int n = vsnprintf(None, 0, text, args2)
    va_end(args2)
    if n < 0: n = 1023
    char s[n + 1]
    vsnprintf(s, n + 1, text, args)

    land_print_string(s, 0, 0)

def land_indent(char const *text, ...):
    VPRINT
    land_font_state.x_pos += land_text_get_width(s)

class LandWordWrapState:
    str line_start_p # start of current line
    str word_end_p # to (one past) end of last word
    str prev_word_end_p # so we can jump back after a wrap

    bool after_newline

    int break_char # one of ' ', '\n', '\0'

    float x, y, w, h
    float cursor_x, cursor_y

    void (*cb)(int a, int b, void *data)
    void *data
    str text

def land_wordwrap_new(float x, y, w, h) -> LandWordWrapState*:
    LandWordWrapState *self; land_alloc(self)
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.cursor_x = x
    self.cursor_y = y
    self.after_newline = True
    return self

def land_wordwrap_destroy(LandWordWrapState *self):
    land_free(self)

def land_wordwrap_print_string(LandWordWrapState *self, str text,
        void (*cb)(int a, int b, void *data), void *data):
    self.line_start_p = text
    self.word_end_p = text
    self.prev_word_end_p = text
    self.text = text
    self.cb = cb
    self.data = data
    float prev_x = self.cursor_x - self.x
    #print("NEW")
    while True:
        if self.h > 0:
            if self.cursor_y >= self.y + self.h:
                break
        _find_next_word(self)
        float x = land_text_get_char_offset(self.line_start_p, self.word_end_p - self.line_start_p)
        #printf("'")
        #for str c = self.line_start_p while c != self.word_end_p with c++:
        #    if *c <= 32: printf("[%d]", *c)
        #    else: printf("%c", *c)
        #printf("' %.0f (%.0f>%.0f)\n", x, self.cursor_x + x, self.x + self.w)
        #land_wait(0.01)
        if self.cursor_x + x > self.x + self.w: # we're over
            if self.prev_word_end_p == self.line_start_p:
                if self.after_newline:
                    # just a singe long word, and at start of line
                    _print_wordwrap_line(self, newline=True, x)
                    if self.break_char == '\0':
                        break
                else:
                    # long word which doesn't fit, but might in the next
                    # line
                    self.word_end_p = self.prev_word_end_p
                    self.break_char = ' '
                    _wordwrap_newline(self)
            else:
                self.word_end_p = self.prev_word_end_p
                self.break_char = ' '
                _print_wordwrap_line(self, newline=True, prev_x)

        else: # we're not over
            if self.break_char == '\0':
                _print_wordwrap_line(self, newline=False, x)
                break
            elif self.break_char == '\n':
                _print_wordwrap_line(self, newline=True, x)
            else:
                # points to space
                self.prev_word_end_p = self.word_end_p
        prev_x = x

def _print_wordwrap_line(LandWordWrapState *self, bool newline, float w):
    # TODO: with different font heights, take maximum? but that is only
    # known later... we'd need two passes, first to find maximum font,
    # then to print
    land_text_pos(self.cursor_x, self.cursor_y)
    self.cb(self.line_start_p - self.text, self.word_end_p - self.text, self.data)
    float h = land_line_height()
    if self.cursor_x + w - self.x > land_font_state.wordwrap_width:
        land_font_state.wordwrap_width = self.cursor_x + w - self.x
    if self.cursor_y + h - self.y > land_font_state.wordwrap_height:
        land_font_state.wordwrap_height = self.cursor_y + h - self.y
    if newline:
        _wordwrap_newline(self)
        _consume_breakchar(self)
        self.prev_word_end_p = self.word_end_p
    else:
        self.after_newline = False
        self.cursor_x += w
    self.line_start_p = self.word_end_p

def _consume_breakchar(LandWordWrapState *self):
    str scan_p = self.word_end_p
    int c = land_utf8_char_const(&scan_p)
    if c == ' ' or c == '\n':
        self.word_end_p = scan_p

def _wordwrap_newline(LandWordWrapState *self):
    self.cursor_x = self.x
    self.cursor_y += land_line_height()
    self.after_newline = True
    self.prev_word_end_p = self.word_end_p

def _find_next_word(LandWordWrapState *self):
    """
    advance word_end_p to possible break and set break_char.
    word_end_p will point exactly to a space or newline.
    """
    bool inside_leading_whitespace = True
    str scan_p = self.word_end_p
    int c = 0
    while True:
        str last_p = scan_p
        c = land_utf8_char_const(&scan_p)
        self.word_end_p = last_p # on the \0 or \n or space
        if c == '\n' or c == '\0': break
        if c == ' ':
            if not inside_leading_whitespace: break
        else:
            inside_leading_whitespace = False
    self.break_char = c

# the callback is called for each line
#
# Existing newlines are honored. If you want to wrap already wrapped
# text to a different width, first remove the newlines.
#
# Extra spaces are prepended to the following word, if you don't want
# them, remove them first.
def land_wordwrap_helper(char const *text, int width, height, xoffset,
        void (*cb)(int a, int b, void *data), void *data) -> int:
    #print("helper %d/%d", width, height)
    auto w = land_wordwrap_new(0, 0, width, height)
    land_wordwrap_print_string(w, text, cb, data)
    int n = w.word_end_p - text
    land_wordwrap_destroy(w)
    return n

static def _print_wordwrap_cb(int a, b, void *data):
    void **p = data
    char *text = p[0]
    int *alignment = p[1]

    char s[b - a + 1]
    strncpy(s, text + a, b - a + 1)
    s[b - a] = 0
    land_print_string(s, 0, *alignment)

def land_print_string_wordwrap(char const *text, int w, h, offset, alignment) -> int:
    """
    Print text inside, and starts a new line whenever the text goes over the
    given width, wrapping at whitespace. If a single word is bigger than w, it
    will be printed in its own line and exceed w. If h is 0, the whole text is
    printed. Otherwise, only as many lines as fit into h pixels are printed.
    The return value is the offset into text in bytes of one past the last
    printed character.
    """
    void *data[] = {(void *)text, &alignment}
    land_wordwrap_reset()
    return land_wordwrap_helper(text, w, h, offset, _print_wordwrap_cb, data)

def land_wordwrap_reset:
    land_font_state.wordwrap_width = 0
    land_font_state.wordwrap_height = 0

def land_print_wordwrap(int w, h, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, offset=0, 0)

def land_print_wordwrap_offset(int w, h, offset, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, offset, 0)

def land_print_wordwrap_right(int w, h, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, offset=0, 1)

def land_print_wordwrap_center(int w, h, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, offset=0, 2)

static def land_wordwrap_text_cb(int a, b, void *data):
    void **p = data
    char const *text = p[0]
    LandArray *lines = p[1]
    char *s = land_malloc(b - a + 1)
    strncpy(s, text + a,  b - a + 1)
    s[b - a] = 0
    land_array_add(lines, s)

def land_wordwrap_text_offset(int w, h, offset, char const *str) -> LandArray *:
    """
    Splits the given string into multiple lines no longer than w pixels. The
    returned array will have a newly allocated string for each line. You are
    responsible for freeing those strings again.
    The calculations will use the current font. Note that for large texts, this
    can take a while, so you should do calculations on demand and only for the
    visible text.
    You can call land_wordwrap_extents after this functions to get the
    dimensions of a box which will be able to hold all the text.
    """
    #print("land_wordwrap_text_offset %d/%d", w, h)
    LandArray *lines = land_array_new()
    land_wordwrap_reset()
    if str:
        void *data[] = {(void *)str, lines}
        land_wordwrap_helper(str, w, h, offset, land_wordwrap_text_cb, data)
    return lines

def land_wordwrap_text(int w, h, char const *str) -> LandArray *:
    return land_wordwrap_text_offset(w, h, offset=0, str)

def land_text_destroy_lines(LandArray *lines):
    if not lines: return
    land_array_destroy_with_strings(lines)

def land_text_splitlines(char const *str) -> LandArray *:
    """
    Splits the text into lines, and updates the wordwrap extents.
    """
    land_font_state.wordwrap_width = 0
    LandFont *super = land_font_state.font

    LandArray *lines = land_array_new()
    while 1:
        char const *p = strchr(str, '\n')
        if not p:
            p = str + strlen(str)
        char *s = land_malloc(p - str + 1)
        strncpy(s, str, p - str)
        s[p - str] = 0

        int w = land_text_get_width(s)
        if w > land_font_state.wordwrap_width:
            land_font_state.wordwrap_width = w
        
        land_array_add(lines, s)
        if p[0] == 0: break
        str = p + 1
    land_font_state.wordwrap_height = land_font_state.font->size *\
        land_array_count(lines) * super.yscaling
    return lines

def land_wordwrap_extents(float *w, float *h):
    if w: *w = land_font_state.wordwrap_width
    if h: *h = land_font_state.wordwrap_height

def land_print_colored_lines(LandArray *lines, int alignment, LandHash *colors):
    """
    Given an array of lines, print the visible ones.
    """
    auto lfs = land_font_state
    float cl, ct, cr, cb
    land_get_clip(&cl, &ct, &cr, &cb)
    LandColor original = land_color_get()
    float fh = land_line_height()
    float ty = land_text_y_pos()
    int first = (ct - ty) / fh
    int last = (cb - ty) / fh
    int n = land_array_count(lines)
    if first < 0: first = 0
    if last > n - 1: last = n - 1
    land_font_state.multi_w = 0
    land_font_state.multi_h = 0
    if alignment & LandAlignMiddle:
        alignment ^= LandAlignMiddle
        land_font_state.y_pos -= n * fh / 2
    land_font_state.y_pos += fh * first

    float ew, eh
    land_wordwrap_extents(&ew, &eh)
    float backup_xpos = lfs.x_pos

    float r = land_font_state.background_radius

    if lfs.confine_hor:
        float over = (lfs.x_pos + ew) - (lfs.confine_x + lfs.confine_w)
        if lfs.background:
            over += r
        if over > 0:
            lfs.x_pos -= over

    if lfs.confine_ver:
        float over = (lfs.y_pos + eh) - (lfs.confine_y + lfs.confine_h)
        if lfs.background:
            over += r
        if over > 0:
            lfs.y_pos -= over # we actually move the text cursor vertically
        if lfs.y_pos < lfs.confine_y:
            lfs.y_pos = lfs.confine_y

    bool restore_background = lfs.background
    if lfs.background:
        lfs.background = False
        float x = land_font_state.x_pos
        float y = land_font_state.y_pos
        LandColor backup = land_color_get()
        land_color_set(land_font_state.background_color)
        float xo = 0, yo = 0
        if alignment & LandAlignMiddle:
            yo = eh / 2
        if alignment & LandAlignCenter:
            xo = ew / 2
        land_filled_rounded_rectangle(x - xo - r, y - r - yo,
            x - xo + ew + r, y - yo + eh + r, r)
        land_color_set(backup)

    for int i = first while i <= last with i++:
        char *s = land_array_get_nth(lines, i)
        char ckey[] = {i % 256, i / 256, 0}
        if colors:
            char *c = land_hash_get(colors, ckey)
            if c:
                land_color_set(land_color_name(c))
            else:
                land_color_set(original)
        land_print_string(s, 1, alignment)

    land_font_state.background = restore_background

    land_color_set(original)
    lfs.x_pos = backup_xpos

def land_set_line_color(LandHash *colors, int i, str col):
    char ckey[] = {i % 256, i / 256, 0}
    land_hash_insert(colors, ckey, (void *)col)

def land_print_lines(LandArray *lines, int alignment):
    land_print_colored_lines(lines, alignment, None)

def land_font_from_image(LandImage *image, int n_ranges,
        int *ranges) -> LandFont *:
    LandFont *self = platform_font_from_image(image, n_ranges, ranges)
    land_font_state.font = self
    return self

def land_print_multiline(char const *text, ...):
    VPRINT
    auto a = land_text_splitlines(s)
    land_print_lines(a, 0)
    land_array_destroy_with_strings(a)

def land_print_multiline_centered(char const *text, ...):
    VPRINT
    auto a = land_text_splitlines(s)
    land_print_lines(a, LandAlignCenter)
    land_array_destroy_with_strings(a)

def land_text_cache_new -> LandTextCache*:
    LandTextCache *self; land_alloc(self)
    self.texts = land_array_new()
    return self

def land_text_cache_start_recording(LandTextCache *self, LandFloat x, y):
    self.x = x
    self.y = y
    land_font_state.cache = self

def land_text_cache_stop_recording(LandTextCache *self):
    land_font_state.cache = None

def land_text_cache_add(LandTextCache *self, str text):
    LandTextCacheEntry *e; land_alloc(e)
    e.text = land_strdup(text)
    e.x = land_text_x()
    e.y = land_text_y()
    e.w = land_text_width()
    e.h = land_text_height()
    e.font = land_font_current()
    e.color = land_color_get()
    land_array_add(self.texts, e)

def land_text_cache_repeat(LandTextCache *self, LandFloat x, y):
    for LandTextCacheEntry *text in self.texts:
        land_text_pos(text.x - self.x + x, text.y - self.y + y)
        land_font_set(text.font)
        land_color_set(text.color)
        land_print(text.text)

def land_text_cache_destroy(LandTextCache *self):
    for LandTextCacheEntry *text in self.texts:
        land_free(text.text)
        land_free(text)
    land_array_destroy(self.texts)
    land_free(self)

