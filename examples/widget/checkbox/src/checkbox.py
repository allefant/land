import global stdlib
import global string

import global land.land

LandWidget *desktop
LandWidgetTheme *theme

def _init(LandRunner *self):
    land_find_data_prefix("data/")

    land_font_load("DejaVuSans.ttf", 12)

    theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(None, 0, 0, 640, 480)
    land_widget_reference(desktop)

    land_widget_button_new(desktop, "A", None, 0, 0, 200, 20)
    land_widget_button_new(desktop, "B", None, 0, 20, 200, 20)
    land_widget_checkbox_new(desktop, "✓", " ", "checkbox", 0, 40, 200, 20)

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_widget_draw(desktop)

def _done(LandRunner *self):
    land_widget_theme_destroy(theme)
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
