static import global allegro
static import exception

static int mx, my, mz, omx, omy, omz
static int mb, omb

static int have_os_cursor = 0

def land_mouse_init():
    land_show_mouse_cursor()

int def land_have_os_cursor():
    return have_os_cursor

def land_mouse_tick():
    omx = mx
    omy = my
    omz = mz
    omb = mb
    mx = mouse_x
    my = mouse_y
    mz = mouse_z
    mb = mouse_b

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
    
int def land_mouse_button():
    """Return the mouse button state for the current tick."""
    return mb

int def land_mouse_delta_x():
    return mx - omx

int def land_mouse_delta_y():
    return my - omy

int def land_mouse_delta_z():
    return mz - omz

int def land_mouse_delta_b():
    return mb ^ omb

def land_mouse_set_pos(int x, int y):
    position_mouse(x, y)
    mx = x
    my = y

int def land_hide_mouse_cursor():
    show_os_cursor(MOUSE_CURSOR_NONE)
    have_os_cursor = 0
    return have_os_cursor

int def land_show_mouse_cursor():
    have_os_cursor = !show_os_cursor(MOUSE_CURSOR_ARROW)
    return have_os_cursor
