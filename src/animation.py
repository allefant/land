import array, image

class LandAnimation:
    float fps
    LandArray *frames

static import animation, mem

LandAnimation *def land_animation_new(LandArray *frames):
    LandAnimation *self
    land_alloc(self)
    self->fps = 10
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

LandAnimation *def land_animation_load_cb(char const *pattern,
    void (*cb)(LandImage *image, void *data), void *data):
    """
    Create a new animation from all files matching the pattern, sorted
    alphabetically. The callback function, if present, is called on each
    frame.
    """
    LandArray *pics = land_load_images_cb(pattern, cb, data)
    if not pics: return None
    return land_animation_new(pics)

def land_animation_draw_frame(LandAnimation *self, int i,
    float x, y):
    LandImage *frame = land_animation_get_frame(self, i)
    land_image_draw(frame, x, y)

def land_animation_draw_frame_rotated(LandAnimation *self, int i,
    float x, y, angle):
    LandImage *frame = land_animation_get_frame(self, i)
    land_image_draw_rotated(frame, x, y, angle)

def land_animation_draw_frame_scaled_rotated(LandAnimation *self, int i,
    float x, y, xs, ys, angle):
    LandImage *frame = land_animation_get_frame(self, i)
    land_image_draw_scaled_rotated(frame, x, y, xs, ys, angle)