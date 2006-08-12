import base
static import land

global LandWidgetInterface *land_widget_box_interface

def land_widget_box_draw(LandWidget *self):
    land_widget_theme_draw(self)

LandWidget *def land_widget_box_new(LandWidget *parent, int x, int y, int w, int h):
    LandWidget *self = land_widget_new(parent, x, y, w, h)

    land_widget_box_interface_initialize()

    self->vt = land_widget_box_interface
    return self

def land_widget_box_interface_initialize(void):
    if land_widget_box_interface: return

    land_widget_box_interface = land_widget_copy_interface(
        land_widget_base_interface, "box")

    land_widget_box_interface->id = LAND_WIDGET_ID_BASE
    land_widget_box_interface->draw = land_widget_box_draw
