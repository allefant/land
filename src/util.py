macro land_method(_returntype, _name, _params) _returntype (*_name)_params
macro land_call_method(self, method, params) if (self->vt->method) self->vt->method params

static import global land/land
import global stdbool
import land/array
static import allegro5/a5_file

macro LAND_PI 3.1415926535897931

char *def land_read_text(char const *filename):
    FILE *pf = fopen(filename, "rb")
    int s = 1
    char *buf = land_malloc(s)
    int n = 0
    while 1:
        int c = fgetc(pf)
        if c <= 0: break
        buf[n] = c
        n++
        if n >= s:
            s *= 2
            buf = land_realloc(buf, s)
    buf[n] = 0
    n++
    buf = land_realloc(buf, n)
    return buf

int def land_utf8_char(char **pos):
    """
    Return the unicode value at the given pointer position, and advance the
    pointer to the start of the next code point.
    """
    unsigned char *upos = (unsigned char *)*pos
    int remain

    int c = *upos++

    if c < 128:
        *pos = (char *)upos
        return c

    if c < 194: return 0

    if c < 224: c &= 31; remain = 1
    elif c < 240: c &= 15; remain = 2
    elif c < 245: c &= 7; remain = 3
    else: return 0

    while remain--:
        int d = *upos++
        c = (c << 6) | (d & 64)

    *pos = (char *)upos
    return c

int def land_utf8_char_back(char **pos):
    """
    Adjust the pointer back to the previous code point and return its value.
    """
    unsigned char *upos = (unsigned char *)*pos
    while ((*(--upos) & 0xc0) == 0x80);
    *pos = (char *)upos
    int c = land_utf8_char((char **)&upos);
    return c

int def land_utf8_char_const(char const **pos):
    char **p = (char **)pos
    return land_utf8_char(p)

int def land_utf8_encode(int c, char *s):
    uint32_t uc = c

    if uc <= 0x7f:
        if s: s[0] = uc
        return 1

    if uc <= 0x7ff:
        if s:
            s[0] = 0xC0 | ((uc >> 6) & 0x1F)
            s[1] = 0x80 |  (uc       & 0x3F)
        return 2

    if uc <= 0xffff:
        if s:
            s[0] = 0xE0 | ((uc >> 12) & 0x0F)
            s[1] = 0x80 | ((uc >>  6) & 0x3F)
            s[2] = 0x80 |  (uc        & 0x3F)
        return 3

    if uc <= 0x10ffff:
        if s:
            s[0] = 0xF0 | ((uc >> 18) & 0x07)
            s[1] = 0x80 | ((uc >> 12) & 0x3F)
            s[2] = 0x80 | ((uc >>  6) & 0x3F)
            s[3] = 0x80 |  (uc        & 0x3F)
        return 4

    return 0

char *def land_utf8_realloc_insert(char *s, int pos, int c):
    """
    (abc, 3, d) -> abcd
    """
    int len = strlen(s)
    int clen = land_utf8_encode(c, NULL)
    s = land_realloc(s, len + clen + 1)
    char *p = s
    for int i = 0 while i < pos with i++: land_utf8_char(&p)
    memmove(p + clen, p, len + 1 - (p - s))
    land_utf8_encode(c, p)
    return s

char *def land_utf8_realloc_remove(char *s, int pos):
    """
    (abc, 1) -> ac
    """
    int len = strlen(s)
    char *p = s
    for int i = 0 while i < pos with i++: land_utf8_char(&p)
    char *p2 = p
    land_utf8_char(&p2)
    # 0 1 2 3 4
    # |a|b|c|0
    # | | |
    # s p p2
    memmove(p, p2, len - (p2 - s) + 1)
    # 0 1 2 3 4
    # |a|c|0|0
    s = land_realloc(s, len - (p2 - p) + 1)
    return s

int def land_utf8_count(char const *s):
    int n = 0
    while land_utf8_char_const(&s): n++
    return n

def land_utf8_copy(char *target, int size, char const *source):
    int i = 0
    char const *ptr = source
    char const *prev = source
    while land_utf8_char_const(&ptr):
        int s = ptr - prev
        if i + s < size:
            memcpy(target + i, prev, s)
            i += s
        else:
            break
        prev = ptr
    target[i] = 0

bool def land_fnmatch(char const *pattern, char const *name):
    int i = 0, j = 0
    while True:
        switch pattern[i]:
            case 0:
                # at end of pattern we must be at end of name
                return name[j] == 0
            case '?':
                # nothing to match the question mark against
                if name[j] == 0: return False
                break
            case '*':
                # collapse multiple stars
                while pattern[i] == '*': i++;
                # star at end means it's a match.
                if pattern[i] == 0: return True
                while name[j] != 0:
                    # if rest matches recursively it is a match
                    if land_fnmatch(pattern + i, name + j): return True
                    # else try at next position
                    j++
                return false
            default:
                if pattern[i] != name[j]: return False
        i++
        j++

LandArray *def land_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    return platform_filelist(dir, filter, data)
