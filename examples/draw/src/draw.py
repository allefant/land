import global land/land

static def game_tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

static float def hueclip(float hue, float pos):
    float a = LAND_PI / 3.0
    float wrap = (pos * a - hue + LAND_PI) / (2 * LAND_PI)
    wrap = (wrap - floor(wrap)) * 2 * LAND_PI - LAND_PI
    float x = 3.0 - fabs(wrap) / a
    x -= 1
    if x < 0:
        x = 0
    if x > 1:
        x = 1
    return x

static def hue_to_rgb(float hue, float *red, float *green, float *blue):
    *red = hueclip(hue, 0)
    *green = hueclip(hue, 2)
    *blue = hueclip(hue, 4)

static def draw_star(float middle_x, middle_y, int n, float r,
        start_angle, spike_length):
    float x, y
    float px, py, pa
    float a = start_angle
    float da = 2 * LAND_PI / n
    int i
    for i = 0 while i <= n with i++:
        float red, green, blue
        float r2 = r
        if i & 1:
            r2 += spike_length
        x = middle_x + r2 * sin(a)
        y = middle_y - r2 * cos(a)
        if i:
            hue_to_rgb(pa - start_angle, &red, &green, &blue)
            land_color(red, green, blue, 1)
            land_line(px, py, x, y)

        px = x
        py = y
        pa = a
        a += da


static def game_draw(LandRunner *self):

    land_clear(0, 0, 0, 1)

#     land_clip(land_mouse_x() - 100, land_mouse_y() - 100,
#         land_mouse_x() + 100, land_mouse_y() + 100)

    land_color(1, 0, 0, 1)
    land_line(10, 10, 14, 14)
    land_line(14, 14, 10, 18)
    land_line(10, 18, 6, 14)
    land_line(6, 14, 10, 10)

    land_color(1, 0, 0, 1)
    land_line(10.5, 20.5, 14.5, 24.5)
    land_line(14.5, 24.5, 10.5, 28.5)
    land_line(10.5, 28.5, 6.5, 24.5)
    land_line(6.5, 24.5, 10.5, 20.5)

    land_color(0, 1, 0, 1)

    land_line(20.5, 19.5, 20.5, 20.5)
    land_line(30.5, 19.5, 30.5, 20.5)
    land_line(19.5, 20.5, 20.5, 20.5)
    land_line(19.5, 30.5, 20.5, 30.5)

    land_color(1, 0, 0, 1)
    land_line(20.5, 20.5, 30.5, 20.5)
    land_line(30.5, 20.5, 30.5, 30.5)
    land_line(30.5, 30.5, 20.5, 30.5)
    land_line(20.5, 30.5, 20.5, 20.5)

    land_clip(21, 21, 30, 30)
    land_color(0.5, 0.5, 1, 1)
    land_line(21.5, 21.5, 29.5, 21.5)
    land_line(29.5, 21.5, 29.5, 29.5)
    land_line(29.5, 29.5, 21.5, 29.5)
    land_line(21.5, 29.5, 21.5, 21.5)

    land_clip(0, 0, land_display_width(), land_display_height())
    land_color(0, 1, 0, 1)

    land_line(20.5, 39.5, 20.5, 40.5)
    land_line(30.5, 39.5, 30.5, 40.5)
    land_line(19.5, 40.5, 20.5, 40.5)
    land_line(19.5, 50.5, 20.5, 50.5)

    land_color(1, 0, 0, 1)
    land_filled_rectangle(20, 40, 31, 51)

    land_clip(21, 41, 30, 50)
    land_color(0, 0, 1, 1)
    land_filled_rectangle(20, 40, 31, 51)

    land_clip(0, 0, land_display_width(), land_display_height())

    land_color(0.5, 0.5, 0.5, 0.5)

    static int t = 0
    int j
    for j = 0 while j < 9 with j++:
   
        int i
        for i = 3 while i < 15 with i++:
       
            draw_star(40.5 + (i - 3) * 50, 40.5 + j * 50, i * 2, 10,
                t * LAND_PI / 360.0, j)
       
        t++

    land_flip()

def begin():
    land_init()
    land_set_display_parameters(640, 480, LAND_WINDOWED | LAND_OPENGL)
    LandRunner *game_runner = land_runner_new("game", NULL, NULL, game_tick, game_draw, NULL, NULL)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(begin)
