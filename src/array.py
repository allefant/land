import global stdlib, stdio, allegro5/allegro5
import util
class LandArray:
    int count
    int size
    void **data

class LandArrayIterator:
    int i

static import mem

def LandArrayIterator_first(LandArray *a) -> LandArrayIterator:
    LandArrayIterator i = {0}
    return i

def LandArrayIterator_item(LandArray *a, LandArrayIterator *i) -> void *:
    return i->i < a->count ? a->data[i->i] : None

def LandArrayIterator_next(LandArray *a, LandArrayIterator *i) -> bool:
    i->i++
    return i->i <= a->count

def LandArray__len__(LandArray *a) -> int:
    return a.count

def land_array_new() -> LandArray *:
    """
    Create a new empty array.
    """
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
    int i = self.count++
    if self.count > self->size:
        if self.size == 0:
            self.size = 1
        else:
            self.size *= 2
        self.data = land_realloc(self->data, self->size *sizeof *self->data)
    self.data[i] = data

def land_array_reserve(LandArray *self, int n):
    """
    Allocate n empty (None) entries for the array. Removes any contents
    of the array if it already has any data added to it.
    """
    self.count = self.size = n
    self.data = land_realloc(self.data, self.size * sizeof *self.data)
    memset(self.data, 0, self.count * sizeof *self.data)

def land_array_pop(LandArray *self) -> void *:
    """
    Remove the last element in the array and return it. Only the last element
    in an array can be removed. To remove another element, you could replace
    it with the last (land_array_replace_nth) and remove the last with this
    function.
    """
    if self.count == 0: return None
    int i = --self.count
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
    return self.data[i]

def land_array_remove(LandArray *self, int i) -> void*:
    """
    Return item at position i and replace it with the last item,
    shortening the array by one.

    If i is the last item this is identical to land_array_pop.
    """
    void* last = land_array_pop(self)
    # we removed the very last item
    if i == land_array_count(self): return last
    return land_array_replace_nth(self, i, last)

def land_array_shift_remove(LandArray *self, int i) -> void*:
    """
    Return item at position i and then shift all the other items in
    the array by one.
    """
    void *x = land_array_get(self, i)
    self.count--
    # [ A B C D E F ] now remove i = 2
    # move (D E F) to the C position
    # [ A B D E F ]
    memmove(self.data + i, self.data + i + 1, sizeof(*self.data) * (self.count - i))
    return x

def land_array_add_data(LandArray **array, void *data):
    """
    *deprecated*
    Use land_array_add in new code, as this function might be removed in a
    future version.

    Given a pointer to a (possibly NULL valued) array pointer, create a new node
    with the given data, and add to the (possibly modified) array.
    """
    LandArray *self = *array
    if not self:
        *** "if" LAND_MEMLOG
        self = land_array_new_memlog(__FILE__, __LINE__)
        *** "else"
        self = land_array_new()
        *** "endif"
        *array = self

    land_array_add(self, data)

def land_array_find(LandArray *self, void *data) -> int:
    """
    Searches the array for the given data. If they are contained, return the
    first index i so that land_array_get_nth(array, i) == data. If the data
    cannot be found, -1 is returned.
    """
    for int i = 0 while i < self.count with i++:
        if self.data[i] == data: return i
    return -1

def land_array_find_string(LandArray *self, char const * string) -> int:
    """
    Searches a string array for the given string. If it is contained return the
    first index i so that land_array_get_nth(array, i) equals the string.
    Otherwise -1 is returned.
    """
    for int i = 0 while i < self.count with i++:
        if land_equals(string, self.data[i]): return i
    return -1

def land_array_get_nth(LandArray const *array, int i) -> void *:
    if i < 0: i += array->count
    return array->data[i]

def land_array_get_or_none(LandArray const *array, int i) -> void *:
    if i < 0 or i >= array.count: return None
    return land_array_get_nth(array, i)

def land_array_get(LandArray const *array, int i) -> void *:
    return land_array_get_nth(array, i)

def land_array_is_empty(LandArray const *array) -> bool:
    return array->count == 0

def land_array_replace_nth(LandArray *array, int i, void *data) -> void *:
    """
    Replace the array entry at the given index, and return the previous
    contents.
    """
    if i >= array->count: return None
    void *old = array->data[i]
    array->data[i] = data
    return old

def land_array_replace_or_resize(LandArray *array, int i, void *data) -> void*:
    """
    Replaces the entry at i and returns the previous data.
    If i is outside the size of the array, resize it.
    """
    while array->count < i + 1:
        land_array_add(array, None)
    return land_array_replace_nth(array, i, data)

def land_array_get_last(LandArray *array) -> void*:
    return land_array_get_nth(array, array.count - 1)

def land_array_destroy(LandArray *self):
    """
    Destroys an array. This does not destroy any of the data put into it - loop
    through the array before and destroy the data if there are no other
    references to them.
    """
    if self.data: land_free(self->data)
    land_free(self)

static def cb_free(void *data, void *_) -> int:
    land_free(data)
    return 0

def land_array_destroy_with_strings(LandArray *self):
    land_array_destroy_with_free(self)

def land_array_destroy_with_free(LandArray *self):
    """
    Like [land_array_destroy] but also calls land_free on every
    element.
    """
    land_array_for_each(self, cb_free, None)
    land_array_destroy(self)

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
    qsort(self.data, self->count, sizeof(void *), cmpfnc)

static def alphacomp(void const *a, void const *b) -> int:
    char const * const *as = a
    char const * const *bs = b
    int r = strcmp(*as, *bs)
    return r

