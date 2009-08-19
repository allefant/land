import global land/land

LandImage *image

static def init(LandRunner *self):
    image = land_image_load(land_argv[1])

static def tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

static def draw(LandRunner *self):
    land_clear(0, 0, 0, 0)
    land_image_draw(image, 0, 0)

land_begin_shortcut(1024, 768, 60, LAND_WINDOWED | LAND_OPENGL,
    init, None, tick, draw, None, None)
