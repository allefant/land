# Polymorphism
#
# The widgets are organized in a class hierarchy. To use polymorphism, you need
# to convert pointers to one class to pointers to a base or specialized class.
# This is done using land_widget_check, which will use the widgets vtable to
# assert that the conversion is possible and generate a runtime error
# otherwise.
#
# Reference counting
#
# The widgets use reference counting to handle deletion. This is a cheap way
# out of dealing with stale references/dangling pointers. A GUI without either reference counting
# or garbage collection is possible, it just needs some more design work. In
# our case here, following a KISS principle, we do simple naive reference counting,
# and leave the user to deal with possible problems like circular references.
#
# In the normal case, it works like this: You create a widget, and have to
# pass along a parent widget to the constructor. Now, the parent will hold a
# reference to the new window. There is no reference from the child to he
# parent, despite the parent field referencing the parent. This is done to
# avoid complications with cyclic references. If your own widgets contain
# cyclic references in another way, you should understand how the reference
# counting works.
#
# The first consequence of the above is, you always should manually reference the
# top level window, since it has no parent it is referenced by.
#
# The apparent problem is the possible dangling pointer of a child to its
# parent. But it should be save, since whenever the parent is deleted, it will
# delete all its children anyway.
#
# An example:
# desktop = desktop_new()
# reference(desktop)
# child = window_new(desktop)
# unreference(desktop)
#
# This does what is expected. The only reference to desktop is removed manually,
# therefore it gets destroyed. The destructor will detach all children. The only
# child in this case will therefore drop its reference count to zero, and get
# destroyed as well.
#
# desktop = desktop_new()
# reference(desktop)
# child = window_new(desktop)
# reference(child)
# unreference(desktop)
#
# Here, a reference is kept to child. Maybe it is the window with keyboard
# focus, and the focus handler holds a reference to it. So, when the desktop
# is destroyed, first all childs are detached again. This means, the parent
# member of child is set to NULL, and its reference is decreased. Since there
# is still the manual reference, nothing else will be done. The desktop itself
# however is destroyed. Also note that any other childs without a reference
# would be destroyed correctly, and it also would work recursively down for
# their childs. Only the child window stays, and the focus handler won't
# crash.
#
# unreference(child)
#
# If the focus handler is done, the reference of child will now drop to zero,
# and it is destroyed as well.
#
# Now, about cyclic references, just either don't use them, or else take care
# to resolve them before dropping the last reference into the cycle. As an
# example, you make a watchdog window, which somehow watches another window.
# So, you play good, and along with storing a reference to that other window,
# you increase the reference count of the other window, just so you never get
# a dangling pointer. In your destructor, you release the reference again, so
# everything seems to work out. But consider this:
#
# desktop = new_widget(NULL)
# reference(desktop)
# watchdog = new_widget(desktop)
# watchdog_watch(desktop)
# unreference(desktop)
#
# Yikes. Now you see the problem. Although nobody holds a reference to watchdog,
# and we remove the only real reference to desktop, neither of them gets deleted.
# Worse, neither of them can ever be deleted again, since the only reference to
# either is from each other.
#
# Simple rule here would be: The watchdog only ever should watch a sibling or
# unrelated widget, never a parent. Of course, in practice, widgets could get
# reparented and whatever, so things like this need watching out. And there
# are many other cases. Also, you never have to use the reference counting. You
# just need to understand that Land provides no way to directly and forcefully
# delete one of its widgets, and why it is like that.
#

import ../hash, gul

# A widget ID must contain the bit-pattern of its parent's ID.

macro  LAND_WIDGET_ID_BASE         0x00000001 # no visual, no layout
macro  LAND_WIDGET_ID_CONTAINER    0x00000011 # no visual, no layout
macro  LAND_WIDGET_ID_SCROLLING    0x00000111 # visual, layout
macro  LAND_WIDGET_ID_VBOX         0x00000211 # no visual, layout
macro  LAND_WIDGET_ID_LIST         0x00001211 # visual, layout
macro  LAND_WIDGET_ID_HBOX         0x00000311 # no visual, layout
macro  LAND_WIDGET_ID_TABBAR       0x00001311 # visual, layout
macro  LAND_WIDGET_ID_SPIN         0x00002311 # visual, layout
macro  LAND_WIDGET_ID_PANEL        0x00000411 # visual, layout
macro  LAND_WIDGET_ID_BOARD        0x00000511 # visual, no layout
macro  LAND_WIDGET_ID_MENU         0x00000611
macro  LAND_WIDGET_ID_MENUBAR      0x00001611
macro  LAND_WIDGET_ID_BOOK         0x00000711
macro  LAND_WIDGET_ID_BUTTON       0x00000021
macro  LAND_WIDGET_ID_MENUBUTTON   0x00000121
macro  LAND_WIDGET_ID_MENUITEM     0x00000221
macro  LAND_WIDGET_ID_LISTITEM     0x00000321
macro  LAND_WIDGET_ID_TAB          0x00000421
macro  LAND_WIDGET_ID_SPINBUTTON   0x00000521
macro  LAND_WIDGET_ID_SCROLLBAR    0x00000031
macro  LAND_WIDGET_ID_EDIT         0x00000041

