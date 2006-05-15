#ifdef _PROTOTYPE_

#include "../land.h"

#include "container.h"

typedef struct LandWidgetScrollbar LandWidgetScrollbar;

struct LandWidgetScrollbar
{
    LandWidget super;
    LandWidget *target;
    int dragged;
    int drag_x, drag_y;
    int vertical;
    void (*callback)(LandWidget *self, int set, int *min, int *max, int *range, int *pos);
};

#define LAND_WIDGET_SCROLLBAR(widget) ((LandWidgetScrollbar *)widget)

#endif /* _PROTOTYPE_ */

#include "widget/scrollbar.h"
#include "widget/box.h"

LandWidgetInterface *land_widget_scrollbar_vertical_interface = NULL;
LandWidgetInterface *land_widget_scrollbar_horizontal_interface = NULL;

static void scroll_vertical_cb(LandWidget *self, int set, int *min, int *max, int *range, int *pos)
{
    LandWidgetScrollbar *bar = LAND_WIDGET_SCROLLBAR(self);
    LandWidget *target = bar->target;
    if (target)
    {
        LandWidget *viewport = target->parent;
        if (set)
        {
                int ty = viewport->box.y + viewport->box.it - *pos;
                land_widget_move(target, 0, ty - target->box.y);
        }
        else
        {
            *min = 0;
            *max = target->box.h - 1;
            *range = viewport->box.h - viewport->box.it - viewport->box.ib;
            *pos = viewport->box.y + viewport->box.it - target->box.y;
            if (*pos + *range - 1 > *max)
                *max = *pos + *range - 1;
        }
    }
}

static void scroll_horizontal_cb(LandWidget *self, int set, int *min, int *max, int *range, int *pos)
{
    LandWidgetScrollbar *bar = LAND_WIDGET_SCROLLBAR(self);
    LandWidget *target = bar->target;
    if (target)
    {
        LandWidget *viewport = target->parent;
        if (set)
        {
                int tx = viewport->box.x + viewport->box.il - *pos;
                land_widget_move(target, tx - target->box.x, 0);
        }
        else
        {
            *min = 0;
            *max = target->box.w - 1;
            *range = viewport->box.w - viewport->box.il - viewport->box.ir;
            *pos = viewport->box.x + viewport->box.il - target->box.x;
        }
    }
}

void land_widget_scrollbar_update(LandWidget *super, int set)
{
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(super);
    int minval, maxval, val, valrange;
    int minpos, maxpos, pos, posrange;

    self->callback(super, 0, &minval, &maxval, &valrange, &val);

    if (self->vertical)
    {
        minpos = super->parent->box.y + super->parent->box.it;
        maxpos = super->parent->box.y + super->parent->box.h - super->parent->box.ib - 1;
        pos = super->box.y;
        posrange = super->box.h;
    }
    else
    {
        minpos = super->parent->box.x + super->parent->box.il;
        maxpos = super->parent->box.x + super->parent->box.w - super->parent->box.ir - 1;
        pos = super->box.x;
        posrange = super->box.w;
    }

    if (set)
    {
        maxpos -= posrange - 1;
        maxval -= valrange - 1;

        if (maxpos == minpos)
            val = minval;
        else
        {
            /* Always round up when setting, since we round down when querying. */
            int round = maxpos - 1 - minpos;
            val = (minval + (pos - minpos) * (maxval - minval) + round) / (maxpos - minpos);
        }

        self->callback(super, 1, &minval, &maxval, &valrange, &val);
    }
    else
    {
        posrange = (1 + maxpos - minpos) * valrange / (1 + maxval - minval);
        if (posrange < 10) /* TODO: use layout minimum */
            posrange = 10;
        maxpos -= posrange - 1;
        maxval -= valrange - 1;
        if (maxval == minval)
            pos = minpos;
        else
            pos = minpos + (val - minval) * (maxpos - minpos) / (maxval - minval);
        if (self->vertical)
        {
            super->box.h = posrange;
            super->box.y = pos;
        }
        else
        {
            super->box.w = posrange;
            super->box.x = pos;
        }
    }
}

void land_widget_scrollbar_draw(LandWidget *self)
{
    land_widget_scrollbar_update(self, 0);
    land_widget_theme_draw(self);
}

void land_widget_scrollbar_mouse_tick(LandWidget *super)
{
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(super);
    if (land_mouse_delta_b())
    {
        if (land_mouse_b() & 1)
        {
            self->drag_x = land_mouse_x() - super->box.x;
            self->drag_y = land_mouse_y() - super->box.y;
            self->dragged = 1;
        }
        else
            self->dragged = 0;
    }

    if ((land_mouse_b() & 1) && self->dragged)
    {
        int newx = land_mouse_x() - self->drag_x;
        int newy = land_mouse_y() - self->drag_y;
        int l = super->parent->box.x + super->parent->box.il;
        int t = super->parent->box.y + super->parent->box.it;
        int r = super->parent->box.x + super->parent->box.w - super->box.w - super->parent->box.ir;
        int b = super->parent->box.y + super->parent->box.h - super->box.h - super->parent->box.ib;
        if (newx > r)
            newx = r;
        if (newy > b)
            newy = b;
        if (newx < l)
            newx = l;
        if (newy < t)
            newy = t;
        land_widget_move(super, newx - super->box.x, newy - super->box.y);
        land_widget_scrollbar_update(super, 1);
    }
}

LandWidget *land_widget_scrollbar_new(LandWidget *parent, LandWidget *target, int vertical, int x, int y, int w, int h)
{
    LandWidgetScrollbar *self;
    
    land_widget_scrollbar_interface_initialize();

    land_alloc(self);
    LandWidget *super = &self->super;
    land_widget_base_initialize(super, parent, x, y, w, h);

    self->target = target;
    self->vertical = vertical;
    if (vertical)
    {
        self->callback = scroll_vertical_cb;
        super->vt = land_widget_scrollbar_vertical_interface;
    }
    else
    {
        self->callback = scroll_horizontal_cb;
        super->vt = land_widget_scrollbar_horizontal_interface;
    }
    return super;
}

void land_widget_scrollbar_interface_initialize(void)
{
    if (!land_widget_scrollbar_vertical_interface)
    {
        LandWidgetInterface *i;
        land_alloc(i);
        i->name = "scrollbar.vertical";
        i->draw = land_widget_scrollbar_draw;
        i->move = land_widget_base_move;
        i->mouse_tick = land_widget_scrollbar_mouse_tick;
        land_widget_scrollbar_vertical_interface = i;
    }
    
    if (!land_widget_scrollbar_horizontal_interface)
    {
        LandWidgetInterface *i;
        land_alloc(i);
        i->name = "scrollbar.horizontal";
        i->draw = land_widget_scrollbar_draw;
        i->move = land_widget_base_move;
        i->mouse_tick = land_widget_scrollbar_mouse_tick;
        land_widget_scrollbar_horizontal_interface = i;
    }
}

