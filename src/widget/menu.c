#ifdef _PROTOTYPE_

#include "button.h"
#include "container.h"

typedef struct LandWidgetMenuButton LandWidgetMenuButton;
typedef struct LandWidgetMenuItem LandWidgetMenuItem;
typedef struct LandWidgetMenu LandWidgetMenu;

struct LandWidgetMenu
{
    LandWidgetContainer super;
    LandWidget *menubutton; /* MenuButton we are attached to, if any. */
    LandWidget *submenu; /* Currently displayed submenu */
};

/* A button which opens a menu when clicked. */
struct LandWidgetMenuButton
{
    LandWidgetButton super;
    LandWidget *menu; /* Menu we are part of, if any. Usually parent. */
    LandWidget *submenu; /* submenu to show */
    unsigned int below : 1; /* If yes, open menu below, else to the right. */
};

/* A button inside a menu. */
struct LandWidgetMenuItem
{
    LandWidgetButton super;
    void (*callback)(LandWidget *self);
    LandWidget *menu; /* Menu we are part of, if any. Usually parent. */
};

#endif /* _PROTOTYPE_ */

#include "widget/theme.h"
#include "widget/menu.h"

LandWidgetInterface *land_widget_menu_interface;
LandWidgetInterface *land_widget_menubutton_interface;
LandWidgetInterface *land_widget_menubar_interface;
LandWidgetInterface *land_widget_menuitem_interface;

#define LAND_WIDGET_MENU(widget) ((LandWidgetMenu *) \
    land_widget_check(widget, LAND_WIDGET_ID_MENU, __FILE__, __LINE__))

#define LAND_WIDGET_MENUBUTTON(widget) ((LandWidgetMenuButton *) \
    land_widget_check(widget, LAND_WIDGET_ID_MENUBUTTON, __FILE__, __LINE__))

#define LAND_WIDGET_MENUITEM(widget) ((LandWidgetMenuItem *) \
    land_widget_check(widget, LAND_WIDGET_ID_MENUITEM, __FILE__, __LINE__))

LandWidget *land_widget_menubar_new(LandWidget *parent, float x, float y,
    float w, float h)
{
    LandWidget *base = land_widget_menu_new(parent, x, y, w, h);
    base->vt = land_widget_menubar_interface;
    land_widget_theme_layout_border(base);
    return base;
}

LandWidget *land_widget_menu_new(LandWidget *parent, float x, float y,
    float w, float h)
{
    land_widget_menu_interface_initialize();
    LandWidgetMenu *self;
    land_alloc(self);
    LandWidget *base = (LandWidget *)self;
    land_widget_container_initialize(base, parent, x, y, w, h);
    base->vt = land_widget_menu_interface;
    land_widget_theme_layout_border(base);
    return base;
}

/* Hide the given menu and all its sub-menus. */
void land_widget_menu_hide_sub(LandWidget *base)
{
    LandWidgetMenu *menu = LAND_WIDGET_MENU(base);
    if (menu->submenu)
    {
        land_widget_menu_hide_sub(menu->submenu);
        menu->submenu = NULL;
        //TODO: reference counts
    }
    land_widget_hide(base);
}

/* Hide the complete menu the given one is part of. */
void land_widget_menu_hide_complete(LandWidget *base)
{
    /* Find topmost menu or menubar. */
    while (1)
    {
        LandWidgetMenu *menu = LAND_WIDGET_MENU(base);
        if (!menu->menubutton)
            break;
        LandWidgetMenuButton *button = LAND_WIDGET_MENUBUTTON(menu->menubutton);
        if (button->menu)
        {
            base = button->menu;
        }
        else
            break;
    }

    if ((base->vt->id & LAND_WIDGET_ID_MENUBAR) == LAND_WIDGET_ID_MENUBAR)
    {
        LandWidgetMenu *menu = LAND_WIDGET_MENU(base);
        base = menu->submenu;
        if (!base) return;
        menu->submenu = NULL;
        // TODO: reference count
    }

    land_widget_menu_hide_sub(base);
}

