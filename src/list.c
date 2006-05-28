#ifdef _PROTOTYPE_

#include "array.h"

typedef struct LandListItem LandListItem;
struct LandListItem
{
    void *data;
    LandListItem *next, *prev;
};

typedef struct LandList LandList;
struct LandList
{
    int count;
    LandListItem *first, *last;
};

 LandList *land_list_new(void);
 void land_list_destroy(LandList *self);
 void land_add_list_data(LandList **list, void *data);

#ifdef LAND_MEMLOG

#define land_list_new() land_list_new_memlog(__FILE__, __LINE__)
#define land_list_destroy(x) land_list_destroy_memlog(x, __FILE__, __LINE__)
#define land_add_list_data(x, y) land_add_list_data_memlog(x, y, __FILE__, __LINE__)
 
#endif

#endif /* _PROTOTYPE_ */

#include "list.h"
#include "memory.h"

/* Inserts a new item to the end of the list. */
void land_list_insert_item(LandList *list, LandListItem *item)
{
    item->next = NULL;
    item->prev = list->last;
    if (list->last)
    {
        list->last->next = item;
    }
    else
    {
        list->first = item;
    }
    list->last = item;
    list->count++;
}

/* Inserts a new item to the list, positioned before the given one. */
void land_list_insert_item_before(LandList *list, LandListItem *insert,
    LandListItem *before)
{
    if (before)
    {
        insert->next = before;
        insert->prev = before->prev;

        if (before->prev)
        {
            before->prev->next = insert;
        }
        else
        {
            list->first = insert;
        }

        before->prev = insert;

        list->count++;
    }
    else
        land_list_insert_item(list, insert);
}

/* May only be called with an item which is in the list. */
void land_list_remove_item(LandList *list, LandListItem *item)
{
    if (item->prev)
    {
        item->prev->next = item->next;
    }
    else
    {
        list->first = item->next;
    }
    if (item->next)
    {
        item->next->prev = item->prev;
    }
    else
    {
        list->last = item->prev;
    }
    list->count--;
}

#ifdef LAND_MEMLOG

#undef land_list_new
#undef land_list_destroy
#undef land_add_list_data

LandList *land_list_new_memlog(char const *f, int l)
{
    LandList *list = land_list_new();
    land_memory_add(list, "list", 1, f, l);
    return list;
}

void land_list_destroy_memlog(LandList *self, char const *f, int l)
{
    land_list_destroy(self);
    land_memory_remove(self, 1, f, l);
}

void land_add_list_data_memlog(LandList **list, void *data, char const *f, int l)
{
    land_memory_remove(*list, 1, f, l);
    land_add_list_data(list, data);
    land_memory_add(*list, "list", 1, f, l);
}

#endif

 LandList *land_list_new(void)
{
    LandList *self;
    land_alloc(self);
    return self;
}

/* Destroys a list and all iterators, but not the data. If you want to destroy
 * the data, first loop through the list and destroy them all.
 */
 void land_list_destroy(LandList *list)
{
    LandListItem *item = list->first;
    while (item)
    {
        LandListItem *next = item->next;
        land_free(item);
        item = next;
    }
    land_free(list);
}


/* Given a pointer to a (possibly NULL valued) list pointer, create a new node
 * with the given data, and add to the (possibly newly created) list.
 */
 void land_add_list_data(LandList **list, void *data)
{
    LandListItem *item;
    land_alloc(item);
    item->data = data;
    if (!*list)
    {
        *list = land_list_new();
    }
    land_list_insert_item(*list, item);
}

/* Don't use, it will loop through the whole list every time, removing the
 * first item with the given data.
 * But normal use of lists is with iterators (LandListItem).
 */
void land_remove_list_data(LandList **list, void *data)
{
    LandListItem *item = (*list)->first;
    while (item)
    {
        LandListItem *next = item->next;
        if (item->data == data)
        {
            land_list_remove_item(*list, item);
            land_free(item);
            return;
        }
        item = next;
    }
}
