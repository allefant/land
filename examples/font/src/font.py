import global land/land

LandFont *big
LandFont *small
LandFont *tiny
LandFont *truecolor
LandFont *paletted
LandFont *muli
LandImage *gradient

def _init(LandRunner *self):
    land_find_data_prefix("data/")
    big = land_font_load("galaxy.ttf", 60)
    small = land_font_load("DejaVuSans.ttf", 30)
    tiny = land_font_load("galaxy.ttf", 12)
    truecolor = land_font_load("truecolor.tga", 0)
    paletted = land_font_load("paletted.tga", 0)
    muli = land_font_load("Muli-Regular.ttf", 14)
  
    gradient = land_image_new(4, 4)
    unsigned char rgba[4 * 4 * 4] = {
        255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 
        255, 255, 000, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 000, 255,
        000, 255, 255, 255, 000, 255, 255, 255, 000, 255, 255, 255, 000, 255, 255, 255, 
        000, 000, 255, 255, 000, 000, 255, 255, 000, 000, 255, 255, 000, 000, 255, 255,
        }
    land_image_set_rgba_data(gradient, rgba)

def _tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

def _draw(LandRunner *self):
    float w = land_display_width()
    float h = land_display_height()
    land_clear(0, 0, 0, 1)
    float xy[] = {0, 0, w, 0, w, h, 0, h}
    float uv[] = {1, 1, 3, 1, 3, 3, 1, 3}
    land_color(1, 1, 1, 1)
    land_reset_transform()
    land_textured_polygon(gradient, 4, xy, uv)

    land_font_set(muli)
    land_color(0, 0, 0, 1)
    land_text_pos(w / 2, land_font_height(muli))
    char const *s1 = "Carnation Violet Daffodil Daisy Lily Rose Poppy Aster Tulip Iris Orchid "
    int n = strlen(s1) + 1
    char s2[n]
    land_print_center(s1)
    float tx = w / 2 - land_text_get_width(s1) / 2
    float ty = land_font_height(muli) * 2
    for int i in range(n):
        strncpy(s2, s1, i)
        s2[i] = 0
        LandColor c = land_color_hsv(i * 360 / n + land_get_time() * 120, 1, 1)
        float tw = land_text_get_width(s2)
        land_color(c.r, c.g, c.b, 1)        
        land_text_pos(tx + tw, ty)
        land_print("%c", s1[i])

    land_font_set(big)
    float x = w / 2
    float y = h / 2 - land_font_height(big) / 2
    float alpha =((int)land_get_time()) & 1 ? 0.5 : 0;
    land_color(alpha, alpha, 0, alpha)
    land_reset_transform()
    land_translate(x, y)
    land_rotate(-sin(land_get_time() * LAND_PI * 0.5) * LAND_PI / 4)
    land_line(0 - 3, 0, 0 + 3, 0)
    land_line(0, 0 - 3, 0, 0 + 3)
    
    for int i in range(21):
        land_reset_transform()
        land_translate(x, y)
        land_rotate(-sin(-land_get_time() * LAND_PI * 0.5) * LAND_PI / 4 + LAND_PI / 4)
        land_rotate(-LAND_PI / 2 * i / 20)
        land_line(0, 0.02 * h, 0, h * 0.35)

    land_reset_transform()
    land_color(0, 0, 1, 1)
    land_text_pos(x, y)
    land_print_center("Land Fonts")

    land_font_set(small)
    land_color(0, 0, 0, 1)
    land_print_center("font example")

    land_font_set(tiny)
    land_color(0, 0, 0, 1)
    land_print_center("Demonstrates use of different fonts accessible with Land.")
    land_print_center("And shows how to use the text cursor for positioning.")

    land_font_set(truecolor)
    land_color(1, 1, 1, 1)

    land_reset_transform()
    land_translate(x, y)
    land_rotate(sin(land_get_time() * LAND_PI * 0.5) * LAND_PI / 4)
    land_translate(0, h * 0.35)
    land_text_pos(0, 0)
    land_print_center("Truecolor")

    float s = 0.6 + 0.5 * sin(land_get_time() * LAND_PI)
    double t = land_get_time()
    double a = fmod((t + sin(t)) * 180, 360) * LAND_PI / 180

    land_reset_transform()
    land_font_set(paletted)
    land_translate(land_display_width() / 4, 2 * land_display_height() / 5)
    land_scale(s, s)
    land_rotate(a)
    land_color(1, 0, 0, 1)
    land_text_pos(0, -30)
    land_print_center("paletted")

    land_reset_transform()
    land_font_set(paletted)
    land_translate(land_display_width() * 0.75, 2 * land_display_height() / 5)
    land_scale(s, s)
    land_rotate(-a)
    land_color(0, 0.5, 0, 1)
    land_text_pos(0, -30)
    land_print_center("paletted")

def _done: pass

land_standard_example()
