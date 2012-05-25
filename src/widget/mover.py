import base, container, button

class LandWidgetMover:
    LandWidgetButton super
    LandWidget *target
    int dragged

macro LAND_WIDGET_MOVER(widget) ((LandWidgetMover *)widget)

static import land/land

static LandWidgetInterface *land_widget_mover_interface

def land_widget_mover_mouse_tick(LandWidget *super):
    LandWidgetMover *self = LAND_WIDGET_MOVER(super)
    if (land_mouse_delta_b()):
        if land_mouse_b() & 1:
            self->target->send_to_top = 1
            self->dragged = 1
        else:
            self->dragged = 0

    if (land_mouse_b() & 1) and self->dragged:
        land_widget_move(self->target, land_mouse_delta_x(), land_mouse_delta_y())


LandWidget *def land_widget_mover_new(LandWidget *parent, char const *text, int x, int y, int w, int h):
    """Create a new mover widget.
    
    By default, the widget will stretch in the horizontal and shrink in the
    vertical direction.
    """
    LandWidgetMover *self

    land_widget_mover_interface_initialize()

    # FIXME: inhibit layout changes until our own vt is set

    land_alloc(self)
    LandWidget *base = (LandWidget *)self
    land_widget_button_initialize(base, parent, text, None, None, x, y, w, h)
    base->vt = land_widget_mover_interface
    
    land_widget_layout_set_shrinking(base, 0, 1)
    land_widget_theme_initialize(base)
    if parent: land_widget_layout(parent)

    # by default, move the parent. 
    self->target = parent
    self->dragged = 0
    return base

def land_widget_mover_set_target(LandWidget *self, LandWidget *target):
    LAND_WIDGET_MOVER(self)->target = target

def land_widget_mover_interface_initialize():
    if land_widget_mover_interface: return

    land_widget_button_interface_initialize()
    land_widget_mover_interface = land_widget_copy_interface(
        land_widget_button_interface, "mover")
    land_widget_mover_interface->mouse_tick = land_widget_mover_mouse_tick
