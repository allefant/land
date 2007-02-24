static import global stdio, stdlib, string, zlib
static import memory, global allegro

class LandBuffer:
    int size
    int n
    char *buffer

LandBuffer *def land_buffer_new():
    LandBuffer *self
    land_alloc(self)
    return self

def land_buffer_del(LandBuffer *self):
    if self->buffer: land_free(self->buffer)
    land_free(self)

def land_buffer_add(LandBuffer *self, char const *buffer, int n):
    self->n += n
    if self->n > self->size:
        if not self->size: self->size = 1
        while self->size < self->n:
            self->size *= 2
        self->buffer = land_realloc(self->buffer, self->size)
    memcpy(self->buffer + self->n - n, buffer, n)

def land_buffer_add_char(LandBuffer *self, char c):
    land_buffer_add(self, &c, 1)

def land_buffer_cat(LandBuffer *self, char const *string):
    land_buffer_add(self, string, strlen(string))

def land_buffer_clear(LandBuffer *self):
    """
    Clears the buffer (but keeps any memory allocation for speedy refilling).
    """
    self->n = 0

def land_buffer_crop(LandBuffer *self):
    """
    Make the buffer use up only the minimum required amount.
    """
    self->buffer = realloc(self->buffer, self->n)
    self->size = self->n

char *def land_buffer_finish(LandBuffer *self):
    """
    Destroys the buffer, but returns a C-string constructed from it by appending
    a 0 character. You may not access the pointer you pass to this function
    anymore after it returns. Also, you have to make sure it does not already
    contain any 0 characters.
    """
    char c[] = "";
    land_buffer_add(self, c, 1)
    char *s = self->buffer
    self->buffer = None
    land_buffer_del(self)
    return s

def land_buffer_write_to_file(LandBuffer *self, char const *filename):
    PACKFILE *pf = pack_fopen(filename, "w")
    pack_fwrite(self->buffer, self->n, pf)
    pack_fclose(pf)

LandBuffer *def land_buffer_read_from_file(char const *filename):
    PACKFILE *pf = pack_fopen(filename, "r")
    LandBuffer *self = land_buffer_new()
    while 1:
        int c = pack_getc(pf)
        if c < 0: break
        land_buffer_add(self, (char *)&c, 1)
    pack_fclose(pf)
    return self

def land_buffer_compress(LandBuffer *self):
    uLongf destlen = self->n * 1.1 + 12
    Bytef *dest = land_malloc(4 + destlen)
    *((uint32_t *)dest) = self->n
    compress(dest + 4, &destlen, (void *)self->buffer, self->n)
    dest = land_realloc(dest, 4 + destlen)
    land_free(self->buffer)
    self->buffer = (void *)dest
    self->size = self->n = 4 + destlen

def land_buffer_decompress(LandBuffer *self):
    uLongf destlen = *((uint32_t *)self->buffer)
    Bytef *dest = land_malloc(destlen)
    uncompress(dest, &destlen, (void *)(4 + self->buffer), self->n)
    land_free(self->buffer)
    self->buffer = (void *)dest
    self->size = self->n = destlen

int def land_buffer_compare(LandBuffer *self, *other):
    if self->n < other->n: return -1
    if self->n > other->n: return 1
    return memcmp(self->buffer, other->buffer, self->n)
