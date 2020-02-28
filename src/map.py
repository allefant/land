import array, layer

class LandMap:
    """
    A tilemap.
    """
    LandLayer *first_layer
    
    # This is a bit game specific - it's never used by Land itself.
    LandLayer *main_layer

def land_map_draw(LandMap *self, LandView *view):
    """
    Render the map using the given ''view''.
    """
    LandLayer *layer = self.first_layer
    while layer:
        land_layer_draw(layer, view)
        layer = layer->next_in_map

def land_map_add_layer(LandMap *map, LandLayer *layer):
    """
    Add another layer to the map, on top of any existing layers.
    """
    if map->first_layer:
        LandLayer *l = map->first_layer
        while l->next_in_map: l = l->next_in_map
        l->next_in_map = layer
    else:
        map->first_layer = layer

def land_map_base_layer(LandMap *map) -> LandLayer *:
    """
    Returns the base layer of the map.
    """
    return map->first_layer

def land_map_find_layer(LandMap *map, char const *name) -> LandLayer *:
    for LandLayer *l = map->first_layer while l with l = l->next_in_map:
        if not strcmp(name, l->name): return l
    return None

def land_map_new() -> LandMap *:
    """
    Create a new map. This is not called directly normally, as you likely want
    to use one of the convenience functions to already create layers of the
    right type along with it.
    """
    LandMap *self
    land_alloc(self)
    return self

def land_map_del(LandMap *self):
    """
    Destroy a map. This also destroys its layers.
    """
    if self.first_layer:
        LandLayer *l = self.first_layer
        while l:
            LandLayer *next = l->next_in_map
            land_layer_del(l)
            l = next

    land_free(self)

def land_map_destroy(LandMap *self):
    """
    Same as land_map_del.
    """
    land_map_del(self)
