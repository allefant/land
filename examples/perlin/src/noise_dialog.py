import global land.land
import main
import color_picker

str noises[] = {"Voronoi", "Perlin", "Plasma", "White", "Waves", "Pyramids",
    "Domes", "Compound"}
str transfers[] = {"linear", "inverse", "sqr", "1-sqr", "sqrt", "1-sqrt"}
str lerps[] = {"None", "Linear", "Cosine", "Smooth", "Smoother", "Smoothest"}
str warps[] = {"none", "warp"}
str blurs[] = {"none", "blur"}
str river_types[] = {"none", "big"}

class Dialog:
    int size

    LandArray *values

    Value *preset
    Value *width
    Value *height
    Value *noise
    Value *transfer
    Value *lerp
    Value *count
    Value *levels
    Value *first_level
    Value *amplitude
    Value *distance
    Value *power_modifier
    Value *randomness
    Value *crispness
    Value *wrap
    Value *river
    Value *compound
    Value *modulo

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
    LandWidget *message

    LandArray *presets
    LandArray *compound_components

    double dt

class Value:
    char *id
    LandWidget *label
    LandWidget *spin
    LandWidget *slider
    LandWidget *name
    LandWidget *color
    LandWidget *button
    LandWidget *edit
    void *data
    char const**names
    LandArray* choices
    int v
    int initial
    char *v_string
    char *initial_string
    bool is_string

Value* show_picker

def dialog_hide_show(Dialog *self):
    value_show_if(self.warp.v == 1, self.warp_offset_x)
    value_show_if(self.warp.v == 1, self.warp_offset_y)
    value_show_if(self.warp.v == 1, self.warp_scale_x)
    value_show_if(self.warp.v == 1, self.warp_scale_y)

    value_show_if(self.blur.v == 1, self.blur_size)

    value_show_if(self.noise.v == 0 or self.noise.v == 4 or\
        self.noise.v == 5 or self.noise.v == 6 or self.noise.v == 7,
        self.count)
    value_show_if(self.noise.v == 0 or self.noise.v == 7, self.randomness)
    
    value_show_if(self.noise.v == 1, self.lerp)
    value_show_if(self.noise.v == 1 or self.noise.v == 3, self.levels)
    value_show_if(self.noise.v == 1 or self.noise.v == 3, self.first_level)

    value_show_if(self.noise.v == 0 or self.noise.v == 7, self.distance)

def noise_dialog_get_compound_components(Dialog *self) -> LandArray *:
    if self.compound_components:
        land_array_destroy_with_strings(self.compound_components)
    str text = land_widget_edit_get_text(self.compound.edit)
    self.compound_components = land_split(text, ",")
    return self.compound_components

def _get_preset_name(Dialog *self) -> char*:
    char name[100]
    sprintf(name, "preset_%s.ini", land_widget_edit_get_text(self.preset.edit))
    char *path = land_get_save_file("perlin", name)
    return path

def dialog_load(Dialog *self):
    char *name = _get_preset_name(self)
    LandIniFile* ini = land_ini_read(name)
    if ini.loaded:
        for Value *value in LandArray* self.values:
            if value.is_string:
                str v = land_ini_get_string(ini, "strings", value.id, "")
                value_set_string(value, v)
            else:
                int v = land_ini_get_int(ini, "values", value.id, 0)
                value_set(value, v)
    else:
        print("could not read %s", name)
    land_ini_destroy(ini)
    land_free(name)

def dialog_save(Dialog *self):
    char *name = _get_preset_name(self)
    str id = land_widget_edit_get_text(self.preset.edit)
    if land_equals(id, "unnamed"):
        message("Cannot save unnamed preset!", land_color_rgba(1, 0, 0, 1))
        return
    LandIniFile* ini = land_ini_new(name)
    for Value *value in LandArray* self.values:
        if value.is_string:
            land_ini_set_string(ini, "strings", value.id, value.v_string)
        else:
            land_ini_set_int(ini, "values", value.id, value.v)
    land_ini_writeback(ini)
    print("saved %s", ini->filename)
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

def _value_set(Value *value, int v, str v_string):
    value.v = v
    value.v_string = None
    if v_string:
        value.v_string = land_strdup(v_string)
    if value.spin: land_widget_spin_set_value(value.spin, value.v)
    if value.slider: land_widget_slider_set_value(value.slider, value.v)
    if value.name: land_widget_button_replace_text(value.name, value.names[value.v])
    if value.color: land_widget_button_replace_text(value.color, color_picker_find_name(v))
    if value.edit:
        if value.is_string:
            land_widget_edit_set_text(value.edit, value.v_string)
        else:
            if value.v < land_array_count(value.choices):
                land_widget_edit_set_text(value.edit, land_array_get(value.choices, value.v))

