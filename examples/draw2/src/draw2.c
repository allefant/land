#include <land/land.h>

typedef struct Game Game;
struct Game
{
    float t;
};

Game *game;

static void game_init(LandRunner *self)
{
    game = calloc(1, sizeof *game);
}

static void game_tick(LandRunner *self)
{
    if (land_key(KEY_ESC))
        land_quit();
    game->t += 1.0 / land_get_frequency();
}

static void game_draw(LandRunner *self)
{
    land_clear(0, 0, 0, 1);

    land_color(0, 0, 1, 1);
    float x = land_display_width() / 2;
    float y = land_display_height() / 2;
    float r = 100 * fabs(sin(game->t));
    land_filled_circle(x - r, y - r, x + r, y + r);
}

land_begin()
{
    land_init();
    land_set_display_parameters(640, 480, 32, 120, LAND_WINDOWED | LAND_OPENGL);
    LandRunner *game_runner = land_runner_new("game",
        game_init, NULL, game_tick, game_draw, NULL, NULL);
    land_runner_register(game_runner);
    land_set_initial_runner(game_runner);
    land_main();
}
