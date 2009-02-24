class LandColor:
   float r, g, b, a

static import land/allegro5/a5_misc

LandColor def land_color_hsv(float hue, sat, val):
    return platform_color_hsv(hue, sat, val)
