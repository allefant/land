import land.array, land.hash, land.mem
static import land.config
*** "ifdef" LAND_HAVE_YAML_H
static import global yaml

static enum LandYAMLEntryType:
    Scalar
    Sequence
    Mapping

class LandYAMLEntry:
    int type # LandYAMLEntryType

    char *scalar
    LandArray *sequence # in case of mapping this has the keys, in order
    LandHash *mapping

class LandYAML:
    char *filename
    LandYAMLEntry *root

    char *key
    LandYAMLEntry *parent
    LandArray *parents
    bool expect_key

def land_yaml_get_mapping(LandYAMLEntry *self) -> LandHash *:
    assert(self.type == Mapping)
    return self.mapping

def land_yaml_get_sequence(LandYAMLEntry *self) -> LandArray *:
    assert(self.type == Sequence)
    return self.sequence

def land_yaml_get_scalar(LandYAMLEntry *self) -> char const *:
    assert(self.type == Scalar)
    return self.scalar

def land_yaml_get_scalar_int(LandYAMLEntry *self) -> int:
    return strtol(self.scalar, None, 0)

def land_yaml_get_scalar_double(LandYAMLEntry *self) -> double:
    return strtod(self.scalar, None)

def land_yaml_get_scalar_nth(LandArray *s, int i) -> char const *:
    return land_yaml_get_scalar(land_array_get_nth(s, i))

def land_yaml_get_scalar_nth_double(LandArray *s, int i) -> double:
    return land_yaml_get_scalar_double(land_array_get_nth(s, i))

def land_yaml_get_entry(LandYAMLEntry *self, char const *name) -> LandYAMLEntry *:
    return land_hash_get(self.mapping, name)

def land_yaml_get_entry_scalar(LandYAMLEntry *self, char const *name) -> char const *:
    return land_yaml_get_scalar(land_yaml_get_entry(self, name))

def land_yaml_get_entry_int(LandYAMLEntry *self,
        char const *name) -> int:
    return land_yaml_get_scalar_int(land_yaml_get_entry(self, name))

def land_yaml_get_nth(LandYAMLEntry *self, int i) -> LandYAMLEntry *:
    return land_array_get_nth(land_yaml_get_sequence(self), i)

def land_yaml_get_nth_int(LandYAMLEntry *self, int i) -> int:
    return land_yaml_get_scalar_int(
        land_array_get_nth(land_yaml_get_sequence(self), i))

def land_yaml_get_nth_double(LandYAMLEntry *self, int i) -> double:
    return land_yaml_get_scalar_double(
        land_array_get_nth(land_yaml_get_sequence(self), i))

def land_yaml_new(char const *filename) -> LandYAML *:
    LandYAML *yaml
    land_alloc(yaml)
    yaml.filename = land_strdup(filename)
    yaml.parents = land_array_new()
    return yaml

static def _add_entry(LandYAML *yaml, LandYAMLEntry *entry):
    if yaml.parent:
        if yaml.parent->type == Sequence:
            land_array_add(yaml.parent->sequence, entry)
        elif yaml.parent->type == Mapping:
            land_hash_insert(yaml.parent->mapping, yaml.key, entry)
            land_array_add(yaml.parent->sequence, land_strdup(yaml.key))
            yaml.expect_key = True
            land_free(yaml.key)
            yaml.key = None
    else:
        yaml.root = entry

    if entry.type == Sequence:
        land_array_add(yaml.parents, yaml.parent)
        yaml.parent = entry
        yaml.expect_key = False
    elif entry.type == Mapping:
        land_array_add(yaml.parents, yaml.parent)
        yaml.parent = entry
        yaml.expect_key = True

def land_yaml_add_mapping(LandYAML *yaml):
    """
After calling this, use land_yaml_add_scalar to add a key, and then
land_yaml_add_* to add a value. Repeat to add the 2nd and more map entries.
Use land_yaml_done when done.
    """
    LandYAMLEntry *entry
    land_alloc(entry)
    entry.type = Mapping
    entry.mapping = land_hash_new()
    entry.sequence = land_array_new()
    _add_entry(yaml, entry)

