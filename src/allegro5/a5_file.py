static import global allegro5/allegro5
import land/array, land/mem
import global stdbool

static def add_files(LandArray **array, ALLEGRO_FS_ENTRY *entry,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    al_opendir(entry)
    while true:
        ALLEGRO_FS_ENTRY *next = al_readdir(entry)
        if not next:
            break
        ALLEGRO_PATH const *path = al_get_fs_entry_name(next)
        if strcmp(al_get_path_tail(path), ".") and strcmp(
            al_get_path_tail(path), ".."):
            char const *name = al_path_cstr(path, '/')
            bool is_dir = al_fs_entry_is_dir(next);
            int f = filter(name, is_dir, data)
            if f & 1:
                land_array_add_data(array, land_strdup(name))
            if (f & 2) and is_dir:
                add_files(array, next, filter, data)
        al_destroy_fs_entry(next)
    al_closedir(entry)

LandArray *def platform_filelist(char const *dir,
    int (*filter)(char const *, bool is_dir, void *data), void *data):
    """
    Returns an array of files in the given directory. Before a file is added,
    the filter function is called, with the name about to be added and an
    indication whether it is a filename or a directory.

    The return value of the filter decides what is done with the name:
    0 - Discard it.
    1 - Append if to the returned list.
    2 - If it is a directory, recurse into it.
    3 - Like 1 and 2 combined.
    """
    ALLEGRO_FS_ENTRY *entry = al_create_fs_entry(dir)
    LandArray *array = None
    add_files(&array, entry, filter, data)
    al_destroy_fs_entry(entry)
    return array
