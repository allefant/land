#include <stdlib.h>
#include <string.h>

#include <land/land.h>

LandWidget *desktop;

typedef struct
{
    LandWidget super;
    float r, g, b, a;
}
LandWidgetColored;

static void colored(LandWidget *self)
{
    LandWidgetColored *c = (void *)self;
    land_color(c->r, c->g, c->b, c->a);
    land_filled_rectangle(self->box.x, self->box.y, self->box.x + self->box.w,
        self->box.y + self->box.h);
}

static void game_init(LandRunner *self)
{
    land_font_load("../../data/galaxy.ttf", 12);

    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480);
    desktop->theme = land_widget_theme_new("../../data/classic.cfg");

    LandWidget *notebook = land_widget_book_new(desktop, 50, 50, 200, 200);

    LandWidgetInterface *my_own = land_widget_copy_interface(land_widget_base_interface, "mine");
    my_own->draw = colored;

    LandWidgetColored *widget;
    land_alloc(widget);
    land_widget_base_initialize(&widget->super, notebook, 0, 0, 20, 20);
    land_widget_book_pagename(notebook, "yellow");
    widget->super.vt = my_own;
    widget->r = 1;
    widget->g = 1;
    widget->b = 0;
    widget->a = 0.5;

    land_alloc(widget);
    land_widget_base_initialize(&widget->super, notebook, 0, 0, 20, 20);
    land_widget_book_pagename(notebook, "blue");
    widget->super.vt = my_own;
    widget->r = 0;
    widget->g = 0;
    widget->b = 1;
    widget->a = 0.5;

    land_alloc(widget);
    land_widget_base_initialize(&widget->super, notebook, 0, 0, 20, 20);
    land_widget_book_pagename(notebook, "green");
    widget->super.vt = my_own;
    widget->r = 0;
    widget->g = 0.5;
    widget->b = 0;
    widget->a = 0.5;

    land_widget_layout(notebook);
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
    LandRunner *game_runner = land_runner_new("notebook", game_init,
        NULL, game_tick, game_draw, NULL, game_exit);
    land_runner_register(game_runner);
    land_set_initial_runner(game_runner);
    land_main();
}
