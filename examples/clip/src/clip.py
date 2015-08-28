import global land/land

LandImage *image

static def game_init(LandRunner *self):
    image = land_image_new(16, 16)
    land_set_image_display(image)
    land_clear(0.5, 0.5, 0.5, 1)
    land_color(1, 1, 0, 1)
    land_line(0, 0, 16, 16)
    land_unset_image_display()
    
    #glEnable(GL_POLYGON_SMOOTH)

static def game_tick(LandRunner *self):
    if land_key(LandKeyEscape) or land_closebutton():
        land_quit()

static def game_draw(LandRunner *self):
    land_clip(0, 0, 640, 480)
    land_color(1, 1, 0, 1)
    land_filled_rectangle(0, 0, 640, 480)
    land_color(0.5, 0.5, 0.5, 1)
    land_filled_rectangle(1, 1, 639, 479)
    
    # Going from left to right, the clip position is shifted to the right from 8
    # (exact middle) to 9.5.
    # Going top to bottom, the image itself is shifted to the right from 0 to
    # 1.5.
    int i, j
    for j = 0 while j < 15 with j++:
        for i = 0 while i < 15 with i++:
            float x = 2 + i * 20
            float y = 2 + j * 20
            float clip = x + 8 + i * 0.5
            x += j * 0.5
            land_clip(clip, 0, 640, 480)
            land_image_draw_tinted(image, x, y, 1, 0, 0, 0.8)
            land_clip(0, 0, clip, 480)
            land_image_draw_tinted(image, x, y, 0, 1, 0, 0.8)

land_begin_shortcut(640, 480, 120, LAND_WINDOWED | LAND_OPENGL,
    game_init, NULL, game_tick, game_draw, NULL, NULL)
