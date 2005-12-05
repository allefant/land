#ifdef _PROTOTYPE_

typedef struct WidgetMover WidgetMover;

#include "base.h"
#include "container.h"

struct WidgetMover
{
    Widget super;
    Widget *target;
    int dragged;
};

#define WIDGET_MOVER(widget) ((WidgetMover *)widget)

#endif /* _PROTOTYPE_ */

#include "land.h"

WidgetInterface *widget_mover_interface = NULL;

void widget_mover_draw(Widget *self)
{
    widget_theme_draw(self);
    /*float r = 1, g = 0, b = 0;
    if (self->got_mouse)
        g = 1;
    land_color(r, g, b);
    land_filled_rectangle(self->box.x + 1, self->box.y + 1, self->box.x + self->box.w - 2,
        self->box.y + self->box.h - 2);
    land_color(r / 2, g / 2, b / 2);
    land_rectangle(self->box.x, self->box.y, self->box.x + self->box.w - 1,
        self->box.y + self->box.h - 1);
    land_text_pos(self->box.x, self->box.y);
    land_print("%p", self);*/
}

void widget_mover_mouse_tick(Widget *super)
{
    WidgetMover *self = WIDGET_MOVER(super);
    if (land_mouse_delta_b())
    {
        if (land_mouse_b() & 1)
        {
            self->target->send_to_top = 1;
            self->dragged = 1;
        }
        else
            self->dragged = 0;
    }

    if ((land_mouse_b() & 1) && self->dragged)
    {
        widget_move(self->target, land_mouse_delta_x(), land_mouse_delta_y());
    }
}

Widget *widget_mover_new(Widget *parent, int x, int y, int w, int h)
{
    WidgetMover *self;
    if (!widget_mover_interface)
        widget_mover_interface_initialize();
    land_alloc(self);
    Widget *super = WIDGET(self);
    widget_base_initialize(super, parent, x, y, w, h);
    super->vt = widget_mover_interface;
    /* by default, move the parent. */
    self->target = parent;
    self->dragged = 0;
    return super;
}

void widget_mover_interface_initialize(void)
{
    land_alloc(widget_mover_interface);
    widget_mover_interface->name = "mover";
    widget_mover_interface->draw = widget_mover_draw;
    widget_mover_interface->mouse_tick = widget_mover_mouse_tick;
    widget_mover_interface->mouse_enter = widget_base_mouse_enter;
    widget_mover_interface->mouse_leave = widget_base_mouse_leave;
}

