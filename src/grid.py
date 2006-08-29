import view

class LandGridInterface:
    void (*draw)(LandGrid *self, LandView *view)
    void (*draw_cell)(LandGrid *self, LandView *view, int cell_x, int cell_y, float pixel_x, float pixel_y)
    void (*get_cell_at)(LandGrid *self, LandView *view, float pixel_x, float pixel_y,
        float *cell_x, float *cell_y)
    void (*del)(LandGrid *self)

class LandGrid:
    LandGridInterface *vt
    int x_cells, y_cells; # in cells 
    int cell_w, cell_h; # in pixels 

static import grid, log, tilegrid, isometric, sprite

static LandGrid *active_grid = 0

def land_grid_draw(LandGrid *self, LandView *view):
    self->vt->draw(self, view)

def land_grid_draw_grid(LandGrid *self, LandView *view):
    int i
    land_color(0, 0, 1, 0.5)

    float cx = view->scroll_x / self->cell_w
    float ox = cx - floor(cx)
    for i = 0; i < view->w / self->cell_w; i++:
        float x = view->x + (i + ox) * self->cell_w
        land_line(x, view->y, x, view->y + view->h)
        
    float cy = view->scroll_y / self->cell_h
    float oy = cy - floor(cy)
    for i = 0; i < view->h / self->cell_h; i++:
        float y = view->y + (i + oy) * self->cell_h
        land_line(view->x, y, view->x + view->w, y)

def land_grid_get_cell_at(LandGrid *self, LandView *view, float view_x, float view_y,
    float *cell_x, float *cell_y):
    self->vt->get_cell_at(self, view, view_x, view_y, cell_x, cell_y)

def land_grid_initialize(LandGrid *self, int cell_w, int cell_h, int x_cells, int y_cells):
    self->x_cells = x_cells
    self->y_cells = y_cells
    self->cell_w = cell_w
    self->cell_h = cell_h

    active_grid = self

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
    self->vt->del(self)
