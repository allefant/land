import global land.land

char *text
LandFont *font
LandArray *lines

int wrap_w = 640
int scroll = 0
float height

def wrap():
    land_text_destroy_lines(lines)
    lines = land_wordwrap_text(wrap_w, 0, text)
    land_wordwrap_extents(None, &height)

def init():
    font = land_font_load("../../data/DejaVuSans.ttf", 10)
    text = land_read_text("../../data/GPL-2")
    wrap()

def done():
    land_free(text)
    land_font_destroy(font)

def tick():
    int lineh = land_font_height(font)
    if land_key_pressed(LandKeyEscape): land_quit()
    if land_key_pressed(LandKeyHome): scroll = 0
    if land_key_pressed(LandKeyEnd): scroll = height - 480
    if land_key_pressed(LandKeyPageUp): scroll -= 480
    if land_key_pressed(LandKeyPageDown): scroll += 480
    if land_key_pressed(LandKeyUp): scroll -= lineh
    if land_key_pressed(LandKeyDown): scroll += lineh
    int ow = wrap_w
    if land_key_pressed(LandKeyLeft):
        if land_key(LandKeyLeftShift): wrap_w -= 20
        else wrap_w--
    if land_key_pressed(LandKeyRight):
        if land_key(LandKeyLeftShift): wrap_w += 20
        else wrap_w++
    if ow != wrap_w:
        wrap()
    int dz = land_mouse_delta_z()
    scroll -= dz * 10

def draw():
    land_clear(0.9, 0.9, 0.9, 1)
    land_color(0.8, 0.8, 1, 1)
    land_filled_rectangle(wrap_w, 0, 640, 480)
    land_color(0, 0, 0, 1)
    land_text_pos(0, -scroll)
    land_print_lines(lines, LandAlignAdjust)

land_begin_shortcut(640, 480, 60, 0, init, None, tick, draw, None, done)
