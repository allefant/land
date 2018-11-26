import land.land
import land.widget

str colors = """
maroon/2
maroon
saddlebrown/2
dark goldenrod/2
olive
dark olivegreen/2
dark green/2
teal
dark slategray/2
deepskyblue/2
midnightblue/2
indigo/2
purple/2
black
rosybrown/2
dark red
saddlebrown
moccasin/2
goldenrod
dark olivegreen
dark green
medium seagreen
teal/2
steelblue
navy
indigo
medium violetred/2
dimgray/2
brown
firebrick
chocolate
dark goldenrod
dark khaki
green
forestgreen
light seagreen
dark slategray
slategray
midnightblue
rebeccapurple
purple
dimgray
sequoia
sienna
peru
tan
khaki
olivedrab
seagreen
medium aquamarine
dark cyan
light slategray
medium blue
dark violet
dark magenta
gray
crimson
red
dark orange
gold
palegoldenrod
yellowgreen
dark seagreen
medium turquoise
cadetblue
dodgerblue
dark slateblue
thistle/2
medium violetred
dark gray
indianred
orangered
sandybrown
wheat
moccasin
chartreuse
limegreen
turquoise
dark turquoise
cornflowerblue
blue
blueviolet
deeppink
silver
rosybrown
tomato
orange
navajowhite
papayawhip
greenyellow
light green
medium springgreen
skyblue
deepskyblue
slateblue
dark orchid
magenta
light gray
light coral
salmon
burlywood
bisque
oldlace
beige
lime
cyan
light blue
light steelblue
royalblue
medium orchid
palevioletred
gainsboro
light pink
coral
peachpuff
antiquewhite
yellow
light goldenrodyellow
springgreen
aquamarine
powderblue
light skyblue
medium slateblue
violet
orchid
whitesmoke
pink
dark salmon
linen
blanchedalmond
cornsilk
light yellow
palegreen
azure
paleturquoise
aliceblue
medium purple
plum
hotpink
snow
mistyrose
light salmon
seashell
floralwhite
lemonchiffon
ivory
honeydew
mintcream
light cyan
ghostwhite
lavender
thistle
lavenderblush
white
"""

LandHash *color_names
LandWidgetInterface *_interface
def _draw(LandWidget *w):
    float l, t, r, b
    land_widget_inner_extents(w, &l, &t, &r, &b)
    str cname = land_widget_get_property(w, "color")
    LandColor c = land_color_name(cname)
    land_color_set(c)
    land_filled_rectangle(l, t, r, b)

def _init_names:
    if not color_names:
        color_names = land_hash_new()
        LandArray* a = land_split(colors, "\n")
        for char* c in a:
            if not c or not c[0]: continue
            LandColor color = land_color_name(c)
            int cint = land_color_to_int(color)
            char key[100]
            sprintf(key, "%d", cint)
            land_hash_insert(color_names, key, land_strdup(c))
        land_array_destroy_with_strings(a)

def color_picker_new(void (*clicked)(LandWidget *w)) -> LandWidget*:
    
    LandWidget* view = land_widget_panel_new(None, 0, 0, 72 * 14, 72 * 11)
    LandWidget* vbox = land_widget_vbox_new(view, 0, 0, 0, 0)
    land_widget_vbox_set_columns(vbox, 14)
    if not _interface:
        _interface = land_widget_copy_interface(land_widget_button_interface, "color")
        _interface.draw = _draw
    LandArray* a = land_split(colors, "\n")
    for char* c in a:
        if not c or not c[0]: continue
        LandWidget* button = land_widget_button_new(vbox, c, clicked, 0, 0, 72, 72)
        button.vt = _interface
        land_widget_set_property(button, "color", land_strdup(c), None)
        land_widget_theme_set_minimum_size_for_contents(button, 72, 72)
    land_array_destroy_with_strings(a)
    return view

def color_picker_find_name(int c) -> str:
    _init_names()
    char key[100]
    sprintf(key, "%d", c)
    str r = land_hash_get(color_names, key)
    return r
