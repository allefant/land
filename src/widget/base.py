"""
Simple themeable widgets to use for in-game user interface elements.

This module implements a simple graphical user interface on top of Land.

= Some Features =

 * Simple. This is intended to be used in-game, so no advanced features.
 * A widget is basically a box. It can contain other boxes, to which mouse and
   keyboard input is dispatched.
 * Themeable, either with custom drawing, or bitmap themes.

= Mouse Focus =

Mouse focus is given to the window under the mouse, if the left button is not
being held. Else the focused window retains focus as long as the left mouse
button is being held pressed, even if the mouse leaves the window.

= Keyboard Focus =

Keyboard focus is only given to widgets requesting it. A focused window retains
keyboard focus, unless focus is transferred to another window.

A widget will normally ask for keyboard focus being transferred to it, when
the mouse is clicked over it, or when the TAB key is pressed and it is the
next in the widget cycle. This cycle is constructed by walking all widgets in
order, starting with the parent, then the children, recursively.

= Layout =

About using the auto layout:

 * Each widget has an outer box, which is how much space it takes up inside
   its parent.

 * Additionally, it has an inner box, which is the space available to
   children. The inner box is 6 values: il, it, ir, ib, hgap, vgap. The first
   4 are for a border all around the widget, the last 2 are gaps between
   multiple children.

 * The space between outer and inner box is usually filled with some kind of
   border by the themeing.

 * The layout allows layers, so child windows can share the same space.

 * By default, container widgets try to fill up as much space as they can, so
   if you place e.g. a VBox onto the desktop, it fills it up completely when
   using auto layout. Non-container widgets on the other hand usually try to
   be as small as possible, e.g. a button will try to fit around the text/image
   inside it. You can of course change for each widget how it behaves.

= Themeing =

Each widget has a pointer to a theme. On creation, a widget inherits this
theme from its parent. So usually is is enough to set a theme for the
desktop, then all widgets spawned from it will inherit the theme. And it's
also easy to have per-widget themes, either for a single widget, or for a
window or menu. In the latter case, simply set the theme before creating
children.

Themes are built from bitmaps. This keeps them very simple, and should be
enough in most cases. And of course, if you absolutely don't want to, you
don't have to use themes. Simply override the draw method of all widgets
which you want to draw yourself.

= Polymorphism =

The widgets are organized in a class hierarchy. To use polymorphism, you need
to convert pointers to one class to pointers to a base or specialized class.
This is done using land_widget_check, which will use the widgets vtable to
assert that the conversion is possible and generate a runtime error
otherwise.

= Reference counting =

The widgets use reference counting to handle deletion. This is a cheap way
out of dealing with stale references/dangling pointers. A GUI without either reference counting
or garbage collection is possible, it just needs some more design work. In
our case here, following a KISS principle, we do simple naive reference counting,
and leave the user to deal with possible problems like circular references.

In the normal case, it works like this: You create a widget, and have to
pass along a parent widget to the constructor. Now, the parent will hold a
reference to the new widget. There is no reference from the child to the
parent, despite the parent field referencing the parent. This is done to
avoid complications with cyclic references. If your own widgets contain
cyclic references in another way, you should understand how the reference
counting works.

The first consequence of the above is, you always should manually reference the
top level window, since it has no parent it is referenced by.

The apparent problem is the possible dangling pointer of a child to its
parent. But it should be save, since whenever the parent is deleted, it will
delete all its children anyway.

= An example =

desktop = desktop_new()
reference(desktop)
child = window_new(desktop)
unreference(desktop)

This does what is expected. The only reference to desktop is removed manually,
therefore it gets destroyed. The destructor will detach all children. The only
child in this case will therefore drop its reference count to zero, and get
destroyed as well.

desktop = desktop_new()
reference(desktop)
child = window_new(desktop)
reference(child)
unreference(desktop)

Here, a reference is kept to child. Maybe it is the window with keyboard
focus, and the focus handler holds a reference to it. So, when the desktop
is destroyed, first all childs are detached again. This means, the parent
member of child is set to NULL, and its reference is decreased. Since there
is still the manual reference, nothing else will be done. The desktop itself
however is destroyed. Also note that any other childs without a reference
would be destroyed correctly, and it also would work recursively down for
their childs. Only the child window stays, and the focus handler won't
crash.

unreference(child)

If the focus handler is done, the reference of child will now drop to zero,
and it is destroyed as well.

Now, about cyclic references, just either don't use them, or else take care
to resolve them before dropping the last reference into the cycle. As an
example, you make a watchdog window, which somehow watches another window.
So, you play good, and along with storing a reference to that other window,
you increase the reference count of the other window, just so you never get
a dangling pointer. In your destructor, you release the reference again, so
everything seems to work out. But consider this:

desktop = new_widget(NULL)
reference(desktop)
watchdog = new_widget(desktop)
watchdog_watch(desktop)
unreference(desktop)

Yikes. Now you see the problem. Although nobody holds a reference to watchdog,
and we remove the only real reference to desktop, neither of them gets deleted.
Worse, neither of them can ever be deleted again, since the only reference to
either is from each other.

Simple rule here would be: The watchdog only ever should watch a sibling or
unrelated widget, never a parent. Of course, in practice, widgets could get
reparented and whatever, so things like this need watching out for. And there
are many other cases. Also, you never have to use the reference counting. You
just need to understand that Land provides no way to directly and forcefully
delete one of its widgets, and why it is like that.
"""
import land.common
import land.hash
import gul

