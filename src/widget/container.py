import base, land/list
static import land/land

class LandWidgetContainer:
    """
    A container is a widget with children. It is not useful all by itself, but
    is the base class of some useful widgets, or can be used to derive your own
    special containers.
    """
    LandWidget super
    LandList *children # we keep a reference to each child.
    LandWidget *mouse # we keep a reference to the focus object.
    LandWidget *keyboard

# Mouse focus works hierarchical. That is, we do not have a single widget having
# mouse focus. Instead, the desktop always has focus if a mouse is inside it.
# Then, one if its windows which has the mouse cursor also might have focus. As
# well as one of its subwindows. And so on.

macro LAND_WIDGET_CONTAINER(widget) ((LandWidgetContainer *)
    land_widget_check(widget, LAND_WIDGET_ID_CONTAINER, __FILE__, __LINE__))

global LandWidgetInterface *land_widget_container_interface

def land_widget_container_destroy(LandWidget *base):
    """Destroy the container and all its children."""
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base)
    if self.mouse:
        land_widget_unreference(self.mouse)

    if self.children:
        LandListItem *item = self.children->first
        while item:
            LandListItem *next = item->next
            LandWidget *child = item->data
            # Detach it. It won't get destroyed if there are still outside
            # references to it.
            child->parent = NULL
            land_widget_unreference(child)
            item = next

        land_list_destroy(self.children)

    land_widget_base_destroy(base)

