import global land.land
import main

char const* noises[] = {"Voronoi", "Perlin", "Plasma", "White"}
char const* lerps[] = {"None", "Linear", "Cosine", "Smooth", "Smoother", "Smoothest"}
char const* warps[] = {"none", "warp"}
char const* blurs[] = {"none", "blur"}

class Dialog:
    Value *size
    Value *noise
    Value *lerp
    Value *count
    Value *levels
    Value *amplitude
    Value *power_modifier
    Value *randomness
    Value *crispness

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

    LandWidget *view

class Value:
    LandWidget *label
    LandWidget *spin
    LandWidget *slider
    LandWidget *name
    void *data
    char const**names
    int v

def dialog_hide_show(Dialog *self):
    value_show_if(self.warp, 1, self.warp_offset_x)
    value_show_if(self.warp, 1, self.warp_offset_y)
    value_show_if(self.warp, 1, self.warp_scale_x)
    value_show_if(self.warp, 1, self.warp_scale_y)

    value_show_if(self.blur, 1, self.blur_size)

    value_show_if(self.noise, 0, self.count)
    value_show_if(self.noise, 0, self.randomness)
    
    value_show_if(self.noise, 1, self.lerp)
    value_show_if(self.noise, 1, self.levels)

def value_show_if(Value *self, int v, Value *show):
    bool hidden = self.v != v
    if hidden:
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

def value_set(Value *value, int v):
    value.v = v
    land_widget_spin_set_value(value.spin, value.v)
    if value.slider: land_widget_slider_set_value(value.slider, value.v)
    if value.name:
        land_widget_button_replace_text(value.name, value.names[value.v])
    
Value *def value_new(LandWidget *parent, char const *name, float val,
    minval, maxval, step, str* names):
    Value *self
    land_alloc(self)
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)

    self.v = val

    if names:
        self.names = names
        self.name = land_widget_text_new(parent, names[(int)val], 0, 0, 0, 1, 1)
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
    
    return self

def dialog_new -> Dialog*:
    Dialog *self
    land_alloc(self)
    self.view = land_widget_panel_new(None, 1024, 0, 200, 100)
    land_widget_reference(self.view)
    
    LandWidget *outer = land_widget_vbox_new(self.view, 0, 0, 100, 100)
    
    LandWidget *vbox = land_widget_vbox_new(outer, 0, 0, 100, 100)
    land_widget_vbox_set_columns(vbox, 3)
    land_widget_layout_set_shrinking(vbox, 0, 1)

    self.size = value_new(vbox, "size", 8, 0, 16, 1, None)
    self.noise = value_new(vbox, "noise", 1, 0, 3, 1, noises)
    self.lerp = value_new(vbox, "lerp", 2, 0, 5, 1, lerps)
    self.count = value_new(vbox, "count", 1, 0, 32, 1, None)
    self.randomness = value_new(vbox, "randomness", 1, 0, 16, 1, None)
    self.levels = value_new(vbox, "levels", 6, 0, 10, 1, None)
    self.amplitude = value_new(vbox, "amplitude", 0, -16, 16, 1, None)
    self.power_modifier = value_new(vbox, "power_modifier", 0, -16, 16, 1, None)

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

    land_widget_button_new(outer, "Seed", click_seed, 0, 0, 10, 10)
    land_widget_button_new(outer, "Generate", click_generate, 0, 0, 10, 10)
    land_widget_button_new(outer, "Color", click_color, 0, 0, 10, 10)
    land_widget_button_new(outer, "Triangles", click_triangles, 0, 0, 10, 10)
    land_widget_button_new(outer, "Debug", click_debug, 0, 0, 10, 10)
    
    return self

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