static void menubutton_clicked(LandWidget *base)
{
    LandWidgetMenuButton *self = LAND_WIDGET_MENUBUTTON(base);
    if (self->below)
    {
        land_widget_move(self->submenu,
            base->box.x - self->submenu->box.x,
            base->box.y + base->box.h - self->submenu->box.y);
    }
    else
    {
        land_widget_move(self->submenu,
            base->box.x + base->box.w - self->submenu->box.x,
            base->box.y - self->submenu->box.y);
    }
    if (self->menu &&
        (self->menu->vt->id & LAND_WIDGET_ID_MENU) == LAND_WIDGET_ID_MENU)
    {
        LandWidgetMenu *menu = LAND_WIDGET_MENU(self->menu);
        if (menu->submenu)
            land_widget_menu_hide_sub(menu->submenu);
        menu->submenu = self->submenu;
        // TODO: reference counts
    }
    self->submenu->send_to_top = 1;
    land_widget_unhide(self->submenu);
}

static void menuitem_clicked(LandWidget *base)
{
    LandWidgetMenuItem *self = LAND_WIDGET_MENUITEM(base);

    if (self->menu &&
        (self->menu->vt->id & LAND_WIDGET_ID_MENU) == LAND_WIDGET_ID_MENU)
    {
        land_widget_menu_hide_complete(self->menu);
    }
    if (self->callback) self->callback(LAND_WIDGET(self));
}

LandWidget *land_widget_menubutton_new(LandWidget *parent, char const *name,
    LandWidget *submenu, float x, float y, float w, float h)
{
    land_widget_menubutton_interface_initialize();
    LandWidgetMenuButton *self;
    land_alloc(self);
    land_widget_reference(submenu);
    self->submenu = submenu;
    self->menu = parent;
    if ((parent->vt->id & LAND_WIDGET_ID_MENUBAR) == LAND_WIDGET_ID_MENUBAR)
        self->below = 1;
    land_widget_button_initialize((LandWidget *)self, parent, name, NULL,
        menubutton_clicked, x, y, w, h);
    LAND_WIDGET(self)->vt = land_widget_menubutton_interface;
    return LAND_WIDGET(self);
}

void land_widget_menubutton_destroy(LandWidget *self)
{
    LandWidgetMenuButton *menubutton = LAND_WIDGET_MENUBUTTON(self);
    if (menubutton->submenu)
        land_widget_unreference(menubutton->submenu);
    land_widget_button_destroy(self);
}

void land_widget_menu_add(LandWidget *base, LandWidget *item)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base);
    land_widget_container_add(base, item);
    int n = container->children->count;
    
    land_widget_layout_inhibit(base);

    land_widget_layout_set_grid(base, 1, n);
    land_widget_layout_set_grid_position(item, 0, n - 1);
    land_widget_layout_set_shrinking(item, 1, 1);
    land_widget_layout_add(base, item);
    
    land_widget_layout_enable(base);
    // FIXME: since the add method is called from the constructor, the layout
    // is not ready yet, e.g. min-size is not calculated yet
    //land_widget_layout_adjust(base, 1, 1, 1);
}

void land_widget_menubar_add(LandWidget *base, LandWidget *item)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(base);
    land_widget_container_add(base, item);
    int n = container->children->count;
    
    land_widget_layout_inhibit(base);

    land_widget_layout_set_grid(base, n, 1);
    land_widget_layout_set_grid_position(item, n - 1, 0);
    land_widget_layout_set_shrinking(item, 1, 1);
    land_widget_layout_add(base, item);
    
    land_widget_layout_enable(base);
    // FIXME: since the add method is called from the constructor, the layout
    // is not ready yet, e.g. min-size is not calculated yet
    //land_widget_layout_adjust(base, 1, 1, 1);
}

LandWidget *land_widget_menuitem_new(LandWidget *parent, char const *name,
    void (*callback)(LandWidget *widget))
{
    int tw = land_text_get_width(name);
    int th = land_font_height(land_font_current());
    LandWidgetMenuItem *menuitem;
    land_alloc(menuitem);
       
    land_widget_menubutton_interface_initialize();
    menuitem->menu = parent;
    menuitem->callback = callback;
    land_widget_button_initialize((LandWidget *)menuitem, parent, name, NULL,
        menuitem_clicked, 0, 0, 10, 10);

    LandWidget *self = LAND_WIDGET(menuitem);
    self->vt = land_widget_menuitem_interface;

    land_widget_theme_layout_border(self);
    land_widget_layout_set_minimum_size(self,
        self->box.il + self->box.ir + tw,
        self->box.it + self->box.ib + th);
        
    // FIXME: this is wrong, since we could be added to anything, or even
    // have no parent - but see the FIXME above in land_widget_menu_add
    land_widget_layout_adjust(parent, 1, 1);

    return self;
}

