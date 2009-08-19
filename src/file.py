import global stdio, stdint, stdbool
import land/mem

class LandFile:
    char *path
    FILE *f

LandFile *def land_file_new(char const *path, char const *mode):
    LandFile *self
    land_alloc(self)
    self->path = land_strdup(path)
    self->f = fopen(path, mode)
    return self

def land_file_destroy(LandFile *self):
    fclose(self->f)
    land_free(self->path)
    land_free(self)

int def land_file_read(LandFile *self, char *buffer, int bytes):
    return fread(buffer, bytes, 1, self->f)

int def land_file_getc(LandFile *self):
    return fgetc(self->f)

bool def land_file_eof(LandFile *self):
    return feof(self->f) != 0

def land_file_skip(LandFile *self, int n):
    fseek(self->f, n, SEEK_CUR)

uint32_t def land_file_get32le(LandFile *self):
    uint32_t a = fgetc(self->f)
    uint32_t b = fgetc(self->f)
    uint32_t c = fgetc(self->f)
    uint32_t d = fgetc(self->f)
    return a | (b << 8) | (c << 16) | (d << 24)

uint16_t def land_file_get16le(LandFile *self):
    uint16_t a = fgetc(self->f)
    uint16_t b = fgetc(self->f)
    return a | (b << 8)

uint32_t def land_file_get32be(LandFile *self):
    uint32_t a = fgetc(self->f)
    uint32_t b = fgetc(self->f)
    uint32_t c = fgetc(self->f)
    uint32_t d = fgetc(self->f)
    return d | (c << 8) | (b << 16) | (a << 24)

uint16_t def land_file_get16be(LandFile *self):
    uint16_t a = fgetc(self->f)
    uint16_t b = fgetc(self->f)
    return b | (a << 8)