def value_set(Value *value, int v): _value_set(value, v, None)
def value_set_string(Value *value, str v): _value_set(value, 0, v)

def on_menu_selection(LandWidget *self):
    Value *value = land_widget_get_property(self.parent, "value")
    int i = 0
    while value.names[i]:
        if land_equals(land_widget_button_get_text(self), value.names[i]):
            value_set(value, i)
        i++

def value_new_internal(Dialog *self, str name) -> Value*:
    Value *v
    land_alloc(v)
    v.id = land_strdup(name)
    land_array_add(self.values, v)
    return v

def value_new(Dialog *dialog, LandWidget *parent, char const *name, int val,
    minval, maxval, step, str* names) -> Value *:
    Value *self = value_new_internal(dialog, name)
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
    
    return self

def value_new_text(Dialog *dialog, LandWidget* parent, str name, LandArray *choices) -> Value *:
    Value *self = value_new_internal(dialog, name)
    self.label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    self.choices = choices
    land_widget_layout_set_shrinking(self.label, 1, 1)
    str initial = land_array_get_or_none(choices, 0)
    if initial == None: initial = ""
    self.edit = land_widget_edit_new(parent, initial, None, 0, 0, 1, 1)
    self.spin = land_widget_spin_new(parent, 0, 0, land_array_count(choices) - 1, 1,
        update_from_spin, 0, 0, 1, 1)
    land_widget_spin_set_minimum_text(self.spin, "99999")
    land_widget_layout_set_shrinking(self.spin, 1, 1)
    land_widget_set_property(self.spin, "value", self, None)
    return self

def value_new_menu(Dialog *dialog, LandWidget *parent, *desktop, char const *name, int val,
        minval, maxval, step, str* names) -> Value *:
    Value *self = value_new_internal(dialog, name)
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)

    self.v = val
    self.initial = val

    self.names = names
    self.name = land_widget_text_new(parent, names[(int)val], 0, 0, 0, 1, 1)
    land_widget_button_set_minimum_text(self.name, "Voronoi")

    self->button = land_widget_menubar_new(parent, 0, 0, 1, 1)
    land_widget_layout_set_shrinking(self->button, 1, 1)

    LandWidget *menu = land_widget_menu_new(desktop, 0, 0, 10, 10)
    land_widget_set_property(menu, "value", self, None)
    for int i in range(minval, 1 + maxval - minval):
        land_widget_menuitem_new(menu, names[i], on_menu_selection)

    LandWidget *pick = land_widget_menubutton_new(self.button, "Pick", menu, 0, 0, 1, 1)
    land_widget_menubutton_on_hover(pick, False)
    land_widget_hide(menu)

    return self

Value *def value_color_new(Dialog *dialog, LandWidget *parent, str name, str val):
    LandColor c = land_color_name(val)
    Value *self = value_new_internal(dialog, name)
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)
    self.v = land_color_to_int(c)
    self.initial = self.v
    self.color = land_widget_text_new(parent, val, 0, 0, 0, 1, 1)
    self.button = land_widget_button_new(parent, "pick", update_pick, 0, 0, 0, 0)
    land_widget_set_property(self.button, "value", self, None)
    return self

Value *def value_button_new(Dialog *dialog, LandWidget *parent, str name, void (*click)(LandWidget *)):
    Value *self = value_new_internal(dialog, name)
    self->label = land_widget_text_new(parent, name, 0, 0, 0, 0, 0)
    land_widget_layout_set_shrinking(self->label, 1, 1)
    land_widget_text_new(parent, "", 0, 0, 0, 1, 1)
    self.button = land_widget_button_new(parent, name, click, 0, 0, 0, 0)
    return self

def _ini_filter(str name, bool is_dir, void *data) -> int:
    if land_fnmatch("preset_*.ini", name): return 1
    return 0

