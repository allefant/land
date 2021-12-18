import global land/land

LandMap *map
LandView *view
int wrap, clip
LandImage *tile
LandImage *tiles[8]
LandGridIsometric *iso
int gridselection = 1

static def draw(LandGrid *self, LandView *view, int cell_x, cell_y, float x, y):
    land_image_draw_scaled(tile, x - iso->cell_w1 * view.scale_x,
        y, view.scale_x, view.scale_y)
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

    iso = (void *)land_isometric_custom_grid(32, 16, 32, 16, 30, 30, wrap, draw)
    layer->grid = (void *)iso

    land_map_add_layer(map, layer)

static def game_init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 20)
    tiles[0] = land_image_load("../../data/isotile1.png")
    tiles[1] = land_image_load("../../data/isotile2.png")
    tiles[2] = land_image_load("../../data/isotile3.png")
    tiles[3] = land_image_load("../../data/isotile4.png")
    tiles[4] = land_image_load("../../data/isotile5.png")
    tile = tiles[0]

    restart()

    view = land_view_new(100, 100, land_display_width() - 200, land_display_height() - 200)

static def game_tick(LandRunner *self):
    int kx = 0, ky = 0
    while not land_keybuffer_empty():
        int k, u
        land_keybuffer_next(&k, &u)
        if u == '+':
            land_view_scale(view, 1.1, 1.1)
        if u == '-':
            land_view_scale(view, 1/1.1, 1/1.1)
        
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
    if land_key_pressed(LandKeyFunction + 1):
        wrap ^= 1
        restart()
    if land_key_pressed(LandKeyFunction + 2):
        int i = gridselection++
        if gridselection == 5: gridselection = 0
        float grids[][4] = {
            {32, 16, 32, 16},
            {32, 16, 64, 32},
            {64, 32, 32, 16},
            {8, 24, 24, 8},
            {24, 8, 8, 24},
            }
        iso->cell_w1 = grids[i][0]
        iso->cell_h1 = grids[i][1]
        iso->cell_w2 = grids[i][2]
        iso->cell_h2 = grids[i][3]
        tile = tiles[i]
    if land_key_pressed(LandKeyFunction + 3):
        clip ^= 1

    if land_mouse_b() & 2:
        view->scroll_x -= land_mouse_delta_x()
        view->scroll_y -= land_mouse_delta_y()

    view->scroll_x += kx
    view->scroll_y += ky

static def game_draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    if clip:
        land_clip(view->x, view->y, view->x + view->w, view->y + view->h)
    land_map_draw(map, view)
    land_color(0, 0, 1, 0.5)
    land_rectangle(view->x - 1, view->y - 1, view->x + view->w, view->y + view->h)

    if clip: land_unclip()

    land_text_pos(0, 0)
    land_color(1, 0, 0, 1)
    float x, y
    land_grid_pixel_to_cell_isometric(map->first_layer->grid, view,
        land_mouse_x(), land_mouse_y(), &x, &y)
    land_print("%.2f / %.2f", x, y)

static def game_exit(LandRunner *self):
    pass

land_begin_shortcut(640, 480, 120,
    LAND_WINDOWED | LAND_OPENGL,
    game_init, NULL, game_tick, game_draw, NULL, game_exit)

