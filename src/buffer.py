static import global stdio, stdlib, string
static import mem
static import file
import array, util, common, exception

static import global zlib if !defined(LAND_NO_COMPRESS)

class LandBuffer:
    uint64_t size # reserved memory
    uint64_t n # number of bytes in the buffer
    char *buffer

class LandBufferAsFile:
    LandBuffer *landbuffer
    int pos
    int ungetc

# can take from start without having to copy memory
class LandRingBuffer:
    LandBuffer ring
    uint64_t c, offset

*** "ifdef" LAND_MEMLOG

*** "undef" land_buffer_new
*** "undef" land_buffer_destroy
*** "undef" land_buffer_finish
*** "undef" land_buffer_read_from_file
*** "undef" land_buffer_split

def land_buffer_new_memlog(char const *f, int l) -> LandBuffer *:
    LandBuffer *self = land_buffer_new()
    land_memory_add(self, "buffer", 1, f, l)
    return self

def land_buffer_destroy_memlog(LandBuffer *self, char const *f, int l):
    land_memory_remove(self, "buffer", 1, f, l)
    land_buffer_destroy(self)

def land_buffer_finish_memlog(LandBuffer *self, char const *f, int l) -> char *:
    land_memory_remove(self, "buffer", 1, f, l)
    char *s = land_buffer_finish(self)
    
    # Give line number of finish call to returned memory block.
    land_memory_remove(s, "", 1, f, l)
    land_memory_add(s, "", strlen(s), f, l)
    return s

def land_buffer_read_from_file_memlog(char const *filename, char const *f, int l) -> LandBuffer *:
    LandBuffer *self = land_buffer_read_from_file(filename)
    land_memory_add(self, "buffer", 1, f, l)
    return self

def land_buffer_split_memlog(LandBuffer const *self, char const *delim, char const *f, int l) -> LandArray *:
    auto a = land_buffer_split(self, delim)
    land_memory_add(a, "array", 1, f, l)
    for LandBuffer *b in a:
        land_memory_add(b, "buffer", 1, f, l)
    return a

*** "endif"

def land_buffer_new() -> LandBuffer *:
    LandBuffer *self
    land_alloc(self)
    return self

def land_buffer_copy(LandBuffer *other) -> LandBuffer *:
    LandBuffer *self
    land_alloc(self)
    land_buffer_add(self, other->buffer, other->n)
    return self

def land_buffer_extract(LandBuffer *other, int x, n) -> LandBuffer *:
    LandBuffer *self = land_buffer_new()
    if n > 0:
        land_buffer_add(self, other.buffer + x, n)
    return self

def land_buffer_copy_from(LandBuffer *other, int x) -> LandBuffer *:
    LandBuffer *self = land_buffer_new()
    land_buffer_add(self, other.buffer + x, other.n - x)
    return self

macro land_buffer_del land_buffer_destroy
def land_buffer_destroy(LandBuffer *self):
    if self.buffer: land_free(self->buffer)
    land_free(self)

def land_buffer_grow(LandBuffer *self, int n):
    # size: 0 1 2 4 8 16 32 64 128 256 ...
    self.n += n
    if self.n > self.size:
        if not self.size: self.size = 1
        while self.size < self.n:
            self.size *= 2
        self.buffer = land_realloc(self.buffer, self.size)
        if not self.buffer:
            land_exception("could not allocate %lu bytes\n", self.size)

def land_buffer_shrink(LandBuffer *self, uint64_t n):
    if n <= self.n:
        self.n -= n
    else:
        self.n = 0

def land_buffer_insert(LandBuffer *self, int pos, char const *buffer, int n):
    land_buffer_grow(self, n)
    memmove(self.buffer + pos + n, self.buffer + pos, self.n - n - pos)
    memcpy(self.buffer + pos, buffer, n)

def land_buffer_move(LandBuffer *self, int64_t from_pos, int64_t to_pos, int64_t n):
    if from_pos < 0: from_pos += self.n
    if to_pos < 0: to_pos += self.n
    memmove(self.buffer + to_pos, self.buffer + from_pos, n)

def land_buffer_cut(LandBuffer *self, int pos, int n):
    memmove(self.buffer + pos, self.buffer + pos + n, self.n - pos - n)
    self.n -= n

def land_buffer_shorten_left(LandBuffer *self, int n):
    land_buffer_cut(self, 0, n)

def land_buffer_add(LandBuffer *self, char const *b, int n):
    land_buffer_insert(self, self.n, b, n)

