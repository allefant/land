static import global stdlib, string
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
        self->buffer = realloc(self->buffer, self->size)
    memcpy(self->buffer + self->n - n, buffer, n)

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
