macro land_method(_returntype, _name, _params) _returntype (*_name)_params
macro land_call_method(self, method, params):
    if self->vt->method: self->vt->method params

import global stdbool
import global ctype
import global stdio
import land/array
import land/buffer
import land/common
static import allegro5/a5_file

macro LAND_PI ALLEGRO_PI
macro LandPi ALLEGRO_PI
macro pi ALLEGRO_PI

def print(char const *s, ...):
    va_list args
    va_start(args, s)
    vprintf(s, args)
    va_end(args)
    printf("\n")

def land_read_text(char const *filename) -> char *:
    LandBuffer* bytebuffer = land_buffer_read_from_file(filename)
    if not bytebuffer:
        return None
    return land_buffer_finish(bytebuffer)

def land_utf8_char(char **pos) -> int:
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
        c = (c << 6) | (d & 63)

    *pos = (char *)upos
    return c

def land_utf8_char_back(char **pos) -> int:
    """
    Adjust the pointer back to the previous code point and return its value.
    """
    unsigned char *upos = (unsigned char *)*pos
    while ((*(--upos) & 0xc0) == 0x80);
    *pos = (char *)upos
    int c = land_utf8_char((char **)&upos);
    return c

def land_utf8_char_const(char const **pos) -> int:
    char **p = (char **)pos
    return land_utf8_char(p)

def land_utf8_encode(int c, char *s) -> int:
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

def land_utf8_realloc_insert(char *s, int pos, int c) -> char *:
    """
    (abc, 3, d) -> abcd
    """
    int l = strlen(s)
    int clen = land_utf8_encode(c, None)
    s = land_realloc(s, l + clen + 1)
    char *p = s
    if pos >= 0:
        for int i = 0 while i < pos with i++:
            land_utf8_char(&p)
    else:
        p += l # to before the 0 character
        # TODO: -1 is at end, -2 before last character, and so on...
    memmove(p + clen, p, l + 1 - (p - s))
    land_utf8_encode(c, p)
    return s

def land_utf8_realloc_remove(char *s, int pos) -> char *:
    """
    (abc, 1) -> ac
    """
    int l = strlen(s)
    char *p = s
    for int i = 0 while i < pos with i++: land_utf8_char(&p)
    char *p2 = p
    land_utf8_char(&p2)
    # 0 1 2 3 4
    # |a|b|c|0
    # | | |
    # s p p2
    memmove(p, p2, l - (p2 - s) + 1)
    # 0 1 2 3 4
    # |a|c|0|0
    s = land_realloc(s, l - (p2 - p) + 1)
    return s

def land_utf8_count(char const *s) -> int:
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

def land_fnmatch(char const *pattern, char const *name) -> bool:
    """
    Match ? and * in the pattern.
    """
    int i = 0, j = 0
    while True:
        switch pattern[i]:
            case 0:
                # at end of pattern we must be at end of name
                return name[j] == 0
            case '?':
                # match an optional block ?(...)
                if pattern[i + 1] == '(':
                    int n = 0
                    while pattern[i + 2 + n] != ')':
                        if pattern[i + 2 + n] == 0:
                            return False # unclosed parenthesis
                        n++
                    char pattern2[strlen(pattern) + 1]
                    strncpy(pattern2, pattern + i + 2, n)
                    pattern2[n] = 0
                    strcat(pattern2 + n, pattern + i + 3 + n)
                    # if it matches with the optional pattern it matches
                    if land_fnmatch(pattern2, name + j):
                        return True
                    # else match without it
                    return land_fnmatch(pattern + i + 3 + n, name + j)
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

def land_string_copy(char *target, char const *source, int size) -> char *:
    """
    size is the size of target in bytes (including the terminating 0)

    Returns target.
    """
    if target == source:
        # strcpy will fail if the areas overlap (or are identical)
        return target
    strncpy(target, source, size - 1)
    target[size - 1] = 0
    return target

def land_equals(char const *s, *s2) -> bool:
    if s == None:
        return s2 == None
    if s2 == None:
        return False
    return strcmp(s, s2) == 0

def land_ends_with(char const *s, *end) -> bool:
    size_t n = strlen(end)
    return strncmp(s + strlen(s) - n, end, n) == 0

def land_starts_with(char const *s, *start) -> bool:
    size_t n = strlen(start)
    return strncmp(s, start, n) == 0

