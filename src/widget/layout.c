#ifdef _PROTOTYPE_

#include "../land.h"
#include "base.h"

#endif /* _PROTOTYPE_ */

#include "widget/layout.h"

void widget_layout_set_grid(Widget *self, int columns, int rows)
{
    self->box.rows = rows;
    self->box.cols = columns;
}

void widget_layout_set_grid_position(Widget *self, int column, int row)
{
    self->box.col = column;
    self->box.row = row;
}

void widget_layout_set_minimum_size(Widget *self, int w, int h)
{
    self->box.min_width = w;
    self->box.min_height = h;
}

void widget_layout_set_shrinking(Widget *self, int x, int y)
{
    if (x)
        self->box.flags |= GUL_SHRINK_X;
    if (y)
        self->box.flags |= GUL_SHRINK_Y;
}

void widget_layout_set_expanding(Widget *self, int x, int y)
{
    if (x)
        self->box.flags &= ~GUL_SHRINK_X;
    if (y)
        self->box.flags &= ~GUL_SHRINK_Y;
}

void widget_layout_set_border(Widget *self, int l, int t, int r, int b, int hgap, int vgap)
{
    self->box.il = l;
    self->box.it = t;
    self->box.ir = r;
    self->box.ib = b;
    self->box.hgap = hgap;
    self->box.vgap = vgap;
}

void widget_layout_add(Widget *parent, Widget *child)
{
    gul_remove_child(&parent->box, &child->box);
    gul_attach_child(&parent->box, &child->box);
}

int widget_layout(Widget *self)
{
    return gul_box_fit_children(&self->box);
}
