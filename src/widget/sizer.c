#ifdef _PROTOTYPE_

typedef struct WidgetSizer WidgetSizer;

#include "base.h"
#include "layout.h"

struct WidgetSizer
{
    Widget super;
    Widget *target;
    int dragged;
    int drag_x, drag_y;
};

#define WIDGET_SIZER(widget) ((WidgetSizer *)widget)

#endif /* _PROTOTYPE_ */

#include "widget/sizer.h"

WidgetInterface *widget_sizer_interface = NULL;

void widget_sizer_draw(Widget *self)
{
    float r = 1, g = 0, b = 0;
    if (self->got_mouse)
        g = 1;
    land_color(r, g, b, 1);
    land_rectangle(self->box.x, self->box.y, self->box.x + self->box.w - 1,
        self->box.y + self->box.h - 1);
}

void widget_sizer_mouse_tick(Widget *super)
{
    WidgetSizer *self = WIDGET_SIZER(super);
    int r = self->target->box.x + self->target->box.w - 1;
    int b = self->target->box.y + self->target->box.h - 1;
    if (land_mouse_delta_b())
    {
        if (land_mouse_b() & 1)
        {
            self->dragged = 1;
            self->drag_x = r - land_mouse_x();
            self->drag_y = b - land_mouse_y();
        }
        else
            self->dragged = 0;
    }

    if ((land_mouse_b() & 1) && self->dragged)
    {
        widget_size(self->target,land_mouse_x() -  r + self->drag_x,
            land_mouse_y() - b + self->drag_y);
    }
}

Widget *widget_sizer_new(Widget *parent, int x, int y, int w, int h)
{
    WidgetSizer *self;
    if (!widget_sizer_interface)
        widget_sizer_interface_initialize();
    land_alloc(self);
    Widget *super = WIDGET(self);
    widget_base_initialize(super, parent, x, y, w, h);
    super->vt = widget_sizer_interface;
    /* by default, size the parent. */
    self->target = parent;
    self->dragged = 0;
    return super;
}

void widget_sizer_interface_initialize(void)
{
    land_alloc(widget_sizer_interface);
    widget_sizer_interface->name = "sizer";
    widget_sizer_interface->draw = widget_sizer_draw;
    widget_sizer_interface->mouse_tick = widget_sizer_mouse_tick;
    widget_sizer_interface->mouse_enter = widget_base_mouse_enter;
    widget_sizer_interface->mouse_leave = widget_base_mouse_leave;
}

