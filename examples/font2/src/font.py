import global land/land

LandFont *f[6]

def _init:
    f[0] = land_initial_font()
    f[1] = land_create_builtin_font(10)
    f[2] = land_create_builtin_font(12)
    f[3] = land_create_builtin_font(14)
    f[4] = land_create_builtin_font(16)
    f[5] = land_create_builtin_font(24)

def _tick:
    if land_key(LandKeyEscape):
        land_quit()

def _draw:
    land_reset_transform()
    land_scale_to_fit(640, 480, 0)
    land_font_set(land_initial_font())
    land_clear(0, 0, 0, 1)
    land_color(1, 1, 0, 1)

    for int i in range(7):
        land_reset_transform()
        if i == 0:
            land_font_set(f[0])
            land_text_pos(12, 12)
            land_scale(3, 3)
        else:
            land_font_set(f[i - 1])
            int x = 12
            for int j in range(1, i):
                int fs = land_font_size(f[j])
                x += fs * 13 + 16
            land_text_pos(x, 400)

        land_text_background_off()
        land_print("%.0f", land_font_load_size(land_font_current()))
        land_print("")
        land_text_background(land_color_rgba(0, 0, 1, 1), 8)
        land_print_multiline(
            "abcdefghijklm" "\n"
            "nopqrstuvwxyz" "\n"
            "ABCDEFGHIJKLM" "\n"
            "NOPQRSTUVWXYZ" "\n"
            "0123456789!?&#" "\n"
            "()<>[]{}\"'" "\n"
            ".:,+-=*/\\%_|" "\n"
            )


def _config(): land_default_display()
land_example(_config, _init, _tick, _draw, None)
