import global land/land

LandMap *map
LandView *view

macro LAND_MAP_ISOMETRIC 1

static def land_create_map(int cw, int ch, int w, int h, int layers, int flags) -> LandMap *:
    LandMap *self = land_map_new()
    int l
    for l = 0 while l < layers with l++:
        LandLayer *layer = land_layer_new()
        if flags & LAND_MAP_ISOMETRIC:
            layer->grid = land_isometric_wrap_new(cw, ch, cw, ch, w, h)
        layer->x = 0
        layer->y = 0
        land_map_add_layer(self, layer)

    return self

def _init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 10)

    map = land_create_map(16, 16, 50, 50, 1, LAND_MAP_ISOMETRIC)

    view = land_view_new(50, 50, land_display_width() - 100, land_display_height() - 100)

def _done(LandRunner *self):
    pass

def _tick(LandRunner *self):
    int kx = 0, ky = 0
    if land_key(LandKeyEscape):
        land_quit()
    if land_key(LandKeyLeft):
        kx = -1
    if land_key(LandKeyRight):
        kx = 1
    if land_key(LandKeyUp):
        ky = -1
    if land_key(LandKeyDown):
        ky = 1

    if land_mouse_b() & 2:
        view->scroll_x -= land_mouse_delta_x()
        view->scroll_y -= land_mouse_delta_y()

    view->scroll_x += kx
    view->scroll_y += ky

def _draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_color(0, 0, 1, 1)
    land_rectangle(view->x - 1, view->y - 1, view->x + view->w, view->y + view->h)
    land_map_draw(map, view)

    land_text_pos(view->x, view->y)
    land_color(1, 1, 1, 1)
    float x, y
    land_grid_get_cell_at(map->first_layer->grid, view,
        land_mouse_x(), land_mouse_y(), &x, &y)
    land_print("%.2f / %.2f", x, y)

def _config(): land_default_display()
land_example(_config, _init, _tick, _draw, _done)
