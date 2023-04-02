import global land.land
import noise_dialog

class Presets:
    LandArray *presets

def presets_new -> Presets*:
    Presets *self; land_alloc(self)
    return self

def _ini_filter(str name, bool is_dir, void *data) -> int:
    if land_fnmatch("preset_*.ini", name): return 1
    return 0

def presets_update(Presets *self, Dialog *dialog):
    char *path = land_get_save_file("perlin", "")
    LandArray* preset_files = land_filelist(path, _ini_filter, 0, None)
    if self.presets:
        land_array_destroy_with_strings(self.presets)
    self.presets = land_array_new()
    land_free(path)
    
    if preset_files == None:
        preset_files = land_array_new()

    for char *ini in preset_files:
        char *name = land_strdup(ini)
        land_shorten(&name, 7, -4)
        char *path2 = land_get_save_file("perlin", ini)
        print("reading %s", path2)
        LandIniFile* ini = land_ini_read(path2)
        if ini.loaded:
            int v = land_ini_get_int(ini, "values", "preset", 0)
            land_array_replace_or_resize(self.presets, v, name)
        land_free(path2)

    land_array_add(self.presets, land_strdup("unnamed"))

    land_array_destroy_with_strings(preset_files)

    str name = land_array_get(self.presets, 0)
    preset_fill_in(self, dialog, name)

def preset_fill_in(Presets *self, Dialog *dialog, str name):
    if dialog.preset:
        value_update_choices(dialog.preset, self.presets, name)
    
def get_preset_id(Presets *self, str name) -> int:
    int i = 0
    for char *name2 in LandArray *self.presets:
        if land_equals(name2, name):
            break
        i++
    return i
