global *** "ifndef" LAND_USE_EXTERNAL_YAML
*** "ifndef" LAND_USE_EXTERNAL_YAML
import land.land
import land.yaml

enum LandYamlFlags:
    LandYamlPretty = 1

class YamlParser:
    LandFile *file
    int line_length
    int flags
    int indent
    bool cannot_break # whatever is written next cannot start on a new line
    
def land_yaml_load(char const *filename) -> LandYaml *:
    LandFile *f = land_file_new(filename, "rb")
    if not f:
        land_log_message("Failed opening %s\n", filename)
        return None
    land_log_message("Parsing yaml %s\n", filename)
    LandYaml *yaml = land_yaml_new(filename)
    LandBuffer *value = land_buffer_new()
    bool ignore_whitespace = True

    while True:
        int c = land_file_getc(f)
        if ignore_whitespace:
            if c == ' ': continue
            if c == '\n': continue
        ignore_whitespace = False
        if c < 0 or strchr("{}[],:\n", c):
            if value.n:
                land_buffer_add_char(value, 0)
                land_yaml_add_scalar(yaml, land_strdup(value.buffer))
                land_buffer_clear(value)

        if c < 0: break
        if c == '{':
            land_yaml_add_mapping(yaml)
            ignore_whitespace = True
        elif c == '[':
            land_yaml_add_sequence(yaml)
            ignore_whitespace = True
        elif c == '}':
            land_yaml_done(yaml)
            ignore_whitespace = True
        elif c == ']':
            land_yaml_done(yaml)
            ignore_whitespace = True
        elif c == ',':
            ignore_whitespace = True
        elif c == ':':
            ignore_whitespace = True
        elif c == '\n': pass
        else: land_buffer_add_char(value, c)

    land_file_destroy(f)
    land_buffer_destroy(value)
    yaml.current = yaml.root
    return yaml

def _yaml_write(YamlParser *p, char const *s):
    if not s:
        s = "null"
    int n = strlen(s)
    if not p.cannot_break:
        if p.line_length + n > 80:
            land_file_write(p.file, "\n", 1)
            p.line_length = 0
    p.cannot_break = False
    land_file_write(p.file, s, n)
    p.line_length += n

static def yaml_write(YamlParser *p, char const *s):
    _yaml_write(p, s)

def _pretty_newline(YamlParser *p):
    if p.flags & LandYamlPretty:
        yaml_write(p, "\n")
        p.line_length = 0
        for int i in range(p.indent):
            yaml_write(p, "    ")

static def _save_mapping(LandYamlEntry *e, YamlParser *p) -> bool:
    yaml_write(p, "{")
    p.indent += 1
    bool prev = False
    for char const *key in LandArray *e.sequence:
        if prev: yaml_write(p, ",")
        _pretty_newline(p)
        _yaml_write(p, key)
        p.cannot_break = True
        _yaml_write(p, ": ") # YAML specs say colon-space (not just colon) must be used as separator
        p.cannot_break = True
        _save_entry(land_hash_get(e.mapping, key), p)
        prev = True
    p.indent -= 1
    _pretty_newline(p)
    yaml_write(p, "}")
    return true

static def _save_sequence(LandYamlEntry *e, YamlParser *p) -> bool:
    yaml_write(p, "[")
    p.indent += 1
    bool prev = False
    for LandYamlEntry *e2 in LandArray *e.sequence:
        if prev: yaml_write(p, ",")
        if p.indent < 2: _pretty_newline(p)
        _save_entry(e2, p)
        prev = True
    p.indent -= 1
    _pretty_newline(p)
    yaml_write(p, "]")
    return true

static def _save_scalar(LandYamlEntry *e, YamlParser *p) -> bool:
    yaml_write(p, e.scalar)
    return True

static def _save_entry(LandYamlEntry *e, YamlParser *p) -> bool:
    if e->type == YamlMapping:
        return _save_mapping(e, p)
    elif e->type == YamlSequence:
        return _save_sequence(e, p)
    elif e->type == YamlScalar:
        return _save_scalar(e, p)
    return false

def land_yaml_save_flags(LandYaml *yaml, int flags):
    LandFile *f = land_file_new(yaml.filename, "wb")
    YamlParser *p = None
    if not f:
        goto error

    land_alloc(p)
    p.file = f
    p.flags = flags
    
    if not _save_entry(yaml.root, p):
        goto error

    label error
    if p: land_free(p)
    if f: land_file_destroy(f)

def land_yaml_save(LandYaml *yaml):
    land_yaml_save_flags(yaml, 0)

*** "endif"
global *** "endif"
