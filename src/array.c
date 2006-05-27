#ifdef _PROTOTYPE_

#include <stdlib.h>

#define land_method(_returntype, _name, _params) _returntype (*_name)_params

#define land_call_method(self, method, params) if (self->vt->method) self->vt->method params

#define land_type(name) \
    typedef struct name name; \
    struct name

#define land_array(name) \
    name **name##_array = NULL; \
    int name##_count = 0;

#define land_init_member(self, member) self->member = member

#define land_local(name) \
    static name **name##_array = NULL; \
    static int name##_count = 0;

#define land_alloc(self); \
    self = calloc(1, sizeof *self);

#define land_allocate malloc

#define land_free(self); \
    free(self);

#define land_new(type, self) \
    type *self; \
    if (!type##_count) type##_count = 1; \
    self = calloc(1, sizeof *self); \
    type##_array = realloc(type##_array, (type##_count + 1) * sizeof *type##_array); \
    type##_array[type##_count] = self; \
    type##_count++;

#define land_last_id(type) (type##_count - 1)

#define land_add(type, self) \
    if (!type##_count) type##_count = 1; \
    type##_array = realloc(type##_array, (type##_count + 1) * sizeof *type##_array); \
    type##_array[type##_count] = self; \
    type##_count++;

#define land_new_count(type, count) \
{ \
    if (type##_count == 0) \
        type##_count = 1; \
    int _i; \
    type##_array = realloc(type##_array, (type##_count + (count)) * sizeof *type##_array); \
    for (_i = 0; _i < (count); _i++) \
    { \
        type##_array[type##_count + _i] = calloc(1, sizeof(type)); \
    } \
    type##_count += (count); \
}

#define land_first(type) 1
#define land_last(type) (type##_count - 1)
#define land_array_size(type) type##_count

#define land_foreach(type, v) \
    for (v = 1; v < type##_count; v++)

#define land_pointer(type, i) \
    type##_array[i]

land_type(LandArray)
{
    int count;
    void **data;
};

#endif /* _PROTOTYPE_ */

#include "array.h"

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
    self->data = realloc(self->data, (self->count + 1) * sizeof *self->data);
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
    free(self->data);
    free(self);
}

void land_array_sort(LandArray *self, int (*cmpfnc)(void const *a, void const *b))
{
    qsort(self->data, self->count, sizeof(void *), cmpfnc);
}
