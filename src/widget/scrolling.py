import container

class LandWidgetScrolling:
    """
    This has 4 fixed children:
    # The contents window, a container.
    # A vertical scrollbar to the right.
    # A horizontal scrollbar at the bottom.
    # The corner area between the scrollbars.
    """
    LandWidgetContainer super

    # 0 = never hide scrollbars [default]
    # 1 = auto hide vertical scrollbar
    # 2 = auto hide horizontal scrollbar
    # 3 = auto hide both scrollbars
    # ored together with:
    # 0 = never hide empty (TODO: not implemented)
    # 4 = hide empty only if both scrollbars are hidden
    # 8 = always hide empty except if both scrollbars are shown (TODO: not implemented)
    unsigned int autohide

    # 0 = no scrollwheel scrolling
    # 1 = scrolling [default]
    # 2 = unlimited
    unsigned int scrollwheel

macro LAND_WIDGET_SCROLLING(widget) ((LandWidgetScrolling *)
    land_widget_check(widget, LAND_WIDGET_ID_SCROLLING, __FILE__, __LINE__))

static import box, scrollbar

global LandWidgetInterface *land_widget_scrolling_interface
static LandWidgetInterface *land_widget_scrolling_contents_container_interface
static LandWidgetInterface *land_widget_scrolling_vertical_container_interface
static LandWidgetInterface *land_widget_scrolling_horizontal_container_interface

def land_widget_scrolling_get_container(LandWidget *base) -> LandWidget *:
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->data;
    return w

def land_widget_scrolling_get_vertical(LandWidget *base) -> LandWidget *:
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->next->data;
    return w

def land_widget_scrolling_get_horizontal(LandWidget *base) -> LandWidget *:
    LandList *children = LAND_WIDGET_CONTAINER(base)->children
    LandWidget *w = children->first->next->next->data;
    return w

def land_widget_scrolling_get_empty(LandWidget *base) -> LandWidget *:
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
    self.autohide = hori + 2 * vert + 4 * empty

    land_widget_scrolling_update(widget)

def land_widget_scrolling_need_vertical_bar(LandWidget *widget) -> bool:
    LandWidget *vbox = land_widget_scrolling_get_vertical(widget)
    return not vbox.hidden

def land_widget_scrolling_update(LandWidget *widget):
    _scrolling_layout(widget)

def land_widget_scrolling_size(LandWidget *widget, float dx, float dy):
    if not (dx or dy): return
    land_widget_scrolling_update(widget)

def land_widget_scrolling_get_scroll_position(LandWidget *base, float *x, *y):
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data
    LandWidget *child = land_widget_scrolling_get_child(base)
    if not child:
        *x = 0
        *y = 0
        return
    *x = child->box.x - contents->box.x - contents->element->il
    *y = child->box.y - contents->box.y - contents->element->it

def land_widget_scrolling_get_scrollable_area(LandWidget *base, float *x, *y):
    """
    Determines the size of the entire scrollable area.
    """
    auto child = land_widget_scrolling_get_child(base)
    if not child:
        *x = *y = 0
        return

    *x = child->box.w
    *y = child->box.h

def land_widget_scrolling_get_scroll_extents(LandWidget *base, float *x, *y):
    """
    Determines the amount, in pixels, the contents could be scrolled.
    """
    LandWidget *contents = land_widget_scrolling_get_container(base)
    auto child = land_widget_scrolling_get_child(base)
    if not child:
        *x = *y = 0
        return
    float cw, ch
    land_widget_get_inner_size(contents, &cw, &ch)

    *x = child->box.w - cw
    *y = child->box.h - ch
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
    if land_mouse_delta_z() and self.scrollwheel != 0:
        if self.scrollwheel == 1:
            float w, h
            land_widget_scrolling_get_scroll_extents(base, &w, &h)
            if h <= 0: return
        int dy = land_mouse_delta_z() * land_font_height(base->element->font)

        land_widget_scrolling_scroll(base, 0, dy)
        
        if self.scrollwheel == 1:
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

    # A freshly added widget starts always at the no-scroll position. 
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

