#ifdef _PROTOTYPE_

typedef struct LandWidgetScrolling LandWidgetScrolling;

#include "container.h"

struct LandWidgetScrolling
{
    LandWidgetContainer super;
};

/* This has 3 fixed children:
 * 1. The contents window, a container.
 * 2. A vertical scrollbar to the right.
 * 3. A horizontal scrollbar at the bottom.
 */

#define LAND_WIDGET_SCROLLING(widget) ((LandWidgetScrolling *) \
    land_widget_check(widget, LAND_WIDGET_ID_SCROLLING, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "widget/scrolling.h"
#include "widget/box.h"
#include "widget/scrollbar.h"

LandWidgetInterface *land_widget_scrolling_interface;
LandWidgetInterface *land_widget_scrolling_contents_container_interface;
LandWidgetInterface *land_widget_scrolling_vertical_container_interface;
LandWidgetInterface *land_widget_scrolling_horizontal_container_interface;

void land_widget_scrolling_move(LandWidget *widget, float dx, float dy)
{
    land_widget_container_move(widget, dx, dy);
}

void land_widget_scrolling_size(LandWidget *widget)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget);
    LandListItem *item = container->children->first;

    item = item->next;
    LandWidgetContainer *right = LAND_WIDGET_CONTAINER(item->data);
    LandListItem *item2 = right->children->first;
    LandWidgetScrollbar *rightbar = LAND_WIDGET_SCROLLBAR(item2->data);
    land_widget_scrollbar_update(LAND_WIDGET(rightbar), 0);

    item = item->next;
    LandWidgetContainer *bottom = LAND_WIDGET_CONTAINER(item->data);
    item2 = bottom->children->first;
    LandWidgetScrollbar *bottombar = LAND_WIDGET_SCROLLBAR(item2->data);
    land_widget_scrollbar_update(LAND_WIDGET(bottombar), 0);
}

void land_widget_scrolling_scrollto(LandWidget *base, float x, float y)
{
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data;
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children;
    if (!children) return;
    LandWidget *child =  children->first->data;

    child->box.x = contents->box.x + contents->box.il + x;
    child->box.y = contents->box.y + contents->box.it + y;

    land_widget_scrolling_size(base);
}

LandWidget *land_widget_scrolling_get_at_pos(LandWidget *base, int x, int y)
{
    return land_widget_container_get_at_pos(base, x, y);
}

void land_widget_scrolling_mouse_tick(LandWidget *base)
{
    if (land_mouse_delta_z())
    {
        LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data;
        LandList *children = LAND_WIDGET_CONTAINER(contents)->children;
        if (!children) return;
        LandWidget *child = children->first->data;
        int maxy = contents->box.y + contents->box.it;
        int miny = contents->box.y + contents->box.h -
            contents->box.ib - child->box.h;
        int target_y = child->box.y + land_mouse_delta_z() * 64;
        if (target_y < miny) target_y = miny;
        if (target_y > maxy) target_y = maxy;
        land_widget_move(child, 0, target_y - child->box.y);
    }
    land_widget_container_mouse_tick(base);
}

void land_widget_scrolling_tick(LandWidget *super)
{
    
}

void land_widget_scrolling_add(LandWidget *widget, LandWidget *add)
{
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget);
    LandListItem *item = container->children->first;
    LandWidget *contents = LAND_WIDGET(item->data);
    land_widget_container_add(contents, add);

    /* A freshly added widget start always at the no-scroll position. */
    add->box.x = contents->box.x + contents->box.il;
    add->box.y = contents->box.y + contents->box.it;

    /* There is no need to add extra references to the added widget from the
     * scrollbars. They live and die with the whole scrolling widget anyway,
     * so if the added widget is to be destroyed, then it has to be detached
     * first from contents, which can *only* happen over
     * land_widget_scrolling_destroy_child.
     */

    item = item->next;
    LandWidgetContainer *right = LAND_WIDGET_CONTAINER(item->data);
    LandListItem *item2 = right->children->first;
    LandWidgetScrollbar *rightbar = LAND_WIDGET_SCROLLBAR(item2->data);
    rightbar->target = add;

    item = item->next;
    LandWidgetContainer *bottom = LAND_WIDGET_CONTAINER(item->data);
    item2 = bottom->children->first;
    LandWidgetScrollbar *bottombar = LAND_WIDGET_SCROLLBAR(item2->data);
    bottombar->target = add;
}

/* Return the child window of the scrolling window. Usually, a scrolling
 * window has exactly one child window, which is controlled by the scrollbars.
 * This window is returned.
 */
LandWidget *land_widget_scrolling_get_child(LandWidget *base)
{
    LandWidget *contents = LAND_WIDGET_CONTAINER(base)->children->first->data;
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children;
    return children ? children->first->data : NULL;
}