# A widget ID must contain the bits of the parent.
macro LAND_WIDGET_ID_BASE           0x00000001 # no visual, no layout
macro LAND_WIDGET_ID_CONTAINER      0x00000011 # no visual, no layout
macro LAND_WIDGET_ID_SCROLLING      0x00000111 # visual, layout
macro LAND_WIDGET_ID_SCROLLING_TEXT 0x00001111
macro LAND_WIDGET_ID_VBOX           0x00000211 # no visual, layout
macro LAND_WIDGET_ID_LIST           0x00001211 # visual, layout
macro LAND_WIDGET_ID_HBOX           0x00000311 # no visual, layout
macro LAND_WIDGET_ID_TABBAR         0x00001311 # visual, layout
macro LAND_WIDGET_ID_SPIN           0x00002311 # visual, layout
macro LAND_WIDGET_ID_BOOKPAGE       0x00003311 # visual, layout
macro LAND_WIDGET_ID_PANEL          0x00000411 # visual, layout
macro LAND_WIDGET_ID_BOARD          0x00000511 # visual, no layout
macro LAND_WIDGET_ID_MENU           0x00000611
macro LAND_WIDGET_ID_MENUBAR        0x00001611
macro LAND_WIDGET_ID_BOOK           0x00000711
macro LAND_WIDGET_ID_SLIDER         0x00000811
macro LAND_WIDGET_ID_CHECKBOX       0x00000911
macro LAND_WIDGET_ID_BUTTON         0x00000021
macro LAND_WIDGET_ID_MENUBUTTON     0x00000121
macro LAND_WIDGET_ID_MENUITEM       0x00000221
macro LAND_WIDGET_ID_LISTITEM       0x00000321
macro LAND_WIDGET_ID_TAB            0x00000421
macro LAND_WIDGET_ID_SPINBUTTON     0x00000521
macro LAND_WIDGET_ID_SCROLLBAR      0x00000031
macro LAND_WIDGET_ID_EDIT           0x00000041
macro LAND_WIDGET_ID_HANDLE         0x00000051

macro LAND_WIDGET_ID_USER           0x80000000

