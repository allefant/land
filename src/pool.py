static import land.mem
import land.array

class LandMemoryPool:
    """
    Allocate by adding to a contiguous memory block.
    """
    LandMemoryPool *prev
    int allocated
    int used
    void *memory

class LandAutoFree:
    """
    Keep a list of pointers to be freed later.
    """
    LandArray *pointers

def land_auto_free_new -> LandAutoFree*:
    LandAutoFree *self; land_alloc(self)
    self.pointers = land_array_new()
    return self

def land_auto_free_add(LandAutoFree *self, void *pointer):
    if not self: return
    land_array_add(self.pointers, pointer)

def land_auto_free(LandAutoFree *self):
    land_array_destroy_with_free(self.pointers)
    land_free(self)

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
