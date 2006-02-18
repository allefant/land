#ifdef _PROTOTYPE_

typedef struct LandView LandView;

#include "grid.h"
#include "array.h"

struct LandView
{
    float scroll_x, scroll_y; /* position inside the map (origin of view relative to origin of map) */
    int x, y, w, h; /* screen area */
};

#endif /* _PROTOTYPE_ */

#include "view.h"

land_array(LandView);

LandView *land_view_new(int x, int y, int w, int h)
{
    land_new(LandView, self);
    self->x = x;
    self->y = y;
    self->w = w;
    self->h = h;
    return self;
}

void land_view_scroll_to(LandView *self, float x, float y)
{
    self->scroll_x = x;
    self->scroll_y = y;
}

void land_view_scroll_center(LandView *self, float x, float y)
{
    self->scroll_x = x - self->w / 2;
    self->scroll_y = y - self->h / 2;
}

void land_view_ensure_visible(LandView *self, float x, float y, float bx, float by)
{
    if (x - self->scroll_x < bx)
        self->scroll_x = x - bx;
    if (x - self->scroll_x > self->w - bx)
        self->scroll_x = x - self->w + bx;
    if (y - self->scroll_y < by)
        self->scroll_y = y - by;
    if (y - self->scroll_y > self->h - by)
        self->scroll_y = y - self->h + by;
}

void land_view_ensure_inside_grid(LandView *self, LandGrid *grid)
{
    int w = grid->x_cells * grid->cell_w;
    int h = grid->y_cells * grid->cell_h;

    if (self->scroll_x < 0) self->scroll_x = 0;
    if (self->scroll_y < 0) self->scroll_y = 0;
    if (self->w > w - self->w) self->w = w - self->w;
    if (self->h > h - self->h) self->h = h - self->h;
}
