import global land/land

static int def filter(char const *name, bool is_dir, void *data):
    return 1    

int def main():
    land_init()

    LandArray *files = land_filelist(".", filter, None)
    
    for int i = 0 while i < land_array_count(files) with i++:
        char const *filename = land_array_get_nth(files, i)
        printf("%s\n", filename)

    return 0
