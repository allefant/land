import global land.land
import main
import color_picker

char const* noises[] = {"Voronoi", "Perlin", "Plasma", "White", "Waves"}
char const* lerps[] = {"None", "Linear", "Cosine", "Smooth", "Smoother", "Smoothest"}
char const* warps[] = {"none", "warp"}
char const* blurs[] = {"none", "blur"}

class Dialog:
    Value *preset
    Value *width
    Value *height
    Value *noise
    Value *lerp
    Value *count
    Value *levels
    Value *amplitude
    Value *power_modifier
    Value *randomness
    Value *crispness
    Value *wrap

    Value *warp
    Value *warp_offset_x
    Value *warp_offset_y
    Value *warp_scale_x
    Value *warp_scale_y

    Value *blur
    Value *blur_size

    Value *z_scale
    Value *z_offset
    Value *z_ease

    Value *plateau
    Value *color1
    Value *color2
    Value *color3
    Value *color4
    Value *color5
    Value *color6
    Value *pos0
    Value *pos1
    Value *pos2
    Value *pos3
    Value *pos4
    Value *pos5
    Value *pos6

    Value *seed

    LandWidget *view

class Value:
    LandWidget *label
    LandWidget *spin
    LandWidget *slider
    LandWidget *name
    LandWidget *color
    LandWidget *button
    void *data
    char const**names
    int v
    int initial

LandArray *values
Value* show_picker

def dialog_hide_show(Dialog *self):
    value_show_if(self.warp.v == 1, self.warp_offset_x)
    value_show_if(self.warp.v == 1, self.warp_offset_y)
    value_show_if(self.warp.v == 1, self.warp_scale_x)
    value_show_if(self.warp.v == 1, self.warp_scale_y)

    value_show_if(self.blur.v == 1, self.blur_size)

    value_show_if(self.noise.v == 0, self.count)
    value_show_if(self.noise.v == 0, self.randomness)
    
    value_show_if(self.noise.v == 1, self.lerp)
    value_show_if(self.noise.v == 1 or self.noise.v == 3, self.levels)

def _get_preset_name(Dialog *self) -> char*:
    char name[100]
    sprintf(name, "preset%d.ini", self.preset.v)
    char *path = land_get_save_file("perlin", name)
    return path

def dialog_load(Dialog *self):
    char *name = _get_preset_name(self)
    LandIniFile* ini = land_ini_read(name)
    for Value *value in values:
        str label = land_widget_button_get_text(value.label)
        int v = land_ini_get_int(ini, "values", label, 0)
        value_set(value, v)
    land_ini_destroy(ini)
    land_free(name)

def dialog_save(Dialog *self):
    char *name = _get_preset_name(self)
    LandIniFile* ini = land_ini_new(name)
    for Value *value in values:
        str label = land_widget_button_get_text(value.label)
        land_ini_set_int(ini, "values", label, value.v)
    land_ini_writeback(ini)
    land_ini_destroy(ini)
    land_free(name)

def value_show_if(bool shown, Value *show):
    if not shown:
        land_widget_hide(show.label)
        land_widget_hide(show.spin)
        if show.slider: land_widget_hide(show.slider)
        if show.name: land_widget_hide(show.name)
    else:
        land_widget_unhide(show.label)
        land_widget_unhide(show.spin)
        if show.slider: land_widget_unhide(show.slider)
        if show.name: land_widget_unhide(show.name)

def update_from_spin(LandWidget *w):
    Value *value = land_widget_get_property(w->parent, "value")
    value_set(value, land_widget_spin_get_value(value.spin))
    
def update_from_slider(LandWidget *w):
    Value *value = land_widget_get_property(w->parent, "value")
    value_set(value, land_widget_slider_get_value(value.slider))

def color_picker_clicked(LandWidget *w):
    str cname = land_widget_get_property(w, "color")
    land_widget_unreference(color_picker)
    color_picker = None
    LandColor c = land_color_name(cname)
    value_set(show_picker, land_color_to_int(c))

