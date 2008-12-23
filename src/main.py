import runner
static import global allegro, sys/time,
static import land
static import jpg

#ifndef LAND_NO_PNG
import global loadpng
#endif

#ifndef LAND_NO_TTF
import global fudgefont
#endif

class LandParameters:
    int w, h, bpp, hz
    int frequency
    int flags
    LandRunner *start

static int _synchronized
static int _maximize_fps
static double frequency
static LandParameters *parameters
static int quit
static volatile int ticks
static int frames
static int x_clicked
static int active
#ifndef ALLEGRO_WINDOWS
static struct timeval start_time
#else
    #FIXME
#endif

static def ticker():
    ticks++

static def closebutton():
    x_clicked++

static def land_exit():
    if not active: return
    active = 0
    land_free(parameters)
    land_log_message("land_exit\n")

def land_init():
    """Initialize Land. This must be called before anything else."""
    if active: return
    active = 1
    #ifndef ALLEGRO_WINDOWS
    gettimeofday(&start_time, NULL)
    #else
    #FIXME

    #endif

    land_log_message("land_init\n")
    land_alloc(parameters)
    parameters->w = 640
    parameters->h = 480
    parameters->frequency = 60

    atexit(land_exit)

    if not land_exception_handler:
        land_exception_handler_set(land_default_exception_handler)

    int seed = time(NULL)
    land_seed(seed)
    land_log_message("Random seed is %d.\n", seed)

    land_log_message("Compiled against Allegro %s.\n", ALLEGRO_VERSION_STR)

    if allegro_init():
        land_log_message("Allegro initialization failed: %s\n", allegro_error)
        land_exception("Error in allegro_init: %s", allegro_error)

    if install_timer():
        land_exception("Error in install_timer: %s", allegro_error)

    #ifndef LAND_NO_PNG
    _png_screen_gamma = 0
    loadpng_init()
    #endif

    register_bitmap_file_type("jpg", load_jpg, None)

    #ifndef LAND_NO_TTF
    install_fudgefont()
    fudgefont_set_kerning(true);
    #endif

static def land_tick():
    land_mouse_tick()
    land_runner_tick_active()
    land_keyboard_tick()

static def land_draw():
    land_runner_draw_active()
    land_flip()

def land_quit():
    """Quit the Land application. Call it when you want the program to exit."""
    quit = 1

int def land_closebutton():
    """Check if the closebutton has been clicked.
    
    * Returns: True if yes, else False.
    """
    int r = x_clicked
    x_clicked = 0
    return r

def land_set_frequency(int f):
    """Set the frequency in Hz at which Land should tick. Default is 60."""

    land_log_message("land_set_frequency %d\n", f)
    parameters->frequency = f

def land_set_display_parameters(int w, int h, int bpp, int hz, int flags):
    """Set the display parameters to use initially.
    * w, h Width and height in pixel.
    * bpp Color depth, 0 for auto.
    * hz Refresh rate, 0 for auto. Passing something besides 0 may be dangerous
    for the monitor, so usually pass 0 here.
    * flags, a combination of:
    ** LAND_WINDOWED
    ** LAND_FULLSCREEN
    ** LAND_OPENGL
    ** LAND_CLOSE_LINES
    """
    parameters->bpp = bpp
    parameters->hz = hz
    parameters->w = w
    parameters->h = h
    parameters->flags = flags

def land_set_initial_runner(LandRunner *runner):
    """Set the initial runner."""
    parameters->start = runner

double def land_get_frequency():
    """Return the current frequency."""
    return frequency

int def land_get_ticks():
    """Return the number of ticks Land has executed."""
    return ticks

double def land_get_time():
    """Get the time in seconds since Land has started."""
    #ifndef ALLEGRO_WINDOWS
    struct timeval tv
    gettimeofday(&tv, NULL)
    return ((tv.tv_sec - start_time.tv_sec) * 1000000.0 + tv.tv_usec) * 0.000001
    #else
    #FIXME
    return ticks / frequency
    #endif

int def land_get_flags():
    return parameters->flags

def land_set_synchronized(int onoff):
    _synchronized = onoff

def land_maximize_fps(int onoff):
    _maximize_fps = onoff

def land_skip_frames():
    """Skip any frames the logic may be behind. Usually, the tick function of
    a runner is called for each tick of Land. If a runner does not return from
    its tick method for some reason, then it can fall behind. For example if
    there is a function to load a lot of data from disk. In this case, it may
    be best to synchronize to the current ticks, and not catch up to the
    current time - this is when you would call this function."""
    frames = ticks

def land_main():
    """Run Land. This function will use all the parameters set before to
    initialize everything, then run the initial runner. It will return when
    you call land_quit() inside the tick function of the active runner.
    """
    land_log_message("land_main\n")
    
    land_exit_function(land_exit)

    land_display_init()
    land_font_init()
    land_image_init()
    land_grid_init()

    LandDisplay *display = land_display_new(parameters->w, parameters->h,
        parameters->bpp, parameters->hz, parameters->flags)

    land_display_set()

    set_close_button_callback(closebutton)
    
    if install_keyboard():
        land_exception("Error in install_keyboard: %s", allegro_error)
    if install_mouse() <= 0:
        land_exception("Error in install_mouse: %s", allegro_error)
    if install_sound(DIGI_AUTODETECT, MIDI_NONE, NULL):
        land_exception("Error in install_sound: %s", allegro_error)

    land_sound_init()

    land_mouse_init()
    land_keyboard_init()

    land_reprogram_timer()

    land_runner_switch_active(parameters->start)

    land_skip_frames()
    int gframes = frames
    while not quit:
        if _synchronized:
            land_tick()
            frames++
            land_draw()
        else:
            while frames <= ticks:
                # We must not poll keyboard or mouse here, since then Allegro
                # will activate polling mode.
                land_tick()
                frames++

            if gframes < frames or _maximize_fps:
                land_draw()
                gframes = frames
            else:
                rest(1)

    land_runner_switch_active(NULL)
    land_runner_destroy_all()
    
    land_display_destroy(display)

    land_sound_exit()
    land_grid_exit()
    land_font_exit()
    land_image_exit()
    land_display_exit()

    land_exit_functions()

    land_log_message("exit\n")

def land_reprogram_timer():
    frequency = parameters->frequency
    long altime = BPS_TO_TIMER(parameters->frequency)
    frequency = TIMERS_PER_SECOND / altime
    install_int_ex(ticker, altime)
