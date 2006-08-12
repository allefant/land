import ../image, ../display

static LandImageInterface *vtable

LandImage *def land_image_allegro_new(LandDisplay *display):
    LandImage *self
    land_alloc(self)
    self->vt = vtable
    return self

def land_image_allegro_del(LandDisplay *display, LandImage *self):
    land_free(self)

def land_image_allegro_draw_scaled_rotated_tinted(LandImage *self,
    float x, float y, float sx, float sy, float angle, float r, float g, float b, float alpha):
    #set_alpha_blender()
    #draw_trans_sprite(land_display_bitmap(), self->bitmap, x, y)
    if angle == 0:
        masked_stretch_blit(self->bitmap,
            LAND_DISPLAY_IMAGE(_land_active_display)->bitmap, 0, 0,
            self->bitmap->w, self->bitmap->h, x - self->x, y - self->y,
            self->bitmap->w * sx, self->bitmap->h * sy)

    else:
        pivot_sprite(LAND_DISPLAY_IMAGE(_land_active_display)->bitmap,
            self->bitmap, x, y, self->x, self->y, ftofix(angle * 128 / AL_PI))


def land_image_allegro_grab(LandImage *self, int x, int y):
    blit(LAND_DISPLAY_IMAGE(_land_active_display)->bitmap, self->bitmap,
        x, y, 0, 0, self->bitmap->w, self->bitmap->h)

def land_image_allegro_init():
    land_log_message("land_image_allegro_init\n")
    land_alloc(vtable)
    vtable->prepare = land_image_allegro_prepare
    vtable->draw_scaled_rotated_tinted = land_image_allegro_draw_scaled_rotated_tinted
    vtable->grab = land_image_allegro_grab

def land_image_allegro_exit():
    land_log_message("land_image_allegro_exit\n")
    land_free(vtable)

def land_image_allegro_prepare(LandImage *self):
    if bitmap_color_depth(self->bitmap) != bitmap_color_depth(screen):
        int w = land_image_width(self)
        int h = land_image_height(self)
        if self->bitmap != self->memory_cache: destroy_bitmap(self->bitmap)
        self->bitmap = create_bitmap_ex(bitmap_color_depth(screen), w, h)
        blit(self->memory_cache, self->bitmap, 0, 0, 0, 0, w, h)

