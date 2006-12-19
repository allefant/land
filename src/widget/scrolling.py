import container

class LandWidgetScrolling:
    """
    This has 3 fixed children:
    # The contents window, a container.
    # A vertical scrollbar to the right.
    # A horizontal scrollbar at the bottom.
    """
    LandWidgetContainer super

macro LAND_WIDGET_SCROLLING(widget) ((LandWidgetScrolling *) \
    land_widget_check(widget, LAND_WIDGET_ID_SCROLLING, __FILE__, __LINE__))

static import widget/box, widget/scrollbar

LandWidgetInterface *land_widget_scrolling_interface
LandWidgetInterface *land_widget_scrolling_contents_container_interface
LandWidgetInterface *land_widget_scrolling_vertical_container_interface
LandWidgetInterface *land_widget_scrolling_horizontal_container_interface

def land_widget_scrolling_move(LandWidget *widget, float dx, float dy):
    land_widget_container_move(widget, dx, dy)

def land_widget_scrolling_size(LandWidget *widget, float dx, float dy):
    if not (dx or dy): return
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandListItem *item = container->children->first

    item = item->next
    LandWidgetContainer *right = LAND_WIDGET_CONTAINER(item->data)
    LandListItem *item2 = right->children->first
    LandWidgetScrollbar *rightbar = LAND_WIDGET_SCROLLBAR(item2->data)
    land_widget_scrollbar_update(LAND_WIDGET(rightbar), 0)

    item = item->next
    LandWidgetContainer *bottom = LAND_WIDGET_CONTAINER(item->data)
    item2 = bottom->children->first
    LandWidgetScrollbar *bottombar = LAND_WIDGET_SCROLLBAR(item2->data)
    land_widget_scrollbar_update(LAND_WIDGET(bottombar), 0)

def land_widget_scrolling_scrollto(LandWidget *base, float x, float y):
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    if not children: return
    LandWidget *child =  children->first->data

    child->box.x = contents->box.x + contents->element->il + x
    child->box.y = contents->box.y + contents->element->it + y

    land_widget_scrolling_size(base, 0, 0)

def land_widget_scrolling_mouse_tick(LandWidget *base):
    if land_mouse_delta_z():
        LandWidget *contents =\
            LAND_WIDGET_CONTAINER(base)->children->first->data
        LandList *children = LAND_WIDGET_CONTAINER(contents)->children
        if not children: return
        LandWidget *child = children->first->data
        int maxy = contents->box.y + contents->element->it
        int miny = contents->box.y + contents->box.h -\
            contents->element->ib - child->box.h
        int dy = land_mouse_delta_z() * 64
        int y = child->box.y
        int target_y = y + dy
        if dy < 0 and target_y < miny: target_y = miny
        if dy > 0 and target_y > maxy: target_y = maxy
        if (dy < 0 and target_y < y) or (dy > 0 and target_y > y):
            land_widget_move(child, 0, target_y - child->box.y)

    land_widget_container_mouse_tick(base)

def land_widget_scrolling_tick(LandWidget *super):
    pass

def land_widget_scrolling_add(LandWidget *widget, LandWidget *add):
    """
    Add a widget to the scrolling widget. The child widget can be bigger than
    the parent, and scrollbars will appear to allow scrolling around.
    """
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandListItem *item = container->children->first
    LandWidget *contents = LAND_WIDGET(item->data)
    land_widget_container_add(contents, add)

    # A freshly added widget start always at the no-scroll position. 
    add->box.x = contents->box.x + contents->element->il
    add->box.y = contents->box.y + contents->element->it

    # There is no need to add extra references to the added widget from the
    # scrollbars. They live and die with the whole scrolling widget anyway,
    # so if the added widget is to be destroyed, then it has to be detached
    # first from contents, which can *only* happen over
    # land_widget_scrolling_destroy_child.

    item = item->next
    LandWidgetContainer *right = LAND_WIDGET_CONTAINER(item->data)
    LandListItem *item2 = right->children->first
    LandWidgetScrollbar *rightbar = LAND_WIDGET_SCROLLBAR(item2->data)
    rightbar->target = add

    item = item->next
    LandWidgetContainer *bottom = LAND_WIDGET_CONTAINER(item->data)
    item2 = bottom->children->first
    LandWidgetScrollbar *bottombar = LAND_WIDGET_SCROLLBAR(item2->data)
    bottombar->target = add

LandWidget *def land_widget_scrolling_get_child(LandWidget *base):
    """
    Return the child window of the scrolling window. Usually, a scrolling
    window has exactly one child window, which is controlled by the scrollbars.
    That window is returned.
    """
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    return children ? children->first->data : NULL

