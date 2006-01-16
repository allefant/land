#include <land/land.h>

LandFont *big;
LandFont *small;
LandFont *tiny;
LandFont *truecolor;
LandFont *paletted;

static void game_init(LandRunner *self)
{
    land_set_glyphkeeper(0);
    big = land_font_load("../../data/galaxy.ttf", 60);
    small = land_font_load("../../data/galaxy.ttf", 30);
    tiny = land_font_load("../../data/galaxy.ttf", 12);
    truecolor = land_font_load("../../data/truecolor.tga", 67);
    paletted = land_font_load("../../data/paletted.tga", 67);
    //builtin = land_allegro_font();
}

static void game_tick(LandRunner *self)
{
    if (land_key(KEY_ESC))
        land_quit();
}

static void game_draw(LandRunner *self)
{
    land_clear(0, 0.5, 1, 1);

    glMatrixMode(GL_MODELVIEW_MATRIX);
    glLoadIdentity();

    land_set_font(big);
    float x = land_display_width() / 2;
    float y = land_display_height() / 2 - land_font_height(big) / 2;
    land_color(0, 1, 0, 0.5);
    land_line(x - 3, y, x + 3, y);
    land_line(x, y - 3, x, y + 3);
    land_color(0, 0, 0, 1);
    land_text_pos(x, y);
    land_print_center("Land Fonts");

    land_set_font(small);
    land_color(0, 0, 0, 1);
    land_print_center("font example");

    land_set_font(tiny);
    land_color(0, 0, 0, 1);
    land_print_center("Demonstrates use of different fonts accessible with Land.");
    land_print_center("And shows how to use the text cursor for positioning.");

    land_set_font(truecolor);
    land_color(1, 1, 1, 1);
    glEnable(GL_BLEND);
    //glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glBlendFunc(GL_SRC_COLOR, GL_ONE_MINUS_SRC_COLOR);
    glTranslatef(land_display_width() / 2, land_display_height() * 0.7, 0);
    glRotatef(45 * sin(land_get_time() * AL_PI * 0.5), 0, 0, 1);
    land_text_pos(0, 0);
    land_print_center("Truecolor");

    float s = 0.6 + 0.5 * sin(land_get_time() * AL_PI);

    glLoadIdentity();
    land_set_font(paletted);
    glTranslatef(land_display_width() / 4, land_display_height() / 4, 0);
    glRotatef(land_get_time() * 180, 0, 0, 1);
    glScalef(s, s, s);
    land_color(0, 0, 0, 1);
    land_text_pos(0, -30);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    land_print_center("paletted");

    glLoadIdentity();
    land_set_font(paletted);
    glTranslatef(land_display_width() * 0.75, land_display_height() / 4, 0);
    glRotatef(land_get_time() * -180, 0, 0, 1);
    glScalef(s, s, s);
    land_color(0, 0, 0, 1);
    land_text_pos(0, -30);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    land_print_center("paletted");
}

land_begin()
{
    land_init();
    land_set_display_parameters(640, 480, 32, 120, LAND_WINDOWED | LAND_OPENGL);
    LandRunner *game_runner = land_runner_new("font example",
        game_init, NULL, game_tick, game_draw, NULL, NULL);
    land_runner_register(game_runner);
    land_set_initial_runner(game_runner);
    land_main();
}
