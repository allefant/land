#ifdef _PROTOTYPE_
#include "runner.h"
#endif /* _PROTOTYPE_ */

#include <allegro.h>

#include "fudgefont.h"
#include "land.h"

land_type(LandParameters)
{
    int w, h, bpp, hz;
    int frequency;
    int flags;
    LandRunner *start;
};

static double frequency;
static LandParameters *parameters;
static int quit = 0;
static volatile int ticks = 0;
static int x_clicked = 0;
static void ticker(void)
{
    ticks++;
}

static void closebutton(void)
{
    x_clicked++;
}

void land_init(void)
{
    land_log_msg("land_init\n");
    parameters = calloc(1, sizeof *parameters);
    parameters->w = 640;
    parameters->h = 480;
    parameters->frequency = 60;

    if (!land_exception_handler)
        land_exception_handler_set(land_default_exception_handler);

    srand(time(NULL));

    if (allegro_init())
        land_exception("Error in allegro_init: %s", allegro_error);

    loadpng_init();
    install_fudgefont();
}

static void land_tick(void)
{
    land_mouse_tick();
    land_runner_tick_active();
    land_keyboard_tick();
}

static void land_draw(void)
{
    land_runner_draw_active();
    land_flip();
}

static void land_exit(void)
{
    land_log_msg("land_exit\n");
}

void land_quit(void)
{
    quit = 1;
}

int land_closebutton(void)
{
    int r = x_clicked;
    x_clicked = 0;
    return r;
}

void land_set_frequency(int f)
{
    land_log_msg("land_set_frequency %d\n", f);
    parameters->frequency = f;
}

void land_set_display_parameters(int w, int h, int bpp, int hz, int flags)
{
    parameters->bpp = bpp;
    parameters->hz = hz;
    parameters->w = w;
    parameters->h = h;
    parameters->flags = flags;

}

void land_set_initial_runner(LandRunner *runner)
{
    parameters->start = runner;
}

double land_get_frequency(void)
{
    return frequency;
}

int land_get_ticks(void)
{
    return ticks;
}

double land_get_time(void)
{
    return ticks / frequency;
}

int land_get_flags(void)
{
    return parameters->flags;
}

int land_main(void)
{
    land_log_msg("land_main\n");
    if (install_keyboard())
        land_exception("Error in install_keyboard: %s", allegro_error);
    if (install_mouse() <= 0)
        land_exception("Error in install_mouse: %s", allegro_error);
    if (install_timer())
        land_exception("Error in install_timer: %s", allegro_error);
    if (install_sound(DIGI_AUTODETECT, MIDI_NONE, NULL))
        land_exception("Error in install_sound: %s", allegro_error);

    land_display_init();
    land_font_init();
    land_image_init();
    land_grid_init();

    land_display_new(parameters->w, parameters->h,
        parameters->bpp, parameters->hz, parameters->flags);

    land_display_set();

    set_close_button_callback(closebutton);

    land_mouse_init();
    land_keyboard_init();

    frequency = parameters->frequency;
    long altime = BPS_TO_TIMER(parameters->frequency);
    frequency = TIMERS_PER_SECOND / altime;
    install_int_ex(ticker, altime);

    land_runner_init_all();

    land_runner_switch_active(parameters->start);

    int frames = ticks;
    int gframes = frames;
    while (!quit)
    {
        while (frames <= ticks)
        {
            land_tick();
            frames++;
        }
        if (gframes < frames)
        {
            land_draw();
            gframes = frames;
        }
        else
        {
            rest(1);
        }
    }
    land_runner_switch_active(NULL);
    land_runner_destroy_all();
    land_exit();
    return 0;
}