def land_concatenate(char **s, char const *cat):
    """
    Extends the string pointed to by s, appending cat.
    """
    if not *s: *s = land_strdup("")
    int sn = strlen(*s)
    int n = sn + strlen(cat) + 1
    char *re = land_realloc(*s, n)
    memmove(re + sn, cat, strlen(cat))
    re[n - 1] = 0
    *s = re

def land_appendv(char **s, str format, va_list args):
    va_list args2
    va_copy(args2, args)
    int n = vsnprintf(None, 0, format, args2)
    va_end(args2)
    if n < 0: n = 1023
    char f[n + 1]
    vsnprintf(f, n + 1, format, args)
    land_concatenate(s, f)

def land_append(char **s, str format, ...):
    va_list args
    va_start(args, format)
    land_appendv(s, format, args)
    va_end(args)

def land_overwrite(char **s, str format, ...):
    va_list args
    va_start(args, format)
    (*s)[0] = 0
    land_appendv(s, format, args)
    va_end(args)

def land_concatenate_with_separator(char **s, char const *cat, *sep):
    if not *s or land_equals(*s, ""):
        land_concatenate(s, cat)
    else:
        land_concatenate(s, sep)
        land_concatenate(s, cat)

def land_prepend(char **s, char const *pre):
    int slen = strlen(*s)
    int n = slen + strlen(pre) + 1
    char *re = land_realloc(*s, n)
    memmove(re + strlen(pre), re, slen)
    memmove(re, pre, strlen(pre))
    re[n - 1] = 0
    *s = re

def land_replace(char **s, int off, char const *wat, *wit) -> int:
    """
    Given a pointer to a string, replaces the string with a new string
    and deletes the original one. The new string will have the
    first occurence of "wat" replaced with "wit", starting at byte
    offset off.
    """
    char *r = strstr(*s + off, wat)
    if not r:
        return strlen(*s)
    int pn = r - *s
    int sn = strlen(*s)
    int n = sn + strlen(wit) - strlen(wat) + 1
    char *re = land_malloc(n)
    memmove(re, *s, r - *s)
    memmove(re + pn, wit, strlen(wit))
    memmove(re + pn + strlen(wit), r + strlen(wat),
        sn - pn - strlen(wat))
    re[n - 1] = 0
    land_free(*s)
    *s = re
    return pn + strlen(wit)

def land_contains(str hay, needle) -> bool:
    return strstr(hay, needle) != None

def land_find(str hay, needle) -> int:
    str x = strstr(hay, needle)
    if not x: return -1
    return x - hay

def land_find_from_back(str hay, needle) -> int:
    # 0123456 01 
    # abcdef  e
    int hn = strlen(hay)
    int nn = strlen(needle)
    int i = hn - nn
    while i >= 0:
        if strncmp(hay + i, needle, nn) == 0: return i
        i--
    return -1

def land_count(str hay, str needle) -> int:
    str p = hay
    int n = 0
    while True:
        str x = strstr(p, needle)
        if not x: return n
        n += 1
        p = x + 1

def land_replace_all(char **s, char const *wat, char const *wit) -> int:
    """
    Like land_replace but replaces all occurences. Returns the number
    of replacements performed.
    """
    int off = 0
    int c = 0
    while True:
        off = land_replace(s, off, wat, wit)
        if not (*s)[off]:
            return c
        c++

def land_lowercase_copy(str s) -> char*:
    char const *pos = s
    char *news = land_strdup("")
    while True:
        int c = land_utf8_char_const(&pos)
        if not c: break
        news = land_utf8_realloc_insert(news, -1, tolower(c))
    return news

def land_shorten(char **s, int start, end):
    """
    Shorten a string so it starts at start and ends before end.

    land_shorten("abcd", 1, 3) -> "bc"
    land_shorten("abcd", 1, -1) -> "bc"
    """
    char *replace = land_substring(*s, start, end)
    land_free(*s)
    *s = replace

def land_replace_string(char **s, str replace):
    """
    Free the target string if it is not None and then replace it with
    a copy of the given replacement.
    """
    if *s: land_free(*s)
    *s = land_strdup(replace)

def land_cut(char **s, int start, end):
    """
    Cut the given sequence from start to before end out of the string.
    """
    char *replace = land_substring(*s, 0, start)
    land_concatenate(&replace, *s + end)
    land_free(*s)
    *s = replace