macro  LAND_WIDGET_ID_USER         0x80000000

class LandWidgetInterface:
    int id
    char const *name

    void (*init)(LandWidget *self)
    void (*enter)(LandWidget *self)
    void (*tick)(LandWidget *self)

    # Called when the mouse focus is transferred to the widget. The got_mouse
    # flag can be used to decline focus.
    void (*mouse_enter)(LandWidget *self, LandWidget *focus)
    void (*mouse_tick)(LandWidget *self)
    # This is called for the widget losing the mouse focus. It has the
    # possibility to retain focus with the got_mouse flag.
    void (*mouse_leave)(LandWidget *self, LandWidget *focus)

    # Called when the keyboard focus is transferred to the widget. This will
    # only happen if the want_focus flag is set, and focus can be declined
    # with the got_keyboard flag.
    void (*keyboard_enter)(LandWidget *self)
    void (*keyboard_tick)(LandWidget *self)
    void (*keyboard_leave)(LandWidget *self)

    void (*add)(LandWidget *self, LandWidget *add)
    void (*move)(LandWidget *self, float dx, float dy)
    void (*size)(LandWidget *self)

    void (*get_inner_size)(LandWidget *self, float *w, float *h)

    void (*draw)(LandWidget *self)
    void (*leave)(LandWidget *self)
    void (*destroy)(LandWidget *self)

# A Land widget.
#
# Event the most basic widget already is a quite heavy object:
# - A widget can have arbitrary string-keyed properties attached to it.
# - A widget is reference counted.
# - A widget has a theme.
#
class LandWidget:
    LandWidgetInterface *vt
    LandWidget *parent
    LandLayoutBox box

    # internal state
    unsigned int got_mouse : 1; # this widget has the mouse focus
    unsigned int got_keyboard : 1; # this widget has the keyboard focus
    unsigned int send_to_top : 1; # move this widget to top in next tick
    unsigned int want_focus : 1; # give keyboard focus to this widget
    unsigned int dont_clip : 1; # children can draw outside this widget
    unsigned int no_decoration : 1; # draw nothing except contents
    unsigned int only_border : 1; # draw only a border, for performance reasons
    unsigned int hidden : 1; # this is not displayed at all, e.g. hidden scrollbar
    unsigned int no_layout : 1; # inhibit layout updates, for performance reasons

    # user state
    unsigned int selected : 1; # e.g. checked checkbox or pressed button
    unsigned int highlighted : 1; # item with mouse hovering over it
    unsigned int disabled : 1; # e.g. button who cannot currently be pressed

    int reference; # reference counting

    LandHash *properties; # arbitrary string-keyed properties

    struct LandWidgetTheme *theme; # this widget's theme

class LandWidgetProperty:
    void (*destroy)(void *data)
    void *data

macro LAND_WIDGET(widget) ((LandWidget *) land_widget_check(widget,
    LAND_WIDGET_ID_BASE, __FILE__, __LINE__))

static import widget/layout, util

global LandWidgetInterface *land_widget_base_interface
LandArray *land_widget_interfaces

void *def land_widget_check(void const *ptr, int id, char const *file,
    int linenum):
    LandWidget const *widget = ptr
    if (widget->vt->id & id) == id:
        return (void *)ptr # should provide a const version of the whole
        #function instead
    land_exception("%s: %d: Widget cannot be converted.", file, linenum)
    return NULL

def land_widget_set_property(LandWidget *self, char const *property,
    void *data, void (*destroy)(void *data)):
    if not self->properties: self->properties = land_hash_new()
    LandWidgetProperty *prop
    land_alloc(prop)
    prop->data = data
    prop->destroy = destroy
    land_hash_insert(self->properties, property, prop)

def land_widget_del_property(LandWidget *self, char const *property):
    if not self->properties: return
    LandWidgetProperty *prop = land_hash_remove(self->properties, property)
    if prop->destroy: prop->destroy(prop)

void *def land_widget_get_property(LandWidget *self, char const *property):
    if not self->properties: return NULL
    LandWidgetProperty *prop = land_hash_get(self->properties, property)
    if prop: return prop->data
    return NULL

def land_widget_remove_all_properties(LandWidget *self):
    LandHash *hash = self->properties
    if not hash: return
    int i
    for i = 0; i < hash->size; i++:
        if hash->entries[i]:
            int j
            for j = 0; j < hash->entries[i]->n; j++:
                LandWidgetProperty *prop = hash->entries[i][j].data
                if prop->destroy: prop->destroy(prop->data)
                land_free(prop)



    land_hash_destroy(self->properties)
    self->properties = NULL

