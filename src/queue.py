import array

class LandQueue:
    """
    A queue data structure is used if the elements need to be kept sorted. It
    allows to quickly pick the minimum element. If you need arbitrary access
    to the elements, use a LandArray instead. If you need arbitrary removal and
    insertion, use a LandList. If you need arbitrary access by something besides
    the index, use a LandHash. If you need multiple properties at once, e.g.
    arbitrary string lookup as well as sorting, your best bet might be to use
    two structures at once (or use your own structure).
    """
    LandArray array
    int (*cmp_cb)(void *data1, void *data2)

static import mem

def land_queue_new(int (*cmp_cb)(void *data1, void *data2)) -> LandQueue *:
    """
    Create a new queue, with the given comparison function for its elements.
    """
    LandQueue *self
    land_alloc(self)
    self.array.data = None
    self.cmp_cb = cmp_cb
    return self

def land_queue_del(LandQueue *q):
    """
    Delete the queue. This will not touch the elements that might have been
    added since its creation.
    """
    land_free(q->array.data)
    land_free(q)

def land_queue_destroy(LandQueue *q):
    land_queue_del(q)

def land_queue_add(LandQueue *q, void *data):
    """
    Add an element to the queue.
    """
    int i = q->array.count

    land_array_add(&q->array, data)

    while i > 0:
        int parent = (i - 1) / 2
        # Parent is smaller (or equal), then everything is ok.
        if q->cmp_cb(q->array.data[parent], q->array.data[i]) <= 0: break
        # We are smaller, so we need to bubble up.
        void *temp = q->array.data[parent]
        q->array.data[parent] = q->array.data[i]
        q->array.data[i] = temp
        i = parent

def land_queue_pop(LandQueue *q) -> void *:
    """
    Return and remove the smallest element in the queue.
    """
    if q->array.count == 0: return None
    # The first element is the one we want.
    void *data = q->array.data[0]
    # Place the last element over the first.
    q->array.data[0] = q->array.data[q->array.count - 1]
    # Remove the last element from the array.
    land_array_pop(&q->array)

    int i = 0
    while 1:
        int child1 = i * 2 + 1
        int child2 = i * 2 + 2
        # Both childs are bigger, then everything is ok.
        if (child1 >= q->array.count or
            q->cmp_cb(q->array.data[child1], q->array.data[i]) >= 0)\
            and\
            (child2 >= q->array.count or
            q->cmp_cb(q->array.data[child2], q->array.data[i]) >= 0):
            break
        # Else bubble up the smaller child.
        if child2 >= q->array.count or (child1 < q->array.count and
            q->cmp_cb(q->array.data[child1], q->array.data[child2]) < 0):
            void *temp = q->array.data[i]
            q->array.data[i] = q->array.data[child1]
            q->array.data[child1] = temp
            i = child1
        else:
            void *temp = q->array.data[i]
            q->array.data[i] = q->array.data[child2]
            q->array.data[child2] = temp
            i = child2
            
    return data

def land_queue_sort(LandQueue *q) -> LandArray *:
    """
    Return an array referencing the same data as the queue. The array will be
    sorted from smallest to largest element. The queue will be destroyed in
    the process. So you should set the parameter you passed to this function to
    None after it returns.
    """
    LandArray *a = land_array_new()
    while 1:
        void *data = land_queue_pop(q)
        if not data: break
        land_array_add(a, data)
    land_queue_del(q)
    return a

def land_queue_for_each(LandQueue *self, int (*cb)(void *item, void *data),
    void *data) -> int:
    """
    Like land_array_for_each. The callback will not be called in any particular
    order, especially it will *not* be sorted. (The first call will be the
    smallest element, but the subsequent order is random.)
    """
    return land_array_for_each(&self.array, cb, data)

def land_queue_count(LandQueue *self) -> int:
    return self.array.count

def land_queue_clear(LandQueue *self):
    land_array_clear(&self.array)

def land_queue_is_empty(LandQueue *self) -> bool:
    return land_array_is_empty(&self.array)
