import global stdbool
static import log

import land/allegro5/a5_main

enum LandKeyboardKeys:
    LandKeyNone = 0
    LandKeyInsert = 1
    LandKeyDelete = 2
    LandKeyHome = 3
    LandKeyEnd = 4
    LandKeyPageUp = 5
    LandKeyPageDown = 6
    LandKeyPadSlash = 7
    LandKeyBackspace = 8
    LandKeyTab = 9
    LandKeyPadStar = 10
    LandKeyPadMinus = 11
    LandKeyPadPlus = 12
    LandKeyEnter = 13
    LandKeyUnknown = 14 # 14=U+0, ..., 24=U+10
    LandKeyBack = 25
    # U+12
    LandKeyEscape = 27
    LandKeyPadDelete = 28
    LandKeyPadEnter = 29
    LandKeyLeftWin = 30
    LandKeyRightWin = 31 # 32=space
    LandKeyUnknown2 = 33 # 33=U'+0, ..., 38=U'+6, 39=quote
    LandKeyLeftShift = '(' # 40
    LandKeyRightShift = ')' # 41
    LandKeyScrollLock = '*' # 42
    LandKeyNumLock = '+' # 43, 44='=', 45=- 46=. 47=/
    LandKeyNumber = '0' # 48=0, ..., 57=9, 58=:, 59=;
    LandKeyLeftAlt= '<' # 61== */
    LandKeyRightAlt= '>'
    LandKeyMenu = '?'
    LandKeyFunction = '@' # 65=F+1, 76=F+12
    LandKeyPad = 'M' # 77=P+0, 86=P+9
    LandKeyLeft = 'W'
    LandKeyRight = 'X'
    LandKeyUp = 'Y'
    LandKeyDown = 'Z' # 91=[, 92=\, 93=], 94=^
    LandKeyCapsLock= '_'
    LandKeyPrint = '`'
    LandKeyLetter = 'a' # 97=a, ..., 122=z
    LandKeyLeftControl = '{'
    LandKeyPause = '|'
    LandKeyRightControl = '}' # 126=~
    LandKeyUnknown3 = 127 # 127=U''+0, ..., 227=U''+100
    LandKeysCount = 228

    LandKeyF5 = LandKeyFunction + 5
    LandKeyShift = LandKeysCount + 1

static int key_state[LandKeysCount]
static int key_pressed[LandKeysCount]
static int keybuffer_keycode[256]
static int keybuffer_unicode[256]
static int keybuffer_first
static int keybuffer_last

def land_key_press_event(int k):
    if not key_state[k]:
        key_pressed[k]++
        key_state[k] = 1

def land_key_release_event(int k):
    key_state[k] = 0

def land_keyboard_init():
    pass

def land_key(int k) -> int:
    if k == LandKeyShift:
        return key_state[LandKeyLeftShift] | key_state[LandKeyRightShift]
    return key_state[k]

def land_key_pressed(int k) -> int:
    return key_pressed[k]

def land_keyboard_tick():
    int i
    for i = 0 while i < LandKeysCount with i++:
        key_pressed[i] = 0
    keybuffer_first = 0
    keybuffer_last = 0

def land_keyboard_add_char(int keycode, int unicode):
    if keybuffer_last == 256: return
    keybuffer_keycode[keybuffer_last] = keycode
    keybuffer_unicode[keybuffer_last] = unicode
    keybuffer_last++

def land_keybuffer_empty() -> bool:
    return keybuffer_last == keybuffer_first

def land_keybuffer_next(int *k, int *u):
    if keybuffer_first < keybuffer_last:
        *k = keybuffer_keycode[keybuffer_first]
        *u = keybuffer_unicode[keybuffer_first]
        keybuffer_first++

def land_key_name(int k) -> char const *:
    return platform_key_name(k)

def land_key_get_pressed(int first) -> int:
    for int i in range(first, LandKeysCount):
        if key_pressed[i]: return i
    return 0
