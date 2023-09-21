import global assert
import array, display, hash
import land.color

class LandFont:
    int size
    double xscaling
    double yscaling
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
    land_filled_rectangle(x + 1, y + 1, x + 11, y + 11)
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

static def initial_font:
    LandImage *i = land_image_new(128 * 16, 16)
    land_set_image_display(i)
    land_blend(LAND_BLEND_SOLID) # applies only to the current image
    land_clear(1, 1, 0, 1)
    for int i in range(128): letter(i, "")
    letter('A', "0 8 m 0 -8 l 8 0 l 0 8 l 0 -3 m -8 0 l")
    letter('B', "0 8 l 6 0 l 2 -2 l -2 -2 l 2 -2 l -2 -2 l -6 0 l 0 4 m 6 0 l")
    letter('C', "8 0 m -8 0 l 0 8 l 8 0 l")
    letter('D', "0 8 l 4 0 l 4 -4 l -4 -4 l -4 0 l")
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
    letter('P', "0 8 l 0 -8 m 6 0 l 2 2 l -2 2 l -6 0 l")
    letter('Q', "8 0 l 0 8 l -8 0 l 0 -8 l 4 4 m 4 4 l")
    letter('R', "0 8 l 0 -8 m 6 0 l 2 2 l -2 2 l -6 0 l 4 0 m 4 4 l")
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
    letter('i', "1 4 m 3 0 l 0 4 l 3 0 l -3 -6 m 0 0 l")
    letter('j', "5 4 m 0 4 l -4 0 l 4 -6 m 0 0 l")
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
    letter('/', "0 8 m 8 -8 l")
    letter('\\', "8 8 l")
    letter('-', "1 4 m 6 0 l")
    letter('+', "1 4 m 6 0 l -3 -3 m 0 6 l")
    letter('0', "8 0 l 0 8 l -8 0 l 0 -8 l")
    letter('1', "2 0 m 2 0 l 0 8 l -4 0 m 8 0 l")
    letter('2', "8 0 l 0 4 l -8 4 l 8 0 l")
    letter('3', "8 0 l 0 4 l -8 0 l 8 0 m 0 4 l -8 0 l")
    letter('4', "0 4 l 8 0 l 0 -4 m 0 8 l")
    letter('5', "8 0 m -8 0 l 0 4 l 8 0 l 0 4 l -8 0 l")
    letter('6', "8 0 m -8 0 l 0 8 l 8 0 l 0 -4 l -8 0 l")
    letter('7', "8 0 l -4 8 l")
    letter('8', "2 4 m -2 2 l 2 2 l 4 0 l 2 -2 l -2 -2 l 2 -2 l -2 -2 l -4 0 l -2 2 l 2 2 l 4 0 l")
    letter('9', "8 0 l 0 8 l -8 0 l 0 -8 m 0 4 l 8 0 l")
    letter('(', "6 0 m -2 1 l -2 2 l 0 2 l 2 2 l 2 1 l")
    letter(')', "2 8 m 2 -1 l 2 -2 l 0 -2 l -2 -2 l -2 -1 l")
    letter('[', "6 0 m -2 0 l 0 8 l 2 0 l")
    letter(']', "4 0 m 2 0 l 0 8 l -2 0 l")
    letter('<', "6 0 m -4 4 l 4 4 l")
    letter('>', "2 0 m 4 4 l -4 4 l")
    letter('{', "6 0 m -2 0 l 0 3 l -2 1 l 2 1 l 0 3 l 2 0 l")
    letter('}', "4 0 m 2 0 l 0 3 l 2 1 l -2 1 l 0 3 l -2 0 l")
    land_unset_image_display()

    int r[] = {0, 127}
    LandFont *f = land_font_from_image(i, 1, r)
    land_font_state.font = initial = f
    land_image_destroy(i)

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
    
def land_font_new() -> LandFont *:
    LandFont *f = platform_font_new()
    return f

def land_font_scale(LandFont *f, double scaling):
    f.xscaling = f.yscaling = scaling

def land_font_yscale(LandFont *f, double scaling):
    f.yscaling = scaling

def land_font_set(LandFont *self):
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
        if alignment & LandAlignCenter:
            xo = ew / 2
        land_filled_rounded_rectangle(lfs.x_pos - xo - r, lfs.y_pos - r - yo,
            lfs.x_pos - xo + ew + r, lfs.y_pos - yo + eh + r, r)
        land_color_set(backup)

    if lfs.print_override:
        PrintFunc *backup = lfs.print_override
        lfs.print_override = None
        backup(s, alignment)
        lfs.print_override = backup
    else:
        platform_font_print(land_font_state, s, alignment)

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

def land_text_get_width(char const *str) -> float:
    int onoff = land_font_state.off
    land_font_state.off = 1
    platform_font_print(land_font_state, str, 0)
    land_font_state.off = onoff
    return land_font_state.w

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