def land_widget_scrolling_remove_child(LandWidget *base):
    """
    Detach the window managed inside the scrolled window. If there are no
    other references to it, it will be destroyed.
    """
    LandList *list = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *contents = list->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    LandWidget *child = children ? children->first->data : NULL
    if child:
        land_widget_container_remove(contents, child)

    # Detach scrollbars. 
    LandWidgetContainer * c
    c = LAND_WIDGET_CONTAINER(list->first->next->data)
    LAND_WIDGET_SCROLLBAR(c->children->first->data)->target = NULL
    c = LAND_WIDGET_CONTAINER(list->first->next->next->data)
    LAND_WIDGET_SCROLLBAR(c->children->first->data)->target = NULL

LandWidget *def land_widget_scrolling_new(LandWidget *parent, int x, y, w, h):
    """
    Creates a new Scrolling widget. You can add a child widget to it, and it
    will automatically display scrollbars and translate mouse coordinates.
    
    By default, the widget will expand in all directions.
    """
    LandWidgetScrolling *self
    
    land_widget_scrolling_interface_initialize()

    land_alloc(self)
    LandWidgetContainer *super = &self->super
    LandWidget *widget = &super->super
    land_widget_container_initialize(widget, parent, x, y, w, h)
    land_widget_layout_enable(widget)

    # Add own widgets without special hook. 
    widget->vt = land_widget_container_interface

    # child 1: container 
    LandWidget *contents = land_widget_container_new(widget, 0, 0, 0, 0)
    contents->only_border = 1
    contents->vt = land_widget_scrolling_contents_container_interface
    land_widget_theme_initialize(contents)

    # child 2: vertical scrollbar 
    LandWidget *right = land_widget_container_new(widget, 0, 0, 0, 0)
    right->vt = land_widget_scrolling_vertical_container_interface
    land_widget_theme_initialize(right)
    land_widget_theme_set_minimum_size(right)
    land_widget_scrollbar_new(right, NULL,
        1, right->element->il, right->element->it, 0, 0)

    # child 3: horizontal scrollbar 
    LandWidget *bottom = land_widget_container_new(widget, 0, 0, 0, 0)
    bottom->vt = land_widget_scrolling_horizontal_container_interface
    land_widget_theme_initialize(bottom)
    land_widget_theme_set_minimum_size(bottom)
    land_widget_scrollbar_new(bottom, NULL,
        0, bottom->element->il, bottom->element->it, 0, 0)

    # overall layout 
    land_widget_layout_set_grid(widget, 2, 2)
    land_widget_layout_set_grid_position(contents, 0, 0)

    # Vertical scrollbar layout. 
    land_widget_layout_set_grid_position(right, 1, 0)
    land_widget_layout_set_shrinking(right, 1, 0)

    # Horizontal scrollbar layout. 
    land_widget_layout_set_grid_position(bottom, 0, 1)
    land_widget_layout_set_shrinking(bottom, 0, 1)

    # Child 4: Empty box. 
    LandWidget *empty = land_widget_panel_new(widget, 0, 0, 0, 0)
    land_widget_layout_set_grid_position(empty, 1, 1)
    land_widget_layout_set_shrinking(empty, 1, 1)

    # From now on, special vtable is used. 
    widget->vt = land_widget_scrolling_interface
    land_widget_theme_initialize(widget)

    land_widget_layout(widget)

    return widget

LandWidget *def land_widget_scrolling_get_empty(LandWidget *base):
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *empty = children->first->next->next->next->data;
    return empty

def land_widget_scrolling_interface_initialize():
    if land_widget_scrolling_interface: return

    land_widget_container_interface_initialize()

    land_widget_scrolling_interface = land_widget_copy_interface(
        land_widget_container_interface, "scrolling")
    land_widget_scrolling_interface->id |= LAND_WIDGET_ID_SCROLLING
    land_widget_scrolling_interface->tick = land_widget_scrolling_tick
    land_widget_scrolling_interface->add = land_widget_scrolling_add
    land_widget_scrolling_interface->move = land_widget_scrolling_move
    land_widget_scrolling_interface->size = land_widget_scrolling_size
    land_widget_scrolling_interface->mouse_tick =\
        land_widget_scrolling_mouse_tick

    land_widget_scrolling_contents_container_interface =\
        land_widget_copy_interface(
        land_widget_container_interface, "scrolling.contents.container")
    land_widget_scrolling_vertical_container_interface =\
        land_widget_copy_interface(
        land_widget_container_interface, "scrolling.vertical.container")
    land_widget_scrolling_horizontal_container_interface =\
        land_widget_copy_interface(
        land_widget_container_interface, "scrolling.horizontal.container")
