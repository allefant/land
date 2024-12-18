import global land/land

LandWidget *desktop
LandWidgetTheme *theme
LandWidgetTheme *classic, *green

static def debug(LandWidget *w):
    print("* %p [%s(%d): %s%s%s%s] %dx%d", w, w->vt->name, w->reference,
        w->no_layout ? "N" : "",
        w->hidden ? "H" : "",
        w->box.flags & GUL_SHRINK_X ? "X" : "",
        w->box.flags & GUL_SHRINK_Y ? "Y" : "",
        w->box.w, w->box.h)
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
            print("(empty)")
        land_text_pos(land_text_x_pos() - 10, land_text_y_pos())

def _init(LandRunner *self):
    land_find_data_prefix("data/")

    land_font_load("galaxy.ttf", 12)

    classic = land_widget_theme_new("classic.cfg")
    green = land_widget_theme_new("green.cfg")
    theme = classic
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)
    
    #LandWidget *scrolling =
    land_widget_scrolling_new(desktop, 20, 20, 600, 440)
    #LandWidget *box = land_widget_box_new(scrolling, 0, 0, 1024, 1024)

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()
    
    if land_key_pressed(' '):
        if theme == green: theme = classic
        else: theme = green
        land_widget_theme_apply(desktop, theme)

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_widget_draw(desktop)
    
    land_text_pos(50, 50)
    debug(desktop)

def _done(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