def land_buffer_addv(LandBuffer *self, char const *format, va_list args):
    va_list args2
    va_copy(args2, args)
    int n = vsnprintf(None, 0, format, args2)
    va_end(args2)
    if n < 0: n = 1023
    char s[n + 1]
    vsnprintf(s, n + 1, format, args)
    land_buffer_add(self, s, n)

def land_buffer_addf(LandBuffer *self, char const *format, ...):
    va_list args
    va_start(args, format)
    land_buffer_addv(self, format, args)
    va_end(args)

def land_buffer_addl(LandBuffer *self, char const *format, ...):
    va_list args
    va_start(args, format)
    land_buffer_addv(self, format, args)
    va_end(args)
    land_buffer_add_char(self, '\n')

def land_buffer_add_uint32_t(LandBuffer *self, uint32_t i):
    land_buffer_add_char(self, i & 255)
    land_buffer_add_char(self, (i >> 8) & 255)
    land_buffer_add_char(self, (i >> 16) & 255)
    land_buffer_add_char(self, (i >> 24) & 255)

def land_buffer_get_uint32_by_index(LandBuffer *self, int pos) -> uint32_t:
    return land_buffer_get_uint32_t(self, pos * sizeof(uint32_t))

def land_buffer_get_uint32_t(LandBuffer *self, int pos) -> uint32_t:
    uint8_t *uc = (uint8_t *)self->buffer + pos
    uint32_t u = *(uc++)
    u += *(uc++) << 8
    u += *(uc++) << 16
    u += *(uc++) << 24
    return u

def land_buffer_pop_uint32_t(LandBuffer *self) -> uint32_t:
    if self.n < 4:
        return 0
    int pos = self.n // 4 - 1
    uint32_t x = land_buffer_get_uint32_t(self, pos)
    land_buffer_shrink(self, 4)
    return x

def land_buffer_get_uint16_t(LandBuffer *self, int pos) -> uint16_t:
    uint8_t *uc = (uint8_t *)self->buffer + pos
    uint16_t u = *(uc++)
    u += *(uc++) << 8
    return u

def land_buffer_get_byte(LandBuffer *self, int pos) -> uint8_t:
    uint8_t *uc = (uint8_t *)self->buffer + pos
    return *uc

def land_buffer_get_float(LandBuffer *self, int pos) -> float:
    float *uc = (float *)(self->buffer + pos)
    return *uc

def land_buffer_add_float(LandBuffer *self, float f):
    uint32_t *i = (void *)&f
    land_buffer_add_uint32_t(self, *i)

def land_buffer_get_land_float(LandBuffer *self, int pos) -> LandFloat:
    LandFloat *uc = (LandFloat *)(self->buffer + pos)
    return *uc

def land_buffer_get_land_float_by_index(LandBuffer *self, int i) -> LandFloat:
    LandFloat *uc = ((LandFloat *)(self->buffer)) + i
    return *uc

def land_buffer_len_land_float(LandBuffer *self) -> int:
    return self.n / sizeof(LandFloat)

def land_buffer_len_uint32(LandBuffer *self) -> int:
    if not self: return 0
    return self.n / sizeof(uint32_t)

def land_buffer_add_land_float(LandBuffer *self, LandFloat f):
    char *b = (void *)&f
    land_buffer_add(self, b, sizeof(f))

def land_buffer_add_char(LandBuffer *self, char c):
    land_buffer_add(self, &c, 1)

def land_buffer_cat(LandBuffer *self, char const *string):
    """
    Appends a zero-terminated string (without the 0 byte) to the buffer.
    """
    land_buffer_add(self, string, strlen(string))

def land_buffer_clear(LandBuffer *self):
    """
    Clears the buffer (but keeps any memory allocation for speedy refilling).
    """
    self.n = 0

def land_buffer_crop(LandBuffer *self):
    """
    Make the buffer use up only the minimum required amount of memory.
    """
    self.buffer = land_realloc(self->buffer, self->n)
    self.size = self->n

def land_buffer_finish(LandBuffer *self) -> char *:
    """
    Destroys the buffer, but returns a C-string constructed from it by appending
    a 0 character. You may not access the pointer you pass to this function
    anymore after it returns. Also, you have to make sure it does not already
    contain any 0 characters. When no longer needed, you should free the string
    with land_free.
    """
    char c[] = "";
    land_buffer_add(self, c, 1)
    char *s = self.buffer
    self.buffer = None
    land_buffer_destroy(self)
    return s

def land_buffer_println(LandBuffer *self):
    printf("%.*s\n", (int)self.n, self.buffer)

def land_buffer_empty(LandBuffer *self) -> bool:
    return self.n == 0

