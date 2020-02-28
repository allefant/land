import land.common
import runner

static import global sys/time
static import land

class LandParameters:
    int w, h
    int fps
    int flags
    int skip # how many render frames to skip (saves battery)
    LandRunner *start

static import allegro5/a5_main

static bool land_active
global bool _land_quit
static LandParameters *parameters
global bool _land_halted
global bool _land_was_halted

static bool x_clicked
global int _land_frames
global bool _land_synchronized
static bool _maximize_fps
static int skip_counter
int _flip_count
int _flips_at_tick[256]
int _flip_tick_i

static def land_exit():
    if not land_active: return
    land_active = False
    land_free(parameters)
    land_log_message("land_exit\n")

def land_halt:
    platform_halt()
    _land_halted = True

def land_resume:
    platform_resume()
    _land_halted = False

def land_was_halted -> bool:
    return _land_halted

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
    land_joystick_tick()
    x_clicked = False
    _land_was_halted = _land_halted
    _flip_tick_i--
    if _flip_tick_i < 0: _flip_tick_i = 255
    _flips_at_tick[_flip_tick_i] = _flip_count

def land_draw():
    if parameters.skip:
        skip_counter++
        if skip_counter <= parameters.skip:
            return
        skip_counter = 0
    land_runner_draw_active()
    _flip_count++
    land_flip()

def land_quit():
    """
    Quit the Land application. Call it when you want the program to
    exit.
    """
    _land_quit = True

def land_closebutton_event():
    x_clicked = True

def land_closebutton() -> int:
    """Check if the closebutton has been clicked.
    * Returns: True if yes, else False.
    """
    return x_clicked

def land_set_fps(int f):
    """Set the frequency in Hz at which Land should tick. Default is 60."""

    land_log_message("land_set_frequency %d\n", f)
    parameters->fps = f

def land_skip_render(int skip):
    parameters.skip = skip

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

def land_get_fps() -> double:
    """Return the current frequency."""
    return parameters->fps

def land_get_current_fps -> int:
    # _flips_at_tick[0] will always be identical to _flip_count during a tick
    int i = (_flip_tick_i + parameters.fps) % 256
    return _flip_count - _flips_at_tick[i]

def land_get_ticks() -> int:
    """Return the number of ticks Land has executed."""
    return _land_frames

def land_get_flips -> int:
    return _flip_count

def land_get_time() -> double:
    """Get the time in seconds since Land has started."""
    return platform_get_time()

def land_pause:
    """Stop time. The tick function of the current runner will not be
    called any longer and [land_get_ticks] will not advance until the
    next call to [land_unpause].
    """
    platform_pause()

def land_unpause:
    platform_unpause()

def land_get_flags() -> int:
    return parameters->flags

def land_set_synchronized(bool onoff):
    _land_synchronized = onoff

def land_maximize_fps(bool onoff):
    _maximize_fps = onoff

def land_mainloop_prepare:
    land_exit_function(land_exit)

    land_display_init()
    land_font_init()
    land_image_init()
    land_grid_init()

def land_mainloop():
    """Run Land. This function will use all the parameters set before to
    initialize everything, then run the initial runner. It will return when
    you call land_quit() inside the tick function of the active runner.
    """
    land_log_message("land_mainloop\n")

    land_mainloop_prepare()

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
    land_log_message("Ceasing operations.\n")

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
