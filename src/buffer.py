static import global stdio, stdlib, string, zlib
static import mem
import global allegro5/allegro5
import array

class LandBuffer:
    int size # reserved memory
    int n # number of bytes in the buffer
    char *buffer

class LandBufferAsFile:
    LandBuffer *landbuffer
    int pos
    int ungetc

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
    Make the buffer use up only the minimum required amount of memory.
    """
    self->buffer = realloc(self->buffer, self->n)
    self->size = self->n

char *def land_buffer_finish(LandBuffer *self):
    """
    Destroys the buffer, but returns a C-string constructed from it by appending
    a 0 character. You may not access the pointer you pass to this function
    anymore after it returns. Also, you have to make sure it does not already
    contain any 0 characters. When no longer needed, you should free the string
    with land_free.
    """
    char c[] = "";
    land_buffer_add(self, c, 1)
    char *s = self->buffer
    self->buffer = None
    land_buffer_del(self)
    return s

LandArray *def land_buffer_split(LandBuffer const *self, char delim):
    """
    Creates an array of buffers. If there are n occurences of character delim
    in the buffer, the array contains n + 1 entries. No buffer in the array
    contains the delim character.
    """
    LandArray *a = land_array_new()
    int start = 0
    for int i = 0; i < self->n; i++:
        if self->buffer[i] == delim:
            LandBuffer *l = land_buffer_new()
            land_buffer_add(l, self->buffer + start, i - start)
            land_array_add(a, l)
            start = i + 1
    LandBuffer *l = land_buffer_new()
    land_buffer_add(l, self->buffer + start, self->n - start)
    land_array_add(a, l)
    return a

def land_buffer_strip(LandBuffer *self, char const *what):
    if self->n == 0: return
    int i = 0
    while ustrchr(what, self->buffer[i]):
        i++
    int j = self->n - 1
    while ustrchr(what, self->buffer[j]):
        j--
    memmove(self->buffer, self->buffer + i, 1 + j - i)
    self->size = 1 + j - i

def land_buffer_write_to_file(LandBuffer *self, char const *filename):
    FILE *f = fopen(filename, "w")
    fwrite(self->buffer, 1, self->n, f)
    fclose(f)

int def land_buffer_rfind(LandBuffer *self, char c):
    if self->n == 0: return -1
    for int i = self->n - 1; i >= 0; i--:
        if self->buffer[i] == c: return i
    return -1

def land_buffer_set_length(LandBuffer *self, int n):
    self->n = n

def land_buffer_shorten(LandBuffer *self, int n):
    self->n -= n

LandBuffer *def land_buffer_read_from_file(char const *filename):
    """
    Read a buffer from the given file. If the file cannot be read, return None.
    """
    FILE *pf = fopen(filename, "r")
    if not pf:
        return None
    LandBuffer *self = land_buffer_new()
    while 1:
        int c = fgetc(pf)
        if c < 0: break
        land_buffer_add(self, (char *)&c, 1)
    fclose(pf)
    return self

#ifndef LAND_NO_COMPRESS
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
#endif

int def land_buffer_compare(LandBuffer *self, *other):
    if self->n < other->n: return -1
    if self->n > other->n: return 1
    return memcmp(self->buffer, other->buffer, self->n)

static int def pf_fclose(void *userdata):
    LandBufferAsFile *self = userdata
    land_free(self)
    return 0

static int def pf_getc(void *userdata):
    LandBufferAsFile *self = userdata
    if self->ungetc & 256:
        int c = self->ungetc & 255
        self->ungetc = 0
        return c
    if self->pos >= self->landbuffer->n: return EOF
    int c = ((unsigned char *)self->landbuffer->buffer)[self->pos]
    self->pos++
    return c

static int def pf_ungetc(int c, void *userdata):
    LandBufferAsFile *self = userdata
    self->ungetc = c | 256
    return c

static long def pf_fread(void *p, long n, void *userdata):
    LandBufferAsFile *self = userdata
    if self->ungetc & 256:
        *(char *)p = self->ungetc & 255
        self->ungetc = 0
        n--
        p = (char *)p + 1
    if self->pos + n > self->landbuffer->n:
        n = self->landbuffer->n - self->pos
    memcpy(p, self->landbuffer->buffer + self->pos, n)
    self->pos += n
    return n

static int def pf_putc(int c, void *userdata):
    LandBufferAsFile *self = userdata
    land_buffer_add_char(self->landbuffer, c)
    return c

static long def pf_fwrite(const void *p, long n, void *userdata):
    LandBufferAsFile *self = userdata
    land_buffer_add(self->landbuffer, p, n)
    return n

static int def pf_fseek(void *userdata, int offset):
    return 0

static int def pf_feof(void *userdata):
    LandBufferAsFile *self = userdata
    if self->pos >= self->landbuffer->n: return True
    return False

static int def pf_ferror(void *userdata):
    return 0


#static struct PACKFILE_VTABLE vt = {
    #pf_fclose,
    #pf_getc,
    #pf_ungetc,
    #pf_fread,
    #pf_putc,
    #pf_fwrite,
    #pf_fseek,
    #pf_feof,
    #pf_ferror
#}

#PACKFILE *def land_buffer_read_packfile(LandBuffer *self):
    #"""
    #Returns a packfile to read from the given buffer. The buffer must not be
    #destroyed as long as the packfile is open.
    #"""
    #LandBufferAsFile *lbaf; land_alloc(lbaf)
    #lbaf->landbuffer = self
    #PACKFILE *pf = pack_fopen_vtable(&vt, lbaf)
    #return pf

#PACKFILE *def land_buffer_write_packfile(LandBuffer *self):
    #"""
    #Returns a packfile to write to the given buffer. The buffer must not be
    #destroyed as long as the packfile is open.
    #"""
    #LandBufferAsFile *lbaf; land_alloc(lbaf)
    #lbaf->landbuffer = self
    #PACKFILE *pf = pack_fopen_vtable(&vt, lbaf)
    #return pf




