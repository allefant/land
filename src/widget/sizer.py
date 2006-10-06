import base, layout

class LandWidgetSizer:
    LandWidget super
    LandWidget *target
    int dragged
    int drag_x, drag_y

macro LAND_WIDGET_SIZER(widget) ((LandWidgetSizer *)widget)

LandWidgetInterface *land_widget_sizer_interface = NULL

def land_widget_sizer_draw(LandWidget *self):
    land_widget_theme_draw(self)
    float x = self->box.x + self->box.il;
    float y = self->box.y + self->box.it;
    float x_ = self->box.x + self->box.w - self->box.ir;
    float y_ = self->box.y + self->box.h - self->box.ib;
    land_color(1, 1, 1, 0.5)
    land_line(x_, y, x, y_)
    land_line(x_, y + 3, x + 3, y_)
    land_line(x_, y + 6, x + 6, y_)
    land_color(0, 0, 0, 0.5)
    land_line(x_, y + 1, x + 1, y_)
    land_line(x_, y + 4, x + 4, y_)
    land_line(x_, y + 7, x + 7, y_)

def land_widget_sizer_mouse_tick(LandWidget *super):
    LandWidgetSizer *self = LAND_WIDGET_SIZER(super)
    int r = self->target->box.x + self->target->box.w - 1
    int b = self->target->box.y + self->target->box.h - 1
    if (land_mouse_delta_b()):
        if (land_mouse_b() & 1):
            self->dragged = 1
            self->drag_x = r - land_mouse_x()
            self->drag_y = b - land_mouse_y()

        else:
            self->dragged = 0

    if ((land_mouse_b() & 1) && self->dragged):
        land_widget_size(self->target, land_mouse_x() - r + self->drag_x,
            land_mouse_y() - b + self->drag_y)


LandWidget *def land_widget_sizer_new(LandWidget *parent, int x, y, w, h):
    LandWidgetSizer *self
    
    land_widget_sizer_interface_initialize()
    
    # FIXME: inhibit layout changes until our own vt is set

    land_alloc(self)
    LandWidget *super = &self->super
    land_widget_base_initialize(super, parent, x, y, w, h)
    super->vt = land_widget_sizer_interface

    land_widget_layout_set_shrinking(super, 1, 1)
    land_widget_theme_layout_border(super)
    if parent: land_widget_layout(parent)
    
    # by default, size the parent. 
    self->target = parent
    self->dragged = 0

    return super

def land_widget_sizer_interface_initialize():
    if land_widget_sizer_interface: return

    land_widget_sizer_interface = land_widget_copy_interface(
        land_widget_base_interface, "sizer")
    land_widget_sizer_interface->draw = land_widget_sizer_draw
    land_widget_sizer_interface->mouse_tick = land_widget_sizer_mouse_tick
