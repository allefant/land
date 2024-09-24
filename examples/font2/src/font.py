import global land/land

def _tick:
    if land_key(LandKeyEscape):
        land_quit()

def _draw:
    land_reset_transform()
    land_scale_to_fit(640, 480, 0)
    land_font_set(land_initial_font())
    land_clear(0, 0, 0, 1)
    land_color(1, 1, 0, 1)
    land_text_background(land_color_rgba(0, 0, 1, 1), 8)

    for int i in range(2):
        if i == 0: land_text_pos(0, 20)
        if i == 1:
            land_text_pos(64, 20)
            land_scale(3, 3)
        land_print_multiline(
            "abcdefghijklm" "\n"
            "nopqrstuvwxyz" "\n"
            "ABCDEFGHIJKLM" "\n"
            "NOPQRSTUVWXYZ" "\n"
            "0123456789!?&#" "\n"
            "()<>[]{}\"'" "\n"
            ".:,+-=*/\\%_|" "\n"
            )
        if i == 1:
            land_scale(1, 1)
    

def _config(): land_default_display()
land_example(_config, None, _tick, _draw, None)
