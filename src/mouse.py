"""
0 is the left mouse button
1 is the right mouse button
2 is the middle mouse button
3,4,... are extra mouse buttons

A button is either pressed or not. And it either changed since the
last time or not. The old API gives us 4 possibilities:

00 not pressed and was not
01 just pressed (was not in last tick)
10 just released (not pressed but was last tick)
11 being held down

However, this will not work with clicks that happen "between" two ticks:

tick     0          1          2          3          4
mouse       D          U  D  U    D   U         

In the above case the 4 ticks will have:
1: 01 (just pressed, correct)
2: 10 (just released) Completely ignores the click in between
3: 00 (nothing) Completely ignores the click
4: 00

There is no good way to solve this with this API. If clicks are detected
as 01 (react as soon as pressed) then we should return this:
1: 01
2: 01 (there was a click after all)
3: 01 (same)
4: 10

This would capture all 3 clicks but would see only one if they are
detected as 10.

If clicks are detected as 10 (react when the button is released):
1: 01 (so no click yet)
2: 10 (we lose the really fast click, which would still be fine)
3: 10 (there was a click)
4: 00

This would capture 2 of the 3 clicks (which is fine, we can never detect
more than one click per tick). But it would only detect one click if
detected as 01.

Both of those solutions also make it so the previous tick state could
differ from the actual one, possibly messing up drag&drop code and so
on if not prepared for it.

One stop-gap measure we do employ is if there is just one fast click
with no click before, we create both a fake 01 and fake 10.

tick     0          1          2          3          4
                        D   U

1: 00
2: 01 (fake, but not really)
3: 10 (to go with it)
4: 00 
"""
import global stdbool
static import exception, land/allegro5/a5_main
static import global assert

static int mx, my, mz
static int omx, omy, omz
static int buttons[5], obuttons[5]
int _clicks[5] # how often was the button pressed down
int _releases[5] # how often was the button released
static float tx[11], ty[11], tb[11], otb[11]

enum LandMouseButtons:
    LandButtonLeft
    LandButtonRight
    LandButtonMiddle

def land_mouse_init():
    land_show_mouse_cursor()

def land_mouse_tick():
    omx = mx
    omy = my
    omz = mz

    for int i = 0 while i < 5 with i++:
        # handle clicks and fake clicks :(
        if buttons[i] == 0:
            obuttons[i] = 0
        elif buttons[i] == 1:
            obuttons[i] = 1
        elif buttons[i] == 2:
            obuttons[i] = 0
            buttons[i] = 0
        elif buttons[i] == 3:
            obuttons[i] = 1
            buttons[i] = 1
        elif buttons[i] == 7:
            obuttons[i] = 1
            buttons[i] = 0
        _clicks[i] = 0
        _releases[i] = 0

    for int i in range(11):
        otb[i] = tb[i]

def land_mouse_move_event(int x, int y, int z):
    mx = x
    my = y
    mz = z

def land_touch_event(float x, y, int n, d):
    if n > 10:
        return
    tx[n] = x
    ty[n] = y
    if d == 1:
        tb[n] = True
    if d == -1:
        tb[n] = False

def land_touch_x(int n) -> float:
    if n > 10:
        return 0
    return tx[n]

def land_touch_y(int n) -> float:
    if n > 10:
        return 0
    return ty[n]

def land_touch_down(int n) -> bool:
    if n > 10:
        return False
    return tb[n]

def land_touch_delta(int n) -> bool:
    if n > 10:
        return False
    return otb[n] != tb[n]

def land_mouse_button_down_event(int b):
    # Note: buttons[] loses fast clicks, i.e. down and up event
    _clicks[b]++
    buttons[b] |= 1 + 2

def land_mouse_button_up_event(int b):
    _releases[b]++
    buttons[b] &= ~1
    if obuttons[b] == 0 and buttons[b] == 2:
        # we "lost" a click and there was no click in the previous tick
        buttons[b] = 7 # fake click

def land_mouse_x() -> int:
    """Return the mouse X coordinate for the current tick."""
    return mx

def land_mouse_y() -> int:
    """Return the mouse Y coordinate for the current tick."""
    return my

def land_mouse_z() -> int:
    """Return the mouse wheel coordinate for the current tick."""
    return mz

# deprecated, will lose short clicks
def land_mouse_b() -> int:
    """deprecated"""
    int mb = 0
    for int i in range(5):
        if land_mouse_button(i):
            mb |= 1 << i
    return mb

# deprecated, will lose short clicks
def land_mouse_button(int i) -> int:
    """Return the mouse button state for the current tick."""
    return buttons[i] & 1

def land_mouse_delta_x() -> int:
    return mx - omx

def land_mouse_delta_y() -> int:
    return my - omy

def land_mouse_delta_z() -> int:
    return mz - omz

# deprecated, will lose short clicks
def land_mouse_delta_b() -> int:
    """deprecated"""
    int mb = 0
    for int i in range(5):
        if land_mouse_delta_button(i):
            mb |= 1 << i
    return mb

# deprecated, will lose short clicks
def land_mouse_delta_button(int i) -> int:
    return (buttons[i] & 1) ^ (obuttons[i] & 1)

def land_mouse_button_clicked(int i) -> int:
    return _clicks[i]
    
def land_mouse_button_released(int i) -> int:
    return _releases[i]

def land_mouse_set_pos(int x, int y):
    platform_mouse_set_pos(x, y)
    mx = x
    my = y

def land_hide_mouse_cursor() -> bool:
    platform_hide_mouse_cursor()
    return true

def land_show_mouse_cursor() -> bool:
    platform_show_mouse_cursor()
    return true
