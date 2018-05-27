import global land.land

static macro _test(name):
    _test_before(***name)
    _test_******name()
    _test_after()

def test_widget:
    land_mainloop_prepare()
    land_find_data_prefix("data/")
    land_font_load("DejaVuSans.ttf", 12)
    land_widget_theme_new("classic.cfg")
    
    _test(minimum)
    _test(border)
    _test(border_rec)
    _test(hbox)
    _test(vbox)
    _test(text1)
    _test(text2)
    _test(scroll1)
    _test(scroll2)
    _test(scroll3)
    _test(scroll4)
    _test(scroll5)
    _test(scroll6)
    _test(scroll7)
    _test(scroll8)
    _test(scroll9)
    _test(scroll10)

str test_name
bool test_failed
LandWidget *widget

def _test_before(str name):
    test_name = name
    test_failed = False
    widget = None

def _test_after:
    _done()

def _done:
    char *name = land_strdup(test_name)
    land_concatenate(&name, ".png")
    land_file_remove(name)
    if widget:
        LandImage *image = land_image_new(widget.box.w, widget.box.h)
        land_set_image_display(image)
        land_widget_draw(widget)
        land_unset_image_display()
        land_image_save(image, name)
        
    if test_failed:
        printf("%-20s %sFAIL%s\n", test_name, land_color_bash("red"),
            land_color_bash(""))
    else:
        printf("%-20s %sPASS%s\n", test_name, land_color_bash("green"),
            land_color_bash(""))

def _assert_size(LandWidget *wid, int x, y, w, h):
    if wid.box.x != x or wid.box.y != y or wid.box.w != w or wid.box.h != h:
        printf("FAIL\n")
        printf("expected size: %d %d %d %d\n", x, y, w, h)
        printf("but found:     %d %d %d %d\n", wid.box.x, wid.box.y, wid.box.w, wid.box.h)
        test_failed = True

def _assert_min_size(LandWidget *wid, int w, h):
    if wid.box.min_width != w or wid.box.min_height != h:
        printf("FAIL\n")
        printf("expected minimum: %d %d\n", w, h)
        printf("but found:        %d %d\n", wid.box.min_width, wid.box.min_height)
        test_failed = True

def _assert_hidden(LandWidget *wid, bool hidden):
    if wid.hidden != hidden:
        printf("FAIL\n")
        printf("expected:  %s\n", hidden ? "hidden" : "not hidden")
        printf("but found: %s\n", wid.hidden ? "hidden" : "not hidden")
        test_failed = True

str sample_text = """''
One Ring to rule them all, One Ring to find them,
One Ring to bring them all and in the darkness bind them
''"""

def _test_minimum:
    widget = land_widget_base_new(None, 0, 0, 100, 100)
    _assert_size(widget, 0, 0, 100, 100)
    _assert_min_size(widget,  100, 100)
    
def _test_border:
    widget = land_widget_panel_new(None, 0, 0, 100, 100)
    LandWidget* wid = land_widget_base_new(widget, 0, 0, 0, 0)
    _assert_size(wid, 8, 8, 84, 84)

def _test_border_rec:
    widget = land_widget_panel_new(None, 0, 0, 100, 100)
    LandWidget* c2 = land_widget_panel_new(widget, 0, 0, 0, 0)
    LandWidget* c3 = land_widget_panel_new(c2, 0, 0, 0, 0)
    LandWidget* c4 = land_widget_panel_new(c3, 0, 0, 0, 0)
    LandWidget* wid = land_widget_base_new(c4, 0, 0, 0, 0)
    _assert_size(wid, 32, 32, 36, 36)
    
def _test_hbox:
    widget = land_widget_hbox_new(None, 0, 0, 100, 100)
    LandWidget* w1 = land_widget_base_new(widget, 0, 0, 0, 0)
    _assert_size(w1, 0, 0, 100, 100)
    LandWidget* w2 = land_widget_base_new(widget, 0, 0, 0, 0)
    _assert_size(w1, 0, 0, 50, 100)
    _assert_size(w2, 50, 0, 50, 100)

