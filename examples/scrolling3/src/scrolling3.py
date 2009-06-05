import global land/land

LandWidget *desktop

static def game_init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("../../data/classic.cfg"))
    desktop = land_widget_board_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)
    
    LandWidget *window = land_widget_panel_new(desktop, 50, 50, 540, 380)
    LandWidget *vbox = land_widget_vbox_new(window, 0, 0, 10, 10)
    LandWidget *mover = land_widget_mover_new(vbox, "Scrolling3", 0, 0, 10, 10)
    land_widget_mover_set_target(mover, window)
    LandWidget *scrolling = land_widget_scrolling_new(vbox, 0, 0, 10, 10)
    land_widget_scrolling_autohide(scrolling, 1, 1, 2)
    LandWidget *hbox = land_widget_hbox_new(vbox, 0, 0, 10, 10)
    LandWidget *box = land_widget_box_new(hbox, 0, 0, 10, 10)
    land_widget_layout_set_shrinking(hbox, 1, 1)
    LandWidget *sizer = land_widget_sizer_new(hbox, 3, 0, 0, 10, 10)
    land_widget_sizer_set_target(sizer, window)
    LandWidget *mainw = land_widget_box_new(scrolling, 0, 0, 256, 256)

static def debug(LandWidget *w):
    land_print("* %s: %d %d %d %d %s]", w->vt->name,
        w->box.x, w->box.y, w->box.w, w->box.h, w->hidden ? "H" : ".")
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


static def game_tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) || land_closebutton():
        land_quit()

    land_widget_tick(desktop)

static def game_draw(LandRunner *self):
    land_widget_draw(desktop)
    
    land_text_pos(300, 50)
    land_color(0, 0, 0, 0.75)
    debug(desktop)


static def game_exit(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

def begin():
    land_init()
    land_set_display_parameters(640, 480, LAND_WINDOWED | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("scrolling", game_init,
        NULL, game_tick, game_draw, NULL, game_exit)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(begin)