class LandWidgetInterface:
    int id
    char *name

    void (*init)(LandWidget *self)
    void (*enter)(LandWidget *self)
    void (*tick)(LandWidget *self)

    # Called when the mouse focus is transferred to the widget.
    void (*mouse_enter)(LandWidget *self)
    void (*mouse_tick)(LandWidget *self)
    # This is called for the widget losing the mouse focus. It has the
    # possibility to retain focus with the got_mouse flag.
    void (*mouse_leave)(LandWidget *self)

    # Called when the keyboard focus is transferred to the widget. This will
    # only happen if the want_focus flag is set, and focus can be declined
    # with the got_keyboard flag.
    void (*keyboard_enter)(LandWidget *self)
    void (*keyboard_tick)(LandWidget *self)
    void (*keyboard_leave)(LandWidget *self)

    # The add and remove methods are called to add/remove a widget from a
    # container widget. Adding is done in two steps, the add method just adds a
    # widget without doing any layout updates, and the update method then
    # instructs the container to adjust itself to the new children.
    void (*add)(LandWidget *self, LandWidget *add)
    void (*update)(LandWidget *self)
    void (*remove)(LandWidget *self, LandWidget *rem)

    # Called whenever the layout algorithm is applied involving the widget.
    # The first one is called befor updating child widgets, the second
    # afterwards.
    void (*layout_changing)(LandWidget *self)
    void (*layout_changed)(LandWidget *self)

    # Called whenever the widget's absolute position changes. It is called
    # after the movement has been done.
    void (*move)(LandWidget *self, float dx, float dy)
    # Called whenever the widget's size changes. It is called after te resizing
    # was done.
    # fixme: if the layout algorithm updates container children, we only
    # call layout_changing and layout_changed above, but not 'size'
    void (*size)(LandWidget *self, float dx, float dy)

    void (*get_inner_size)(LandWidget *self, float *w, float *h)

    void (*draw)(LandWidget *self)
    void (*leave)(LandWidget *self)
    void (*destroy)(LandWidget *self)

class LandWidget:
    """
    The base widget class.

    Even the most basic widget already is a quite heavy object:
    * It has a parent.
    * It has an on-screen position.
    * It has layout parameters.
    * It has various flags (like keyboard focus, hidden, ...).
    * Each widget can have arbitrary string-keyed properties attached to it.
    * Each widget is reference counted.
    * Each widget has a theme pointer.
    """
    LandWidgetInterface *vt
    LandWidget *parent
    LandLayoutBox box

    # internal state
    unsigned int got_mouse with 1 # this widget has the mouse focus
    unsigned int got_keyboard with 1 # this widget has the keyboard focus
    unsigned int send_to_top with 1 # move this widget to top in next tick
    unsigned int want_focus with 1 # give keyboard focus to this widget
    unsigned int dont_clip with 1 # children can draw outside this widget
    unsigned int no_clip_check with 1 # even when the parent does use clipping,
        # do not skip drawing of this child if it is outside the clip bounds
    unsigned int no_decoration with 1 # draw nothing except contents
    unsigned int only_border with 1 # draw only a border, for performance
        # reasons
    # Widget is not displayed at all, e.g. hidden scrollbar.
    unsigned int hidden with 1
    # Like hidden but for mouse handling only
    unsigned int nomouse with 1
    # inhibit layout updates, for performance reasons
    unsigned int no_layout with 1
    # when changing the layout from within the layout update this flag
    # is used to avoid (infinite) recursion
    unsigned int no_layout_notify with 1

    unsigned int layout_hack with 1 # signals that the layout calculation needs
                                    # to start over

    # user state
    unsigned int selected with 1 # e.g. checked checkbox or pressed button
    unsigned int highlighted with 1 # item with mouse hovering over it
    unsigned int disabled with 1 # e.g. button which cannot currently be pressed

    int reference # reference counting

    LandHash *properties # arbitrary string-keyed properties

    struct LandWidgetThemeElement *element # this widget's theme
    # FIXME: get_inner_size() method should be called and those two
    # properties removed. They cache the minimum dimensions needed for
    # the contents of the window (without theme border).
    int inner_w, inner_h

class LandWidgetProperty:
    void (*destroy)(void *data)
    void *data

macro LAND_WIDGET(widget) ((LandWidget *) land_widget_check(widget,
    LAND_WIDGET_ID_BASE, __FILE__, __LINE__))

static import layout, land/util

global LandWidgetInterface *land_widget_base_interface
static LandArray *land_widget_interfaces

