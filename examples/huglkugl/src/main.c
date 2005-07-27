#include <land/land.h>

LandImage *player_image;
LandImage *platform_image;

LandSpriteType *player_type;
LandSpriteType *platform_type;

typedef struct Game Game;
struct Game
{
    LandMap *map;
    LandLayer *back_layer;
    LandLayer *front_layer;
    LandGrid *back_grid;
    LandGrid *front_grid;
    LandView *view;
};

Game game;

LandSprite *sprites[100];

static void player_type_draw(LandSprite *sprite, LandView *view)
{
    float x = sprite->x + sprite->type->x - view->scroll_x + view->x;
    float y = sprite->y + sprite->type->y - view->scroll_y + view->y;
    land_image_draw(player_image, x, y);
}

static void platform_type_draw(LandSprite *sprite, LandView *view)
{
    float x = sprite->x + sprite->type->x - view->scroll_x + view->x;
    float y = sprite->y + sprite->type->y - view->scroll_y + view->y;
    land_image_draw(platform_image, x, y);
}

static void game_init(void)
{
    game.map = land_map_new();
    game.back_layer = land_layer_new();
    game.front_layer = land_layer_new();
    land_map_add_layer(game.map, game.back_layer);
    land_map_add_layer(game.map, game.front_layer);

    game.back_grid = game.back_layer->grid = land_sprites_grid_new(64, 64, 16, 16);
    game.front_grid = game.front_layer->grid = land_sprites_grid_new(64, 64, 16, 16);

    game.view = land_view_new(-64, -64, land_display_width() + 128,
        land_display_height() + 128);

    player_type = land_spritetype_new();
    player_type->draw = player_type_draw;

    platform_type = land_spritetype_new();
    platform_type->draw = platform_type_draw;

    player_image = land_image_load("../../data/huglkugl.png");
    land_image_center(player_image);
    platform_image = land_image_load("../../data/platform1.png");
    land_image_center(platform_image);

    sprites[0] = land_sprite_new(player_type);
    land_sprite_place_into_grid(sprites[0], game.front_grid, 0, 0);

    int i;
    int x = 64;
    for (i = 1; i < 9; i++) {
        sprites[i] = land_sprite_new(platform_type);
        land_sprite_place_into_grid(sprites[i], game.back_grid, x, 100);
        x += 128;
    }
}

static void game_tick(void)
{
    if (land_key_pressed(KEY_ESC)) land_quit();

    int kx = 0, ky = 0;
    if (land_key(KEY_LEFT)) kx = -1;
    if (land_key(KEY_RIGHT)) kx = 1;
    if (land_key(KEY_UP)) ky = -1;
    if (land_key(KEY_DOWN)) ky = 1;

    land_sprite_move(sprites[0], game.front_grid, kx * 3, ky * 3);

    land_view_ensure_visible(game.view, sprites[0]->x, sprites[0]->y, 140, 140);
}

static void game_draw(void)
{
    land_clear(0, 0, 0);
    land_map_draw(game.map, game.view);
}

static void game_exit(void)
{
}

land_begin_shortcut(640, 480, 32, 60, LAND_OPENGL | LAND_WINDOWED,
    game_init, NULL, game_tick, game_draw, NULL, game_exit);
