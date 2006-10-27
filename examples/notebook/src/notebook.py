import global stdlib
import global string

import global land/land

LandWidget *desktop

class LandWidgetColored:
    LandWidget super
    float r, g, b, a

static def colored(LandWidget *self):
    LandWidgetColored *c = (void *)self
    land_color(c->r, c->g, c->b, c->a)
    land_filled_rectangle(self->box.x, self->box.y, self->box.x + self->box.w,
        self->box.y + self->box.h)

static def game_init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("../../data/classic.cfg"))
    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480)

    LandWidget *notebook = land_widget_book_new(desktop, 50, 50, 200, 200)

    LandWidgetInterface *my_own = land_widget_copy_interface(land_widget_base_interface, "mine")
    my_own->draw = colored

    LandWidgetColored *widget
    land_alloc(widget)
    land_widget_base_initialize(&widget->super, notebook, 0, 0, 20, 20)
    land_widget_book_pagename(notebook, "yellow")
    widget->super.vt = my_own
    widget->r = 1
    widget->g = 1
    widget->b = 0
    widget->a = 0.5

    land_alloc(widget)
    land_widget_base_initialize(&widget->super, notebook, 0, 0, 20, 20)
    land_widget_book_pagename(notebook, "blue")
    widget->super.vt = my_own
    widget->r = 0
    widget->g = 0
    widget->b = 1
    widget->a = 0.5

    land_alloc(widget)
    land_widget_base_initialize(&widget->super, notebook, 0, 0, 20, 20)
    land_widget_book_pagename(notebook, "green")
    widget->super.vt = my_own
    widget->r = 0
    widget->g = 0.5
    widget->b = 0
    widget->a = 0.5

    land_widget_layout(notebook)

static def game_tick(LandRunner *self):
    if land_key_pressed(KEY_ESC) || land_closebutton():
        land_quit()

    land_widget_tick(desktop)

static def game_draw(LandRunner *self):
    land_widget_draw(desktop)

static def game_exit(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

def begin():
    land_init()
    land_set_display_parameters(640, 480, 32, 100, LAND_WINDOWED | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("notebook", game_init,
        NULL, game_tick, game_draw, NULL, game_exit)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_main()

land_use_main(begin)
