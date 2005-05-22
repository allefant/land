#ifdef _PROTOTYPE_

typedef struct LandGrid LandGrid;
typedef struct LandGridInterface LandGridInterface;

#include "view.h"

struct LandGridInterface
{
    void (*draw)(LandGrid *self, LandView *view);
    void (*draw_cell)(LandGrid *self, LandView *view, int cell_x, int cell_y, float pixel_x, float pixel_y);
    void (*get_cell_at)(LandGrid *self, LandView *view, float pixel_x, float pixel_y,
        float *cell_x, float *cell_y);
};

struct LandGrid
{
    LandGridInterface *vt;
    unsigned int x_cells, y_cells; /* in cells */
    unsigned int cell_w, cell_h; /* in pixels */
    int wrap_x, wrap_y;
};

#endif /* _PROTOTYPE_ */

#include "grid.h"
#include "log.h"
#include "tilegrid.h"
#include "isometric.h"
#include "sprite.h"

land_array(LandGrid);

static LandGrid *active_grid = 0;

void land_grid_draw(LandGrid *self, LandView *view)
{
    self->vt->draw(self, view);
}

void land_grid_get_cell_at(LandGrid *self, LandView *view, float view_x, float view_y,
    float *cell_x, float *cell_y)
{
    self->vt->get_cell_at(self, view, view_x, view_y, cell_x, cell_y);
}

void land_grid_initialize(LandGrid *self, int cell_w, int cell_h, int x_cells, int y_cells)
{
    self->x_cells = x_cells;
    self->y_cells = y_cells;
    self->cell_w = cell_w;
    self->cell_h = cell_h;

    active_grid = self;
}

void land_grid_init(void)
{
    land_log_msg("land_grid_init\n");
    land_tilemap_init();
    land_isometric_init();
    land_sprites_init();
}

