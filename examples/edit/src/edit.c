#include <stdlib.h>
#include <string.h>

#include <land/land.h>

LandWidget *desktop;

LandImage *prev, *current;

LandWidget *edit_text;
LandWidget *edit_red;
LandWidget *edit_green;
LandWidget *edit_blue;

LandFont *af;

static void redraw(LandWidget *self)
{
    LandImage *temp = prev;
    prev = current;
    current = temp;
    LandFont *f = land_font_current();
    land_font_set(af);
    land_set_image_display(current);
    land_clear(0, 0, 0, 1);
    float r = land_widget_spin_get_value(edit_red);
    float g = land_widget_spin_get_value(edit_green);
    float b = land_widget_spin_get_value(edit_blue);
    land_color(r, g, b, 1);
    land_line(0, 0, 128, 0);
    char const *text = land_widget_edit_get_text(edit_text);
    land_text_pos(64, 64);
    land_print_center(text);
    land_unset_image_display();

    land_font_set(f);
}

static void game_init(LandRunner *self)
{
    af = land_font_allegro_load("data/galaxy.ttf", 20);

    land_font_load("data/galaxy.ttf", 12);

    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480);
    desktop->theme = land_widget_theme_new("../../data/classic.cfg");

    LandWidget *vbox = land_widget_vbox_new(desktop, 10, 10, 10, 10);
    land_widget_vbox_set_columns(vbox, 2);
    land_widget_text_new(vbox, "Text", 0, 0, 1, 1);
    edit_text = land_widget_edit_new(vbox, "Land", redraw, 0, 0, 100, 0);
    land_widget_text_new(vbox, "Red", 0, 0, 1, 1);
    edit_red = land_widget_spin_new(vbox, 0.5, 0, 1, 0.01, redraw, 0, 0, 0, 0);
    land_widget_text_new(vbox, "Green", 0, 0, 1, 1);
    edit_green = land_widget_spin_new(vbox, 0.5, 0, 1, 0.01, redraw, 0, 0, 0, 0);
    land_widget_text_new(vbox, "Blue", 0, 0, 1, 1);
    edit_blue = land_widget_spin_new(vbox, 0.5, 0, 1, 0.01, redraw, 0, 0, 0, 0);

    land_widget_layout(vbox);

    prev = land_image_create(128, 128);
    current = land_image_create(128, 128);
}

static void game_tick(LandRunner *self)
{
    if (land_key_pressed(KEY_ESC) || land_closebutton())
        land_quit();

    land_widget_tick(desktop);
}

static void game_draw(LandRunner *self)
{
    land_widget_draw(desktop);

    land_image_draw(prev, 320, 10);
    land_image_draw(current, 320, 20 + 128);
}

static void game_exit(LandRunner *self)
{
    land_widget_theme_destroy(desktop->theme);
    land_widget_unreference(desktop);
    land_font_destroy(land_font_current());
}

land_begin()
{
    land_init();
    land_set_display_parameters(640, 480, 32, 100, LAND_WINDOWED | LAND_OPENGL);
    LandRunner *game_runner = land_runner_new("edit", game_init,
        NULL, game_tick, game_draw, NULL, game_exit);
    land_runner_register(game_runner);
    land_set_initial_runner(game_runner);
    land_main();
}