LandWidget *land_widget_submenuitem_new(LandWidget *parent, char const *name,
    LandWidget *submenu)
{
    int tw = land_text_get_width(name);
    int th = land_font_height(land_font_current());
    LandWidget *button = land_widget_menubutton_new(parent, name, submenu,
        0, 0, 0, 0);
    LAND_WIDGET_MENU(submenu)->menubutton = button;
    land_widget_theme_layout_border(button);
    land_widget_layout_set_minimum_size(button,
        button->box.il + button->box.ir + tw,
        button->box.it + button->box.ib + th);

    // FIXME: this is wrong, since we could be added to anything, or even
    // have no parent - but see the FIXME above in land_widget_menu_add
    land_widget_layout_adjust(parent, 1, 1);
    return button;
}

LandWidget *land_widget_menu_spacer_new(LandWidget *parent)
{
    LandWidget *button = land_widget_box_new(parent, 0, 0, 0, 0);
    land_widget_theme_layout_border(button);

    // FIXME: this is wrong, since we could be added to anything, or even
    // have no parent - but see the FIXME above in land_widget_menu_add
    land_widget_layout_adjust(parent, 1, 1);
    return button;
}


void land_widget_menu_mouse_enter(LandWidget *self, LandWidget *focus)
{
}

void land_widget_menu_mouse_leave(LandWidget *self, LandWidget *focus)
{
    // FIXME: check that this is indeed part of the same menu?
    if (focus && (focus->vt->id & LAND_WIDGET_ID_MENU) == LAND_WIDGET_ID_MENU)
    {
        return;
    }
    if (self->hidden) return;
    land_widget_retain_mouse_focus(self);
}


void land_widget_menubutton_mouse_enter(LandWidget *self, LandWidget *focus)
{
    /* Auto-open menus */
    // TODO: maybe make this a theme option, and a configurable delay
    menubutton_clicked(self);
}

void land_widget_menubutton_mouse_leave(LandWidget *self, LandWidget *focus)
{

}

void land_widget_menubar_mouse_leave(LandWidget *self, LandWidget *focus)
{
    // FIXME: check that this is indeed part of the same menu?
    if (focus && (focus->vt->id & LAND_WIDGET_ID_MENU) == LAND_WIDGET_ID_MENU)
    {
        return;
    }
    if (!LAND_WIDGET_MENU(self)->submenu)
        return;
    land_widget_retain_mouse_focus(self);
}

void land_widget_menu_mouse_tick(LandWidget *self)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self);

    land_widget_container_mouse_tick(self);

    if (!container->mouse && land_mouse_delta_b() && land_mouse_b())
    {
        /* outside click */
        land_widget_menu_hide_complete(self);
        return;
    }
}

void land_widget_menu_interface_initialize(void)
{
    if (land_widget_menu_interface) return;

    land_widget_container_interface_initialize();

    land_widget_menu_interface = land_widget_copy_interface(
        land_widget_container_interface, "menu");
    land_widget_menu_interface->id |= LAND_WIDGET_ID_MENU;
    land_widget_menu_interface->add = land_widget_menu_add;
    land_widget_menu_interface->mouse_enter = land_widget_menu_mouse_enter;
    land_widget_menu_interface->mouse_leave = land_widget_menu_mouse_leave;
    land_widget_menu_interface->mouse_tick = land_widget_menu_mouse_tick;
    
    land_widget_menubar_interface = land_widget_copy_interface(
        land_widget_menu_interface, "menubar");
    land_widget_menubar_interface->id |= LAND_WIDGET_ID_MENUBAR;
    land_widget_menubar_interface->add = land_widget_menubar_add;
    land_widget_menubar_interface->mouse_leave = land_widget_menubar_mouse_leave;
}

void land_widget_menubutton_interface_initialize(void)
{
    if (land_widget_menubutton_interface) return;

    land_widget_button_interface_initialize();

    land_widget_menubutton_interface = land_widget_copy_interface(
        land_widget_button_interface, "menubutton");
    land_widget_menubutton_interface->id |= LAND_WIDGET_ID_MENUBUTTON;
    land_widget_menubutton_interface->mouse_enter = land_widget_menubutton_mouse_enter;
    land_widget_menubutton_interface->mouse_leave = land_widget_menubutton_mouse_leave;
    land_widget_menubutton_interface->destroy = land_widget_menubutton_destroy;
    
    land_widget_menuitem_interface = land_widget_copy_interface(
        land_widget_button_interface, "menuitem");
    land_widget_menuitem_interface->id |= LAND_WIDGET_ID_MENUITEM;
}
