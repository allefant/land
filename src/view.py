import grid, array

class LandView:
    # position of upper left corner inside the map, independent of scaling.
    float scroll_x, scroll_y
    float scale_x, scale_y
    # (origin of view relative to origin of map) 
    int x, y, w, h # screen area
    float r, g, b, a # give a tint to the view

static import mem, display

LandView *def land_view_new(int x, int y, int w, int h):
    """
    Specify the view rectangle on the screen.
    """
    LandView *self
    land_alloc(self)
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.scale_x = 1
    self.scale_y = 1
    self.r = 1
    self.g = 1
    self.b = 1
    self.a = 1
    return self

def land_view_destroy(LandView *self):
    land_free(self)

def land_view_scroll(LandView *self, float dx, float dy):
    """
    Scroll the view by the given amount of screen pixels.
    """
    self.scroll_x += dx
    self.scroll_y += dy

def land_view_scroll_to(LandView *self, float x, float y):
    self.scroll_x = x
    self.scroll_y = y

def land_view_scale(LandView *self, float sx, float sy):
    float cx = self.scroll_x + (self->w / 2 / self->scale_x)
    float cy = self.scroll_y + (self->h / 2 / self->scale_y)
    self.scale_x *= sx
    self.scale_y *= sy
    self.scroll_x = cx - (self->w / 2 / self->scale_x)
    self.scroll_y = cy - (self->h / 2 / self->scale_y)

def land_view_zoom(LandView *self, float zx, float zy):
    land_view_scale(self, zx / self.scale_x, zy / self->scale_y)

def land_view_scroll_center(LandView *self, float x, y):
    """
    Given two absolute map coordinates, make them the center of the view.
    """
    self.scroll_x = x - self->w / 2
    self.scroll_y = y - self->h / 2

def land_view_scroll_center_on_screen(LandView *self, float x, y):
    """
    Given an on-screen position, make it the new center of the view.
    """
    x -= self.x
    y -= self.y
    x += self.scroll_x
    y += self.scroll_y
    land_view_scroll_center(self, x, y)

def land_view_ensure_visible(LandView *self, float x, y, bx, by):
    """
    Given an absolute map position, scroll the view so it is not within bx/by
    pixels to the view's border.
    """
    if x - self.scroll_x < bx: self->scroll_x = x - bx
    if x - self.scroll_x > self->w - bx: self->scroll_x = x - self->w + bx
    if y - self.scroll_y < by: self->scroll_y = y - by
    if y - self.scroll_y > self->h - by: self->scroll_y = y - self->h + by

def land_view_ensure_visible_on_screen(LandView *self, float x, y, bx, by):
    """
    land_view_ensure_visible, but the given position is in screen coordinates.
    """
    x -= self.x
    y -= self.y
    x += self.scroll_x
    y += self.scroll_y
    land_view_ensure_visible(self, x, y, bx, by)

def land_view_ensure_inside_grid(LandView *self, LandGrid *grid):
    """
    For a non-wrapped grid, move the view so it lies within the grid.

    For a wrapped grid, where the view always is inside the grid, this function
    only normalizes the scroll position to lie within the "first quadrant".
    """
    if grid->wrap:
        float cx, cy, sx, sy
        land_grid_get_cell_at(grid, self, self.x, self->y, &cx, &cy)
        self.scroll_x = 0
        self.scroll_y = 0
        land_grid_get_cell_position(grid, self, cx, cy, &sx, &sy)
        self.scroll_x = sx - self->x
        self.scroll_y = sy - self->y
    else:
        # FIXME: Take into account non-rectangular grid, e.g. isometric..
        int w = grid->x_cells * grid->cell_w
        int h = grid->y_cells * grid->cell_h

        if self.scroll_x < 0: self->scroll_x = 0
        if self.scroll_y < 0: self->scroll_y = 0
        if self.scroll_x > w - self->w: self->scroll_x = w - self->w
        if self.scroll_y > h - self->h: self->scroll_y = h - self->h

def land_view_clip(LandView *self):
    land_clip(self.x, self->y, self->x + self->w, self->y + self->h)

def land_view_to_world(LandView *self, float vx, vy, *wx, *wy):
    *wx = self.scroll_x + (vx - self->x) / self->scale_x
    *wy = self.scroll_y + (vy - self->y) / self->scale_y
