import global stdlib
class LandArray:
    int count
    void **data

static import array, memory

#ifdef LAND_MEMLOG

#undef land_array_new
#undef land_array_destroy

LandArray *def land_array_new_memlog(char const *f, int l):
    LandArray *array = land_array_new()
    land_memory_add(array, "array", 1, f, l)
    return array

def land_array_destroy_memlog(LandArray *self, char const *f, int l):
    land_memory_remove(self, "array", 1, f, l)
    land_array_destroy(self)

#endif

LandArray *def land_array_new():
    LandArray *self
    land_alloc(self)
    return self

def land_array_add_data(LandArray **array, void *data):
    """
    Given a pointer to a (possibly NULL valued) array pointer, create a new node
    with the given data, and add to the (possibly modified) array.
    """
    LandArray *self = *array
    if !self:
        #ifdef LAND_MEMLOG
        self = land_array_new_memlog(__FILE__, __LINE__)
        #else
        self = land_array_new()
        #endif

    self->data = land_realloc(self->data, (self->count + 1) * sizeof *self->data)
    self->data[self->count] = data
    self->count++
    *array = self

void *def land_array_get_nth(LandArray *array, int i):
    return array->data[i]

void *def land_array_replace_nth(LandArray *array, int i, void *data):
    """
    Replace the array entry at the given index, and return the previous
    contents.
    """
    void *old = array->data[i]
    array->data[i] = data
    return old

def land_array_destroy(LandArray *self):
    """
    Destroys an array. This does not destroy any of the data put into it - loop
    through the array before and destroy the data if there are no other
    references to them.
    """
    if self->data: land_free(self->data)
    land_free(self)

def land_array_sort(LandArray *self, int (*cmpfnc)(void const *a, void const *b)):
    qsort(self->data, self->count, sizeof(void *), cmpfnc)

int def land_array_count(LandArray *self):
    if not self: return 0
    return self->count

#header
#ifdef LAND_MEMLOG

macro land_array_new() land_array_new_memlog(__FILE__, __LINE__)
macro land_array_destroy(x) land_array_destroy_memlog(x, __FILE__, __LINE__)

#endif
