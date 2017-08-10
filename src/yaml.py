import land.array, land.hash, land.mem
static import land.config
import yaml.external
import yaml.internal
import yaml.xml

enum LandYamlEntryType:
    YamlScalar
    YamlSequence
    YamlMapping

class LandYamlEntry:
    int type # LandYamlEntryType

    char *scalar
    LandArray *sequence # in case of mapping this has the keys, in order
    LandHash *mapping

class LandYaml:
    char *filename
    LandYamlEntry *root

    char *key
    LandYamlEntry *parent
    LandArray *parents
    bool expect_key

def land_yaml_get_mapping(LandYamlEntry *self) -> LandHash *:
    assert(self.type == YamlMapping)
    return self.mapping

def land_yaml_get_if_mapping(LandYamlEntry *self) -> LandHash *:
    if not self or self.type != YamlMapping: return None
    return self.mapping

def land_yaml_get_sequence(LandYamlEntry *self) -> LandArray *:
    assert(self.type == YamlSequence)
    return self.sequence

def land_yaml_get_scalar(LandYamlEntry *self) -> char const *:
    assert(self.type == YamlScalar)
    return self.scalar

def land_yaml_get_if_scalar(LandYamlEntry *self) -> char const *:
    if not self or self.type != YamlScalar: return None
    return self.scalar

def land_yaml_get_scalar_int(LandYamlEntry *self) -> int:
    if not self: return 0
    return strtol(self.scalar, None, 0)

def land_yaml_get_scalar_double(LandYamlEntry *self) -> double:
    return strtod(self.scalar, None)

def land_yaml_get_scalar_nth(LandArray *s, int i) -> char const *:
    return land_yaml_get_scalar(land_array_get_nth(s, i))

def land_yaml_get_scalar_nth_double(LandArray *s, int i) -> double:
    return land_yaml_get_scalar_double(land_array_get_nth(s, i))

def land_yaml_get_entry(LandYamlEntry *self, char const *name) -> LandYamlEntry *:
    return land_hash_get(self.mapping, name)

def land_yaml_get_entry_scalar(LandYamlEntry *self, char const *name) -> char const *:
    return land_yaml_get_if_scalar(land_yaml_get_entry(self, name))

def land_yaml_get_entry_int(LandYamlEntry *self,
        char const *name) -> int:
    return land_yaml_get_scalar_int(land_yaml_get_entry(self, name))

def land_yaml_get_entry_double(LandYamlEntry *self,
        char const *name) -> double:
    return land_yaml_get_scalar_double(land_yaml_get_entry(self, name))

def land_yaml_get_nth(LandYamlEntry *self, int i) -> LandYamlEntry *:
    return land_array_get_nth(land_yaml_get_sequence(self), i)

def land_yaml_get_nth_int(LandYamlEntry *self, int i) -> int:
    return land_yaml_get_scalar_int(
        land_array_get_nth(land_yaml_get_sequence(self), i))

def land_yaml_get_nth_double(LandYamlEntry *self, int i) -> double:
    return land_yaml_get_scalar_double(
        land_array_get_nth(land_yaml_get_sequence(self), i))

def land_yaml_get_entry_sequence(LandYamlEntry *self, char const *name) -> LandArray*:
    return land_yaml_get_sequence(land_yaml_get_entry(self, name))

def land_yaml_new(char const *filename) -> LandYaml *:
    LandYaml *yaml
    land_alloc(yaml)
    yaml.filename = land_strdup(filename)
    yaml.parents = land_array_new()
    return yaml

static def _add_entry(LandYaml *yaml, LandYamlEntry *entry):
    if yaml.parent:
        if yaml.parent->type == YamlSequence:
            land_array_add(yaml.parent->sequence, entry)
        elif yaml.parent->type == YamlMapping:
            land_hash_insert(yaml.parent->mapping, yaml.key, entry)
            land_array_add(yaml.parent->sequence, land_strdup(yaml.key))
            yaml.expect_key = True
            land_free(yaml.key)
            yaml.key = None
    else:
        yaml.root = entry

    if entry.type == YamlSequence:
        land_array_add(yaml.parents, yaml.parent)
        yaml.parent = entry
        yaml.expect_key = False
    elif entry.type == YamlMapping:
        land_array_add(yaml.parents, yaml.parent)
        yaml.parent = entry
        yaml.expect_key = True

