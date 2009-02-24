import global land/land

LandFont *my_font
LandWidgetTheme *theme
LandWidget *desktop

LandWidgetInterface *reddish

static def init(LandRunner *self):
    int i

    my_font = land_font_load("data/galaxy.ttf", 10)
    land_font_set(my_font)

    theme = land_widget_theme_new("data/classic.cfg")
    land_widget_theme_set_default(theme)

    desktop = land_widget_container_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandWidget *window =  land_widget_vbox_new(desktop, 100, 200, 10, 10)
    LandWidget *mover = land_widget_mover_new(window, "move", 0, 0, 100, 20)
    LandWidget *panel = land_widget_panel_new(window, 0, 0, 100, 100)
    reddish = land_widget_copy_interface(land_widget_panel_interface, "reddish")
    panel->vt = reddish
    land_widget_theme_initialize(panel)

static def tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()
    land_widget_tick(desktop)

static def draw(LandRunner *self):
    land_clear(0.5, 0.5, 0.5, 1)
    land_widget_draw(desktop)

static def done(LandRunner *self):
    land_widget_unreference(desktop)
    land_widget_theme_destroy(theme)
    land_font_destroy(my_font)

land_begin_shortcut(640, 480, 32, 60, LAND_WINDOWED | LAND_OPENGL, init, NULL, tick,
        draw, NULL, done)

