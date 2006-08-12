#ifdef _PROTOTYPE_

#include "base.h"
#include "scrolling.h"

typedef struct LandWidgetVBox LandWidgetVBox;

/* A VBox is a container where new children will be added in rows. It's layout
 * will adjust to the children.
 */
struct LandWidgetVBox
{
    LandWidgetContainer super;
    int columns;
    int disable_updates : 1;
};

#define LAND_WIDGET_VBOX(widget) ((LandWidgetVBox *) \
    land_widget_check(widget, LAND_WIDGET_ID_VBOX, __FILE__, __LINE__))

extern LandWidgetInterface *land_widget_vbox_interface;

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "widget/vbox.h"

LandWidgetInterface *land_widget_vbox_interface;

/* Call this before adding *many* items to the vbox, then call
 * land_widget_vbox_update when done. This can speed things up, since there is
 * no need to calculate intermediate layouts for each single added item.
 */

void land_widget_vbox_disable_updates(LandWidget *base)
{
    LAND_WIDGET_VBOX(base)->disable_updates = 1;
}

void land_widget_vbox_update(LandWidget *base)
{
    LAND_WIDGET_VBOX(base)->disable_updates = 0;
    land_widget_layout_adjust(base, 1, 1);
}

void land_widget_vbox_add(LandWidget *base, LandWidget *add)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base);
    LandWidgetVBox *vbox = LAND_WIDGET_VBOX(base);

    land_widget_container_add(base, add);

    int n = container->children->count;
    int rows = (n + vbox->columns - 1) / vbox->columns;
    int row = rows - 1;
    int column = n - row * vbox->columns - 1;
    
    land_widget_layout_inhibit(base);

    land_widget_layout_set_grid_position(add, column, row);
    land_widget_layout_set_grid(base, vbox->columns, rows);

    land_widget_layout_set_shrinking(add, 0, 1);
    land_widget_layout_add(base, add);
    
    land_widget_layout_enable(base);

    if (!vbox->disable_updates)
    {
        land_widget_vbox_update(base);
    }
}

void land_widget_vbox_set_columns(LandWidget *base, int n)
{
    LAND_WIDGET_VBOX(base)->columns = n;
}

void land_widget_vbox_initialize(LandWidget *base, LandWidget *parent,
    int x, int y, int w, int h)
{
    land_widget_vbox_interface_initialize();

    LandWidgetVBox *self = (LandWidgetVBox *)base;
    land_widget_container_initialize(base, parent, x, y, w, h);
    base->vt = land_widget_vbox_interface;
    self->columns = 1;
   
    land_widget_theme_layout_border(base);
}

/* Create a new List widget. A list is simply a container with a layout in
 * rows and columns. Each time you add a widget to it, it will be placed in the
 * next column/row.
 */
LandWidget *land_widget_vbox_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetVBox *self;
    land_alloc(self);
    LandWidget *widget = (LandWidget *)self;
    land_widget_vbox_initialize(widget, parent, x, y, w, h);

    return widget;
}

void land_widget_vbox_interface_initialize(void)
{
    if (land_widget_vbox_interface) return;
    land_widget_container_interface_initialize();

    land_widget_vbox_interface = land_widget_copy_interface(
        land_widget_container_interface, "vbox");
    land_widget_vbox_interface->id |= LAND_WIDGET_ID_VBOX;
    land_widget_vbox_interface->add = land_widget_vbox_add;
}
