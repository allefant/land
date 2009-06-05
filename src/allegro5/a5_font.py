import land/font
static import global allegro5/allegro5, allegro5/a5_font
static import global allegro5/a5_ttf

static class LandFontPlatform:
    LandFont super
    ALLEGRO_FONT *a5

def platform_font_init():
    al_init_font_addon()
    al_init_ttf_addon()

def platform_font_exit():
    pass

LandFont *def platform_font_load(char const *filename, float size):
    land_log_message("Loading font %s..", filename);
    LandFontPlatform *self;
    land_alloc(self);

    self->a5 = al_load_font(filename, size, 0)

    land_log_message_nostamp("%s.\n", self->a5 ? "success" : "failure")
    LandFont *super = (void *)self
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
    al_set_blender(ALLEGRO_ALPHA, ALLEGRO_INVERSE_ALPHA, al_map_rgba_f(
        d->color_r, d->color_g, d->color_b, d->color_a))

    if alignment == 2:
        al_draw_text(self->a5, x, y, ALLEGRO_ALIGN_CENTRE, str)
    elif alignment == 1:
        al_draw_text(self->a5, x, y, ALLEGRO_ALIGN_RIGHT, str)
    else:
        al_draw_text(self->a5, x, y, 0, str)
    
    al_restore_state(&state)
