import button, container

class LandWidgetMenu:
    LandWidgetContainer super
    LandWidget *menubutton # MenuButton we are attached to, if any. 
    LandWidget *submenu # Currently displayed submenu 

# A button which opens a menu when clicked. 
class LandWidgetMenuButton:
    LandWidgetButton super
    LandWidget *menu # Menu we are part of, if any. Usually parent. 
    LandWidget *submenu # submenu to show 
    bool below # If yes, open menu below, else to the right. 

# A button inside a menu. 
class LandWidgetMenuItem:
    LandWidgetButton super
    void (*callback)(LandWidget *self)
    LandWidget *menu; # Menu we are part of, if any. Usually parent. 

static import theme, menu

static LandWidgetInterface *land_widget_menu_interface
static LandWidgetInterface *land_widget_menubutton_interface
static LandWidgetInterface *land_widget_menubar_interface
static LandWidgetInterface *land_widget_menuitem_interface

macro LAND_WIDGET_MENU(widget) ((LandWidgetMenu *) land_widget_check(widget, LAND_WIDGET_ID_MENU, __FILE__, __LINE__))
macro LAND_WIDGET_MENUBUTTON(widget) ((LandWidgetMenuButton *) land_widget_check(widget, LAND_WIDGET_ID_MENUBUTTON, __FILE__, __LINE__))
macro LAND_WIDGET_MENUITEM(widget) ((LandWidgetMenuItem *) land_widget_check(widget, LAND_WIDGET_ID_MENUITEM, __FILE__, __LINE__))

LandWidget *def land_widget_menubar_new(LandWidget *parent, float x, float y,
    float w, float h):
    """
    Create a new menubar. That is, a menu which is layout horizontally instead
    of vertically. By default, a menubar will expand horizontally, and shrink
    vertically.
    """
    LandWidget *base = land_widget_menu_new(parent, x, y, w, h)
    base->vt = land_widget_menubar_interface
    land_widget_theme_initialize(base)
    land_widget_layout_set_shrinking(base, 1, 1)
    return base

LandWidget *def land_widget_menu_new(LandWidget *parent, float x, float y,
    float w, float h):
    """
    Create a new menu, with menu items layout out vertically.
    """
    land_widget_menu_interface_initialize()
    LandWidgetMenu *self
    land_alloc(self)
    LandWidget *base = (LandWidget *)self
    land_widget_container_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_menu_interface
    land_widget_layout_enable(base)
    land_widget_theme_initialize(base)
    return base

def land_widget_menu_hide_sub(LandWidget *base):
    """
    Hide the given menu and all its sub-menus.
    """
    LandWidgetMenu *menu = LAND_WIDGET_MENU(base)
    if menu->submenu:
        land_widget_menu_hide_sub(menu->submenu)
        menu->submenu = NULL
        # TODO: reference counts

    land_widget_hide(base)

def land_widget_menu_hide_complete(LandWidget *base):
    """
    Hide the complete menu the given one is part of. 
    """
    # Find topmost menu or menubar. 
    while 1:
        LandWidgetMenu *menu = LAND_WIDGET_MENU(base)
        if not menu->menubutton:
            break
        LandWidgetMenuButton *button = LAND_WIDGET_MENUBUTTON(menu->menubutton)
        if button->menu:
            base = button->menu

        else:
            break

    if ((base->vt->id & LAND_WIDGET_ID_MENUBAR) == LAND_WIDGET_ID_MENUBAR):
        LandWidgetMenu *menu = LAND_WIDGET_MENU(base)
        base = menu->submenu
        if not base: return
        menu->submenu = NULL
        # TODO: reference count

    land_widget_menu_hide_sub(base)

static def menubutton_clicked(LandWidget *base):
    LandWidgetMenuButton *self = LAND_WIDGET_MENUBUTTON(base)
    if self->below:
        land_widget_move(self->submenu,
            base->box.x - self->submenu->box.x,
            base->box.y + base->box.h - self->submenu->box.y)

    else:
        land_widget_move(self->submenu,
            base->box.x + base->box.w - self->submenu->box.x,
            base->box.y - self->submenu->box.y)

    if (self->menu and
        (self->menu->vt->id & LAND_WIDGET_ID_MENU) == LAND_WIDGET_ID_MENU):
        LandWidgetMenu *menu = LAND_WIDGET_MENU(self->menu)
        if menu->submenu:
            land_widget_menu_hide_sub(menu->submenu)
        menu->submenu = self->submenu
        # TODO: reference counts

    self->submenu->send_to_top = 1
    land_widget_unhide(self->submenu)

    # in case menu items were added/removed while it was hidden (which
    # inhibits all layout updates)
    land_widget_layout(self->submenu)

static def menuitem_clicked(LandWidget *base):
    LandWidgetMenuItem *self = LAND_WIDGET_MENUITEM(base)

    if self->menu and land_widget_is(self->menu, LAND_WIDGET_ID_MENU):
        land_widget_menu_hide_complete(self->menu)

    if self->callback: self->callback(LAND_WIDGET(self))

