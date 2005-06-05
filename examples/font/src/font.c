#include <land/land.h>

LandFont *big;
LandFont *small;
LandFont *builtin;

static void game_init(void)
{
    big = land_load_font("../../data/galaxy.ttf", 40);
    small = land_load_font("../../data/galaxy.ttf", 10);
    //builtin = land_allegro_font();
}

static void game_tick(void)
{
    if (land_key(KEY_ESC))
        land_quit();
}

static void game_draw(void)
{
    land_clear(1, 1, 1);

    land_set_font(big);
    land_text_pos(land_display_width() / 2,
        land_display_height() / 2 - land_font_height(big) / 2);
    land_print_center("Land");

    land_set_font(small);
    land_print_center("font example");
}

land_begin()
{
    land_init();
    land_set_display_parameters(640, 480, 32, 120, LAND_WINDOWED | LAND_OPENGL);
    LandRunner *game_runner = land_runner_register("font example",
        game_init, NULL, game_tick, game_draw, NULL, NULL);
    land_set_initial_runner(game_runner);
    land_main();
}
