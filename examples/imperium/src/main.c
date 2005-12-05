#include <land.h>

LandMap *map;
LandView *view;

#define LAND_MAP_ISOMETRIC 1

static LandMap *land_create_map(int cw, int ch, int w, int h, int layers, int flags)
{
    LandMap *self = land_map_new();
    int l;
    for (l = 0; l < layers; l++)
    {
        LandLayer *layer = land_layer_new();
        if (flags & LAND_MAP_ISOMETRIC)
            layer->grid = land_isometric_wrap_new(cw, ch, w, h);
        layer->x = 0;
        layer->y = 0;
        land_map_add_layer(self, layer);
    }
    return self;
}

static void game_init(LandRunner *self)
{
    land_load_font("../../data/galaxy.ttf", 10);

    map = land_create_map(16, 16, 50, 50, 1, LAND_MAP_ISOMETRIC);

    view = land_view_new(50, 50, land_display_width() - 100, land_display_height() - 100);
}

static void game_tick(LandRunner *self)
{
    int kx = 0, ky = 0;
    if (land_key(KEY_ESC))
        land_quit();
    if (land_key(KEY_LEFT))
        kx = -1;
    if (land_key(KEY_RIGHT))
        kx = 1;
    if (land_key(KEY_UP))
        ky = -1;
    if (land_key(KEY_DOWN))
        ky = 1;

    if (land_mouse_b() & 2)
    {
        view->scroll_x -= land_mouse_delta_x();
        view->scroll_y -= land_mouse_delta_y();
    }

    view->scroll_x += kx;
    view->scroll_y += ky;
}

static void game_draw(LandRunner *self)
{
    land_clear(0, 0, 0);
    land_color(0, 0, 1);
    land_rectangle(view->x - 1, view->y - 1, view->x + view->w, view->y + view->h);
    land_map_draw(map, view);

    land_text_pos(view->x, view->y);
    land_text_color(1, 1, 1, 1);
    float x, y;
    land_grid_get_cell_at(map->first_layer->grid, view,
        land_mouse_x(), land_mouse_y(), &x, &y);
    land_print("%.2f / %.2f", x, y);
}

static void game_exit(LandRunner *self)
{
}

land_begin()
{
    land_init();
    land_set_display_parameters(640, 480, 32, 120, LAND_WINDOWED | LAND_OPENGL);
    LandRunner *game_runner = land_runner_register("game",
        game_init, NULL, game_tick, game_draw, NULL, game_exit);
    land_set_initial_runner(game_runner);
    land_main();
}

