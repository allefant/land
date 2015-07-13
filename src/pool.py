static import land.mem

class LandMemoryPool:
    LandMemoryPool *prev
    int allocated
    int used
    void *memory

def land_pool_new_initial(int initial) -> LandMemoryPool *:
    LandMemoryPool *self; land_alloc(self)
    self.allocated = initial
    self.memory = land_calloc(self->allocated)
    self.prev = self
    return self

def land_pool_new() -> LandMemoryPool *:
    return land_pool_new_initial(1024)

def land_pool_destroy(LandMemoryPool *self):
    LandMemoryPool *last = self.prev
    while True:
        LandMemoryPool *prev = last->prev
        land_free(last->memory)
        land_free(last)
        if last == self:
            break
        last = prev

def land_pool_alloc(LandMemoryPool *self, int size) -> void *:
    LandMemoryPool *last = self.prev

    while last->used + size > last->allocated:
        LandMemoryPool *another = land_pool_new_initial(last->allocated * 2)
        another->prev = last
        self.prev = another
        last = another

    void *p = last->memory + last->used
    last->used += size
    return p
