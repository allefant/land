import global land/land

LandWidget *desktop

LandWidget *window
LandWidget *scrolling

def _init(LandRunner *self):
    land_find_data_prefix("data/")

    land_font_load("galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("green.cfg"))
    desktop = land_widget_board_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)
    
    window = land_widget_panel_new(desktop, 50, 50, 350, 350)
    LandWidget *vbox = land_widget_vbox_new(window, 0, 0, 10, 10)
    LandWidget *mover = land_widget_mover_new(vbox, "Scrolling3", 0, 0, 10, 10)
    land_widget_mover_set_target(mover, window)
    scrolling = land_widget_scrolling_new(vbox, 0, 0, 10, 10)
    land_widget_scrolling_autohide(scrolling, 1, 1, 2)
    LandWidget *hbox = land_widget_hbox_new(vbox, 0, 0, 10, 10)
    land_widget_box_new(hbox, 0, 0, 10, 10)
    land_widget_layout_set_shrinking(hbox, 1, 1)
    LandWidget *sizer = land_widget_sizer_new(hbox, 3, 0, 0, 10, 10)
    land_widget_sizer_set_target(sizer, window)
    land_widget_box_new(scrolling, 0, 0, 256, 256)

def _debug(LandWidget *w):
    land_print("* %s: %d %d %d %d %s]", w->vt->name,
        w->box.x, w->box.y, w->box.w, w->box.h, w->hidden ? "H" : ".")
    if land_widget_is(w, LAND_WIDGET_ID_CONTAINER):
        LandList *l = LAND_WIDGET_CONTAINER(w)->children
        land_text_pos(land_text_x_pos() + 10, land_text_y_pos())
        if not land_widget_container_is_empty(w):
            LandListItem *i = l->first
            while i:
                LandWidget *w = i->data
                _debug(w)
                i = i->next
        else:
            land_print("(empty)")
        land_text_pos(land_text_x_pos() - 10, land_text_y_pos())


def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()
    
    if land_key_pressed('u'):
        land_widget_scrolling_update(scrolling)
    
    if land_key_pressed(LandKeyLeft): land_widget_resize(window, -1, 0)
    if land_key_pressed(LandKeyRight): land_widget_resize(window, 1, 0)
    if land_key_pressed(LandKeyUp): land_widget_resize(window, 0, -1)
    if land_key_pressed(LandKeyDown): land_widget_resize(window, 0, 1)

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_widget_draw(desktop)
    
    land_text_pos(300, 10)
    land_color(0, 0, 0, 0.75)
    _debug(desktop)


def _done(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
