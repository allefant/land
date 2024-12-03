import global land/land

LandImage *image1, *image2
LandFont *font

def _init(LandRunner *self):
    font = land_create_builtin_font(16)
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

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

def _draw(LandRunner *self):
    land_font_set(font)
    land_clear(0, 0, 1, 1)
    land_image_draw(image1, 0, 0)
    land_image_draw(image2, 100, 0)
    land_image_draw_scaled(image2, 100, 100, 6, 6)
    land_image_draw_scaled(image2, 600, 100, 6, 6)
    land_color(1, 1, 1, 1)
    land_text_pos(100, 80)
    land_print("original")
    land_text_pos(600, 80)
    land_print("copy")

def _done: pass

land_standard_example()
