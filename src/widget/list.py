import base, scrolling, vbox

class LandWidgetList:
    LandWidgetVBox super
    # If set, multiple items can get selected. 
    bool multi_select

macro LAND_WIDGET_LIST(widget) ((LandWidgetList *) land_widget_check(widget,
    LAND_WIDGET_ID_LIST, __FILE__, __LINE__))

static import land/land, button

static LandWidgetInterface *land_widget_list_interface
static LandWidgetInterface *land_widget_listitem_interface

# Call this before adding *many* items to the list, then call
# land_widget_list_update when done. This can speed things up, since there is
# no need to calculate intermediate layouts for each single added item.
# 

def land_widget_list_disable_updates(LandWidget *base):
    land_widget_vbox_disable_updates(base)

def land_widget_list_update(LandWidget *base):
    land_widget_vbox_update(base)

def land_widget_list_set_columns(LandWidget *base, int n):
    land_widget_vbox_set_columns(base, n)

def land_widget_list_initialize(LandWidget *base, LandWidget *parent,
    int x, int y, int w, int h):
    land_widget_list_interface_initialize()

    land_widget_vbox_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_list_interface

    land_widget_theme_initialize(base)

    land_call_method(parent, update, (parent))

# Create a new List widget. A list is simply a container with a layout in
# rows and columns. Each time you add a widget to it, it will be placed in the
# next column/row.
# 
LandWidget *def land_widget_list_new(LandWidget *parent, int x, y, w, h):
    LandWidgetList *self
    land_alloc(self)
    LandWidget *widget = (LandWidget *)self
    land_widget_list_initialize(widget, parent, x, y, w, h)

    return widget

LandWidget *def land_widget_listitem_new(LandWidget *parent,
    char const *text, void (*clicked)(LandWidget *self),
    int x, int y, int w, int h):
    LandWidget *self = land_widget_button_new(parent, text, clicked,
        x, y, w, h)
    land_widget_listitem_interface_initialize()
    self.vt = land_widget_listitem_interface
    land_widget_theme_initialize(self)
    land_widget_layout(parent)
    return self

def land_widget_list_interface_initialize():
    if land_widget_list_interface: return

    land_widget_vbox_interface_initialize()
    land_widget_list_interface = land_widget_copy_interface(
        land_widget_vbox_interface, "list")
    land_widget_list_interface->id |= LAND_WIDGET_ID_LIST

def land_widget_listitem_interface_initialize():
    # FIXME: What is the difference to a button?
    if land_widget_listitem_interface: return
    land_widget_button_interface_initialize()

    land_widget_listitem_interface = land_widget_copy_interface(
        land_widget_button_interface, "listitem")
    land_widget_listitem_interface->id |= LAND_WIDGET_ID_LISTITEM

# Given a list, this returns an array of all the selected children. The caller
# takes ownership of the array and is responsible for destroying it with
# land_array_destroy after use.
# 
LandArray *def land_widget_list_get_selected_items(LandWidget *self):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)
    LandArray *array = land_array_new()
    LandListItem *item
    for item = container->children->first while item with item = item->next:
        LandWidget *child = item->data
        if child->selected:
            land_array_add_data(&array, child)

    return array

def land_widget_list_clear_selection(LandWidget *self):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)
    LandListItem *item
    for item = container->children->first while item with item = item->next:
        LandWidget *child = item->data
        if child->selected:
            child->selected = 0
