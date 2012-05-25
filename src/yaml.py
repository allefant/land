import land.array, land.hash, land.mem
static import global yaml

union LandYamlDataType:
    char *scalar
    LandArray *sequence
    LandHash *mapping

class LandYAMLEntry:
    int type # 0=scalar, 1=sequence, 2=mapping
    LandYamlDataType data

class LandYAML:
    LandYAMLEntry *root

LandYAML *def land_yaml_load(char const *filename):
    yaml_parser_t parser
    FILE *f = fopen(filename, "rb")

    if f:
        LandYAML *yaml; land_alloc(yaml)
        LandYAMLEntry *entry = None
        LandYAMLEntry *parent = None
        LandArray *parents = land_array_new()

        bool expect_key = False
        char *key = None

        yaml_parser_initialize(&parser)
        yaml_parser_set_input_file(&parser, f)
        while True:
            yaml_event_t event
            if not yaml_parser_parse(&parser, &event): break

            if event.type == YAML_MAPPING_START_EVENT:
                land_alloc(entry)
                entry->type = 2
                entry->data.mapping = land_hash_new()
            elif event.type == YAML_SEQUENCE_START_EVENT:
                land_alloc(entry)
                entry->type = 1
                entry->data.sequence = land_array_new()
            elif event.type == YAML_SCALAR_EVENT:
                char const *v = (void *)event.data.scalar.value

                if expect_key:
                    expect_key = False
                    key = strdup(v)
                else:
                    land_alloc(entry)
                    entry->type = 0
                    entry->data.scalar = strdup(v)

            elif event.type == YAML_MAPPING_END_EVENT:
                expect_key = False
                parent = land_array_pop(parents)
                if parent and parent->type == 2: expect_key = True
            elif event.type == YAML_SEQUENCE_END_EVENT:
                parent = land_array_pop(parents)
                if parent and parent->type == 2: expect_key = True
            elif event.type == YAML_STREAM_END_EVENT:
                yaml_event_delete(&event)
                break

            if entry:
                if parent:
                    if parent->type == 1:
                        land_array_add(parent->data.sequence, entry)
                    elif parent->type == 2:
                        land_hash_insert(parent->data.mapping, key, entry)
                        expect_key = True
                        key = None
                else:
                    yaml->root = entry
                
                if entry->type == 1:
                    land_array_add(parents, parent)
                    parent = entry
                    expect_key = False
                elif entry->type == 2:
                    land_array_add(parents, parent)
                    parent = entry
                    expect_key = True
                entry = None

            yaml_event_delete(&event)
        
        land_array_destroy(parents)
        
        yaml_parser_delete(&parser)
        fclose(f)

        return yaml
    return None

static def land_yaml_destroy_entry(LandYAMLEntry *self):
    if self->type == 0:
        land_free(self->data.scalar)
    elif self->type == 1:
        for int i = 0 while i < land_array_count(self->data.sequence) with i++:
            land_yaml_destroy_entry(land_array_get_nth(self->data.sequence, i))
        land_array_destroy(self->data.sequence)
    elif self->type == 2:
        LandArray *keys = land_hash_keys(self->data.mapping)
        for int i = 0 while i < land_array_count(keys) with i++:
            char const *key = land_array_get_nth(keys, i)
            land_yaml_destroy_entry(land_hash_get(self->data.mapping, key))
        land_hash_destroy(self->data.mapping)
        land_array_destroy(keys)
    land_free(self)

def land_yaml_destroy(LandYAML *self):
    land_yaml_destroy_entry(self->root)
    land_free(self)

static def land_yaml_dump_entry(LandYAMLEntry *self, int indent):
    if self->type == 0:
        for int i = 0 while i < indent with i++: printf("    ")
        printf("%s\n", self->data.scalar)
    elif self->type == 1:
        for int i = 0 while i < land_array_count(self->data.sequence) with i++:
            for int j = 0 while j < indent with j++: printf("    ")
            printf("-\n")
            land_yaml_dump_entry(land_array_get_nth(self->data.sequence, i), indent + 1)
    elif self->type == 2:
        LandArray *keys = land_hash_keys(self->data.mapping)
        for int i = 0 while i < land_array_count(keys) with i++:
            char const *key = land_array_get_nth(keys, i)
            for int j = 0 while j < indent with j++: printf("    ")
            printf("%s:\n", key)
            land_yaml_dump_entry(land_hash_get(self->data.mapping, key), indent + 1)
        land_array_destroy(keys)

def land_yaml_dump(LandYAML *self):
    land_yaml_dump_entry(self->root, 0)
