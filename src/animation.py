import array, image

class LandAnimation:
    LandArray *frames

static import animation, memory

LandAnimation *def land_animation_new(LandArray *frames):
    LandAnimation *self
    land_alloc(self)
    self->frames = frames
    return self

def land_animation_destroy(LandAnimation *self):
    int i
    if self->frames:
        for i = 0; i < self->frames->count; i++:
            land_image_destroy(land_array_get_nth(self->frames, i))

        land_array_destroy(self->frames)

    land_free(self)

LandImage *def land_animation_get_frame(LandAnimation *self, int i):
    return land_array_get_nth(self->frames, i)