def update_pick(LandWidget *w):
    Value *value = land_widget_get_property(w, "value")
    show_picker = value
    color_picker = color_picker_new(color_picker_clicked)
    land_widget_reference(color_picker)

def value_set(Value *value, int v):
    value.v = v
    if value.spin: land_widget_spin_set_value(value.spin, value.v)
    if value.slider: land_widget_slider_set_value(value.slider, value.v)
    if value.name: land_widget_button_replace_text(value.name, value.names[value.v])
    if value.color: land_widget_button_replace_text(value.color, color_picker_find_name(v))
    
Value *def value_new(LandWidget *parent, char const *name, int val,
    minval, maxval, step, str* names):
    Value *self
    land_alloc(self)
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)

    self.v = val
    self.initial = val

    if names:
        self.names = names
        self.name = land_widget_text_new(parent, names[(int)val], 0, 0, 0, 1, 1)
        land_widget_button_set_minimum_text(self.name, "Voronoi")
    else:
        self->slider = land_widget_slider_new(parent, minval, maxval, False,
            update_from_slider, 0, 0, 1, 1)
        land_widget_slider_set_value(self.slider, val)
        land_widget_set_property(self->slider, "value", self, None)

    self->spin = land_widget_spin_new(parent, val, minval, maxval, step,
        update_from_spin, 0, 0, 1, 1)
    land_widget_spin_set_minimum_text(self->spin, "99999")
    land_widget_layout_set_shrinking(self->spin, 1, 1)
    land_widget_set_property(self->spin, "value", self, None)

    land_array_add(values, self)
    
    return self

Value *def value_color_new(LandWidget *parent, str name, str val):
    LandColor c = land_color_name(val)
    Value *self
    land_alloc(self)
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)
    self.v = land_color_to_int(c)
    self.initial = self.v
    self.color = land_widget_text_new(parent, val, 0, 0, 0, 1, 1)
    self.button = land_widget_button_new(parent, "pick", update_pick, 0, 0, 0, 0)
    land_widget_set_property(self.button, "value", self, None)
    land_array_add(values, self)
    return self

Value *def value_button_new(LandWidget *parent, str name, void (*click)(LandWidget *)):
    Value *self
    land_alloc(self)
    self.v = 0
    self.initial = self.v
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)
    land_widget_text_new(parent, "", 0, 0, 0, 1, 1)
    self.button = land_widget_button_new(parent, name, click, 0, 0, 0, 0)
    land_array_add(values, self)
    return self

