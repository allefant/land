import base, container

class LandWidgetMover:
    LandWidget super
    LandWidget *target
    int dragged

macro LAND_WIDGET_MOVER(widget) ((LandWidgetMover *)widget)

static import land

LandWidgetInterface *land_widget_mover_interface = NULL

def land_widget_mover_draw(LandWidget *self):
    land_widget_theme_draw(self)

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


LandWidget *def land_widget_mover_new(LandWidget *parent, int x, int y, int w, int h):
    LandWidgetMover *self

    land_widget_mover_interface_initialize()

    land_alloc(self)
    LandWidget *super = &self->super
    land_widget_base_initialize(super, parent, x, y, w, h)
    super->vt = land_widget_mover_interface
    # by default, move the parent. 
    self->target = parent
    self->dragged = 0
    return super

def land_widget_mover_set_target(LandWidget *self, LandWidget *target):
    LAND_WIDGET_MOVER(self)->target = target

def land_widget_mover_interface_initialize():
    if land_widget_mover_interface: return

    land_widget_mover_interface = land_widget_copy_interface(
        land_widget_base_interface, "mover")
    land_widget_mover_interface->draw = land_widget_mover_draw
    land_widget_mover_interface->mouse_tick = land_widget_mover_mouse_tick
