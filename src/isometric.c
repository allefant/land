#ifndef _PROTOTYPE_

#include "grid.h"

#endif /* _PROTOTYPE_ */

#include <math.h>

#include "isometric.h"
#include "log.h"
#include "display.h"

/* Isometric cells:
 *
 * Where is a cell drawn? As origin, we use the top. X-axis goes right down,
 * Y-axis goes left down. In a sense, we rotate the non-isometric grid 45°
 * clockwise.
 *
 * Now where does that put the tile at position cx/cy?
 *
 * px = cx * w/2 - cy * w/2    (1)
 * py = cx * h/2 + cy * h/2    (2)
 *
 * w/h is the size of a tile.
 *
 * Reverse, which tile is under px/py?
 *
 * We solve for cx/cy:
 *
 * (1->) cx = px/(w/2) + cy    (3)
 * (2->) cx = py/(h/2) - cy    (4)
 *
 * (3+4->) cx = px/(w/2) + py/(h/2) - cx
 * (4+3->) cy = py/(h/2) - px/(w/2) - cy
 *
 * We get:
 *
 * cx = (px/(w/2) + py/(h/2)) / 2
 * cy = (py/(h/2) - px/(w/2)) / 2
 */

LandGridInterface *land_grid_vtable_isometric;
LandGridInterface *land_grid_vtable_isometric_wrap;

LandGrid *land_isometric_new(int cell_w, int cell_h, int x_cells, int y_cells)
{
    land_new(LandGrid, self);
    land_grid_initialize(self, cell_w, cell_h, x_cells, y_cells);
    self->vt = land_grid_vtable_isometric;
    return self;
}

/* Returns the grid position in cells below the specified pixel position in
 * the given view. */
void land_grid_pixel_to_cell_isometric(LandGrid *self, LandView *view,
    float mx, float my, float *partial_x, float *partial_y)
{
    float x = view->scroll_x + mx - view->x;
    float y = view->scroll_y + my - view->y;
    *partial_x = x / self->cell_w + y / self->cell_h;
    *partial_y = y / self->cell_h - x / self->cell_w;
}

void land_grid_pixel_to_cell_isometric_wrap(LandGrid *self, LandView *view,
    float mx, float my, float *partial_x, float *partial_y)
{
    float x, y;
    land_grid_pixel_to_cell_isometric(self, view, mx, my, &x, &y);
    *partial_x = x - floorf(x / self->x_cells) * self->x_cells;
    *partial_y = y - floorf(y / self->y_cells) * self->y_cells;
}

/* Returns the grid position in cells below the specified view position in
 * pixels. */
static void view_to_cell(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y)
{
    float w = self->cell_w / 2;
    float h = self->cell_h / 2;

    // TODO: clarify wrapped/clamped case
    *cell_x = (view_x / w + view_y / h) / 2;
    *cell_y = (view_y / h - view_x / w) / 2;
}

static void cell_to_view(LandGrid *self, int cell_x, int cell_y,
    float *view_x, float *view_y)
{
    int w = self->cell_w / 2;
    int h = self->cell_h / 2;

    *view_x = cell_x * w - cell_y * w;
    *view_y = cell_x * h + cell_y * h;
}

/* Given a pixel position inside the grid, this returns an integer cell
 * position of the cell below that position, and a pixel offset how much
 * to offset tiles so they match.
 *
 * A return value of 0 means, there is no visible tiles, and the out
 * parameters are meaningless (cases 1, 2 and 7 in the diagram below).
 *
 *       (4)   |   |
 * ____________|(6)|
 *             /\  |
 *            /  \ |
 *     (5)   /    \|
 *          /     /|
 *         /     / |(2)
 *  ______/     /  |
 *    (3) \    /(7)|
 *         \  /    |
 *  ________\/_____|
 *        (1)
 *
 */
static int find_offset(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y, float *pixel_x, float *pixel_y)
{
    float w = self->cell_w / 2;
    float h = self->cell_h / 2;

    float out_x = (int)(self->x_cells - self->y_cells) * w;
    float out_y = (self->x_cells + self->y_cells) * h;

    // TODO: Currently, this does not work in the wrapped case

    if (view_y >= out_y) /* (1) */
    {
        return 0;
    }

    if (view_x >= self->x_cells * w) /* (2) */
    {
        return 0;
    }

    if (view_y >= self->y_cells * h &&
        (view_x - out_x) * h < (view_y - out_y) * w) /* 3 */
    {
        *cell_x = (view_y - self->y_cells * h) / h;
        *cell_y = self->y_cells - 1;
        goto done;
    }

    if (view_x < 0)
    {
        if (view_y < 0) /* (4) */
        {
            *cell_x = 0;
            *cell_y = 0;
            goto done;
        }
        else if (view_x * h < -view_y * w && view_y < self->y_cells * h) /* (5) */
        {
            *cell_x = 0;
            *cell_y = view_y / h;
            goto done;
        }
    }

    if (view_y < self->x_cells * h)
    {
        if (view_y * w < view_x * h) /* (6) */
        {
            *cell_x = view_x / w;
            *cell_y = 0;
            goto done;
        }
    }
    else
    {
        if ((view_x - out_x) * h > -(view_y - out_y) * w) /* 7 */
        {
            return 0;
        }
    }

    view_to_cell(self, view_x, view_y, cell_x, cell_y);

done:
    cell_to_view(self, *cell_x, *cell_y, pixel_x, pixel_y);
    *pixel_x -= view_x;
    *pixel_y -= view_y;
    return 1;
}

