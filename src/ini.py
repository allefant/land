static import global string, stdlib, stdbool, stdio
static import land/mem
static import land/allegro5/a5_main
static import land.file
import land.hash

class LandIniEntry:
    char *key
    void *val

class LandIniSection:
    LandArray *entries
    LandHash *lookup

class LandIniFile:
    char *filename
    LandIniSection *sections

static def _get(LandIniSection *s, char const *key) -> void *:
    LandIniEntry *e = land_hash_get(s.lookup, key)
    if e:
        return e.val
    return None

static def _add(LandIniSection *s, char const *key, void *val):
    LandIniEntry *e = land_hash_get(s.lookup, key)
    if e:
        land_free(e.val)
        e.val = val
        return

    e = land_calloc(sizeof *e)
    e.key = land_strdup(key)
    e.val = val
    land_array_add(s.entries, e)
    land_hash_insert(s.lookup, key, e)

static def _del(LandIniSection *s):
    for LandIniEntry *e in LandArray *s.entries:
        land_free(e.key)
        if e.val:
            land_free(e.val)
        land_free(e)

    land_array_destroy(s.entries)
    land_hash_destroy(s.lookup)
    land_free(s)

static def _new() -> LandIniSection *:
    LandIniSection *s = land_calloc(sizeof *s)
    s.lookup = land_hash_new()
    s.entries = land_array_new()
    return s

def land_ini_set_string(LandIniFile *ini,
    char const *section, char const *key, char const *val):
    LandIniSection *s = _get(ini->sections, section)
    if not s:
        s = _new()
        _add(ini->sections, section, s)

    _add(s, key, val ? land_strdup(val) : None)

def land_ini_set_int(LandIniFile *ini,
    char const *section, char const *key, int val):
    char temp[100]
    snprintf(temp, sizeof temp, "%d", val)
    land_ini_set_string(ini, section, key, temp)

def land_ini_get_string(LandIniFile *ini,
    char const *section, char const *key, char const *de) -> char const *:
    LandIniSection *s = _get(ini->sections, section)
    if not s: return de
    char *v = _get(s, key)
    if v: return v
    return de

def land_ini_get_int(LandIniFile *ini,
    char const *section, char const *key, int de) -> int:
    char const *s = land_ini_get_string(ini, section, key, None)
    if s == None: return de
    return strtol(s, None, 0)

def land_ini_get_number_of_entries(LandIniFile *ini,
    char const *section) -> int:
    LandIniSection *s = ini->sections
    if not s: return 0
    if section:
        s = _get(s, section)
        if not s: return 0
    return land_array_count(s.entries)

def land_ini_get_nth_entry(LandIniFile *ini, char const *section,
        int i) -> char const *:
    """
    Get the n-th entry of an ini section. If section is None get the
    n-th section instead.
    """
    LandIniSection *s = ini->sections
    if section:
        s = _get(s, section)
    LandIniEntry *e = land_array_get_nth(s.entries, i)
    return e.key

static def is_whitespace(char c) -> bool:
    if c == ' ' or c == '\t' or c == '\n': return true
    return false

static macro addc(var, l):
    var[l] = c;
    if l < (int)sizeof(var) - 1: l++
    var[l] = '\0'

static enum State:
    OUTSIDE
    SECTION
    KEY
    EQUALS
    VALUE
    COMMENT

def land_ini_read(char const *filename) -> LandIniFile *:
    char section_name[1024] = "", key_name[1024] = "", value[1024] = ""
    int slen = 0, klen = 0, vlen = 0
    State state = OUTSIDE
    LandIniFile *ini = land_calloc(sizeof *ini)
    ini->filename = land_strdup(filename)
    ini->sections = _new()
    LandFile *f = land_file_new(filename, "rb")
    if not f: return ini
    int done = 0
    while not done:
        int c = land_file_getc(f)
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
            if c == ']' or c == '\n':
                state = OUTSIDE
            else:
                addc(section_name, slen)

        elif state == KEY: # key name
            if c == '\n': state = OUTSIDE
            elif c == '=': state = EQUALS
            else: addc(key_name, klen)

        elif state == EQUALS: # = sign
            if c == '\n':
                value[0] = 0
                goto got_value
            if not is_whitespace(c):
                state = VALUE
                vlen = 0
                addc(value, vlen)

        elif state == VALUE: # key value
            if c == '\n':
                label got_value

                # remove trailing whitespace
                int trailing = strlen(key_name)
                while trailing > 1:
                    trailing--
                    if is_whitespace(key_name[trailing]):
                        key_name[trailing] = 0;
                    else:
                        break

                land_ini_set_string(ini, section_name, key_name, value)
                state = OUTSIDE
            else:
                addc(value, vlen)
        
        elif state == COMMENT: # key value
            if c == '\n':
                state = OUTSIDE

    land_file_destroy(f)
    return ini

def land_ini_new(char const *filename) -> LandIniFile *:
    LandIniFile *ini = land_calloc(sizeof *ini)
    ini->filename = land_strdup(filename)
    ini->sections = _new()
    return ini

def land_ini_destroy(LandIniFile *ini):
    for LandIniEntry *e in LandArray *ini.sections->entries:
        LandIniSection *s = e.val
        _del(s)
        e.val = None

    _del(ini->sections)
    land_free(ini->filename)
    land_free(ini)

def land_ini_writeback(LandIniFile *ini):
    FILE *f = fopen(ini->filename, "wb")
    if not f: return
    LandIniSection *ss = ini.sections
    for LandIniEntry *es in LandArray *ss.entries:
        LandIniSection *s = es.val
        char *name = es.key
        if name and name[0]:
            fprintf(f, "[%s]\n", name)
        for LandIniEntry *e in LandArray *s.entries:
            if e.val:
                fprintf(f, "%s = %s\n", e.key, (char *)e.val)
    fclose(f)

def land_ini_app_settings(char const *appname) -> LandIniFile *:
    char *name = platform_get_app_settings_file(appname)
    LandIniFile *ini = land_ini_read(name)
    land_free(name)
    return ini

