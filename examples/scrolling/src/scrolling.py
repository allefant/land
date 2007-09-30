import global land/land

LandWidget *desktop

static def game_init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("../../data/classic.cfg"))
    desktop = land_widget_board_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)
    
    LandWidget *scrolling = land_widget_scrolling_new(desktop, 50, 50, 540, 380)
    LandWidget *box = land_widget_box_new(scrolling, 0, 0, 1024, 1024)

static def game_tick(LandRunner *self):
    if land_key_pressed(KEY_ESC) || land_closebutton():
        land_quit()

    land_widget_tick(desktop)

static def game_draw(LandRunner *self):
    land_widget_draw(desktop)

static def game_exit(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

def begin():
    land_init()
    land_set_display_parameters(640, 480, 32, 100, LAND_WINDOWED | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("scrolling", game_init,
        NULL, game_tick, game_draw, NULL, game_exit)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_main()

land_use_main(begin)
