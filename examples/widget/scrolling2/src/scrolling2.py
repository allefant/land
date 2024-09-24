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
    land_find_data_prefix("data/")

    land_font_load("galaxy.ttf", 12)

    land_widget_theme_set_default(land_widget_theme_new("classic.cfg"))
    desktop = land_widget_board_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)
    
    LandWidgetInterface *my_own = land_widget_copy_interface(
        land_widget_base_interface, "mine")
    my_own->draw = colored
    
    LandWidget *notebook = land_widget_book_new(desktop, 50, 50, 540, 380)
    
    LandWidget *scrolling = land_widget_scrolling_new(notebook, 0, 0, 10, 10)
    land_widget_scrolling_autohide(scrolling, 1, 1, 2)
    land_widget_book_pagename(notebook, "Yellow (scrollbars should be hidden)")
    
    LandWidgetColored *cwidget
    land_alloc(cwidget)
    LandWidget *widget = (void *)cwidget
    land_widget_base_initialize(widget, scrolling, 0, 0, 200, 200)
    widget->vt = my_own
    cwidget->r = 1
    cwidget->g = 1
    cwidget->b = 0
    cwidget->a = 0.5
    
    scrolling = land_widget_scrolling_new(notebook, 0, 0, 10, 10)
    land_widget_scrolling_autohide(scrolling, 1, 1, 2)
    land_widget_book_pagename(notebook, "Purple (vertical)")
    
    land_alloc(cwidget)
    widget = (void *)cwidget
    land_widget_base_initialize(widget, scrolling, 0, 0, 200, 2000)
    widget->vt = my_own
    cwidget->r = 1
    cwidget->g = 0
    cwidget->b = 0.5
    cwidget->a = 0.7
    
    scrolling = land_widget_scrolling_new(notebook, 0, 0, 10, 10)
    land_widget_scrolling_autohide(scrolling, 1, 1, 2)
    land_widget_book_pagename(notebook, "Blue (horizontal)")
    
    land_alloc(cwidget)
    widget = (void *)cwidget
    land_widget_base_initialize(widget, scrolling, 0, 0, 2000, 200)
    widget->vt = my_own
    cwidget->r = 0.25
    cwidget->g = 0.25
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
