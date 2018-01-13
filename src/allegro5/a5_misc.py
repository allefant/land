import land.color
import land.common
static import global allegro5.allegro_color
static import global allegro5.allegro_native_dialog if !defined(ANDROID)

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

def platform_popup(str title, str text):
    *** "ifdef" ANDROID
    *** "else"
    al_show_native_message_box(al_get_current_display(), title,
        title, text, None, ALLEGRO_MESSAGEBOX_ERROR)
    *** "endif"
  
