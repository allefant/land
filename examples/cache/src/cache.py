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
    if land_key_pressed(LandKeyEscape):
        land_quit()

    if land_key(LandKeyLeft):
        angle--
        cached = 0

    if land_key(LandKeyLeft):
        angle++
        cached = 0

double def periodic(double x, w):
    x /= w
    x -= floor(x)
    x *= w
    return x

def paint(int x, y, w, h, xp, yp, tw, th):
    # Paint pretty background. 
    int i, j
    int mx = tw / 2
    int my = th / 2
    for j = yp; j < yp + h; j++:
        for i = xp; i < xp + w; i++:
            float a = atan2(j - my, i - mx)
            float d = sqrt((i - mx) * (i - mx) + (j - my) * (j - my))
            float hue = angle + 3 * a * 180 / LAND_PI
            hue = periodic(hue, 360)
            float sat = pow(1.0 - 1 / (1 + d * 0.05), 5)
            LandColor c = land_color_hsv(hue, sat, 1)
            land_color(c.r, c.g, c.b, 1)
            land_plot(x + i - xp + 0.5, y + j - yp + 0.5)

def draw(LandRunner *self):
    if not cached:
        int i, j
        for i = 0; i < 1024; i += 256:
            for j = 0; j < 1024; j += 256:
                paint(0, 0, 256, 256, i, j, 1024, 1024)
                land_image_grab_into(cache, 0, 0, i, j, 256, 256)

        #land_image_save(cache, "test.png")
        #paint(0, 0, 1024, 1024, 0, 0, 1024, 1024)
        cached = 1
        land_image_center(cache)

    land_image_draw_scaled_rotated(cache, 320, 240,
        0.9 + 0.1 * sin(land_get_time()),
        0.9 + 0.1 * sin(land_get_time()),
        land_get_time() * (1 + 4 * fabs(sin(land_get_time() * 0.2))))
    #land_clear(1, 0.9, 0.8, 1)
    #land_image_draw(cache, 0, 0)

    # if not cached:
    #    land_clear(0, 0, 1, 1)
    #    land_image_draw(bitmap, 0, 0)
    #    land_image_grab_into(cache, 0, 0, 0, 0, 200, 200)
    #    cached = 1
    #land_clear(1, 0, 0, 1)
    #land_image_draw(cache, 0, 0)

land_begin_shortcut(640, 480, 0, 60, LAND_OPENGL | LAND_FULLSCREEN,
    init, NULL, tick, draw, NULL, NULL)