# Get the position at which the nth character is drawn. 
def land_text_get_char_offset(char const *str, int nth) -> int:
    char *u = land_strdup(str)
    char *p = u
    for int i = 0 while i < nth with i++:
        land_utf8_char(&p)
    *p = 0
    int x = land_text_get_width(u)
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

static def _wordwrap_helper(char const *text, int w, h,
    void (*cb)(int a, int b, void *data), void *data) -> int:
    int y = land_text_y_pos()
    float fh = land_font_state.font->size

    char const *line_start_p = text
    land_font_state.adjust_width = w
    #printf("wordwrap %d %d\n", w, h)

    while 1:
        # A new line begins.
        if h > 0 and land_text_y_pos() >= y + h: break
        float width_of_line = 0
        int word_end_glyphs = 0
        char const *word_end_p = line_start_p
        char const *prev_word_end_p = line_start_p
        char const *ptr
        int c
        while 1:
            # Find next possible break location.
            bool inside_leading_whitespace = True
            ptr = word_end_p
            int glyphs = word_end_glyphs
            while 1:
                c = land_utf8_char_const(&ptr)
                if c == 0: break
                if c == '\n': break
                if c == ' ':
                    if not inside_leading_whitespace: break
                else:
                    inside_leading_whitespace = False
                if inside_leading_whitespace and word_end_glyphs == 0:
                    line_start_p = ptr
                else:
                    glyphs++
                    word_end_p = ptr

            int x = land_text_get_char_offset(line_start_p, glyphs)
            if x > w: # found break point
                if word_end_glyphs == 0: # uh oh, only a single word
                    word_end_glyphs = glyphs
                    width_of_line = x
                else:
                    c = ' ' # in case it was 0 so we don't lose the last word
                    ptr = word_end_p = prev_word_end_p
                break
            width_of_line = x
            word_end_glyphs = glyphs
            prev_word_end_p = word_end_p
            if c == 0 or c == '\n':
                break
        if width_of_line > land_font_state.wordwrap_width:
            land_font_state.wordwrap_width = width_of_line
        land_font_state.wordwrap_height += fh
        if word_end_p < line_start_p:
            cb(line_start_p - text, line_start_p - text, data)
        else
            cb(line_start_p - text, word_end_p - text, data)
        line_start_p = ptr
        if c == 0: break
    return line_start_p - text

static def _print_wordwrap_cb(int a, b, void *data):
    void **p = data
    char *text = p[0]
    int *alignment = p[1]

    char s[b - a + 1]
    strncpy(s, text + a, b - a + 1)
    s[b - a] = 0
    land_print_string(s, 1, *alignment)

def land_print_string_wordwrap(char const *text, int w, h, alignment) -> int:
    """
    Print text inside, and starts a new line whenever the text goes over the
    given width, wrapping at whitespace. If a single word is bigger than w, it
    will be printed in its own line and exceed w. If h is 0, the whole text is
    printed. Otherwise, only as many lines as fit into h pixels are printed.
    The return value is the offset into text in bytes of one past the last
    printed character.
    """
    void *data[] = {(void *)text, &alignment}
    return _wordwrap_helper(text, w, h, _print_wordwrap_cb, data)

def land_print_wordwrap(int w, h, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, 0)

def land_print_wordwrap_right(int w, h, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, 1)

def land_print_wordwrap_center(int w, h, char const *text, ...) -> int:
    VPRINT
    return land_print_string_wordwrap(s, w, h, 2)

static def land_wordwrap_text_cb(int a, b, void *data):
    void **p = data
    char const *text = p[0]
    LandArray *lines = p[1]
    char *s = land_malloc(b - a + 1)
    strncpy(s, text + a,  b - a + 1)
    s[b - a] = 0
    land_array_add(lines, s)

def land_wordwrap_text(int w, h, char const *str) -> LandArray *:
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
    LandArray *lines = land_array_new()
    land_font_state.wordwrap_width = 0
    land_font_state.wordwrap_height = 0
    if str:
        void *data[] = {(void *)str, lines}
        _wordwrap_helper(str, w, h, land_wordwrap_text_cb, data)
    return lines

def land_text_destroy_lines(LandArray *lines):
    if not lines: return
    land_array_destroy_with_strings(lines)

def land_text_splitlines(char const *str) -> LandArray *:
    """
    Splits the text into lines, and updates the wordwrap extents.
    """
    land_font_state.wordwrap_width = 0

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
        land_array_count(lines)
    return lines

def land_wordwrap_extents(float *w, float *h):
    if w: *w = land_font_state.wordwrap_width
    if h: *h = land_font_state.wordwrap_height

def land_print_colored_lines(LandArray *lines, int alignment, LandHash *colors):
    """
    Given an array of lines, print the visible ones.
    """
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
    bool restore_background = land_font_state.background
    if land_font_state.background:
        land_font_state.background = False
        float ew, eh
        land_wordwrap_extents(&ew, &eh)
        float r = land_font_state.background_radius
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
