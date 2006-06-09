#ifdef _PROTOTYPE_

typedef struct LandWidgetBook LandWidgetBook;

struct LandWidgetBook
{
    LandWidgetContainer super;
    LandList *pages;
};

#define LAND_WIDGET_BOOK(widget) ((LandWidgetBook *) \
    land_widget_check(widget, LAND_WIDGET_ID_BOOK, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"
#include "widget/book.h"
#include "widget/hbox.h"

LandWidgetInterface *land_widget_book_interface;

void land_widget_book_initialize(LandWidget *base,
    LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetBook *self = (LandWidgetBook *)base;
    land_alloc(self);

    land_widget_container_initialize(base, parent, x, y, w, h);

    /* Tabs bar. */
    LandWidget *tabbar = land_widget_hbox_new(base, 0, 0, 10, 10);

    /* The panel with the active page. */
    LandWidget *page = land_widget_panel_new(base, 0, 0, 10, 10);
    
    /* The layout. */
    land_widget_layout_set_grid(base, 1, 2);
    land_widget_layout_set_grid_position(tabbar, 0, 0);
    land_widget_layout_set_grid_position(page, 0, 1);
    land_widget_layout_add(base, tabbar);
    land_widget_layout_add(base, page);
    land_widget_layout_set_shrinking(tabbar, 0, 1);

    /* From now on, adding a subwindow will create a tab. */
    land_widget_book_interface_initialize();
    base->vt = land_widget_book_interface;
}

static void clicked(LandWidget *button)
{
    /* We need to hide the currently visible ab, and show the one corresponding
     * to the clicked button.
     */
    LandWidgetContainer *hbox = LAND_WIDGET_CONTAINER(button->parent);
    LandWidgetContainer *book = LAND_WIDGET_CONTAINER(button->parent->parent);
    LandWidgetContainer *panel = LAND_WIDGET_CONTAINER(book->children->first->next->data);
    
    LandListItem *panelitem = panel->children->first;

    /* Hide all panels first. */
    while(panelitem)
    {
        land_widget_hide(panelitem->data);
        panelitem = panelitem->next;
    }

    LandListItem *item = hbox->children->first;
    panelitem = panel->children->first;
    /* Then unhide the active one. */
    while(item)
    {
        if (item->data == button)
        {
            land_widget_unhide(panelitem->data);
            break;
        }
        item = item->next;
        panelitem = panelitem->next;
    }
    land_widget_layout(LAND_WIDGET(book));
}

void land_widget_book_add(LandWidget *widget, LandWidget *add)
{
    /* A new item is added to the book, we'll create a new tab button for it,
     * and add it to our container.
     */

    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget);
    LandWidgetHBox *hbox = LAND_WIDGET_HBOX(container->children->first->data);
    LandWidget *panel = LAND_WIDGET(container->children->first->next->data);

    LandWidget *tab = land_widget_button_new(LAND_WIDGET(hbox),
        "new tab", clicked, 0, 0, 10, 10);

    land_widget_container_add(panel, add);
    land_widget_hide(add); /* Newly added widget is not visible. */

    /* Each page is handled by the layout, so it should always auto-size to the
     * page panel.
     */
    land_widget_layout_set_grid(panel, 1, 1);
    land_widget_layout_set_grid_position(add, 0, 0);
    land_widget_layout_add(panel, add);
}

void land_widget_book_pagename(LandWidget *widget, char const *name)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget);
    LandWidgetContainer *hbox = LAND_WIDGET_CONTAINER(container->children->first->data);
    LandWidget *button = hbox->children->last->data;
    land_widget_button_set_text(button, name);
}

LandWidget *land_widget_book_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetBook *self;
    land_alloc(self);
    land_widget_book_initialize((LandWidget *)self, parent, x, y, w, h);
    return LAND_WIDGET(self);
}

void land_widget_book_interface_initialize(void)
{
    if (land_widget_book_interface) return;
    land_widget_container_interface_initialize();
    land_widget_book_interface = land_widget_copy_interface(
        land_widget_container_interface, "book");
    land_widget_book_interface->id |= LAND_WIDGET_ID_BOOK;
    land_widget_book_interface->add = land_widget_book_add;
}
