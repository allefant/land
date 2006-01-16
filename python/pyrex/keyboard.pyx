cdef extern from "land.h":
    void land_keyboard_init()
    int land_key(int k)
    int land_key_pressed(int k)
    void land_keyboard_tick()
    int keypressed()
    int ureadkey(int *)
    void clear_keybuf()

    ctypedef enum:
        KEY_A
        KEY_B
        KEY_C
        KEY_D
        KEY_E
        KEY_F
        KEY_G
        KEY_H
        KEY_I
        KEY_J
        KEY_K
        KEY_L
        KEY_M
        KEY_N
        KEY_O
        KEY_P
        KEY_Q
        KEY_R
        KEY_S
        KEY_T
        KEY_U
        KEY_V
        KEY_W
        KEY_X
        KEY_Y
        KEY_Z
        KEY_0
        KEY_1
        KEY_2
        KEY_3
        KEY_4
        KEY_5
        KEY_6
        KEY_7
        KEY_8
        KEY_9
        KEY_0_PAD
        KEY_1_PAD
        KEY_2_PAD
        KEY_3_PAD
        KEY_4_PAD
        KEY_5_PAD
        KEY_6_PAD
        KEY_7_PAD
        KEY_8_PAD
        KEY_9_PAD
        KEY_F1
        KEY_F2
        KEY_F3
        KEY_F4
        KEY_F5
        KEY_F6
        KEY_F7
        KEY_F8
        KEY_F9
        KEY_F10
        KEY_F11
        KEY_F12
        KEY_ESC
        KEY_TILDE
        KEY_MINUS
        KEY_EQUALS
        KEY_BACKSPACE
        KEY_TAB
        KEY_OPENBRACE
        KEY_CLOSEBRACE
        KEY_ENTER
        KEY_COLON
        KEY_QUOTE
        KEY_BACKSLASH
        KEY_BACKSLASH2
        KEY_COMMA
        KEY_STOP
        KEY_SLASH
        KEY_SPACE
        KEY_INSERT
        KEY_DEL
        KEY_HOME
        KEY_END
        KEY_PGUP
        KEY_PGDN
        KEY_LEFT
        KEY_RIGHT
        KEY_UP
        KEY_DOWN
        KEY_SLASH_PAD
        KEY_ASTERISK
        KEY_MINUS_PAD
        KEY_PLUS_PAD
        KEY_DEL_PAD
        KEY_ENTER_PAD
        KEY_PRTSCR
        KEY_PAUSE
        KEY_ABNT_C1
        KEY_YEN
        KEY_KANA
        KEY_CONVERT
        KEY_NOCONVERT
        KEY_AT
        KEY_CIRCUMFLEX
        KEY_COLON2
        KEY_KANJI
        KEY_EQUALS_PAD
        KEY_BACKQUOTE
        KEY_SEMICOLON
        KEY_COMMAND
        KEY_UNKNOWN1
        KEY_UNKNOWN2
        KEY_UNKNOWN3
        KEY_UNKNOWN4
        KEY_UNKNOWN5
        KEY_UNKNOWN6
        KEY_UNKNOWN7
        KEY_UNKNOWN8
        KEY_MODIFIERS
        KEY_LSHIFT
        KEY_RSHIFT
        KEY_LCONTROL
        KEY_RCONTROL
        KEY_ALT
        KEY_ALTGR
        KEY_LWIN
        KEY_RWIN
        KEY_MENU
        KEY_SCRLOCK
        KEY_NUMLOCK
        KEY_CAPSLOCK
        KEY_MAX

def check(k):
    return land_key(k)

def pressed(k):
    return land_key_pressed(k)

def tick():
    land_keyboard_tick()

def clear():
    clear_keybuf()

def next():
    cdef int k
    if keypressed():
        u = ureadkey(&k)
        return unichr(u).encode("utf8"), k
    return None

