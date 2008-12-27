import container

class LandWidgetScrolling:
    """
    This has 3 fixed children:
    # The contents window, a container.
    # A vertical scrollbar to the right.
    # A horizontal scrollbar at the bottom.
    """
    LandWidgetContainer super

    # 0 = never hide scrollbars [default]
    # 1 = auto hide vertical scrollbar
    # 2 = auto hide horizontal scrollbar
    # 3 = auto hide both scrollbars
    # ored together with:
    # 0 = never hide empty
    # 4 = hide empty only if both scrollbars are hidden
    # 8 = always hide empty except if both scrollbars are shown
    unsigned int autohide : 4

    # 0 = no scrollwheel scrolling
    # 1 = scrolling [default]
    # 2 = unlimited
    unsigned int scrollwheel : 2

macro LAND_WIDGET_SCROLLING(widget) ((LandWidgetScrolling *)
    land_widget_check(widget, LAND_WIDGET_ID_SCROLLING, __FILE__, __LINE__))

static import box, scrollbar

global LandWidgetInterface *land_widget_scrolling_interface
LandWidgetInterface *land_widget_scrolling_contents_container_interface
LandWidgetInterface *land_widget_scrolling_vertical_container_interface
LandWidgetInterface *land_widget_scrolling_horizontal_container_interface

LandWidget *def land_widget_scrolling_get_container(LandWidget *base):
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->data;
    return w

LandWidget *def land_widget_scrolling_get_vertical(LandWidget *base):
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->next->data;
    return w

LandWidget *def land_widget_scrolling_get_horizontal(LandWidget *base):
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->next->next->data;
    return w

LandWidget *def land_widget_scrolling_get_empty(LandWidget *base):
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->next->next->next->data;
    return w

def land_widget_scrolling_move(LandWidget *widget, float dx, float dy):
    land_widget_container_move(widget, dx, dy)

def land_widget_scrolling_autohide(LandWidget *widget, int hori, vert, empty):
    """
    Set hori/vert to 1 if the horizontal/vertical scrollbar should be auto
    hidden. Set empty to 1 if the empty should be auto hidden, and set empty to
    2 if the empty should be hidden as soon as one bar is hidden.
    """
    LandWidgetScrolling *self = LAND_WIDGET_SCROLLING(widget)
    self->autohide = hori + 2 * vert + 4 * empty

    land_widget_scrolling_update(widget)

int def land_widget_scrolling_autobars(LandWidget *widget):
    """
    Returns 0 if nothing changed or 1 if something changed.
    """
    LandWidgetScrolling *self = LAND_WIDGET_SCROLLING(widget)

    if (self->autohide & 3) == 0: return 0

    LandWidget *container = land_widget_scrolling_get_container(widget)
    LandWidget *empty = land_widget_scrolling_get_empty(widget)
    LandWidget *vbox = land_widget_scrolling_get_vertical(widget)
    LandWidget *hbox = land_widget_scrolling_get_horizontal(widget)

    # FIXME: should we already freeze the layout here? it means the contents
    # box doesn't have a chance to update, so of course need to fix that
    # somehow. But right now I'm worried about triggering an infinite
    # recursion if things go bad..

    int before = 0
    # Hide the bars and empty.
    if not vbox->hidden or not hbox->hidden or not empty->hidden:
        if not vbox->hidden:
            before += 1
            land_widget_hide(vbox)
        if not hbox->hidden:
            before += 2
            land_widget_hide(hbox)
        if not empty->hidden:
            before += 4
            land_widget_hide(empty)
        land_widget_layout_set_grid_extra(container, 1, 1)
        land_widget_layout_set_grid_extra(hbox, 0, 0)
        land_widget_layout_set_grid_extra(vbox, 0, 0)

    int f = land_widget_layout_freeze(widget)

    LandWidget *vslider = land_widget_container_child(vbox)
    LandWidget *hslider = land_widget_container_child(hbox)
    # Get scrolling parameters
    #      r
    # a   ___    b   
    # |..|___|...|
    #    p
    int xa, xb, xr, xp
    int ya, yb, yr, yp
    LAND_WIDGET_SCROLLBAR(hslider)->callback(hslider, 0, &xa, &xb, &xr, &xp)
    LAND_WIDGET_SCROLLBAR(vslider)->callback(vslider, 0, &ya, &yb, &yr, &yp)

    # Determine which bars are needed.
    int needh = self->autohide & 1 ? 0 : 1, needv = self->autohide & 2 ? 0 : 1
    if xp > xa or 1 + xb - xa > xr: needh = 1
    if yp > ya or 1 + yb - ya > yr: needv = 1
    int neede = 1
    if self->autohide & 4:
        if not needh and not needv: neede = 0
    if self->autohide & 8:
        if not needh or not needv: neede = 0

    if not needh and not needv and not neede:
        # Keep them all hidden.
        goto done

    if not needh and not needv:
        # Show empty only.
        land_widget_unhide(empty)
        land_widget_layout_set_grid_extra(container, 0, 0)
        goto done

    if needh and needv:
        # Show both bars and empty.
        land_widget_unhide(hbox)
        land_widget_unhide(vbox)
        land_widget_unhide(empty)
        land_widget_layout_set_grid_extra(container, 0, 0)
        goto done

    if needh:
        land_widget_unhide(hbox)
        if neede: land_widget_unhide(empty)
        else: land_widget_layout_set_grid_extra(hbox, 1, 0)
        land_widget_layout_set_grid_extra(container, 1, 0)

        # This has reduced the vertical space, so check again.
        LAND_WIDGET_SCROLLBAR(vslider)->callback(vslider, 0, &ya, &yb, &yr, &yp)
        if yp > ya or 1 + yb - ya > yr:
            f = land_widget_layout_freeze(widget)
            land_widget_unhide(vbox)
            land_widget_layout_set_grid_extra(container, 0, 0)
        else:
            goto done
    else:
        land_widget_unhide(vbox)
        if neede: land_widget_unhide(empty)
        else: land_widget_layout_set_grid_extra(vbox, 0, 1)
        land_widget_layout_set_grid_extra(container, 0, 1)

        LAND_WIDGET_SCROLLBAR(hslider)->callback(hslider, 0, &xa, &xb, &xr, &xp)
        if xp > xa or 1 + xb - xa > xr:
            f = land_widget_layout_freeze(widget)
            land_widget_unhide(hbox)
            land_widget_layout_set_grid_extra(container, 0, 0)
        else:
            goto done

    label done
    if f: land_widget_layout_unfreeze(widget)
    land_widget_layout(widget)

    int after = 0
    if not vbox->hidden: after += 1
    if not hbox->hidden: after += 2
    if not empty->hidden: after += 4
    if after == before: return 0
    return 1

