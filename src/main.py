import runner

static import global sys/time
static import land

typedef double LandFloat

class LandParameters:
    int w, h
    int fps
    int flags
    LandRunner *start

static import allegro5/a5_main

static bool land_active
global bool _land_quit
static LandParameters *parameters
static bool x_clicked
static int ticks
global int _land_frames
global bool _land_synchronized
static bool _maximize_fps

static def land_exit():
    if not land_active: return
    land_active = False
    land_free(parameters)
    land_log_message("land_exit\n")

def land_init():
    """Initialize Land. This must be called before anything else."""
    if land_active: return
    land_active = True

    land_log_message("land_init\n")
    land_alloc(parameters)
    parameters->w = 640
    parameters->h = 480
    parameters->fps = 60

    atexit(land_exit)

    if not land_exception_handler:
        land_exception_handler_set(land_default_exception_handler)

    int seed = time(NULL)
    land_seed(seed)
    land_log_message("Random seed is %d.\n", seed)

    char cd[1024]
    if not getcwd(cd, sizeof cd):
        sprintf(cd, "<none>")
    land_log_message("Current path: %s\n", cd)

    platform_init()

def land_tick():
    land_display_tick()
    land_runner_tick_active()
    land_mouse_tick()
    land_keyboard_tick()
    ticks++
    x_clicked = False

def land_draw():
    land_runner_draw_active()
    land_flip()

def land_quit():
    """
    Quit the Land application. Call it when you want the program to
    exit.
    """
    _land_quit = True

def land_closebutton_event():
    x_clicked = True

int def land_closebutton():
    """Check if the closebutton has been clicked.
    * Returns: True if yes, else False.
    """
    return x_clicked

def land_set_fps(int f):
    """Set the frequency in Hz at which Land should tick. Default is 60."""

    land_log_message("land_set_frequency %d\n", f)
    parameters->fps = f

def land_set_display_parameters(int w, int h, int flags):
    """Set the display parameters to use initially.
    * w, h Width and height in pixel.
    * flags, a combination of:
    ** LAND_WINDOWED
    ** LAND_FULLSCREEN
    ** LAND_OPENGL
    ** LAND_CLOSE_LINES
    """
    parameters->w = w
    parameters->h = h
    parameters->flags = flags

def land_set_initial_runner(LandRunner *runner):
    """Set the initial runner."""
    parameters->start = runner

double def land_get_fps():
    """Return the current frequency."""
    return parameters->fps

int def land_get_ticks():
    """Return the number of ticks Land has executed."""
    return _land_frames

double def land_get_time():
    """Get the time in seconds since Land has started."""
    return platform_get_time()

int def land_get_flags():
    return parameters->flags

def land_set_synchronized(bool onoff):
    _land_synchronized = onoff

def land_maximize_fps(bool onoff):
    _maximize_fps = onoff

def land_skip_frames():
    """Skip any frames the logic may be behind. Usually, the tick function of
    a runner is called for each tick of Land. If a runner does not return from
    its tick method for some reason, then it can fall behind. For example if
    there is a function to load a lot of data from disk. In this case, it may
    be best to synchronize to the current ticks, and not catch up to the
    current time - this is when you would call this function."""
    _land_frames = ticks

def land_mainloop():
    """Run Land. This function will use all the parameters set before to
    initialize everything, then run the initial runner. It will return when
    you call land_quit() inside the tick function of the active runner.
    """
    land_log_message("land_mainloop\n")

    land_exit_function(land_exit)

    land_display_init()
    land_font_init()
    land_image_init()
    land_grid_init()

    LandDisplay *display = land_display_new(parameters->w,
        parameters->h, parameters->flags)

    land_log_message("About to create the main window.\n")
    land_display_set()
    land_log_message("Video initialized.\n")
    land_sound_init()
    land_log_message("Audio initialized.\n")

    land_mouse_init()
    land_log_message("Mouse initialized.\n")
    land_keyboard_init()
    land_log_message("Keyboard initialized.\n")

    land_runner_switch_active(parameters->start)

    land_log_message("Commencing operations.\n")
    platform_mainloop(parameters)

    land_runner_switch_active(None)
    land_runner_destroy_all()

    land_display_destroy(display)

    land_sound_exit()
    land_grid_exit()
    land_font_exit()
    land_image_exit()
    land_display_exit()

    land_exit_functions()

    land_log_message("exit\n")