def land_buffer_split(LandBuffer const *self, str delim) -> LandArray *:
    """
    Creates an array of buffers. If there are n occurences of string delim
    in the buffer, the array contains n + 1 entries. No buffer in the array
    contains the delim string.
    """
    LandArray *a = land_array_new()
    int start = 0
    for uint64_t i in range(self.n):
        bool matches = True
        int j = 0
        while delim[j]:
            if self.buffer[i + j] != delim[j]:
                matches = False
                break
            j++
        if matches:
            LandBuffer *l = land_buffer_new()
            land_buffer_add(l, self.buffer + start, i - start)
            land_array_add(a, l)
            start = i + j
    LandBuffer *l = land_buffer_new()
    land_buffer_add(l, self.buffer + start, self->n - start)
    land_array_add(a, l)
    return a

def land_buffer_strip_right(LandBuffer *self, char const *what):
    if self.n == 0: return
    int away = 0
    char *p = self.buffer + self->n
    while p > self.buffer:
        int c = land_utf8_char_back(&p);
        char const *q = what
        while 1:
            int d = land_utf8_char_const(&q)
            if not d:
                goto done
            if c == d:
                away++
                break
    label done
    self.n -= away

def land_buffer_strip_left(LandBuffer *self, char const *what):
    if self.n == 0: return
    int away = 0
    char *p = self.buffer
    while 1:
        label again
        int c = land_utf8_char(&p)
        if not c: break
        char const *q = what
        while 1:
            int d = land_utf8_char_const(&q)
            if not d: break
            if c == d:
                away++
                goto again
        break
    self.n -= away
    memmove(self.buffer, self->buffer + away, self->n)

def land_buffer_strip(LandBuffer *self, char const *what):
    land_buffer_strip_right(self, what)
    land_buffer_strip_left(self, what)

def land_buffer_is(LandBuffer *self, char const *what) -> bool:
    uint64_t n = strlen(what)
    if n != self.n:
        return False
    return memcmp(self.buffer, what, self.n) == 0

def land_buffer_remove_if_start(LandBuffer *self, char const *what):
    if memcmp(self.buffer, what, strlen(what)) == 0:
        land_buffer_shorten_left(self, strlen(what))

def land_buffer_remove_if_end(LandBuffer *self, char const *what):
    if memcmp(self.buffer + self.n - strlen(what), what,
            strlen(what)) == 0:
        land_buffer_shorten(self, strlen(what))

def land_buffer_rfind(LandBuffer *self, char c) -> int:
    if self.n == 0: return -1
    for int i = self.n - 1 while i >= 0 with i--:
        if self.buffer[i] == c: return i
    return -1

def land_buffer_find(LandBuffer const *self, int offset,
        char const *what) -> int:
    int n = strlen(what)
    for uint64_t i in range(offset, self.n):
        for int j in range(n):
            if self.buffer[i + j] != what[j]:
                goto mismatch
        return i
        label mismatch
    return -1

def land_buffer_replace(LandBuffer *self, int offset,
        char const *wat, *wit) -> int:
    int x = land_buffer_find(self, offset, wat)
    if x < 0:
        return x
    land_buffer_cut(self, x, strlen(wat))
    land_buffer_insert(self, x, wit, strlen(wit))
    return x + strlen(wit)

def land_buffer_replace_all(LandBuffer *self,
        char const *wat, *wit) -> int:
    int x = 0
    int count = 0
    while True:
        x = land_buffer_replace(self,x, wat, wit)
        if x < 0:
            break
        count++
    return count

def land_buffer_set_length(LandBuffer *self, int n):
    self.n = n

def land_buffer_shorten(LandBuffer *self, int n):
    self.n -= n

def land_buffer_read_from_file(char const *filename) -> LandBuffer *:
    """
    Read a buffer from the given file. If the file cannot be read, return None.
    """
    LandFile *pf = land_file_new(filename, "rb")
    if not pf:
        return None
    LandBuffer *self = land_buffer_new()
    land_file_add_to_buffer(pf, self)
    land_file_destroy(pf)
    return self

def land_buffer_write_to_file(LandBuffer *self, char const *filename) -> bool
    LandFile *pf = land_file_new(filename, "wb")
    if not pf:
        return False
    uint64_t written = land_file_write(pf, self.buffer, self.n)
    land_file_destroy(pf)
    return written == self.n

def land_ring_buffer_new -> LandRingBuffer*:
    LandRingBuffer *self
    land_alloc(self)
    return self

