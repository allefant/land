import land.array, land.hash, land.mem, land.buffer

class LandProtobuf:
    LandBuffer *data
    uint64_t pos
    uint64_t end

LandProtobuf *def land_protobuf_load(char const *filename):
    LandBuffer *b = land_buffer_read_from_file(filename)
    if not b:
        return None

    LandProtobuf *pbuf
    land_alloc(pbuf)

    pbuf->data = b
    pbuf->end = b->n
    
    return pbuf

static uint64_t varint(LandProtobuf *self):
    uint64_t x = 0
    int s = 0
    while True:
        uint8_t c = self->data->buffer[self->pos++]
        x += (c & 127) << s
        s += 7
        if c & 128:
            continue
        return x

int def land_protobuf_next(LandProtobuf *self, uint64_t *size):
    if self.pos >= self->end:
        return 0

    int x = varint(self)
    int kind = x & 3
    if kind == 2:
        *size = varint(self)

    return x >> 3

def land_protobuf_sub_start(LandProtobuf *self, uint64_t *size):
    uint64_t end = self.end
    self.end = self->pos + *size
    *size = end

def land_protobuf_sub_end(LandProtobuf *self, uint64_t end):
    self.pos = self->end
    self.end = end

static macro R(T):
    T x = *(T *)(self->data->buffer + self->pos)
    self->pos += sizeof(T)
    return x

double def land_protobuf_double(LandProtobuf *self):
    double x
    void *p = &x
    memcpy(p, self.data->buffer + self->pos, 8)
    self.pos += 8
    return x

float def land_protobuf_float(LandProtobuf *self):
    float x
    void *p = &x
    memcpy(p, self.data->buffer + self->pos, 4)
    self.pos += 4
    return x

uint32_t def land_protobuf_fixed32(LandProtobuf *self):
    R(uint32_t)

int32_t def land_protobuf_sfixed32(LandProtobuf *self):
    R(int32_t)

char *def land_protobuf_string(LandProtobuf *self, int size):
    self.pos += size
    return self.data->buffer + self->pos - size

def land_protobuf_destroy(LandProtobuf *self):
    land_buffer_del(self.data)
    land_free(self)

