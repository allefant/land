#include <stdlib.h>
#include <string.h>

#include <land/land.h>

char const *data[] =
{
    "Antelope", "Armadillo",
    "Beaver", "Bear", "Badger",
    "Crocodile", "Camel", "Coyote",
    "Donkey",
    "Elephant", "Elk",
    "Fox", "Frog",
    "Goat", "Giraffe", "Gnu",
    "Hippo", "Hyena", "Hedgehog", "Hamster",
    "Kangaroo",
    "Leopard", "Lion", "Llama",
    "Monkey", "Moose", "Mouse",
    "Pig", "Panda",
    "Rabbit", "Racoon",
    "Rhino",
    "Skunk", "Squirrel",
    "Tiger", "Turtle",
    "Whale", "Weasel", "Wombat",
    "Yak",
    "Zebra",
    NULL
};

LandWidget *desktop;

static void game_init(LandRunner *self)
{
    land_font_load("../../data/galaxy.ttf", 12);

    desktop = land_widget_container_new(NULL, 0, 0, 640, 480);
    desktop->theme = land_widget_theme_new("../../data/classic.cfg");
}

static void construct_menu(void)
{
    int index[26];
    int i, j;
    for (i = 0; i < 26; i++)
    {
        for (j = 0; data[j]; j++)
        {
            if (data[j][0] == 'A' + i) break;
        }
        index[i] = j;
    }
    LandWidget *menu = land_widget_menu_new(desktop,
        land_mouse_x(), land_mouse_y(), 10, 10);
    for (i = 0; i < 10; i++)
    {
        char name[256];
        int h = land_rand(0, 25);
        name[0] = 'A' + h;
        name[1] = '\0';
        LandWidget *submenu = land_widget_menu_new(desktop, 0, 0, 10, 10);
        for (j = 0;  data[index[h] + j] && data[index[h] + j][0] == 'A' + h; j++)
        {
            land_widget_menuitem_new(submenu, data[index[h] + j], NULL);
        }
        land_widget_hide(submenu);
        land_widget_submenuitem_new(menu, name, submenu);
    }
}

static void game_tick(LandRunner *self)
{
    if (land_key_pressed(KEY_ESC) || land_closebutton())
        land_quit();

    if ((land_mouse_b() & 1) && (land_mouse_delta_b() & 1))
    {
        construct_menu();
    }

    land_widget_tick(desktop);
}

static void game_draw(LandRunner *self)
{
    land_widget_draw(desktop);
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
    LandRunner *game_runner = land_runner_new("menu", game_init,
        NULL, game_tick, game_draw, NULL, game_exit);
    land_runner_register(game_runner);
    land_set_initial_runner(game_runner);
    land_main();
}
