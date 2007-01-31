import array, grid, sprite

class LandLayer:
    float x, y; # position inside the map (origin of layer relative to origin of map) 

    # For parallax scrolling, given the above fixed position, this is the speed
    # with which the layer scrolls compared to the main map. 1 would mean, it
    # scrolls with the main map. 0.5 would mean, if the main map scrolls 10
    # pixels, this layer will only have scrolled 5.
      
    float scrolling_x, scrolling_y

    # This allows adding an offset to the view area. For example if you have a
    # layer with objects who can overlap to the tiles above, it might make sense
    # to increase view_h so additional tiles which could be visible are drawn.
    float view_x, view_y, view_w, view_h

    LandGrid *grid

    LandSprite *first_active

    LandLayer *next_in_map

def land_layer_draw(LandLayer *self, LandView *view):
    LandView v = *view
    v.scroll_x -= self->x
    v.scroll_y -= self->y
    v.scroll_x *= self->scrolling_x
    v.scroll_y *= self->scrolling_y
    v.x += self->view_x
    v.y += self->view_y
    v.w += self->view_w
    v.h += self->view_h
    # TODO: can a layer have more than one grid?
    if self->grid: land_grid_draw(self->grid, &v)

LandLayer *def land_layer_new():
    LandLayer * self
    land_alloc(self)
    self->scrolling_x = 1
    self->scrolling_y = 1
    return self

def land_layer_del(LandLayer *self):
    land_grid_del(self->grid)
    land_free(self)

LandLayer *def land_layer_new_with_grid(LandGrid *grid):
    LandLayer *self
    land_alloc(self)
    self->scrolling_x = 1
    self->scrolling_y = 1
    self->grid = grid
    return self

def land_layer_set_scroll_speed(LandLayer *self, float x, float y):
    self->scrolling_x = x
    self->scrolling_y = y

def land_layer_set_position(LandLayer *self, float x, float y):
    self->x = x
    self->y = y

def land_layer_set_grid(LandLayer *self, LandGrid *grid):
    self->grid = grid
