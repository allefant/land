import grid

static import global math, stdbool
static import log, display

# Isometric cells:
#
# Where is a cell drawn? As origin, we use the top. X-axis goes right down,
# Y-axis goes left down. In a sense, we rotate the non-isometric grid 45°
# clockwise.
#
# The dimensions of a tile look like this:
#
#  w1 | w2
# h1 /\
# __/  \
#   \   \
# h2 \   \
#     \  /
#      \/
#
# Now where does that put the tile at position cx/cy?
#
# px = cx * w2 - cy * w1    (1)
# py = cx * h2 + cy * h1    (2)
#
# w/h is the size of a tile.
#
# Reverse, which tile is under px/py?
#
# We solve for cx/cy:
#
# (1->) cx = (px + cy * w1) / w2    (3)
# (1->) cy = (cx * w2 - px) / w1    (4)
# (2->) cx = (py - cy * h1) / h2    (5)
# (2->) cy = (py - cx * h2) / h1    (6)
#
# (6 in 3->) cx = (px + ((py - cx * h2) / h1) * w1) / w2    (7)
# (5 in 4->) cy = (((py - cy * h1) / h2) * w2 - px) / w1    (8)
#
# (7->) cx * (w2 * h1 + h2 * w1) = px * h1 + py * w1
# (8->) cy * (w1 * h2 + w2 * h1) = py * w2 - px * h2
# 
# We get:
#
# a = w1 * h2 + w2 * h1
# cx = (px * h1 + py * w1) / a
# cy = (py * w2 - px * h2) / a
#

class LandGridIsometric:
    LandGrid super
    float cell_w1, cell_h1
    float cell_w2, cell_h2

global LandGridInterface *land_grid_vtable_isometric
global LandGridInterface *land_grid_vtable_isometric_wrap

static def new(float cell_w1, cell_h1, cell_w2, cell_h2,
    int x_cells, y_cells) -> LandGrid *:
    LandGridIsometric *self
    land_alloc(self)
    land_grid_initialize(&self.super, cell_w1 + cell_w2, cell_h1 + cell_h2,
        x_cells, y_cells)
    self.cell_w1 = cell_w1
    self.cell_h1 = cell_h1
    self.cell_w2 = cell_w2
    self.cell_h2 = cell_h2
    return &self.super

def land_isometric_new(float cell_w1, cell_h1, cell_w2, cell_h2,
    int x_cells, y_cells) -> LandGrid *:
    LandGrid *self = new(cell_w1, cell_h1, cell_w2, cell_h2, x_cells, y_cells)
    self.vt = land_grid_vtable_isometric
    return self

def land_isometric_wrap_new(float cell_w1, cell_h1, cell_w2, cell_h2,
    int x_cells, y_cells) -> LandGrid *:
    LandGrid *self = new(cell_w1, cell_h1, cell_w2, cell_h2, x_cells, y_cells)
    self.vt = land_grid_vtable_isometric_wrap
    self.wrap = true
    return self

def land_isometric_custom_grid(
    float cell_w1, cell_h1, cell_w2, cell_h2, int x_cells, y_cells, bool wrap,
    void (*draw_cell)(LandGrid *self, LandView *view, int cell_x, int cell_y,
        float x, float y)) -> LandGrid *:
    LandGrid *self = new(cell_w1, cell_h1, cell_w2, cell_h2, x_cells, y_cells)
    land_alloc(self.vt)
    self.vt->draw = wrap ? land_grid_draw_isometric_wrap :\
        land_grid_draw_isometric
    self.vt->get_cell_at = wrap ? land_grid_pixel_to_cell_isometric_wrap :\
        land_grid_pixel_to_cell_isometric
    self.vt->draw_cell = draw_cell
    self.vt->get_cell_position = wrap ?\
        land_grid_cell_to_pixel_isometric_wrap :\
        land_grid_cell_to_pixel_isometric
    self.wrap = wrap
    return self

