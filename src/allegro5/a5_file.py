static import global allegro5/allegro5
import land/array, land/mem, land/log, land/file
import global stdbool

void *def platform_fopen(char const *filename, char const *mode):
    ALLEGRO_FILE *f = al_fopen(filename, mode)
    return f

def platform_fclose(void *f):
    al_fclose(f)

int def platform_fread(void *f, char *buffer, int bytes):
    return al_fread(f, buffer, bytes)

int def platform_fwrite(void *f, char const *buffer, int bytes):
    return al_fwrite(f, buffer, bytes)

def platform_ungetc(void *f, int c):
    al_fungetc(f, c)

int def platform_fgetc(void *f):
    return al_fgetc(f)

bool def platform_feof(void *f):
    return al_feof(f)

def platform_fseek(void *f, int n):
    al_fseek(f, n, ALLEGRO_SEEK_CUR)

static def add_files(LandArray **array, ALLEGRO_FS_ENTRY *entry,
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
            char const *fpath
            if flags & LAND_FULL_PATH:
                fpath = al_path_cstr(path, '/')
            else:
                fpath = name
            int f = filter(fpath, is_dir, data)
            if f & 1:
                if not *array: *array = land_array_new()
                land_array_add(*array, land_strdup(fpath))
            if (f & 2) and is_dir:
                add_files(array, next, filter, flags, data)
        al_destroy_fs_entry(next)
        al_destroy_path(path)
    al_close_directory(entry)

LandArray *def platform_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data),
    int flags, void *data):
    land_log_message("platform_filelist %s\n", dir)
    ALLEGRO_FS_ENTRY *entry = al_create_fs_entry(dir)
    LandArray *array = None
    add_files(&array, entry, filter, flags, data)
    al_destroy_fs_entry(entry)
    return array

bool def platform_is_dir(char const *path):
    ALLEGRO_FS_ENTRY *fse = al_create_fs_entry(path)
    bool r = al_get_fs_entry_mode(fse) & ALLEGRO_FILEMODE_ISDIR
    al_destroy_fs_entry(fse)
    return r

char *def platform_get_save_file(char const *appname, char const *name):
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
