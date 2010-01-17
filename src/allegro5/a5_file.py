static import global allegro5/allegro5
import land/array, land/mem
import global stdbool

static def add_files(LandArray **array, ALLEGRO_FS_ENTRY *entry,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    if not al_open_directory(entry):
        return
    while true:
        ALLEGRO_FS_ENTRY *next = al_read_directory(entry)
        if not next:
            break
        ALLEGRO_PATH const *path = al_get_fs_entry_name(next)
        char const *name = al_get_path_filename(path)
        if not name[0]:
            name = al_get_path_component(path, -1)
        if strcmp(name, ".") and strcmp(name, ".."):
            bool is_dir = al_fs_entry_is_directory(next)
            char const *fpath = al_path_cstr(path, '/')
            int f = filter(fpath, is_dir, data)
            if f & 1:
                land_array_add_data(array, land_strdup(fpath))
            if (f & 2) and is_dir:
                add_files(array, next, filter, data)
        al_destroy_fs_entry(next)
    al_close_directory(entry)

LandArray *def platform_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    ALLEGRO_FS_ENTRY *entry = al_create_fs_entry(dir)
    LandArray *array = None
    add_files(&array, entry, filter, data)
    al_destroy_fs_entry(entry)
    return array

bool def platform_is_dir(char const *path):
    ALLEGRO_FS_ENTRY *fse = al_create_fs_entry(path)
    bool r = al_fs_entry_is_directory(fse)
    al_destroy_fs_entry(fse)
    return r
