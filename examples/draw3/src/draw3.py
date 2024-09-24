import global land/land

def _tick:
    if land_key(LandKeyEscape):
        land_quit()

def _draw:
    land_scale_to_fit(640, 480, 0)
    land_clear(0, 0, 0, 1)
    land_color(1, 1, 1, 1)
    land_filled_rounded_rectangle(40, 40, 600, 440, 40)

    for int i in range(12):
        float a = 2 * pi * i / 12
        float r1 = 100
        float r2 = 150
        land_gradient(320 + r1 * cos(a), 240 + r1 * sin(a), 320 + r2 * cos(a), 240 + r2 * sin(a), 20,
            land_color_name("white"), land_color_name("plum"))
        r1 = 150
        r2 = 200
        land_gradient(320 + r1 * cos(a), 240 + r1 * sin(a), 320 + r2 * cos(a), 240 + r2 * sin(a), 20,
            land_color_name("plum"), land_color_name("white"))

    float a = land_get_ticks() * 2 * pi / 600
    land_gradient(320, 240, 320 + 200 * cos(a), 240 + 200 * sin(a), 30, land_color_name("banana"), land_color_name("orange"))

    float a2 = land_get_ticks() * 2 * pi / 600 * 12
    land_gradient(320, 240, 320 + 200 * cos(a2), 240 + 200 * sin(a2), 10, land_color_name("citron"), land_color_name("lime"))

def _init: pass
def _done: pass

land_standard_example()