static int def scrolling_update_layout(LandWidget *widget):
    """
    Update the scrolling window after it was resized or scrolled. Returns 1
    if any bars were hidden or unhidden.
    """

    int r = land_widget_scrolling_autobars(widget)

    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandListItem *item = container->children->first

    item = item->next
    LandWidget *right = LAND_WIDGET(item->data)

    LandListItem *item2 = LAND_WIDGET_CONTAINER(right)->children->first
    LandWidgetScrollbar *rightbar = LAND_WIDGET_SCROLLBAR(item2->data)
    land_widget_scrollbar_update(LAND_WIDGET(rightbar), 0)

    item = item->next
    LandWidget *bottom = LAND_WIDGET(item->data)
    LandListItem *item3 = LAND_WIDGET_CONTAINER(bottom)->children->first
    LandWidgetScrollbar *bottombar = LAND_WIDGET_SCROLLBAR(item3->data)
    land_widget_scrollbar_update(LAND_WIDGET(bottombar), 0)

    return r

def land_widget_scrolling_update(LandWidget *widget):
    scrolling_update_layout(widget)

def land_widget_scrolling_size(LandWidget *widget, float dx, float dy):
    if not (dx or dy): return
    land_widget_scrolling_update(widget)

def land_widget_scrolling_get_scroll_position(LandWidget *base, float *x, *y):
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    if not children:
        *x = 0
        *y = 0
        return
    LandWidget *child =  children->first->data
    *x = child->box.x - contents->box.x - contents->element->il
    *y = child->box.y - contents->box.y - contents->element->it

def land_widget_scrolling_get_scroll_extents(LandWidget *base, float *x, *y):
    """
    Determines the "scrollable area", that is how much overlap there is in
    horizontal and vertical direction.
    """
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    if not children:
        *x = 0
        *y = 0
        return
    LandWidget *child =  children->first->data
    *x = child->box.w - contents->box.w + contents->element->il + contents->element->ir
    *y = child->box.h - contents->box.h + contents->element->it + contents->element->ib
    if *x < 0: *x = 0
    if *y < 0: *y = 0

def land_widget_scrolling_get_view(LandWidget *base, float *l, *t, *r, *b):
    """
    Determine pixel coordinates of the viewable area.
    """
    LandWidget *contents = land_widget_scrolling_get_container(base)
    land_widget_inner_extents(contents, l, t, r, b)

def land_widget_scrolling_scrollto(LandWidget *base, float x, y):
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    if not children: return
    LandWidget *child =  children->first->data

    land_widget_move(child,
        contents->box.x + contents->element->il + x - child->box.x,
        contents->box.y + contents->element->it + y - child->box.y)

    land_widget_scrolling_update(base)

def land_widget_scrolling_scroll(LandWidget *base, float dx, dy):
    float x, y
    land_widget_scrolling_get_scroll_position(base, &x, &y)
    land_widget_scrolling_scrollto(base, x + dx, y + dy)

