import global allegro, fudgefont
import ../array, ../font, ../log

class LandFontAllegro:
    struct LandFont super
    FONT *font

macro LAND_FONT_ALLEGRO(_x_) ((LandFontAllegro *)_x_)

static LandFontInterface *vtable

LandFont *def land_font_allegro_load(char const *filename, int size):
    land_log_message("land_font_allegr_load %s %d..", filename, size)
    LandFontAllegro *self
    land_alloc(self)
    PALETTE pal
    self->font = load_font(filename, pal, &size)
    select_palette(pal)
    
    # There are 3 possibilities:
    #     * It was a normal, paletted Allegro font, from an 8-bit bitmap.
    #     * It was an alpha font from a 32-bit bitmap.
    #     * It was a TTF and now is 8-bit.

    self->super.size = text_height(self->font)
    self->super.vt = vtable
    land_log_message_nostamp(self->font ? "success\n" : "failure\n"); 
    return &self->super

def land_font_allegro_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement):
    LandFontAllegro *self = LAND_FONT_ALLEGRO(state->font)
    if !self: return

    int w = text_length(self->font, text)
    int h = state->font->size

    float x = state->x_pos
    float y = state->y_pos
    if alignement == 1: # right 
        x -= w
    elif alignement == 2: # center 
        x -= w / 2
    if !state->off:
        int r = display->color_r * 255
        int g = display->color_g * 255
        int b = display->color_b * 255
        # FIXME: This makes only sense for paletted fonts on black background..
        # TODO: properly support different kinds of fonts, ideally with
        # anti aliasing
        # If FudgeFont would output 32-bit glyphs, we couldn't recolor the
        # palette. So there certainly is no easy solution.
        fudgefont_color_range(0, 0, 0, r, g, b)
        textout_ex(LAND_DISPLAY_IMAGE(display)->bitmap, self->font, text, x, y,
            -1, -1)
        if bitmap_color_depth(LAND_DISPLAY_IMAGE(display)->bitmap) == 32:
            # FIXME: This is really hackish.. but if the target is 32bit,
            # textout will kill the alpha channel, so we patch it back to
            # one here.
            int i, j
            for j = 0; j < h; j++:
                for i = 0; i < w; i++:
                    int c = getpixel(LAND_DISPLAY_IMAGE(display)->bitmap, x + i, y + j)
                    int red = getr(c)
                    int green = getg(c)
                    int blue = getb(c)
                    c = makeacol(red, green, blue, 255)
                    putpixel(LAND_DISPLAY_IMAGE(display)->bitmap, x + i, y + j, c)

    state->x = x
    state->y = y
    state->w = w
    state->h = h

def land_font_allegro_destroy(LandFont *self):
    LandFontAllegro *a = (LandFontAllegro *)self
    destroy_font(a->font)
    land_free(a)

def land_font_allegro_init():
    land_log_message("land_font_allegro_init\n");   
    land_alloc(vtable)
    vtable->print = land_font_allegro_print
    vtable->destroy = land_font_allegro_destroy

def land_font_allegro_exit():
    land_log_message("land_font_allegro_exit\n");   
    land_free(vtable)