def land_widget_is(LandWidget const *self, int id) -> int:
    """
    Return true if the widget has the given type (or one derived from it).
    """
    int i
    for i = 0 while i < 7 with i++:
        int digit = id & (0xf << (i * 4))
        if not digit: break
        if (self.vt->id & (0xf << (i * 4))) != digit: return 0
    return 1

def land_widget_check(void const *ptr, int id, char const *file,
    int linenum) -> void *:
    LandWidget const *widget = ptr
    if land_widget_is(widget, id):
        return (void *)ptr # should provide a const version of the whole
        #function instead
    land_exception("%s: %d: Widget cannot be converted.", file, linenum)
    return NULL

def land_widget_info_string(LandWidget *w) -> char const *:
    static char str[1024]
    if not w:
        strcpy(str, "none")
    elif land_widget_is(w, LAND_WIDGET_ID_MENU):
        LandWidgetContainer *c = (void *)w
        int n = 0
        if c->children: n = c->children->count
        sprintf(str, "menu (%d items)", n)
    elif land_widget_is(w, LAND_WIDGET_ID_MENUBAR):
        LandWidgetContainer *c = (void *)w
        int n = 0
        if c->children: n = c->children->count
        sprintf(str, "menubar (%d items)", n)
    elif land_widget_is(w, LAND_WIDGET_ID_MENUITEM):
        LandWidgetButton *b = (void *)w
        sprintf(str, "menuitem %s", b->text)
    elif land_widget_is(w, LAND_WIDGET_ID_MENUBUTTON):
        LandWidgetButton *b = (void *)w
        sprintf(str, "menubutton %s", b->text)
    elif land_widget_is(w, LAND_WIDGET_ID_BUTTON):
        LandWidgetButton *b = (void *)w
        if b.text:
            sprintf(str, "button %.10s", b.text)
        elif b.spans:
            sprintf(str, "button (%d spans)", land_array_count(b->spans->spans))
        else:
            sprintf(str, "button (no text)")
    elif land_widget_is(w, LAND_WIDGET_ID_CHECKBOX):
        sprintf(str, "checkbox")
    elif land_widget_is(w, LAND_WIDGET_ID_BOOK):
        sprintf(str, "book")
    elif land_widget_is(w, LAND_WIDGET_ID_SCROLLING):
        sprintf(str, "scrolling")
    elif land_widget_is(w, LAND_WIDGET_ID_SCROLLBAR):
        sprintf(str, "scrollbar")
    elif land_widget_is(w, LAND_WIDGET_ID_BOOKPAGE):
        sprintf(str, "bookpage")
    elif land_widget_is(w, LAND_WIDGET_ID_LIST):
        sprintf(str, "list")
    elif land_widget_is(w, LAND_WIDGET_ID_LISTITEM):
        sprintf(str, "listitem")
    elif land_widget_is(w, LAND_WIDGET_ID_VBOX):
        sprintf(str, "vbox")
    elif land_widget_is(w, LAND_WIDGET_ID_HBOX):
        sprintf(str, "hbox")
    elif land_widget_is(w, LAND_WIDGET_ID_PANEL):
        sprintf(str, "panel")
    elif land_widget_is(w, LAND_WIDGET_ID_CONTAINER):
        sprintf(str, "container")
    elif land_widget_is(w, LAND_WIDGET_ID_BASE):
        sprintf(str, "base")
    else:
        sprintf(str, "unknown (%d)", w.vt.id)
    return str

def land_widget_set_property(LandWidget *self, char const *property,
    void *data, void (*destroy)(void *data)):
    if not self.properties: self->properties = land_hash_new()
    LandWidgetProperty *prop
    land_alloc(prop)
    prop->data = data
    prop->destroy = destroy
    land_hash_insert(self.properties, property, prop)

def land_widget_del_property(LandWidget *self, char const *property):
    if not self.properties: return
    LandWidgetProperty *prop = land_hash_remove(self.properties, property)
    if prop->destroy: prop->destroy(prop)

