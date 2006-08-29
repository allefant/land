import container, ../list

class LandWidgetBook:
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

    LandWidgetBook *self = (LandWidgetBook *)base
    land_alloc(self)

    land_widget_container_initialize(base, parent, x, y, w, h)

    # The panel with the active page. This is the first child so it gets
    # drawn first and we can draw the tabs overlapping a bit.
    
    LandWidget *page = land_widget_panel_new(base, 0, 0, 10, 10)
    land_widget_theme_layout_border(page)

    # Tab bar.
    LandWidget *tabbar = land_widget_hbox_new(base, 0, 0, 10, 10)
    tabbar->dont_clip = 1
    tabbar->vt = land_widget_tabbar_interface
    land_widget_theme_layout_border(tabbar)

    # The layout.
    land_widget_layout_set_grid(base, 1, 2)
    land_widget_layout_set_grid_position(tabbar, 0, 0)
    land_widget_layout_set_grid_position(page, 0, 1)
    land_widget_layout_add(base, tabbar); /* Here, the tabbar is first. */
    land_widget_layout_add(base, page)
    land_widget_layout_set_shrinking(tabbar, 0, 1)

    # From now on, adding a subwindow will create a tab.
    base->vt = land_widget_book_interface

def land_widget_book_show_page(LandWidget *self, LandWidget *page):
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
    # A new item is added to the book, we'll create a new tab button for it,
    # and add it to our container.

    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandWidgetHBox *hbox = LAND_WIDGET_HBOX(
        container->children->first->next->data)
    LandWidget *panel = LAND_WIDGET(container->children->first->data)

    LandWidget *tab = land_widget_button_new(LAND_WIDGET(hbox),
        "", clicked, 0, 0, 10, 10)
    tab->vt = land_widget_tab_interface
    land_widget_theme_layout_border(tab)

    land_widget_container_add(panel, add)
    land_widget_hide(add); /* Newly added widget is not visible. */

    # Each page is handled by the layout, so it should always auto-size to the
    # page panel.

    land_widget_layout_set_grid(panel, 1, 1)
    land_widget_layout_set_grid_position(add, 0, 0)
    land_widget_layout_add(panel, add)

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

# Return the current active page or NULL
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

    return NULL

# Return the last active page or NULL.
LandWidget *def land_widget_book_get_last_page(LandWidget *self):
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(self)
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(
        book->children->first->data)

    LandListItem *panelitem = panel->children->last
    if panelitem:
        return LAND_WIDGET(panelitem->data)
    return NULL

# Return the given page, starting with 0 for the first page. If there is no
# such page, NULL is returned.
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

    return NULL
