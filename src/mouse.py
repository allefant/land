import global stdbool
static import exception, land/allegro5/a5_main
static import global assert

static int mx, my, mz, mb
static int omx, omy, omz, omb
static int buttons[5], obuttons[5], clicks[5]

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

def land_mouse_move_event(int x, int y, int z):
    mx = x
    my = y
    mz = z

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

int def land_mouse_x():
    """Return the mouse X coordinate for the current tick."""
    return mx

int def land_mouse_y():
    """Return the mouse Y coordinate for the current tick."""
    return my

int def land_mouse_z():
    """Return the mouse wheel coordinate for the current tick."""
    return mz

int def land_mouse_b():
    """Short for land_mouse_button."""
    return mb

int def land_mouse_button(int i):
    """Return the mouse button state for the current tick."""
    return buttons[i] & 1

int def land_mouse_delta_x():
    return mx - omx

int def land_mouse_delta_y():
    return my - omy

int def land_mouse_delta_z():
    return mz - omz

int def land_mouse_delta_b():
    return mb ^ omb

int def land_mouse_delta_button(int i):
    return (buttons[i] & 1) ^ (obuttons[i] & 1)

int def land_mouse_button_clicked(int i):
    return clicks[i]

def land_mouse_set_pos(int x, int y):
    platform_mouse_set_pos(x, y)
    mx = x
    my = y

bool def land_hide_mouse_cursor():
    platform_hide_mouse_cursor()
    return true

bool def land_show_mouse_cursor():
    platform_show_mouse_cursor()
    return true
