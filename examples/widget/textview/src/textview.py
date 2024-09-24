import global land/land

LandWidget *desktop
LandWidgetTheme *theme
LandWidget *scrolling1, *scrolling2, *scrolling3
LandWidget *window3

def create_dialog():
    land_find_data_prefix("data/")
    land_font_load("galaxy.ttf", 12)
    theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_board_new(None, 0, 0, land_display_width(), land_display_height())
    land_widget_reference(desktop)

    make_window1()
    make_window2()
    make_window3()
    make_window4()

def make_window1:
    char *text = land_read_text("GPL-2")

    LandWidget *window = land_widget_vbox_new(desktop, 100, 100, 200, 200)
    land_widget_mover_new(window, "GPL-2", 0, 0, 4, 4)
    scrolling1 = land_widget_scrolling_new(window, 0, 0, 0, 0)
    LandWidget *empty = land_widget_scrolling_get_empty(scrolling1)
    LandWidget *sizer = land_widget_sizer_new(None, 3, 0, 0, 10, 10)
    land_widget_replace(empty, sizer)
    land_widget_layout_set_expanding(sizer, 1, 1)
    land_widget_sizer_set_target(sizer, window)
    LandWidget *textview = land_widget_text_new(scrolling1, None, 2, 0, 0, 0, 0)

    (float iw, ih) = land_widget_get_inner_size(scrolling1)
    (float iw2, ih2) = land_widget_get_inner_size(textview)
    land_widget_set_size_permanent(textview, iw, ih)
    
    land_widget_button_set_text(textview, text)
    #land_widget_scrolling_autohide(scrolling1, 1, 1, 0)
    float w = land_widget_scrolling_get_width(scrolling1)
    if w < iw:
        land_widget_set_size_permanent(textview, w, 0)
        land_widget_button_refresh_text(textview)
    land_widget_scrolling_autohide(scrolling1, 1, 1, 0)

def make_window2:
    char *text = land_read_text("GPL-2")
    LandWidget *window2 = land_widget_vbox_new(desktop, 300, 100, 200, 200)
    land_widget_mover_new(window2, "GPL-2", 0, 0, 4, 4)
    scrolling2 = land_widget_scrolling_text_new(window2, text, 2, 0, 0, 0, 0)
    LandWidget *empty2 = land_widget_scrolling_get_empty(scrolling2)
    LandWidget *sizer2 = land_widget_sizer_new(None, 3, 0, 0, 10, 10)
    land_widget_replace(empty2, sizer2)
    land_widget_layout_set_expanding(sizer2, 1, 1)
    land_widget_sizer_set_target(sizer2, window2)

def make_window4:
    char *text = """I am the one who has called the heroes of the realm out to this place to rid the lands of evil monsters.

Many have been arriving. Many have perished."""
    LandWidget *window4 = land_widget_vbox_new(desktop, 700, 100, 200, 200)
    land_widget_mover_new(window4, "space", 0, 0, 4, 4)
    auto scrolling4 = land_widget_scrolling_text_new(window4, text, 2, 0, 0, 0, 0)
    LandWidget *empty = land_widget_scrolling_get_empty(scrolling4)
    LandWidget *sizer = land_widget_sizer_new(None, 3, 0, 0, 10, 10)
    land_widget_replace(empty, sizer)
    land_widget_layout_set_expanding(sizer, 1, 1)
    land_widget_sizer_set_target(sizer, window4)

