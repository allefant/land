import container

class LandWidgetBoard:
    """
    A board widget can have several children but has no layout of any kind.
    """
    LandWidgetContainer super

macro LAND_WIDGET_BOARD(widget) ((LandWidgetBoard *) land_widget_check(widget,
    LAND_WIDGET_ID_BOARD, __FILE__, __LINE__))

static import land/land

global LandWidgetInterface *land_widget_board_interface

def land_widget_board_initialize(LandWidget *base,
    LandWidget *parent, int x, int y, int w, int h):
    LandWidgetBoard *self = (LandWidgetBoard *)base
    land_widget_board_interface_initialize()
    LandWidgetContainer *super = &self.super
    land_widget_container_initialize(&super->super, parent, x, y, w, h)
    base->vt = land_widget_board_interface
    land_widget_theme_initialize(base)

def land_widget_board_new(LandWidget *parent, int x, y, w, h) -> LandWidget *:
    LandWidgetBoard *self
    land_alloc(self)
    land_widget_board_initialize((LandWidget *)self, parent, x, y, w, h)
    return LAND_WIDGET(self)

def land_widget_board_add(LandWidget *base, LandWidget *add):
    land_widget_container_add(base, add)

def land_widget_board_interface_initialize():
    land_widget_container_interface_initialize()
    land_widget_board_interface = land_widget_copy_interface(
        land_widget_container_interface, "board")
    land_widget_board_interface->id |= LAND_WIDGET_ID_BOARD
    land_widget_board_interface->add = land_widget_board_add
