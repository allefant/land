import global land/land

int def string_cmp(void *s1, void *s2):
    return strcmp(s1, s2)

int def print_cb(void *item, void *data):
    printf(" * %s\n", item)
    return 0

int def main():
    land_init()
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
    return 0