def assign_presets(Dialog *dialog):
    char *path = land_get_save_file("perlin", "")
    LandArray* preset_files = land_filelist(path, _ini_filter, 0, None)
    dialog.presets = land_array_new()
    land_free(path)
    
    if preset_files == None:
        preset_files = land_array_new()

    for char *ini in preset_files:
        char *name = land_strdup(ini)
        land_shorten(&name, 7, 4)
        char *path2 = land_get_save_file("perlin", ini)
        LandIniFile* ini = land_ini_read(path2)
        if ini.loaded:
            int v = land_ini_get_int(ini, "values", "preset", 0)
            land_array_replace_or_resize(dialog.presets, v, name)
        land_free(path2)

    land_array_add(dialog.presets, "unnamed")

    land_array_destroy_with_strings(preset_files)

def get_preset_id(Dialog *dialog, str name) -> int:
    int i = 0
    for char *name2 in LandArray *dialog.presets:
        if land_equals(name2, name):
            break
        i++
    return i

def dialog_new(int width, height) -> Dialog*:
    Dialog *self
    land_alloc(self)
    self.size = width
    int w = land_display_width()
    self.view = land_widget_board_new(self.view, w - width, 0, width, height)
    land_widget_reference(self.view)

    LandWidget* panel = land_widget_panel_new(self.view, w - width, 0, width, 10)
    int th = land_line_height()
    self.message = land_widget_text_new(self.view, "ready", 0, w - width, height - th, width, th)

    if self.values: land_array_destroy(self.values)
    self.values = land_array_new()
    
    LandWidget *outer = land_widget_vbox_new(panel, 0, 0, 100, 100)
    LandWidget *vbox = land_widget_vbox_new(outer, 0, 0, 100, 100)
    land_widget_vbox_set_columns(vbox, 3)
    land_widget_layout_set_shrinking(vbox, 0, 1)

    assign_presets(self)
    self.preset = value_new_text(self, vbox, "preset", self.presets)
    self.noise = value_new_menu(self, vbox, self.view, "noise", 7, 0, 7, 1, noises)
    self.width = value_new(self, vbox, "width", 8, 0, 16, 1, None)
    self.height = value_new(self, vbox, "height", 8, 0, 16, 1, None)
    self.wrap = value_new(self, vbox, "wrap", 1, 0, 1, 1, None)
    self.transfer = value_new(self, vbox, "transfer", 0, 0, 5, 1, transfers)
    self.lerp = value_new(self, vbox, "lerp", 5, 0, 5, 1, lerps)
    self.count = value_new(self, vbox, "count", 8, 0, 32, 1, None)
    self.randomness = value_new(self, vbox, "randomness", 0, 0, 16, 1, None)
    self.levels = value_new(self, vbox, "levels", 0, 0, 10, 1, None)
    self.first_level = value_new(self, vbox, "first", 0, 0, 10, 1, None)
    self.amplitude = value_new(self, vbox, "amplitude", 0, -16, 16, 1, None)
    self.power_modifier = value_new(self, vbox, "power modifier", 0, -16, 16, 1, None)
    self.distance = value_new(self, vbox, "distance", 2, 0, 64, 1, None)
    self.modulo = value_new_internal(self, "modulo")

    LandWidget* book = land_widget_book_new(outer, 0, 0, 1, 1)
    LandWidget *vbox_warp = land_widget_vbox_new(book, 0, 0, 100, 10)
    land_widget_book_pagename(book, "warp")
    land_widget_vbox_set_columns(vbox_warp, 3)
    self.warp = value_new(self, vbox_warp, "warp", 0, 0, 1, 1, warps)
    self.warp_offset_x = value_new(self, vbox_warp, "warp ox", 0, -128, 128, 1, None)
    self.warp_offset_y = value_new(self, vbox_warp, "warp oy", 0, -128, 128, 1, None)
    self.warp_scale_x = value_new(self, vbox_warp, "warp sx", 0, 0, 256, 1, None)
    self.warp_scale_y = value_new(self, vbox_warp, "warp sy", 0, 0, 256, 1, None)

    LandWidget *vbox_blur = land_widget_vbox_new(book, 0, 0, 100, 10)
    land_widget_book_pagename(book, "blur")
    land_widget_vbox_set_columns(vbox_blur, 3)
    self.blur = value_new(self, vbox_blur, "blur", 0, 0, 1, 1, blurs)
    self.blur_size = value_new(self, vbox_blur, "blur size", 1, 1, 8, 1, None)

    LandWidget *vbox_z = land_widget_vbox_new(book, 0, 0, 100, 10)
    land_widget_book_pagename(book, "z")
    land_widget_vbox_set_columns(vbox_z, 3)
    self.z_scale = value_new(self, vbox_z, "z scale", 0, -16, 32, 1, None)
    self.z_offset = value_new(self, vbox_z, "z offset", 0, -32, 32, 1, None)
    self.z_ease = value_new(self, vbox_z, "z ease", 0, 0, 16, 1, None)
    self.plateau = value_new(self, vbox_z, "plateau", 0, 0, 31, 1, None)

    land_widget_vbox_new(book, 0, 0, 0, 0)
    LandWidget* pname = land_widget_book_pagename(book, "^")
    land_widget_layout_set_shrinking(pname, True, True)

    self.river = value_new(self, vbox, "river", 0, 0, 1, 1, river_types)

    book = land_widget_book_new(outer, 0, 0, 1, 1)

    LandWidget *vbox_colors = land_widget_vbox_new(book, 0, 0, 100, 100)
    land_widget_book_pagename(book, "colors")
    land_widget_vbox_set_columns(vbox_colors, 3)
    land_widget_layout_set_shrinking(vbox_colors, 0, 1)
    self.color1 = value_color_new(self, vbox_colors, "water", "blue")
    self.color2 = value_color_new(self, vbox_colors, "shore", "dodgerblue")
    self.color3 = value_color_new(self, vbox_colors, "grass", "greenyellow")
    self.color4 = value_color_new(self, vbox_colors, "hills", "greenyellow")
    self.color5 = value_color_new(self, vbox_colors, "mountain", "sandybrown")
    self.color6 = value_color_new(self, vbox_colors, "snow", "white")

    LandWidget *vbox_heights = land_widget_vbox_new(book, 0, 0, 100, 100)
    land_widget_book_pagename(book, "heights")
    land_widget_vbox_set_columns(vbox_heights, 3)
    land_widget_layout_set_shrinking(vbox_heights, 0, 1)
    self.pos0 = value_new(self, vbox_heights, "water start", 0, 0, 31, 1, None)
    self.pos1 = value_new(self, vbox_heights, "water end", 3, 0, 31, 1, None)
    self.pos2 = value_new(self, vbox_heights, "grass start", 6, 0, 31, 1, None)
    self.pos3 = value_new(self, vbox_heights, "grass end", 15, 0, 31, 1, None)
    self.pos4 = value_new(self, vbox_heights, "mountain start", 18, 0, 31, 1, None)
    self.pos5 = value_new(self, vbox_heights, "mountain end", 28, 0, 31, 1, None)
    self.pos6 = value_new(self, vbox_heights, "snow start", 30, 0, 31, 1, None)

    LandWidget *vbox_compound = land_widget_vbox_new(book, 0, 0, 100, 10)
    land_widget_book_pagename(book, "compound")
    land_widget_layout_set_shrinking(vbox_compound, 0, 1)
    auto value = value_new_internal(self, "compound")
    value.is_string = True
    value.initial_string = land_strdup("greenhills,mountains,desert,marsh,ocean")
    value.edit = land_widget_edit_new(vbox_compound, value.initial_string, None, 0, 0, 10, 10)
    self.compound = value

    land_widget_vbox_new(book, 0, 0, 0, 0)
    pname = land_widget_book_pagename(book, "^")
    land_widget_layout_set_shrinking(pname, True, True)

    land_widget_text_new(outer, "", 0, 0, 0, 0, 0)
    self.seed = value_new_internal(self, "seed")
    land_widget_button_new(outer, "Seed (S)", click_seed, 0, 0, 10, 10)
    land_widget_button_new(outer, "Generate (RET)", click_generate, 0, 0, 10, 10)
    land_widget_button_new(outer, "Color (C)", click_color, 0, 0, 10, 10)
    land_widget_button_new(outer, "Triangles (T)", click_triangles, 0, 0, 10, 10)
    land_widget_button_new(outer, "Debug (D)", click_debug, 0, 0, 10, 10)
    _dialog_button_new(self, outer, "Reset (R)", click_reset)
    _dialog_button_new(self, outer, "Load Preset (L)", click_load)
    _dialog_button_new(self, outer, "Save Preset", click_save)
    land_widget_button_new(outer, "Export Mesh", click_export, 0, 0, 10, 10)

    return self

def dialog_destroy(Dialog *self):
    land_widget_unreference(self.view)
    land_free(self)

def _dialog_button_new(Dialog *dialog, LandWidget *parent, str name,
        void (*callback)(LandWidget *)):
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
    main_reset()

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
