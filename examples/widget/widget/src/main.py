import global land/land

LandFont *my_font
LandWidgetTheme *theme
LandWidget *desktop
LandWidget *scrolling1
LandWidget *outside
LandWidget *list
LandWidget *vbox
LandWidget *button
LandWidget *panel
LandWidget *slider

static def my_draw(LandWidget *self):
    land_color(1, 1, 0, 1)
    int x, y
    x = self->box.x
    for y = self->box.y while y < self->box.y + self->box.h with y += 8:
        land_line(x + 1 + 0.5, y + 0.5, x + self->box.w - 0.5, y)

    land_color(0, 1, 1, 1)
    y = self->box.y
    land_rectangle(x + 0.5, y + 0.5, x + self->box.w - 0.5, y + self->box.h - 0.5)

#static def clicked2(LandWidget *self):
#    # Remove the box when it is clicked. The reference counting will ensure that
#    # it is automatically deleted.
#    land_widget_remove(self)

#static def clicked(LandWidget *self):
#    static int c = 0
#    char str[256]
#    snprintf(str, sizeof str, "Remove me %d", c++)
#    LandWidget *entry = land_widget_button_new(vbox, str, clicked2,
#        0, 0, 1, 1)
#    land_widget_layout_set_expanding(entry, 1, 1)

static def init(LandRunner *self):
    my_font = land_font_load("../../data/galaxy.ttf", 10)
    land_font_set(my_font)

    theme = land_widget_theme_new("../../data/classic.cfg")
    land_widget_theme_set_default(theme)

    desktop = land_widget_container_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandWidget *window =  land_widget_vbox_new(desktop, 100, 200, 10, 10)
    #LandWidget *mover =
    land_widget_mover_new(window, "move", 0, 0, 100, 20)
    LandWidget *panel = land_widget_panel_new(window, 0, 0, 100, 100)
    scrolling1 = land_widget_scrolling_new(panel, 0, 0, 100, 100)
    land_widget_scrolling_autohide(scrolling1, 1, 1, 0)
    LandWidget *empty = land_widget_scrolling_get_empty(scrolling1)
    LandWidget *sizer = land_widget_sizer_new(empty, 3, 0, 0, 10, 10)
    land_widget_layout_set_expanding(sizer, 1, 1)
    LAND_WIDGET_SIZER(sizer)->target = window
    outside = land_widget_box_new(scrolling1, 102, 202, 200, 200)
    land_widget_create_interface(outside, "mine")
    outside->vt->draw = my_draw

    #LandWidget *text = land_widget_text_new(desktop, "Land Widgets Example", 0, 10, 10, 100, 20)

    #button = land_widget_button_new(desktop, "Add entry below", clicked, 10, 30, 2, 2)
    #panel = land_widget_panel_new(desktop, 10, 50, 50, 50)
    #vbox = land_widget_vbox_new(panel, 0, 0, 2, 2)

    #land_widget_text_new(desktop, "Slider", 0, 100, 30, 3, 3)
    #slider = land_widget_slider_new(desktop, -1, 1, False, None, 100, 50, 100, 10)

static def tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

    if land_key(LandKeyLeft):
        land_widget_scrolling_scroll(scrolling1, -1, 0)

    if land_key(LandKeyRight):
        land_widget_scrolling_scroll(scrolling1, 1, 0)

    if land_key(LandKeyUp):
        land_widget_scrolling_scroll(scrolling1, 0, -1)

    if land_key(LandKeyDown):
        land_widget_scrolling_scroll(scrolling1, 0, 1)

    if land_key_pressed('u'):
        _land_gul_layout_updated(scrolling1)

    if land_key_pressed('a'):
        land_widget_scrolling_autobars(scrolling1)

    land_widget_tick(desktop)

static def debug(LandWidget *w):
    land_print("* %p [%s: %s%s%s%s]", w, w->vt->name,
        w->no_layout ? "N" : "",
        w->hidden ? "H" : "",
        w->box.flags & GUL_SHRINK_X ? "X" : "",
        w->box.flags & GUL_SHRINK_Y ? "Y" : "")
    if land_widget_is(w, LAND_WIDGET_ID_CONTAINER):
        LandList *l = LAND_WIDGET_CONTAINER(w)->children
        land_text_pos(land_text_x_pos() + 10, land_text_y_pos())
        if not land_widget_container_is_empty(w):
            LandListItem *i = l->first
            while i:
                LandWidget *w = i->data
                debug(w)
                i = i->next
        else:
            land_print("(empty)")
        land_text_pos(land_text_x_pos() - 10, land_text_y_pos())

static def draw(LandRunner *self):
    land_clear(0.5, 0.5, 0.5, 1)
    land_widget_draw(desktop)

    land_text_pos(300, 50)
    land_color(0, 0, 0, 0.75)
    debug(desktop)

static def done(LandRunner *self):
    land_widget_unreference(desktop)
    land_widget_theme_destroy(theme)
    land_font_destroy(my_font)

land_begin_shortcut(640, 480, 60, LAND_WINDOWED | LAND_OPENGL, init, NULL, tick,
        draw, NULL, done)

