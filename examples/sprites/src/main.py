import global land/land

LandMap *map
LandView *my_view

static int sprites, sprites_count

class MySprite:
    LandSprite super
    int id

static def sprite_drawer(MySprite *self, LandView *view):
    LandSprite *s = &self->super
    float x = (s->x + s->type->x - view->scroll_x) * view->scale_x + view->x
    float y = (s->y + s->type->y - view->scroll_y) * view->scale_y + view->y
    land_color(1, 0, 0, 1)
    land_rectangle(x, y, x + self->super.type->w * view->scale_x,
        y + self->super.type->h * view->scale_y)
    if view->scale_x > 0.10:
        land_color(1, 1, 1, 1)
        land_text_pos(x + 1, y + 1)
        land_print("%d", self->id)

    sprites++

static def game_init(LandRunner *self):
    map = land_map_new()

    LandLayer *layer = land_layer_new()
    layer->x = 0
    layer->y = 0

    layer->grid = land_sprites_grid_new(128, 128, 1000, 1000)

    land_map_add_layer(map, layer)

    my_view = land_view_new(0, 10, land_display_width(),
        land_display_height() - 10)

    LandSpriteType *spritetype = land_spritetype_new()
    spritetype->draw = (void *)sprite_drawer
    spritetype->x = 0
    spritetype->y = 0
    spritetype->w = 40
    spritetype->h = 40

    sprites_count = layer->grid->x_cells * layer->grid->y_cells

    int i
    for i = 0 while i < sprites_count with i++:
        float x = rand() % (layer->grid->x_cells * layer->grid->cell_w)
        float y = rand() % (layer->grid->y_cells * layer->grid->cell_h)
        MySprite *sprite
        land_alloc(sprite)
        land_sprite_initialize(&sprite->super, spritetype)
        sprite->id = i

        land_sprite_place_into_grid(&sprite->super, layer->grid, x, y)

    land_font_load("../../data/galaxy.ttf", 10)

static def game_tick(LandRunner *self):
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
    if land_key(LandKeyHome):
        land_view_scroll_to(my_view, 0, 0)

    int z = land_mouse_delta_z()
    if z > 0:
        land_view_scale(my_view, 1 / 0.9, 1 / 0.9)
    if z < 0:
        land_view_scale(my_view, 0.9, 0.9)

    if land_mouse_b() & 2:
        my_view->scroll_x -= land_mouse_delta_x() / my_view->scale_x
        my_view->scroll_y -= land_mouse_delta_y() / my_view->scale_y

    my_view->scroll_x += kx / my_view->scale_x
    my_view->scroll_y += ky / my_view->scale_y

static def game_draw(LandRunner *self):
    sprites = 0
    land_clear(0, 0, 0, 0)
    land_color(0, 0, 1, 1)
    land_rectangle(my_view->x + 0.5, my_view->y + 0.5,
        my_view->x + my_view->w - 0.5, my_view->y + my_view->h - 0.5)
    land_view_clip(my_view)
    land_map_draw(map, my_view)
    land_unclip()
    land_text_pos(0, 0)
    land_color(1, 1, 1, 1)
    land_print("%d/%d sprites visible", sprites, sprites_count)

static def game_exit(LandRunner *self):
    pass

def begin():
    land_init()
    land_set_display_parameters(640, 480, LAND_WINDOWED | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("game",
        game_init, NULL, game_tick, game_draw, NULL, game_exit)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(begin)
