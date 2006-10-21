#FIXME: merge hbox and vbox
import base, scrolling

class LandWidgetVBox:
    """A VBox is a container where all children are layed out in rows."""
    LandWidgetContainer super
    int columns
    int disable_updates : 1

macro LAND_WIDGET_VBOX(widget) ((LandWidgetVBox *)land_widget_check(widget,
    LAND_WIDGET_ID_VBOX, __FILE__, __LINE__))

static import land

global LandWidgetInterface *land_widget_vbox_interface

def land_widget_vbox_disable_updates(LandWidget *base):
    """
    Call this before adding *many* items to the vbox, then call
    land_widget_vbox_update when done. This can speed things up, since there is
    no need to calculate intermediate layouts for each single added item.
    """
    LAND_WIDGET_VBOX(base)->disable_updates = 1

def land_widget_vbox_update(LandWidget *base):
    """
    Update the vbox, after updates have previously been disabled with
    land_widget_vbox_disable_updates.
    """
    LAND_WIDGET_VBOX(base)->disable_updates = 0
    land_widget_layout(base)

static def land_widget_vbox_renumber(LandWidget *base):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    LandWidgetVBox *vbox = LAND_WIDGET_VBOX(base)
    if container->children:
        int x = 0, y = 0
        LandListItem *item = container->children->first
        while item:
            LandWidget *child = item->data
            land_widget_layout_set_grid_position(child, x, y)
            x++
            if x == vbox->columns:
                x = 0
                y++
            item = item->next
    if !vbox->disable_updates:
        land_widget_vbox_update(base)

def land_widget_vbox_add(LandWidget *base, LandWidget *add):
    """
    Add a widget to the vbox. It will be put to the end, going left to right
    in columns and top to bottom in rows.
    """
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    LandWidgetVBox *vbox = LAND_WIDGET_VBOX(base)

    land_widget_container_add(base, add)

    int n = container->children->count
    int rows = (n + vbox->columns - 1) / vbox->columns
    int row = rows - 1
    int column = n - row * vbox->columns - 1
    
    int layout = land_widget_layout_freeze(base)

    land_widget_layout_set_grid_position(add, column, row)
    land_widget_layout_set_grid(base, vbox->columns, rows)

    if layout: land_widget_layout_unfreeze(base)

    if !vbox->disable_updates:
        land_widget_vbox_update(base)

def land_widget_vbox_remove(LandWidget *base, LandWidget *rem):
    """Remove a widget from the vbox."""
    int layout = land_widget_layout_freeze(base)
    land_widget_container_remove(base, rem)
    if layout: land_widget_layout_unfreeze(base)

    land_widget_vbox_renumber(base)

def land_widget_vbox_set_columns(LandWidget *base, int n):
    """Specify the number of columns for the vbox. By default, it is 1."""
    LAND_WIDGET_VBOX(base)->columns = n

def land_widget_vbox_initialize(LandWidget *base, LandWidget *parent,
    int x, int y, int w, int h):
    """Initialize the given vbox widget."""
    land_widget_vbox_interface_initialize()

    LandWidgetVBox *self = (LandWidgetVBox *)base
    land_widget_container_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_vbox_interface
    land_widget_layout_enable(base)
    self->columns = 1
   
    land_widget_theme_initialize(base)

# Create a new List widget. A list is simply a container with a layout in
# rows and columns. Each time you add a widget to it, it will be placed in the
# next column/row.
# 
LandWidget *def land_widget_vbox_new(LandWidget *parent, int x, int y, int w,
    int h):
    """Create a new vbox widget."""
    LandWidgetVBox *self
    land_alloc(self)
    LandWidget *widget = (LandWidget *)self
    land_widget_vbox_initialize(widget, parent, x, y, w, h)

    return widget

def land_widget_vbox_interface_initialize():
    if land_widget_vbox_interface: return
    land_widget_container_interface_initialize()

    land_widget_vbox_interface = land_widget_copy_interface(
        land_widget_container_interface, "vbox")
    land_widget_vbox_interface->id |= LAND_WIDGET_ID_VBOX
    land_widget_vbox_interface->add = land_widget_vbox_add
    land_widget_vbox_interface->remove = land_widget_vbox_remove
