import array, display

class LandFontInterface:
    land_method(void, print, (LandFontState *state, LandDisplay *display, char const *text,
        int alignement))
    land_method(void, destroy, (LandDisplay *d, LandFont *self))
    land_method(float, length, (LandFontState *state,    char const *text))

class LandFont:
    LandFontInterface *vt
    int size

class LandFontState:
    float x_pos, y_pos
    LandFont *font
    float x, y, w, h
    float off
    float wordwrap_width, wordwrap_height

static import global allegro, stdio
static import font, exception, main
static import allegro/font, allegrogl/font

static LandFontState *land_font_state
static int active

def land_font_init():
    land_alloc(land_font_state)
    land_font_allegrogl_init()
    land_font_allegro_init()
    active = 1

def land_font_exit():
    land_free(land_font_state)
    land_font_allegro_exit()
    land_font_allegrogl_exit()
    active = 0

int def land_font_active():
    return active

LandFont *def land_font_load(char const *filename, float size):
    LandFont *self
    if land_get_flags() & LAND_OPENGL:
        self = land_font_allegrogl_load(filename, size)
    else:
        self = land_font_allegro_load(filename, size)

    land_font_state->font = self
    return self

LandFont *def land_font_default():
    LandFont *self = None
    if land_get_flags() & LAND_OPENGL:
        self = land_font_allegrogl_default()
    land_font_state->font = self
    return self

def land_font_destroy(LandFont *self):
    land_display_del_font(self)

def land_font_set(LandFont *self):
    land_font_state->font = self

#__attribute__((noreturn))
def land_text_size(float sx, float sy):
    land_exception("Text sizing currently not implemented, use different fonts instead.")

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

def land_print_string(char const *str, int newline, int alignement):
    land_font_state->font->vt->print(land_font_state, _land_active_display, str,
        alignement)
    if newline:
        land_font_state->y_pos = land_font_state->y + land_font_state->h
    else:
        land_font_state->x_pos = land_font_state->x + land_font_state->w

int def land_text_get_width(char const *str):
    if land_font_state->font->vt->length:
        return land_font_state->font->vt->length(land_font_state, str)
    else:
        int onoff = land_font_state->off
        land_font_state->off = 1
        land_font_state->font->vt->print(land_font_state, NULL, str, 0)
        land_font_state->off = onoff
        return land_font_state->w

# Get the position at which the nth character is drawn. 
int def land_text_get_char_offset(char const *str, int nth):
    int l = ustrlen(str)
    if nth > l: nth = l
    char *s = land_strdup(str)
    usetat(s, nth, 0)
    int x = land_text_get_width(s)
    land_free(s)
    return x

# Get the character index which is under the given pixel position, so that
# the following j always is i:
# x = land_text_get_char_offset(str, i)
# j = land_text_get_char_index(str, x)
# 
int def land_text_get_char_index(char const *str, int x):
    if x < 0: return 0
    int l = ustrlen(str)
    int i
    for i = 0; i <= l; i++:
        if land_text_get_char_offset(str, i) > x: return i - 1

    return l

macro VPRINT char str[1024]; va_list args; va_start(args, text); vsnprintf(str, sizeof str, text, args); va_end(args);

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
    char const *a = text
    char glyph[sizeof(int) * 2]
    int *ig = (void *)glyph
    ig[1] = 0
    while 1:
        char const *ptr = a
        if h > 0 and land_text_y_pos() >= y + h: break
        int n = 0
        float offset = 0
        float www = 0
        int pn
        while 1:
            pn = n
            int c
            while 1:
                c = ugetat(ptr, 0)
                if c == 0: break
                if c == ' ' or c == '\n':
                    break
                ig[0] = c
                offset += land_text_get_width(glyph)
                ptr += uoffset(a, 1)
                n++

            int x = offset
            if x > w:
                if pn > 0:
                    n = pn - 1
                else:
                    www = x
                break
            www = x
            if c == 0 or c == '\n': break
            ig[0] = c
            offset += land_text_get_width(glyph)
            ptr += uoffset(ptr, 1)
            n++

        if www > land_font_state->wordwrap_width:
            land_font_state->wordwrap_width = www
        land_font_state->wordwrap_height += fh
        cb(a - text, a + n - text, data)

        a += uoffset(a, n)
        int c = ugetat(a, 0)
        if c == 0: break
        if c == ' ' or c == '\n': a += uoffset(a, 1)
    return a - text

static def _print_wordwrap_cb(int a, b, void *data):
    void **p = data
    char *text = p[0]
    int *alignement = p[1]

    char s[b - a + 1]
    ustrzcpy(s, b - a + 1, text + a)
    land_print_string(s, 1, *alignement)

int def land_print_string_wordwrap(char const *text, int w, h, alignement):
    """
    Print text inside, and starts a new line whenever the text goes over the
    given width, wrapping at whitespace. If a single word is bigger than w, it
    will be printed in its own line and exceed w. If h is 0, the whole text is
    printed. Otherwise, only as many lines as fit into h pixels are printed.
    The return value is the offset into text in bytes of one past the last
    printed character.
    """
    void *data[] = {(void *)text, &alignement}
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
    ustrzcpy(s, b - a + 1, text + a)
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

LandArray *def land_text_splitlines(char const *str):
    """
    Splits the text into lines, and updates the wordwrap extents.
    """
    land_font_state->wordwrap_width = 0

    LandArray *lines = land_array_new()
    while 1:
        char const *p = ustrchr(str, '\n')
        if not p:
            p = str + strlen(str)
        char *s = land_malloc(p - str + 1)
        ustrzcpy(s, p - str + 1, str)

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
    *w = land_font_state->wordwrap_width
    *h = land_font_state->wordwrap_height

def land_print_lines(LandArray *lines, int alignement):
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
    for int i = first; i <= last; i++:
        char *s = land_array_get_nth(lines, i)
        land_print_string(s, 1, alignement)
