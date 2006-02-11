#include <land.h>

LandImage *image;

void init(LandRunner *self)
{

    image = land_image_new(100, 100);
    //image = land_image_load("test.tga");
    land_set_image_display(image);
    int mx = 50;
    int my = 50;
    int r = 20;
    land_clear(1, 1, 1, 1);
    land_color(0, 0, 0, 1);
    land_filled_circle(mx - r, my - r, mx + r, my + r);
    land_unset_image_display();

}

void tick(LandRunner *self)
{
    if (land_key_pressed(KEY_ESC))
        land_quit();
}

void draw(LandRunner *self)
{
    land_clear(0.2, 0.1, 0, 1);
    land_clip(0, 0, 50, 50);
    land_image_draw(image, 0, 0);
}

int main(void)
{
    land_init();
    LandRunner *runner = land_runner_new("Village", init, NULL, tick, draw, NULL, NULL);
    land_runner_register(runner);
    land_set_initial_runner(runner);
    land_set_display_parameters(640, 480, 32, 100, LAND_OPENGL | LAND_WINDOWED);
    land_set_frequency(100);
    land_main();
    return 0;
}
