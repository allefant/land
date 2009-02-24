import global land/land

LandWidget *desktop
LandWidgetTheme *theme
LandWidget *scrolling, *contents

def create_dialog():
    land_font_load("../../data/galaxy.ttf", 12)
    theme = land_widget_theme_new("../../data/classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(None, 0, 0, 640, 480)
    land_widget_reference(desktop)

    char *text = land_read_text("../../data/GPL-2")

    LandWidget *window =  land_widget_vbox_new(desktop, 100, 100, 4, 4)
    LandWidget *mover = land_widget_mover_new(window, "GPL-2", 0, 0, 4, 4)

    scrolling = land_widget_scrolling_text_new(window,
        text, 2,
        100, 100, 200, 200)
    land_widget_scrolling_autohide(scrolling, 1, 1, 1)

    LandWidget *empty = land_widget_scrolling_get_empty(scrolling)
    LandWidget *sizer = land_widget_sizer_new(empty, 3, 0, 0, 10, 10)
    land_widget_layout_set_expanding(sizer, 1, 1)
    land_widget_sizer_set_target(sizer, scrolling)

def init(LandRunner *r):
    create_dialog()

def tick(LandRunner *r):
    if land_closebutton(): land_quit()
    if land_key_pressed(LandKeyEscape): land_quit()

    int kx = 0, ky = 0
    if land_key(LandKeyLeft): kx -= 1
    if land_key(LandKeyRight): kx += 1
    if land_key(LandKeyUp): ky -= 1
    if land_key(LandKeyDown): ky += 1

    if kx or ky:
        land_widget_scrolling_scroll(scrolling, kx, ky)

    land_widget_tick(desktop)

def draw(LandRunner *r):
    land_widget_draw(desktop)

land_begin_shortcut(640, 480, 0, 60,
    LAND_OPENGL | LAND_WINDOWED,
    init, None, tick, draw, None, None)
