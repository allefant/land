import global land/land

LandFont *big
LandFont *small
LandFont *tiny
LandFont *truecolor
LandFont *paletted

static def game_init(LandRunner *self):
    big = land_font_load("../../data/galaxy.ttf", 60)
    small = land_font_load("../../data/galaxy.ttf", 30)
    tiny = land_font_load("../../data/galaxy.ttf", 12)
    truecolor = land_font_load("../../data/truecolor.tga", 67)
    paletted = land_font_load("../../data/paletted.tga", 67)
    # builtin = land_allegro_font()

static def game_tick(LandRunner *self):
    if land_key(KEY_ESC):
        land_quit()

static def game_draw(LandRunner *self):
    land_clear(0, 0.5, 1, 1)

    glMatrixMode(GL_MODELVIEW_MATRIX)
    glLoadIdentity()

    glEnable(GL_LINE_SMOOTH)

    land_font_set(big)
    float x = land_display_width() / 2
    float y = land_display_height() / 2 - land_font_height(big) / 2
    land_color(0, 1, 0, 0.5)
    land_line(x - 3, y, x + 3, y)
    land_line(x, y - 3, x, y + 3)
    land_color(0, 0, 0, 1)
    land_text_pos(x, y)
    land_print_center("Land Fonts")

    land_font_set(small)
    land_color(0, 0, 0, 1)
    land_print_center("font example")

    land_font_set(tiny)
    land_color(0, 0, 0, 1)
    land_print_center("Demonstrates use of different fonts accessible with Land.")
    land_print_center("And shows how to use the text cursor for positioning.")

    land_font_set(truecolor)
    land_color(1, 1, 1, 1)

    glLoadIdentity()
    glTranslatef(land_display_width() / 2, land_display_height() * 0.7, 0)
    glRotatef(45 * sin(land_get_time() * AL_PI * 0.5), 0, 0, 1)
    land_text_pos(0, 0)
    land_print_center("Truecolor")

    float s = 0.6 + 0.5 * sin(land_get_time() * AL_PI)
    double t = land_get_time()
    double a = fmod((t + sin(t)) * 180, 360)

    glLoadIdentity()
    land_font_set(paletted)
    glTranslatef(land_display_width() / 4, 2 * land_display_height() / 5, 0)
    glRotatef(a, 0, 0, 1)
    glScalef(s, s, 1)
    land_color(0, 0, 0, 1)
    land_text_pos(0, -30)

    land_print_center("paletted")

    glLoadIdentity()
    land_font_set(paletted)
    glTranslatef(land_display_width() * 0.75, 2 * land_display_height() / 5, 0)
    glRotatef(-a, 0, 0, 1)
    glScalef(s, s, 1)
    land_color(0, 0, 0, 1)
    land_text_pos(0, -30)

    land_print_center("paletted")

def my_main():
    land_init()
    land_set_display_parameters(640, 480, 32, 120, LAND_WINDOWED | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("font example",
        game_init, NULL, game_tick, game_draw, NULL, NULL)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_main()

land_use_main(my_main)
