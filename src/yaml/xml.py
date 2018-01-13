import land.land
import land.yaml
import global ctype

static enum XmlState:
    Outside
    ElementName
    Attributes
    AttributeName
    AttributeStart
    AttributeValue

static class XmlParser:
    XmlState state
    bool closing
    LandBuffer *value
    LandYaml *yaml

static def scalar(XmlParser *x):
    land_buffer_add_char(x.value, 0)
    land_yaml_add_scalar(x.yaml, land_strdup(x.value.buffer))
    land_buffer_clear(x.value)

static def opt_scalar(XmlParser *x):
    if x.value.n:
        scalar(x)

static def discard_scalar(XmlParser *x):
    land_buffer_clear(x.value)

#
# <a x="2">b<c>d</c>e<f y="3"/></a>
#
# [{"<":"a", "x":"2", ">":["b", {"<":"c", ">":["d"]}, "e", {"<":f", "y":"3"}]}]
#
#
def land_yaml_load_xml(str filename) -> LandYaml *:
    LandFile *f = land_file_new(filename, "rb")
    if not f:
        land_log_message("Failed opening %s\n", filename)
        return None
    land_log_message("Parsing yaml %s\n", filename)
    XmlParser x_
    XmlParser *x = &x_
    x.yaml = land_yaml_new(filename)
    x.value = land_buffer_new()
    x.state = Outside
    x.closing = False

    land_yaml_add_sequence(x.yaml) # root list of elements

    while True:
        int c = land_file_getc(f)
        if c < 0:
            break
        if x.state == Outside:
            if c == '<':
                opt_scalar(x)
                x.state = ElementName
                continue
        elif x.state == ElementName:
            if c == '/':
                x.closing = True
                continue
            elif c == '>':
                if x.closing:
                    discard_scalar(x)
                    close_tag(x)
                    land_yaml_done(x.yaml) # content
                else:
                    create_tag(x)
                    open_tag(x) # no attributes
                continue
            elif isspace(c):
                create_tag(x)
                x.state = Attributes
                continue
        elif x.state == Attributes:
            if isspace(c):
                continue
            elif c == '/':
                x.closing = True
                continue
            elif c == '?': # to deal with the XML header
                x.closing = True
                continue
            elif c == '>':
                if x.closing:
                    close_tag(x)
                else:
                    open_tag(x)
                continue
            elif c == '=':
                scalar(x)
                x.state = AttributeStart
                continue
        elif x.state == AttributeStart:
            if c == '"':
                x.state = AttributeValue
            continue
        elif x.state == AttributeValue:
            if c == '"':
                x.state = Attributes
                scalar(x)
                continue

        add_char(x, c)

    land_yaml_done(x.yaml) # root list of elements

    land_file_destroy(f)
    land_buffer_destroy(x.value)
    return x.yaml

static def add_char(XmlParser *x, char c):
    land_buffer_add_char(x.value, c)

static def create_tag(XmlParser *x):
    land_yaml_add_mapping(x.yaml) # tag mapping
    land_yaml_add_scalar(x.yaml, land_strdup("<"))
    scalar(x)

static def open_tag(XmlParser *x):
    x.state = Outside
    land_yaml_add_scalar(x.yaml, land_strdup(">"))
    land_yaml_add_sequence(x.yaml) # content

static def close_tag(XmlParser *x):
    land_yaml_done(x.yaml) # tag mapping
    x.state = Outside
    x.closing = False

# saving XML

static def xml_write(YamlParser *p, char const *s, bool can_break_before):
    int n = strlen(s)
    if can_break_before and p.line_length + n > 80:
        land_file_write(p.file, "\n", 1)
        p.line_length = 0
    land_file_write(p.file, s, n)
    int i = land_find(s, "\n")
    if i >= 0:
        p.line_length = n - 1 - i
    else:
        p.line_length += n

static def xml_save_mapping(LandYamlEntry *e, YamlParser *p) -> bool:
    str name = land_yaml_get_entry_scalar(e, "<")
    if not name: return False

    xml_write(p, "<", False)
    xml_write(p, name, False)

    for char const *key in LandArray *e.sequence:
        if land_equals(key, "<") or land_equals(key, ">"): continue
        xml_write(p, " ", False)
        xml_write(p, key, True)
        xml_write(p, "=\"", False)
        str value = land_yaml_get_entry_scalar(e, key)
        xml_write(p, value, False)
        xml_write(p, "\"", False)

    LandYamlEntry *contents = land_yaml_get_entry(e, ">")
    if contents:
        xml_write(p, ">", True)
        xml_save_sequence(contents, p)
        
        xml_write(p, "</", False)
        xml_write(p, name, False)
        xml_write(p, ">", True)
    else:
        xml_write(p, " />", True)

    return True

static def xml_save_sequence(LandYamlEntry *e, YamlParser *p) -> bool:
    for LandYamlEntry *e2 in LandArray *e.sequence:
        xml_save_entry(e2, p)
    return True

static def xml_save_scalar(LandYamlEntry *e, YamlParser *p) -> bool:
    xml_write(p, e.scalar, False)
    return True

static def xml_save_entry(LandYamlEntry *e, YamlParser *p) -> bool:
    if e.type == YamlMapping:
        return xml_save_mapping(e, p)
    elif e.type == YamlSequence:
        return xml_save_sequence(e, p)
    elif e.type == YamlScalar:
        return xml_save_scalar(e, p)
    return false

def land_yaml_save_xml(LandYaml *yaml):
    LandFile *f = land_file_new(yaml.filename, "wb")
    if not f:
        goto error

    YamlParser p
    memset(&p, 0, sizeof p)
    p.file = f
    
    if not xml_save_entry(yaml.root, &p): goto error

    label error

    if f: land_file_destroy(f)

def _xml(LandYaml *yaml):
    if not yaml.root or not yaml.parent:
        land_yaml_add_sequence(yaml)
    elif yaml.parent->type == YamlMapping:
        land_yaml_add_scalar(yaml, ">")
        land_yaml_add_sequence(yaml)

def land_yaml_xml_tag(LandYaml *yaml, str name):
    _xml(yaml)
    land_yaml_add_mapping(yaml)
    land_yaml_add_scalar(yaml, "<")
    land_yaml_add_scalar(yaml, name)

def land_yaml_xml_content(LandYaml *yaml, str content):
    _xml(yaml)
    land_yaml_add_scalar(yaml, content)

def land_yaml_xml_attribute(LandYaml *yaml, str key, value):
    land_yaml_add_scalar(yaml, key)
    land_yaml_add_scalar(yaml, value)

def land_yaml_xml_end(LandYaml *yaml):
    land_yaml_done(yaml)
    # If we close a tag, we close the mapping, so additional children
    # can be added. When we close the parent, we just closed the
    # sequence, but we also need to close the mapping. Basically we
    # always need to be in a sequence after this function returns.
    if yaml.parent and yaml.parent->type == YamlMapping:
        land_yaml_done(yaml)
