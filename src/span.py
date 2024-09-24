import land.font
import land.color

class LandTextSpan:
    char *text
    LandFont *font
    LandColor color

    float cache_x, cache_y

class LandText:
    int w, h
    int x, y
    LandArray *spans
    int alignment

    float cursor_x, cursor_y

    int ex, ey, ew, eh

def land_text_new(int x, y, w, h) -> LandText*:
    LandText *self; land_alloc(self)
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.spans = land_array_new()
    self.cursor_x = x
    self.cursor_y = y
    return self

def land_text_destroy(LandText *self):
    for LandTextSpan *span in self.spans:
        land_free(span.text)
        land_free(span)
    land_array_destroy(self.spans)
    land_free(self)

def land_text_add_span(LandText *self, LandFont *font, LandColor color, str f, ...):
    va_list args
    va_start(args, f)
    int n = vsnprintf(None, 0, f, args)
    va_end(args)
    if n < 0: n = 1023
    char *s = land_calloc(n + 1)
    va_start(args, f)
    vsnprintf(s, n + 1, f, args)
    va_end(args)

    LandTextSpan *span; land_alloc(span)
    span.text = s
    span.font = font
    span.color = color
    land_array_add(self.spans, span)

def land_text_draw(LandText *self):
    # fixme: could optimize for clipping rectangle, e.g. in case of
    # scrolling text
    # fixme: should cache text positions instead of doing a full
    # wordwrap every time
    self.ex = self.x
    self.ey = self.y
    self.ew = 0
    self.eh = 0
    self.cursor_x = self.x
    self.cursor_y = self.y
    land_text_pos(self.x, self.y)
    land_wordwrap_reset()
    LandWordWrapState *w = land_wordwrap_new(self.x, self.y, self.w, self.h)
    for LandTextSpan *span in self.spans:
        _span_draw(self, w, span)
        if self.h > 0:
            if land_text_y_pos() >= self.y + self.h: break
    land_wordwrap_destroy(w)
    (float ww, wh) = land_wordwrap_extents()
    self.ew = ww
    self.eh = wh

def _span_wordwrap_cb(int a, b, void *data):
    void **p = data
    LandText *text = p[0]
    LandTextSpan *span = p[1]
    char s[b - a + 1]
    strncpy(s, span.text + a, b - a)
    s[b - a] = 0
    land_print_string(s, 0, text.alignment)

def _span_draw(LandText *self, LandWordWrapState *w, LandTextSpan *span):
    land_color_set(span.color)
    if span.font: land_font_set(span.font)
    void *data[] = {self, span}
    land_wordwrap_print_string(w, span.text, _span_wordwrap_cb, data)

def land_text_get_size(LandText *self, float *w, *h):
    int backup_h = self.h
    self.h = 0
    land_text_off()
    land_text_draw(self)
    land_text_on()
    *w = self.ew
    *h = self.eh
    self.h = backup_h