def land_yaml_done(LandYAML *yaml):
    """
Call this when done with a mapping or sequence.
"""
    yaml.expect_key = False
    yaml.parent = land_array_pop(yaml.parents)
    if yaml.parent and yaml.parent->type == Mapping: yaml.expect_key = True

def land_yaml_add_sequence(LandYAML *yaml):
    """
After calling this, use land_yaml_add_* to add sequence items,
then land_yaml_done when the sequence is done.
"""
    LandYAMLEntry *entry
    land_alloc(entry)
    entry.type = Sequence
    entry.sequence = land_array_new()
    _add_entry(yaml, entry)

def land_yaml_add_scalar(LandYAML *yaml, char const *v):
    """
Call this to add an item to a sequence, a key to a mapping, or a value to
a mapping.
"""
    if yaml.expect_key:
        yaml.expect_key = False
        yaml.key = strdup(v)
    else:
        LandYAMLEntry *entry
        land_alloc(entry)
        entry.type = Scalar
        entry.scalar = land_strdup(v)
        _add_entry(yaml, entry)

def land_yaml_add_scalar_v(LandYAML *yaml, char const *v, va_list args):
    va_list args2
    va_copy(args2, args)
    int n = vsnprintf(None, 0, v, args2)
    va_end(args2)
    if n < 0: n = 1023
    char s[n + 1]
    vsnprintf(s, n + 1, v, args)
    land_yaml_add_scalar(yaml, s)

def land_yaml_add_scalar_f(LandYAML *yaml, char const *v, ...):
    va_list args
    va_start(args, v)
    land_yaml_add_scalar_v(yaml, v, args)
    va_end(args)

def land_yaml_load(char const *filename) -> LandYAML *:
    yaml_parser_t parser
    FILE *f = fopen(filename, "rb")

    if not f:
        return None

    LandYAML *yaml = land_yaml_new(filename)

    yaml_parser_initialize(&parser)
    yaml_parser_set_input_file(&parser, f)
    while True:
        yaml_event_t event
        if not yaml_parser_parse(&parser, &event): break

        if event.type == YAML_MAPPING_START_EVENT:
            land_yaml_add_mapping(yaml)
        elif event.type == YAML_SEQUENCE_START_EVENT:
            land_yaml_add_sequence(yaml)
        elif event.type == YAML_SCALAR_EVENT:
            char const *v = (void *)event.data.scalar.value
            land_yaml_add_scalar(yaml, v)
        elif event.type == YAML_MAPPING_END_EVENT:
            land_yaml_done(yaml)
        elif event.type == YAML_SEQUENCE_END_EVENT:
            land_yaml_done(yaml)
        elif event.type == YAML_STREAM_END_EVENT:
            yaml_event_delete(&event)
            break

        yaml_event_delete(&event)

    yaml_parser_delete(&parser)
    fclose(f)

    return yaml

static bool def _save_entry(LandYAMLEntry *e, yaml_emitter_t *emitter)

static def _save_mapping(LandYAMLEntry *e, yaml_emitter_t *emitter) -> bool:
    yaml_event_t event

    memset(&event, 0, sizeof event)
    if not yaml_mapping_start_event_initialize(&event, None, None, 1,
        YAML_BLOCK_MAPPING_STYLE): return false
    if not yaml_emitter_emit(emitter, &event): return false

    for char const *key in LandArray *e.sequence:

        memset(&event, 0, sizeof event)
        if not yaml_scalar_event_initialize(&event, None, None, (void *)key,
            -1, 1, 1, YAML_PLAIN_SCALAR_STYLE): return false
        if not yaml_emitter_emit(emitter, &event): return false
        
        _save_entry(land_hash_get(e.mapping, key), emitter)

    memset(&event, 0, sizeof event)
    if not yaml_mapping_end_event_initialize(&event): return false
    if not yaml_emitter_emit(emitter, &event): return false

    return true

