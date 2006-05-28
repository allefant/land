#ifdef _PROTOTYPE_

#include "../land.h"
#include "base.h"

#endif /* _PROTOTYPE_ */

#include "widget/layout.h"

void land_widget_layout_set_grid(LandWidget *self, int columns, int rows,
    int update)
{
    self->box.rows = rows;
    self->box.cols = columns;
    if (update)
        gul_layout_changed(&self->box);
}

void land_widget_layout_set_grid_position(LandWidget *self, int column, int row,
    int update)
{
    self->box.col = column;
    self->box.row = row;
    if (self->parent && update)
        gul_layout_changed(&self->parent->box);
}

void land_widget_layout_set_grid_extra(LandWidget *self, int columns, int rows,
    int update)
{
    self->box.extra_cols = columns;
    self->box.extra_rows = rows;
    if (self->parent && update)
        gul_layout_changed(&self->parent->box);
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

void land_widget_layout_add(LandWidget *parent, LandWidget *child, int update)
{
    gul_remove_child(&parent->box, &child->box, update);
    gul_attach_child(&parent->box, &child->box, update);
}

int land_widget_layout(LandWidget *self, int update)
{
    if (update)
        gul_layout_changed(&self->box);
    return gul_box_fit_children(&self->box, 0, 0);
}

int land_widget_layout_adjust(LandWidget *self, int x, int y, int update)
{
    if (update)
        gul_layout_changed(&self->box);
    return gul_box_fit_children(&self->box, x, y);
}
