#ifdef _PROTOTYPE_

#include "array.h"
#include "grid.h"
#include "sprite.h"

typedef struct LandLayer LandLayer;

struct LandLayer
{
    float x, y; /* position inside the map (origin of layer relative to origin of map) */

    /* For parallax scrolling, given the above fixed position, this is the speed
     * with which the layer scrolls compared to the main map. 1 would mean, it
     * scrolls with the main map. 0.5 would mean, if the main map scrolls 10
     * pixels, this layer will only have scrolled 5.
     */
    float scrolling_x, scrolling_y;

    LandGrid *grid;

    LandSprite *first_active;

    LandLayer *next_in_map;
};

#endif /* _PROTOTYPE_ */

#include "layer.h"

void land_layer_draw(LandLayer *self, LandView *view)
{
    LandView v = *view;
    v.scroll_x -= self->x;
    v.scroll_y -= self->y;
    v.scroll_x *= self->scrolling_x;
    v.scroll_y *= self->scrolling_y;
    // TODO: can a layer have more than one grid?
    if (self->grid)
        land_grid_draw(self->grid, &v);
}

LandLayer *land_layer_new(void)
{
    LandLayer * self;
    land_alloc(self);
    self->scrolling_x = 1;
    self->scrolling_y = 1;
    return self;
}

void land_layer_del(LandLayer *self)
{
    land_grid_del(self->grid);
    land_free(self);
}

LandLayer *land_layer_new_with_grid(LandGrid *grid)
{
    LandLayer *self;
    land_alloc(self);
    self->scrolling_x = 1;
    self->scrolling_y = 1;
    self->grid = grid;
    return self;
}

void land_layer_set_scroll_speed(LandLayer *self, float x, float y)
{
    self->scrolling_x = x;
    self->scrolling_y = y;
}

void land_layer_set_position(LandLayer *self, float x, float y)
{
    self->x = x;
    self->y = y;
}
