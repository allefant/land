import global stdlib
import global string

import global land/land

LandWidget *desktop
LandWidgetTheme *theme

def _init(LandRunner *self):
    #land_font_load_zoom("galaxy.ttf", 1)
    land_font_load_zoom("NotoColorEmoji.ttf", 1)
    int W = land_display_width()
    int H = land_display_height()
    theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(NULL, 2, 2, W - 4, H - 4)
    land_widget_reference(desktop)
    land_widget_text_new(desktop, "here be dragons 🐉🦕🦖", 0, W / 2, H / 2, 0, 0)

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_widget_draw(desktop)

def _done(LandRunner *self):
    land_widget_theme_destroy(theme)
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
