import global assert
import array, display

class LandFont:
    int size

class LandFontState:
    float x_pos, y_pos
    LandFont *font
    float x, y, w, h
    bool off
    float wordwrap_width, wordwrap_height

enum:
    LandAlignLeft
    LandAlignRight
    LandAlignCenter

static import global stdio
static import font, exception, main

static import allegro5/a5_font

static LandFontState *land_font_state
static int active

def land_font_init():
    if active: return
    land_alloc(land_font_state)
    platform_font_init()
    active = 1

def land_font_exit():
    if not active: return
    land_free(land_font_state)
    platform_font_exit()
    active = 0

int def land_font_active():
    return active

LandFont *def land_font_load(char const *filename, float size):
    """
    Load the given font file, with the given size. The size usually is the pixel
    height of a line in the font. But some fonts, e.g. bitmap fonts, will
    ignore it. The font also us made the current font if successfully loaded.
    """
    LandFont *self = platform_font_load(filename, size)

    land_font_state->font = self
    return self

def land_font_destroy(LandFont *self):
    land_display_del_font(self)

def land_font_set(LandFont *self):
    land_font_state->font = self

def land_text_pos(float x, float y):
    land_font_state->x_pos = x
    land_font_state->y_pos = y

# Current cursor X coordinate.
float def land_text_x_pos():
    return land_font_state->x_pos

# Current cursor Y coordinate.
float def land_text_y_pos():
    return land_font_state->y_pos

# Left edge of last printed text.
float def land_text_x():
    return land_font_state->x

# Top edge of last printed text.
float def land_text_y():
    return land_font_state->y

# Width of last printed text.
float def land_text_width():
    return land_font_state->w

# Height of last printed text.
float def land_text_height():
    return land_font_state->h

int def land_text_state():
    return land_font_state->off

int def land_font_height(LandFont *self):
    return self->size

LandFont *def land_font_current():
    return land_font_state->font

def land_text_off():
    land_font_state->off = 1

def land_text_on():
    land_font_state->off = 0

def land_print_string(char const *str, int newline, int alignment):
    platform_font_print(land_font_state, str, alignment)
    if newline:
        land_font_state->y_pos = land_font_state->y + land_font_state->h
    else:
        land_font_state->x_pos = land_font_state->x + land_font_state->w

int def land_text_get_width(char const *str):
    int onoff = land_font_state->off
    land_font_state->off = 1
    platform_font_print(land_font_state, str, 0)
    land_font_state->off = onoff
    return land_font_state->w

# Get the position at which the nth character is drawn. 
int def land_text_get_char_offset(char const *str, int nth):
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
int def land_text_get_char_index(char const *str, int x):
    if x < 0: return 0
    int l = 0
    char *p = (char *)str
    while land_utf8_char(&p): l++
    for int i = 0 while i <= l with i++:
        if land_text_get_char_offset(str, i) > x: return i - 1
    return l

macro VPRINT:
    char str[1024]
    va_list args
    va_start(args, text)
    vsnprintf(str, sizeof str, text, args)
    va_end(args)

def land_print(char const *text, ...):
    VPRINT
    land_print_string(str, 1, 0)

def land_print_right(char const *text, ...):
    VPRINT
    land_print_string(str, 1, 1)

def land_print_center(char const *text, ...):
    VPRINT
    land_print_string(str, 1, 2)

def land_write(char const *text, ...):
    VPRINT
    land_print_string(str, 0, 0)

def land_write_right(char const *text, ...):
    VPRINT
    land_print_string(str, 0, 1)

def land_write_center(char const *text, ...):
    VPRINT
    land_print_string(str, 0, 2)

static int def _wordwrap_helper(char const *text, int w, h,
    void (*cb)(int a, int b, void *data), void *data):
    int y = land_text_y_pos()
    float fh = land_font_state->font->size

    char const *line_start_p = text
    printf("wordwrap %d %d\n", w, h)

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
        if width_of_line > land_font_state->wordwrap_width:
            land_font_state->wordwrap_width = width_of_line
        land_font_state->wordwrap_height += fh
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

int def land_print_string_wordwrap(char const *text, int w, h, alignment):
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

int def land_print_wordwrap(int w, h, char const *text, ...):
    VPRINT
    return land_print_string_wordwrap(str, w, h, 0)

int def land_print_wordwrap_right(int w, h, char const *text, ...):
    VPRINT
    return land_print_string_wordwrap(str, w, h, 1)

int def land_print_wordwrap_center(int w, h, char const *text, ...):
    VPRINT
    return land_print_string_wordwrap(str, w, h, 2)

static def land_wordwrap_text_cb(int a, b, void *data):
    void **p = data
    char *text = p[0]
    LandArray *lines = p[1]
    char *s = land_malloc(b - a + 1)
    strncpy(s, text + a,  b - a + 1)
    s[b - a] = 0
    land_array_add(lines, s)

LandArray *def land_wordwrap_text(int w, h, char const *str):
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
    land_font_state->wordwrap_width = 0
    land_font_state->wordwrap_height = 0
    if str:
        void *data[] = {(void *)str, lines}
        _wordwrap_helper(str, w, h, land_wordwrap_text_cb, data)
    return lines

def land_text_destroy_lines(LandArray *lines):
    if not lines: return
    int n = land_array_count(lines)
    for int i = 0 while i < n with i++:
        char *s = land_array_get_nth(lines, i)
        land_free(s)
    land_array_destroy(lines)

LandArray *def land_text_splitlines(char const *str):
    """
    Splits the text into lines, and updates the wordwrap extents.
    """
    land_font_state->wordwrap_width = 0

    LandArray *lines = land_array_new()
    while 1:
        char const *p = strchr(str, '\n')
        if not p:
            p = str + strlen(str)
        char *s = land_malloc(p - str + 1)
        strncpy(s, str, p - str)
        s[p - str] = 0

        int w = land_text_get_width(s)
        if w > land_font_state->wordwrap_width:
            land_font_state->wordwrap_width = w
        
        land_array_add(lines, s)
        if p[0] == 0: break
        str = p + 1
    land_font_state->wordwrap_height = land_font_state->font->size *\
        land_array_count(lines)
    return lines

def land_wordwrap_extents(float *w, float *h):
    if w: *w = land_font_state->wordwrap_width
    if h: *h = land_font_state->wordwrap_height

def land_print_lines(LandArray *lines, int alignment):
    """
    Given an array of lines, print the visible ones.
    """
    float cl, ct, cr, cb
    land_get_clip(&cl, &ct, &cr, &cb)
    float fh = land_font_state->font->size
    float ty = land_text_y_pos()
    int first = (ct - ty) / fh
    int last = (cb - ty) / fh
    int n = land_array_count(lines)
    if first < 0: first = 0
    if last > n - 1: last = n - 1
    land_font_state->y_pos += fh * first
    for int i = first while i <= last with i++:
        char *s = land_array_get_nth(lines, i)
        land_print_string(s, 1, alignment)