def land_widget_get_property(LandWidget *self, char const *property) -> void *:
    if not self.properties: return None
    LandWidgetProperty *prop = land_hash_get(self.properties, property)
    if prop: return prop->data
    return None

def land_widget_remove_all_properties(LandWidget *self):
    LandHash *hash = self.properties
    if not hash: return
    int i
    for i = 0 while i < hash->size with i++:
        if hash->entries[i]:
            int j
            for j = 0 while j < hash->entries[i]->n with j++:
                LandWidgetProperty *prop = hash->entries[i][j].data
                if prop->destroy: prop->destroy(prop->data)
                land_free(prop)

    land_hash_destroy(self.properties)
    self.properties = None

def land_widget_base_initialize(LandWidget *self, *parent, int x, y, w, h):
    land_widget_base_interface_initialize()

    land_widget_layout_initialize(self, x, y, w, h)
    self.vt = land_widget_base_interface
    land_widget_layout_set_minimum_size(self, w, h)
    if parent:
        # Retrieve "base" theme element.
        if parent->element:
            self.element = land_widget_theme_find_element(
                parent->element->theme, self)
        land_call_method(parent, add, (parent, self))
    else:
        self.element = land_widget_theme_find_element(
            land_widget_theme_default(), self)

def land_widget_base_new(LandWidget *parent, int x, y, w, h) -> LandWidget *:
    LandWidget *self
    land_alloc(self)
    land_widget_base_initialize(self, parent, x, y, w, h)
    return self

def land_widget_remove(LandWidget *self):
    """Remove a widget from its parent.
    Note: If the reference held by the parent was the last this will
    also destroy the widget.
    """
    if not self.parent: return
    land_call_method(self.parent, remove, (self->parent, self))

def land_widget_interfaces_destroy_all():
    int n = land_array_count(land_widget_interfaces)
    land_log_message("land_widget_interfaces_destroy_all (%d)\n", n)
    int i
    for i = 0 while i < n with i++:
        LandWidgetInterface *f = land_array_get_nth(land_widget_interfaces, i)
        land_free(f->name)
        land_free(f)

    land_array_destroy(land_widget_interfaces)

def land_widget_interface_register(LandWidgetInterface *vt):
    """Register a new widget interface with Land.
    The interface is then owned by Land, and you should not try to free the
    passed pointer. Land will automatically free it when you call land_quit().
    """
    if not land_widget_interfaces:
        land_log_message("land_widget_interfaces\n")
        land_exit_function(land_widget_interfaces_destroy_all)

    land_array_add_data(&land_widget_interfaces, vt)

def land_widget_copy_interface(LandWidgetInterface *basevt,
    char const *name) -> LandWidgetInterface *:
    LandWidgetInterface *vt
    land_alloc(vt)
    memcpy(vt, basevt, sizeof *vt)
    vt->name = land_strdup(name)

    land_widget_interface_register(vt)

    return vt

def land_widget_create_interface(LandWidget *widget, char const *name):
    widget->vt = land_widget_copy_interface(widget->vt, name)
    land_widget_theme_update(widget)

def land_widget_base_destroy(LandWidget *self):
    land_widget_remove_all_properties(self)
    land_internal_land_gul_box_deinitialize(&self.box)
    land_free(self)

static def land_widget_really_destroy(LandWidget *self):
    if self.vt->destroy:
        self.vt->destroy(self)
    else:
        land_log_message("*** widget without destructor?\n")
        land_widget_base_destroy(self)

def land_widget_unreference(LandWidget *self):
    self.reference--
    if self.reference <= 0:
        land_widget_really_destroy(self)

def land_widget_reference(LandWidget *self):
    self.reference++

def land_widget_base_mouse_enter(LandWidget *self, LandWidget *focus):
    pass

def land_widget_base_mouse_leave(LandWidget *self, LandWidget *focus):
    pass

def land_widget_base_move(LandWidget *self, float dx, dy):
    pass

def land_widget_move(LandWidget *self, float dx, dy):
    """
    Moves the widget.
    """
    self.box.x += dx
    self.box.y += dy
    land_call_method(self, move, (self, dx, dy))

