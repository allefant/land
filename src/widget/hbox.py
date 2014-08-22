#FIXME: merge hbox and vbox
import base, scrolling

class LandWidgetHBox:
    """A HBox is a container where all children are layed out in columns."""
    LandWidgetContainer super
    int rows
    bool disable_updates

macro LAND_WIDGET_HBOX(widget) ((LandWidgetHBox *) land_widget_check(widget,
    LAND_WIDGET_ID_HBOX, __FILE__, __LINE__))

static import land/land

global LandWidgetInterface *land_widget_hbox_interface

# Call this before adding *many* items to the hbox, then call
# land_widget_hbox_update when done. This can speed things up, since there is
# no need to calculate intermediate layouts for each single added item.
# 

def land_widget_hbox_disable_updates(LandWidget *base):
    LAND_WIDGET_HBOX(base)->disable_updates = 1

def land_widget_hbox_do_update(LandWidget *base):
    LAND_WIDGET_HBOX(base)->disable_updates = 0
    land_widget_layout(base)

def land_widget_hbox_update(LandWidget *base):
    land_widget_container_update(base)
    if not LAND_WIDGET_HBOX(base)->disable_updates:
        land_widget_layout(base)

static def land_widget_hbox_renumber(LandWidget *base):
    int layout = land_widget_layout_freeze(base)
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    LandWidgetHBox *hbox = LAND_WIDGET_HBOX(base)
    if container->children:
        int x = 0, y = 0
        LandListItem *item = container->children->first
        while item:
            LandWidget *child = item->data
            land_widget_layout_set_grid_position(child, x, y)
            y++
            if y == hbox->rows:
                x++
                y = 0
            item = item->next
    if layout: land_widget_layout_unfreeze(base)
    if not hbox->disable_updates:
        land_widget_hbox_do_update(base)

def land_widget_hbox_add(LandWidget *base, LandWidget *add):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    LandWidgetHBox *hbox = LAND_WIDGET_HBOX(base)

    land_widget_container_add(base, add)

    int n = container->children->count
    int columns = (n + hbox->rows - 1) / hbox->rows
    int column = columns - 1
    int row = n - column * hbox->rows - 1

    int f = land_widget_layout_freeze(base)

    land_widget_layout_set_grid_position(add, column, row)
    land_widget_layout_set_grid(base, columns, hbox->rows)

    if f: land_widget_layout_unfreeze(base)

    if not hbox->disable_updates:
        land_widget_hbox_do_update(base)

def land_widget_hbox_remove(LandWidget *base, LandWidget *rem):
    int layout = land_widget_layout_freeze(base)
    land_widget_container_remove(base, rem)
    if layout: land_widget_layout_unfreeze(base)
    
    land_widget_hbox_renumber(base)

def land_widget_hbox_set_rows(LandWidget *base, int n):
    LAND_WIDGET_HBOX(base)->rows = n

def land_widget_hbox_initialize(LandWidget *base, LandWidget *parent,
    int x, int y, int w, int h):
    land_widget_hbox_interface_initialize()

    LandWidgetHBox *self = (LandWidgetHBox *)base
    land_widget_container_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_hbox_interface
    land_widget_layout_enable(base)
    self.rows = 1

    land_widget_theme_initialize(base)

# Create a new List widget. A list is simply a container with a layout in
# rows and columns. Each time you add a widget to it, it will be placed in the
# next column/row.
# 
LandWidget *def land_widget_hbox_new(LandWidget *parent, int x, int y, int w, int h):
    LandWidgetHBox *self
    land_alloc(self)
    LandWidget *widget = (LandWidget *)self
    land_widget_hbox_initialize(widget, parent, x, y, w, h)

    return widget
    

def land_widget_hbox_interface_initialize():
    if land_widget_hbox_interface: return
    land_widget_container_interface_initialize()

    land_widget_hbox_interface = land_widget_copy_interface(
        land_widget_container_interface, "hbox")
    land_widget_hbox_interface->id |= LAND_WIDGET_ID_HBOX
    land_widget_hbox_interface->add = land_widget_hbox_add
    land_widget_hbox_interface->remove = land_widget_hbox_remove
    land_widget_hbox_interface->update = land_widget_hbox_update
