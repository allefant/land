"""
The art of programming tilemaps

= Types of tilemaps =

== The classic fixed-cell grid-map ==

This is the simplest form of a tilemap. Just define a grid and store a tile-id
in each cell.

== Optimized fixed-cell map ==

There are various ways to optimize the simple tilemap to consume less memory.
For example, quad-trees or similar techniques. A quad-tree can optimize away
large empty areas, and makes it easy to have different-sized tiles as long as
bigger ones have double the dimensions of smaller ones.

== Layers ==

Simply have multiple layers, one on top of another. This can have many uses,
for example different tile-sizes and parallax scrolling.

== Non-rectangle ==

Popular types of tiles don't use a fixed rectangular grid, but use hexagon or
isometric maps. We'll deal with both of them.

= The basics =

== Drawing ==

Assume, we have a fixed cell map. The x and y position of a tile can
be calculated like this:

 * pixel_x = tile_x * cell_width
 * pixel_y = tile_y * cell_height

If the map data are stored as an array, and each map position just
stores a tile number, we  can retriece it like this:

 * tile_numer = array[tile_y * map_width + tile_x]

So now, we have all we need. We can draw the tile to its position.
Doing this for all tiles in the map, we can draw the complete map.

== Picking ==

Something which is not obvious to do at first, but will be useful soon, is how
to pick tiles out of a map. Thinking about it, it is quite simple to
do. It is, in a sense, the opposite of drawing.

We have a (pixel) position, and want to know which tile lies under it.

 * tile_x = pixel_x / cell_width
 * tile_y = pixel_y / cell_height

== Collision ==

Since we know how to pick a tile from a position, we can easily do
collision detection now.

= Non-rectangular maps =

== Isometric (diamond layout) ==

== Hexagon (diamond layout) ==

== Isometric (row or column shifted layout) ==

== Hexagon (row or coumn shifted layout) ==


"""

import global stdbool
import view

class LandGridInterface:
    void (*draw)(LandGrid *self, LandView *view)
    void (*draw_cell)(LandGrid *self, LandView *view, int cell_x, int cell_y,
        float pixel_x, float pixel_y)
    void (*get_cell_at)(LandGrid *self, LandView *view, float pixel_x, float pixel_y,
        float *cell_x, float *cell_y)
    void (*get_cell_position)(LandGrid *self, LandView *view, float cell_x,
        float cell_y, float *pixel_x, float *pixel_y)
    void (*del)(LandGrid *self)

class LandGrid:
    LandGridInterface *vt
    int x_cells, y_cells # in cells 
    int cell_w, cell_h # in pixels
    bool wrap

static import grid, log, tilegrid, isometric, sprite, global math

def land_grid_draw(LandGrid *self, LandView *view):
    self->vt->draw(self, view)

def land_grid_get_cell_at(LandGrid *self, LandView *view, float view_x, view_y,
    *cell_x, *cell_y):
    """
    Given a view position, return the corresponding cell position.

    For a wrapped grid, the returned position will always be normalized to
    lie within the grid, even if the passed position or the view's scroll
    position are outside.
    """
    self->vt->get_cell_at(self, view, view_x, view_y, cell_x, cell_y)

def land_grid_get_cell_position(LandGrid *self, LandView *view, float cell_x,
    cell_y, *view_x, *view_y):
    """
    Given a cell position, return the corresponding view position, in pixels.

    For a wrapped grid, the returned position will first be normalized to
    lie within the grid, and then related to the view position. Try normalizing
    the view's scroll position first (land_view_ensure_inside_grid) so it lies
    within the grid, if you experience unexpected offsets.
    """
    self->vt->get_cell_position(self, view, cell_x, cell_y, view_x, view_y)

def land_grid_initialize(LandGrid *self,
    int cell_w, cell_h, int x_cells, y_cells):
    self->x_cells = x_cells
    self->y_cells = y_cells
    self->cell_w = cell_w
    self->cell_h = cell_h

def land_grid_init():
    land_log_message("land_grid_init\n")
    land_tilemap_init()
    land_isometric_init()
    land_sprites_init()

def land_grid_exit():
    land_log_message("land_grid_exit\n")
    land_tilemap_exit()
    land_isometric_exit()
    land_sprites_exit()

def land_grid_del(LandGrid *self):
    land_call_method(self, del, (self))
