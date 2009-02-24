import land/land

def game_draw(LandRunner *self):
    pass

def game_tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape): land_quit()

def begin():
    land_init()
    land_set_display_parameters(640, 480, LAND_FULLSCREEN | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("game",
        NULL, NULL, game_tick, game_draw, NULL, NULL)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(begin)