def land_grid_pixel_to_cell_isometric(LandGrid *self, LandView *view,
    float mx, float my, float *partial_x, float *partial_y):
    """
    Returns the grid position in cells below the specified pixel position in
    the given view. 
    """
    LandGridIsometric *iso = (void *)self

    float x = mx
    float y = my
    if view:
        x += view->scroll_x - view->x
        y += view->scroll_y - view->y

    float a = iso->cell_w1 * iso->cell_h2 + iso->cell_w2 * iso->cell_h1

    *partial_x = (x * iso->cell_h1 + y * iso->cell_w1) / a
    *partial_y = (y * iso->cell_w2 - x * iso->cell_h2) / a

def land_grid_cell_to_pixel_isometric(LandGrid *self, LandView *view,
    float cell_x, cell_y, *view_x, *view_y):
    """
    Given a cell position, return the position of the cell's origin in
    on-screen coordinates, using the current view.
    """
    LandGridIsometric *iso = (void *)self

    float mx = cell_x * iso->cell_w2 - cell_y * iso->cell_w1
    float my = cell_x * iso->cell_h2 + cell_y * iso->cell_h1
    mx = view->x + mx - view->scroll_x
    my = view->y + my - view->scroll_y
    *view_x = mx
    *view_y = my

def land_grid_cell_to_pixel_isometric_wrap(LandGrid *self, LandView *view,
    float cell_x, cell_y, *view_x, *view_y):
    """
    Given a cell position, return the position of the cell's origin in
    on-screen coordinates, using the current view.
    """
    LandGridIsometric *iso = (void *)self

    # We are a wrapped grid, so normalize the passed cell position first to
    # lie in the zero quadrant.
    cell_x = cell_x - floorf(cell_x / self.x_cells) * self->x_cells
    cell_y = cell_y - floorf(cell_y / self.y_cells) * self->y_cells

    # The pixel offset then also is guaranteed to be normalized.
    float mx = cell_x * iso->cell_w2 - cell_y * iso->cell_w1
    float my = cell_x * iso->cell_h2 + cell_y * iso->cell_h1

    # If the view was not normalized, that may be intended by the caller, so
    # don't mess with it.
    mx = view->x + mx - view->scroll_x
    my = view->y + my - view->scroll_y
    *view_x = mx
    *view_y = my

def land_grid_pixel_to_cell_isometric_wrap(LandGrid *self, LandView *view,
    float mx, float my, float *partial_x, float *partial_y):
    float x, y
    land_grid_pixel_to_cell_isometric(self, view, mx, my, &x, &y)
    *partial_x = x - floorf(x / self.x_cells) * self->x_cells
    *partial_y = y - floorf(y / self.y_cells) * self->y_cells

# Returns the grid position in cells below the specified view position in
# pixels. The view position must be valid. 
static def view_to_cell(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y):
    LandGridIsometric *iso = (void *)self
    float x = view_x
    float y = view_y

    float a = iso->cell_w1 * iso->cell_h2 + iso->cell_w2 * iso->cell_h1

    *cell_x = floor((x * iso->cell_h1 + y * iso->cell_w1) / a)
    *cell_y = floor((y * iso->cell_w2 - x * iso->cell_h2) / a)

# Returns the grid position in cells below the specified view position in
# pixels, wrapping around in both dimensions. 
static def view_to_cell_wrap(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y):
    int cx, cy
    view_to_cell(self, view_x, view_y, &cx, &cy)

    # NOTE: C99 semantics for negative values assumed
    cx %= self.x_cells
    cy %= self.y_cells
    if cx < 0: cx += self.x_cells
    if cy < 0: cy += self.y_cells

    *cell_x = cx
    *cell_y = cy

static def cell_to_view(LandGrid *self, float cell_x, cell_y, *view_x, *view_y):
    LandGridIsometric *iso = (void *)self

    *view_x = cell_x * iso->cell_w2 - cell_y * iso->cell_w1
    *view_y = cell_x * iso->cell_h2 + cell_y * iso->cell_h1

