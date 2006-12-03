import global land

LandMap *map
LandView *view
int wrap
LandImage *tile

static def draw(LandGrid *self, LandView *view, int cell_x, cell_y, float x, y):
    land_image_draw(tile, x - 32, y)
    land_color(0, 0, 0, 1)
    land_text_pos(x, y + 4)
    if cell_x == 0 and cell_y == 0:
        land_print("0")
    elif cell_x == 0:
        land_print("y")
    elif cell_y == 0:
        land_print("x")

static def restart():
    if map:
        land_map_del(map)

    map = land_map_new()

    LandLayer *layer = land_layer_new()
    layer->x = 0
    layer->y = 0

    layer->grid = land_isometric_custom_grid(64, 32, 50, 50, wrap, draw)

    land_map_add_layer(map, layer)

static def game_init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 20)
    tile = land_image_load("../../data/isotile.png")

    restart()

    view = land_view_new(50, 50, land_display_width() - 100, land_display_height() - 100)

static def game_tick(LandRunner *self):
    int kx = 0, ky = 0
    if land_key(KEY_ESC):
        land_quit()
    if land_key(KEY_LEFT):
        kx = -1
    if land_key(KEY_RIGHT):
        kx = 1
    if land_key(KEY_UP):
        ky = -1
    if land_key(KEY_DOWN):
        ky = 1
    if land_key_pressed(KEY_F1):
        wrap ^= 1
        restart()

    if land_mouse_b() & 2:
        view->scroll_x -= land_mouse_delta_x()
        view->scroll_y -= land_mouse_delta_y()

    view->scroll_x += kx
    view->scroll_y += ky

static def game_draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_map_draw(map, view)
    land_color(0, 0, 1, 0.5)
    land_rectangle(view->x - 1, view->y - 1, view->x + view->w, view->y + view->h)

    land_text_pos(view->x, view->y)
    land_color(1, 0, 0, 1)
    float x, y
    land_grid_pixel_to_cell_isometric(map->first_layer->grid, view,
        land_mouse_x(), land_mouse_y(), &x, &y)
    land_print("%.2f / %.2f", x, y)

static def game_exit(LandRunner *self):
    pass

land_begin_shortcut(640, 480, 32, 120,
    LAND_WINDOWED | LAND_OPENGL,
    game_init, NULL, game_tick, game_draw, NULL, game_exit)

