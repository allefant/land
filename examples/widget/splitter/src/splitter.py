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
    
    LandWidgetInterface *my_own = land_widget_copy_interface(
        land_widget_base_interface, "mine")
    my_own->draw = colored

    LandWidget *window = land_widget_hbox_new(desktop, 50, 50, 540, 380)
    land_widget_layout_set_maximum_size(window, 540, 380)
    
    LandWidget *left = land_widget_panel_new(window, 0, 0, 0, 0)
    LandWidgetColored *cwidget
    land_alloc(cwidget)
    LandWidget *widget = (void *)cwidget
    land_widget_base_initialize(widget, left, 0, 0, 20, 20)
    widget->vt = my_own
    cwidget->r = 1
    cwidget->g = 1
    cwidget->b = 0
    cwidget->a = 0.5
    land_widget_layout_set_shrinking(left, 1, 1)
    
    LandWidget *splitter = land_widget_sizer_new(window, 2, 0, 0, 4, 4)
    land_widget_sizer_set_target(splitter, left)
    
    LandWidget *right = land_widget_panel_new(window, 0, 0, 0, 0)
    land_alloc(cwidget)
    widget = (void *)cwidget
    land_widget_base_initialize(widget, right, 0, 0, 20, 20)
    widget->vt = my_own
    cwidget->r = 0
    cwidget->g = 0.5
    cwidget->b = 1
    cwidget->a = 0.5


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
