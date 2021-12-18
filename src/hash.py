import global assert, stdio, stdlib

class LandHashEntry:
    char *thekey
    void *data
    int n

class LandHash:
    """
    A hash stores a number of objects, which can be accessed by a named key.
    """
    int count # Actual number of elements.
    int size # Size of table.
    int bits
    unsigned int (*hash_function)(LandHash *self, char const *thekey)
    LandHashEntry **entries

class LandHashIterator:
    int i, j

class LandHashKeysIterator:
    int i, j

import array

static import hash, mem

def _get_data(LandHash *self, LandHashIterator *i, void **data) -> bool:
    if not self.entries: return False
    while i->i < self.size:
        if self.entries[i->i]:
            if i->j < self.entries[i->i][0].n:
                if data: *data = self.entries[i->i][i->j].data
                return True
            i->j = 0
        i->i++
    return False

def _get_key(LandHash *self, LandHashKeysIterator *i, void **data) -> bool:
    if not self.entries: return False
    while i->i < self.size:
        if self.entries[i->i]:
            if i->j < self.entries[i->i][0].n:
                if data: *data = self.entries[i->i][i->j].thekey
                return True
            i->j = 0
        i->i++
    return False

def land_hash_count(LandHash *self) -> int:
    return self.count

def LandHashIterator_first(LandHash *self) -> LandHashIterator:
    LandHashIterator i = {0, 0}
    return i

def LandHashIterator_item(LandHash *self, LandHashIterator *i) -> void *:
    void *data = None
    _get_data(self, i, &data)
    return data

def LandHashIterator_next(LandHash *self, LandHashIterator *i) -> bool:
    if _get_data(self, i, None):
        i->j++
        return True
    return False

def LandHashKeysIterator_first(LandHash *self) -> LandHashKeysIterator:
    LandHashKeysIterator i = {0, 0}
    return i

def LandHashKeysIterator_item(LandHash *self, LandHashKeysIterator *i) -> void *:
    void *data = None
    _get_key(self, i, &data)
    return data

def LandHashKeysIterator_next(LandHash *self, LandHashKeysIterator *i) -> bool:
    if _get_key(self, i, None):
        i->j++
        return True
    return False

*** "ifdef" LAND_MEMLOG

*** "undef" land_hash_new
*** "undef" land_hash_destroy

def land_hash_new_memlog(char const *f, int l) -> LandHash *:
    LandHash *hash = land_hash_new()
    land_memory_add(hash, "hash", 1, f, l)
    return hash

def land_hash_destroy_memlog(LandHash *self, char const *f, int l):
    land_hash_destroy(self)
    land_memory_remove(self, "hash", 1, f, l)

*** "endif"


#
# FIXME: This is the worst possible hash function.
# 
static def hash_function(LandHash *self, char const *thekey) -> unsigned int:
    int i
    unsigned int hash = 5381
    for i = 0 while thekey[i] with i++:
        unsigned char c = thekey[i]
        hash = hash * 33 + c

    return hash & (self.size - 1)

def land_hash_new() -> LandHash *:
    """Create a new LandHash."""
    LandHash *self
    land_alloc(self)
    self.hash_function = hash_function
    return self

def land_hash_clear(LandHash *self):
    """
    Clears the hash. Referenced data are not touched though.
    """
    for int i in range(self.size):
        LandHashEntry *entry = self.entries[i]
        if entry:
            int j
            for j = 0 while j < entry->n with j++:
                land_free(entry[j].thekey)

            land_free(entry)

    self.count = 0
    self.size = 0

    if self.entries:
        land_free(self.entries)
        self.entries = None

def land_hash_destroy(LandHash *self):
    """
    Destroy a LandHash. The data inside the hash are not freed (just
    everything else, like key names and internal data structures).
    """
    if not self: return
    land_hash_clear(self)
    land_free(self)

def land_hash_insert(LandHash *self, char const *thekey, void *data) -> void *:
    """Insert data into a LandHash.
    
    A LandHash simply is a mapping of keys to data pointers - it will never
    touch the passed data in any way. E.g. you need to make sure to delete any
    pointers you add to a hash. A copy of the passed key is made so you need
    not keep it around.
    
    If the key already exists, there will be two entries with the same key
    from now on, and it is undefined behavior which one will get returned when
    querying for the key."""

    assert(thekey)

    int i

    # Need to resize? 
    if (self.count + 1) * 2 > self->size:
        int oldsize = self.size
        LandHashEntry **oldentries = self.entries
        if not self.size: self->bits = 1 # for first entry, we already want size 2 
        else: self.bits++
        self.size = 1 << self->bits
        self.entries = land_calloc(self->size * sizeof *self->entries)
        self.count = 0
        for i = 0 while i < oldsize with i++:
            LandHashEntry *entry = oldentries[i]
            if entry:
                int j
                for j = 0 while j < entry[0].n with j++:
                    land_hash_insert(self, entry[j].thekey, entry[j].data)
                    land_free(entry[j].thekey)

                land_free(entry)

        if oldentries: land_free(oldentries)

    # Now there should be ample room to add the new one. 
    i = self.hash_function(self, thekey)
    LandHashEntry *entry = self.entries[i]
    int n = entry ? entry->n + 1 : 1
    self.entries[i] = land_realloc(entry, n * sizeof *entry)
    self.entries[i][n - 1].thekey = land_strdup(thekey)
    self.entries[i][n - 1].data = data
    self.entries[i][0].n = n
    self.count++
    return data

