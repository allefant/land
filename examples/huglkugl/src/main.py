import global land/land

LandImage *player_image
LandImage *platform_image

LandSpriteType *player_type
LandSpriteType *platform_type

class Game:
    LandMap *map
    LandLayer *back_layer # for level 
    LandLayer *front_layer # for sprites 
    LandGrid *back_grid
    LandGrid *front_grid
    LandView *view

Game game

LandSprite *sprites[100]

def _init(LandRunner *self):
    land_font_load("../../data/Muli-Regular.ttf", 12)

    game.map = land_map_new()
    game.back_layer = land_layer_new()
    game.front_layer = land_layer_new()
    land_map_add_layer(game.map, game.back_layer)
    land_map_add_layer(game.map, game.front_layer)

    game.back_grid = game.back_layer->grid = land_sprites_grid_new(64, 64, 16, 16)
    game.front_grid = game.front_layer->grid = land_sprites_grid_new(64, 64, 16, 16)

    game.view = land_view_new(-64, -64, land_display_width() + 128,
        land_display_height() + 128)

    player_image = land_image_load("../../data/huglkugl.png")
    land_image_center(player_image)
    platform_image = land_image_load("../../data/platform1.png")
    land_image_center(platform_image)

    player_type = land_spritetype_image_new(player_image, True, -1)
    platform_type = land_spritetype_image_new(platform_image, True, 1)

    sprites[0] = land_sprite_new(player_type)
    land_sprite_place_into_grid(sprites[0], game.front_grid, 0, 0)

    int i
    int x = 64
    for i = 1 while i < 9 with i++:
        sprites[i] = land_sprite_new(platform_type)
        land_sprite_place_into_grid(sprites[i], game.back_grid, x, 100)
        x += 128


def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape): land_quit()

    int kx = 0, ky = 0
    if land_key(LandKeyLeft): kx = -1
    if land_key(LandKeyRight): kx = 1
    if land_key(LandKeyUp): ky = -1
    if land_key(LandKeyDown): ky = 1
    
    if kx == -1: sprites[0]->flipped = True
    if kx == 1: sprites[0]->flipped = False

    land_sprite_move(sprites[0], game.front_grid, kx * 3, ky * 3)

    land_view_ensure_visible(game.view, sprites[0]->x, sprites[0]->y, 140, 140)

def _draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_map_draw(game.map, game.view)

    LandList *overlappers = land_sprites_grid_overlap(sprites[0], game.back_grid)
    land_color(1, 0, 0, 1)
    land_text_pos(0, 0)
    land_print("Overlap:")
    if overlappers:
        LandListItem *item = overlappers->first

        while item:
            land_print("%p", item->data)
            item = item->next

        land_list_destroy(overlappers)


def _done(LandRunner *self):
    pass

def _config(): land_default_display()
land_example(_config, _init, _tick, _draw, _done)
