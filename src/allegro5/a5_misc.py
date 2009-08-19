import land/color
static import global allegro5/allegro_color

LandColor def platform_color_hsv(float hue, sat, val):
    LandColor c
    al_color_hsv_to_rgb(hue, sat, val, &c.r, &c.g, &c.b)
    c.a = 1
    return c
