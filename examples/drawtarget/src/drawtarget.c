#include <land.h>

LandImage *image;
float angle = 0;

void init(LandRunner *self)
{

    image = land_image_new(100, 100); 
    land_image_center(image);
    land_set_image_display(image);
    int mx = 50;
    int my = 50;
    int r = 50;
    land_clear(0, 0, 0, 0);
    land_color(1, 1, 1, 1);
    land_filled_circle(mx - r, my - r, mx + r, my + r);
    land_color(0, 0, 0, 1);
    r = 20;
    land_filled_circle(mx - r, my - r, mx + r, my + r);
    land_unset_image_display();

}

void tick(LandRunner *self)
{
    if (land_key_pressed(KEY_ESC))
        land_quit();
    angle += 0.1;

    land_set_image_display(image);
    land_color(0, 0, 0, 0);
    int x = land_rand(0, 99);
    int y = land_rand(0, 99);
    int r = land_rand(0, 2);
    land_filled_circle(x - r, y - r, x + r, y + r);
    land_unset_image_display();
}

void draw(LandRunner *self)
{
    land_clear(0.2, 0.1, 0, 1);
    int x = 320;
    int y = 240;
    float t = sqrt(50 * 50 + 50 * 50);
    float s = 50;
    land_image_draw_scaled_rotated(image, x - s, y - s, 1, 1, angle);
    land_image_draw_scaled_rotated(image, x - s, y + s, 1, 1, angle);
    land_image_draw_scaled_rotated(image, x + s, y - s, 1, 1, angle);
    land_image_draw_scaled_rotated(image, x + s, y + s, 1, 1, angle);
    land_image_draw_scaled_rotated(image, x - t, y, 1, 1, -angle);
    land_image_draw_scaled_rotated(image, x + t, y, 1, 1, -angle);
    land_image_draw_scaled_rotated(image, x, y - t, 1, 1, -angle);
    land_image_draw_scaled_rotated(image, x, y + t, 1, 1, -angle);
    land_image_draw_scaled_rotated(image, x, y, 1, 1, angle);
}

void done(LandRunner *self)
{
    land_image_destroy(image);
}

int main(void)
{
    land_init();
    LandRunner *runner = land_runner_new("Draw Target", init, NULL, tick, draw, NULL, done);
    land_runner_register(runner);
    land_set_initial_runner(runner);
    land_set_display_parameters(640, 480, 32, 100, LAND_OPENGL | LAND_WINDOWED);
    land_set_frequency(100);
    land_main();
    return 0;
}
