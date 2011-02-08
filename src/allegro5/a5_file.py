static import global allegro5/allegro5
import land/array, land/mem, land/log
import global stdbool

static def add_files(LandArray **array, ALLEGRO_FS_ENTRY *entry,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    if not al_open_directory(entry):
        land_log_message("Cannot open directory (%d).\n",
            al_get_fs_entry_mode(entry) & ALLEGRO_FILEMODE_ISDIR)
        return
    while true:
        ALLEGRO_FS_ENTRY *next = al_read_directory(entry)
        if not next:
            break
        ALLEGRO_PATH *path = al_create_path(al_get_fs_entry_name(next))
        char const *name = al_get_path_filename(path)
        printf("* %s\n", name);
        if not name[0]:
            name = al_get_path_component(path, -1)
        if strcmp(name, ".") and strcmp(name, ".."):
            bool is_dir = al_get_fs_entry_mode(next) & ALLEGRO_FILEMODE_ISDIR
            char const *fpath = al_path_cstr(path, '/')
            int f = filter(fpath, is_dir, data)
            if f & 1:
                if not *array: *array = land_array_new()
                land_array_add(*array, land_strdup(fpath))
            if (f & 2) and is_dir:
                add_files(array, next, filter, data)
        al_destroy_fs_entry(next)
        al_destroy_path(path)
    al_close_directory(entry)

LandArray *def platform_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    land_log_message("platform_filelist %s\n", dir)
    ALLEGRO_FS_ENTRY *entry = al_create_fs_entry(dir)
    LandArray *array = None
    add_files(&array, entry, filter, data)
    al_destroy_fs_entry(entry)
    return array

bool def platform_is_dir(char const *path):
    ALLEGRO_FS_ENTRY *fse = al_create_fs_entry(path)
    bool r = al_get_fs_entry_mode(fse) & ALLEGRO_FILEMODE_ISDIR
    al_destroy_fs_entry(fse)
    return r