# Given a pixel position relative to the grid origin, this returns an integer
# cell position of the cell below that position, and a pixel offset how much
# to offset tiles so they match.
#
# A return value of 0 means, there is no visible tiles, and the out
# parameters are meaningless (cases 1, 2 and 7 in the diagram below).
#
#       (3)   |   |
# ____________|(6)|
#             /\  |
#            /  \ |
#     (4)   /    \|
#          /     /|
#         /     / |(2)
#  ______/     /  |
#    (5) \    /(7)|
#         \  /    |
#  ________\/_____|
#        (1)
#
static def find_offset(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y, float *pixel_x, float *pixel_y) -> int:
    LandGridIsometric *iso = (void *)self
    float h1 = iso->cell_h1
    float w2 = iso->cell_w2
    float h2 = iso->cell_h2

    float right_x = w2 * self.x_cells
    float right_y = h2 * self.x_cells
    float left_y = h1 * self.y_cells
    float bottom_y = right_y + left_y

    view_to_cell(self, view_x, view_y, cell_x, cell_y)

    if view_y >= bottom_y: return 0 # (1)
    elif view_x >= right_x: return 0 # (2)
    elif view_x < 0 and view_y < 0: # (3)
        *cell_x = 0
        *cell_y = 0
    elif *cell_x < 0 and view_x < 0 and view_y < left_y: # (4)
        *cell_x = 0
        *cell_y = view_y / h1
    elif *cell_y >= self.y_cells: # (5)
        *cell_x = (view_y - left_y) / h2
        *cell_y = self.y_cells - 1
    elif *cell_y < 0: # (6)
        *cell_x = view_x / w2
        *cell_y = 0
    elif *cell_x >= self.x_cells: # (7)
        return 0

    cell_to_view(self, *cell_x, *cell_y, pixel_x, pixel_y)
    *pixel_x -= view_x
    *pixel_y -= view_y
    return 1

static def find_offset_wrap(LandGrid *self, float view_x, float view_y,
    int *cell_x, int *cell_y, float *pixel_x, float *pixel_y):
    float vw = (self.x_cells * self->cell_w) / 2
    float vh = (self.y_cells * self->cell_h) / 2
    float x, y
    view_to_cell_wrap(self, view_x, view_y, cell_x, cell_y)
    cell_to_view(self, *cell_x, *cell_y, &x, &y)

    x -= view_x
    y -= view_y

    *pixel_x = x - (1 + floorf(x / vw - 0.5)) * vw
    *pixel_y = y - (1 + floorf(y / vh - 0.5)) * vh

#
#               |-
#             ||  ||
#           ||      ||
#         ||          ||
#       xX||          ||oO
#     xx  xx||      ||oo  oo
#   xx      xx||  ||oo      oo
# xx          xx||oo          oo
# xx          xx.*oo          oo
#   xx      xx..  ..oo      oo
#     xx  xx..      ..oo  oo
#       xx..          ..oo
#         ..          ..
#           ..      ..
#             ..  ..
#               ..
#
# 
def land_grid_isometric_placeholder(LandGrid *self, LandView *view, int cell_x, cell_y, float x, y):
    int x_, y_
    int w = self.cell_w / 2
    int h = self.cell_h / 2
    land_color(1, 0, 0, 1)
    x_ = x + w
    y_ = y + h
    land_line(x, y, x_, y_)
    x = x_
    y = y_
    x_ = x - w
    y_ = y + h
    land_line(x, y, x_, y_)
    x = x_
    y = y_
    x_ = x - w
    y_ = y - h
    land_line(x, y, x_, y_)
    x = x_
    y = y_
    x_ = x + w
    y_ = y - h
    land_line(x, y, x_, y_)

