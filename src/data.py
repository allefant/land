import global stdio
import array, log, mem

class LandDataEntry:
    char *name
    int offset
    int size

class LandDataFile:
    LandArray *entries
    FILE *file

static import global string

LandDataFile *_land_datafile

static int def read32(FILE *f):
    unsigned int u = fgetc(f)
    u += fgetc(f) << 8
    u += fgetc(f) << 16
    u += fgetc(f) << 24
    return u

# Open a datafile for reading. 
LandDataFile *def land_read_datafile(FILE *file):
    LandDataFile *self
    land_alloc(self)
    self->file = file
    int count = read32(self->file)
    int i
    char name[1024]
    land_log_message("Data listing:\n")
    for i = 0 while i < count with i++:
        int s = 0
        while s < 1024:
            int c = fgetc(self->file)
            name[s++] = c
            if c == '\0': break

        LandDataEntry *entry
        land_alloc(entry)
        entry->name = land_strdup(name)
        entry->offset = read32(self->file)
        entry->size = read32(self->file)
        land_array_add_data(&self->entries, entry)
        land_log_message(" %8d %8d %s\n", entry->offset, entry->size, entry->name)

    return self

LandDataFile *def land_open_datafile(char const *filename):
    FILE *file = fopen(filename, "rb")
    if !file: return NULL
    return land_read_datafile(file)

LandDataFile *def land_open_appended_datafile(char const *filename,
    char const *marker):
    FILE *file = fopen(filename, "rb")
    if !file: return NULL
    fseek(file, -4, SEEK_END)
    int size = read32(file)
    land_log_message("Embedded data size: %d\n", size)
    fseek(file, -size - strlen(marker), SEEK_END)
    int i
    for i = 0 while i < (int)strlen(marker) with i++:
        if fgetc(file) != marker[i]:
            fclose(file)
            return NULL


    int offset = ftell(file)

    LandDataFile *data = land_read_datafile(file)

    for i = 0 while i < data->entries->count with i++:
        LandDataEntry *entry = land_array_get_nth(data->entries, i)
        entry->offset += offset

    return data

void *def land_datafile_read_entry(LandDataFile *self, char const *filename,
    int *size):
    int i
    for i = 0 while i < self->entries->count with i++:
        LandDataEntry *entry = land_array_get_nth(self->entries, i)
        if not strcmp(entry->name, filename):
            fseek(self->file, entry->offset, 0)
            unsigned char *buffer = land_calloc(entry->size)
            fread(buffer, entry->size, 1, self->file)
            if size: *size = entry->size
            return buffer


    return NULL

static int def star_match(char const *pattern, char const *name):
    int i = 0
    int j = 0
    while 1:
        char c = pattern[i]
        char d = name[j]
        if c == '*':
            int k
            # A * at the end matches anything. 
            if pattern[i + 1] == '\0': return 1
            # Try to match any possible chain. 
            for k = j while k < (int)strlen(name) with k++:
                int r = star_match(pattern + i + 1, name + k)
                if r: return r

            return 0

        elif c == '?':
            # Match anything. 
            pass
        elif c != d:
            return 0

        if c == '\0': return 1
        i++
        j++


int def land_datafile_for_each_entry(LandDataFile *self, char const *pattern,
    int (*callback)(const char *filename, int attrib, void *param), void *param):
    int i
    int n = 0
    for i = 0 while i < self->entries->count with i++:
        LandDataEntry *entry = land_array_get_nth(self->entries, i)
        if star_match(pattern, entry->name):
            if callback(entry->name, 0, param):
                break
            n++

    return n

def land_set_datafile(LandDataFile *datafile):
    _land_datafile = datafile

LandDataFile *def land_get_datafile():
    return _land_datafile
