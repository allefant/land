#ifdef _PROTOTYPE_

typedef struct LandWidgetMover LandWidgetMover;

#include "base.h"
#include "container.h"

struct LandWidgetMover
{
    LandWidget super;
    LandWidget *target;
    int dragged;
};

#define LAND_WIDGET_MOVER(widget) ((LandWidgetMover *)widget)

#endif /* _PROTOTYPE_ */

#include "land.h"

LandWidgetInterface *land_widget_mover_interface = NULL;

void land_widget_mover_draw(LandWidget *self)
{
    land_widget_theme_draw(self);
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

void land_widget_mover_mouse_tick(LandWidget *super)
{
    LandWidgetMover *self = LAND_WIDGET_MOVER(super);
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
        land_widget_move(self->target, land_mouse_delta_x(), land_mouse_delta_y());
    }
}

LandWidget *land_widget_mover_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetMover *self;
    if (!land_widget_mover_interface)
        land_widget_mover_interface_initialize();
    land_alloc(self);
    LandWidget *super = LAND_WIDGET(self);
    land_widget_base_initialize(super, parent, x, y, w, h);
    super->vt = land_widget_mover_interface;
    /* by default, move the parent. */
    self->target = parent;
    self->dragged = 0;
    return super;
}

void land_widget_mover_interface_initialize(void)
{
    land_alloc(land_widget_mover_interface);
    land_widget_mover_interface->name = "mover";
    land_widget_mover_interface->draw = land_widget_mover_draw;
    land_widget_mover_interface->mouse_tick = land_widget_mover_mouse_tick;
    land_widget_mover_interface->mouse_enter = land_widget_base_mouse_enter;
    land_widget_mover_interface->mouse_leave = land_widget_base_mouse_leave;
}

