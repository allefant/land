import base, ../list
static import land

class LandWidgetContainer:
    """
    A container is a widget with children. It is not useful all by itself, but
    it the base class of some useful widgets, or can be used to derive your own
    special containers.
    """
    LandWidget super
    LandList *children # we keep a reference to each child.
    LandWidget *mouse # we keep a reference to the focus object.
    LandWidget *keyboard

macro LAND_WIDGET_CONTAINER(widget) ((LandWidgetContainer *)
    land_widget_check(widget, LAND_WIDGET_ID_CONTAINER, __FILE__, __LINE__))

global LandWidgetInterface *land_widget_container_interface

def land_widget_container_destroy(LandWidget *base):
    """Destroy the container and all its children."""
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base)
    if self->mouse:
        land_widget_unreference(self->mouse)

    if self->children:
        LandListItem *item = self->children->first
        while item:
            LandListItem *next = item->next
            LandWidget *child = item->data
            # Detach it. It won't get destroyed if there are still outside
            # references to it.
            child->parent = NULL
            land_widget_unreference(child)
            item = next

        land_list_destroy(self->children)

    land_widget_base_destroy(base)

def land_widget_container_mouse_enter(LandWidget *self, LandWidget *focus):
    pass

def land_widget_container_mouse_leave(LandWidget *super, LandWidget *focus):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if self->mouse:
        self->mouse->got_mouse = 0
        land_call_method(self->mouse, mouse_leave, (self->mouse, focus))
        if self->mouse->got_mouse:
            super->got_mouse = 1
        else:
            land_widget_unreference(self->mouse)
            self->mouse = NULL

def land_widget_container_keyboard_enter(LandWidget *super):
    """ Give keyboard focus to the container, and to children who requested
        focus."""
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if self->children:
        LandListItem *item, *next
        item = self->children->first
        for ; item; item = next:
            next = item->next
            LandWidget *child = item->data

            if child->want_focus:
                child->want_focus = 0
                child->got_keyboard = 1
                land_call_method(child, keyboard_enter, (child))
                self->keyboard = child
                land_widget_reference(self->keyboard)
                break

# Remove keyboard focus from the container and its children.
def land_widget_container_keyboard_leave(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    if self->keyboard:
        self->keyboard->got_keyboard = 0
        land_call_method(self->keyboard, keyboard_leave, (self->keyboard))
        if self->keyboard->got_keyboard:
            super->got_keyboard = 1
            return

        land_widget_unreference(self->keyboard)
        self->keyboard = NULL


# Returns the item/iterator for the given child of the container.
LandListItem *def land_widget_container_child_item(LandWidget *super, *child):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if !self->children:
        return NULL
    LandListItem *item = self->children->first
    while item:
        if item->data == child:
            return item
        item = item->next

    return NULL

def land_widget_container_to_top(LandWidget *super, LandWidget *child):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    LandListItem *item = land_widget_container_child_item(super, child)
    land_list_remove_item(self->children, item)
    land_list_insert_item(self->children, item)

def land_widget_container_draw(LandWidget *base):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base)
    # The base container theme is completely invisible, but derived classes
    # like panel or board will draw themselves here.
    land_widget_theme_draw(base)

    if not self->children:
        return

    if not base->dont_clip:
        int l = base->box.x + base->box.il
        int t = base->box.y + base->box.it
        int r = base->box.x + base->box.w - base->box.ir
        int b = base->box.y + base->box.h - base->box.ib
        land_clip_push()
        land_clip_intersect(l, t, r, b)

    float cl, ct, cr, cb
    land_get_clip(&cl, &ct, &cr, &cb)

    LandListItem *item = self->children->first
    for ; item; item = item->next:
        LandWidget *child = item->data
        if child->hidden: continue
        if not base->dont_clip:
            if (child->box.x <= cr and child->box.x + child->box.w >= cl and
                child->box.y <= cb and child->box.y + child->box.h >= ct):
                land_widget_draw(child)

        else:
            land_widget_draw(child)

    if not base->dont_clip:
        land_clip_pop()

def land_widget_container_move(LandWidget *super, float dx, float dy):
    super->box.x += dx
    super->box.y += dy
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if !self->children:
        return
    LandListItem *item = self->children->first
    while item:
        LandWidget *child = item->data
        land_widget_move(child, dx, dy)
        item = item->next

