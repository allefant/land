import global allegro, fudgefont
import ../array, ../font, ../log

# To be able to write out the range->texture mapping in the logs, we include
# below 2 internal structs from AllegroGL. This is likely to break, but can
# simply be removed.

# FIXME: HACK
static class AGL_GLYPH:
    int glyph_num
    int x, y, w, h
    int offset_x, offset_y, offset_w, offset_h

# FIXME: HACK
static class FONT_AGL_DATA:
    int type
    int start, end
    int is_free_chunk

    float scale
    GLint format

    void *data
    AGL_GLYPH *glyph_coords
    GLuint list_base
    GLuint texture

    FONT_AGL_DATA *next

    int has_alpha

class LandFontAllegrogl:
    struct LandFont super
    FONT *font
    char *filename
    float size

macro LAND_FONT_ALLEGROGL(_x_) ((LandFontAllegrogl *)_x_)

static import allegrogl/font, global allegro/internal/aintern
static import data

static LandFontInterface *vtable
static LandList *fonts

# Simple font implementation bypassing AllegroGL. Probably we should switch
# to using this one, and ditch the AllegroGL one, which is way too
# complicated, and doesn't even support kerning.

# FIXME
#static def grab(LandFontAllegrogl *self):
#    LandImage *image = self->image
#    BITMAP *bmp = image->memory_cache
#    int w = land_image_width(image)
#    int h = land_image_height(image)
#    int x, y
#    int b = getpixel(bmp, 0, 0)
#    int i = 32
#    for y = 1; y < h; y++:
#        for x = 1; x < w; x++:
#            int c = getpixel(bmp, x, y)
#            int c1 = getpixel(bmp, x - 1, y)
#            int c2 = getpixel(bmp, x - 1, y - 1)
#            int c3 = getpixel(bmp, x, y - 1)
#            if c1 == b && c2 == b && c3 == b && c != b:
#                self->x[i] = x
#                self->y[i] = y
#                self->w[i] = 0
#                self->h[i] = 0
#                while (getpixel(bmp, x + self->w[i], y) != b):
#                    self->w[i] += 1
#
#                while (getpixel(bmp, x, y + self->h[i]) != b):
#                    self->h[i] += 1
#
#                land_log_message(" %d: %d / %d: %d x %d\n", i,
#                    self->x[i], self->y[i],
#                    self->w[i], self->h[i])
#                i++
#
#    for y = 0; y < h; y++:
#        for x = 0; x < w; x++:
#            if (getpixel(bmp, x, y) == b)
#                putpixel(bmp, x, y, 0)
#
#
#    land_image_prepare(self->image)
#
# FIXME
#static LandFont *def __land_font_allegrogl_load(char const *filename, float size):
#    land_log_message("land_font_allegrogl_load %s %.1f\n", filename, size)
#    LandFontAllegrogl *self
#    land_alloc(self)
#
#    self->image = land_image_load(filename)
#    
#    grab(self)
#    
#    self->super.size = self->h[32]
#    self->super.vt = vtable
#    if self->image:
#        land_log_message(" %d success\n", self->h[32])
#
#    else
#        land_log_message(" failure\n")
#
#    return &self->super

# FIXME
#static def __land_font_allegrogl_print(LandFontState *state, LandDisplay *display,
#    char const *text, int alignement):
#    LandFontAllegrogl *self = LAND_FONT_ALLEGROGL(state->font)
#    if !self:
#        return
#
#    int l = ustrlen(text)
#    int i
#    int w = 0
#    for i = 0; i < l; i++:
#        w += self->w[(int)text[i]]
#
#    int h = state->font->size
#
#    float x = state->x_pos
#    float y = state->y_pos
#    if (alignement == 1) /* right */
#        x -= w
#    else if (alignement == 2) /* center */
#        x -= w / 2.0
#    if !state->off:
#        float ox = x
#        float r, g, b, a
#        land_get_color(&r, &g, &b, &a)
#        for i = 0; i < l; i++:
#            int glyph = text[i]
#            land_image_clip(self->image, self->x[glyph] - 1, self->y[glyph] - 1,
#                self->x[glyph] + self->w[glyph] + 1,
#                self->y[glyph] + self->h[glyph] + 1)
            # Attempt to make small text not get blurry - doesn't seem to
            # work reliably.

#            ox = (int)ox
#            y = (int)y
#            land_image_draw_tinted(self->image, ox - self->x[glyph],
#                y - self->y[glyph], r, g, b, a)
#            ox += self->w[glyph]


