import global land/land

int cached = 0
LandImage *cache
#LandImage *bitmap

float angle = 0

def init(LandRunner *self):
    cache = land_image_new(1024, 1024)
    #cache = land_image_new(640, 480);
    #bitmap = land_image_load("../../data/test.png")

def tick(LandRunner *self):
    if land_key_pressed(KEY_ESC):
        land_quit()

    if land_key(KEY_LEFT):
        angle--
        cached = 0

    if land_key(KEY_RIGHT):
        angle++
        cached = 0

def paint(int x, int y, int w, int h, int tw, int th):
    # Paint pretty background. 
    int i, j
    int mx = tw / 2
    int my = th / 2
    for i = y; i < y + h; i++:
        for j = x; j < x + w; j++:
            int r, g, b
            float a = atan2(j - mx, i - my)
            float d = sqrt((j - mx) * (j - mx) + (i - my) * (i - my))
            hsv_to_rgb(angle + 3 * a * 180 / AL_PI, pow(1.0 - 1 / (1 + d * 0.05), 5), 1, &r, &g, &b)
            land_color(r / 255.0, g / 255.0, b / 255.0, 1)
            land_plot(j - x, i - y)

def draw(LandRunner *self):
    if not cached:
        int i, j
        for i = 0; i < 1024; i += 256:
            for j = 0; j < 1024; j += 256:
                paint(j, i, 256, 256, 1024, 1024)
                land_image_grab_into(cache, 0, 0, j, i, 256, 256)


        # paint(0, 0, 640, 480, 640, 480)
        cached = 1
        land_image_center(cache)

    land_image_draw_scaled_rotated(cache, 320, 240,
        0.9 + 0.1 * sin(land_get_time()),
        0.9 + 0.1 * sin(land_get_time()),
        land_get_time() * (1 + 4 * fabs(sin(land_get_time() * 0.2))))

    # if not cached:
    #    land_clear(0, 0, 1, 1)
    #    land_image_draw(bitmap, 0, 0)
    #    land_image_grab_into(cache, 0, 0, 0, 0, 200, 200)
    #    cached = 1
    #land_clear(1, 0, 0, 1)
    #land_image_draw(cache, 0, 0)

land_begin_shortcut(640, 480, 0, 200, LAND_OPENGL |  LAND_FULLSCREEN,
    init, NULL, tick, draw, NULL, NULL)
