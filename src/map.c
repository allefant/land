#ifdef _PROTOTYPE_

#include "array.h"
#include "layer.h"

land_type(LandMap)
{
    LandLayer *first_layer;
};

#endif /* _PROTOTYPE_ */

#include "map.h"

land_array(LandMap);

void land_map_draw(LandMap *self, LandView *view)
{
    LandLayer *layer = self->first_layer;
    while (layer)
    {
        land_layer_draw(layer, view);
        layer = layer->next_in_map;
    }
}

void land_map_add_layer(LandMap *map, LandLayer *layer)
{
    if (map->first_layer)
    {
        LandLayer *l = map->first_layer;
        while(l->next_in_map)
            l = l->next_in_map;
        l->next_in_map = layer;
    }
    else
        map->first_layer = layer;
}

LandMap *land_map_new(void)
{
    land_new(LandMap, self);
    return self;
}
