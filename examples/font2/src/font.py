import global land/land

def _tick:
    if land_key(LandKeyEscape):
        land_quit()

def _draw:
    land_scale_to_fit(640, 480, 0)
    land_clear(0, 0, 0, 1)
    land_color(1, 1, 0, 1)
    land_text_pos(320, 240)
    land_text_background(land_color_rgba(0, 0, 1, 1), 8)

    land_print_multiline(
        "abcdefghijklm" "\n"
        "nopqrstuvwxyz" "\n"
        "ABCDEFGHIJKLM" "\n"
        "NOPQRSTUVWXYZ" "\n"
        "()<>[]{}" "\n")

def begin():
    land_init()
    land_set_display_percentage_aspect(0.5, 4.0 / 3, LAND_WINDOWED | LAND_OPENGL | LAND_RESIZE)
    land_callbacks(None, _tick, _draw, None)
    land_mainloop()

land_use_main(begin)
