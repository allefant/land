import global stdio, stdint, stdbool
import land/mem
import allegro5/a5_file
import land.buffer

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
        land_log_message("Opening file %s (%s) failed.\n", path2, mode)
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

def land_file_add_to_buffer(LandFile* self, LandBuffer* buf):
    while 1:
        char kb[16384]
        size_t n = land_file_read(self, kb, 16384)
        land_buffer_add(buf, kb, n)
        if n < 16384:
            break

def land_file_lines(LandFile *self) -> LandArray*:
    """
    Return the file contents as an array of strings. Once done with the
    strings you can destroy them (and the array) with:

    land_array_destroy_with_strings
    """
    LandBuffer* buf = land_buffer_new()
    land_file_add_to_buffer(self, buf)
    char* text = land_buffer_finish(buf)
    LandArray* lines = land_split(text, "\n")
    land_free(text)
    return lines

def land_file_print(LandFile *self, char const *f, ...):
    char s[1024]
    va_list args
    va_start(args, f)
    vsnprintf(s, sizeof s, f, args)
    strcat(s, "\n")
    va_end(args)
    land_file_write(self, s, strlen(s))

def land_file_printnn(LandFile *self, char const *f, ...):
    char s[1024]
    va_list args
    va_start(args, f)
    vsnprintf(s, sizeof s, f, args)
    va_end(args)
    land_file_write(self, s, strlen(s))

def land_file_fputs(LandFile *self, char const *string) -> int:
    int n = strlen(string)
    return land_file_write(self, string, n)

def land_file_getc(LandFile *self) -> int:
    return platform_fgetc(self.f)

def land_file_putc(LandFile *self, int x):
    return platform_fputc(self.f, x)

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

def land_file_put32le(LandFile *self, uint32_t x):
    uint32_t a = x & 255
    uint32_t b = (x >> 8) & 255
    uint32_t c = (x >> 16) & 255
    uint32_t d = x >> 24
    platform_fputc(self.f, a)
    platform_fputc(self.f, b)
    platform_fputc(self.f, c)
    platform_fputc(self.f, d)

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

def land_get_data_path() -> char *:
    return platform_get_data_path()

def land_path_with_prefix(char const *name) -> char *:
    """
    Returns a new string with has the global data prefix prefixed to
    the given path.
    """
    if name and name[0] == '/': return land_strdup(name)
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
        prefix = None
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

            # If the data folder has a single file named "link" in it
            # then we append the path in that file. So for example
            # "data" is passed to this function and ../data/link has
            # "../blah" in it then the path will be ../data/../blah.
            char* link = land_read_text("link")
            if link:
                land_strip(&link)
                p = land_path_with_prefix(link)
                land_set_prefix(p)
                land_free(p)
                land_free(link)
            return
        strcat(s, "../")
    land_set_prefix(path)

def land_replace_filename(char const *path, char const *name) -> char *:
    char *slash = strrchr(path, '/')
    int n = 0
    if slash:
        n = slash - path
    char *result = land_malloc(n + strlen("/") + strlen(name) + 1)
    strncpy(result, path, n)
    result[n] = 0
    if n > 0: strcat(result, "/")
    strcat(result, name)
    return result

def land_file_remove(char const *path) -> bool:
    return platform_remove_file(path)

def land_file_time(char const *path) -> int64_t:
    return platform_file_time(path)

def land_user_data_path(char const *app, *path) -> char*:
    return platform_get_app_data_file(app, path)
