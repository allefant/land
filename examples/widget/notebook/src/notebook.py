import global stdlib
import global string

import global land/land

LandWidget *desktop
LandWidget *notebook

LandWidgetTheme *theme
LandWidgetTheme *classic, *green

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

    classic = land_widget_theme_new("classic.cfg")
    green = land_widget_theme_new("green.cfg")
    theme = green
    land_widget_theme_set_default(theme)
    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    notebook = land_widget_book_new(desktop, 50, 50, 200, 200)

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

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()
        
    if land_key_pressed(LandKeyDelete):
        LandWidget *page = land_widget_book_get_current_page(notebook)
        land_widget_book_remove_page(notebook, page)

    if land_key_pressed(' '):
        if theme == green: theme = classic
        else: theme = green
        land_widget_theme_apply(desktop, theme)

    land_widget_tick(desktop)

def _print(char const *str, ...):
    va_list args
    va_start(args, str)
    char t[1024]
    vsnprintf(t, sizeof t, str, args)
    va_end(args)

    float x = land_text_x_pos()
    float y = land_text_y_pos()
    land_color(0, 0, 0, 1)
    land_text_pos(x - 1, y)
    land_print(t)
    land_text_pos(x + 1, y)
    land_print(t)
    land_text_pos(x, y - 1)
    land_print(t)
    land_text_pos(x, y + 1)
    land_print(t)
    land_text_pos(x, y)
    land_color(1, 1, 1, 1)
    land_print(t)

static def debug(LandWidget *w):
    _print("* %p [%s(%d): %s%s%s%s]", w, w->vt->name, w->reference,
        w->no_layout ? "N" : "",
        w->hidden ? "H" : "",
        w->box.flags & GUL_SHRINK_X ? "X" : "",
        w->box.flags & GUL_SHRINK_Y ? "Y" : "")
    if land_widget_is(w, LAND_WIDGET_ID_CONTAINER):
        LandList *l = LAND_WIDGET_CONTAINER(w)->children
        land_text_pos(land_text_x_pos() + 10, land_text_y_pos())
        if not land_widget_container_is_empty(w):
            LandListItem *i = l->first
            while i:
                LandWidget *w = i->data
                debug(w)
                i = i->next
        else:
            _print("(empty)")
        land_text_pos(land_text_x_pos() - 10, land_text_y_pos())

def _draw(LandRunner *self):
    land_widget_draw(desktop)
    
    land_text_pos(300, 50)
    debug(desktop)

def _done(LandRunner *self):
    land_widget_theme_destroy(land_widget_theme_default())
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
