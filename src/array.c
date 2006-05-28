#ifdef _PROTOTYPE_

#include <stdlib.h>

#define land_method(_returntype, _name, _params) _returntype (*_name)_params
#define land_call_method(self, method, params) if (self->vt->method) self->vt->method params

typedef struct LandArray LandArray;
struct LandArray
{
    int count;
    void **data;
};

#endif /* _PROTOTYPE_ */

#include "array.h"
#include "memory.h"

/* Given a pointer to a (possibly NULL valued) array pointer, create a new node
 * with the given data, and add to the (possibly modified) array.
 */
void land_array_add_data(LandArray **array, void *data)
{
    LandArray *self = *array;
    if (!self)
    {
        land_alloc(self)
    }
    self->data = land_realloc(self->data, (self->count + 1) * sizeof *self->data);
    self->data[self->count] = data;
    self->count++;
    *array = self;
}

void *land_array_get_nth(LandArray *array, int i)
{
    return array->data[i];
}

void land_array_destroy(LandArray *self)
{
    land_free(self->data);
    land_free(self);
}

void land_array_sort(LandArray *self, int (*cmpfnc)(void const *a, void const *b))
{
    qsort(self->data, self->count, sizeof(void *), cmpfnc);
}
