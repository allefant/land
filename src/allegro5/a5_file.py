static import global allegro5/allegro5
import land/array, land/mem, land/log, land/file
import global stdbool

def platform_fopen(char const *filename, char const *mode) -> void *:
    ALLEGRO_FILE *f = al_fopen(filename, mode)
    return f

def platform_fclose(void *f):
    al_fclose(f)

def platform_fread(void *f, char *buffer, int bytes) -> int:
    return al_fread(f, buffer, bytes)

def platform_fwrite(void *f, char const *buffer, int bytes) -> int:
    return al_fwrite(f, buffer, bytes)

def platform_ungetc(void *f, int c):
    al_fungetc(f, c)

def platform_fgetc(void *f) -> int:
    return al_fgetc(f)

def platform_feof(void *f) -> bool:
    return al_feof(f)

def platform_fseek(void *f, int n):
    al_fseek(f, n, ALLEGRO_SEEK_CUR)

static def add_files(char const *rel, LandArray **array, ALLEGRO_FS_ENTRY *entry,
        int (*filter)(char const *, bool is_dir, void *data), int flags,
        void *data):

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

        if not name[0]:
            name = al_get_path_component(path, -1)
        if strcmp(name, ".") and strcmp(name, ".."):
            bool is_dir = al_get_fs_entry_mode(next) & ALLEGRO_FILEMODE_ISDIR

            char rel2[strlen(rel) + strlen("/") + strlen(name) + 1]
            strcpy(rel2, rel)
            strcat(rel2, "/")
            strcat(rel2, name)

            char const *fpath
            if flags & LAND_FULL_PATH:
                fpath = al_path_cstr(path, '/')
            elif flags & LAND_RELATIVE_PATH:
                fpath = rel2
            else:
                fpath = name
            int f = 3
            if filter:
                f = filter(fpath, is_dir, data)
            if f & 1:
                if not *array: *array = land_array_new()
                land_array_add(*array, land_strdup(fpath))
            if (f & 2) and is_dir:
                add_files(rel2, array, next, filter, flags, data)
        al_destroy_fs_entry(next)
        al_destroy_path(path)
    al_close_directory(entry)

def platform_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data),
    int flags, void *data) -> LandArray *:
    land_log_message("platform_filelist %s\n", dir)
    ALLEGRO_FS_ENTRY *entry = al_create_fs_entry(dir)
    LandArray *array = None
    add_files(dir, &array, entry, filter, flags, data)
    al_destroy_fs_entry(entry)
    return array

def platform_is_dir(char const *path) -> bool:
    ALLEGRO_FS_ENTRY *fse = al_create_fs_entry(path)
    bool r = al_get_fs_entry_mode(fse) & ALLEGRO_FILEMODE_ISDIR
    al_destroy_fs_entry(fse)
    return r

def platform_file_exists(char const *path) -> bool:
    return al_filename_exists(path)

def platform_get_save_file(char const *appname, char const *name) -> char *:
    al_set_org_name("")
    al_set_app_name(appname)
    ALLEGRO_PATH *path = al_get_standard_path(ALLEGRO_USER_SETTINGS_PATH)
    const char *str = al_path_cstr(path, ALLEGRO_NATIVE_PATH_SEP)
    if not al_filename_exists(str):
        land_log_message("Creating new settings path %s.\n", str);
        al_make_directory(str)
    al_set_path_filename(path, name)
    str = al_path_cstr(path, ALLEGRO_NATIVE_PATH_SEP)
    land_log_message("Using save file %s.\n", str);
    char *dup = land_strdup(str)
    al_destroy_path(path)
    return dup

def platform_get_current_directory() -> char *:
    char *d = al_get_current_directory()
    # need do dup it as it's different memory managers
    # TODO: why do we not hook into Allegro's memory allocation functions?
    char *dup = land_strdup(d)
    al_free(d)
    return dup

def platform_get_data_path -> char *:
    ALLEGRO_PATH *path = al_get_standard_path(ALLEGRO_RESOURCES_PATH)
    char *dup = land_strdup(al_path_cstr(path, '/'))
    al_destroy_path(path)
    return dup

def platform_remove_file(char const *path) -> bool:
    return al_remove_filename(path)
