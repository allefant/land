#include <land/land.h>

LandImage *image;
LandImage *image_parts[4];

static LandImage *create_test_image(void)
{
    int w = 100;
    int h = 100;
    image = land_image_new(w, h);
    int i;
    land_set_image_display(image);
    for (i = 0; i < w * h; i++)
    {
        int x = i % w;
        int y = i / w;
        float red, green, blue;
        red = MAX(0, 1 - (float)x / w - (float)y / h);
        green = MAX(0, (float)x / w - (float)y / h);
        blue = MAX(0, (float)y / h - (float)x / w);
        int b;
        for (b = 1; b < 8; b++)
        {
            int mask = (1 << b) - 1;
            if (((x & mask) == mask) && y < mask)
            {
                blue = 0;
                green = 1;
                red = 1;
            }

            if (((y & mask) == mask) && x < mask)
            {
                blue = 1;
                green = 0;
                red = 1;
            }
        }
        if (x >= w / 2 && y >= h / 2)
        {
            int ix = w * 3 / 4 - x;
            int iy = h * 3 / 4 - y;
            if (ix <= 0)
                ix--;
            if (iy <= 0)
                iy--;
            int iz = MAX(abs(ix), abs(iy));
            if ((iz & 3) == 0)
            {
                blue = 1;
                green = 1;
                red = 0;
            }
        }
        land_color(red, green, blue, 1);
        land_plot(x, y);
    }
    land_unset_image_display();
    return image;
}

static void init(LandRunner *self)
{
    image = create_test_image();
    image = land_image_load("../../data/land3.png");
    land_image_offset(image, 20, 12);

    int w = land_image_width(image);
    int h = land_image_height(image);

    image_parts[0] = land_image_new_from(image, 0, 0, w / 2, h / 2);
    image_parts[1] = land_image_new_from(image, w / 2, 0, w / 2, h / 2);
    image_parts[2] = land_image_new_from(image, w / 2, h / 2, w / 2, h / 2);
    image_parts[3] = land_image_new_from(image, 0, h / 2, w / 2, h / 2);
}

static void destroy(LandRunner *self)
{
    int i;
    for (i = 0; i < 4; i++)
        land_image_del(image_parts[i]);
    land_image_del(image);
}

static void tick(LandRunner *self)
{
    if (land_key(KEY_ESC))
        land_quit();
}

static void draw(LandRunner *self)
{
    static float angle = 0;
    int w = land_image_width(image);
    int h = land_image_height(image);

    static int clip_switch = 0;
    clip_switch++;

    if (clip_switch % 60 == 0)
    {
        if ((clip_switch / 60) & 1)
        {
            int cw = land_rand(w / 2, w);
            int ch = land_rand(h / 2, h);
            int cx = land_rand(0, w - cw);
            int cy = land_rand(0, h - ch);
            land_image_clip(image, cx, cy, cx + cw, cy + ch);
        }
        else
            land_image_unclip(image);
    }


    land_clear(0.2, 0, 0, 0);
    land_color(1, 1, 1, 1);
    land_rectangle(10 - 0.5, 10 - 0.5, 10 + land_image_width(image) + 0.5,
        10 + land_image_height(image) + 0.5);
    land_rectangle(8 - 0.5, 8 - 0.5, 12 + land_image_width(image) + 0.5,
        12 + land_image_height(image) + 0.5);

    land_image_draw(image, 10, 10);

    land_image_draw_rotated(image, 480, 160, angle);
    land_color(0, 1, 0, 1);
    land_filled_circle(480 - 2, 160 - 2, 480 + 2, 160 + 2);

    float sx = cos(angle + AL_PI / 4) * 1.5;
    float sy = sin(angle + AL_PI / 4) * 1.5;
    land_image_draw_scaled_rotated(image, 480, 320, sx, sy, -sin(angle));
    land_color(0, 1, 0, 1);
    land_filled_circle(480 - 2, 320 - 2, 480 + 2, 320 + 2);

    float s = (cos(angle * 3) + 1) * 10;
    land_image_draw(image_parts[0], 40 - s, 240 - s);
    land_image_draw(image_parts[1], 40 + w / 2 + s, 240 - s);
    land_image_draw(image_parts[2], 40 + w / 2 + s, 240 + h / 2 + s);
    land_image_draw(image_parts[3], 40 - s, 240 + h / 2 + s);

    angle += 1.0 * AL_PI / 180.0;
    angle /= AL_PI * 2;
    angle -= floor(angle);
    angle *= AL_PI * 2;

}

land_begin_shortcut(640, 480, 0, 60, LAND_WINDOWED | LAND_OPENGL,
    init, NULL, tick, draw, NULL, destroy);