LandWidget *def land_widget_menubutton_new(LandWidget *parent, char const *name,
    LandWidget *submenu, float x, float y, float w, float h):
    """
    Create a submenu, i.e. a button in a menu to open another menu when clicked.
    """
    land_widget_menubutton_interface_initialize()
    LandWidgetMenuButton *self
    land_alloc(self)
    land_widget_reference(submenu)
    self->submenu = submenu
    self->menu = parent
    if ((parent->vt->id & LAND_WIDGET_ID_MENUBAR) == LAND_WIDGET_ID_MENUBAR):
        self->below = 1
    LandWidget *base = (void *)self
    land_widget_button_initialize(base, parent, name, NULL,
        menubutton_clicked, x, y, w, h)
    LAND_WIDGET_MENU(submenu)->menubutton = base
    base->vt = land_widget_menubutton_interface
    land_widget_theme_initialize(base)
    return base

def land_widget_menubutton_destroy(LandWidget *self):
    LandWidgetMenuButton *menubutton = LAND_WIDGET_MENUBUTTON(self)
    if menubutton->submenu:
        land_widget_unreference(menubutton->submenu)
    land_widget_button_destroy(self)

def land_widget_menu_add(LandWidget *base, LandWidget *item):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    land_widget_container_add(base, item)
    int n = container->children->count

    land_widget_layout_freeze(base)

    land_widget_layout_set_grid(base, 1, n)
    land_widget_layout_set_grid_position(item, 0, n - 1)
    land_widget_layout_set_shrinking(item, 1, 1)

    land_widget_layout_unfreeze(base)
    # FIXME: since the add method is called from the constructor, the layout
    # is not ready yet, e.g. min-size is not calculated yet
    # land_widget_layout_adjust(base, 1, 1, 1)

def land_widget_menubar_add(LandWidget *base, LandWidget *item):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base)
    land_widget_container_add(base, item)
    int n = container->children->count
    
    land_widget_layout_freeze(base)

    land_widget_layout_set_grid(base, n, 1)
    land_widget_layout_set_grid_position(item, n - 1, 0)
    land_widget_layout_set_shrinking(item, 1, 1)

    land_widget_layout_unfreeze(base)
    # FIXME: since the add method is called from the constructor, the layout
    # is not ready yet, e.g. min-size is not calculated yet
    # land_widget_layout_adjust(base, 1, 1, 1)

LandWidget *def land_widget_menuitem_new(LandWidget *parent, char const *name,
    void (*callback)(LandWidget *widget)):
    """
    Create a new menu item, i.e. en entry which can be clicked to execute the
    given callback.
    """
    int tw = land_text_get_width(name)
    int th = land_font_height(land_font_current())
    LandWidgetMenuItem *menuitem
    land_alloc(menuitem)
       
    land_widget_menubutton_interface_initialize()
    menuitem->menu = parent
    menuitem->callback = callback

    land_widget_button_initialize((LandWidget *)menuitem, parent, name,
        None, menuitem_clicked, 0, 0, 10, 10)

    LandWidget *self = LAND_WIDGET(menuitem)
    self->vt = land_widget_menuitem_interface

    land_widget_theme_initialize(self)
    land_widget_layout_set_minimum_size(self,
        self->element->il + self->element->ir + tw,
        self->element->it + self->element->ib + th)
        
    # FIXME: this is wrong, since we could be added to anything, or even
    # have no parent - but see the FIXME above in land_widget_menu_add
    land_widget_layout(parent)

    return self

LandWidget *def land_widget_submenuitem_new(LandWidget *parent,
    char const *name, LandWidget *submenu):
    int tw = land_text_get_width(name)
    int th = land_font_height(land_font_current())
    LandWidget *button = land_widget_menubutton_new(parent, name, submenu,
        0, 0, 0, 0)
    LAND_WIDGET_MENU(submenu)->menubutton = button
    land_widget_theme_initialize(button)
    land_widget_layout_set_minimum_size(button,
        button->element->il + button->element->ir + tw,
        button->element->it + button->element->ib + th)

    # FIXME: this is wrong, since we could be added to anything, or even
    # have no parent - but see the FIXME above in land_widget_menu_add
    land_widget_layout(parent)
    return button

LandWidget *def land_widget_menu_spacer_new(LandWidget *parent):
    LandWidget *button = land_widget_box_new(parent, 0, 0, 0, 0)
    land_widget_theme_initialize(button)

    # FIXME: this is wrong, since we could be added to anything, or even
    # have no parent - but see the FIXME above in land_widget_menu_add
    land_widget_layout(parent)
    return button

LandWidget *def land_widget_menu_find(LandWidget *super, int n,
    char const *names[]):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(super)
    LandList *l = container->children
    if l:
        LandListItem *listitem = l->first
        while listitem:
            if land_widget_is(listitem->data, LAND_WIDGET_ID_BUTTON):
                LandWidgetButton *button = listitem->data
                if not strcmp(button->text, names[0]):
                    if n <= 1: return (void *)button
                    if land_widget_is(listitem->data, LAND_WIDGET_ID_MENUBUTTON):
                        LandWidgetMenuButton *mb = listitem->data
                        return land_widget_menu_find(mb->submenu, n - 1, names + 1)
            listitem = listitem->next
    
    return None

