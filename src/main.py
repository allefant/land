import runner
static import global allegro, sys/time, loadpng, jpgalleg, fudgefont
static import land

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
static struct timeval start_time

static def ticker():
    ticks++

static def closebutton():
    x_clicked++

def land_init():
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

    if not land_exception_handler:
        land_exception_handler_set(land_default_exception_handler)

    land_seed(time(NULL))

    if allegro_init():
        land_exception("Error in allegro_init: %s", allegro_error)

    _png_screen_gamma = 0
    loadpng_init()
    jpgalleg_init()

    install_fudgefont()

static def land_exit():
    land_free(parameters)
    land_log_message("land_exit\n")

static def land_tick():
    land_mouse_tick()
    land_runner_tick_active()
    land_keyboard_tick()

static def land_draw():
    land_runner_draw_active()
    land_flip()

def land_quit():
    quit = 1

int def land_closebutton():
    int r = x_clicked
    x_clicked = 0
    return r

def land_set_frequency(int f):
    land_log_message("land_set_frequency %d\n", f)
    parameters->frequency = f

def land_set_display_parameters(int w, int h, int bpp, int hz, int flags):
    parameters->bpp = bpp
    parameters->hz = hz
    parameters->w = w
    parameters->h = h
    parameters->flags = flags

def land_set_initial_runner(LandRunner *runner):
    parameters->start = runner

double def land_get_frequency():
    return frequency

int def land_get_ticks():
    return ticks

# Get the time in seconds. 
double def land_get_time():
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
    frames = ticks

int def land_main():
    land_log_message("land_main\n")

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
    if install_timer():
        land_exception("Error in install_timer: %s", allegro_error)
    if install_sound(DIGI_AUTODETECT, MIDI_NONE, NULL):
        land_exception("Error in install_sound: %s", allegro_error)

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
    
    land_grid_exit()
    land_font_exit()
    land_image_exit()
    land_display_exit()

    land_exit()

    land_log_message("exit\n")
    return 0

def land_reprogram_timer():
    frequency = parameters->frequency
    long altime = BPS_TO_TIMER(parameters->frequency)
    frequency = TIMERS_PER_SECOND / altime
    install_int_ex(ticker, altime)