#   state->x = x
#    state->y = y
#    state->w = w
#    state->h = h

       
static def convert(LandFontAllegrogl *self, FONT *af, PALETTE pal):
    int alpha = 0
    int paletted = 0
    if is_color_font(af):
        FONT_COLOR_DATA *fcd = af->data
        if bitmap_color_depth(fcd->bitmaps[0]) == 32:
            alpha = 1
        else:
            paletted = 1
            fudgefont_color_range(0, 0, 0, 255, 255, 255)
    else:
        select_palette(pal)
        paletted = 1

    if alpha:
        make_trans_font(af)
    land_log_message(" using %salpha, using %spalette\n",
        alpha ? "" : "no ", paletted ? "" : "no ")

    self->font = allegro_gl_convert_allegro_font_ex(af,
        AGL_FONT_TYPE_TEXTURED, -1, paletted ? GL_ALPHA : GL_RGBA8)
    self->super.size = text_height(self->font)
    self->super.vt = vtable
    if self->font:
        land_log_message(" font of height %d loaded\n", text_height(af))
        #int n = allegro_gl_list_font_textures(self->font, NULL, 0)
        #GLuint ids[n]
        #allegro_gl_list_font_textures(self->font, ids, n)
        #for int i = 0; i < n; i++:
        FONT_AGL_DATA *data = self->font->data
        while data:
            int w, h, r, g, b, a
            glBindTexture(GL_TEXTURE_2D, data->texture)
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w)
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h)
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_RED_SIZE, &r)
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_GREEN_SIZE, &g)
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_BLUE_SIZE, &b)
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_ALPHA_SIZE, &a)
            land_log_message(" texture %d: %d x %d x (%d%d%d%d) [%d..%d]\n",
                data->texture, w, h, r, g, b, a, data->start, data->end)
            data = data->next
    else:
        land_log_message_nostamp("failure\n")

extern LandDataFile *_land_datafile

LandFont *def land_font_allegrogl_new(LandDisplay *super):
    LandFontAllegrogl *self
    land_alloc(self)
    land_add_list_data(&fonts, self)
    return &self->super

def land_font_allegrogl_destroy(LandDisplay *d, LandFont *self):
    LandFontAllegrogl *a = (LandFontAllegrogl *)self
    destroy_font(a->font)
    if a->filename: land_free(a->filename)
    land_remove_list_data(&fonts, self)
    land_free(a)

def land_font_allegrogl_del(LandDisplay *d, LandFont *self):
    land_font_allegrogl_destroy(d, self)

static def reload(LandFontAllegrogl *self):
    int data = self->size
    PALETTE pal
    FONT *temp = None
    if _land_datafile:
        # FIXME: check for ttf extension, in which case fudgefont should support
        # loading from memory instead of a file.
        LandImage *image = land_image_load(self->filename)
        temp = grab_font_from_bitmap(image->bitmap)
        land_image_destroy(image)
        
    if not temp:
        temp = load_font(self->filename, pal, &data)
    convert(self, temp, pal)
    destroy_font(temp)

LandFont *def land_font_allegrogl_load(char const *filename, float size):
    land_log_message("land_font_allegrogl_load %s %.1f\n", filename, size)
    LandFontAllegrogl *self = (void *)land_display_new_font()
    self->filename = land_strdup(filename)
    self->size = size
    reload(self)

    return &self->super

LandFont *def land_font_allegrogl_default():
    LandFontAllegrogl *self = (void *)land_display_new_font()
    land_log_message("land_font_allegrogl_default\n")
    PALETTE pal
    memcpy(pal, default_palette, sizeof pal)
    convert(self, font, pal)
    return &self->super

def land_font_allegrogl_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement):
    LandFontAllegrogl *self = LAND_FONT_ALLEGROGL(state->font)
    if not self:
        return

    int w = text_length(self->font, text)
    int h = state->font->size

    float x = state->x_pos
    float y = state->y_pos
    if alignement == 1: # right
        x -= w
    elif alignement == 2: # center
        x -= w / 2.0
    # To avoid extra anti-aliasing "smear" effect with default viewport.
    x = (int)x
    y = (int)y
    if !state->off:
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        allegro_gl_printf_ex(self->font, x, y, 0, "%s", text)

    state->x = x
    state->y = y
    state->w = w
    state->h = h

float def land_font_allegrogl_text_length(LandFontState *state,
    char const *text):
    LandFontAllegrogl *self = LAND_FONT_ALLEGROGL(state->font)
    return text_length(self->font, text)

def land_font_allegrogl_unupload(void):
    if not fonts: return
    LandListItem *i
    land_log_message("Un-uploading all fonts..\n")
    for i = fonts->first; i; i = i->next:
        LandFontAllegrogl *f = i->data
        destroy_font(f->font)
        f->font = NULL

def land_font_allegrogl_reupload(void):
    if not fonts: return
    LandListItem *i
    land_log_message("Re-uploading all fonts..\n")

    for i = fonts->first; i; i = i->next:
        LandFontAllegrogl *f = i->data
        if not f->font:
            reload(f)

def land_font_allegrogl_init(void):
    land_log_message("land_font_allegrogl_init\n")
    land_alloc(vtable)
    vtable->print = land_font_allegrogl_print
    vtable->destroy = land_font_allegrogl_destroy
    vtable->length = land_font_allegrogl_text_length
    fonts = land_list_new()

def land_font_allegrogl_exit(void):
    land_log_message("land_font_allegrogl_exit\n")
    land_list_destroy(fonts)
    land_free(vtable)
