#ifdef _PROTOTYPE_

#include <stdio.h>
#include <stdlib.h>
#include <allegro.h>

typedef struct LandHash LandHash;
typedef struct LandHashEntry LandHashEntry;

struct LandHashEntry
{
    char *thekey;
    void *data;
    int n;
};

struct LandHash
{
    int count;
    int size;
    unsigned int (*hash_function)(LandHash *self, char const *thekey);
    LandHashEntry **entries;
};

#endif /* _PROTOTYPE_ */

#include "hash.h"
#include "memory.h"

/*
 * FIXME: This is the worst possible hash function.
 */
static unsigned int hash_function(LandHash *self, char const *thekey)
{
    int i, s = 0;
    unsigned int hash = 0;
    for (i = 0; thekey[i]; i++)
    {
        hash |= thekey[i] << s;
        s += 8;
        s &= 31;
    }
    return hash & (self->size - 1);
}

LandHash *land_hash_new(void)
{
    LandHash *self;
    land_alloc(self);
    self->hash_function = hash_function;
    return self;
}

void land_hash_destroy(LandHash *self)
{
    int i;
    for (i = 0; i < self->size; i++)
    {
        LandHashEntry *entry = self->entries[i];
        if (entry)
        {
            int j;
            for (j = 0; j < entry->n; j++)
            {
                land_free(entry[j].thekey);
            }
            land_free(entry);
        }
    }
    land_free(self);
}

void *land_hash_insert(LandHash *self, char const *thekey, void *data)
{
    int i;
    self->count++;
    if (self->count * 2 > self->size)
    {
        int oldsize = self->size;
        LandHashEntry **oldentries = self->entries;
        if (!self->size)
            self->size = 1;
        else
            self->size *= 2;
        self->entries = land_calloc(self->size * sizeof *self->entries);
        self->count = 0;
        for (i = 0; i < oldsize; i++)
        {
            LandHashEntry *entry = oldentries[i];
            if (entry)
            {
                int j;
                for (j = 0; j < entry->n; j++)
                {
                    land_hash_insert(self, entry[j].thekey, entry[j].data);
                    land_free(entry[j].thekey);
                }
                land_free(entry);
            }
        }
        land_free(oldentries);
    }
    i = self->hash_function(self, thekey);
    LandHashEntry *entry = self->entries[i];
    int n = entry ? entry->n + 1 : 1;
    self->entries[i] = land_realloc(entry, n * sizeof *entry);
    self->entries[i][n - 1].thekey = land_strdup(thekey);
    self->entries[i][n - 1].data = data;
    self->entries[i]->n = n;
    return data;
}

void *land_hash_remove(LandHash *self, char const *thekey)
{
    int i = self->hash_function(self, thekey);
    if (!self->entries[i]) return NULL;
    int n = self->entries[i]->n;
    int j;
    for (j = 0; j < n; j++)
    {
        if (!ustrcmp(self->entries[i][j].thekey, thekey))
        {
            void *data = self->entries[i][j].data;
            land_free(self->entries[i][j].thekey);
            self->entries[i]->n--;
            self->entries[i][j] = self->entries[i][n - 1];
            self->entries[i] = land_realloc(self->entries[i],
                self->entries[i]->n * sizeof *self->entries[i]);
            self->count--;
            return data;
        }
    }
    return NULL;
}

void *land_hash_get(LandHash *self, char const *thekey)
{
    int i = self->hash_function(self, thekey);
    if (!self->entries[i])
        return NULL;
    int j;
    for (j = 0; j < self->entries[i]->n; j++)
    {
        if (!ustrcmp(self->entries[i][j].thekey, thekey))
            return self->entries[i][j].data;
    }
    return NULL;
}
