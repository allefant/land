static import global string, stdlib, stdbool, stdio
static import land/mem

class LandIniEntry:
    char *key
    void *val

class LandIniSection:
    int n
    LandIniEntry *entries

class LandIniFile:
    char *filename
    LandIniSection *sections

static void *def _get(LandIniSection *s, char const *key):
    for int i = 0 while i < s->n with i++:
        if not strcmp(s->entries[i].key, key) && s->entries[i].val:
            return s->entries[i].val
    return None

static def _add(LandIniSection *s, char const *key, void *val):
    for int i = 0 while i < s->n with i++:
        if not strcmp(s->entries[i].key, key):
            land_free(s->entries[i].val)
            s->entries[i].val = val
            return

    int i = s->n
    s->n++
    s->entries = land_realloc(s->entries, s->n * sizeof(LandIniEntry))
    s->entries[i].key = strdup(key)
    s->entries[i].val = val

static def _del(LandIniSection *s):
    for int i = 0 while i < s->n with i++:
        land_free(s->entries[i].key)
        if s->entries[i].val: land_free(s->entries[i].val)

    land_free(s->entries)
    land_free(s)

def land_ini_set_string(LandIniFile *ini,
    char const *section, char const *key, char const *val):
    LandIniSection *s = _get(ini->sections, section)
    if not s:
        s = calloc(1, sizeof *s)
        _add(ini->sections, section, s)

    _add(s, key, val ? strdup(val) : NULL)

def land_ini_set_int(LandIniFile *ini,
    char const *section, char const *key, int val):
    char temp[100]
    snprintf(temp, sizeof temp, "%d", val)
    land_ini_set_string(ini, section, key, temp)

char const *def land_ini_get_string(LandIniFile *ini,
    char const *section, char const *key, char const *de):
    LandIniSection *s = _get(ini->sections, section)
    if not s: return de
    char *v = _get(s, key)
    if v: return v
    return de

int def land_ini_get_int(LandIniFile *ini,
    char const *section, char const *key, int de):
    char const *s = land_ini_get_string(ini, section, key, None)
    if s == None: return de
    return strtol(s, None, 0)

int def land_ini_get_number_of_entries(LandIniFile *ini,
    char const *section):
    LandIniSection *s = ini->sections
    if not s: return 0
    if section:
        s = _get(s, section)
        if not s: return 0
    return s->n

char const *def land_init_get_nth_entry(LandIniFile *ini,
    char const *section, int i):
    LandIniSection *s = ini->sections
    if section:
        s = _get(s, section)
    return s->entries[i].key

static bool def is_whitespace(char c):
    if c == ' ' || c == '\t' || c == '\n': return true
    return false

static macro addc(var, len):
    var[len] = c;
    if len < (int)sizeof(var) - 1: len++
    var[len] = '\0'

static enum State:
    OUTSIDE
    SECTION
    KEY
    EQUALS
    VALUE
    COMMENT

LandIniFile *def land_ini_read(char const *filename):
    char section_name[1024] = "", key_name[1024] = "", value[1024] = ""
    int slen = 0, klen = 0, vlen = 0
    State state = OUTSIDE
    LandIniFile *ini = calloc(1, sizeof *ini)
    ini->filename = strdup(filename)
    ini->sections = calloc(1, sizeof *ini->sections)
    FILE *f = fopen(filename, "rb")
    if not f: return ini
    int done = 0
    while not done:
        char c = fgetc(f)
        if c == EOF:
            done = 1
            c = '\n'

        if c == '\r': continue

        if state == OUTSIDE: # outside
            if c == '[':
                slen = 0
                state = SECTION
            
            elif c == '#':
                state = COMMENT

            elif not is_whitespace(c):
                klen = 0
                addc(key_name, klen)
                state = KEY


        elif  state == SECTION: # section name
            if c == ']' || c == '\n':
                state = OUTSIDE
            else:
                addc(section_name, slen)

        elif state == KEY: # key name
            if c == '\n': state = OUTSIDE
            elif c == '=': state = EQUALS
            elif not is_whitespace(c):
                addc(key_name, klen)

        elif state == EQUALS: # = sign
            if c == '\n':
                value[0] = 0
                goto got_value
            if c == '\n' or not is_whitespace(c):
                state = VALUE
                vlen = 0
                addc(value, vlen)

        elif state == VALUE: # key value
            if c == '\n':
                label got_value
                land_ini_set_string(ini, section_name, key_name, value)
                state = OUTSIDE
            else:
                addc(value, vlen)
        
        elif state == COMMENT: # key value
            if c == '\n':
                state = OUTSIDE

    fclose(f)
    return ini

LandIniFile *def land_ini_new(char const *filename):
    LandIniFile *ini = calloc(1, sizeof *ini)
    ini->filename = strdup(filename)
    ini->sections = calloc(1, sizeof *ini->sections)
    return ini

def land_ini_destroy(LandIniFile *ini):
    for int i = 0 while i < ini->sections->n with i++:
        LandIniSection *s = ini->sections->entries[i].val
        _del(s)
        ini->sections->entries[i].val = NULL

    _del(ini->sections)
    free(ini->filename)
    free(ini)

def land_ini_writeback(LandIniFile *ini):
    FILE *f = fopen(ini->filename, "wb")
    if not f: return
    for int i = 0 while i < ini->sections->n with i++:
        char *name = ini->sections->entries[i].key
        if name && name[0]:
            fprintf(f, "[%s]\n", name)
        LandIniSection *s = ini->sections->entries[i].val
        for int j = 0 while j < s->n with j++:
            if s->entries[j].val:
                fprintf(f, "%s = %s\n", s->entries[j].key,
                    (char *)s->entries[j].val)
    fclose(f)
