import base, scrolling

class LandWidgetHBox:
    LandWidgetContainer super
    int rows
    int disable_updates : 1

macro LAND_WIDGET_HBOX(widget) ((LandWidgetHBox *) land_widget_check(widget, LAND_WIDGET_ID_HBOX, __FILE__, __LINE__))

static import land, widget/hbox

global LandWidgetInterface *land_widget_hbox_interface

# Call this before adding *many* items to the hbox, then call
# land_widget_hbox_update when done. This can speed things up, since there is
# no need to calculate intermediate layouts for each single added item.
# 

def land_widget_hbox_disable_updates(LandWidget *base):
    LAND_WIDGET_HBOX(base)->disable_updates = 1

def land_widget_hbox_update(LandWidget *base):
    LAND_WIDGET_HBOX(base)->disable_updates = 0
    land_widget_layout_adjust(base, 1, 1)

def land_widget_hbox_add(LandWidget *base, LandWidget *add):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    LandWidgetHBox *hbox = LAND_WIDGET_HBOX(base)

    land_widget_container_add(base, add)

    int n = container->children->count
    int columns = (n + hbox->rows - 1) / hbox->rows
    int column = columns - 1
    int row = n - column * hbox->rows - 1

    land_widget_layout_inhibit(base)

    land_widget_layout_set_grid_position(add, column, row)
    land_widget_layout_set_grid(base, columns, hbox->rows)

    land_widget_layout_set_shrinking(add, 1, 0)
    land_widget_layout_add(base, add)

    land_widget_layout_enable(base)

    if !hbox->disable_updates:
        land_widget_hbox_update(base)


def land_widget_hbox_set_rows(LandWidget *base, int n):
    LAND_WIDGET_HBOX(base)->rows = n

def land_widget_hbox_initialize(LandWidget *base, LandWidget *parent,
    int x, int y, int w, int h):
    land_widget_hbox_interface_initialize()

    LandWidgetHBox *self = (LandWidgetHBox *)base
    land_widget_container_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_hbox_interface
    self->rows = 1

    land_widget_theme_layout_border(base)

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
