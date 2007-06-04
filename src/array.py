import global stdlib, allegro, stdio
class LandArray:
    int count
    int size
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

def land_array_add(LandArray *self, void *data):
    """
    Add data to an array.
    """
    # count size
    # 0     0
    # 1     1
    # 2     2
    # 3     4
    # 4     4
    # 5     8
    # 6     8
    # 7     8
    # 8     8
    # 9     16
    int i = self->count++
    if self->count > self->size:
        if self->size == 0:
            self->size = 1
        else:
            self->size *= 2
        self->data = land_realloc(self->data, self->size *sizeof *self->data)
    self->data[i] = data

void *def land_array_pop(LandArray *self):
    """
    Remove the last element in the array and return it. Only the last element
    in an array can be removed. To remove another element, you could replace
    it with the last (land_array_replace_nth) and remove the last with this
    function.
    """
    if self->count == 0: return None
    int i = --self->count
    # We should eventually reduce the allocated memory size as well. One idea
    # would be to half the size when only 25% are filled anymore (not 50%, since
    # adding/removing at just the 50% mark will constantly grow/shrink then.)
    # Also, a likely scenario is to pop the array empty and then destroy, so
    # shrinking might not be needed at all.
    #
    # count size
    # 9     16
    # 8     16
    # 7     16
    # 6     16
    # 5     16
    # 4     8 (25%)
    # 3     8
    # 2     4 (25%)
    # 1     2 (25%)
    # 0     0 (0 is special cased and we completely free)
    return self->data[i]

def land_array_add_data(LandArray **array, void *data):
    """
    *deprecated*
    Use land_array_add in new code, as this function might be removed in a
    future version.

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
        *array = self

    land_array_add(self, data)

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

def land_array_sort(LandArray *self, int (*cmpfnc)(void const *a,
    void const *b)):
    """
    Sorts the entries in the array. The given callback function gets passed
    two direct pointers to two array elements, and expects a return value
    determining the order:
    < 0: a is before b
    = 0: order is arbitrary
    > 0: a is after b
    """
    qsort(self->data, self->count, sizeof(void *), cmpfnc)

static int def alphacomp(void const *a, void const *b):
    char const * const *as = a
    char const * const *bs = b
    int r = ustrcmp(*as, *bs)
    return r

def land_array_sort_alphabetical(LandArray *self):
    """
    Expects all array members to be strings and sorts alphabetically.
    """
    land_array_sort(self, alphacomp)

int def land_array_count(LandArray *self):
    if not self: return 0
    return self->count

int def land_array_for_each(LandArray *self, int (*cb)(void *item, void *data),
    void *data):
    """
    Call the given callback for each array element. If the callback returns
    anything but 0, the iteration is stopped. The return value is the number
    of times the callback was called. The data argument simply is passed as-is
    to the callback.
    """
    if not self: return 0
    int i
    for i = 0; i < self->count; i++:
        if cb(self->data[i], data): break
    return i

def land_array_clear(LandArray *self):
    """
    Clear all elements in the array.
    """
    self->count = 0

#header
#ifdef LAND_MEMLOG

macro land_array_new() land_array_new_memlog(__FILE__, __LINE__)
macro land_array_destroy(x) land_array_destroy_memlog(x, __FILE__, __LINE__)

#endif
