"""
0 is the left mouse button
1 is the right mouse button
2 is the middle mouse button
3,4,... are extra mouse buttons
"""
import global stdbool
static import exception, land/allegro5/a5_main
static import global assert

static int mx, my, mz, mb
static int omx, omy, omz, omb
static int buttons[5], obuttons[5], clicks[5]
static float tx[11], ty[11], tb[11], otb[11]

def land_mouse_init():
    land_show_mouse_cursor()

def land_mouse_tick():
    omx = mx
    omy = my
    omz = mz
    omb = mb

    for int i = 0 while i < 5 with i++:
        obuttons[i] = buttons[i]
        if buttons[i] == 2: buttons[i] = 0
        clicks[i] = 0

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
    # FIXME: can lose fast clicks this way, should simply treat the
    # mouse buttons as additional keys in the keyboard module
    mb |= 1 << b
    if not (buttons[b] & 1):
        clicks[b]++
    buttons[b] |= 1 + 2

def land_mouse_button_up_event(int b):
    mb &= ~(1 << b)
    buttons[b] &= ~1

def land_mouse_x() -> int:
    """Return the mouse X coordinate for the current tick."""
    return mx

def land_mouse_y() -> int:
    """Return the mouse Y coordinate for the current tick."""
    return my

def land_mouse_z() -> int:
    """Return the mouse wheel coordinate for the current tick."""
    return mz

def land_mouse_b() -> int:
    """Short for land_mouse_button."""
    return mb

def land_mouse_button(int i) -> int:
    """Return the mouse button state for the current tick."""
    return buttons[i] & 1

def land_mouse_delta_x() -> int:
    return mx - omx

def land_mouse_delta_y() -> int:
    return my - omy

def land_mouse_delta_z() -> int:
    return mz - omz

def land_mouse_delta_b() -> int:
    return mb ^ omb

def land_mouse_delta_button(int i) -> int:
    return (buttons[i] & 1) ^ (obuttons[i] & 1)

def land_mouse_button_clicked(int i) -> int:
    return clicks[i]

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
