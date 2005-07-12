#ifdef _PROTOTYPE_

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "widget/base.h"
#include "widget/box.h"

WidgetInterface *widget_box_interface = NULL;

void widget_box_draw(Widget *self)
{
    widget_theme_draw(self);
}

Widget *widget_box_new(Widget *parent, int x, int y, int w, int h)
{
    Widget *self = widget_new(parent, x, y, w, h);
    if (!widget_box_interface)
        widget_box_interface_initialize();
    self->vt = widget_box_interface;
    return self;
}

void widget_box_interface_initialize(void)
{
    land_alloc(widget_box_interface);
    widget_box_interface->name = "box";
    widget_box_interface->draw = widget_box_draw;
}

