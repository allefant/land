#ifdef _PROTOTYPE_

#include "array.h"
#include "image.h"

typedef struct LandAnimation LandAnimation;
struct LandAnimation
{
    LandArray *frames;
};

#endif /* _PROTOTYPE_ */

#include "animation.h"

LandAnimation *land_animation_new(LandArray *frames)
{
    LandAnimation *self;
    land_alloc(self);
    self->frames = frames;
    return self;
}

LandImage *land_animation_get_frame(LandAnimation *self, int i)
{
    return land_array_get_nth(self->frames, i);
}