def land_widget_scrolling_get_child(LandWidget *base) -> LandWidget *:
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

    # Add own widgets without special hook. 
    widget.vt = land_widget_container_interface

    LandWidgetScrolling *scrolling = (void *)widget
    scrolling->scrollwheel = 1

    # child 1: container 
    LandWidget *contents = land_widget_container_new(widget, 0, 0, 0, 0)
    contents->vt = land_widget_scrolling_contents_container_interface
    land_widget_theme_initialize(contents)
    land_widget_layout_disable(contents)
    contents.box.flags |= GUL_STEADFAST
    
    # child 2: vertical scrollbar 
    LandWidget *right = land_widget_container_new(widget, 0, 0, 0, 0)
    right->vt = land_widget_scrolling_vertical_container_interface
    land_widget_theme_initialize(right)
    land_widget_scrollbar_new(right, None,
        1, right->element->il, right->element->it, 0, 0)
    right.box.flags |= GUL_STEADFAST

    # child 3: horizontal scrollbar 
    LandWidget *bottom = land_widget_container_new(widget, 0, 0, 0, 0)
    bottom->vt = land_widget_scrolling_horizontal_container_interface
    land_widget_theme_initialize(bottom)
    land_widget_scrollbar_new(bottom, None,
        0, bottom->element->il, bottom->element->it, 0, 0)
    bottom.box.flags |= GUL_STEADFAST

    # child 4: Empty box. 
    land_widget_box_new(widget, 0, 0, 0, 0)

    # From now on, special vtable is used. 
    widget->vt = land_widget_scrolling_interface
    land_widget_theme_initialize(widget)

    _scrolling_layout(widget)

def _scrolling_layout(LandWidget *self):
    LandWidgetScrolling *scrolling = LAND_WIDGET_SCROLLING(self)
    
    auto container = land_widget_scrolling_get_container(self)
    auto horizontal = land_widget_scrolling_get_horizontal(self)
    auto vertical = land_widget_scrolling_get_vertical(self)
    auto empty = land_widget_scrolling_get_empty(self)
    LandWidget* hbar = land_widget_container_child(horizontal)
    LandWidget* vbar = land_widget_container_child(vertical)

    LandWidgetThemeElement *element = land_widget_theme_element(self)

    float l, t, r, b
    land_widget_inner_extents(self, &l, &t,&r, &b)

    int ver_w = vbar.box.w
    int hor_h = hbar.box.h
    int hgap = element.hgap
    int vgap = element.vgap

    land_widget_theme_set_minimum_size_for_contents(horizontal, 0, hor_h)
    land_widget_theme_set_minimum_size_for_contents(vertical, ver_w, 0)

    hor_h = horizontal.box.min_height
    ver_w = vertical.box.min_width

    land_widget_move_to(container, l, t)
    land_widget_move_to(horizontal, l, b - hor_h)
    land_widget_move_to(vertical, r - ver_w, t)
    land_widget_move_to(empty, r - ver_w, b - hor_h)

    land_widget_set_size(container, r - l, b - t)
    float vw, vh
    land_widget_get_inner_size(container, &vw, &vh)

    float sx, sy, sw, sh
    land_widget_scrolling_get_scroll_position(self, &sx, &sy)
    land_widget_scrolling_get_scrollable_area(self, &sw, &sh)

    float su = 0, sd = 0, sl = 0, sr = 0, sr2 = 0, sd2 = 0
    # sx     0          sx+sw
    # [      <___>      ]
    if sx < 0: sl = -sx
    if sy < 0: su = -sy
    if sx + sw > vw: sr = sx + sw - vw
    if sy + sh > vh: sd = sy + sh - vh
    # scroll variations in case bars are shown
    if sx + sw > vw - hgap - ver_w: sr2 = sx + sw - vw + hgap + ver_w
    if sy + sh > vh - vgap - hor_h: sd2 = sy + sh - vh + vgap + hor_h

    int w = r - l
    int h = b - t
    if sl + sr == 0 and su + sd == 0:
        # no scrollbars needed
        if scrolling.autohide & 2: hor_h = 0
        if scrolling.autohide & 1: ver_w = 0
    elif su + sd > 0 and sl + sr2 == 0:
        # only vertical bar needed
        if scrolling.autohide & 2: hor_h = 0
    elif sl + sr > 0 and su + sd2 == 0:
        # only horizontal bar needed
        if scrolling.autohide & 1: ver_w = 0
    else:
        # both bars needed
        pass

    if ver_w > 0: w -= hgap + ver_w
    if hor_h > 0: h -= vgap + hor_h

    land_widget_set_size(container, w, h)
    land_widget_set_size(horizontal, w, hor_h)
    land_widget_set_size(vertical, ver_w, h)
    land_widget_set_size(empty, ver_w, hor_h)

    land_widget_set_hidden(horizontal, hor_h == 0)
    land_widget_set_hidden(vertical, ver_w == 0)
    land_widget_set_hidden(empty, hor_h == 0 or ver_w == 0)
    
    land_widget_scrollbar_update(hbar, 0)
    land_widget_scrollbar_update(vbar, 0)
    
def land_widget_scrolling_wheel(LandWidget *widget, int wheel):
    """
    0: no wheel scrolling
    1: wheel scrolling [default]
    2: unlimited scrolling
    """
    LandWidgetScrolling *self = LAND_WIDGET_SCROLLING(widget)
    self.scrollwheel = wheel

def land_widget_scrolling_new(LandWidget *parent, int x, y, w, h) -> LandWidget *:
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
        _scrolling_layout(widget)

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
