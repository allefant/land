import container, ../list

class LandWidgetBook:
    """
    A book widget is a container, which shows only one of its children at a
    time. The visible one can be selected with tabs (usually at the top).
    """
    LandWidgetContainer super
    LandList *pages

macro LAND_WIDGET_BOOK(widget) ((LandWidgetBook *) land_widget_check(widget,
    LAND_WIDGET_ID_BOOK, __FILE__, __LINE__))

static import land, widget/hbox

LandWidgetInterface *land_widget_book_interface
LandWidgetInterface *land_widget_tab_interface
LandWidgetInterface *land_widget_tabbar_interface

def land_widget_book_initialize(LandWidget *base,
    LandWidget *parent, int x, int y, int w, int h):
    land_widget_book_interface_initialize()

    land_widget_container_initialize(base, parent, x, y, w, h)
    land_widget_layout_enable(base)

    # The panel with the active page. This is the first child so it gets
    # drawn first and we can draw the tabs overlapping a bit.
    
    LandWidget *page = land_widget_panel_new(base, 0, 0, 10, 10)

    # Tab bar.
    LandWidget *tabbar = land_widget_hbox_new(base, 0, 0, 10, 10)
    tabbar->dont_clip = 1
    tabbar->vt = land_widget_tabbar_interface
    land_widget_theme_initialize(tabbar)

    # The layout.
    land_widget_layout_set_grid(base, 1, 2)
    land_widget_layout_set_grid_position(tabbar, 0, 0)
    land_widget_layout_set_grid_position(page, 0, 1)
    land_widget_layout_set_shrinking(tabbar, 0, 1)

    # From now on, adding a subwindow will create a tab.
    base->vt = land_widget_book_interface
    
    land_widget_theme_initialize(base)

def land_widget_book_show_page(LandWidget *self, LandWidget *page):
    """
    Change the visible page of the notebook. If ''page'' is None or not a
    children of the notebook, then an empty tab will be shown.
    """
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(self)
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(
        book->children->first->data)
    LandWidgetContainer *tabbar = LAND_WIDGET_CONTAINER(
        book->children->first->next->data)

    LandListItem *panelitem = panel->children->first
    LandListItem *tabitem = tabbar->children->first

    # Hide all panels first.
    while panelitem:
        land_widget_hide(panelitem->data)
        LAND_WIDGET(tabitem->data)->selected = 0
        panelitem = panelitem->next
        tabitem = tabitem->next

    panelitem = panel->children->first
    tabitem = tabbar->children->first
    # Then unhide the active one.
    while panelitem:
        if panelitem->data == page:
            land_widget_unhide(panelitem->data)
            LAND_WIDGET(tabitem->data)->selected = 1
            break

        panelitem = panelitem->next
        tabitem = tabitem->next

    land_widget_layout(LAND_WIDGET(book))

static def clicked(LandWidget *button):
    # The page corresponding to the button is the one with the same index. This
    # should probably be changed by having a direct link to the page. for now,
    # we will have to loop.
    
    LandWidgetContainer *hbox = LAND_WIDGET_CONTAINER(button->parent)
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(button->parent->parent)
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(
        book->children->first->data)

    LandListItem *panelitem = panel->children->first
    LandListItem *item = hbox->children->first
    while item:
        if item->data == button:
            land_widget_book_show_page(button->parent->parent, panelitem->data)
            break

        item = item->next
        panelitem = panelitem->next


def land_widget_book_add(LandWidget *widget, LandWidget *add):
    """
    Add a new item to the notebook. This will not make it visible yet, use
    ["land_widget_book_show_page"] for that.
    """

    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandWidgetHBox *hbox = LAND_WIDGET_HBOX(
        container->children->first->next->data)
    LandWidget *panel = LAND_WIDGET(container->children->first->data)

    LandWidget *tab = land_widget_button_new(LAND_WIDGET(hbox),
        "", clicked, 0, 0, 10, 10)
    tab->vt = land_widget_tab_interface
    land_widget_theme_initialize(tab)

    land_widget_container_add(panel, add)
    land_widget_hide(add) # Newly added widget is not visible.

    # Each page is handled by the layout, so it should always auto-size to the
    # page panel.

    land_widget_layout_set_grid(panel, 1, 1)
    land_widget_layout_set_grid_position(add, 0, 0)

def land_widget_book_pagename(LandWidget *widget, char const *name):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandWidgetContainer *hbox = LAND_WIDGET_CONTAINER(
        container->children->first->next->data)
    LandWidget *button = hbox->children->last->data
    land_widget_button_set_text(button, name)

LandWidget *def land_widget_book_new(LandWidget *parent, int x, y, w, h):
    LandWidgetBook *self
    land_alloc(self)
    land_widget_book_initialize((LandWidget *)self, parent, x, y, w, h)
    return LAND_WIDGET(self)

def land_widget_book_interface_initialize(void):
    if (land_widget_book_interface) return
    land_widget_container_interface_initialize()
    land_widget_book_interface = land_widget_copy_interface(
        land_widget_container_interface, "book")
    land_widget_book_interface->id |= LAND_WIDGET_ID_BOOK
    land_widget_book_interface->add = land_widget_book_add
    
    land_widget_button_interface_initialize()
    land_widget_tab_interface = land_widget_copy_interface(
        land_widget_button_interface, "tab")
    land_widget_tab_interface->id |= LAND_WIDGET_ID_TAB
    
    land_widget_hbox_interface_initialize()
    land_widget_tabbar_interface = land_widget_copy_interface(
        land_widget_hbox_interface, "tabbar")
    land_widget_tabbar_interface->id |= LAND_WIDGET_ID_TABBAR

# Return the current active page or None
LandWidget *def land_widget_book_get_current_page(LandWidget *self):
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(self)
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(
        book->children->first->data)

    LandListItem *panelitem = panel->children->first

    # Find first non hidden page.
    while panelitem:
        LandWidget *page = LAND_WIDGET(panelitem->data)
        if not page->hidden:
            return page

        panelitem = panelitem->next

    return None

# Return the last active page or None.
LandWidget *def land_widget_book_get_last_page(LandWidget *self):
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(self)
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(
        book->children->first->data)

    LandListItem *panelitem = panel->children->last
    if panelitem:
        return LAND_WIDGET(panelitem->data)
    return None

# Return the given page, starting with 0 for the first page. If there is no
# such page, None is returned.
LandWidget *def land_widget_book_get_nth_page(LandWidget *self, int n):
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(self)
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(
        book->children->first->data)

    LandListItem *panelitem = panel->children->first

    int i = 0
    while panelitem:
        LandWidget *page = LAND_WIDGET(panelitem->data)
        if i == n:
            return page

        panelitem = panelitem->next
        i++

    return None

def land_widget_book_show_nth(LandWidget *self, int n):
    LandWidget *page = land_widget_book_get_nth_page(self, n)
    if page: land_widget_book_show_page(self, page)