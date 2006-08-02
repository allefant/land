#ifdef _PROTOTYPE_

#include "grid.h"
#include "image.h"

typedef struct LandTileGrid LandTileGrid;
struct LandTileGrid
{
    LandGrid super;
    LandImage **tiles;
};

#endif /* _PROTOTYPE_ */

#include "tilegrid.h"
#include "view.h"
#include "display.h"
#include "log.h"
#include "memory.h"

#define LAND_TILE_GRID(_) ((LandTileGrid *)(_))

LandGridInterface *land_grid_vtable_tilegrid;

LandGrid *land_tilegrid_new(int cell_w, int cell_h, int x_cells, int y_cells)
{
    LandTileGrid *self;
    land_alloc(self);
    land_grid_initialize(&self->super, cell_w, cell_h, x_cells, y_cells);
    self->super.vt = land_grid_vtable_tilegrid;
    
    self->tiles = land_calloc(x_cells * y_cells * sizeof *self->tiles);
    return &self->super;
}

/* Destroys a tile grid. Images used by the grid are not affected. */
void land_tilegrid_del(LandGrid *self)
{
    land_free(LAND_TILE_GRID(self)->tiles);
    land_free(self);
}

void land_tilegrid_place(LandGrid *super, int cell_x, int cell_y,
    LandImage *image)
{
    if (cell_x < 0 || cell_y < 0 || cell_x >= super->x_cells ||
        cell_y >= super->y_cells)
        return;
    LandTileGrid *self = LAND_TILE_GRID(super);
    self->tiles[cell_y * super->x_cells + cell_x] = image;
}

static void land_tilegrid_draw_cell(LandGrid *self, LandView *view,
    int cell_x, int cell_y, float pixel_x, float pixel_y)
{
    LandImage *image = LAND_TILE_GRID(self)->tiles
        [cell_y * self->x_cells + cell_x];
    if (image)
    {
        land_image_draw(image, pixel_x, pixel_y);
    }
}

/* Convert a view position inside the grid into cell and pixel position. */
static void view_x_to_cell_and_pixel_x(LandGrid *self, int view_x, int *cell_x, int *pixel_x)
{
#if 0
    if (self->wrap_x)
    {
        /* wrap around -> there's always a cell at the left border */
        *cell_x = (unsigned int)view_x / self->cell_w;
        *pixel_x = -((unsigned int)view_x % self->cell_w);
    }
    else
#endif
    {
        if (view_x < 0)
        {
            /* skip empty left area */
            *cell_x = 0;
            *pixel_x = -view_x;
        }
        else
        {
            *cell_x = (unsigned int)view_x / self->cell_w;
            *pixel_x = *cell_x * self->cell_w - view_x;
        }
    }
}

/* Convert a view position inside the grid into cell and pixel position. */
static void view_y_to_cell_and_pixel_y(LandGrid *self, int view_y, int *cell_y, int *pixel_y)
{
#if 0
    if (self->wrap_y)
    {
        /* wrap around -> there's always a cell at the top border */
        *cell_y = (unsigned int)view_y / self->cell_h;
        *pixel_y = -((unsigned int)view_y % self->cell_h);
    }
    else
#endif
    {
        if (view_y < 0)
        {
            /* skip empty top area */
            *cell_y = 0;
            *pixel_y = -view_y;
        }
        else
        {
            *cell_y = (unsigned int)view_y / self->cell_h;
            *pixel_y = *cell_y * self->cell_h - view_y;
        }
    }
}

void land_grid_draw_normal(LandGrid *self, LandView *view)
{
    int cell_x, cell_y;
    int pixel_x, pixel_y;

    float view_x = view->scroll_x;
    float view_y = view->scroll_y;

    view_y_to_cell_and_pixel_y(self, view_y, &cell_y, &pixel_y);
    pixel_y += view->y;

    for (; pixel_y < view->y + view->h; cell_y++, pixel_y += self->cell_h)
    {
        if (cell_y >= self->y_cells)
        {
#if 0
            if (self->wrap_y)
                cell_y -= self->y_cells;
            else
#endif
                break;
        }

        view_x_to_cell_and_pixel_x(self, view_x, &cell_x, &pixel_x);
        pixel_x += view->x;

        for (; pixel_x < view->x + view->w; cell_x++, pixel_x += self->cell_w)
        {
            if (cell_x >= self->x_cells)
            {
#if 0
                if (self->wrap_x)
                    cell_x -= self->x_cells;
                else
#endif
                    break;
            }

            self->vt->draw_cell(self, view, cell_x, cell_y, pixel_x, pixel_y);
        }
    }
}

void land_tilemap_init(void)
{
    land_log_message("land_tilemap_init\n");
    land_alloc(land_grid_vtable_tilegrid);
    land_grid_vtable_tilegrid->draw = land_grid_draw_normal;
    land_grid_vtable_tilegrid->draw_cell = land_tilegrid_draw_cell;
    land_grid_vtable_tilegrid->del = land_tilegrid_del;
}

void land_tilemap_exit(void)
{
    land_log_message("land_tilemap_exit\n");
    land_free(land_grid_vtable_tilegrid);
}
