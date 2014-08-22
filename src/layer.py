import global stdbool, math
import array, grid, sprite

class LandLayer:
    # position inside the map (origin of layer relative to origin of map) 
    float x, y

    # For parallax scrolling, given the above fixed position, this is the speed
    # with which the layer scrolls compared to the main map. 1 would mean, it
    # scrolls with the main map. 0.5 would mean, if the main map scrolls 10
    # pixels, this layer will only have scrolled 5.
    float scrolling_x, scrolling_y
    
    # Scale factor for the entire layer. It does not affect x/y nor
    # scrolling_x/scrolling_y but scales the grid which is being drawn
    # as a whole.
    float scale_x, scale_y

    # This allows adding an offset to the view area. For example if you have a
    # layer with objects who can overlap to the tiles above, it might make sense
    # to increase view_h so additional tiles which could be visible are drawn.
    float view_x, view_y, view_w, view_h
    
    float r, g, b, a

    char *name

    LandGrid *grid

    LandSprite *first_active

    LandLayer *next_in_map

    # Just the same as removing the layer, but if a layer is toggled
    # on and off it may be easier to use the flag than removing and
    # re-adding it.
    bool hidden

def land_layer_draw(LandLayer *self, LandView *view):
    if self.hidden: return
    LandView v = *view
   
    v.scroll_x += self.view_x - self->x
    v.scroll_y += self.view_y - self->y
    v.scroll_x *= self.scrolling_x / self->scale_x
    v.scroll_y *= self.scrolling_y / self->scale_y
    v.scale_x *= self.scale_x;
    v.scale_y *= self.scale_y;
    v.x += self.view_x
    v.y += self.view_y
    v.w += self.view_w
    v.h += self.view_h
    v.r *= self.r
    v.g *= self.g
    v.b *= self.b
    v.a *= self.a
    # TODO: can a layer have more than one grid?
    if self.grid: land_grid_draw(self->grid, &v)

def land_layer_draw_grid(LandLayer *self, LandView *view):
    """
    Draws a debug grid using the layer's cell size.
    """
    LandGrid *grid = self.grid
    LandView v = *view
    
    v.scroll_x += self.view_x - self->x
    v.scroll_y += self.view_y - self->y
    v.scroll_x *= self.scrolling_x
    v.scroll_y *= self.scrolling_y
    v.scale_x *= self.scale_x;
    v.scale_y *= self.scale_y;
    v.x += self.view_x
    v.y += self.view_y
    v.w += self.view_w
    v.h += self.view_h
    
    view = &v

    land_color(0, 0, 1, 0.5)

    # FIXME: Can't assume rectangular grid, might be iso/hex
    float cx = view->scroll_x / grid->cell_w
    float cy = view->scroll_y / grid->cell_h
    float ox = floor(cx) - cx
    float oy = floor(cy) - cy
    float sx = grid->cell_w * view->scale_x
    float sy = grid->cell_h * view->scale_y
    float min_x = view->x + ox * sx + 0.5
    float min_y = view->y + oy * sy + 0.5
    if cx < 0:
        min_x -= floor(cx) * sx
    if cy < 0:
        min_y -= floor(cy) * sy
    float max_x = view->x + sx * (grid->x_cells - cx) + 1
    float max_y = view->y + sy * (grid->y_cells - cy) + 1
    
    float vy1 = view->y
    float vy2 = view->y + view->h
    if vy1 < min_y: vy1 = min_y
    if vy2 > max_y: vy2 = max_y
    
    float vx1 = view->x
    float vx2 = view->x + view->w
    if vx1 < min_x: vx1 = min_x
    if vx2 > max_x: vx2 = max_x
    
    for float x = min_x while x < view->x + view->w with x += sx:
        if x > max_x: break
        land_line(x, vy1, x, vy2)

    for float y = min_y while y < view->y + view->h with y += sy:
        if y > max_y: break
        land_line(vx1, y, vx2, y)

def land_layer_set_name(LandLayer *self, char const *name):
    if self.name: land_free(self->name)
    self.name = land_strdup(name)

def land_layer_del(LandLayer *self):
    land_grid_del(self.grid)
    if self.name: land_free(self->name)
    land_free(self)

LandLayer *def land_layer_new_with_grid(LandGrid *grid):
    LandLayer *self
    land_alloc(self)
    self.scrolling_x = 1
    self.scrolling_y = 1
    self.scale_x = 1
    self.scale_y = 1
    self.grid = grid
    self.r = 1
    self.g = 1
    self.b = 1
    self.a = 1
    return self

LandLayer *def land_layer_new():
    return land_layer_new_with_grid(None)

def land_layer_set_scroll_speed(LandLayer *self, float x, float y):
    self.scrolling_x = x
    self.scrolling_y = y

def land_layer_set_scale(LandLayer *self, float x, float y):
    self.scale_x = x
    self.scale_y = y

def land_layer_set_position(LandLayer *self, float x, float y):
    self.x = x
    self.y = y

def land_layer_set_grid(LandLayer *self, LandGrid *grid):
    self.grid = grid

def land_layer_hide(LandLayer *self):
    self.hidden = true

def land_layer_unhide(LandLayer *self):
    self.hidden = false
