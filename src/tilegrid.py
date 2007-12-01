import grid, image

class LandTileGrid:
    LandGrid super
    LandImage **tiles

static import view, display, log, mem

macro LAND_TILE_GRID(_) ((LandTileGrid *)(_))

LandGridInterface *land_grid_vtable_tilegrid

LandGrid *def land_tilegrid_new(int cell_w, int cell_h, int x_cells, int y_cells):
    LandTileGrid *self
    land_alloc(self)
    land_grid_initialize(&self->super, cell_w, cell_h, x_cells, y_cells)
    self->super.vt = land_grid_vtable_tilegrid
    
    self->tiles = land_calloc(x_cells * y_cells * sizeof *self->tiles)
    return &self->super

# Destroys a tile grid. Images used by the grid are not affected. 
def land_tilegrid_del(LandGrid *self):
    land_free(LAND_TILE_GRID(self)->tiles)
    land_free(self)

def land_tilegrid_place(LandGrid *super, int cell_x, int cell_y,
    LandImage *image):
    if cell_x < 0 or cell_y < 0 or cell_x >= super->x_cells or \
        cell_y >= super->y_cells: return
    LandTileGrid *self = LAND_TILE_GRID(super)
    self->tiles[cell_y * super->x_cells + cell_x] = image

static def land_tilegrid_draw_cell(LandGrid *self, LandView *view,
    int cell_x, int cell_y, float pixel_x, float pixel_y):
    LandImage *image = LAND_TILE_GRID(self)->tiles[
        cell_y * self->x_cells + cell_x]
    if image:
        land_image_draw(image, pixel_x, pixel_y)


# Convert a view position inside the grid into cell and pixel position. 
static def view_x_to_cell_and_pixel_x(LandGrid *self, float view_x, int *cell_x,
    float *pixel_x):
    #FIXME
    # if self->wrap_x:
    #    # wrap around -> there's always a cell at the left border 
    #    *cell_x = (unsigned int)view_x / self->cell_w
    #    *pixel_x = -((unsigned int)view_x % self->cell_w)
    #
    # else
    if view_x < 0:
        # skip empty left area 
        *cell_x = 0
        *pixel_x = -view_x

    else:
        *cell_x = (unsigned int)view_x / self->cell_w
        *pixel_x = *cell_x * self->cell_w - view_x



# Convert a view position inside the grid into cell and pixel position. 
static def view_y_to_cell_and_pixel_y(LandGrid *self, float view_y, int *cell_y,
    float *pixel_y):
    #FIXME
    # if self->wrap_y:
    #    # wrap around -> there's always a cell at the top border 
    #    *cell_y = (unsigned int)view_y / self->cell_h
    #    *pixel_y = -((unsigned int)view_y % self->cell_h)
    #
    # else
    if view_y < 0:
        # skip empty top area 
        *cell_y = 0
        *pixel_y = -view_y

    else:
        *cell_y = (unsigned int)view_y / self->cell_h
        *pixel_y = *cell_y * self->cell_h - view_y

def land_grid_draw_normal(LandGrid *self, LandView *view):
    int cell_x, cell_y
    float pixel_x, pixel_y

    float view_x = view->scroll_x
    float view_y = view->scroll_y

    view_y_to_cell_and_pixel_y(self, view_y, &cell_y, &pixel_y)
    pixel_y += view->y * view->scale_y

    for ; pixel_y < view->y + view->h; cell_y++,\
        pixel_y += self->cell_h * view->scale_y:
        if cell_y >= self->y_cells:
            #FIXME
            # if self->wrap_y: cell_y -= self->y_cells
            # else
            break

        view_x_to_cell_and_pixel_x(self, view_x, &cell_x, &pixel_x)
        pixel_x += view->x * view->scale_x

        for ; pixel_x < view->x + view->w; cell_x++,\
            pixel_x += self->cell_w * view->scale_x:
            if cell_x >= self->x_cells:
                #FIXME
                # if self->wrap_x: cell_x -= self->x_cells
                # else
                break

            self->vt->draw_cell(self, view, cell_x, cell_y, pixel_x, pixel_y)

def land_tilemap_init():
    land_log_message("land_tilemap_init\n")
    land_alloc(land_grid_vtable_tilegrid)
    land_grid_vtable_tilegrid->draw = land_grid_draw_normal
    land_grid_vtable_tilegrid->draw_cell = land_tilegrid_draw_cell
    land_grid_vtable_tilegrid->del = land_tilegrid_del

def land_tilemap_exit():
    land_log_message("land_tilemap_exit\n")
    land_free(land_grid_vtable_tilegrid)
