import land.main
static import global allegro5.allegro, allegro5.allegro_font
static import global allegro5.allegro_image
static import global allegro5.allegro_primitives
static import land.land
static import land.allegro5.a5_display
static import land.allegro5.a5_sound
static import land.allegro5.a5_joystick
static import land.joystick

*** "ifdef" ANDROID
*** "include" "allegro5/allegro_android.h"
*** "endif"

*** "ifdef" __EMSCRIPTEN__
*** "include" <emscripten.h>
*** "endif"

static bool redraw
static LandDisplayPlatform *d
static ALLEGRO_EVENT_QUEUE *queue
static ALLEGRO_TIMER *timer

static void (*global_cb)(void)

static def replacement_main(int argc, char **argv) -> int:
    global_cb()
    return 0

def platform_without_main(void (*cb)(void)):
    global_cb = cb
    al_run_main(0, None, replacement_main);

def platform_get_time() -> double:
    return al_current_time()

def platform_halt:
    platform_sound_halt()

def platform_resume:
    platform_sound_resume()

def platform_init():
    land_log_message("Compiled against Allegro %s.\n",
        ALLEGRO_VERSION_STR)

    if not al_init():
        land_log_message("Allegro initialization failed.\n")
        land_exception("Error in allegro_init.")

    *** "ifdef" ANDROID
    al_android_set_apk_file_interface()
    # FIXME: for loading data it can be useful to traverse the APK
    # filesystem, but for everything else (like configuration or
    # savegames) we need the normal filesystem.
    #al_android_set_apk_fs_interface()
    *** "endif"

    al_init_image_addon()
    al_install_keyboard()
    al_install_mouse()
    al_init_primitives_addon()

static macro _UnkKey(x) \
    LandKeyUnknown3 + x + 0, \
    LandKeyUnknown3 + x + 1, \
    LandKeyUnknown3 + x + 2, \
    LandKeyUnknown3 + x + 3, \
    LandKeyUnknown3 + x + 4, \
    LandKeyUnknown3 + x + 5, \
    LandKeyUnknown3 + x + 6, \
    LandKeyUnknown3 + x + 7, \
    LandKeyUnknown3 + x + 8, \
    LandKeyUnknown3 + x + 9

static int keyboard_conversion_table[ALLEGRO_KEY_MAX] = {
    LandKeyNone, # 0
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3',
    '4', '5', '6', '7', '8', '9',
    LandKeyPad + 0,
    LandKeyPad + 1,
    LandKeyPad + 2,
    LandKeyPad + 3, # 40
    LandKeyPad + 4,
    LandKeyPad + 5,
    LandKeyPad + 6,
    LandKeyPad + 7,
    LandKeyPad + 8,
    LandKeyPad + 9,
    LandKeyFunction + 1,
    LandKeyFunction + 2,
    LandKeyFunction + 3,
    LandKeyFunction + 4, # 50
    LandKeyFunction + 5,
    LandKeyFunction + 6,
    LandKeyFunction + 7,
    LandKeyFunction + 8,
    LandKeyFunction + 9,
    LandKeyFunction + 10,
    LandKeyFunction + 11,
    LandKeyFunction + 12,
    LandKeyEscape,
    '~', # 60
    '-',
    '=',
    LandKeyBackspace,
    LandKeyTab,
    '[',
    ']',
    LandKeyEnter,
    ';',
    '\'',
    '\\', # 70
    LandKeyUnknown + 0,
    ',',
    '.',
    '/',
    ' ',
    LandKeyInsert,
    LandKeyDelete,
    LandKeyHome,
    LandKeyEnd,
    LandKeyPageUp, # 80
    LandKeyPageDown,
    LandKeyLeft,
    LandKeyRight,
    LandKeyUp,
    LandKeyDown,
    LandKeyPadSlash,
    LandKeyPadStar,
    LandKeyPadMinus,
    LandKeyPadPlus,
    LandKeyPadDelete, # 90
    LandKeyPadEnter,

    LandKeyPrint,
    LandKeyPause,
    
    LandKeyUnknown + 1,
    LandKeyUnknown + 2,
    LandKeyUnknown + 3,
    LandKeyUnknown + 4,
    LandKeyUnknown + 5,
    '@',
    '^', # 100
    ':',
    LandKeyUnknown + 6,
    
    LandKeyUnknown + 7,
    LandKeyUnknown + 8,
    LandKeyUnknown + 9,
    LandKeyUnknown + 10,
    LandKeyBack,
    LandKeyUnknown + 12,
    LandKeyUnknown2 + 0,
    LandKeyUnknown2 + 1, # 110
    LandKeyUnknown2 + 2,
    LandKeyUnknown2 + 3,
    LandKeyUnknown2 + 4,
    LandKeyUnknown2 + 5,
    
    LandKeyUnknown3 + 0,
    LandKeyUnknown3 + 1,
    LandKeyUnknown3 + 2,
    LandKeyUnknown3 + 3,
    LandKeyUnknown3 + 4,
    LandKeyUnknown3 + 5, # 120
    
    _UnkKey(6), # 130
    _UnkKey(16), # 140
    _UnkKey(26), # 150
    _UnkKey(36), # 160
    _UnkKey(46), # 170
    _UnkKey(56), # 180
    _UnkKey(66), # 190
    _UnkKey(76), # 200
    _UnkKey(86), # 210
    
    LandKeyUnknown3 + 96,
    LandKeyUnknown3 + 97,
    LandKeyUnknown3 + 98,
    LandKeyUnknown3 + 99,

    LandKeyLeftShift,
    LandKeyRightShift,
    LandKeyLeftControl,
    LandKeyRightControl,
    LandKeyLeftAlt,
    LandKeyRightAlt, # 120
    LandKeyLeftWin,
    LandKeyRightWin,
    LandKeyMenu, # also on Android
    LandKeyScrollLock,
    LandKeyNumLock,
    LandKeyCapsLock}