def land_array_sort_alphabetical(LandArray *self):
    """
    Expects all array members to be strings and sorts alphabetically.
    """
    land_array_sort(self, alphacomp)

def land_array_count(LandArray const *self) -> int:
    if not self: return 0
    return self.count

def land_array_for_each(LandArray *self, int (*cb)(void *item, void *data),
    void *data) -> int:
    """
    Call the given callback for each array element. If the callback returns
    anything but 0, the iteration is stopped. The return value is the number
    of times the callback was called. The data argument simply is passed as-is
    to the callback.
    """
    if not self: return 0
    int i
    for i = 0 while i < self.count with i++:
        if cb(self.data[i], data): break
    return i

def land_array_clear(LandArray *self):
    """
    Clear all elements in the array.
    """
    self.count = 0

def land_array_concat(LandArray *self, LandArray const *other):
    int new_count = self.count + other->count
    self.size = new_count
    self.data = land_realloc(self->data, self->size *sizeof *self->data)
    # data is void ** so pointer arithmetic works
    memcpy(self.data + self->count, other->data,
        other->count * sizeof * other->data)
    self.count = self->size

def land_array_merge(LandArray *self, *other):
    land_array_concat(self, other)
    land_array_destroy(other)

def land_array_copy(LandArray const *self) -> LandArray *:
    LandArray *copy = land_array_new()
    land_array_concat(copy, self)
    return copy

def land_array_swap(LandArray *self, int a, b):
    if a < 0: a += self.count
    if b < 0: b += self.count
    void *temp = self.data[a]
    self.data[a] = self->data[b]
    self.data[b] = temp

def land_array_move(LandArray *self, int ifrom, ito):
    """
    0 1 2 3 4 5 6
    A B C D E F G
    from: 2 to: 5

    0 1 2 3 4 5 6
    A B D E F C G
    """
    int i = ifrom
    while i != ito:
        if i < ito:
            land_array_swap(self, i, i + 1)
            i += 1
        else:
            land_array_swap(self, i, i - 1)
            i -= 1

def land_array_move_behind(LandArray *self, int a, b):
    """
    Move item at position a so it is behind b. If b is 0 then a is moved to
    the beginning. If b is n then a is moved to the end.
    """
    void *temp = self.data[a]
    if a < b:
        # . . a _ _ _ b . .
        # . . _ _ _ a b . .
        #
        # if b is n:
        # . . a _ _ _ n
        # . . _ _ _ a n
        for int i = a while i < b - 1 with i++:
            self.data[i] = self.data[i + 1]
        self.data[b - 1] = temp
    else:
        # . . b _ _ _ a . .
        # . . a b _ _ _ . .
        for int i = a while i > b with i--:
            self.data[i] = self.data[i - 1]
        self.data[b] = temp

def land_array_reverse(LandArray *self):
    # count == 0: do nothing
    # count == 1: do nothing
    # count == 2: swap(0, 1)
    # count == 3: swap(0, 2)
    # count == 4: swap(0, 3) swap(1, 2)

    for int i in range(self.count / 2):
        land_array_swap(self, i, self.count - 1 - i)

*** "ifdef" LAND_MEMLOG

*** "undef" land_array_new
*** "undef" land_array_destroy
*** "undef" land_array_add
*** "undef" land_array_clear
*** "undef" land_array_merge
*** "undef" land_array_concat
*** "undef" land_array_copy

def land_array_new_memlog(char const *f, int l) -> LandArray *:
    LandArray *array = land_array_new()
    land_memory_add(array, "array", 1, f, l)
    return array

def land_array_destroy_memlog(LandArray *self, char const *f, int l):
    land_memory_remove(self, "array", 1, f, l)
    land_array_destroy(self)

def land_array_add_memlog(LandArray *self, void *data, char const *f, int l):
    land_array_add(self, data)
    land_memory_remove(self, "array", 1, f, l)
    land_memory_add(self, "array", self.size, f, l)

def land_array_copy_memlog(LandArray const *self, char const *f, int l) -> LandArray *:
    LandArray *copy = land_array_copy(self)
    land_memory_add(copy, "array", copy->size, f, l)
    return copy

def land_array_concat_memlog(LandArray *self, LandArray const *other,
        char const *f, int l):
    land_array_concat(self, other)
    land_memory_remove(self, "array", 1, f, l)
    land_memory_add(self, "array", self.size, f, l)

def land_array_merge_memlog(LandArray *self, *other, char const *f, int l):
    land_array_merge(self, other)
    land_memory_remove(self, "array", 1, f, l)
    land_memory_add(self, "array", self.size, f, l)
    land_memory_remove(other, "array", 1, f, l)

def land_array_clear_memlog(LandArray *self, char const *f, int l):
    land_array_clear(self)
    land_memory_remove(self, "array", 1, f, l)
    land_memory_add(self, "array", self.size, f, l)

*** "endif"

global *** "ifdef" LAND_MEMLOG

macro land_array_new() land_array_new_memlog(__FILE__, __LINE__)
macro land_array_destroy(x) land_array_destroy_memlog(x, __FILE__, __LINE__)
macro land_array_add(x, y) land_array_add_memlog(x, y, __FILE__, __LINE__)
macro land_array_copy(x) land_array_copy_memlog(x, __FILE__, __LINE__)
macro land_array_merge(x, y) land_array_merge_memlog(x, y, __FILE__, __LINE__)
macro land_array_concat(x, y) land_array_concat_memlog(x, y, __FILE__, __LINE__)
macro land_array_clear(x) land_array_clear_memlog(x, __FILE__, __LINE__)

global *** "endif"
