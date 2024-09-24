import global land/land

class Game:
    float t

Game *game

def _init:
    land_alloc(game)

def _done:
    land_free(game)

def _tick:
    if land_key(LandKeyEscape):
        land_quit()
    game->t += 1.0 / land_get_fps()

def _draw:
    land_clear(0, 0, 0, 1)

    float w = land_display_width()
    float h = land_display_height()
    float x = w / 2
    float y = h / 2
    float r = 100 * fabs(sin(game->t))

    land_color(0, 0.25, 0, 1)
    land_line(x, 0, x, h)
    land_line(0, y, w, y)
    
    land_color(0, 0, 1, 1)
    land_filled_circle(x - r, y - r, x + r, y + r)

    land_color(1, 1, 0, 1)
    land_filled_circle(0, 0, 8, 8)
    land_filled_circle(w - 8, 0, w, 8)
    land_filled_circle(w - 8, h - 8, w, h)
    land_filled_circle(0, h - 8, 8, h)

land_standard_example()
