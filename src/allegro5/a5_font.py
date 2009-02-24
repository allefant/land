import land/font
static import global allegro5/allegro5, allegro5/a5_font

static class LandFontPlatform:
    LandFont super
    ALLEGRO_FONT *a5

def platform_font_init():
    pass

def platform_font_exit():
    pass

LandFont *def platform_font_load(char const *filename, float size):
    pass

def platform_font_print(LandFontState *land_font_state,
    char const *str, int alignement):
    pass
    
