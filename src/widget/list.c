#ifdef _PROTOTYPE_

#include "base.h"
#include "scrolling.h"

typedef struct LandWidgetList LandWidgetList;

struct LandWidgetList
{
    LandWidgetContainer super;
    int columns;
    int disable_updates : 1;
};

#define LAND_WIDGET_LIST(widget) ((LandWidgetList *) \
    land_widget_check(widget, LAND_WIDGET_ID_LIST, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "list.h"

LandWidgetInterface *land_widget_list_interface = NULL;

/* Call this before adding *many* items to the list, then call
 * land_widget_list_update when done. This can speed things up, since there is
 * no need to calculate intermediate layouts for each single added item.
 */

void land_widget_list_disable_updates(LandWidget *base)
{
    LAND_WIDGET_LIST(base)->disable_updates = 1;
}

void land_widget_list_update(LandWidget *base)
{
    LAND_WIDGET_LIST(base)->disable_updates = 0;
    land_widget_layout_adjust(base, 1, 1, 1);
}

void land_widget_list_add(LandWidget *base, LandWidget *add)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base);
    LandWidgetList *list = LAND_WIDGET_LIST(base);

    land_widget_container_add(base, add);
    
    int n = container->children->count;
    int rows = (n + list->columns - 1) / list->columns;
    int row = rows - 1;
    int column = n - row * list->columns - 1;

    land_widget_layout_set_grid_position(add, column, row, 0);
    land_widget_layout_set_grid(base, list->columns, n, 0);
    
    land_widget_layout_set_shrinking(add, 0, 1);
    land_widget_layout_add(base, add, 0);

    if (!list->disable_updates)
    {
        land_widget_list_update(base);
    }
}



void land_widget_list_set_columns(LandWidget *base, int n)
{
    LAND_WIDGET_LIST(base)->columns = n;
}

void land_widget_list_initialize(LandWidgetList *self, LandWidget *parent,
    int x, int y, int w, int h)
{
    land_widget_list_interface_initialize();

    LandWidgetContainer *super = &self->super;
    land_widget_container_initialize(super, parent, x, y, w, h);
    LandWidget *base = &super->super;
    base->vt = land_widget_list_interface;
    self->columns = 1;
   
    land_widget_theme_layout_border(base);
}

/* Create a new List widget. A list is simply a container with a layout in
 * rows and columns. Each time you add a widget to it, it will be placed in the
 * next column/row.
 */
LandWidget *land_widget_list_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetList *self = calloc(1, sizeof *self);
    land_widget_list_initialize(self, parent, x, y, w, h);

    return LAND_WIDGET(self);
}

void land_widget_list_interface_initialize(void)
{
    if (land_widget_list_interface) return;

    land_widget_list_interface = land_widget_copy_interface(
        land_widget_container_interface, "list");
    land_widget_list_interface->id |= LAND_WIDGET_ID_LIST;
    land_widget_list_interface->add = land_widget_list_add;
}
