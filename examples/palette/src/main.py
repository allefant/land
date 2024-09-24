import land.land

int mode
LandImage *background

def _init:
    land_find_data_prefix("data/")
    land_font_load("URWGothicBook.ttf", 40)
    background = land_image_new(64, 64)
    byte rgba[64 * 64 * 4]
    land_image_get_rgba_data(background, rgba)
    for int y in range(64):
        for int x in range(64):
            LandColor c = land_rgb(.25, .25, .25)
            if (x // 2) % 2 == 0 and (y // 2) % 2 == 0: c = land_rgb(.5, .5, .5)
            land_color_copy_to_bytes(c, rgba + y * 64 * 4 + x * 4)
    land_image_set_rgba_data(background, rgba)

def _tick:
    if land_closebutton(): land_quit()
    if land_key_pressed(LandKeyEscape): land_quit()
    if land_key_pressed(' '):
        mode += 1
        if mode == 4: mode = 0

def _draw:
    land_color(0, 0, 0, 1)
    land_clear_color()
    int dw = land_display_width()
    int dh = land_display_height()
    float xy[] = {0, 0, 0, dh, dw, dh, dw, 0}
    float s = 1
    float uv[] = {0, 0, 0, dh / s, dw / s, dh / s, dw / s, 0}
    land_set_white()
    land_textured_polygon(background, 4, xy, uv)
    int maxc = 35
    int cw = dw / maxc
    int ch = cw
    int y = 8
    str pals1[] = {"greys", "light", "dark", "reds", "browns",
        "yellows", "greens", "blues", "purples", "colorless",
        "colorful", None}
    str pals2[] = {"material-red", "material-pink","material-purple",
        "material-deep purple","material-indigo","material-blue",
        "material-light blue", "material-cyan", "material-teal",
        "material-green", "material-light green", "material-lime",
        "material-yellow", "material-amber", "material-orange",
        "material-deep orange", "material-grey", "material-brown",
        "material-blue grey", None}
    str pals3[] = {"14x11", None}
    str *pals = pals1
    if mode == 1: pals = pals2
    if mode == 2: pals = pals2
    if mode == 3: pals = pals3
    LandHash *duplicate = land_hash_new()
    uint32_t j = 0
    int left = 8
    while pals[j]:
        int n = land_palette_length(pals[j])
        land_set_white()
        land_text_pos(left, y)
        land_print("%s", pals[j])
        y = land_text_y_pos()
        int x = left
        for int i in range(n):
            int mh = ch
            LandColor ocol = land_palette_color(pals[j], i)
            LandColor col = ocol
            if mode == 2:
                col = land_palette_close("14x11", ocol)
                char html[8]
                land_color_to_html(col, html)
                if land_hash_has(duplicate, html):
                    mh = ch // 8
                else:
                    land_color_to_html(col, html)
                    land_hash_insert(duplicate, html, None)
            land_color_set(col)
            land_filled_rectangle(x, y + ch - mh, x + cw, y + ch)
            if mode == 2:
                land_color_set(ocol)
                land_filled_rectangle(x, y + ch + 1, x + cw, y + ch + 1 + ch // 8)
            x += cw * 1.05
            if x + cw > dw or (mode == 3 and i % 14 == 13):
                x = left
                y += cw * 1.05
        if x > 8: y += cw * 1.05
        j += 1
        if y + land_line_height() + cw > dh:
            y = 8
            left = 8 + 15 * cw
    land_hash_destroy(duplicate)

def _config(): land_default_display()
land_example(_config, _init, _tick, _draw, None)
