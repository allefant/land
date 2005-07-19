#include <land/land.h>

LandMap *map;
LandView *my_view;

static int sprites, sprites_count;

land_type(MySprite)
{
    LandSprite super;
    int id;
};

static void sprite_drawer(MySprite *self, LandView *view)
{
    float x = self->super.x + self->super.type->x - view->scroll_x + view->x;
    float y = self->super.y + self->super.type->y - view->scroll_y + view->y;
    land_color(1, 0, 0);
    land_rectangle(x, y, x + self->super.type->w,
        y + self->super.type->h);
    land_text_color(1, 1, 1, 1);
    land_text_pos(x + 1, y + 1);
    land_print("%d", self->id);

    sprites++;
}

static void game_init(void)
{
    map = land_map_new();

    LandLayer *layer = land_layer_new();
    layer->x = 0;
    layer->y = 0;

    layer->grid = land_sprites_grid_new(128, 128, 1000, 1000);

    land_map_add_layer(map, layer);

    my_view = land_view_new(0, 0, land_display_width(), land_display_height());

    LandSpriteType *spritetype = land_spritetype_new();
    spritetype->draw = (void *)sprite_drawer;
    spritetype->x = 0;
    spritetype->y = 0;
    spritetype->w = 40;
    spritetype->h = 40;

    sprites_count = layer->grid->x_cells * layer->grid->y_cells;

    int i;
    for (i = 0; i < sprites_count; i++)
    {
        float x = rand() % (layer->grid->x_cells * layer->grid->cell_w);
        float y = rand() % (layer->grid->y_cells * layer->grid->cell_h);
        MySprite *sprite;
        land_alloc(sprite);
        land_sprite_initialize(&sprite->super, spritetype);
        sprite->id = i;

        land_sprite_place_into_grid(&sprite->super, layer->grid, x, y);
    }

    land_load_font("../../data/galaxy.ttf", 10);
}

static void game_tick(void)
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
        my_view->scroll_x -= land_mouse_delta_x();
        my_view->scroll_y -= land_mouse_delta_y();
    }

    my_view->scroll_x += kx;
    my_view->scroll_y += ky;
}

static void game_draw(void)
{
    sprites = 0;
    land_clear(0, 0, 0);
    land_color(0, 0, 1);
    land_rectangle(my_view->x - 1, my_view->y - 1, my_view->x + my_view->w,
        my_view->y + my_view->h);
    land_map_draw(map, my_view);
    land_text_pos(0, 0);
    land_text_color(1, 1, 1, 1);
    land_print("%d/%d sprites visible", sprites, sprites_count);
}

static void game_exit(void)
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

