import global land/land

class Game:
    LandImage *img1
    LandImage *img2

    float angle
    float x, y, x_, y_

Game game

static def game_init(LandRunner *self):
    land_font_load("../../data/galaxy.ttf", 10)

    game.img1 = land_image_new(40, 40)
    land_image_center(game.img1)

    game.img2 = land_image_new(100, 100)
    land_image_center(game.img2)

    land_set_image_display(game.img1)
    float w = 40, h = 40
    land_clear(0, 0, 0, 0)
    land_color(1, 0, 0, 1)
    float x = w / 2
    float y = h / 2
    land_line(x, 0, x, y)
    land_line(x, y, 0, h)
    land_line(x, y, w, h)
    land_unset_image_display()

    land_set_image_display(game.img2)
    w = 100, h = 100
    land_clear(0, 0, 0, 0)
    land_color(1, 0, 0, 1)
    land_line(0, 0, w, h)
    land_unset_image_display()

    land_image_create_pixelmasks(game.img1, 256, 128)
    land_image_create_pixelmasks(game.img2, 1, 128)

    game.x_ = land_display_width() / 2 + 100
    game.y_ = land_display_height() / 2

    game.x = land_mouse_x()
    game.y = land_mouse_y()

static def game_tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape):
        land_quit()

    float dx = land_mouse_x() - game.x
    float dy = land_mouse_y() - game.y
    float d = sqrtf(dx * dx + dy * dy)

    float dmax = d
    if dmax > 10:
        dmax = 10

    int kx = 0, ky = 0
    if land_key(LandKeyLeft):
        kx = 1
    if land_key(LandKeyRight):
        kx = -1

    float da = 0.1 * kx

    int overlaps = 0

    float f, x, y
    for f = 0.5 while f < dmax with f++:
        x = game.x + dx / d
        y = game.y + dy / d
        overlaps = land_image_overlaps(game.img1, x, y, game.angle,
            game.img2, game.x_, game.y_, 0)
        if not overlaps:
            game.x = x
            game.y = y

        else:
            break

    float a = game.angle + da
    overlaps = land_image_overlaps(game.img1, game.x, game.y, a,
        game.img2, game.x_, game.y_, 0)
    if not overlaps:
        game.angle = a


static def game_draw(LandRunner *self):
    land_clear(0.5, 0.5, 0.5, 1)
    land_image_draw_rotated(game.img1, (int)game.x, (int)game.y, game.angle)
    land_image_draw(game.img2, game.x_, game.y_)

    #land_color(0, 1, 0, 0.5)
    #land_image_debug_pixelmask(game.img1, (int)game.x, (int)game.y, game.angle)
    #land_image_debug_pixelmask(game.img2, (int)game.x_, (int)game.y_, 0)

    land_text_pos(0, 0)
    land_color(1, 1, 1, 1)
    land_print("Collision")

static def game_exit(LandRunner *self):
    pass

land_begin_shortcut(640, 480, 60, LAND_WINDOWED | LAND_OPENGL,
    game_init, NULL, game_tick, game_draw, NULL, game_exit)
