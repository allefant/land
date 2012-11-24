import global land/land

class Game:
    float t

Game *game

static def game_init(LandRunner *self):
    land_alloc(game)

static def game_tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()
    game->t += 1.0 / land_get_fps()

static def game_draw(LandRunner *self):
    land_clear(0, 0, 0, 1)

    land_color(0, 0, 1, 1)
    float w = land_display_width()
    float h = land_display_height()
    float x = w / 2
    float y = h / 2
    float r = 100 * fabs(sin(game->t))
    land_filled_circle(x - r, y - r, x + r, y + r)

    land_color(1, 1, 0, 1)
    land_filled_circle(0, 0, 8, 8)
    land_filled_circle(w - 8, 0, w, 8)
    land_filled_circle(w - 8, h - 8, w, h)
    land_filled_circle(0, h - 8, 8, h)

def init():
    land_init()
    land_set_display_parameters(640, 480, LAND_WINDOWED | LAND_RESIZE |
        LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("game",
        game_init, NULL, game_tick, game_draw, NULL, NULL)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(init)
