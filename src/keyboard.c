#include <allegro.h>

#include "keyboard.h"

static int key_state[KEY_MAX];
static int key_pressed[KEY_MAX];

static void cb(int k)
{
    if (k & 128)
    {
        key_state[k & 127] = 0;
    }
    else
    {
        if (!key_state[k])
        {
            key_pressed[k]++;
            key_state[k] = 1;
        }
    }
}

void land_keyboard_init(void)
{
    keyboard_lowlevel_callback = cb;
}

int land_key(int k)
{
    return key[k];
}

int land_key_pressed(int k)
{
    return key_pressed[k];
}

void land_keyboard_tick(void)
{
    int i;
    for (i = 0; i < KEY_MAX; i++)
    {
        key_pressed[i] = 0;
    }
}
