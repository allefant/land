import global land/land

LandFont *my_font
LandWidgetTheme *theme
LandWidget *desktop

LandWidgetInterface *reddish

def _init(LandRunner *self):
    land_find_data_prefix("data/")
    my_font = land_font_load("galaxy.ttf", 10)
    land_font_set(my_font)

    theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)

    desktop = land_widget_container_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandWidget *window =  land_widget_vbox_new(desktop, 100, 200, 10, 10)
    #LandWidget *mover =
    land_widget_mover_new(window, "move", 0, 0, 100, 20)
    LandWidget *panel = land_widget_panel_new(window, 0, 0, 100, 100)
    reddish = land_widget_copy_interface(land_widget_panel_interface, "reddish")
    panel->vt = reddish
    land_widget_theme_initialize(panel)

def _tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()
    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_clear(0.5, 0.5, 0.5, 1)
    land_widget_draw(desktop)

def _done(LandRunner *self):
    land_widget_unreference(desktop)
    land_widget_theme_destroy(theme)
    land_font_destroy(my_font)

land_standard_example()
