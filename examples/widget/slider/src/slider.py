import global stdlib
import global string

import global land/land

LandWidget *desktop
LandWidgetTheme *theme

static def init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 12)

    theme = land_widget_theme_new("../../data/classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_panel_new(None, 0, 0, 640, 480)
    land_widget_reference(desktop)

    land_widget_slider_new(desktop, 0, 1, False, None, 0, 0, 0, 0)

static def tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

static def draw(LandRunner *self):
    land_widget_draw(desktop)

static def done(LandRunner *self):
    land_widget_theme_destroy(theme)
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_begin_shortcut(640, 480, 60, LAND_WINDOWED | LAND_OPENGL, init, NULL, tick,
        draw, NULL, done)
