#include <land/land.h>

static void game_tick(void)
{
    if (land_key(KEY_ESC))
        land_quit();
}

static void game_draw(void)
{
    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT);
    glEnable(GL_LINE_SMOOTH);
    glEnable(GL_POINT_SMOOTH);
    glEnable(GL_POLYGON_SMOOTH);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA_SATURATE, GL_ONE);

    land_clip(land_mouse_x() - 100, land_mouse_y() - 100,
        land_mouse_x() + 100, land_mouse_y() + 100);

    land_color(1, 0, 0);
    land_rectangle(0, 0, 639, 479);
    land_color(0, 1, 0);
    land_line(1, 1, 319, 239);
    land_line(638, 1, 320, 239);
    land_line(638, 478, 320, 240);
    land_line(1, 478, 319, 240);

    land_color(1, 1, 0);
    land_line(3, 1, 319, 237);
    land_line(636, 1, 320, 237);
    land_line(636, 478, 320, 242);
    land_line(3, 478, 319, 242);

    land_color(1, 1, 0);
    land_line(1, 3, 317, 239);
    land_line(638, 3, 322, 239);
    land_line(638, 476, 322, 240);
    land_line(1, 476, 317, 240);

    float r = 40;
    land_color(0, 0, 1);
    land_circle(320 - r, 120 - r, 320 + r, 120 + r);
    land_circle(320 - r, 360 - r, 320 + r, 360 + r);
    land_filled_circle(160 - r, 240 - r, 160 + r, 240 + r);
    land_filled_circle(480 - r, 240 - r, 480 + r, 240 + r);
}

land_begin()
{
    land_init();
    land_set_display_parameters(640, 480, 32, 120, LAND_WINDOWED | LAND_OPENGL);
    LandRunner *game_runner = land_runner_register("game",
        NULL, NULL, game_tick, game_draw, NULL, NULL);
    land_set_initial_runner(game_runner);
    land_main();
}