def make_window3:
    window3 = land_widget_vbox_new(desktop, 500, 100, 200, 200)
    land_widget_mover_new(window3, "spans", 0, 0, 4, 4)
    scrolling3 = land_widget_scrolling_text_new(window3, None, 2, 0, 0, 0, 0)
    LandWidget *empty3 = land_widget_scrolling_get_empty(scrolling3)
    LandWidget *sizer3 = land_widget_sizer_new(None, 3, 0, 0, 10, 10)
    land_widget_replace(empty3, sizer3)
    land_widget_layout_set_expanding(sizer3, 1, 1)
    land_widget_sizer_set_target(sizer3, window3)

    str colors[] = {"maroon/2", "maroon", "saddlebrown/2", "dark goldenrod/2",
    "moccasin/2", "dark olivegreen/2", "dark green/2", "teal",
    "dark slategray/2", "deepskyblue/2", "midnightblue/2", "indigo/2",
    "purple/2", "black", "rosybrown/2", "dark red", "saddlebrown",
    "dark goldenrod", "olive", "dark green", "green", "dark cyan", "teal/2",
    "royalblue", "navy", "indigo", "medium violetred/2", "dimgray/2",
    "brown", "firebrick", "peru", "gold", "goldenrod", "dark olivegreen",
    "forestgreen", "medium seagreen", "dark slategray", "steelblue",
    "midnightblue", "dark violet", "purple", "dimgray", "crimson",
    "sienna", "dark orange", "wheat", "dark khaki", "olivedrab",
    "seagreen", "light seagreen", "cadetblue", "slategray", "medium blue",
    "thistle/2", "dark magenta", "gray", "indianred", "red", "sandybrown",
    "navajowhite", "khaki", "yellowgreen", "dark seagreen",
    "dark turquoise", "skyblue", "light slategray", "dark slateblue",
    "blueviolet", "sequoia", "dark gray", "rosybrown", "chocolate",
    "orange", "moccasin", "palegoldenrod", "chartreuse", "limegreen",
    "medium aquamarine", "light blue", "dodgerblue", "blue", "dark orchid",
    "medium violetred", "silver", "light coral", "orangered", "tan",
    "antiquewhite", "banana", "citron", "light green", "medium turquoise",
    "powderblue", "cornflowerblue", "rebeccapurple", "medium orchid",
    "deeppink", "light gray", "salmon", "tomato", "burlywood",
    "blanchedalmond", "beige", "greenyellow", "lime", "turquoise",
    "paleturquoise", "deepskyblue", "slateblue", "orchid", "magenta",
    "gainsboro", "light pink", "coral", "peachpuff", "papayawhip",
    "yellow", "light goldenrodyellow", "springgreen", "medium springgreen",
    "cyan", "light steelblue", "medium slateblue", "violet",
    "palevioletred", "whitesmoke", "pink", "dark salmon", "bisque",
    "oldlace", "cornsilk", "light yellow", "palegreen", "aquamarine",
    "light cyan", "light skyblue", "medium purple", "plum", "hotpink",
    "ghostwhite", "mistyrose", "light salmon", "seashell", "floralwhite",
    "lemonchiffon", "ivory", "honeydew", "mintcream", "azure", "aliceblue",
    "lavender", "thistle", "lavenderblush", "white"}
    for int i in range(14 * 11):
        char name[100]
        sprintf(name, "%s ", colors[i])
        land_widget_scrolling_text_add(scrolling3, name, land_color_name(colors[i]), None)
    land_widget_scrolling_text_update(scrolling3)
    

def _init(LandRunner *r):
    create_dialog()
    #print("land_widget_resize")
    #land_widget_resize(window3, 1, 0)

def _tick(LandRunner *r):
    if land_closebutton(): land_quit()
    if land_key_pressed(LandKeyEscape): land_quit()

    int kx = 0, ky = 0
    if land_key(LandKeyLeft): kx -= 1
    if land_key(LandKeyRight): kx += 1
    if land_key(LandKeyUp): ky -= 1
    if land_key(LandKeyDown): ky += 1

    if kx or ky:
        land_widget_scrolling_scroll(scrolling1, kx, ky)
        land_widget_scrolling_scroll(scrolling2, kx, ky)

    land_widget_tick(desktop)

def _draw(LandRunner *r):
    land_widget_draw(desktop)
    #land_exception("test")

def _done:
    pass

land_standard_example()
