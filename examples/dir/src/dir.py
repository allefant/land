import global land/land

static def filter(char const *name, bool is_dir, void *data) -> int:
    return 1    

def main() -> int:
    land_init()

    LandArray *files = land_filelist(".", filter, 0, None)
    
    for int i = 0 while i < land_array_count(files) with i++:
        char const *filename = land_array_get_nth(files, i)
        printf("%s\n", filename)

    return 0
