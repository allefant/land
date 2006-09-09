static import keyboard, global allegro

static int key_state[KEY_MAX]
static int key_pressed[KEY_MAX]

static def cb(int k):
    if k & 128:
        key_state[k & 127] = 0

    else:
        if !key_state[k]:
            key_pressed[k]++
            key_state[k] = 1

def land_keyboard_init():
    keyboard_lowlevel_callback = cb

int def land_key(int k):
    return key[k]

int def land_key_pressed(int k):
    return key_pressed[k]

def land_keyboard_tick():
    int i
    for i = 0; i < KEY_MAX; i++:
        key_pressed[i] = 0

