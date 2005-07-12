#ifdef _PROTOTYPE_

typedef struct Widget Widget;
typedef struct WidgetInterface WidgetInterface;

#include "widget/gul.h"

struct WidgetInterface
{
    char const *name;

    void (*init)(Widget *self);
    void (*enter)(Widget *self);
    void (*tick)(Widget *self);

    void (*mouse_enter)(Widget *self);
    void (*mouse_tick)(Widget *self);
    void (*mouse_leave)(Widget *self);

    void (*keyboard_enter)(Widget *self);
    void (*keyboard_tick)(Widget *self);
    void (*keyboard_leave)(Widget *self);

    void (*add)(Widget *self, Widget *add);
    void (*move)(Widget *self, float dx, float dy);
    void (*size)(Widget *self, float dx, float dy);

    void (*draw)(Widget *self);
    void (*leave)(Widget *self);
    void (*destroy)(Widget *self);
};

struct Widget
{
    WidgetInterface *vt;
    Widget *parent;
    GUL_BOX box;
    int got_mouse;
    int send_to_top;
    int dont_clip;
    void *properties;

   struct WidgetTheme *theme;
};

#define WIDGET(self) ((Widget *)self)

#endif /* _PROTOTYPE_ */

#include "widget/base.h"
#include "widget/layout.h"

WidgetInterface *widget_base_interface = NULL;

// FIXME: Themeing
int theme_scrollbar_broadness = 16;
int theme_scrollbar_minimum_length = 8;

void widget_base_initialize(Widget *self, Widget *parent, int x, int y, int w, int h)
{
    if (!widget_base_interface)
        widget_base_interface_initialize();
    gul_box_initialize(&self->box);
    self->box.x = x;
    self->box.y = y;
    self->box.w = w;
    self->box.h = h;
    if (parent)
    {
        self->theme = parent->theme;
        land_call_method(parent, add, (parent, self));
    }
}

Widget *widget_new(Widget *parent, int x, int y, int w, int h)
{
    Widget *self;
    land_alloc(self);
    widget_base_initialize(self, parent, x, y, w, h);
    return self;
}

void widget_base_del(Widget *self)
{
    free(self);
}

void widget_del(Widget *self)
{
    if (self->vt->destroy)
        self->vt->destroy(self);
    else
        widget_base_del(self);
}

void widget_base_mouse_enter(Widget *self)
{
    self->got_mouse = 1;
}

void widget_base_mouse_leave(Widget *self)
{
    self->got_mouse = 0;
}

void widget_base_move(Widget *self, float dx, float dy)
{
    self->box.x += dx;
    self->box.y += dy;
}

void widget_move(Widget *self, float dx, float dy)
{
    if (self->vt->move)
        self->vt->move(self, dx, dy);
    else
    {
        widget_base_move(self, dx, dy);
    }
}

void widget_base_size(Widget *self, float dx, float dy)
{
    self->box.w += dx;
    self->box.h += dy;
    if (widget_layout(self))
    {
        if (self->box.w < self->box.min_width)
            self->box.w = self->box.min_width;
        if (self->box.h < self->box.min_height)
            self->box.h = self->box.min_height;
        widget_layout(self);
    }
}

void widget_size(Widget *self, float dx, float dy)
{
    if (self->vt->size)
        self->vt->size(self, dx, dy);
    else
    {
        widget_base_size(self, dx, dy);
    }
}

void widget_tick(Widget *self)
{
    land_call_method(self, tick, (self));
}

void widget_draw(Widget *self)
{
    int pop = 0;
    if (!self->dont_clip)
    {
        land_clip_push();
        land_clip_on();
        land_clip_intersect(self->box.x, self->box.y, self->box.x + self->box.w,
            self->box.y + self->box.h);
        pop = 1;
    }
    land_call_method(self, draw, (self));
    if (pop)
    {
        land_clip_pop();
    }
}

void widget_base_interface_initialize(void)
{
    land_alloc(widget_base_interface);
    widget_base_interface->name = "name";
}
