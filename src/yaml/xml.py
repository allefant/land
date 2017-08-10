import land.land
import land.yaml
import global ctype

static enum State:
    Outside
    ElementName
    Attributes
    AttributeName
    AttributeStart
    AttributeValue

static class XmlParser:
    State state
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