def land_widget_keep_in_parent(LandWidget *self):
    LandWidget *parent = self.parent
    float r = self.box.x + self.box.w
    float pr = parent.box.x + parent.box.w
    if r > pr:
        land_widget_move(self, pr - r, 0)

def land_widget_move_to(LandWidget *self, float x, y):
    land_widget_move(self, x - self.box.x, y - self.box.y)

def land_widget_center(LandWidget *self):
    land_widget_align(self, LandAlignCenter | LandAlignMiddle)

def land_widget_align(LandWidget *self, int align):
    int dw = land_display_width()
    int dh = land_display_height()
    int x = self.box.x
    int y = self.box.y
    int w = self.box.w
    int h = self.box.h

    int px = x
    int py = y

    if align & LandAlignRight:
        px = dw - w
    if align & LandAlignCenter:
        px = (dw - w) / 2
    if align & LandAlignBottom:
        py = dh - h
    if align & LandAlignMiddle:
        py = (dh - h) / 2

    land_widget_move(self, px - x, py - y)

def land_widget_base_size(LandWidget *self, float dx, dy):
    pass

def land_widget_size(LandWidget *self, float dx, dy):
    """
    Resizes a widget.
    """
    self.box.w += dx
    self.box.h += dy
    land_call_method(self, size, (self, dx, dy))
    # after a resize we need to update the layout
    #land_widget_layout(self)

def land_widget_resize(LandWidget *self, float dx, dy):
    """
    Changes the minimum size of the widget to its current size modified by the
    given offset.
    """
    self.box.min_width = self->box.w + dx
    self.box.min_height = self->box.h + dy
    land_widget_size(self, dx, dy)

def land_widget_set_size_permanent(LandWidget *self, float w, float h):
    land_widget_resize(self, w - self.box.w, h - self->box.h)

def land_widget_set_size(LandWidget *self, float w, float h):
    land_widget_size(self, w - self.box.w, h - self->box.h)

def land_widget_set_height(LandWidget *self, float h):
    land_widget_resize(self, 0, h - self->box.h)

def land_widget_retain_mouse_focus(LandWidget *self):
    """
    Called inside mouse_leave, will keep the mouse focus, and no other widget
    can get highlighted.
    """
    self.got_mouse = 1

def land_widget_refuse_mouse_focus(LandWidget *self):
    """
    Called inside mouse_enter, inhibits highlighting of the widget.
    """
    self.got_mouse = 0

def land_widget_request_keyboard_focus(LandWidget *self):
    """
    Called in mouse_tick (or elsewhere), will cause the widget to receive the
    keyboard focus.
    """
    auto w = self
    while w:
        w.want_focus = True
        w = w.parent

def land_widget_retain_keyboard_focus(LandWidget *self):
    """
    Called in keyboard_leave to keep the focus. Doesn't usually make sense.
    """
    self.got_keyboard = 1

def land_widget_tick(LandWidget *self):
    """
    Call this regularly on your desktop widget. It's the base function which is
    needed in any widgets application to handle input to the widgets. The other
    important function is land_widget_draw, which handles display of widgets.
    """
    land_call_method(self, tick, (self))

def land_widget_draw(LandWidget *self):
    """
    Draw a widget on its current position. Call this on your desktop widget to
    display all of your widgets. This function and land_widget_tick are the two
    functions you should call on your desktop widget in each widgets using
    application.
    """
    if self.hidden: return
    int pop = 0
    if not self.dont_clip:
        land_clip_push()
        land_clip_on()

        land_clip_intersect(self.box.x, self->box.y, self->box.x + self->box.w,
            self.box.y + self->box.h)

        pop = 1

    land_call_method(self, draw, (self))
    if pop:
        land_clip_pop()

def land_widget_hide(LandWidget *self):
    """
    Hide the widget. It will not be displayed anymore, and also not take up any
    more space.
    """
    if self.hidden: return
    self.hidden = 1
    self.box.flags |= GUL_HIDDEN
    if self.parent: land_widget_layout(self->parent)