static int find_offset_wrap(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y, float *pixel_x, float *pixel_y)
{
    view_to_cell(self, view_x, view_y, cell_x, cell_y);
    cell_to_view(self, *cell_x, *cell_y, pixel_x, pixel_y);
    *pixel_x -= view_x;
    *pixel_y -= view_y;
}

/*
 *               |-
 *             ||  ||
 *           ||      ||
 *         ||          ||
 *       xX||          ||oO
 *     xx  xx||      ||oo  oo
 *   xx      xx||  ||oo      oo
 * xx          xx||oo          oo
 * xx          xx.*oo          oo
 *   xx      xx..  ..oo      oo
 *     xx  xx..      ..oo  oo
 *       xx..          ..oo
 *         ..          ..
 *           ..      ..
 *             ..  ..
 *               ..
 *
 */
static void placeholder(LandGrid *self, LandView *view, int cell_x, int cell_y, float x, float y)
{
    int x_, y_;
    int w = self->cell_w / 2;
    int h = self->cell_h / 2;
    land_color(255, 0, 0);
    x_ = x + w;
    y_ = y + h;
    land_line(x, y, x_, y_);
    x = x_;
    y = y_;
    x_ = x - w;
    y_ = y + h;
    land_line(x, y, x_, y_);
    x = x_;
    y = y_;
    x_ = x - w;
    y_ = y - h;
    land_line(x, y, x_, y_);
    x = x_;
    y = y_;
    x_ = x + w;
    y_ = y - h;
    land_line(x, y, x_, y_);
}

void land_grid_draw_isometric(LandGrid *self, LandView *view)
{
    float w = self->cell_w / 2;
    float h = self->cell_h / 2;
    int cell_x, cell_y;
    float pixel_x, pixel_y;

    float view_x = view->scroll_x;
    float view_y = view->scroll_y;

    if (!find_offset(self, view_x, view_y, &cell_x, &cell_y, &pixel_x, &pixel_y))
        return;

    /* One row up might also be in. */
    if (pixel_y > -h)
    {
        if (cell_x > 0 && pixel_x > 0)
        {
            cell_x--;
            pixel_x -= w;
            pixel_y -= h;
        }
        else
        if (cell_y > 0)
        {
            cell_y--;
            pixel_x += w;
            pixel_y -= h;
        }
    }

    pixel_x += view->x;
    pixel_y += view->y;

    while (pixel_y < view->y + view->h)
    {
        float line_pixel_x = pixel_x;
        float line_pixel_y = pixel_y;
        int line_cell_x = cell_x;
        int line_cell_y = cell_y;
        while (pixel_x - w < view->x + view->w)
        {
            self->vt->draw_cell(self, view, cell_x, cell_y, pixel_x, pixel_y);
            if (cell_x < (int)self->x_cells - 1)
            {
                pixel_x += w;
                pixel_y += h;
                cell_x++;
            }
            else
                break;
            if (cell_y > 0)
            {
                pixel_x += w;
                pixel_y -= h;
                cell_y--;
            }
            else
                break;
        }
        cell_x = line_cell_x;
        cell_y = line_cell_y;
        pixel_x = line_pixel_x;
        pixel_y = line_pixel_y;

        if (pixel_x > view->x && cell_y < (int)self->y_cells - 1)
        {
            pixel_x -= w;
            pixel_y += h;
            cell_y++;
        }
        else
        {
            if (cell_x >= (int)self->x_cells - 1)
                break;
            pixel_x += w;
            pixel_y += h;
            cell_x++;
        }
    }
}

void land_grid_draw_isometric_wrapped(LandGrid *self, LandView *view)
{
    float w = self->cell_w / 2;
    float h = self->cell_h / 2;
    int cell_x, cell_y;
    float pixel_x, pixel_y;

    float view_x = view->scroll_x;
    float view_y = view->scroll_y;


    if (!find_offset(self, view_x, view_y, &cell_x, &cell_y, &pixel_x, &pixel_y))
        return;

    /* One row up might also be in. */
    if (pixel_y > -h)
    {
        if (cell_x > 0 && pixel_x > 0)
        {
            cell_x--;
            pixel_x -= w;
            pixel_y -= h;
        }
        else
        if (cell_y > 0)
        {
            cell_y--;
            pixel_x += w;
            pixel_y -= h;
        }
    }

    pixel_x += view->x;
    pixel_y += view->y;

    while (pixel_y < view->y + view->h)
    {
        float line_pixel_x = pixel_x;
        float line_pixel_y = pixel_y;
        int line_cell_x = cell_x;
        int line_cell_y = cell_y;
        while (pixel_x - w < view->x + view->w)
        {
            self->vt->draw_cell(self, view, cell_x, cell_y, pixel_x, pixel_y);
            if (cell_x < (int)self->x_cells - 1)
            {
                pixel_x += w;
                pixel_y += h;
                cell_x++;
            }
            else
                break;
            if (cell_y > 0)
            {
                pixel_x += w;
                pixel_y -= h;
                cell_y--;
            }
            else
                break;
        }
        cell_x = line_cell_x;
        cell_y = line_cell_y;
        pixel_x = line_pixel_x;
        pixel_y = line_pixel_y;

        if (pixel_x > view->x && cell_y < (int)self->y_cells - 1)
        {
            pixel_x -= w;
            pixel_y += h;
            cell_y++;
        }
        else
        {
            if (cell_x >= (int)self->x_cells - 1)
                break;
            pixel_x += w;
            pixel_y += h;
            cell_x++;
        }
    }
}

void land_isometric_init(void)
{
    land_log_msg("land_isometric_init\n");
    land_alloc(land_grid_vtable_isometric);
    land_grid_vtable_isometric->draw = land_grid_draw_isometric;
    land_grid_vtable_isometric->draw_cell = placeholder;
}