def land_widget_container_size(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    land_widget_base_size(super)
    if !self->children:
        return
    LandListItem *item = self->children->first
    while item:
        LandWidget *child = item->data
        land_call_method(child, size, (child))
        item = item->next

LandWidget *def land_widget_container_get_at_pos(LandWidget *super, int x, y):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if not self->children:
        return NULL
    LandListItem *item = self->children->last
    for ; item; item = item->prev:
        LandWidget *child = item->data
        if child->hidden: continue
        if (x >= child->box.x && y >= child->box.y &&
            x < child->box.x + child->box.w && y < child->box.y + child->box.h):
            return child

    return NULL

# Transfer the mouse focus inside base to child. If child is NULL, remove any
# mouse focus.
static def transfer_mouse_focus(LandWidget *base, LandWidget *child):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base)
    
    # We can't have this deleted inside any method call or we get a
    # dangling pointer. In case it receives the focus, the reference will
    # be hold until the focus is lost again.
    if (child) land_widget_reference(child)

    # Take focus away?
    if self->mouse:
        self->mouse->got_mouse = 0
        land_call_method(self->mouse, mouse_leave, (self->mouse, child))
        # Retain focus?
        if self->mouse->got_mouse:
            if (child) land_widget_unreference(child)
            return

        land_widget_unreference(self->mouse)
        self->mouse = NULL

    if child:
        child->got_mouse = 1
        land_call_method(child, mouse_enter, (child, self->mouse))
        if not child->got_mouse: # refuses focus:
            land_widget_unreference(child)
            return

    self->mouse = child

static def transfer_keyboard_focus(LandWidget *base):
    # Need to take focus away first?

    base->got_keyboard = 0
    land_widget_container_keyboard_leave(base)
    # Retain focus?
    if base->got_keyboard:
        return

    # At this point, no childs have focus anymore. Next we give focus to
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
    if self->mouse:
        land_call_method(self->mouse, mouse_tick, (self->mouse))
    LandWidget *mouse = land_widget_container_get_at_pos(super, land_mouse_x(),
        land_mouse_y())
    if (mouse != self->mouse && !(land_mouse_b() & 1)):
        transfer_mouse_focus(super, mouse)

    int f = 0
    if self->children:
        LandListItem *item, *next, *last
        item = self->children->first
        last = self->children->last
        for ; item; item = next:
            next = item->next
            LandWidget *child = item->data

            # Propagate up focus request.
            if child->want_focus:
                super->want_focus = 1

            if child->send_to_top:
                land_widget_container_to_top(super, child)
                child->send_to_top = 0
                f = 1

            if item == last:
                break

def land_widget_container_set_mouse(LandWidget *super, LandWidget *mouse):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)
    if mouse != self->mouse:
        transfer_mouse_focus(super, mouse)

def land_widget_container_keyboard_tick(LandWidget *super):
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    if super->want_focus:
        transfer_keyboard_focus(super)

    if self->keyboard:
        land_call_method(self->keyboard, keyboard_tick, (self->keyboard))

def land_widget_container_tick(LandWidget *super):
    land_call_method(super, mouse_tick, (super))
    land_call_method(super, keyboard_tick, (super))

def land_widget_container_add(LandWidget *super, LandWidget *add):

    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super)

    # We increase the reference count of the child only. Increasing the
    # parent's reference (even though there is the ->parent pointer), would
    # cause a cyclic dependancy! We still never get a dangling pointer, since
    # the parent cannot be destroyed without first detaching its children.

    land_add_list_data(&self->children, add)
    land_widget_reference(add)

    add->parent = super

# Containers do not know about layout - the derived class like VBox must make
# sure to also fix up the layout structure when a widget is removed, and should
# then call this method.
def land_widget_container_remove(LandWidget *base, LandWidget *rem):
    ASSERT(rem->parent == base)

    rem->parent = NULL
    land_remove_list_data(&LAND_WIDGET_CONTAINER(base)->children, rem)

    # Whenever the item was added to our container, the container acquired a
    # reference to it, which it has to give up now.
    land_widget_unreference(rem)

def land_widget_container_initialize(LandWidget *super, *parent,
    int x, y, w, h):
   land_widget_container_interface_initialize()

   LandWidgetContainer *self = (LandWidgetContainer *)super
   land_widget_base_initialize(super, parent, x, y, w, h)
   super->vt = land_widget_container_interface
   self->children = NULL

LandWidget *def land_widget_container_new(LandWidget *parent, int x, y, w, h):
    LandWidgetContainer *self
    land_alloc(self)
    land_widget_container_initialize(&self->super, parent, x, y, w, h)
    return &self->super

def land_widget_container_interface_initialize():
    if (land_widget_container_interface) return

    land_alloc(land_widget_container_interface)
    land_widget_interface_register(land_widget_container_interface)
    land_widget_container_interface->id = LAND_WIDGET_ID_BASE |\
        LAND_WIDGET_ID_CONTAINER
    land_widget_container_interface->name = "container"
    land_widget_container_interface->destroy = land_widget_container_destroy
    land_widget_container_interface->draw = land_widget_container_draw
    land_widget_container_interface->tick = land_widget_container_tick
    land_widget_container_interface->add = land_widget_container_add
    land_widget_container_interface->remove = land_widget_container_remove
    land_widget_container_interface->move = land_widget_container_move
    land_widget_container_interface->size = land_widget_container_size
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