def land_hash_remove(LandHash *self, char const *thekey) -> void *:
    """Remove the first entry found with the key, and return the associated
    data.
    
    The returned pointer might need to be destroyed after you remove it from
    the hash, if it has no more use.
    """
    if not self.size: return None
    int i = self.hash_function(self, thekey)
    if not self.entries[i]: return None
    int n = self.entries[i][0].n
    int j
    for j = 0 while j < n with j++:
        if not strcmp(self.entries[i][j].thekey, thekey):
            void *data = self.entries[i][j].data
            land_free(self.entries[i][j].thekey)
            if n > 1:
                self.entries[i][j] = self->entries[i][n - 1]
                self.entries[i] = land_realloc(self->entries[i],
                    (n - 1) * sizeof *self.entries[i])
                self.entries[i][0].n = n - 1
            else:
                land_free(self.entries[i])
                self.entries[i] = None
            self.count--
            return data

    return None

static def land_hash_get_entry(LandHash *self,
        char const *thekey) -> LandHashEntry *:
    if not self.size or not thekey: return None
    int i = self.hash_function(self, thekey)
    if not self.entries[i]: return None
    int j
    for j = 0 while j < self.entries[i][0].n with j++:
        if not strcmp(self.entries[i][j].thekey, thekey):
            return &self.entries[i][j]

    return None

def land_hash_replace(LandHash *self, char const *thekey, void *data) -> void *:
    """
    If an association to the given key exists, replace it with the given data,
    and return the old data.
    Else, do the same as land_hash_insert, and return None.
    """
    LandHashEntry *entry = land_hash_get_entry(self, thekey)
    if entry:
        void *old = entry->data
        entry->data = data
        return old
    land_hash_insert(self, thekey, data)
    return None

def land_hash_get(LandHash *self, char const *thekey) -> void *:
    """Return the data associated with a hash key. If the key exists multiple
    times, it can be not relied on a certain one being returned. It might always
    be the same, but it might not be - this is especially true if other entries
    are added which could lead to a re-hashing when it gets too full.

    If the key is not found, None is returned.
    """
    LandHashEntry *entry = land_hash_get_entry(self, thekey)
    if entry: return entry->data
    return None

def land_hash_has(LandHash *self, char const *thekey) -> int:
    LandHashEntry *entry = land_hash_get_entry(self, thekey)
    if entry: return True
    return False

def land_hash_keys(LandHash *hash, bool alloc) -> LandArray *:
    """Return an array containing all the keys in the hash.

    If alloc is true, each key is allocated and must be freed. A
    convenient way is to use land_array_destroy_with_strings.

    Otherwise the strings are direct pointers into the hash - so you
    must not modify or free them, and they will get invalid if the hash
    is modifed (even just by adding/removing an unrelated key).

    You are responsible for destroying the array with land_array_destroy
    when you are done using it.
    """
    LandArray *array = land_array_new()
    int i
    for i = 0 while i < hash->size with i++:
        if hash->entries[i]:
            int n = hash->entries[i]->n
            int j
            for j = 0 while j < n with j++:
                char *key = hash->entries[i][j].thekey
                if alloc:
                    key = land_strdup(key)
                land_array_add_data(&array, key)

    return array   

def land_hash_data(LandHash *hash) -> LandArray *:
    """Return an array with all the data pointers in the hash. If you want to
    destroy a hash including all its data, this may be a convenient way to
    do it:

    LandArray *data = land_hash_data(hash)
    for int i = 0 while i < land_array_count(data) with i++:
        void *entry = land_array_get_nth(data, i)
        land_free(entry)
    land_array_destroy(data)
    land_hash_destroy(hash)

    """
    LandArray *array = land_array_new()
    int i
    for i = 0 while i < hash->size with i++:
        if hash->entries[i]:
            int n = hash->entries[i]->n
            int j
            for j = 0 while j < n with j++:
                land_array_add_data(&array, hash->entries[i][j].data)


    return array

def land_hash_print_stats(LandHash *hash):
    """This is an internal function for debugging purposes, which will print
    out statistics about the hash to the console.
    """
    int i
    int u = 0
    int c = 0
    int l = 0
    for i = 0 while i < hash->size with i++:
        if hash->entries[i]:
            int n = hash->entries[i]->n
            if n > 1: c += n
            if n > l: l = n
            u++

    printf("hash stats: %d/%d[%d%%] full, %d/%d[%d%%] used, %d/%d[%d%%] colliding, longest chain is %d.\n",
        hash->count, hash->size, hash->size ? 100 * hash->count / hash->size : 0,
        u, hash->size, hash->size ? 100 * u / hash->size : 0,
        c, hash->count, hash->count ? 100 * c / hash->count : 0,
        l)

global *** "ifdef" LAND_MEMLOG

macro land_hash_new() land_hash_new_memlog(__FILE__, __LINE__)
macro land_hash_destroy(x) land_hash_destroy_memlog(x, __FILE__, __LINE__)

global *** "endif"