def _test_vbox:
    widget = land_widget_vbox_new(None, 0, 0, 100, 100)
    LandWidget* w1 = land_widget_base_new(widget, 0, 0, 0, 0)
    _assert_size(w1, 0, 0, 100, 100)
    LandWidget* w2 = land_widget_base_new(widget, 0, 0, 0, 0)
    _assert_size(w1, 0, 0, 100, 50)
    _assert_size(w2, 0, 50, 100, 50)

def _test_text1:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* t  = land_widget_text_new(widget, "Hola", 2, 0, 0, 0, 0)
    # the board has no layout so the text cannot move/grow
    _assert_size(t, 0, 0, 0, 0)
    _assert_min_size(t, 30, 18)

def _test_text2:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* t  = land_widget_text_new(widget, "Hola", 2, 0, 0, 0, 0)
    # explicitly calling layout it will still resize to its minimum size
    land_widget_layout(t)
    _assert_size(t, 0, 0, 30, 18)

def _test_scroll1:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    _assert_size(s, 2, 2, 96, 96)
    
def _test_scroll2:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, "Hola", 2, 0, 0, 92, 0)
    _assert_size(t, 4, 4, 92, 0)
    _assert_size(s, 2, 2, 96, 96)

def _test_scroll3:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, "Hola", 2, 0, 0, 92, 0)
    land_widget_layout(t)
    _assert_size(t, 4, 4, 92, 18)
    _assert_size(s, 2, 2, 96, 96)

def _test_scroll4:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(s, 2, 2, 96, 96)
    _assert_hidden(land_widget_scrolling_get_vertical(s), True)
    _assert_hidden(land_widget_scrolling_get_horizontal(s), True)

def _test_scroll5:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, "Hola", 2, 0, 0, 0, 0)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(t, 4, 4, 0, 0)
    _assert_size(s, 2, 2, 96, 96)

def _test_scroll6:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, "Hola", 2, 0, 0, 92, 0)
    land_widget_layout(t)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(t, 4, 4, 92, 18)
    _assert_size(s, 2, 2, 96, 96)

def _test_scroll7:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, sample_text, 1, 0, 0, 0, 0)
    land_widget_layout(t)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(t, 4, 4, 355, 60)
    _assert_size(s, 2, 2, 96, 96)
    _assert_hidden(land_widget_scrolling_get_vertical(s), True)
    _assert_hidden(land_widget_scrolling_get_horizontal(s), False)

def _test_scroll8:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, sample_text, 2, 0, 0, 0, 0)
    land_widget_layout(t)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(t, 4, 4, 58, 270)
    _assert_size(s, 2, 2, 96, 96)
    _assert_hidden(land_widget_scrolling_get_vertical(s), False)
    _assert_hidden(land_widget_scrolling_get_horizontal(s), True)

def _test_scroll9:
    widget = land_widget_board_new(None, 0, 0, 100, 100)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 96)
    LandWidget* t  = land_widget_text_new(s, sample_text, 2, 0, 0, 74, 0)
    land_widget_layout(t)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(t, 4, 4, 74, 200)
    _assert_size(s, 2, 2, 96, 96)
    _assert_hidden(land_widget_scrolling_get_vertical(s), False)
    _assert_hidden(land_widget_scrolling_get_horizontal(s), True)

def _test_scroll10:
    widget = land_widget_board_new(None, 0, 0, 100, 166)
    LandWidget* s = land_widget_scrolling_new(widget, 2, 2, 96, 162)
    LandWidget* t  = land_widget_text_new(s, sample_text, 2, 0, 0, 92, 0)
    land_widget_layout(t)
    land_widget_scrolling_autohide(s, 1, 1, 2)
    _assert_size(t, 4, 4, 92, 158)
    _assert_size(s, 2, 2, 96, 162)
    _assert_hidden(land_widget_scrolling_get_vertical(s), True)
    _assert_hidden(land_widget_scrolling_get_horizontal(s), True)
