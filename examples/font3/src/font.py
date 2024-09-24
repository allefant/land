import global land/land

LandText *text

str text_sample1 = """def _init:
    auto f = land_initial_font()
    text = land_text_new("""
str text_sample2 = """_, _, _, _, _, _ _ _ , , ,"""
str text_sample3 = """)
    span(text, f, name("white"), text_sample)

int x2 = 50 + 400, y2 = 50 + 300

def _tick:
    land_scale_to_fit(640, 480, 256)
    if land_key(LandKeyEscape):
        land_quit()
    (int mx_, my_) = land_mouse_pos()
    float mx = mx_, my = my_
    land_mouse_transformed(&mx, &my)
    if land_mouse_button_clicked(0):
        x2 = mx
        y2 = my

def _draw:
    land_scale_to_fit(640, 480, 0)
    land_font_set(land_initial_font())
    land_clear(.5, .5, .5, 1)
    land_color(.9, .8, .7, 1)
    float tx = 50, ty = 50, tw = x2 - tx, th = y2 - ty
"""

def _init:
    pass

int x2 = 50 + 156, y2 = 50 + 300
int offset = 0

def _tick:
    land_scale_to_fit(640, 480, 256)
    if land_key(LandKeyEscape):
        land_quit()
    (int mx_, my_) = land_mouse_pos()
    float mx = mx_, my = my_
    land_mouse_transformed(&mx, &my)
    if land_mouse_button_clicked(LandButtonLeft):
        x2 = mx
        y2 = my
    if land_mouse_button_clicked(LandButtonRight):
        offset = mx - 50

def _draw:
    float tx = 50, ty = 50
    float tw = x2 - tx, th = y2 - ty
    land_scale_to_fit(640, 480, 0)
    land_font_set(land_initial_font())

    text = land_text_new(50, 50, tw, th)
    auto f = land_initial_font()
    land_text_add_span(text, f, land_color_name("white"), text_sample1)
    land_text_add_span(text, f, land_color_name("orange"), text_sample2)
    land_text_add_span(text, f, land_color_name("pink"), text_sample3)

    land_clear(0, 0, 0, 1)
    land_color(.5, .5, .5, 1)
    land_filled_rectangle(0, 0, 640, 480)
    land_color_set_named("moccasin/2")
    
    land_filled_rectangle(tx, ty, tx + tw, ty + th)
    #land_text_pos(tx, ty)
    #land_color(0, 0, 0, 1)
    #land_print_wordwrap_offset(tw, th, offset, text_sample)
    land_text_draw(text)
    land_color(1, 0, 0, 1)
    land_rectangle(text.ex, text.ey, text.ex + text.ew, text.ey + text.eh)

    land_text_destroy(text)

def _done:
    pass

land_standard_example()
