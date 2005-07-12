#ifdef _PROTOTYPE_

typedef struct WidgetContainer WidgetContainer;

#include "widget/base.h"

#include "array.h"

struct WidgetContainer
{
    Widget super;
    LandList *children;
    Widget *mouse;
    Widget *keyboard;
};

#define WIDGET_CONTAINER(widget) ((WidgetContainer *)widget)

#endif /* _PROTOTYPE_ */

#include "land.h"

WidgetInterface *widget_container_interface = NULL;

void widget_container_mouse_enter(Widget *self)
{
    self->got_mouse = 1;
}

void widget_container_mouse_leave(Widget *super)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    if (self->mouse)
        land_call_method(self->mouse, mouse_leave, (self->mouse));
    super->got_mouse = 0;
    self->mouse = NULL;
}

LandListItem *widget_container_child_item(Widget *super, Widget *child)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    if (!self->children)
        return NULL;
    LandListItem *item = self->children->first;
    while (item)
    {
        if (item->data == child)
            return item;
        item = item->next;
    }
    return NULL;
}

void widget_container_to_top(Widget *super, Widget *child)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    LandListItem *item = widget_container_child_item(super, child);
    land_list_remove_item(self->children, item);
    land_list_insert_item(self->children, item);
}

void widget_container_draw(Widget *base)
{
    WidgetContainer *self = WIDGET_CONTAINER(base);
    widget_theme_draw(base);
    if (!self->children)
        return;

    land_clip_intersect(base->box.x + base->box.il, base->box.y + base->box.it,
        base->box.x + base->box.w - base->box.ir, base->box.y + base->box.h - base->box.ib);

    LandListItem *item = self->children->first;
    while (item)
    {
        Widget *child = item->data;
        widget_draw(child);
        item = item->next;
    }
}

void widget_container_move(Widget *super, float dx, float dy)
{
    super->box.x += dx;
    super->box.y += dy;
    WidgetContainer *self = WIDGET_CONTAINER(super);
    if (!self->children)
        return;
    LandListItem *item = self->children->first;
    while (item)
    {
        Widget *child = item->data;
        widget_move(child, dx, dy);
        item = item->next;
    }
}

Widget *widget_container_get_at_pos(Widget *super, int x, int y)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    if (!self->children)
        return NULL;
    LandListItem *item = self->children->last;
    while (item)
    {
        Widget *child = item->data;
        if (x >= child->box.x && y >= child->box.y &&
            x < child->box.x + child->box.w && y < child->box.y + child->box.h)
            return child;
        item = item->prev;
    }
    return NULL;
}

void widget_container_mouse_tick(Widget *super)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    if (self->mouse)
        land_call_method(self->mouse, mouse_tick, (self->mouse));
    Widget *mouse = widget_container_get_at_pos(super, land_mouse_x(),
        land_mouse_y());
    if (mouse != self->mouse && !(land_mouse_b() & 1))
    {
        if (self->mouse)
            land_call_method(self->mouse, mouse_leave, (self->mouse));
        self->mouse = mouse;
        if (self->mouse)
            land_call_method(self->mouse, mouse_enter, (self->mouse));
    }

    int f = 0;
    if (self->children)
    {
        LandListItem *item, *next, *last;
        item = self->children->first;
        last = self->children->last;
        while (item)
        {
            next = item->next;
            Widget *child = item->data;
            if (child->send_to_top)
            {
                widget_container_to_top(super, child);
                child->send_to_top = 0;
                f = 1;
            }
            if (item == last)
                break;
            item = next;
        }
    }
}

void widget_container_tick(Widget *super)
{

}

void widget_container_add(Widget *super, Widget *add)
{
    WidgetContainer *self = WIDGET_CONTAINER(super);
    land_add_list_data(&self->children, add);
    add->parent = super;
}

void widget_container_initialize(WidgetContainer *self, Widget *parent, int x, int y, int w, int h)
{
   if (!widget_container_interface)
        widget_container_interface_initialize();
   Widget *super = &self->super;
   widget_base_initialize(super, parent, x, y, w, h);
   super->vt = widget_container_interface;
   self->children = NULL;
}

Widget *widget_container_new(Widget *parent, int x, int y, int w, int h)
{
    WidgetContainer *self;
    land_alloc(self);
    widget_container_initialize(self, parent, x, y, w, h);
    return &self->super;
}

void widget_container_interface_initialize(void)
{
    land_alloc(widget_container_interface);
    widget_container_interface->name = "container";
    widget_container_interface->draw = widget_container_draw;
    widget_container_interface->tick = widget_container_tick;
    widget_container_interface->add = widget_container_add;
    widget_container_interface->move = widget_container_move;
    widget_container_interface->mouse_tick = widget_container_mouse_tick;
    widget_container_interface->mouse_enter = widget_container_mouse_enter;
    widget_container_interface->mouse_leave = widget_container_mouse_leave;
}