def land_widget_menu_mouse_enter(LandWidget *self):
    pass

static int def is_in_menu(LandWidget *self, LandWidget *other):
    """
    Check if the given menu has other as an ancestor.
    """
    while self:
        if self == other: return 1
        LandWidgetMenu *menu = LAND_WIDGET_MENU(self)
        LandWidget *buttonwidget = menu->menubutton
        if not buttonwidget: break
        LandWidgetMenuButton *button = LAND_WIDGET_MENUBUTTON(buttonwidget)
        self = button->menu
    return 0

static int def is_related(LandWidget *self, LandWidget *other):
    """
    Check if other is a menu item or menu button related to this menu.
    """
    if land_widget_is(other, LAND_WIDGET_ID_MENUITEM):
        LandWidgetMenuItem *othermenuitem = LAND_WIDGET_MENUITEM(other)
        LandWidget *othermenuwidget = othermenuitem->menu
        while othermenuwidget:
            if is_in_menu(self, othermenuwidget): return 1
            LandWidgetMenu *othermenu = LAND_WIDGET_MENU(othermenuwidget)
            LandWidget *otherbuttonwidget = othermenu->menubutton
            if not otherbuttonwidget: break
            LandWidgetMenuButton *othermenubutton = LAND_WIDGET_MENUBUTTON(
                otherbuttonwidget)
            othermenuwidget = othermenubutton->menu
    elif land_widget_is(other, LAND_WIDGET_ID_MENUBUTTON):
        while other:
            LandWidgetMenuButton *otherbutton = LAND_WIDGET_MENUBUTTON(other)
            LandWidget *othermenuwidget = otherbutton->menu
            if not othermenuwidget: break
            if is_in_menu(self, othermenuwidget): return 1
            LandWidgetMenu *othermenu = LAND_WIDGET_MENU(othermenuwidget)
            other = othermenu->menubutton

    return 0

def land_widget_menu_mouse_leave(LandWidget *self):
    if self->hidden: return

    # If the mouse is over another menu, then switch to that.
    # TODO: Maybe add some configurable delay before switching.
    LandWidget *up = self
    while up->parent:
        up = up->parent

    LandWidget *target = land_widget_container_get_descendant_at_pos(up,
        land_mouse_x(), land_mouse_y())

    if is_related(self, target):
        return

    land_widget_retain_mouse_focus(self)

def land_widget_menubutton_mouse_enter(LandWidget *self):
    # Auto-open menus 
    # TODO: maybe make this a theme option, and a configurable delay
    menubutton_clicked(self)

def land_widget_menubutton_mouse_leave(LandWidget *self):
    pass

def land_widget_menubar_mouse_leave(LandWidget *self):
    # FIXME: check that this is indeed part of the same menu?

    # if not LAND_WIDGET_MENU(self)->submenu:
    #    return
    # land_widget_retain_mouse_focus(self)
    
    return

def land_widget_menu_mouse_tick(LandWidget *self):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)

    land_widget_container_mouse_tick(self)

    if (not container->mouse and land_mouse_delta_b() and land_mouse_b()):
        # outside click 
        land_widget_menu_hide_complete(self)
        return

def land_widget_menu_interface_initialize():
    if land_widget_menu_interface: return

    land_widget_container_interface_initialize()

    land_widget_menu_interface = land_widget_copy_interface(
        land_widget_container_interface, "menu")
    land_widget_menu_interface->id |= LAND_WIDGET_ID_MENU
    land_widget_menu_interface->add = land_widget_menu_add
    land_widget_menu_interface->mouse_enter = land_widget_menu_mouse_enter
    land_widget_menu_interface->mouse_leave = land_widget_menu_mouse_leave
    land_widget_menu_interface->mouse_tick = land_widget_menu_mouse_tick
    
    land_widget_menubar_interface = land_widget_copy_interface(
        land_widget_menu_interface, "menubar")
    land_widget_menubar_interface->id |= LAND_WIDGET_ID_MENUBAR
    land_widget_menubar_interface->add = land_widget_menubar_add
    land_widget_menubar_interface->mouse_leave = land_widget_menubar_mouse_leave

def land_widget_menubutton_interface_initialize():
    if land_widget_menubutton_interface: return

    land_widget_button_interface_initialize()

    land_widget_menubutton_interface = land_widget_copy_interface(
        land_widget_button_interface, "menubutton")
    land_widget_menubutton_interface->id |= LAND_WIDGET_ID_MENUBUTTON
    land_widget_menubutton_interface->mouse_enter = land_widget_menubutton_mouse_enter
    land_widget_menubutton_interface->mouse_leave = land_widget_menubutton_mouse_leave
    land_widget_menubutton_interface->destroy = land_widget_menubutton_destroy
    
    land_widget_menuitem_interface = land_widget_copy_interface(
        land_widget_button_interface, "menuitem")
    land_widget_menuitem_interface->id |= LAND_WIDGET_ID_MENUITEM
