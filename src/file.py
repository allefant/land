import global stdio, stdint, stdbool
import land/mem
import allegro5/a5_file

enum:
    LAND_FULL_PATH = 1
    LAND_RELATIVE_PATH = 2

class LandFile:
    char *path
    void *f

static char *prefix

def land_file_new(char const *path, char const *mode) -> LandFile *:
    char *path2
    if mode[0] == 'r':
        path2 = land_path_with_prefix(path)
    else:
        path2 = land_strdup(path)
    void *f = platform_fopen(path2, mode)
    if not f:
        land_free(path2)
        return None
    LandFile *self
    land_alloc(self)
    self.path = path2
    self.f = f
    return self

def land_file_destroy(LandFile *self):
    platform_fclose(self.f)
    land_free(self.path)
    land_free(self)

def land_file_read(LandFile *self, char *buffer, int bytes) -> int:
    return platform_fread(self.f, buffer, bytes)

def land_file_write(LandFile *self, char const *buffer, int bytes) -> int:
    return platform_fwrite(self.f, buffer, bytes)

def land_file_fputs(LandFile *self, char const *string) -> int:
    int n = strlen(string)
    return land_file_write(self, string, n)

def land_file_getc(LandFile *self) -> int:
    return platform_fgetc(self.f)

def land_file_ungetc(LandFile *self, int c):
    platform_ungetc(self.f, c)

def land_file_eof(LandFile *self) -> bool:
    return platform_feof(self.f) != 0

def land_file_skip(LandFile *self, int n):
    platform_fseek(self.f, n)

def land_file_get32le(LandFile *self) -> uint32_t:
    uint32_t a = platform_fgetc(self.f)
    uint32_t b = platform_fgetc(self.f)
    uint32_t c = platform_fgetc(self.f)
    uint32_t d = platform_fgetc(self.f)
    return a | (b << 8) | (c << 16) | (d << 24)

def land_file_get16le(LandFile *self) -> uint16_t:
    uint16_t a = platform_fgetc(self.f)
    uint16_t b = platform_fgetc(self.f)
    return a | (b << 8)

def land_file_get32be(LandFile *self) -> uint32_t:
    uint32_t a = platform_fgetc(self.f)
    uint32_t b = platform_fgetc(self.f)
    uint32_t c = platform_fgetc(self.f)
    uint32_t d = platform_fgetc(self.f)
    return d | (c << 8) | (b << 16) | (a << 24)

def land_file_get16be(LandFile *self) -> uint16_t:
    uint16_t a = platform_fgetc(self.f)
    uint16_t b = platform_fgetc(self.f)
    return b | (a << 8)

def land_file_is_dir(char const *name) -> bool:
    return platform_is_dir(name)

def land_file_exists(char const *name) -> bool:
    return platform_file_exists(name)

def land_get_save_file(char const *appname, char const *name) -> char *:
    """
    The returned string is owned by the caller and needs to be freed with
    land_free.
    """
    return platform_get_save_file(appname, name)

def land_get_current_directory() -> char *:
    return platform_get_current_directory()

def land_path_with_prefix(char const *name) -> char *:
    int n = strlen(name)
    if prefix:
        n += strlen(prefix)
    n++
    char *r = land_malloc(n)
    if prefix:
        strcpy(r, prefix)
        strcat(r, name)
    else:
        strcpy(r, name)
    return r

def land_set_prefix(char const *path):
    if not path:
        land_free(prefix)
        land_log_message("Prefix unset.\n")
    else:
        prefix = land_realloc(prefix, strlen(path) + 1)
        strcpy(prefix, path)
        land_log_message("Prefix set to %s.\n", prefix)

def land_find_data_prefix(char const *path):
    char s[3 * 10 + 1] = ""
    for int i in range(10):
        land_set_prefix(s)
        char *p = land_path_with_prefix(path)
        if land_file_is_dir(p):
            land_set_prefix(p)
            land_free(p)
            return
        strcat(s, "../")
    land_set_prefix(path)
