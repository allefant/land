#ifdef _PROTOTYPE_

#include "array.h"

land_type (LandView)
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

