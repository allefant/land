#ifdef _PROTOTYPE_

typedef struct LandWidgetContainer LandWidgetContainer;

#include "base.h"

#include "../list.h"

struct LandWidgetContainer
{
    LandWidget super;
    LandList *children;
    LandWidget *mouse;
    LandWidget *keyboard;
};

extern LandWidgetInterface *land_widget_container_interface;

#define LAND_WIDGET_CONTAINER(widget) ((LandWidgetContainer *) \
    land_widget_check(widget, LAND_WIDGET_ID_CONTAINER, __FILE__, __LINE__))

#endif /* _PROTOTYPE_ */

#include "land.h"

LandWidgetInterface *land_widget_container_interface = NULL;

/* Destroy the container and all its children. */
void land_widget_container_destroy(LandWidget *base)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base);
    LandListItem *item = self->children->first;
    while (item)
    {
        LandListItem *next = item->next;
        LandWidget *child = item->data;
        /* Detach it. It won't get destroyed if there are still outside
         * references to it.
         */
        child->parent = NULL;
        land_widget_unreference(item->data);
        item = next;
    }
    land_list_destroy(self->children);
    land_widget_base_destroy(base);
}

void land_widget_container_mouse_enter(LandWidget *self)
{
    self->got_mouse = 1;
}

void land_widget_container_mouse_leave(LandWidget *super)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);
    if (self->mouse)
        land_call_method(self->mouse, mouse_leave, (self->mouse));
    super->got_mouse = 0;
    self->mouse = NULL;
}

LandListItem *land_widget_container_child_item(LandWidget *super, LandWidget *child)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);
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

void land_widget_container_to_top(LandWidget *super, LandWidget *child)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);
    LandListItem *item = land_widget_container_child_item(super, child);
    land_list_remove_item(self->children, item);
    land_list_insert_item(self->children, item);
}

void land_widget_container_draw(LandWidget *base)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(base);
    land_widget_theme_draw(base);
    if (!self->children)
        return;
        
    //land_color(0, 0, 0, 1);
    //land_text_pos(base->box.x, base->box.y);

    if (!base->dont_clip)
    {
        int l = base->box.x + base->box.il;
        int t = base->box.y + base->box.it;
        int r = base->box.x + base->box.w - base->box.ir;
        int b = base->box.y + base->box.h - base->box.ib;
        
        //land_print("%s %d %d %d %d", base->vt->name, l, t, r, b);
        land_clip_push();
        land_clip_intersect(l, t, r, b);
    }

    LandListItem *item = self->children->first;
    while (item)
    {
        LandWidget *child = item->data;
        land_widget_draw(child);
        item = item->next;
    }

    if (!base->dont_clip)
    {
        land_clip_pop();
    }
}

void land_widget_container_move(LandWidget *super, float dx, float dy)
{
    super->box.x += dx;
    super->box.y += dy;
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);
    if (!self->children)
        return;
    LandListItem *item = self->children->first;
    while (item)
    {
        LandWidget *child = item->data;
        land_widget_move(child, dx, dy);
        item = item->next;
    }
}

LandWidget *land_widget_container_get_at_pos(LandWidget *super, int x, int y)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);
    if (!self->children)
        return NULL;
    LandListItem *item = self->children->last;
    while (item)
    {
        LandWidget *child = item->data;
        if (x >= child->box.x && y >= child->box.y &&
            x < child->box.x + child->box.w && y < child->box.y + child->box.h)
            return child;
        item = item->prev;
    }
    return NULL;
}

void land_widget_container_mouse_tick(LandWidget *super)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);
    if (self->mouse)
        land_call_method(self->mouse, mouse_tick, (self->mouse));
    LandWidget *mouse = land_widget_container_get_at_pos(super, land_mouse_x(),
        land_mouse_y());
    if (mouse != self->mouse && !(land_mouse_b() & 1))
    {
        if (mouse)
            land_widget_reference(mouse);
        if (self->mouse)
        {
            land_call_method(self->mouse, mouse_leave, (self->mouse));
            land_widget_unreference(self->mouse);
        }
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
            LandWidget *child = item->data;
            if (child->send_to_top)
            {
                land_widget_container_to_top(super, child);
                child->send_to_top = 0;
                f = 1;
            }
            if (item == last)
                break;
            item = next;
        }
    }
}

void land_widget_container_tick(LandWidget *super)
{
    land_widget_container_mouse_tick(super);
}

void land_widget_container_add(LandWidget *super, LandWidget *add)
{
    LandWidgetContainer *self = LAND_WIDGET_CONTAINER(super);

    /* We increase the reference count of the child only. Increasing the
     * parent's reference (even though there is the ->parent pointer), would
     * cause a cyclic dependancy! We still never get a dangling pointer, since
     * the parent cannot be destroyed without first detaching its children.
     */
    land_add_list_data(&self->children, add);
    land_widget_reference(add);

    add->parent = super;
}

void land_widget_container_remove(LandWidget *base, LandWidget *rem)
{
    // TODO: assert here that parent points to base, of not.. we're fucked
    rem->parent = NULL;
    land_remove_list_data(&LAND_WIDGET_CONTAINER(base)->children, rem);
    land_widget_unreference(rem);
}

void land_widget_container_initialize(LandWidgetContainer *self, LandWidget *parent, int x, int y, int w, int h)
{
   land_widget_container_interface_initialize();

   LandWidget *super = &self->super;
   land_widget_base_initialize(super, parent, x, y, w, h);
   super->vt = land_widget_container_interface;
   self->children = NULL;
}

LandWidget *land_widget_container_new(LandWidget *parent, int x, int y, int w, int h)
{
    LandWidgetContainer *self;
    land_alloc(self);
    land_widget_container_initialize(self, parent, x, y, w, h);
    return &self->super;
}

void land_widget_container_interface_initialize(void)
{
    if (land_widget_container_interface) return;

    land_alloc(land_widget_container_interface);
    land_widget_container_interface->id = LAND_WIDGET_ID_BASE |
        LAND_WIDGET_ID_CONTAINER;
    land_widget_container_interface->name = "container";
    land_widget_container_interface->destroy = land_widget_container_destroy;
    land_widget_container_interface->draw = land_widget_container_draw;
    land_widget_container_interface->tick = land_widget_container_tick;
    land_widget_container_interface->add = land_widget_container_add;
    land_widget_container_interface->move = land_widget_container_move;
    land_widget_container_interface->mouse_tick = land_widget_container_mouse_tick;
    land_widget_container_interface->mouse_enter = land_widget_container_mouse_enter;
    land_widget_container_interface->mouse_leave = land_widget_container_mouse_leave;
}