void land_widget_scrolling_remove_child(LandWidget *base)
{
    LandList *list = LAND_WIDGET_CONTAINER(base)->children;
    LandWidget *contents = list->first->data;
    LandList *children = LAND_WIDGET_CONTAINER(contents)->children;
    LandWidget *child = children ? children->first->data : NULL;
    if (child)
        land_widget_container_remove(contents, child);

    /* Detach scrollbars. */
    LandWidgetContainer * c;
    c = LAND_WIDGET_CONTAINER(list->first->next->data);
    LAND_WIDGET_SCROLLBAR(c->children->first->data)->target = NULL;
    c = LAND_WIDGET_CONTAINER(list->first->next->next->data);
    LAND_WIDGET_SCROLLBAR(c->children->first->data)->target = NULL;
    
}

/* Creates a new Scrolling widget. You can add a child widget to it, and it
 * will automatically display scrollbars and translate mouse coordinates.
 */
LandWidget *land_widget_scrolling_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetScrolling *self;
    
    land_widget_scrolling_interface_initialize();

    land_alloc(self);
    LandWidgetContainer *super = &self->super;
    LandWidget *widget = &super->super;
    land_widget_container_initialize(widget, parent, x, y, w, h);

    /* Add own widgets without special hook. */
    widget->vt = land_widget_container_interface;

    /* child 1: container */
    LandWidget *contents = land_widget_container_new(widget, 0, 0, 0, 0);
    contents->only_border = 1;
    contents->vt = land_widget_scrolling_contents_container_interface;
    land_widget_theme_layout_border(contents);

    /* child 2: vertical scrollbar */
    LandWidget *right = land_widget_container_new(widget, 0, 0, 0, 0);
    right->vt = land_widget_scrolling_vertical_container_interface;
    land_widget_theme_set_minimum_size(right);
    LandWidget *rightbar = land_widget_scrollbar_new(right, NULL, 1, 0, 0, 0, 0);
    land_widget_theme_set_minimum_size(rightbar);
    
    land_widget_layout_set_grid(right, 1, 1);
    land_widget_layout_set_grid_position(rightbar, 0, 0);
    land_widget_layout_add(right, rightbar);

    /* child 3: horizontal scrollbar */
    LandWidget *bottom = land_widget_container_new(widget, 0, 0, 0, 0);
    bottom->vt = land_widget_scrolling_horizontal_container_interface;
    land_widget_theme_set_minimum_size(bottom);
    LandWidget *bottombar = land_widget_scrollbar_new(bottom, NULL, 0, 0, 0, 0, 0);
    land_widget_theme_set_minimum_size(bottombar);

    land_widget_layout_set_grid(bottom, 1, 1);
    land_widget_layout_set_grid_position(bottombar, 0, 0);
    land_widget_layout_add(bottom, bottombar);

    /* overall layout */
    land_widget_layout_set_grid(widget, 2, 2);
    land_widget_theme_layout_border(widget);
    land_widget_layout_add(widget, contents);
    land_widget_layout_add(widget, right);
    land_widget_layout_add(widget, bottom);

    land_widget_layout_set_grid_position(contents, 0, 0);

    /* Vertical scrollbar layout. */
    land_widget_layout_set_grid_position(right, 1, 0);
    land_widget_theme_layout_border(right);
    land_widget_layout_set_shrinking(right, 1, 0);

    /* Horizontal scrollbar layout. */
    land_widget_layout_set_grid_position(bottom, 0, 1);
    land_widget_theme_layout_border(bottom);
    land_widget_layout_set_shrinking(bottom, 0, 1);

    /* FIXME: The layout lib allows no empty cells yet, so need to put an empty box. */
    LandWidget *empty = land_widget_box_new(widget, 0, 0, 0, 0);
    land_widget_layout_add(widget, empty);
    land_widget_layout_set_grid_position(empty, 1, 1);
    land_widget_layout_set_shrinking(empty, 1, 1);

    /* From now on, special vtable is used. */
    widget->vt = land_widget_scrolling_interface;
    
    land_widget_layout(widget);

    return widget;
}

void land_widget_scrolling_interface_initialize(void)
{
    if (land_widget_scrolling_interface) return;

    land_widget_container_interface_initialize();

    land_widget_scrolling_interface = land_widget_copy_interface(
        land_widget_container_interface, "scrolling");
    land_widget_scrolling_interface->id |= LAND_WIDGET_ID_SCROLLING;
    land_widget_scrolling_interface->tick = land_widget_scrolling_tick;
    land_widget_scrolling_interface->add = land_widget_scrolling_add;
    land_widget_scrolling_interface->move = land_widget_scrolling_move;
    land_widget_scrolling_interface->size = land_widget_scrolling_size;
    land_widget_scrolling_interface->mouse_tick = land_widget_scrolling_mouse_tick;

    land_widget_scrolling_contents_container_interface =
        land_widget_copy_interface(land_widget_container_interface,
        "scrolling.contents.container");
    land_widget_scrolling_vertical_container_interface =
        land_widget_copy_interface(land_widget_container_interface,
        "scrolling.vertical.container");
    land_widget_scrolling_horizontal_container_interface =
        land_widget_copy_interface(land_widget_container_interface,
        "scrolling.horizontal.container");
}

