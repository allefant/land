import global land/land

def string_cmp(void *s1, void *s2) -> int:
    return strcmp(s1, s2)

def print_cb(void *item, void *data) -> int:
    printf(" * %s\n", (char *)item)
    return 0

def _com:
    LandQueue *queue = land_queue_new(string_cmp)

    land_queue_add(queue, "Elephant")
    land_queue_add(queue, "Crocodile")
    land_queue_add(queue, "Camel")
    land_queue_add(queue, "Zebra")
    land_queue_add(queue, "Hippopotamus")
    land_queue_add(queue, "Rhinocerus")
    land_queue_add(queue, "Giraffe")

    printf("Heap contents:\n")
    land_queue_for_each(queue, print_cb, None)

    LandArray *array = land_queue_sort(queue)
    printf("As sorted array:\n")
    land_array_for_each(array, print_cb, None)

    land_array_destroy(array)

land_commandline_example()