def land_substring(char const *s, int a, b) -> char *:
    """
    a is inlusive
    b is exclusive
    """
    #    a=2  b=6
    # AB[CDEF]G
    # CDEFEFG memmove(s, s + 2, 4)
    # CDEF s[4] = 0
    if a < 0: a += strlen(s)
    if b < 0: b += strlen(s)
    char *r = land_malloc(b - a + 1)
    memmove(r, s + a, b - a)
    r[b - a] = 0
    return r

def land_strip(char **s):
    LandBuffer *b = land_buffer_new()
    land_buffer_cat(b, *s)
    land_buffer_strip(b, " \t\n\r")
    land_free(*s)
    *s = land_buffer_finish(b)

def land_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data), int flags, void *data) -> LandArray *:
    """
    Returns an array of files in the given directory. Before a file is added,
    the filter function is called, with the name about to be added and an
    indication whether it is a filename or a directory.
    
    If flags is LAND_FULL_PATH files are returned as a full path, if
    LAND_RELATIVE_PATH relative to dir, otherwise as
    only the filename.

    The return value of the filter decides what is done with the name:
    0 - Discard it.
    1 - Append it to the returned list.
    2 - If it is a directory, recurse into it.
    3 - Like 1 and 2 combined.
    """
    char* dir2 = land_path_with_prefix(dir)
    LandArray* array = platform_filelist(dir2, filter, flags, data)
    land_free(dir2)
    return array

def _filter(char const *name, bool is_dir, void *data) -> int:
    char const *pattern = data
    if is_dir:
        return 2
    if land_fnmatch(pattern, name):
        return 1
    return 0

def land_for_each_file(str pattern, void (*cb)(str path, void* data), void* data) -> int:
    LandBuffer* dirbuf = land_buffer_new()
    int j = 0
    for int i = 0 while pattern[i] with i++:
        if pattern[i] == '/':
            land_buffer_add(dirbuf, pattern + j, i - j)
            j = i
        if pattern[i] == '?' or pattern[i] == '*':
            break
    char *dirpath = land_buffer_finish(dirbuf)

    int count = 0
    LandArray* filenames = land_filelist(dirpath, _filter, LAND_RELATIVE_PATH, (void *)pattern)
    if filenames:
        count = filenames->count

    land_free(dirpath)

    if not filenames: return 0

    land_array_sort_alphabetical(filenames)

    int i
    for i = 0 while i < filenames->count with i++:
        char *filename = land_array_get_nth(filenames, i)
        cb(filename, data)
        land_free(filename)

    land_array_destroy(filenames)
    return count

def land_split_path_name_ext(char const *filename) -> LandArray*:
    """
Returns a LandArray with three elements, for example:

    data/blah/tree.png -> ["data/blah", "tree", "png"]
    test.txt -> [None, "test", "txt"]
    /etc/passwd -> ["/etc", "passwd", None]

The return value can most conveniently be freed like this:

    a = land_split_path_name_ext(filename)
    ...
    land_array_destroy_with_strings(a)
    """
    LandArray *a = land_array_new()
    char *path = land_strdup(filename)
    char *name
    char *ext
    char *slash = strrchr(path, '/')
    if slash:
        *slash = 0
        name = land_strdup(slash + 1)
    else:
        name = path
        path = None
    char *dot = strrchr(name, '.')
    if dot:
        *dot = 0
        ext = land_strdup(dot + 1)
    else:
        ext = None
        
    land_array_add(a, path)
    land_array_add(a, name)
    land_array_add(a, ext)
    return a

def land_split(char const *text, str c) -> LandArray *:
    """
    Returns an array of strings which you should destroy with
    land_array_destroy_with_strings
    """
    LandArray *split = land_array_new()
    LandBuffer *buf = land_buffer_new()
    land_buffer_cat(buf, text)
    LandArray *lines = land_buffer_split(buf, c)
    for LandBuffer *line in LandArray *lines:
        char *x = land_buffer_finish(line)
        land_array_add(split, x)
    land_array_destroy(lines)
    land_buffer_destroy(buf)
    return split

def land_split_two(str text, str sep, char **a, **b) -> bool:
    int x = land_find(text, sep)
    if x < 0: return False
    *a = land_substring(text, 0, x)
    *b = land_substring(text, x + strlen(sep), strlen(text))
    return True

def land_split_lines(char const *text) -> LandArray *:
    return land_split(text, "\n")

def land_null_or_empty(str text) -> bool:
    return not text or not text[0]

def land_to_int(str text) -> int:
    return strtol(text, None, 0)