def land_yaml_add_mapping(LandYaml *yaml):
    """
After calling this, use land_yaml_add_scalar to add a key, and then
land_yaml_add_* to add a value. Repeat to add the 2nd and more map entries.
Use land_yaml_done when done.
    """
    LandYamlEntry *entry
    land_alloc(entry)
    entry.type = YamlMapping
    entry.mapping = land_hash_new()
    entry.sequence = land_array_new()
    _add_entry(yaml, entry)

def land_yaml_done(LandYaml *yaml):
    """
Call this when done with a mapping or sequence.
"""
    yaml.expect_key = False
    yaml.parent = land_array_pop(yaml.parents)
    if yaml.parent and yaml.parent->type == YamlMapping: yaml.expect_key = True

def land_yaml_add_sequence(LandYaml *yaml):
    """
After calling this, use land_yaml_add_* to add sequence items,
then land_yaml_done when the sequence is done.
"""
    LandYamlEntry *entry
    land_alloc(entry)
    entry.type = YamlSequence
    entry.sequence = land_array_new()
    _add_entry(yaml, entry)

def land_yaml_add_scalar(LandYaml *yaml, char const *v):
    """
Call this to add an item to a sequence, a key to a mapping, or a value to
a mapping.
"""
    if yaml.expect_key:
        yaml.expect_key = False
        yaml.key = strdup(v)
    else:
        LandYamlEntry *entry
        land_alloc(entry)
        entry.type = YamlScalar
        entry.scalar = land_strdup(v)
        _add_entry(yaml, entry)

def land_yaml_add_scalar_v(LandYaml *yaml, char const *v, va_list args):
    va_list args2
    va_copy(args2, args)
    int n = vsnprintf(None, 0, v, args2)
    va_end(args2)
    if n < 0: n = 1023
    char s[n + 1]
    vsnprintf(s, n + 1, v, args)
    land_yaml_add_scalar(yaml, s)

def land_yaml_add_scalar_f(LandYaml *yaml, char const *v, ...):
    va_list args
    va_start(args, v)
    land_yaml_add_scalar_v(yaml, v, args)
    va_end(args)

static def _destroy_entry(LandYamlEntry *self):
    if self.type == YamlScalar:
        land_free(self.scalar)
    elif self.type == YamlSequence:
        for int i = 0 while i < land_array_count(self.sequence) with i++:
            _destroy_entry(land_array_get_nth(self.sequence, i))
        land_array_destroy(self.sequence)
    elif self.type == YamlMapping:
        for char *key in LandArray *self.sequence:
            _destroy_entry(land_hash_get(self.mapping, key))
            land_free(key)
        land_array_destroy(self.sequence)
        land_hash_destroy(self.mapping)
    land_free(self)

static def _indent(int indent):
    for int i in range(indent):
        printf("    ")

static def land_yaml_dump_entry(LandYamlEntry *self, int indent):
    if not self:
        return
    if self.type == YamlScalar:
        _indent(indent)
        printf("%s\n", self.scalar)
    elif self.type == YamlSequence:
        for int i = 0 while i < land_array_count(self.sequence) with i++:
            _indent(indent)
            printf("-\n")
            land_yaml_dump_entry(land_array_get_nth(self.sequence, i), indent + 1)
    elif self.type == YamlMapping:
        LandArray *keys = self.sequence
        for int i = 0 while i < land_array_count(keys) with i++:
            char const *key = land_array_get_nth(keys, i)
            _indent(indent)
            printf("%s:\n", key)
            land_yaml_dump_entry(land_hash_get(self.mapping, key), indent + 1)

def land_yaml_destroy(LandYaml *self):
    _destroy_entry(self.root)
    land_array_destroy(self.parents)
    land_free(self.filename)
    land_free(self)

def land_yaml_dump(LandYaml *self):
    land_yaml_dump_entry(self.root, 0)
