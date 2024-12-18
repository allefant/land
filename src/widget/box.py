import base
static import land/land

global LandWidgetInterface *land_widget_box_interface

def land_widget_box_draw(LandWidget *self):
    land_widget_theme_draw(self)

def land_widget_box_new(LandWidget *parent, int x, y, w, h) -> LandWidget *:
    LandWidget *self = land_widget_base_new(parent, x, y, w, h)

    land_widget_box_interface_initialize()

    self.vt = land_widget_box_interface
    
    land_widget_theme_initialize(self)

    land_call_method(parent, update, (parent))

    return self

def land_widget_box_interface_initialize():
    if land_widget_box_interface: return

    land_widget_box_interface = land_widget_copy_interface(
        land_widget_base_interface, "box")

    land_widget_box_interface->id = LAND_WIDGET_ID_BASE
    land_widget_box_interface->draw = land_widget_box_draw

def land_widget_space_new(LandWidget *parent) -> LandWidget*:
    LandWidget *self = land_widget_base_new(parent, 0, 0, 0, 0)
    land_widget_layout_set_expanding(self, 1, 1)
    return self
