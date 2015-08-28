import global land/land

LandImage *image1, *image2

float angle = 0

def init(LandRunner *self):
    image1 = land_image_new(64, 64)
    land_set_image_display(image1)
    land_clear(1, 1, 1, 1)
    land_color(0, 0, 0, 1)
    land_line(0, 0, 64, 64)
    land_unset_image_display()
    #land_image_save(image1, "image1.png")

    image2 = land_image_create(64, 64)
    land_set_image_display(image2)
    land_image_draw(image1, 0, 0)
    land_unset_image_display()
    #land_image_save(image2, "image2.png")

def tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

def draw(LandRunner *self):
    land_image_draw(image1, 0, 0)
    land_image_draw(image2, 100, 0)

land_begin_shortcut(640, 480, 60, LAND_OPENGL | LAND_WINDOWED,
    init, NULL, tick, draw, NULL, NULL)
