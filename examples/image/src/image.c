#include <land/land.h>

LandImage *image;

static LandImage *create_test_image(void)
{
    int w = 100;
    int h = 100;
    image = land_image_new(w, h);
    int i;
    for (i = 0; i < w * h; i++)
    {
        int x = i % w;
        int y = i / w;
        int red, green, blue;
        red = MAX(0, 255 - x - y);
        green = MAX(0, x - y);
        blue = MAX(0, y - x);
        int b;
        for (b = 1; b < 8; b++)
        {
            int mask = (1 << b) - 1;
            if (((x & mask) == mask) && y < mask)
            {
                blue = 0;
                green = 255;
                red = 255;
            }

            if (((y & mask) == mask) && x < mask)
            {
                blue = 255;
                green = 0;
                red = 255;
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
                blue = 255;
                green = 255;
                red = 0;
            }
        }
        putpixel(image->memory_cache, x, y, makeacol(red, green, blue, 255));
    }
    image->vt->prepare(image);
    return image;
}

static void init(LandRunner *self)
{
    //image = create_test_image();
    image = land_image_load("../../data/land2.png");
    //image = create_test_image();
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

    land_clear(0.2, 0, 0);
    land_color(1, 1, 1);
    land_rectangle(10 - 0.5, 10 - 0.5, 10 + land_image_width(image) + 0.5,
        10 + land_image_height(image) + 0.5);
    land_rectangle(8 - 0.5, 8 - 0.5, 12 + land_image_width(image) + 0.5,
        12 + land_image_height(image) + 0.5);
    land_image_draw(image, 10, 10);

    land_image_draw_rotated(image, 480, 160, angle);

    float sx = cos(angle + AL_PI / 4) * 1.5;
    float sy = sin(angle + AL_PI / 4) * 1.5;
    land_image_draw_scaled(image, 480, 320, sx, sy);

    LandImage *image_parts[4];
    image_parts[0] = land_image_new_from(image, 0, 0, w / 2, h / 2);
    image_parts[1] = land_image_new_from(image, w / 2, 0, w / 2, h / 2);
    image_parts[2] = land_image_new_from(image, w / 2, h / 2, w / 2, h / 2);
    image_parts[3] = land_image_new_from(image, 0, h / 2, w / 2, h / 2);
    float s = (cos(angle * 3) + 1) * 10;
    land_image_draw(image_parts[0], 40 - s, 240 - s);
    land_image_draw(image_parts[1], 40 + w / 2 + s, 240 - s);
    land_image_draw(image_parts[2], 40 + w / 2 + s, 240 + h / 2 + s);
    land_image_draw(image_parts[3], 40 - s, 240 + h / 2 + s);
    int i;
    for (i = 0; i < 4; i++)
        land_image_del(image_parts[i]);

    angle += 1.0 * AL_PI / 180.0;
    angle /= AL_PI * 2;
    angle -= floor(angle);
    angle *= AL_PI * 2;
}

land_begin_shortcut(640, 480, 0, 60, LAND_OPENGL | LAND_WINDOWED,
    init, NULL, tick, draw, NULL, NULL);
