#ifdef _PROTOTYPE_

#include "../land.h"
#include "base.h"

#endif /* _PROTOTYPE_ */

#include "widget/layout.h"

void land_widget_layout_set_grid(LandWidget *self, int columns, int rows)
{
    self->box.rows = rows;
    self->box.cols = columns;
}

void land_widget_layout_set_grid_position(LandWidget *self, int column, int row)
{
    self->box.col = column;
    self->box.row = row;
}

void land_widget_layout_set_minimum_size(LandWidget *self, int w, int h)
{
    self->box.min_width = w;
    self->box.min_height = h;
}

void land_widget_layout_set_shrinking(LandWidget *self, int x, int y)
{
    if (x)
        self->box.flags |= GUL_SHRINK_X;
    if (y)
        self->box.flags |= GUL_SHRINK_Y;
}

void land_widget_layout_set_expanding(LandWidget *self, int x, int y)
{
    if (x)
        self->box.flags &= ~GUL_SHRINK_X;
    if (y)
        self->box.flags &= ~GUL_SHRINK_Y;
}

void land_widget_layout_set_border(LandWidget *self, int l, int t, int r, int b, int hgap, int vgap)
{
    self->box.il = l;
    self->box.it = t;
    self->box.ir = r;
    self->box.ib = b;
    self->box.hgap = hgap;
    self->box.vgap = vgap;
}

void land_widget_layout_add(LandWidget *parent, LandWidget *child)
{
    gul_remove_child(&parent->box, &child->box);
    gul_attach_child(&parent->box, &child->box);
}

int land_widget_layout(LandWidget *self)
{
    return gul_box_fit_children(&self->box, 0, 0);
}

int land_widget_layout_adjust(LandWidget *self, int x, int y)
{
    
    return gul_box_fit_children(&self->box, x, y);
}
