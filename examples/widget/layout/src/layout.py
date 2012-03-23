import global land/land

LandFont *font
LandWidgetTheme *theme, *classic, *green
LandWidget *desktop, *panel
int page = 0

extern int gul_debug;

def my_draw(LandWidget *self):
    land_widget_theme_draw(self)
    float x, y, w, h
    land_widget_inner(self, &x, &y, &w, &h)
    land_color(0, 0, 1, 0.2)
    land_rectangle(x + 0.5, y + 0.5, x + w - 0.5, y + h - 0.5)
    land_text_pos(x, y)
    land_color(1, 0, 0, 0.5)
    land_line(x + 0.5, y + h / 2, x + w - 0.5, y + h / 2)
    land_line(x + w / 2, y + 0.5, x + w / 2, y + h - 0.5)
    land_color(0, 0, 0, 1)
    land_print("%d x %d", self->box.w, self->box.h)

LandWidget * def land_widget_mybox_new(LandWidget *parent):
    static LandWidgetInterface *myvt = NULL
    if not myvt:
        land_widget_box_interface_initialize()
        myvt = land_widget_copy_interface(land_widget_box_interface, "mybox")
        myvt->draw = my_draw

    LandWidget *self = land_widget_box_new(parent, 0, 0, 0, 0) 
    self->vt = myvt
    return self

def panel_0():
    panel = land_widget_panel_new(desktop, 30, 30, 300, 300)

    LandWidget *vbox = land_widget_vbox_new(panel, 0, 0, 0, 0)
    land_widget_mybox_new(vbox)

def panel_1():
    panel = land_widget_panel_new(desktop, 30, 30, 300, 300)

    LandWidget *vbox = land_widget_vbox_new(panel, 0, 0, 0, 0)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)

def panel_2():
    panel = land_widget_panel_new(desktop, 30, 30, 300, 300)

    LandWidget *hbox = land_widget_hbox_new(panel, 0, 0, 0, 0)
    land_widget_mybox_new(hbox)
    land_widget_mybox_new(hbox)

def panel_3():
    panel = land_widget_panel_new(desktop, 30, 30, 300, 300)

    LandWidget *vbox = land_widget_vbox_new(panel, 0, 0, 0, 0)
    land_widget_vbox_set_columns(vbox, 2)

    LandWidget *hbox = land_widget_hbox_new(vbox, 0, 0, 0, 0)
    land_widget_mybox_new(hbox)
    land_widget_mybox_new(hbox)
    land_widget_mybox_new(hbox)

    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)
    land_widget_mybox_new(vbox)

def panel_4():
    panel = land_widget_panel_new(desktop, 30, 30, 300, 300)

    LandWidget *hbox = land_widget_hbox_new(panel, 0, 0, 0, 0)

    # left column
    land_widget_mybox_new(hbox)

    #middle column
    LandWidget *vbox = land_widget_vbox_new(hbox, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(vbox, 1, 0)
    land_widget_mybox_new(vbox)
    LandWidget *box = land_widget_mybox_new(vbox)
    land_widget_layout_set_minimum_size(box, 50, 50)
    land_widget_layout_set_shrinking(box, 1, 1)
    land_widget_mybox_new(vbox)

    # right column
    land_widget_mybox_new(hbox)

def panel_5():
    panel = land_widget_panel_new(desktop, 30, 30, 300, 300)

    LandWidget *container = land_widget_container_new(panel, 0, 0, 0, 0)
    land_widget_layout_enable(container)

    LandWidget *box1 = land_widget_mybox_new(container)
    LandWidget *box2 = land_widget_mybox_new(container)
    LandWidget *box3 = land_widget_mybox_new(container)
    LandWidget *box4 = land_widget_mybox_new(container)
    LandWidget *box5 = land_widget_mybox_new(container)

    land_widget_layout_set_grid(container, 3, 3)

    land_widget_layout_set_grid_position(box1, 0, 0)
    land_widget_layout_set_grid_extra(box1, 1, 0)
    land_widget_layout_set_grid_position(box2, 2, 0)
    land_widget_layout_set_grid_extra(box2, 0, 1)
    land_widget_layout_set_grid_position(box3, 1, 2)
    land_widget_layout_set_grid_extra(box3, 1, 0)
    land_widget_layout_set_grid_position(box4, 0, 1)
    land_widget_layout_set_grid_extra(box4, 0, 1)
    land_widget_layout_set_grid_position(box5, 1, 1)

def init(LandRunner *self):
    gul_debug = 0;
    font = land_font_load("../../data/galaxy.ttf", 12)
    theme = classic = land_widget_theme_new("../../data/classic.cfg")
    green = land_widget_theme_new("../../data/green.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(NULL, 20, 20, 600, 440)

    land_widget_reference(desktop)

    panel_0()

def tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape): land_quit()
    if land_closebutton(): land_quit()

    if land_key_pressed(' '):
        if panel: land_widget_remove(panel)
        page++
        if page == 1: panel_1()
        elif page == 2: panel_2()
        elif page == 3: panel_3()
        elif page == 4: panel_4()
        elif page == 5: panel_5()
        else:
            page = 0
            panel_0()
    if land_key_pressed(13):
        if theme == classic:
            theme = green
        else:
            theme = classic
        land_widget_theme_apply(desktop, theme)

def draw(LandRunner *self):
    land_clear(0.5, 0.5, 1, 1)
    land_widget_draw(desktop)

    land_text_pos(0, 0)
    land_color(1, 1, 1, 1)
    land_print("Press Space for next dialog")
    land_text_pos(0, land_display_height() - land_text_height())
    land_print("Dialog is inside a 300x300 pixel square")

def done(LandRunner *self):
    land_widget_unreference(desktop)
    land_widget_theme_destroy(classic)
    land_widget_theme_destroy(green)
    land_font_destroy(font)

land_begin_shortcut(640, 480, 100,
    LAND_WINDOWED | LAND_OPENGL,
    init, NULL, tick, draw, NULL, done)