def land_widget_base_initialize(LandWidget *self, *parent, int x, y, w, h):
    land_widget_base_interface_initialize()

    gul_box_initialize(&self->box)
    self->box.x = x
    self->box.y = y
    self->box.w = w
    self->box.h = h
    land_widget_layout_set_minimum_size(self, w, h)
    if parent:
        self->theme = parent->theme
        land_call_method(parent, add, (parent, self))


LandWidget *def land_widget_base_new(LandWidget *parent, int x, y, w, h):
    LandWidget *self
    land_alloc(self)
    land_widget_base_initialize(self, parent, x, y, w, h)
    return self

def land_widget_interfaces_destroy_all(void):
    int i
    for i = 0; i < land_widget_interfaces->count; i++:
        land_free(land_array_get_nth(land_widget_interfaces, i))

    land_array_destroy(land_widget_interfaces)

def land_widget_interface_register(LandWidgetInterface *vt):
    if not land_widget_interfaces:
        atexit(land_widget_interfaces_destroy_all)

    land_array_add_data(&land_widget_interfaces, vt)

LandWidgetInterface *def land_widget_copy_interface(LandWidgetInterface *basevt,
    char const *name):
    LandWidgetInterface *vt
    land_alloc(vt)
    memcpy(vt, basevt, sizeof *vt)
    vt->name = name

    land_widget_interface_register(vt)

    return vt

def land_widget_create_interface(LandWidget *widget, char const *name):
    widget->vt = land_widget_copy_interface(widget->vt, name)

LandWidget *def land_widget_new(LandWidget *parent, int x, y, w, h):
    LandWidget *self
    land_alloc(self)
    land_widget_base_initialize(self, parent, x, y, w, h)
    return self

def land_widget_base_destroy(LandWidget *self):
    land_widget_remove_all_properties(self)
    gul_box_deinitialize(&self->box)
    land_free(self)

static def land_widget_really_destroy(LandWidget *self):
    if self->vt->destroy:
        self->vt->destroy(self)
    else:
        land_log_message("*** widget without destructor?\n")
        land_widget_base_destroy(self)


def land_widget_unreference(LandWidget *self):
    self->reference--
    if self->reference <= 0:
        land_widget_really_destroy(self)

def land_widget_reference(LandWidget *self):
    self->reference++

def land_widget_base_mouse_enter(LandWidget *self, LandWidget *focus):
    pass

def land_widget_base_mouse_leave(LandWidget *self, LandWidget *focus):
    pass

def land_widget_base_move(LandWidget *self, float dx, float dy):
    self->box.x += dx
    self->box.y += dy

def land_widget_move(LandWidget *self, float dx, float dy):
    if self->vt->move:
        self->vt->move(self, dx, dy)
    else:
        land_widget_base_move(self, dx, dy)


def land_widget_base_size(LandWidget *self):
    land_widget_layout_inhibit(self)
    int r = land_widget_layout(self)
    if r:
        land_widget_layout_adjust(self, r & 1, r & 2)

    land_widget_layout_enable(self)

def land_widget_size(LandWidget *self, float dx, dy):
    self->box.w += dx
    self->box.h += dy
    land_call_method(self, size, (self))

# Called inside mouse_leave, will keep the mouse focus, and no other widget
# can get highlighted.
#
def land_widget_retain_mouse_focus(LandWidget *self):
    self->got_mouse = 1

# Called inside mouse_enter, inhibits highlighting of the widget.
def land_widget_refuse_mouse_focus(LandWidget *self):
    self->got_mouse = 0

# Called in mouse_tick (or elsewhere), will cause the widget to receive the
# keyboard focus.
#
def land_widget_request_keyboard_focus(LandWidget *self):
    self->want_focus = 1

# Called in keyboard_leave to keep the focus. Doesn't usually make sense.
def land_widget_retain_keyboard_focus(LandWidget *self):
    self->got_keyboard = 1

def land_widget_tick(LandWidget *self):
    land_call_method(self, tick, (self))

def land_widget_draw(LandWidget *self):
    if self->hidden: return
    int pop = 0
    if !self->dont_clip:
        land_clip_push()
        land_clip_on()
        land_clip_intersect(self->box.x, self->box.y, self->box.x + self->box.w,
            self->box.y + self->box.h)
        pop = 1

    land_call_method(self, draw, (self))
    if pop:
        land_clip_pop()


def land_widget_hide(LandWidget *self):
    if self->hidden: return
    self->hidden = 1
    self->box.flags |= GUL_HIDDEN
    land_widget_layout(self->parent)

def land_widget_unhide(LandWidget *self):
    if not self->hidden: return
    self->hidden = 0
    self->box.flags &= ~GUL_HIDDEN
    land_widget_layout(self->parent)

def land_widget_base_interface_initialize(void):
    if land_widget_base_interface: return

    land_alloc(land_widget_base_interface)
    land_widget_interface_register(land_widget_base_interface)
    land_widget_base_interface->id = LAND_WIDGET_ID_BASE
    land_widget_base_interface->name = "base"
    land_widget_base_interface->size = land_widget_base_size
    land_widget_base_interface->destroy = land_widget_base_destroy
