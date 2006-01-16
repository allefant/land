#include <allegro.h>

#include "mouse.h"
#include "exception.h"

static int mx, my, mz, omx, omy, omz;
static int mb, omb;

static int have_os_cursor = 0;

void land_mouse_init(void)
{
    enable_hardware_cursor();
    select_mouse_cursor(MOUSE_CURSOR_ARROW);
    show_mouse(screen);
    have_os_cursor = gfx_capabilities & GFX_SYSTEM_CURSOR;
    if (!have_os_cursor)
        show_mouse(NULL);
}

int land_have_os_cursor(void)
{
    return have_os_cursor;
}

void land_mouse_tick(void)
{
    omx = mx;
    omy = my;
    omz = mz;
    omb = mb;
    mx = mouse_x;
    my = mouse_y;
    mz = mouse_z;
    mb = mouse_b;
}

int land_mouse_x(void)
{
    return mx;
}

int land_mouse_y(void)
{
    return my;
}

int land_mouse_z(void)
{
    return mz;
}

int land_mouse_b(void)
{
    return mb;
}

int land_mouse_delta_x(void)
{
    return mx - omx;
}

int land_mouse_delta_y(void)
{
    return my - omy;
}

int land_mouse_delta_z(void)
{
    return mz - omz;
}

int land_mouse_delta_b(void)
{
    return mb ^ omb;
}

void land_mouse_set_pos(int x, int y)
{
    position_mouse(x, y);
}

int land_hide_mouse_cursor(void)
{
    return !show_os_cursor(MOUSE_CURSOR_NONE);
}

int land_show_mouse_cursor(void)
{
    return !show_os_cursor(MOUSE_CURSOR_ARROW);
}
