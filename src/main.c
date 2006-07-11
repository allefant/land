#ifdef _PROTOTYPE_
#include "runner.h"
#endif /* _PROTOTYPE_ */

#include <allegro.h>
#include <sys/time.h>
#include <loadpng.h>
#include <jpgalleg.h>

#include "fudgefont.h"
#include "land.h"

typedef struct LandParameters LandParameters;
struct LandParameters
{
    int w, h, bpp, hz;
    int frequency;
    int flags;
    LandRunner *start;
};

static int _synchronized = 0;
static int _maximize_fps = 0;
static double frequency;
static LandParameters *parameters;
static int quit = 0;
static volatile int ticks = 0;
static int frames = 0;
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
    land_alloc(parameters);
    parameters->w = 640;
    parameters->h = 480;
    parameters->frequency = 60;

    if (!land_exception_handler)
        land_exception_handler_set(land_default_exception_handler);

    land_seed(time(NULL));

    if (allegro_init())
        land_exception("Error in allegro_init: %s", allegro_error);

    _png_screen_gamma = 0;
    loadpng_init();
    jpgalleg_init();

    install_fudgefont();
}

static void land_exit(void)
{
    land_free(parameters);
    land_log_msg("land_exit\n");
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

/* Get the time in seconds. */
double land_get_time(void)
{
#ifndef ALLEGRO_WINDOWS
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec * 1000000.0 + tv.tv_usec) * 0.000001;
#else
    // FIXME
    return ticks / frequency;
#endif
}

int land_get_flags(void)
{
    return parameters->flags;
}

void land_set_synchronized(int onoff)
{
    _synchronized = onoff;
}

void land_maximize_fps(int onoff)
{
    _maximize_fps = onoff;
}

void land_skip_frames(void)
{
    frames = ticks;
}

int land_main(void)
{
    land_log_msg("land_main\n");

    land_display_init();
    land_font_init();
    land_image_init();
    land_grid_init();

    LandDisplay *display = land_display_new(parameters->w, parameters->h,
        parameters->bpp, parameters->hz, parameters->flags);

    land_display_set();

    set_close_button_callback(closebutton);
    
    if (install_keyboard())
        land_exception("Error in install_keyboard: %s", allegro_error);
    if (install_mouse() <= 0)
        land_exception("Error in install_mouse: %s", allegro_error);
    if (install_timer())
        land_exception("Error in install_timer: %s", allegro_error);
    if (install_sound(DIGI_AUTODETECT, MIDI_NONE, NULL))
        land_exception("Error in install_sound: %s", allegro_error);

    land_mouse_init();
    land_keyboard_init();

    land_reprogram_timer();

    land_runner_switch_active(parameters->start);

    land_skip_frames();
    int gframes = frames;
    while (!quit)
    {
        if (_synchronized)
        {
            land_tick();
            frames++;
            land_draw();
        }
        else
        {
            while (frames <= ticks)
            {
                poll_keyboard(); /* just in case */
                land_tick();
                frames++;
            }
            if (gframes < frames || _maximize_fps)
            {
                land_draw();
                gframes = frames;
            }
            else
            {
                rest(1);
            }
        }
    }
    land_runner_switch_active(NULL);
    land_runner_destroy_all();
    
    land_display_destroy(display);
    
    land_grid_exit();
    land_font_exit();
    land_image_exit();
    land_display_exit();

    land_exit();

    land_log_msg("exit");
    return 0;
}

void land_reprogram_timer(void)
{
    frequency = parameters->frequency;
    long altime = BPS_TO_TIMER(parameters->frequency);
    frequency = TIMERS_PER_SECOND / altime;
    install_int_ex(ticker, altime);
}
