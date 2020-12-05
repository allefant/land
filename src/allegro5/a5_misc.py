import land.land
static import global allegro5.allegro_color
static import global allegro5.allegro_native_dialog if !defined(ANDROID)

def platform_color_hsv(float hue, sat, val) -> LandColor:
    LandColor c
    al_color_hsv_to_rgb(hue, sat, val, &c.r, &c.g, &c.b)
    c.a = 1
    return c

def platform_color_name(char const *name) -> LandColor:
    LandColor c
    if land_equals(name, "sequoia"):
        c.r = 0x90 / 255.0
        c.g = 0x50 / 255.0
        c.b = 0x60 / 255.0
        c.a = 1
        return c

    # if there's spaces ignore them
    int i = 0
    while name[i]:
        if name[i] == ' ':
            # "light blue" [i = 5]
            char name2[strlen(name)]
            strncpy(name2, name, i) # "light"
            int j = i
            i++ # "light" [i = 6, J = 5]
            while name[i]:
                if name[i] == ' ':
                    i++
                    continue
                name2[j++] = name[i++]
            name2[j] = 0

            al_color_name_to_rgb(name2, &c.r, &c.g, &c.b)
            c.a = 1
            return c
        i++
    
    al_color_name_to_rgb(name, &c.r, &c.g, &c.b)
    c.a = 1
    return c

def platform_popup(str title, str text):
    *** "ifdef" ANDROID
    *** "else"
    al_show_native_message_box(al_get_current_display(), title,
        title, text, None, ALLEGRO_MESSAGEBOX_ERROR)
    *** "endif"
  