def land_widget_unhide(LandWidget *self):
    """
    Unhide the widget.
    """
    if not self.hidden: return
    self.hidden = 0
    self.box.flags &= ~GUL_HIDDEN
    if self.parent: land_widget_layout(self->parent)

def land_widget_set_hidden(LandWidget *self, bool hidden):
    if self.hidden == hidden: return
    self.hidden = hidden
    self.box.flags ^= GUL_HIDDEN
    if self.parent: land_widget_layout(self->parent)

def land_widget_is_hidden(LandWidget *self) -> bool:
    return self.hidden

def land_widget_outer(LandWidget *self, float *x, *y, *w, *h):
    *x = self.box.x
    *y = self.box.y
    *w = self.box.w
    *h = self.box.h

def land_widget_inner(LandWidget *self, float *x, *y, *w, *h):
    *x = self.box.x
    *y = self.box.y
    *w = self.box.w
    *h = self.box.h
    
    if self.element:
        *x += self.element->il
        *y += self.element->it
        *w -= self.element->ir + self->element->ir
        *h -= self.element->ib + self->element->ib

def land_widget_inner_extents(LandWidget *self, float *l, *t, *r, *b):
    *l = self.box.x
    *t = self.box.y
    *r = self.box.x + self->box.w
    *b = self.box.y + self->box.h 
    
    if self.element:
        *l += self.element->il
        *t += self.element->it
        *r -= self.element->ir
        *b -= self.element->ib

def land_widget_get_inner_size(LandWidget *self, float *w, *h):
    *w = self->box.w
    *h = self->box.h 
    
    if self.element:
        *w -= self.element->il
        *h -= self.element->it
        *w -= self.element->ir
        *h -= self.element->ib

def land_widget_get_inner_center(LandWidget *self, float *x, *y):
    float l, t, r, b
    land_widget_inner_extents(self, &l, &t, &r, &b)
    *x = (l + r) / 2
    *y = (t + b) / 2

def land_widget_inner_width(LandWidget *self) -> float:
    return self->box.w - self.element->il - self.element->ir

def land_widget_inner_height(LandWidget *self) -> float:
    return self->box.h - self.element->it - self.element->ib

def land_widget_base_interface_initialize():
    if land_widget_base_interface: return

    land_alloc(land_widget_base_interface)
    land_widget_interface_register(land_widget_base_interface)
    land_widget_base_interface->id = LAND_WIDGET_ID_BASE
    land_widget_base_interface->name = land_strdup("base")
    land_widget_base_interface->size = land_widget_base_size
    land_widget_base_interface->destroy = land_widget_base_destroy

def land_widget_debug(LandWidget *w, int indentation):
    for int i in range(indentation):
        printf("  ");
    if not w:
        print("(none)")
        return
    printf("%s %d %d %d %d %s\n", land_widget_info_string(w),
        w->box.x, w->box.y, w->box.w, w->box.h, land_widget_flags_string(w))

    if land_widget_is(w, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *c = LAND_WIDGET_CONTAINER(w)
        if c.children:
            for LandWidget *child in LandList *c.children:
                land_widget_debug(child, indentation + 1)
    
def land_widget_keyboard_leave(LandWidget *self):
    land_call_method(self, keyboard_leave, (self))

def land_widget_keyboard_focus(LandWidget *self):
    land_widget_request_keyboard_focus(self)

char _blah[100]
def land_widget_flags_string(LandWidget *w) -> str:
    strcpy(_blah, "")
    if w.box.flags & GUL_SHRINK_X: strcat(_blah, " xsh")
    if w.box.flags & GUL_SHRINK_Y: strcat(_blah, " ysh")
    if w.box.flags & GUL_HIDDEN: strcat(_blah, " hid")
    if w.box.flags & GUL_NO_LAYOUT: strcat(_blah, " nol")
    if w.box.flags & GUL_STEADFAST: strcat(_blah, " stf")
    if w.got_keyboard: strcat(_blah, " K")
    if w.got_mouse: strcat(_blah, " M")
    if w.want_focus: strcat(_blah, " F!")
    return _blah
