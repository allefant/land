import land/font
static import global allegro5/allegro5, allegro5/allegro_font
static import global allegro5/allegro_ttf
static import land/allegro5/a5_display

static class LandFontPlatform:
    LandFont super
    ALLEGRO_FONT *a5
    LandHash *glyph_advance_cache

def platform_font_init():
    al_init_font_addon()
    al_init_ttf_addon()

def platform_font_exit():
    pass

def platform_font_load(char const *filename, float size) -> LandFont *:
    land_log_message("Loading font %s..", filename)
    LandFontPlatform *self
    land_alloc(self)

    self.a5 = al_load_font(filename, size, 0)

    land_log_message_nostamp("%s.\n", self.a5 ? "success" : "failure")
    LandFont *super = (void *)self
    if self.a5:
        super->size = al_get_font_line_height(self.a5)
        super.flags |= LAND_LOADED
    super.xscaling = 1.0
    super.yscaling = 1.0
    return super

def platform_font_from_image(LandImage *image, int n_ranges,
    int *ranges) -> LandFont *:
    LandFontPlatform *self
    LandImagePlatform *i = (void *)image
    land_alloc(self)

    self.a5 = al_grab_font_from_bitmap(i->a5, n_ranges, ranges);
    LandFont *super = (void *)self
    if self.a5:
        super->size = al_get_font_line_height(self.a5)
    super.xscaling = 1.0
    super.yscaling = 1.0
    return super

def platform_text_width(LandFontState *lfs, str text) -> float:
    LandFont *super = lfs->font
    LandFontPlatform *self = (void *)super

    if not self.a5: return 0

    double xscaling = super.xscaling
    #return al_get_text_width(self.a5, text) * xscaling

    char key[9]
    int w = 0
    int prev = ALLEGRO_NO_KERNING
    char *p = (char *)text
    while True:
        int codepoint = land_utf8_char(&p)
        # -1 is not encoded into the string properly so we use 31
        int prev2 = prev
        if prev2 == ALLEGRO_NO_KERNING:
            prev2 = 31
        int n = land_utf8_encode(prev2, key)
        n += land_utf8_encode(codepoint, key + n)
        key[n] = 0
        if not self.glyph_advance_cache:
            self.glyph_advance_cache = land_hash_new()
        int x = 0
        int *wp = land_hash_get(self.glyph_advance_cache, key)
        if wp:
            x = *wp
        else:
            x = al_get_glyph_advance(self.a5, prev, codepoint)
            land_alloc(wp)
            *wp = x
            land_hash_insert(self.glyph_advance_cache, key, wp)
        w += x
        if codepoint == 0:
            break
        prev = codepoint

    return w * xscaling
    
    """
    LandFont *current = land_font_state.font
    if current.string_width_cache:
        float *wp = land_hash_get(current.string_width_cache, s)
        if wp:
            return *wp
    int onoff = land_font_state.off
    land_font_state.off = 1
    platform_font_print(land_font_state, s, 0)
    land_font_state.off = onoff
    if not current.string_width_cache:
        current.string_width_cache = land_hash_new()
    float *wp = land_calloc(sizeof *wp)
    *wp = land_font_state.w
    # fixme: we need something better, but huge cache here is even slower
    # then recalculating every time
    if land_hash_count(current.string_width_cache) < 1000:
        land_hash_insert(current.string_width_cache, s, wp)
    return land_font_state.w
    """

def platform_font_print(LandFontState *lfs,
    char const *str, int alignment):
    LandFont *super = lfs->font
    LandFontPlatform *self = (void *)super

    if not self.a5: return

    double xscaling = super.xscaling
    double yscaling = super.yscaling
    double rotation = super.rotation

    float x = lfs->x_pos
    float y = lfs->y = lfs->y_pos
    lfs->w = al_get_text_width(self.a5, str) * xscaling
    lfs->h = al_get_font_line_height(self.a5) * yscaling

    if lfs.confine_hor:
        float left = x
        if alignment & LandAlignCenter:
            left -= lfs->w / 2
        if alignment & LandAlignRight:
            left -= lfs->w
        if left < lfs.confine_x:
            x += lfs.confine_x - left
        if left + lfs.w > lfs.confine_x + lfs.confine_w:
            x -= left + lfs.w - (lfs.confine_x + lfs.confine_w)

    lfs.x = x

    if lfs->off: return

    bool transformed = False
    if xscaling != 1 or yscaling != 1 or rotation != 0:
        transformed = True
        land_push_transform()
        land_translate(x, y)
        land_scale(xscaling, yscaling)
        land_rotate(rotation)
        land_translate(-x, -y)

    ALLEGRO_STATE state
    al_store_state(&state, ALLEGRO_STATE_BLENDER)
    LandDisplay *d = _land_active_display;
    al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_INVERSE_ALPHA)
    
    land_a5_display_check_transform()
    
    ALLEGRO_COLOR c = al_map_rgba_f(d->color_r, d->color_g, d->color_b, d->color_a)

    int a = ALLEGRO_ALIGN_INTEGER

    if alignment & LandAlignMiddle:
        # Note: y itself is affected by the transformation we set above.
        # lfs.h already was multipled by yscaling. So we need to
        # unmultiply or it would be applied twice.
        y -= lfs.h / 2 / yscaling
        lfs->y -= lfs.h / 2 / yscaling
    elif alignment & LandAlignBottom:
        y -= lfs->h / yscaling
        lfs->y -= lfs->h / yscaling

    if alignment & LandAlignAdjust:
        al_draw_justified_text(self.a5, c, x, x + lfs->adjust_width, y,
            lfs->adjust_width * 0.5,
            a | ALLEGRO_ALIGN_CENTRE, str)
    elif alignment & LandAlignCenter:
        al_draw_text(self.a5, c, x, y, a | ALLEGRO_ALIGN_CENTRE, str)
        lfs.x -= lfs.w / 2
    elif alignment & LandAlignRight:
        al_draw_text(self.a5, c, x, y, a | ALLEGRO_ALIGN_RIGHT, str)
        lfs->x -= lfs->w
    else:
        al_draw_text(self.a5, c, x, y, a, str)
    
    al_restore_state(&state)

    if transformed:
        land_pop_transform()

def platform_font_new() -> LandFont *:
    return None

def platform_font_destroy(LandFont *super):
    LandFontPlatform *self = (void *)super
    al_destroy_font(self.a5)
    land_free(self)