def platform_key_name(int lk) -> char const *:
    int ak = 0
    for int i = 0 while i < ALLEGRO_KEY_MAX with i++:
        if keyboard_conversion_table[i] == lk:
            ak = i
            break
    char const *s = al_keycode_to_name(ak)
    return s

static def platform_keycode(int ak) -> int:
    return keyboard_conversion_table[ak]

def platform_hide_mouse_cursor():
    LandDisplayPlatform *d = (void *)_land_active_display
    al_hide_mouse_cursor(d->a5)

def platform_show_mouse_cursor():
    LandDisplayPlatform *d = (void *)_land_active_display
    al_show_mouse_cursor(d->a5)

def platform_mouse_set_pos(float x, y):
    LandDisplayPlatform *d = (void *)_land_active_display
    al_set_mouse_xy(d->a5, x, y)

def platform_pause:
    if timer:
        al_stop_timer(timer)

def platform_unpause:
    if timer:
        al_resume_timer(timer)

def platform_mainloop(LandParameters *parameters):
    d = (void *)_land_active_display
    queue = al_create_event_queue()
    timer = al_create_timer(1.0 / parameters->fps)
    al_register_event_source(queue, al_get_keyboard_event_source())
    al_register_event_source(queue, al_get_mouse_event_source())

    if al_install_touch_input():
        al_register_event_source(queue, al_get_touch_input_event_source())

    if al_install_joystick():
        al_register_event_source(queue, al_get_joystick_event_source())
    a5_joystick_create_mapping()

    al_register_event_source(queue, al_get_display_event_source(d->a5))

    al_register_event_source(queue, al_get_timer_event_source(timer))
    al_start_timer(timer);

    # Make sure querying mouse coordinates already works before any event.
    ALLEGRO_MOUSE_STATE s
    al_get_mouse_state(&s)
    land_mouse_move_event(s.x, s.y, s.z)

    redraw = False

    *** "ifdef" __EMSCRIPTEN__
    _land_synchronized = True
    emscripten_set_main_loop(platform_frame, 0, true);
    *** "else"
    while not _land_quit:
        platform_frame()
    *** "endif"

