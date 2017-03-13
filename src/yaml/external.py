global *** "ifdef" LAND_USE_EXTERNAL_YAML
*** "ifdef" LAND_USE_EXTERNAL_YAML
import land.yaml
static import global yaml if defined LAND_USE_EXTERNAL_YAML

def land_yaml_load(char const *filename) -> LandYaml *:
    yaml_parser_t parser
    FILE *f = fopen(filename, "rb")

    if not f:
        return None

    LandYaml *yaml = land_yaml_new(filename)

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

static def _save_mapping(LandYamlEntry *e, yaml_emitter_t *emitter) -> bool:
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

static def _save_sequence(LandYamlEntry *e, yaml_emitter_t *emitter) -> bool:
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

static def _save_scalar(LandYamlEntry *e, yaml_emitter_t *emitter) -> bool:
    yaml_event_t event

    memset(&event, 0, sizeof event)
    if not yaml_scalar_event_initialize(&event, None, None, (void *)e.scalar,
        -1, 1, 1, YAML_PLAIN_SCALAR_STYLE): return false
    if not yaml_emitter_emit(emitter, &event): return false
    return true

static def _save_entry(LandYamlEntry *e, yaml_emitter_t *emitter) -> bool:
    if e->type == Mapping:
        return _save_mapping(e, emitter)
    elif e->type == Sequence:
        return _save_sequence(e, emitter)
    elif e->type == Scalar:
        return _save_scalar(e, emitter)
    return false

def land_yaml_save(LandYaml *yaml):
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

*** "endif"
global *** "endif"
