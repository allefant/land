*** "ifndef" LAND_USE_EXTERNAL_YAML
import land.land
import land.yaml
static import global yaml

class YamlParser:
    LandFile *file

def land_yaml_load(char const *filename) -> LandYaml *:
    LandFile *f = land_file_new(filename, "rb")
    if not f:
        return None
    LandYaml *yaml = land_yaml_new(filename)
    LandBuffer *value = land_buffer_new()

    while True:
        int c = land_file_getc(f)

        if c < 0 or strchr("{}[],:", c):
            if value.n:
                land_buffer_add_char(value, 0)
                land_yaml_add_scalar(yaml, land_strdup(value.buffer))
                land_buffer_clear(value)

        if c < 0: break
        if c == '{': land_yaml_add_mapping(yaml)
        elif c == '[': land_yaml_add_sequence(yaml)
        elif c == '}': land_yaml_done(yaml)
        elif c == ']': land_yaml_done(yaml)
        elif c == ',': pass
        elif c == ':': pass
        else: land_buffer_add_char(value, c)

    land_file_destroy(f)
    land_buffer_destroy(value)
    return yaml

static def _save_mapping(LandYamlEntry *e, YamlParser *p) -> bool:
    land_file_printnn(p.file, "{")
    bool prev = False
    for char const *key in LandArray *e.sequence:
        if prev: land_file_printnn(p.file, ",")
        land_file_printnn(p.file, "%s:", key)
        _save_entry(land_hash_get(e.mapping, key), p)
        prev = True
    land_file_printnn(p.file, "}")
    return true

static def _save_sequence(LandYamlEntry *e, YamlParser *p) -> bool:
    land_file_printnn(p.file, "[")
    bool prev = False
    for LandYamlEntry *e2 in LandArray *e.sequence:
        if prev: land_file_printnn(p.file, ",")
        _save_entry(e2, p)
        prev = True
    land_file_printnn(p.file, "]")
    return true

static def _save_scalar(LandYamlEntry *e, YamlParser *p) -> bool:
    land_file_printnn(p.file, e.scalar)
    return True

static def _save_entry(LandYamlEntry *e, YamlParser *p) -> bool:
    if e->type == YamlMapping:
        return _save_mapping(e, p)
    elif e->type == YamlSequence:
        return _save_sequence(e, p)
    elif e->type == YamlScalar:
        return _save_scalar(e, p)
    return false

def land_yaml_save(LandYaml *yaml):
    LandFile *f = land_file_new(yaml.filename, "wb")
    if not f:
        goto error

    YamlParser p
    p.file = f
    
    if not _save_entry(yaml.root, &p): goto error

    label error
   
    if f: land_file_destroy(f)

*** "endif"
