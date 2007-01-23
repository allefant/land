import array, display

class LandFontInterface:
    land_method(void, print, (LandFontState *state, LandDisplay *display, char const *text,
        int alignement))
    land_method(void, destroy, (LandDisplay *d, LandFont *self))

class LandFont:
    LandFontInterface *vt
    int size

class LandFontState:
    float x_pos, y_pos
    LandFont *font
    float x, y, w, h
    float off

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

static def _print(char const *str, int newline, int alignement):
    land_font_state->font->vt->print(land_font_state, _land_active_display, str,
        alignement)
    if newline:
        land_font_state->y_pos = land_font_state->y + land_font_state->h
    else:
        land_font_state->x_pos = land_font_state->x + land_font_state->w

int def land_text_get_width(char const *str):
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
    _print(str, 1, 0)

def land_print_right(char const *text, ...):
    VPRINT
    _print(str, 1, 1)

def land_print_center(char const *text, ...):
    VPRINT
    _print(str, 1, 2)

def land_write(char const *text, ...):
    VPRINT
    _print(str, 0, 0)

def land_write_right(char const *text, ...):
    VPRINT
    _print(str, 0, 1)

def land_write_center(char const *text, ...):
    VPRINT
    _print(str, 0, 2)

static int def _wordwrap_helper(char const *text, int w, h,
    void (*cb)(int a, int b, void *data), void *data):
    int y = land_text_y_pos()
    char const *a = text
    while 1:
        if h > 0 and land_text_y_pos() >= y + h: break
        int n = 0
        int pn
        while 1:
            pn = n
            int c
            while 1:
                c = ugetat(a, n)
                if c == 0: break
                if c == ' ' or c == '\n':
                    break
                n++

            int x = land_text_get_char_offset(a, n)
            if x > w:
                if pn > 0:
                    n = pn - 1
                break
            if c == 0 or c == '\n': break
            n++

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
    _print(s, 1, *alignement)

static int def _print_wordwrap(char const *text, int w, h, alignement):
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
    return _print_wordwrap(str, w, h, 0)

int def land_print_wordwrap_right(int w, h, char const *text, ...):
    VPRINT
    return _print_wordwrap(str, w, h, 1)

int def land_print_wordwrap_center(int w, h, char const *text, ...):
    VPRINT
    return _print_wordwrap(str, w, h, 2)

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
    """
    LandArray *lines = land_array_new()
    
    void *data[] = {(void *)str, lines}
    _wordwrap_helper(str, w, h, land_wordwrap_text_cb, data)

    return lines