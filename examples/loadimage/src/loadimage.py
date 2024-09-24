import global land/land

LandImage *image

def _init(LandRunner *self):
    if land_argc == 2:
        image = land_image_load(land_argv[1])

def _tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

def _draw(LandRunner *self):
    land_clear(0, 0, 0, 0)
    if image: land_image_draw(image, 0, 0)

def _done:
    if image: land_image_destroy(image)

land_standard_example()
