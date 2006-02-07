#ifdef _PROTOTYPE_

#include "base.h"
#include "scrolling.h"

typedef struct WidgetList WidgetList;

struct WidgetList
{
    WidgetContainer super;
    int columns;
};


#define WIDGET_LIST(widget) ((WidgetList *)widget)

#endif /* _PROTOTYPE_ */

#include "land.h"

WidgetInterface *widget_list_interface = NULL;

void widget_list_add(Widget *base, Widget *add)
{
    widget_container_add(base, add);
    WidgetContainer *container = WIDGET_CONTAINER(base);
    int n = container->children->count;

    widget_layout_set_grid_position(add, 0, n - 1);
    widget_layout_add(base, add);
    widget_layout_set_minimum_size(add, 10, 10);
    widget_layout_set_shrinking(add, 0, 1);

    widget_layout_set_grid(base, 1, n);
    //widget_layout_set_shrinking(base, 0, 1);
    widget_layout_set_border(base, 2, 2, 2, 2, 1, 1);
    widget_layout(base);
}

void widget_list_initialize(WidgetList *self, Widget *parent, int x, int y, int w, int h)
{
   if (!widget_list_interface)
        widget_list_interface_initialize();
   WidgetContainer *super = &self->super;
   widget_container_initialize(super, parent, x, y, w, h);
   Widget *base = &super->super;
   base->vt = widget_list_interface;
}

Widget *widget_list_new(Widget *parent, int x, int y, int w, int h)
{
    WidgetList *self = calloc(1, sizeof *self);
    widget_list_initialize(self, parent, x, y, w, h);

    return WIDGET(self);
}

void widget_list_interface_initialize(void)
{
    widget_list_interface = calloc(1, sizeof *widget_list_interface);
    memcpy(widget_list_interface, widget_container_interface,
        sizeof *widget_list_interface);
    widget_list_interface->name = "list";
    widget_list_interface->add = widget_list_add;
}

