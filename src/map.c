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
    land_layer_draw(self->first_layer, view);
}

void land_map_add_layer(LandMap *map, LandLayer *layer)
{
    map->first_layer = layer;
}

LandMap *land_map_new(void)
{
    land_new(LandMap, self);
    return self;
}