def land_grid_draw_isometric(LandGrid *self, LandView *view):
    LandGridIsometric *iso = (void *)self
    float w1 = iso->cell_w1
    float h1 = iso->cell_h1
    float w2 = iso->cell_w2
    float h2 = iso->cell_h2

    int cell_x, cell_y
    float pixel_x, pixel_y

    float view_x = view->scroll_x
    float view_y = view->scroll_y

    if not find_offset(self, view_x, view_y, &cell_x, &cell_y, &pixel_x,
            &pixel_y):
        return

    pixel_x += view->x
    pixel_y += view->y

    float h = h1
    if h2 < h: h = h2
    float upper_y = view->y

    int row = 0

    while 1:
        float line_pixel_x = pixel_x
        float line_pixel_y = pixel_y
        int line_cell_x = cell_x
        int line_cell_y = cell_y

        while 1:
            while pixel_y + h2 > upper_y and cell_y > 0:
                pixel_x += w1
                pixel_y -= h1
                cell_y--

            if pixel_x - w1 >= view->x + view->w: break

            if pixel_y + h1 + h2 - upper_y <= h:
                if pixel_y >= view->y + view->h: return
                self.vt->draw_cell(self, view, cell_x, cell_y, pixel_x, pixel_y)

            pixel_x += w2
            pixel_y += h2
            cell_x++

            if cell_x >= self.x_cells: break

        cell_x = line_cell_x
        cell_y = line_cell_y
        pixel_x = line_pixel_x
        pixel_y = line_pixel_y

        upper_y += h
        row++

        if pixel_y + h1 + h2 <= upper_y:
            if pixel_x + w2 - w1 > view->x and cell_y < self.y_cells - 1:
                pixel_x -= w1
                pixel_y += h1
                cell_y++
            else:
                if cell_x >= self.x_cells - 1:
                    break
                pixel_x += w2
                pixel_y += h2
                cell_x++

def land_grid_draw_isometric_wrap(LandGrid *self, LandView *view):
    float w = self.cell_w / 2
    float h = self.cell_h / 2
    int cell_x, cell_y
    float pixel_x, pixel_y

    float view_x = view->scroll_x
    float view_y = view->scroll_y

    find_offset_wrap(self, view_x, view_y, &cell_x, &cell_y, &pixel_x, &pixel_y)

    # One row up might also be in. 
    if pixel_y > -h:
        cell_y--
        if cell_y < 0: cell_y += self.y_cells
        pixel_x += w
        pixel_y -= h

    pixel_x += view->x
    pixel_y += view->y

    while pixel_y < view->y + view->h:
        float line_pixel_x = pixel_x
        float line_pixel_y = pixel_y
        int line_cell_x = cell_x
        int line_cell_y = cell_y
        while pixel_x - w < view->x + view->w:
            self.vt->draw_cell(self, view, cell_x, cell_y, pixel_x, pixel_y)

            pixel_x += w
            pixel_y += h
            cell_x++
            if cell_x >= self.x_cells: cell_x -= self->x_cells

            pixel_x += w
            pixel_y -= h
            cell_y--
            if cell_y < 0: cell_y += self.y_cells

        cell_x = line_cell_x
        cell_y = line_cell_y
        pixel_x = line_pixel_x
        pixel_y = line_pixel_y

        if pixel_x > view->x:
            pixel_x -= w
            pixel_y += h
            cell_y++
            if cell_y >= self.y_cells: cell_y -= self->y_cells

        else:
            pixel_x += w
            pixel_y += h
            cell_x++
            if cell_x >= self.x_cells: cell_x -= self->x_cells

def land_isometric_init():
    land_log_message("land_isometric_init\n")

    land_alloc(land_grid_vtable_isometric)
    land_grid_vtable_isometric->draw = land_grid_draw_isometric
    land_grid_vtable_isometric->draw_cell = land_grid_isometric_placeholder
    land_grid_vtable_isometric->get_cell_at = land_grid_pixel_to_cell_isometric
    land_grid_vtable_isometric->get_cell_position =\
        land_grid_cell_to_pixel_isometric

    land_alloc(land_grid_vtable_isometric_wrap)
    land_grid_vtable_isometric_wrap->draw = land_grid_draw_isometric_wrap
    land_grid_vtable_isometric_wrap->draw_cell = land_grid_isometric_placeholder
    land_grid_vtable_isometric_wrap->get_cell_at =\
        land_grid_pixel_to_cell_isometric_wrap
    land_grid_vtable_isometric_wrap->get_cell_position =\
        land_grid_cell_to_pixel_isometric_wrap

def land_isometric_exit():
    land_free(land_grid_vtable_isometric)
    land_free(land_grid_vtable_isometric_wrap)
