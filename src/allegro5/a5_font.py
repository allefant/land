import land/font
static import global allegro5/allegro5, allegro5/allegro_font
static import global allegro5/allegro_ttf
static import land/allegro5/a5_display

static class LandFontPlatform:
    LandFont super
    ALLEGRO_FONT *a5

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

def platform_font_print(LandFontState *lfs,
    char const *str, int alignment):
    LandFont *super = lfs->font
    LandFontPlatform *self = (void *)super

    if not self.a5: return

    double xscaling = super.xscaling
    double yscaling = super.yscaling

    float x = lfs->x = lfs->x_pos
    float y = lfs->y = lfs->y_pos
    lfs->w = al_get_text_width(self.a5, str) * xscaling
    lfs->h = al_get_font_line_height(self.a5) * yscaling

    if lfs->off: return

    if xscaling != 1 or yscaling != 1:
        land_push_transform()
        land_translate(x, y)
        land_scale(xscaling, yscaling)
        land_translate(-x, -y)

    ALLEGRO_STATE state
    al_store_state(&state, ALLEGRO_STATE_BLENDER)
    LandDisplay *d = _land_active_display;
    al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_INVERSE_ALPHA)
    
    land_a5_display_check_transform()
    
    ALLEGRO_COLOR c = al_map_rgba_f(d->color_r, d->color_g, d->color_b, d->color_a)

    int a = ALLEGRO_ALIGN_INTEGER

    if alignment & LandAlignMiddle:
        y -= lfs->h / 2 / yscaling
        lfs->y -= lfs->h / 2 / yscaling
    elif alignment & LandAlignBottom:
        y -= lfs->h
        lfs->y -= lfs->h

    if alignment & LandAlignAdjust:
        al_draw_justified_text(self.a5, c, x, x + lfs->adjust_width, y,
            lfs->adjust_width * 0.5,
            a | ALLEGRO_ALIGN_CENTRE, str)
    elif alignment & LandAlignCenter:
        al_draw_text(self.a5, c, x, y, a | ALLEGRO_ALIGN_CENTRE, str)
    elif alignment & LandAlignRight:
        al_draw_text(self.a5, c, x, y, a | ALLEGRO_ALIGN_RIGHT, str)
        lfs->x -= lfs->w
    else:
        al_draw_text(self.a5, c, x, y, a, str)
    
    al_restore_state(&state)

    if xscaling != 1 or yscaling != 1:
        land_pop_transform()

def platform_font_new() -> LandFont *:
    return None

def platform_font_destroy(LandFont *super):
    LandFontPlatform *self = (void *)super
    al_destroy_font(self.a5)
    land_free(self)
