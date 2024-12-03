import global land/land

LandImage *image1
LandFont *font

def _init(LandRunner *self):
    font = land_create_builtin_font(16)
    land_find_data_prefix("data/")
    image1 = land_image_load("huglkugl.png")
    land_image_offset(image1, 11, 62)

def _tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

def land_mark(int x, y, kind):
    if kind == 0:
        land_color(0, 1, 0, 1)
        land_line(x, y - 5, x, y + 5)
        land_line(x - 5, y, x + 5, y)
    if kind == 1:
        land_color(1, 0, 0, 1)
        land_circle(x - 5, y - 5, x + 5, y + 5)

def _draw(LandRunner *self):
    land_font_set(font)
    land_clear(0, 0, 1, 1)
    
    land_image_draw(image1, 100, 100)
    land_mark(100, 100 , 0)
    land_mark(100 - 11, 100 - 62, 1)
    
    land_image_draw_flipped(image1, 300, 100)
    land_mark(300, 100 , 0)
    land_mark(300 + 11, 100 - 62, 1)
    
    land_image_draw_scaled_rotated_tinted_flipped(image1, 500, 100, 1, 1, 0, 1, 1, 1, 1, 2)
    land_mark(500, 100 , 0)
    land_mark(500 - 11, 100 + 62, 1)
    
    land_image_draw_scaled_rotated_tinted_flipped(image1, 700, 100, 1, 1, 0, 1, 1, 1, 1, 3)
    land_mark(700, 100 , 0)
    land_mark(700 + 11, 100 + 62, 1)
    
    land_image_draw_scaled(image1, 100, 600, 6, 6)
    land_mark(100, 600 , 0)
    land_image_draw_scaled_rotated_tinted_flipped(image1, 900, 600, 6, 6, 0, 1, 1, 1, 1, 1)
    land_mark(900, 600 , 0)
    land_image_draw_scaled_rotated_tinted_flipped(image1, 100, 700, 6, 6, 0, 1, 1, 1, 1, 2)
    land_mark(100, 700 , 0)
    land_image_draw_scaled_rotated_tinted_flipped(image1, 900, 700, 6, 6, 0, 1, 1, 1, 1, 3)
    land_mark(900, 700 , 0)
    land_color(1, 1, 1, 1)
    land_text_pos(100, 650)
    land_print("original")
    land_text_pos(500, 650)
    land_print("flipped")

def _done: pass

land_standard_example()
