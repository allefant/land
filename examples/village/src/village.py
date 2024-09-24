import global land/land

LandImage *image

def _init(LandRunner *self):
    image = land_image_new(100, 100)
    # image = land_image_load("test.tga")
    land_set_image_display(image)
    int mx = 50
    int my = 50
    int r = 20
    land_clear(1, 1, 1, 1)
    land_color(0, 0, 0, 1)
    land_filled_circle(mx - r, my - r, mx + r, my + r)
    land_unset_image_display()

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape):
        land_quit()

def _draw(LandRunner *self):
    land_clear(0.2, 0.1, 0, 1)
    land_clip(0, 0, 50, 50)
    land_image_draw(image, 0, 0)

def _done: pass

land_standard_example()
