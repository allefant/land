import global land/land

LandImage *image
float angle = 0

def _init(LandRunner *self):
    image = land_image_new(100, 100); 
    land_image_center(image)
    land_set_image_display(image)
    land_blend(LAND_BLEND_SOLID)
    int mx = 50
    int my = 50
    int r = 50
    land_clear(1, 0, 0, 0)
    land_color(1, 1, 1, 1)
    land_filled_circle(mx - r, my - r, mx + r, my + r)
    land_color(0, 0, 0, 0)
    r = 20
    land_filled_circle(mx - r, my - r, mx + r, my + r)
    land_unset_image_display()

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape):
        land_quit()
    angle += 0.1

    land_set_image_display(image)
    land_blend(LAND_BLEND_SOLID)
    land_color(0, 0, 0, 0)
    int x = land_rand(0, 99)
    int y = land_rand(0, 99)
    int r = land_rand(0, 2)
    land_filled_circle(x - r, y - r, x + r, y + r)
    land_unset_image_display()

def _draw(LandRunner *self):
    land_clear(0.2, 0.1, 0, 1)
    int x = 320
    int y = 240
    float t = sqrt(50 * 50 + 50 * 50)
    float s = 50
    land_image_draw_scaled_rotated(image, x - s, y - s, 1, 1, angle)
    land_image_draw_scaled_rotated(image, x - s, y + s, 1, 1, angle)
    land_image_draw_scaled_rotated(image, x + s, y - s, 1, 1, angle)
    land_image_draw_scaled_rotated(image, x + s, y + s, 1, 1, angle)
    land_image_draw_scaled_rotated(image, x - t, y, 1, 1, -angle)
    land_image_draw_scaled_rotated(image, x + t, y, 1, 1, -angle)
    land_image_draw_scaled_rotated(image, x, y - t, 1, 1, -angle)
    land_image_draw_scaled_rotated(image, x, y + t, 1, 1, -angle)
    land_image_draw_scaled_rotated(image, x, y, 1, 1, angle)

def _done(LandRunner *self):
    land_image_destroy(image)

def _config:
    land_set_display_parameters(640, 480, LAND_OPENGL | LAND_WINDOWED)
    land_set_fps(100)
land_example(_config, _init, _tick, _draw, _done)
