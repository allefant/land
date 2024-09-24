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

def _init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("../../data/classic.cfg"))
    desktop = land_widget_board_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandWidget *window = land_widget_vbox_new(desktop, 50, 50, 200, 200)
    land_widget_layout_set_shrinking(window, 1, 1)
    land_widget_vbox_set_columns(window, 3)
    
    land_widget_sizer_new(window, 7, 0, 0, 4, 4)
    land_widget_sizer_new(window, 0, 0, 0, 4, 4)
    land_widget_sizer_new(window, 1, 0, 0, 4, 4)
    land_widget_sizer_new(window, 6, 0, 0, 4, 4)

    LandWidgetInterface *my_own = land_widget_copy_interface(
        land_widget_base_interface, "mine")
    my_own->draw = colored

    LandWidgetColored *widget
    land_alloc(widget)
    land_widget_base_initialize(&widget->super, window, 0, 0, 20, 20)
    widget->super.vt = my_own
    widget->r = 1
    widget->g = 1
    widget->b = 0
    widget->a = 0.5

    land_widget_sizer_new(window, 2, 0, 0, 4, 4)
    land_widget_sizer_new(window, 5, 0, 0, 4, 4)
    land_widget_sizer_new(window, 4, 0, 0, 4, 4)
    land_widget_sizer_new(window, 3, 0, 0, 4, 4)   

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_widget_draw(desktop)

def _done(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