def platform_frame:
    if not _land_quit:
        if redraw and (_land_synchronized or
                al_event_queue_is_empty(queue)):
            if not _land_halted:
                land_draw()
            redraw = False

        while True:
            ALLEGRO_EVENT event
            *** "ifdef" __EMSCRIPTEN__
            if not al_get_next_event(queue, &event):
                break
            *** "else"
            al_wait_for_event(queue, &event)
            *** "endif"

            switch event.type:
                case ALLEGRO_EVENT_DISPLAY_CLOSE:
                    land_closebutton_event()
                    break
                case ALLEGRO_EVENT_TIMER:
                    if _land_was_halted and _land_halted:
                        al_stop_timer(timer)
                    else:
                        land_tick()
                        _land_frames++
                        redraw = True
                    break
                case ALLEGRO_EVENT_KEY_DOWN:
                    int lk = platform_keycode(event.keyboard.keycode)
                    land_key_press_event(lk)
                    break
                case ALLEGRO_EVENT_KEY_CHAR:
                    int lk = platform_keycode(event.keyboard.keycode)
                    land_keyboard_add_char(lk, event.keyboard.unichar)
                    break;
                case ALLEGRO_EVENT_KEY_UP:
                    int lk = platform_keycode(event.keyboard.keycode)
                    land_key_release_event(lk)
                    break
                case ALLEGRO_EVENT_MOUSE_AXES:
                    land_mouse_move_event(
                        event.mouse.x, event.mouse.y, event.mouse.z)
                    if land_mouse_b() & 1:
                        land_touch_event(event.mouse.x, event.mouse.y,
                            10, 0)
                    break
                case ALLEGRO_EVENT_MOUSE_BUTTON_DOWN:
                    land_mouse_button_down_event(event.mouse.button - 1)
                    land_touch_event(land_mouse_x(), land_mouse_y(),
                        10, 1)
                    break
                case ALLEGRO_EVENT_MOUSE_BUTTON_UP:
                    land_mouse_button_up_event(event.mouse.button - 1)
                    land_touch_event(land_mouse_x(), land_mouse_y(),
                        10, -1)
                    break
                case ALLEGRO_EVENT_TOUCH_BEGIN:
                    land_touch_event(event.touch.x, event.touch.y,
                        event.touch.id, 1)
                    break
                case ALLEGRO_EVENT_TOUCH_END:
                    land_touch_event(event.touch.x, event.touch.y,
                        event.touch.id, -1)
                    break
                case ALLEGRO_EVENT_TOUCH_MOVE:
                    land_touch_event(event.touch.x, event.touch.y,
                        event.touch.id, 0)
                    break
                case ALLEGRO_EVENT_DISPLAY_RESIZE:
                    al_acknowledge_resize((ALLEGRO_DISPLAY *)event.any.source)
                    land_resize_event(event.display.width, event.display.height)
                    break
                case ALLEGRO_EVENT_DISPLAY_SWITCH_OUT:
                    land_switch_out_event()
                    break
                case ALLEGRO_EVENT_DISPLAY_HALT_DRAWING:
                    land_halt()
                    al_acknowledge_drawing_halt(d->a5)
                    break
                case ALLEGRO_EVENT_DISPLAY_SWITCH_IN:
                    break
                case ALLEGRO_EVENT_DISPLAY_RESUME_DRAWING:
                    land_resume()
                    al_acknowledge_drawing_resume(d->a5)
                    al_start_timer(timer)
                    break
                case ALLEGRO_EVENT_JOYSTICK_CONFIGURATION:
                    al_reconfigure_joysticks()
                    a5_joystick_create_mapping()
                    break
                case ALLEGRO_EVENT_JOYSTICK_AXIS:
                    int a = a5_joystick_axis_to_land(event.joystick.id,
                        event.joystick.stick, event.joystick.axis)
                    land_joystick_axis_event(a, event.joystick.pos)
                    break
                case ALLEGRO_EVENT_JOYSTICK_BUTTON_DOWN:
                    int b = a5_joystick_button_to_land(event.joystick.id,
                        event.joystick.button)
                    land_joystick_button_down_event(b)
                    break
                case ALLEGRO_EVENT_JOYSTICK_BUTTON_UP:
                    int b = a5_joystick_button_to_land(event.joystick.id,
                        event.joystick.button)
                    land_joystick_button_up_event(b)
                    break
                    
                
            *** "ifdef" __EMSCRIPTEN__
            continue
            *** "endif"
            break

def platform_get_app_settings_file(char const *appname) -> char *:
    al_set_org_name("")
    al_set_app_name(appname)
    ALLEGRO_PATH *path = al_get_standard_path(ALLEGRO_USER_SETTINGS_PATH)
    const char *str = al_path_cstr(path, ALLEGRO_NATIVE_PATH_SEP)
    if not al_filename_exists(str):
        land_log_message("Creating new settings path %s.\n", str);
        al_make_directory(str)
    al_set_path_filename(path, "settings.cfg")
    str = al_path_cstr(path, ALLEGRO_NATIVE_PATH_SEP)
    land_log_message("Using settings file %s.\n", str);
    char *dup = land_strdup(str)
    al_destroy_path(path)
    return dup

def platform_wait(double seconds):
    al_rest(seconds)