A = KEY_A
B = KEY_B
C = KEY_C
D = KEY_D
E = KEY_E
F = KEY_F
G = KEY_G
H = KEY_H
I = KEY_I
J = KEY_J
K = KEY_K
L = KEY_L
M = KEY_M
N = KEY_N
O = KEY_O
P = KEY_P
Q = KEY_Q
R = KEY_R
S = KEY_S
T = KEY_T
U = KEY_U
V = KEY_V
W = KEY_W
X = KEY_X
Y = KEY_Y
Z = KEY_Z
KEY0 = KEY_0
KEY1 = KEY_1
KEY2 = KEY_2
KEY3 = KEY_3
KEY4 = KEY_4
KEY5 = KEY_5
KEY6 = KEY_6
KEY7 = KEY_7
KEY8 = KEY_8
KEY9 = KEY_9
PAD0 = KEY_0_PAD
PAD1 = KEY_1_PAD
PAD2 = KEY_2_PAD
PAD3 = KEY_3_PAD
PAD4 = KEY_4_PAD
PAD5 = KEY_5_PAD
PAD6 = KEY_6_PAD
PAD7 = KEY_7_PAD
PAD8 = KEY_8_PAD
PAD9 = KEY_9_PAD
F1 = KEY_F1
F2 = KEY_F2
F3 = KEY_F3
F4 = KEY_F4
F5 = KEY_F5
F6 = KEY_F6
F7 = KEY_F7
F8 = KEY_F8
F9 = KEY_F9
F10 = KEY_F10
F11 = KEY_F11
F12 = KEY_F12
ESC = ESCAPE = KEY_ESC
TILDE = KEY_TILDE
MINUS = KEY_MINUS
EQUALS = KEY_EQUALS
BACKSPACE = KEY_BACKSPACE
TAB = KEY_TAB
OPENBRACE = KEY_OPENBRACE
CLOSEBRACE = KEY_CLOSEBRACE
ENTER = KEY_ENTER
COLON = KEY_COLON
QUOTE = KEY_QUOTE
BACKSLASH = KEY_BACKSLASH
BACKSLASH2 = KEY_BACKSLASH2
COMMA = KEY_COMMA
STOP = KEY_STOP
SLASH = KEY_SLASH
SPACE = KEY_SPACE
INSERT = KEY_INSERT
DEL = DELETE = KEY_DEL
HOME = KEY_HOME
END = KEY_END
PGUP = PAGEUP = KEY_PGUP
PGDN = PAGEDOWN = KEY_PGDN
LEFT = KEY_LEFT
RIGHT = KEY_RIGHT
UP = KEY_UP
DOWN = KEY_DOWN
SLASH_PAD = KEY_SLASH_PAD
ASTERISK = KEY_ASTERISK
MINUS_PAD = KEY_MINUS_PAD
PLUS_PAD = KEY_PLUS_PAD
DEL_PAD = KEY_DEL_PAD
ENTER_PAD = KEY_ENTER_PAD
PRTSCR = KEY_PRTSCR
PAUSE = KEY_PAUSE
ABNT_C1 = KEY_ABNT_C1
YEN = KEY_YEN
KANA = KEY_KANA
CONVERT = KEY_CONVERT
NOCONVERT = KEY_NOCONVERT
AT = KEY_AT
CIRCUMFLEX = KEY_CIRCUMFLEX
COLON2 = KEY_COLON2
KANJI = KEY_KANJI
EQUALS_PAD = KEY_EQUALS_PAD
BACKQUOTE = KEY_BACKQUOTE
SEMICOLON = KEY_SEMICOLON
COMMAND = KEY_COMMAND
UNKNOWN1 = KEY_UNKNOWN1
UNKNOWN2 = KEY_UNKNOWN2
UNKNOWN3 = KEY_UNKNOWN3
UNKNOWN4 = KEY_UNKNOWN4
UNKNOWN5 = KEY_UNKNOWN5
UNKNOWN6 = KEY_UNKNOWN6
UNKNOWN7 = KEY_UNKNOWN7
UNKNOWN8 = KEY_UNKNOWN8
MODIFIERS = KEY_MODIFIERS
LSHIFT = KEY_LSHIFT
RSHIFT = KEY_RSHIFT
LCONTROL = KEY_LCONTROL
RCONTROL = KEY_RCONTROL
ALT = KEY_ALT
ALTGR = KEY_ALTGR
LWIN = KEY_LWIN
RWIN = KEY_RWIN
MENU = KEY_MENU
SCRLOCK = KEY_SCRLOCK
NUMLOCK = KEY_NUMLOCK
CAPSLOCK = KEY_CAPSLOCK
MAX = KEY_MAX

ESCAPE = ESC