def dialog_new -> Dialog*:
    Dialog *self
    land_alloc(self)
    self.view = land_widget_panel_new(None, 1024, 0, 250, 100)
    land_widget_reference(self.view)

    if values: land_array_destroy(values)
    values = land_array_new()
    
    LandWidget *outer = land_widget_vbox_new(self.view, 0, 0, 100, 100)
    
    LandWidget *vbox = land_widget_vbox_new(outer, 0, 0, 100, 100)
    land_widget_vbox_set_columns(vbox, 3)
    land_widget_layout_set_shrinking(vbox, 0, 1)

    self.preset = value_new(vbox, "preset", 1, 1, 9, 1, None)
    self.width = value_new(vbox, "width", 8, 0, 16, 1, None)
    self.height = value_new(vbox, "height", 8, 0, 16, 1, None)
    self.wrap = value_new(vbox, "wrap", 1, 0, 1, 1, None)
    self.noise = value_new(vbox, "noise", 1, 0, 4, 1, noises)
    self.lerp = value_new(vbox, "lerp", 2, 0, 5, 1, lerps)
    self.count = value_new(vbox, "count", 1, 0, 32, 1, None)
    self.randomness = value_new(vbox, "randomness", 1, 0, 16, 1, None)
    self.levels = value_new(vbox, "levels", 6, 0, 10, 1, None)
    self.amplitude = value_new(vbox, "amplitude", 8, -16, 16, 1, None)
    self.power_modifier = value_new(vbox, "power modifier", 0, -16, 16, 1, None)

    self.warp = value_new(vbox, "warp", 0, 0, 1, 1, warps)
    self.warp_offset_x = value_new(vbox, "warp ox", 0, -128, 128, 1, None)
    self.warp_offset_y = value_new(vbox, "warp oy", 0, -128, 128, 1, None)
    self.warp_scale_x = value_new(vbox, "warp sx", 0, 0, 256, 1, None)
    self.warp_scale_y = value_new(vbox, "warp sy", 0, 0, 256, 1, None)

    self.blur = value_new(vbox, "blur", 0, 0, 1, 1, blurs)
    self.blur_size = value_new(vbox, "blur size", 1, 1, 8, 1, None)
    
    self.z_scale = value_new(vbox, "z scale", 0, -16, 32, 1, None)
    self.z_offset = value_new(vbox, "z offset", 0, -32, 32, 1, None)
    self.z_ease = value_new(vbox, "z ease", 0, 0, 16, 1, None)

    self.plateau = value_new(vbox, "plateau", 0, 0, 31, 1, None)

    self.pos0 = value_new(vbox, "water start", 0, 0, 31, 1, None)
    self.color1 = value_color_new(vbox, "water", "blue")
    self.pos1 = value_new(vbox, "water end", 3, 0, 31, 1, None)
    self.color2 = value_color_new(vbox, "shore", "dodgerblue")
    self.pos2 = value_new(vbox, "grass start", 6, 0, 31, 1, None)
    self.color3 = value_color_new(vbox, "grass", "greenyellow")
    self.pos3 = value_new(vbox, "grass end", 15, 0, 31, 1, None)
    self.color4 = value_color_new(vbox, "hills", "greenyellow")
    self.pos4 = value_new(vbox, "mountain start", 18, 0, 31, 1, None)
    self.color5 = value_color_new(vbox, "mountain", "sandybrown")
    self.pos5 = value_new(vbox, "mountain end", 28, 0, 31, 1, None)
    self.color6 = value_color_new(vbox, "snow", "white")
    self.pos6 = value_new(vbox, "snow start", 30, 0, 31, 1, None)

    self.seed = value_button_new(vbox, "seed", click_seed)
    land_widget_button_new(outer, "Generate (RET)", click_generate, 0, 0, 10, 10)
    land_widget_button_new(outer, "Color (C)", click_color, 0, 0, 10, 10)
    land_widget_button_new(outer, "Triangles (T)", click_triangles, 0, 0, 10, 10)
    land_widget_button_new(outer, "Debug", click_debug, 0, 0, 10, 10)
    land_widget_button_new(outer, "Reset", click_reset, 0, 0, 10, 10)
    _dialog_button_new(outer, "Load Preset", click_load, self)
    _dialog_button_new(outer, "Save Preset", click_save, self)
    land_widget_button_new(outer, "Export Mesh", click_export, 0, 0, 10, 10)
    
    return self

def _dialog_button_new(LandWidget *parent, str name,
        void (*callback)(LandWidget *), void *dialog):
    LandWidget *button = land_widget_button_new(parent, name, callback, 0, 0, 10, 10)
    land_widget_set_property(button, "dialog", dialog, None)

def click_generate(LandWidget *self):
    main_heightmap()
    
def click_seed(LandWidget *self):
    main_seed()
    
def click_color(LandWidget *self):
    main_color()
    
def click_triangles(LandWidget *self):
    main_triangles(False)
    
def click_debug(LandWidget *self):
    main_triangles(True)

def click_reset(LandWidget *self):
    for Value *value in values:
        value_set(value, value.initial)

def click_load(LandWidget *self):
    Dialog *dialog = land_widget_get_property(self, "dialog")
    dialog_load(dialog)

def click_save(LandWidget *self):
    Dialog *dialog = land_widget_get_property(self, "dialog")
    dialog_save(dialog)

def _split_cb(float x, y, z) -> int:
    int f = floor(x / 128)
    return f

def click_export(LandWidget *self):
    main_export(_split_cb, False)