def land_widget_scrolling_limit(LandWidget *base):
    float x, y, w, h
    land_widget_scrolling_get_scroll_position(base, &x, &y)
    land_widget_scrolling_get_scroll_extents(base, &w, &h)
    if y < -h: land_widget_scrolling_scrollto(base, x, -h)
    if y > 0: land_widget_scrolling_scrollto(base, x, 0)

def land_widget_scrolling_mouse_tick(LandWidget *base):
    LandWidgetScrolling *self = LAND_WIDGET_SCROLLING(base)
    if land_mouse_delta_z() and self->scrollwheel:
        if not (self->scrollwheel & 2):
            float w, h
            land_widget_scrolling_get_scroll_extents(base, &w, &h)
            if h <= 0: return
        int dy = land_mouse_delta_z() * land_font_height(base->element->font)
        land_widget_scrolling_scroll(base, 0, dy)
        if not (self->scrollwheel & 2):
            land_widget_scrolling_limit(base)

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

    # There is no point in updating here, as the widget to be added likely is
    # not fully created yet.

LandWidget *def land_widget_scrolling_get_child(LandWidget *base):
    """
    Return the child window of the scrolling window. Usually, a scrolling
    window has exactly one child window, which is controlled by the scrollbars.
    That window is returned.
    """
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children
    return children ? children->first->data : None

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

def land_widget_scrolling_initialize(LandWidget *widget,
    LandWidget *parent, int x, y, w, h):

    land_widget_scrolling_interface_initialize()

    land_widget_container_initialize(widget, parent, x, y, w, h)
    land_widget_layout_enable(widget)

    # Add own widgets without special hook. 
    widget->vt = land_widget_container_interface

    LandWidgetScrolling *scrolling = (void *)widget
    scrolling->scrollwheel = 1

    # child 1: container 
    LandWidget *contents = land_widget_container_new(widget, 0, 0, 0, 0)
    # FIXME: shouldn't the theme handle this?
    # contents->only_border = 1
    contents->vt = land_widget_scrolling_contents_container_interface
    land_widget_theme_initialize(contents)

    # child 2: vertical scrollbar 
    LandWidget *right = land_widget_container_new(widget, 0, 0, 0, 0)
    right->vt = land_widget_scrolling_vertical_container_interface
    land_widget_theme_initialize(right)
    land_widget_scrollbar_new(right, NULL,
        1, right->element->il, right->element->it, 0, 0)

    # child 3: horizontal scrollbar 
    LandWidget *bottom = land_widget_container_new(widget, 0, 0, 0, 0)
    bottom->vt = land_widget_scrolling_horizontal_container_interface
    land_widget_theme_initialize(bottom)
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

def land_widget_scrolling_wheel(LandWidget *widget, int wheel):
    """
    0: no wheel scrolling
    1: wheel scrolling [default]
    2: unlimited scrolling
    """
    LandWidgetScrolling *self = LAND_WIDGET_SCROLLING(widget)
    self->scrollwheel = wheel

LandWidget *def land_widget_scrolling_new(LandWidget *parent, int x, y, w, h):
    """
    Creates a new Scrolling widget. You can add a child widget to it, and it
    will automatically display scrollbars and translate mouse coordinates.
    
    By default, the widget will expand in all directions.
    """
    LandWidgetScrolling *self
    land_alloc(self)
    LandWidget *widget = (LandWidget *)self
    land_widget_scrolling_initialize(widget, parent, x, y, w, h)

    return widget

def land_widget_scrolling_layout_changed(LandWidget *widget):
    if widget->box.w != widget->box.ow or widget->box.h != widget->box.oh:
        int f = land_widget_layout_freeze(widget)
        int r = scrolling_update_layout(widget)
        if f: land_widget_layout_unfreeze(widget)
        gul_layout_updated_during_layout(widget)
        if r: widget->layout_hack = 1

def land_widget_scrolling_layout_changing(LandWidget *widget):
    pass

def land_widget_scrolling_interface_initialize():
    if land_widget_scrolling_interface: return

    land_widget_container_interface_initialize()

    land_widget_scrolling_interface = land_widget_copy_interface(
        land_widget_container_interface, "scrolling")
    land_widget_scrolling_interface->id |= LAND_WIDGET_ID_SCROLLING
    land_widget_scrolling_interface->tick = land_widget_scrolling_tick
    land_widget_scrolling_interface->add = land_widget_scrolling_add
    land_widget_scrolling_interface->update = land_widget_scrolling_update
    land_widget_scrolling_interface->move = land_widget_scrolling_move
    land_widget_scrolling_interface->size = land_widget_scrolling_size
    land_widget_scrolling_interface->layout_changed =\
        land_widget_scrolling_layout_changed
    land_widget_scrolling_interface->layout_changing =\
        land_widget_scrolling_layout_changing
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
