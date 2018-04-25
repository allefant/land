import global stdbool
import global land.util
static import log
static import land.allegro5.a5_joystick
import land/allegro5/a5_main

global macro LandJoystickButtonsCount 100
global macro LandJoystickAxesCount 100

static int button_state[LandJoystickButtonsCount]
static int button_pressed[LandJoystickButtonsCount]
static float axis[LandJoystickAxesCount]
static float oaxis[LandJoystickAxesCount]

def land_joystick_button_down_event(int button):
    if not button_state[button]:
        button_pressed[button]++
        button_state[button] = 1

def land_joystick_button_up_event(int button):
    button_state[button] = 0

def land_joystick_axis_event(int a, float x):
    axis[a] = x
    
def land_joystick_tick():
    int bn = land_joystick_button_count()
    for int i in range(1, bn):
        button_pressed[i] = 0
    int an = land_joystick_axis_count()
    for int i in range(1, an):
        oaxis[i] = axis[i]

def land_joystick_button(int button) -> int:
    """
    Is the Joystick button down during this tick. The button is a number
    between 1 inclusive and land_joystick_button_count() exclusive.
    """
    return button_state[button]

def land_joystick_button_pressed(int button) -> int:
    """
    How often was the joystick button pressed in this tick (almost
    always will be either 0 or 1, except you can press your button
    very fast).
    """
    return button_pressed[button]

def land_joystick_axis(int a) -> float:
    """
    The joystick axis position of the given axis. The axis is a number
    between 1 inclusive and land_joystick_axis_count() exclusive.
    """
    return axis[a]

def land_joystick_delta_axis(int a) -> float:
    return axis[a] - oaxis[a]

def land_joystick_button_name(int b) -> str:
    return platform_joystick_button_name(b)

def land_joystick_axis_name(int a) -> str:
    return platform_joystick_axis_name(a)

def land_joystick_button_count -> int: return platform_joystick_button_count()
def land_joystick_axis_count -> int: return platform_joystick_axis_count()

def land_joystick_find_axis(str name) -> int:
    int an = land_joystick_axis_count()
    for int ai in range(1, an):
        str axis = land_joystick_axis_name(ai)
        if land_equals(axis, name):
                return ai
    return 0

def land_joystick_find_button(str name) -> int:
    int bn = land_joystick_button_count()
    for int bi in range(1, bn):
        str button = land_joystick_button_name(bi)
        if land_equals(button, name):
            return bi
    return 0

def land_joystick_debug:
    int an = land_joystick_axis_count()
    for int ai in range(1, an):
        float v = land_joystick_axis(ai)
        if v: printf("%s: %f\n", land_joystick_axis_name(ai), v)
    int bn = land_joystick_button_count()
    for int bi in range(1, bn)
        int v = land_joystick_button_pressed(bi)
        if v: printf("%s: %d\n", land_joystick_button_name(bi), v)