def land_widget_container_mouse_enter(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    # Get the child under the mouse
    LandWidget *child = land_widget_container_get_child_at_pos(super,
        land_mouse_x(), land_mouse_y())
    if child:
        land_widget_reference(child)
        child->got_mouse = 1
        land_call_method(child, mouse_enter, (child))
        self.mouse = child

def land_widget_container_mouse_leave(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if self.mouse:
        self.mouse->got_mouse = 0
        land_call_method(self.mouse, mouse_leave, (self->mouse))
        if self.mouse->got_mouse:
            super->got_mouse = 1
        else:
            land_widget_unreference(self.mouse)
            self.mouse = None

def land_widget_container_keyboard_enter(LandWidget *super):
    """ Give keyboard focus to the container, and to children who requested
        focus."""
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if self.children:
        LandListItem *item, *next
        item = self.children->first
        for  while item with item = next:
            next = item->next
            LandWidget *child = item->data

            if child->want_focus:
                child->want_focus = 0
                child->got_keyboard = 1
                land_call_method(child, keyboard_enter, (child))
                self.keyboard = child
                land_widget_reference(self.keyboard)
                break

def land_widget_container_get_keyboard_focus(LandWidget *super) -> LandWidget*:
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    return self.keyboard

# Remove keyboard focus from the container and its children.
def land_widget_container_keyboard_leave(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    if self.keyboard:
        LandWidget* keyboard = self.keyboard
        self.keyboard = NULL
        
        keyboard.got_keyboard = 0
        land_call_method(keyboard, keyboard_leave, (keyboard))

        if keyboard.got_keyboard: # if keyboard_leave set it again
            super.got_keyboard = 1
            self.keyboard = keyboard
            # we still have the reference
            return

        super.got_keyboard = 0
        land_widget_unreference(keyboard)

        if super.parent:
            land_widget_keyboard_leave(super.parent)

# Returns the item/iterator for the given child of the container.
def land_widget_container_child_item(LandWidget *super, *child) -> LandListItem *:
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if not self.children:
        return NULL
    LandListItem *item = self.children->first
    while item:
        if item->data == child:
            return item
        item = item->next

    return NULL

def land_widget_container_to_top(LandWidget *super, LandWidget *child):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    LandListItem *item = land_widget_container_child_item(super, child)
    land_list_remove_item(self.children, item)
    land_list_insert_item(self.children, item)

def land_widget_container_draw(LandWidget *base):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base)
    # The base container theme is completely invisible, but derived classes
    # like panel or board will draw themselves here.
    land_widget_theme_draw(base)

    if not self.children:
        return

    if not base->dont_clip:
        float l, t, r, b
        land_widget_inner_extents(base, &l, &t, &r, &b)
        land_clip_push()
        land_clip_intersect(l, t, r, b)

    float cl, ct, cr, cb
    land_get_clip(&cl, &ct, &cr, &cb)

    LandListItem *item = self.children->first
    for  while item with item = item->next:
        LandWidget *child = item->data
        if child->hidden: continue
        if not base->dont_clip and not child->no_clip_check:
            if (child->box.x <= cr and child->box.x + child->box.w >= cl and
                    child->box.y <= cb and child->box.y + child->box.h >= ct):
                #printf("land_widget_draw %s\n", land_widget_info_string(child))
                land_widget_draw(child)

        else:
            land_widget_draw(child)

    if not base->dont_clip:
        land_clip_pop()

def land_widget_container_move(LandWidget *super, float dx, float dy):
    """
    Move all children of the container when the container itself is moved.
    """
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if not self.children: return
    LandListItem *item = self.children->first
    while item:
        LandWidget *child = item->data
        land_widget_move(child, dx, dy)
        item = item->next

def land_widget_container_size(LandWidget *super, float dx, dy):
    if dx or dy: land_widget_layout(super)

def land_widget_container_get_descendant_at_pos(LandWidget *super,
    int x, y) -> LandWidget *:
    """
    Returns a descendant under a specific (absolute) position, or else the
    widget itself.
    """
    LandWidget *child = land_widget_container_get_child_at_pos(super, x, y)
    if child:
        if land_widget_is(child, LAND_WIDGET_ID_CONTAINER):
            return land_widget_container_get_descendant_at_pos(child, x, y)
        return child

    return super

def land_widget_container_get_child_at_pos(LandWidget *super,
    int x, y) -> LandWidget *:
    """
    Returns the direct child under a specific (absolute) position.
    """
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if not self.children:
        return None
    LandListItem *item = self.children->last
    for  while item with item = item->prev:
        LandWidget *child = item->data
        if child->hidden: continue
        if (x >= child->box.x
        and y >= child->box.y
        and x < child->box.x + child->box.w
        and y < child->box.y + child->box.h):
            return child

    return None

# Transfer the mouse focus inside base to child. If child is NULL, remove any
# mouse focus.
static def transfer_mouse_focus(LandWidget *base, LandWidget *child):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base)

    # We can't have this deleted inside any method call or we get a
    # dangling pointer. In case it receives the focus, the reference will
    # be hold until the focus is lost again.
    if child: land_widget_reference(child)

    # Take focus away? If the currently focused widget does not want to give up
    # focus, then so be it.
    if self.mouse:
        self.mouse->got_mouse = 0
        land_call_method(self.mouse, mouse_leave, (self->mouse))
        # Retain focus?
        if self.mouse->got_mouse:
            if child: land_widget_unreference(child)
            return

        # Ok, we do take away focus.
        land_widget_unreference(self.mouse)
        self.mouse = None

    # Give focus to the new widget. There is no way to refuse focus. If there
    # will arise any use case where it might make sense, can add it here.
    if child:
        self.mouse = child
        land_call_method(self.mouse, mouse_enter, (self->mouse))

static def transfer_keyboard_focus(LandWidget *base):
    # Need to take focus away first?

    base->got_keyboard = 0
    land_widget_container_keyboard_leave(base)
    # Retain focus?
    if base->got_keyboard:
        return

    # At this point, no children have focus anymore. Next we give focus to
    # those who want it.
    base->want_focus = 0
    base->got_keyboard = 1
    land_widget_container_keyboard_enter(base)

# Focus handling works like this:
# The mouse focus is the widget the mouse is over. The widget with mouse
# focus can set the want_focus flag to additionally receive keyboard focus.
# In this case, the flag will be propagated up to the parents by the mouse
# handler. The keyboard handler then will react to the flags and shift focus,
# starting with the parent and going down.
#
# 1. C, B and A currently have focus. E requests focus.
#  _________
# |A        |
# |________f|
#  _|_   _|_
# |B  | |D  |
# |__f| |___|
#  _|_   _|_
# |C  | |E  |
# |__f| |_*_|
#
# 2. Request propagated up to D and A.
#  _________
# |A        |
# |____*___f|
#  _|_   _|_
# |B  | |D  |
# |__f| |_*_|
#  _|_   _|_
# |C  | |E  |
# |__f| |_*_|
#
# 3. Focus is taken from A. This recurses down to children who also lose focus.
#    If any child refuses, focus is kept at A.
#  _________
# |A        |
# |____*____|
#  _|_   _|_
# |B  | |D  |
# |___| |_*_|
#  _|_   _|_
# |C  | |E  |
# |___| |_*_|
#
# 4. Focus is transferred to A.
#  _________
# |A        |
# |________f|
#  _|_   _|_
# |B  | |D  |
# |___| |_*_|
#  _|_   _|_
# |C  | |E  |
# |___| |_*_|
#
# 5. Focus is transferred recusivley to D and E.
#  _________
# |A        |
# |________f|
#  _|_   _|_
# |B  | |D  |
# |___| |__f|
#  _|_   _|_
# |C  | |E  |
# |___| |__f|
def land_widget_container_mouse_tick(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    if self.mouse:
        land_call_method(self.mouse, mouse_tick, (self->mouse))

    LandWidget *mouse = land_widget_container_get_child_at_pos(super,
        land_mouse_x(), land_mouse_y())

    # Transfer mouse focus?

    if mouse != self.mouse and not (land_mouse_b() & 1):
        transfer_mouse_focus(super, mouse)

    # Transfer keyboard focus?

    # If any direct child wants keyboard focus, so do we.
    if self.children:
        LandListItem *item, *next, *last
        item = self.children->first
        last = self.children->last
        for  while item with item = next:
            next = item->next
            LandWidget *child = item->data

            # Propagate up focus request.
            if child->want_focus:
                super->want_focus = 1

            if child->send_to_top:
                land_widget_container_to_top(super, child)
                child->send_to_top = 0

            if item == last:
                break

def land_widget_container_set_mouse_focus(LandWidget *super, LandWidget *mouse):
    """
    Only suceeds if the currently focused window agrees.
    """
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if mouse != self.mouse:
        transfer_mouse_focus(super, mouse)

def land_widget_container_keyboard_tick(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    if super->want_focus:
        transfer_keyboard_focus(super)

    if self.keyboard:
        land_call_method(self.keyboard, keyboard_tick, (self->keyboard))

def land_widget_container_tick(LandWidget *super):
    # Don't allow anyone pulling the carpet below our feet.
    land_widget_reference(super)
    
    land_call_method(super, mouse_tick, (super))
    land_call_method(super, keyboard_tick, (super))

    # See above.
    land_widget_unreference(super)

def land_widget_container_add(LandWidget *super, LandWidget *add):

    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    # We increase the reference count of the child only. Increasing the
    # parent's reference (even though there is the ->parent pointer), would
    # cause a cyclic dependancy! We still never get a dangling pointer, since
    # the parent cannot be destroyed without first detaching its children.

    land_add_list_data(&self.children, add)
    land_widget_reference(add)

    add->parent = super

# Containers do not know about layout - the derived class like VBox must make
# sure to also fix up the layout structure when a widget is removed, and should
# then call this method.
def land_widget_container_remove(LandWidget *base, LandWidget *rem):
    assert(rem->parent == base)

    rem->parent = NULL
    land_remove_list_data(&LAND_WIDGET_CONTAINER(base)->children, rem)

    # Whenever the item was added to our container, the container acquired a
    # reference to it, which it has to give up now.
    land_widget_unreference(rem)

def land_widget_container_remove_all(LandWidget *base):
    while True:
        LandWidget *child = land_widget_container_child(base)
        if not child: break
        land_widget_container_remove(base, child)

def land_widget_container_update(LandWidget *widget):
    """
    The update method is called after the add method. We simply defer it to
    our children.
    """
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    if not container->children: return
    LandListItem *item = container->children->first
    while item:
        LandWidget *child = item->data
        land_call_method(child, update, (child))
        item = item->next

def land_widget_container_child(LandWidget *super) -> LandWidget *:
    """
    Return the first child of the container or None.
    """
    LandWidgetContainer *self = (LandWidgetContainer *)super
    LandList *l = self.children
    if l:
        LandListItem *first = l->first
        if first:
            return first->data
    return None

def land_widget_container_child_i(LandWidget *super, int i) -> LandWidget *:
    """
    Return the child i or else None.
    """
    LandWidgetContainer *self = (LandWidgetContainer *)super
    int j = 0
    if not self.children:
        return None
    for LandWidget *w in LandList *self.children:
        if i == j: return w
        j++
    return None

def land_widget_get_sibling(LandWidget *widget, int d) -> LandWidget *:
    """
    Return the previous (d=-1) or next (d=1) sibling. Returns None as
    previous/next sibling for the first/last widget.

    Crashes if you pass a widget not in a container.
    """
    LandWidgetContainer *self = (LandWidgetContainer *)widget.parent
    LandWidget* prev = None
    if not self.children:
        return None
    for LandWidget *w in LandList *self.children:
        if w == widget and d == -1: return prev
        if prev == widget and d == 1: return w
        prev = w
    return None


def land_widget_container_is_empty(LandWidget *super) -> int:
    LandWidgetContainer *self = (LandWidgetContainer *)super
    return not self.children or self->children->count == 0

def land_widget_container_initialize(LandWidget *super, *parent,
    int x, y, w, h):
    land_widget_container_interface_initialize()

    LandWidgetContainer *self = (LandWidgetContainer *)super
    land_widget_base_initialize(super, parent, x, y, w, h)
    super->vt = land_widget_container_interface
    self.children = None
    # By default, a container does not use a layout.
    land_widget_layout_disable(super)

    land_widget_theme_initialize(super)

def land_widget_container_new(LandWidget *parent, int x, y, w, h) -> LandWidget *:
    LandWidgetContainer *self
    land_alloc(self)
    land_widget_container_initialize(&self.super, parent, x, y, w, h)
    return &self.super

def land_widget_container_interface_initialize():
    if land_widget_container_interface: return

    land_alloc(land_widget_container_interface)
    land_widget_interface_register(land_widget_container_interface)
    land_widget_container_interface->id = LAND_WIDGET_ID_BASE |\
        LAND_WIDGET_ID_CONTAINER
    land_widget_container_interface->name = land_strdup("container")
    land_widget_container_interface->destroy = land_widget_container_destroy
    land_widget_container_interface->draw = land_widget_container_draw
    land_widget_container_interface->tick = land_widget_container_tick
    land_widget_container_interface->add = land_widget_container_add
    land_widget_container_interface->remove = land_widget_container_remove
    land_widget_container_interface->move = land_widget_container_move
    land_widget_container_interface->size = land_widget_container_size
    land_widget_container_interface->update = land_widget_container_update
    land_widget_container_interface->mouse_tick =\
        land_widget_container_mouse_tick
    land_widget_container_interface->mouse_enter =\
        land_widget_container_mouse_enter
    land_widget_container_interface->mouse_leave =\
        land_widget_container_mouse_leave
    land_widget_container_interface->keyboard_tick =\
        land_widget_container_keyboard_tick
    land_widget_container_interface->keyboard_enter =\
        land_widget_container_keyboard_enter
    land_widget_container_interface->keyboard_leave =\
        land_widget_container_keyboard_leave
