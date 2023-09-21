import global land/land

static def game_tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

static def game_draw(LandRunner *self):
    land_scale_to_fit(640, 480, 0)
    land_clear(0, 0, 0, 1)
    land_color(1, 1, 1, 1)
    land_filled_rounded_rectangle(40, 40, 600, 440, 40)

def begin():
    land_init()
    land_set_display_parameters(640, 480, LAND_WINDOWED | LAND_OPENGL | LAND_RESIZE)
    LandRunner *game_runner = land_runner_new("game", NULL, NULL, game_tick, game_draw, NULL, NULL)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(begin)
