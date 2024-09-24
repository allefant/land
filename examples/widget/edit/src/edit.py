import global stdlib
import global string

import global land/land

LandWidget *desktop
LandWidgetTheme *theme

LandImage *prev, *current

LandWidget *edit_text
LandWidget *edit_red
LandWidget *edit_green
LandWidget *edit_blue
LandWidget *slider_red
LandWidget *slider_green
LandWidget *slider_blue

LandFont *af

static def redraw(LandWidget *self):
    LandImage *temp = prev
    prev = current
    current = temp
    LandFont *f = land_font_current()
    land_font_set(af)
    land_set_image_display(current)
    land_clear(0, 0, 0, 1)
    float r = land_widget_spin_get_value(edit_red)
    float g = land_widget_spin_get_value(edit_green)
    float b = land_widget_spin_get_value(edit_blue)
    land_color(r, g, b, 1)
    land_line(0, 0, 128, 0)
    char const *text = land_widget_edit_get_text(edit_text)
    land_text_pos(64, 64)
    land_print_center(text)
    land_unset_image_display()

    land_font_set(f)

static def slider(LandWidget *self):
    float r = land_widget_slider_get_value(slider_red)
    float g = land_widget_slider_get_value(slider_green)
    float b = land_widget_slider_get_value(slider_blue)
    land_widget_spin_set_value(edit_red, r)
    land_widget_spin_set_value(edit_green, g)
    land_widget_spin_set_value(edit_blue, b)
    redraw(self)

def _init(LandRunner *self):
    land_find_data_prefix("data/")
    af = land_font_load("galaxy.ttf", 20)

    int dpi = land_display_dpi()
    int pixels = 10 * dpi / 72
    land_font_load("galaxy.ttf", pixels)

    theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandWidget *vbox = land_widget_vbox_new(desktop, 10, 10, 10, 10)
    land_widget_vbox_set_columns(vbox, 3)
    land_widget_text_new(vbox, "Text", 0, 0, 0, 1, 1)
    land_widget_box_new(vbox, 0, 0, 100, 0)
    edit_text = land_widget_edit_new(vbox, "Land", redraw, 0, 0, 100, 0)
    
    land_widget_text_new(vbox, "Red", 0, 0, 0, 1, 1)
    slider_red = land_widget_slider_new(vbox, 0, 1, False, slider, 0, 0, 0, 0)
    edit_red = land_widget_spin_new(vbox, 0.5, 0, 1, 0.01, redraw, 0, 0, 0, 0)
    
    land_widget_text_new(vbox, "Green", 0, 0, 0, 1, 1)
    slider_green = land_widget_slider_new(vbox, 0, 1, False, slider, 0, 0, 0, 0)
    edit_green = land_widget_spin_new(vbox, 0.5, 0, 1, 0.01, redraw, 0, 0, 0, 0)
    
    land_widget_text_new(vbox, "Blue", 0, 0, 0, 1, 1)
    slider_blue = land_widget_slider_new(vbox, 0, 1, False, slider, 0, 0, 0, 0)
    edit_blue = land_widget_spin_new(vbox, 0.5, 0, 1, 0.01, redraw, 0, 0, 0, 0)

    land_widget_layout_set_shrinking(vbox, 1, 1)
    land_widget_layout(vbox)

    prev = land_image_create(128, 128)
    current = land_image_create(128, 128)

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    if land_was_resized():
        pass

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_widget_draw(desktop)

    land_image_draw(prev, 320, 10)
    land_image_draw(current, 320, 20 + 128)

def _done(LandRunner *self):
    land_widget_theme_destroy(theme)
    land_widget_unreference(desktop)
    land_font_destroy(land_font_current())

land_standard_example()