static def _save_sequence(LandYAMLEntry *e, yaml_emitter_t *emitter) -> bool:
    yaml_event_t event

    memset(&event, 0, sizeof event)
    if not yaml_sequence_start_event_initialize(&event, None, None, 1,
        YAML_FLOW_SEQUENCE_STYLE): return false
    if not yaml_emitter_emit(emitter, &event): return false
    
    for int i = 0 while i < land_array_count(e.sequence) with i++:
        _save_entry(land_array_get_nth(e.sequence, i), emitter)

    memset(&event, 0, sizeof event)
    if not yaml_sequence_end_event_initialize(&event): return false
    if not yaml_emitter_emit(emitter, &event): return false

    return true

static def _save_scalar(LandYAMLEntry *e, yaml_emitter_t *emitter) -> bool:
    yaml_event_t event

    memset(&event, 0, sizeof event)
    if not yaml_scalar_event_initialize(&event, None, None, (void *)e.scalar,
        -1, 1, 1, YAML_PLAIN_SCALAR_STYLE): return false
    if not yaml_emitter_emit(emitter, &event): return false
    return true

static def _save_entry(LandYAMLEntry *e, yaml_emitter_t *emitter) -> bool:
    if e->type == Mapping:
        return _save_mapping(e, emitter)
    elif e->type == Sequence:
        return _save_sequence(e, emitter)
    elif e->type == Scalar:
        return _save_scalar(e, emitter)
    return false

def land_yaml_save(LandYAML *yaml):
    yaml_event_t event
    yaml_emitter_t emitter
    yaml_emitter_initialize(&emitter)

    FILE *f = fopen(yaml.filename, "wb")
    if not f:
        goto error

    yaml_emitter_set_output_file(&emitter, f)
    
    memset(&event, 0, sizeof event)
    yaml_stream_start_event_initialize(&event, YAML_UTF8_ENCODING);
    if not yaml_emitter_emit(&emitter, &event): goto error

    memset(&event, 0, sizeof event)
    if not yaml_document_start_event_initialize(&event, 0, 0, 0, 1): goto error
    if not yaml_emitter_emit(&emitter, &event): goto error

    if not _save_entry(yaml.root, &emitter): goto error

    memset(&event, 0, sizeof event)
    if not yaml_document_end_event_initialize(&event, 1): goto error
    if not yaml_emitter_emit(&emitter, &event): goto error
    
    memset(&event, 0, sizeof event)
    yaml_stream_end_event_initialize(&event);
    if not yaml_emitter_emit(&emitter, &event): goto error

    label error
    yaml_emitter_delete(&emitter)
    if f: fclose(f)

static def _destroy_entry(LandYAMLEntry *self):
    if self.type == Scalar:
        land_free(self.scalar)
    elif self.type == Sequence:
        for int i = 0 while i < land_array_count(self.sequence) with i++:
            _destroy_entry(land_array_get_nth(self.sequence, i))
        land_array_destroy(self.sequence)
    elif self.type == Mapping:
        for char *key in LandArray *self.sequence:
            _destroy_entry(land_hash_get(self.mapping, key))
            land_free(key)
        land_array_destroy(self.sequence)
        land_hash_destroy(self.mapping)
    land_free(self)

static def land_yaml_dump_entry(LandYAMLEntry *self, int indent):
    if self.type == Scalar:
        for int i = 0 while i < indent with i++: printf("    ")
        printf("%s\n", self.scalar)
    elif self.type == Sequence:
        for int i = 0 while i < land_array_count(self.sequence) with i++:
            for int j = 0 while j < indent with j++: printf("    ")
            printf("-\n")
            land_yaml_dump_entry(land_array_get_nth(self.sequence, i), indent + 1)
    elif self.type == Mapping:
        LandArray *keys = self.sequence
        for int i = 0 while i < land_array_count(keys) with i++:
            char const *key = land_array_get_nth(keys, i)
            for int j = 0 while j < indent with j++: printf("    ")
            printf("%s:\n", key)
            land_yaml_dump_entry(land_hash_get(self.mapping, key), indent + 1)

def land_yaml_destroy(LandYAML *self):
    _destroy_entry(self.root)
    land_array_destroy(self.parents)
    land_free(self.filename)
    land_free(self)

def land_yaml_dump(LandYAML *self):
    land_yaml_dump_entry(self.root, 0)
*** "endif"
