import land/color
static import global allegro5/allegro_color

def platform_color_hsv(float hue, sat, val) -> LandColor:
    LandColor c
    al_color_hsv_to_rgb(hue, sat, val, &c.r, &c.g, &c.b)
    c.a = 1
    return c

def platform_color_name(char const *name) -> LandColor:
    LandColor c
    al_color_name_to_rgb(name, &c.r, &c.g, &c.b)
    c.a = 1
    return c
