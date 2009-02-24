import global land/land

LandWidget *desktop, *panel
int page = 0

def my_draw(LandWidget *self):
    land_widget_theme_draw(self)
    float x, y, w, h
    land_widget_inner(self, &x, &y, &w, &h)

    land_color(0, 0, 0, 1)
    land_text_pos(x, y)
    LandArray *history = land_widget_get_property(self, "history")
    for int i = 0; i < land_array_count(history); i++:
        land_print("%s", land_array_get_nth(history, i))

def cleanup(void *data):
    LandArray *a = data
    for int i = 0; i < land_array_count(a); i++:
        land_free(land_array_get_nth(a, i))
    land_array_destroy(a)

def my_mouse_tick(LandWidget *self):
    if land_mouse_delta_b():
        LandArray *history = land_widget_get_property(self, "history") 
        land_free(land_array_get_nth(history, 0))
        for int i = 0; i < land_array_count(history) - 1; i++:
            char *str = land_array_get_nth(history, i + 1)
            land_array_replace_nth(history, i, str)
        char str[256]

        uszprintf(str, sizeof str, "mouse_tick %d %d %d %d",
            land_mouse_x(), land_mouse_y(), land_mouse_b(),
            land_mouse_delta_b())
        land_array_replace_nth(history, land_array_count(history) - 1,
            land_strdup(str))

LandWidget *def land_widget_mybox_new(LandWidget *parent):
    static LandWidgetInterface *myvt = NULL
    if not myvt:
        land_widget_box_interface_initialize()
        myvt = land_widget_copy_interface(land_widget_box_interface, "mybox")
        myvt->draw = my_draw
        myvt->mouse_tick = my_mouse_tick

    LandWidget *self = land_widget_box_new(parent, 0, 0, 0, 0) 
    self->vt = myvt
    LandArray *history = land_array_new()
    land_array_add_data(&history, land_strdup("..."))
    land_array_add_data(&history, land_strdup("..."))
    land_array_add_data(&history, land_strdup("..."))
    land_array_add_data(&history, land_strdup("..."))
    land_array_add_data(&history, land_strdup("new"))
    land_widget_set_property(self, "history", history, cleanup)
    return self

def panel_1():
    panel = land_widget_panel_new(desktop, 20, 20, 300, 300)

    LandWidget *vbox = land_widget_vbox_new(panel, 0, 0, 0, 0)
    land_widget_vbox_set_columns(vbox, 2)

    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)

def init(LandRunner *self):
    land_font_load("data/galaxy.ttf", 12)
    LandWidgetTheme *theme = land_widget_theme_new("data/classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(NULL, 10, 10, 620, 460)

    land_widget_reference(desktop)

    panel_1()

def tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape): land_quit()
    if land_closebutton(): land_quit()

    land_widget_tick(desktop)

def draw(LandRunner *self):
    land_clear(0.5, 0.5, 1, 1)
    land_widget_draw(desktop)

def done(LandRunner *self):
    pass

land_begin_shortcut(640, 480, 32, 100,
    LAND_WINDOWED | LAND_OPENGL,
    init, NULL, tick, draw, NULL, done)
