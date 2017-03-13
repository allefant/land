import global stdbool
import global land.util
static import log

import land/allegro5/a5_main

global macro LandJoystickButtonsCount 100
global macro LandJoystickAxesCount 100

static int button_state[LandJoystickButtonsCount]
static int button_pressed[LandJoystickButtonsCount]
static float axis[LandJoystickAxesCount]

def land_joystick_button_down_event(int button):
    if not button_state[button]:
        button_pressed[button]++
        button_state[button] = 1

def land_joystick_button_up_event(int button):
    button_state[button] = 0

def land_joystick_axis_event(int axis, float x):
    pass
    
def land_joystick_tick():
    int i
    for i = 0 while i < LandJoystickButtonsCount with i++:
        button_pressed[i] = 0

def joystick_button(int k) -> int:
    """
    Is the Joystick button down during this tick.
    """
    return button_state[k]

def land_joystick_pressed(int k) -> int:
    """
    How often was the joystick button pressed in this tick (almost
    always will be either 0 or 1, except you can press your button
    very fast).
    """
    return button_pressed[k]

def land_joystick_axis(int a) -> float:
    """
    The joystick axis position of the given axis.
    """
    return axis[a]

def land_joystick_button_name(int b) -> str:
    return platform_joystick_button_name(b)

def land_joystick_axis_name(int a) -> str:
    return platform_joystick_axis_name(a)
