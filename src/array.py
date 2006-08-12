import global stdlib
class LandArray:
    int count
    void **data

static import array, memory

LandArray *def land_array_new():
    LandArray *self
    land_alloc(self)
    return self

# Given a pointer to a (possibly NULL valued) array pointer, create a new node
# with the given data, and add to the (possibly modified) array.
# 
def land_array_add_data(LandArray **array, void *data):
    LandArray *self = *array
    if !self:
        self = land_array_new()

    self->data = land_realloc(self->data, (self->count + 1) * sizeof *self->data)
    self->data[self->count] = data
    self->count++
    *array = self

void *def land_array_get_nth(LandArray *array, int i):
    return array->data[i]

def land_array_destroy(LandArray *self):
    land_free(self->data)
    land_free(self)

def land_array_sort(LandArray *self, int (*cmpfnc)(void const *a, void const *b)):
    qsort(self->data, self->count, sizeof(void *), cmpfnc)
