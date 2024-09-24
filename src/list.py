import array

class LandListItem:
    void *data
    LandListItem *next, *prev

class LandList:
    int count
    LandListItem *first, *last

class LandListIterator:
    LandListItem *i

static import mem

*** "ifdef" LAND_MEMLOG

*** "undef" land_list_new
*** "undef" land_list_destroy
*** "undef" land_add_list_data

def land_list_new_memlog(char const *f, int l) -> LandList *:
    LandList *list = land_list_new()
    land_memory_add(list, "list", 1, f, l)
    return list

def land_list_destroy_memlog(LandList *self, char const *f, int l):
    land_memory_remove(self, "list", 1, f, l)
    land_list_destroy(self)

def land_add_list_data_memlog(LandList **list, void *data, char const *f, int l):
    if *list:
        land_memory_remove(*list, "list", 1, f, l)
        land_add_list_data(list, data)
        land_memory_add(*list, "list", 1, f, l)

    else:
        *list = land_list_new_memlog(f, l)
        land_add_list_data(list, data)

*** "endif"

def LandListIterator_first(LandList *a) -> LandListIterator:
    LandListIterator i = {a->first}
    return i

def LandListIterator_item(LandList *a, LandListIterator *i) -> void *:
    return i->i ? i->i->data : None

def LandListIterator_next(LandList *a, LandListIterator *i) -> bool:
    if i->i:
        i->i = i->i->next
        return True
    return False

def land_list_new() -> LandList *:
    LandList *self
    land_alloc(self)
    return self

def land_list_clear(LandList *list):
    LandListItem *item = list->first
    while item:
        LandListItem *next = item->next
        land_listitem_destroy(item)
        item = next
    list->first = None
    list->last = None
    list->count = 0

# Destroys a list and all iterators, but not the data. If you want to destroy
# the data, first loop through the list and destroy them all.
# 
def land_list_destroy(LandList *list):
    land_list_clear(list)
    land_free(list)

def land_listitem_new(void *data) -> LandListItem *:
    LandListItem *self
    land_alloc(self)
    self.data = data
    return self

def land_listitem_destroy(LandListItem *self):
    land_free(self)

# Inserts a new item to the end of the list. 
def land_list_insert_item(LandList *list, LandListItem *item):
    item->next = NULL
    item->prev = list->last
    if list->last:
        list->last->next = item

    else:
        list->first = item

    list->last = item
    list->count++

# Inserts a new item to the list, positioned before the given one. 
def land_list_insert_item_before(LandList *list, LandListItem *insert,
    LandListItem *before):
    if before:
        insert->next = before
        insert->prev = before->prev

        if before->prev:
            before->prev->next = insert

        else:
            list->first = insert

        before->prev = insert

        list->count++

    else:
        land_list_insert_item(list, insert)

# May only be called with an item which is in the list. 
def land_list_remove_item(LandList *list, LandListItem *item):
    if item->prev:
        item->prev->next = item->next
    else:
        list->first = item->next

    if item->next:
        item->next->prev = item->prev
    else:
        list->last = item->prev

    list->count--

def land_list_replace_item(LandList *list, LandListItem *item, *replace):
    land_list_insert_item_before(list, item, replace)
    land_list_remove_item(list, item)

# Returns None if the list is empty. Also returns None if the data value
# of the first list tiem is None.
def land_list_pop_first(LandList *self) -> void *:
    LandListItem *first = self.first
    if not first: return None
    void *data = first.data
    land_list_remove_item(self, first)
    land_listitem_destroy(first)
    return data

def land_list_pop_last(LandList *self) -> void *:
    LandListItem *last = self.last
    if not last: return None
    void *data = last.data
    land_list_remove_item(self, last)
    land_listitem_destroy(last)
    return data

# Given a pointer to a (possibly NULL valued) list pointer, create a new node
# with the given data, and add to the (possibly newly created) list.
# 
def land_add_list_data(LandList **list, void *data):
    LandListItem *item = land_listitem_new(data)
    if not *list:
        *list = land_list_new()

    land_list_insert_item(*list, item)

# Don't use, it will loop through the whole list every time, removing the
# first item with the given data.
# But normal use of lists is with iterators (LandListItem).
# 
def land_remove_list_data(LandList **list, void *data):
    LandListItem *item = (*list)->first
    while item:
        LandListItem *next = item->next
        if item->data == data:
            land_list_remove_item(*list, item)
            land_listitem_destroy(item)
            return

        item = next

def land_list_add(LandList *l, void *data):
    auto item = land_listitem_new(data)
    land_list_insert_item(l, item)

#def land_list_remove(LandList *l, int i)

global *** "ifdef" LAND_MEMLOG

macro land_list_new() land_list_new_memlog(__FILE__, __LINE__)
macro land_list_destroy(x) land_list_destroy_memlog(x, __FILE__, __LINE__)
macro land_add_list_data(x, y) land_add_list_data_memlog(x, y, __FILE__, __LINE__)

global *** "endif"
