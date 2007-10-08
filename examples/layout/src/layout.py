import global land

LandWidget *desktop, *panel
int page = 0

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

def panel_1():
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

def panel_2():
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

def panel_3():
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
    land_font_load("../../data/galaxy.ttf", 12)
    LandWidgetTheme *theme = land_widget_theme_new("../../data/classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(NULL, 20, 20, 600, 440)

    land_widget_reference(desktop)

    panel_1()

def tick(LandRunner *self):
    if land_key_pressed(KEY_ESC): land_quit()
    if land_closebutton(): land_quit()

    if land_key_pressed(KEY_SPACE):
        if panel: land_widget_remove(panel)
        page++
        if page == 1: panel_2()
        elif page == 2: panel_3()
        else:
            page = 0
            panel_1()

def draw(LandRunner *self):
    land_clear(0.5, 0.5, 1, 1)
    land_widget_draw(desktop)

    land_text_pos(0, 0)
    land_color(1, 1, 1, 1)
    land_print("Press Space for next dialog")
    land_text_pos(0, land_display_height() - land_text_height())
    land_print("Dialog is inside a 300x300 pixel square")

def done(LandRunner *self):
    pass

land_begin_shortcut(640, 480, 32, 100,
    LAND_WINDOWED | LAND_OPENGL,
    init, NULL, tick, draw, NULL, done)
