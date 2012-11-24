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

LandFont *def platform_font_load(char const *filename, float size):
    land_log_message("Loading font %s..", filename)
    LandFontPlatform *self
    land_alloc(self)

    self->a5 = al_load_font(filename, size, 0)

    land_log_message_nostamp("%s.\n", self->a5 ? "success" : "failure")
    LandFont *super = (void *)self
    if self->a5:
        super->size = al_get_font_line_height(self->a5)
    return super

LandFont *def platform_font_from_image(LandImage *image, int n_ranges,
    int *ranges):
    LandFontPlatform *self
    LandImagePlatform *i = (void *)image
    land_alloc(self)

    self->a5 = al_grab_font_from_bitmap(i->a5, n_ranges, ranges);
    LandFont *super = (void *)self
    if self->a5:
        super->size = al_get_font_line_height(self->a5)
    return super

def platform_font_print(LandFontState *lfs,
    char const *str, int alignment):
    LandFont *super = lfs->font
    LandFontPlatform *self = (void *)super

    if not self->a5: return

    float x = lfs->x = lfs->x_pos
    float y = lfs->y = lfs->y_pos
    lfs->w = al_get_text_width(self->a5, str)
    lfs->h = al_get_font_line_height(self->a5)

    if lfs->off: return

    ALLEGRO_STATE state
    al_store_state(&state, ALLEGRO_STATE_BLENDER)
    LandDisplay *d = _land_active_display;
    al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_INVERSE_ALPHA)
    
    land_a5_display_check_transform()
    
    ALLEGRO_COLOR c = al_map_rgba_f(d->color_r, d->color_g, d->color_b, d->color_a)

    if alignment == LandAlignAdjust:
        al_draw_justified_text(self->a5, c, x, x + lfs->adjust_width, y,
            lfs->adjust_width * 0.5,
            ALLEGRO_ALIGN_CENTRE, str)
    elif alignment == LandAlignCenter:
        al_draw_text(self->a5, c, x, y, ALLEGRO_ALIGN_CENTRE, str)
    elif alignment == LandAlignRight:
        al_draw_text(self->a5, c, x, y, ALLEGRO_ALIGN_RIGHT, str)
    else:
        al_draw_text(self->a5, c, x, y, 0, str)
    
    al_restore_state(&state)

LandFont *def platform_font_new():
    return None

def platform_font_destroy(LandFont *super):
    LandFontPlatform *self = (void *)super
    al_destroy_font(self->a5)
    land_free(self)