def land_ring_buffer_destroy(LandRingBuffer* self):
    if self.ring.buffer:
        land_free(self.ring.buffer)
    land_free(self)

def land_ring_add_uint32(LandRingBuffer *self, uint32_t x):
    # size=8, n=7, c=0, offset=3
    # |   |   |   | a | b | c | d |   |
    # |_0_|_1_|_2_|_3_|_4_|_5_|_6_|_7_|
    # size=8, n=8, c=1, offset=3
    # | f |   |   | a | b | c | d | e |
    # |_0_|_1_|_2_|_3_|_4_|_5_|_6_|_7_|
    # size=8, n=8, c=2, offset=7
    # | b | c |   |   |   |   |   | a |
    # |_0_|_1_|_2_|_3_|_4_|_5_|_6_|_7_|

    # we have space at the end of the buffer
    if self.offset + self.ring.n + 4 <= self.ring.size:
        uint32_t *ring = (void*)self.ring.buffer
        int i = self.ring.n // 4
        ring[i] = x
        self.ring.n += 4
    # we have space at the beginning, before offset
    elif self.c + 4 <= self.offset:
        uint32_t *ring = (void*)self.ring.buffer
        int i = self.c // 4
        ring[i] = x
        self.c += 4
    # we are full and need to reallocate
    else:
        land_buffer_grow(&self.ring, self.c + 4)
        # first copy the self.c ring bytes to the end
        memmove(self.ring.buffer + self.ring.n, self.ring.buffer, self.c)
        # then shuffle everything back to offset 0
        memmove(self.ring.buffer, self.ring.buffer + self.offset, self.ring.n)
        self.ring.n = self.ring.n - self.offset + self.c
        self.c = 0
        self.offset = 0
        uint32_t *ring = (void*)self.ring.buffer
        int i = self.ring.n // 4 - 1
        ring[i] = x

def land_ring_pop_first_uint32(LandRingBuffer *self) -> uint32_t:
    if self.ring.n == 0: return 0
    uint32_t *ring = (void *)self.ring.buffer
    int i = self.offset // 4
    uint32_t x = ring[i]
    self.offset += 4
    if self.offset == self.ring.n:
        self.offset = 0
        self.ring.n = self.c
        self.c = 0
    return x

def land_ring_len(LandRingBuffer *self) -> uint64_t:
    return self.ring.n - self.offset + self.c

def land_ring_len_uint32(LandRingBuffer *self) -> uint64_t:
    return land_ring_len(self) // sizeof(uint32_t)

*** "ifndef" LAND_NO_COMPRESS
def land_buffer_compress(LandBuffer *self):
    uLongf destlen = self.n * 1.1 + 12
    Bytef *dest = land_malloc(destlen)
    compress(dest, &destlen, (void *)self->buffer, self->n)
    dest = land_realloc(dest, destlen)
    land_free(self.buffer)
    self.buffer = (void *)dest
    self.size = self->n = destlen

def land_buffer_decompress(LandBuffer *self):
    z_stream z
    z.zalloc = Z_NULL
    z.zfree = Z_NULL
    z.opaque = Z_NULL
    z.next_in = (void *)self.buffer
    z.avail_in = self.n
    int err = inflateInit2(&z, 15 | 32)
    if err != Z_OK:
        return
    LandBuffer *temp = land_buffer_new()

    char *out = malloc(8192)
    while True:
        z.avail_out = 8192
        z.next_out = (void *)out
        err = inflate(&z, Z_NO_FLUSH)
        if err < 0:
            goto break2
        land_buffer_add(temp, out, 8192 - z.avail_out)
        if z.avail_out > 0:
            break
    label break2
    land_free(out)
    land_free(self.buffer)
    self.buffer = temp.buffer
    self.n = temp.n
    temp.buffer = None
    land_buffer_destroy(temp)
*** "endif"

def land_buffer_compare(LandBuffer *self, *other) -> int:
    if self.n < other->n: return -1
    if self.n > other->n: return 1
    return memcmp(self.buffer, other->buffer, self->n)

global *** "ifdef" LAND_MEMLOG

macro land_buffer_new() land_buffer_new_memlog(__FILE__, __LINE__)
macro land_buffer_destroy(x) land_buffer_destroy_memlog(x, __FILE__, __LINE__)
macro land_buffer_finish(x) land_buffer_finish_memlog(x, __FILE__, __LINE__)
macro land_buffer_read_from_file(x) land_buffer_read_from_file_memlog(x, __FILE__, __LINE__)
macro land_buffer_split(x, y) land_buffer_split_memlog(x, y, __FILE__, __LINE__)

global *** "endif"
