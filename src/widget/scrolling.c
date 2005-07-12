#ifdef _PROTOTYPE_

typedef struct WidgetScrolling WidgetScrolling;

#include "widget/container.h"

struct WidgetScrolling
{
    WidgetContainer super;
};

/* This has 3 fixed children:
 * 1. The contents window, a container.
 * 2. A vertical scrollbar to the right.
 * 3. A horizontal scrollbar at the bottom.
 */

#define WIDGET_SCROLLING(widget) ((WidgetScrolling *)widget)

#endif /* _PROTOTYPE_ */

#include "widget/scrolling.h"
#include "widget/box.h"
#include "widget/scrollbar.h"

WidgetInterface *widget_scrolling_interface = NULL;

void widget_scrolling_mouse_enter(Widget *self)
{
    self->got_mouse = 1;
}

void widget_scrolling_mouse_leave(Widget *super)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    if (self->mouse)
        land_call_method(self->mouse, mouse_leave, (self->mouse));
    super->got_mouse = 0;
    self->mouse = NULL;
}

void widget_scrolling_move(Widget *widget, float dx, float dy)
{
    widget_container_move(widget, dx, dy);
}

Widget *widget_scrolling_get_at_pos(Widget *super, int x, int y)
{
    return widget_container_get_at_pos(super, x, y);
}

void widget_scrolling_mouse_tick(Widget *super)
{
    widget_container_mouse_tick(super);
}

void widget_scrolling_tick(Widget *super)
{

}

void widget_scrolling_add(Widget *widget, Widget *add)
{
    WidgetContainer *container = WIDGET_CONTAINER(widget);
    LandListItem *item = container->children->first;
    Widget *contents = WIDGET(item->data);
    widget_container_add(contents, add);

    item = item->next;
    WidgetContainer *right = WIDGET_CONTAINER(item->data);
    LandListItem *item2 = right->children->first;
    WidgetScrollbar *rightbar = WIDGET_SCROLLBAR(item2->data);
    rightbar->target = add;

    item = item->next;
    WidgetContainer *bottom = WIDGET_CONTAINER(item->data);
    item2 = bottom->children->first;
    WidgetScrollbar *bottombar = WIDGET_SCROLLBAR(item2->data);
    bottombar->target = add;
}

Widget *widget_scrolling_new(Widget *parent, int x, int y, int w, int h)
{
    WidgetScrolling *self;
    if (!widget_scrolling_interface)
        widget_scrolling_interface_initialize();
    land_alloc(self);
    WidgetContainer *super = &self->super;
    widget_container_initialize(super, parent, x, y, w, h);
    Widget *widget = &super->super;

    /* Add own widgets without special hook. */
    widget->vt = widget_container_interface;

    /* child 1: container */
    Widget *contents = widget_container_new(widget, 0, 0, 0, 0);
    widget_layout_set_border(contents, 2, 2, 2, 2, 1, 1);

    /* child 2: vertical scrollbar */
    Widget *right = widget_container_new(widget, 0, 0, 0, 0);
    Widget *rightbar = widget_scrollbar_new(right, NULL, 1, 0, 0, 0, 0);

    widget_layout_set_grid(right, 1, 1);
    widget_layout_set_grid_position(rightbar, 0, 0);
    widget_layout_add(right, rightbar);

    /* child 3: horizontal scrollbar */
    Widget *bottom = widget_container_new(widget, 0, 0, 0, 0);
    Widget *bottombar = widget_scrollbar_new(bottom, NULL, 0, 0, 0, 0, 0);

    widget_layout_set_grid(bottom, 1, 1);
    widget_layout_set_grid_position(bottombar, 0, 0);
    widget_layout_add(bottom, bottombar);

    widget_layout_set_grid(widget, 2, 2);
    widget_layout_set_border(widget, 2, 2, 2, 2, 1, 1);
    widget_layout_add(widget, contents);
    widget_layout_add(widget, right);
    widget_layout_add(widget, bottom);

    widget_layout_set_grid_position(contents, 0, 0);

    /* Vertical scrollbar layout. */
    widget_layout_set_grid_position(right, 1, 0);
    widget_layout_set_border(right, 2, 2, 2, 2, 1, 1);
    widget_layout_set_minimum_size(right, theme_scrollbar_broadness, theme_scrollbar_minimum_length);
    widget_layout_set_shrinking(right, 1, 0);

    /* Horizontal scrollbar layout. */
    widget_layout_set_grid_position(bottom, 0, 1);
    widget_layout_set_border(bottom, 2, 2, 2, 2, 1, 1);
    widget_layout_set_minimum_size(bottom, theme_scrollbar_minimum_length, theme_scrollbar_broadness);
    widget_layout_set_shrinking(bottom, 0, 1);

    /* FIXME: The layout lib allows no empty cells yet, so need to put an empty box. */
    Widget *empty = widget_box_new(widget, 0, 0, 0, 0);
    widget_layout_add(widget, empty);
    widget_layout_set_grid_position(empty, 1, 1);
    widget_layout_set_shrinking(empty, 1, 1);

    widget_layout(widget);

    /* From now on, special vtable is used. */
    widget->vt = widget_scrolling_interface;

    return widget;
}

void widget_scrolling_interface_initialize(void)
{
    land_alloc(widget_scrolling_interface);
    widget_scrolling_interface->name = "scrolling";
    widget_scrolling_interface->draw = widget_container_draw;
    widget_scrolling_interface->tick = widget_scrolling_tick;
    widget_scrolling_interface->add = widget_scrolling_add;
    widget_scrolling_interface->move = widget_scrolling_move;
    widget_scrolling_interface->mouse_tick = widget_scrolling_mouse_tick;
    widget_scrolling_interface->mouse_enter = widget_scrolling_mouse_enter;
    widget_scrolling_interface->mouse_leave = widget_scrolling_mouse_leave;
}

