import global stdio, stdlib, allegro

class LandHashEntry:
    char *thekey
    void *data
    int n

class LandHash:
    int count
    int size
    int bits
    unsigned int (*hash_function)(LandHash *self, char const *thekey)
    LandHashEntry **entries

import array

static import hash, memory

#ifdef LAND_MEMLOG

#undef land_hash_new
#undef land_hash_destroy

LandHash *def land_hash_new_memlog(char const *f, int l):
    LandHash *hash = land_hash_new()
    land_memory_add(hash, "hash", 1, f, l)
    return hash

def land_hash_destroy_memlog(LandHash *self, char const *f, int l):
    land_hash_destroy(self)
    land_memory_remove(self, "hash", 1, f, l)

#endif


#
# FIXME: This is the worst possible hash function.
# 
static unsigned int def hash_function(LandHash *self, char const *thekey):
    int i
    unsigned int hash = 5381
    for i = 0; thekey[i]; i++:
        unsigned char c = thekey[i]
        hash = hash * 33 + c

    return hash & (self->size - 1)

LandHash *def land_hash_new():
    LandHash *self
    land_alloc(self)
    self->hash_function = hash_function
    return self

def land_hash_destroy(LandHash *self):
    int i
    for i = 0; i < self->size; i++:
        LandHashEntry *entry = self->entries[i]
        if entry:
            int j
            for j = 0; j < entry->n; j++:
                land_free(entry[j].thekey)

            land_free(entry)


    if self->entries: land_free(self->entries)
    land_free(self)

void *def land_hash_insert(LandHash *self, char const *thekey, void *data):
    int i

    # Need to resize? 
    if (self->count + 1) * 2 > self->size:
        int oldsize = self->size
        LandHashEntry **oldentries = self->entries
        if !self->size: self->bits = 1 # for first entry, we already want size 2 
        else: self->bits++
        self->size = 1 << self->bits
        self->entries = land_calloc(self->size * sizeof *self->entries)
        self->count = 0
        for i = 0; i < oldsize; i++:
            LandHashEntry *entry = oldentries[i]
            if entry:
                int j
                for j = 0; j < entry->n; j++:
                    land_hash_insert(self, entry[j].thekey, entry[j].data)
                    land_free(entry[j].thekey)

                land_free(entry)


        if oldentries: land_free(oldentries)

    # Now there should be ample room to add the new one. 
    i = self->hash_function(self, thekey)
    LandHashEntry *entry = self->entries[i]
    int n = entry ? entry->n + 1 : 1
    self->entries[i] = land_realloc(entry, n * sizeof *entry)
    self->entries[i][n - 1].thekey = land_strdup(thekey)
    self->entries[i][n - 1].data = data
    self->entries[i]->n = n
    self->count++
    return data

void *def land_hash_remove(LandHash *self, char const *thekey):
    if !self->size: return NULL
    int i = self->hash_function(self, thekey)
    if !self->entries[i]: return NULL
    int n = self->entries[i]->n
    int j
    for j = 0; j < n; j++:
        if not ustrcmp(self->entries[i][j].thekey, thekey):
            void *data = self->entries[i][j].data
            land_free(self->entries[i][j].thekey)
            self->entries[i]->n--
            self->entries[i][j] = self->entries[i][n - 1]
            self->entries[i] = land_realloc(self->entries[i],
                self->entries[i]->n * sizeof *self->entries[i])
            self->count--
            return data

    return NULL

void *def land_hash_get(LandHash *self, char const *thekey):
    if !self->size: return NULL
    int i = self->hash_function(self, thekey)
    if !self->entries[i]: return NULL
    int j
    for j = 0; j < self->entries[i]->n; j++:
        if not ustrcmp(self->entries[i][j].thekey, thekey):
            return self->entries[i][j].data

    return NULL

LandArray *def land_hash_keys(LandHash *hash):
    LandArray *array = land_array_new()
    int i
    for i = 0; i < hash->size; i++:
        if hash->entries[i]:
            int n = hash->entries[i]->n
            int j
            for j = 0; j < n; j++:
                land_array_add_data(&array, hash->entries[i][j].thekey)


    return array

LandArray *def land_hash_data(LandHash *hash):
    LandArray *array = land_array_new()
    int i
    for i = 0; i < hash->size; i++:
        if hash->entries[i]:
            int n = hash->entries[i]->n
            int j
            for j = 0; j < n; j++:
                land_array_add_data(&array, hash->entries[i][j].data)


    return array

def land_hash_print_stats(LandHash *hash):
    int i
    int u = 0
    int c = 0
    int l = 0
    for i = 0; i < hash->size; i++:
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

#header
#ifdef LAND_MEMLOG

macro land_hash_new() land_hash_new_memlog(__FILE__, __LINE__)
macro land_hash_destroy(x) land_hash_destroy_memlog(x, __FILE__, __LINE__)

#endif
