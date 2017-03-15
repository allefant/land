import land.main
static import global allegro5.allegro
static import land.mem
import land.util
static import land.joystick
static import land.log

static LandArray *joys
static class Stick:
    int first_axis
    int axes

static class Joy:
    ALLEGRO_JOYSTICK *allegro
    int allegro_button
    int first_axis
    int axes
    int first_button
    int buttons
    LandArray *sticks

static LandArray *button_names
static LandArray *axis_names

def a5_joystick_create_mapping:
    if joys:
        for Joy *joy in joys:
            land_array_destroy_with_free(joy.sticks)
        land_array_destroy_with_free(joys)
        land_array_destroy_with_free(button_names)
        land_array_destroy_with_free(axis_names)
    joys = land_array_new()
    button_names = land_array_new()
    land_array_add(button_names, land_strdup("none"))
    axis_names = land_array_new()
    land_array_add(axis_names, land_strdup("none"))

    int jn = al_get_num_joysticks()
    int axes = 1
    int buttons = 1
    for int j in range(jn):
        ALLEGRO_JOYSTICK *allegro = al_get_joystick(j)
        Joy *joy = land_calloc(sizeof *joy)
        joy.allegro = allegro
        joy.buttons = al_get_joystick_num_buttons(allegro)
        joy.sticks = land_array_new()
        joy.first_axis = axes
        joy.first_button = buttons
        joy.axes = 0
        land_array_add(joys, joy)
        int sn = al_get_joystick_num_sticks(allegro)
        for int s in range(sn):
            Stick *stick = land_calloc(sizeof *stick)
            stick.first_axis = axes
            stick.axes = al_get_joystick_num_axes(allegro, s)
            land_array_add(joy.sticks, stick)
            for int a in range(stick.axes):
                char *name = land_strdup(al_get_joystick_stick_name(allegro, s))
                land_concatenate_with_separator(&name, al_get_joystick_axis_name(allegro, s, a), " ")
                land_log_message("joystick axis %d: %s\n", axes + a, name)
                land_array_add(axis_names, name)
            joy.axes += stick.axes
            axes += stick.axes
            if axes > LandJoystickAxesCount - 1:
                axes = LandJoystickAxesCount - 1
                land_log_message("Error: too many joystick axes!\n")
        for int b in range(joy.buttons):
            char *name = land_strdup(al_get_joystick_button_name(allegro, b))
            land_log_message("joystick button %d: %s\n", buttons + b, name)
            land_array_add(button_names, name)
        buttons += joy.buttons
        if buttons > LandJoystickButtonsCount - 1:
            buttons = LandJoystickButtonsCount - 1
            land_log_message("Error: too many joystick buttons!")

def a5_joystick_axis_to_land(ALLEGRO_JOYSTICK *allegro, int s, int a) -> int:
    for Joy *joy in joys:
        if joy.allegro == allegro:
            Stick *stick = land_array_get_nth(joy.sticks, s)
            return stick.first_axis + a
    return 0

def a5_joystick_button_to_land(ALLEGRO_JOYSTICK *allegro, int b) -> int:
    for Joy *joy in joys:
        if joy.allegro == allegro:
            return joy.first_button + b
    return 0

def platform_joystick_axis_count -> int:
    return len(axis_names)

def platform_joystick_button_count -> int:
    return len(button_names)
    
def platform_joystick_button_name(int b) -> str:
    if b >= len(button_names): return "none"
    return land_array_get_nth(button_names, b)

def platform_joystick_axis_name(int a) -> str:
    if a >= len(axis_names): return "none"
    return land_array_get_nth(axis_names, a)
