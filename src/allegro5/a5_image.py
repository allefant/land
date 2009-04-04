import land/image, land/display
static import global allegro5/allegro5, allegro5/a5_iio, allegro5/a5_opengl

static class LandImagePlatform:
    LandImage super
    ALLEGRO_BITMAP *a5

static macro SELF \
    LandImagePlatform *self = (void *)super;

static ALLEGRO_BITMAP *previous

LandImage *def platform_new_image():
    LandImagePlatform *self
    land_alloc(self)
    return (void *)self

def platform_del_image(LandImage *super):
    SELF
    if self->a5:
        al_destroy_bitmap(self->a5)
    land_free(self)

def platform_image_empty(LandImage *super):
    SELF
    if not self->a5:
        self->a5 = al_create_bitmap(super->width, super->height)
    ALLEGRO_STATE state
    al_store_state(&state, ALLEGRO_STATE_TARGET_BITMAP)
    al_set_target_bitmap(self->a5)
    al_clear(al_map_rgba_f(0, 0, 0, 0))
    al_restore_state(&state)

LandImage *def platform_image_load(char const *filename):
    LandImage *super = land_display_new_image()
    super->filename = land_strdup(filename)
    super->name = land_strdup(filename)
    ALLEGRO_BITMAP *bmp = al_iio_load(filename)
    if bmp:        
        LandImagePlatform *self = (void *)super
        self->a5 = bmp
        super->width = al_get_bitmap_width(bmp)
        super->height = al_get_bitmap_height(bmp)
        super->flags |= LAND_LOADED
    return super

def platform_image_save(LandImage *super, char const *filename):
    LandImagePlatform *self = (void *)super
    al_iio_save(filename, self->a5)

def platform_image_prepare(LandImage *super):
    pass

def platform_image_draw_scaled_rotated_tinted(LandImage *super, float x,
    float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha):
    SELF
    if r != 1 or g != 1 or b != 1 or alpha != 1:
        al_set_blender(ALLEGRO_ALPHA, ALLEGRO_INVERSE_ALPHA,
            al_map_rgba_f(r, g, b, alpha))
    if super->l or super->t or super->r or super->b:
        if angle != 0 or sx != 1 or sy != 1:
            ALLEGRO_BITMAP *sub = al_create_sub_bitmap(self->a5,
                super->l, super->t,
                super->width - super->l - super->r,
                super->height - super->t - super->b)
            float cx = super->x - super->l
            float cy = super->y - super->t
            al_draw_rotated_scaled_bitmap(sub, cx, cy,
                x, y, sx, sy, angle, 0)
            al_destroy_bitmap(sub)
        else:
            al_draw_bitmap_region(self->a5, super->l, super->t,
                super->width - super->l - super->r,
                super->height - super->t - super->b,
                x + super->l,
                y + super->t, 0)
    else:
        al_draw_rotated_scaled_bitmap(self->a5, super->x, super->y,
            x, y, sx, sy, angle, 0)

def platform_set_image_display(LandImage *super):
    SELF
    previous = al_get_target_bitmap()
    al_set_target_bitmap(self->a5)

def platform_unset_image_display():
    al_set_target_bitmap(previous)

def platform_image_grab_into(LandImage *super,
    float x, y, tx, ty, tw, th):
    SELF
    ALLEGRO_STATE state
    al_store_state(&state, ALLEGRO_STATE_TARGET_BITMAP)
    ALLEGRO_BITMAP *from = al_get_target_bitmap()
    al_set_target_bitmap(self->a5)
    al_draw_bitmap_region(from, x, y, tw, th, tx, ty, 0)
    al_restore_state(&state)

def platform_image_get_rgba_data(LandImage *super, unsigned char *rgba):
    SELF
    int w = super->width
    int h = super->height
    unsigned char *p = rgba
    ALLEGRO_LOCKED_REGION *lock
    lock = al_lock_bitmap(self->a5, ALLEGRO_PIXEL_FORMAT_ABGR_8888,
        ALLEGRO_LOCK_READONLY)
    unsigned char *p2 = lock->data
    for int y = 0; y < h; y++:
        unsigned char *p3 = p2
        for int x = 0; x < w; x++:
            unsigned char r, g, b, a
            r = *(p3++)
            g = *(p3++)
            b = *(p3++)
            a = *(p3++)
            *(p++) = r
            *(p++) = g
            *(p++) = b
            *(p++) = a
        p2 += lock->pitch
    al_unlock_bitmap(self->a5)

def platform_image_set_rgba_data(LandImage *super,
    unsigned char const *rgba):
    SELF
    int w = super->width
    int h = super->height
    unsigned char const *p = rgba
    ALLEGRO_LOCKED_REGION *lock
    lock = al_lock_bitmap(self->a5, ALLEGRO_PIXEL_FORMAT_ABGR_8888,
        ALLEGRO_LOCK_WRITEONLY)
    unsigned char *p2 = lock->data
    for int y = 0; y < h; y++:
        unsigned char *p3 = p2
        for int x = 0; x < w; x++:
            int r, g, b, a
            r = *(p++)
            g = *(p++)
            b = *(p++)
            a = *(p++)
            *(p3++) = r
            *(p3++) = g
            *(p3++) = b
            *(p3++) = a
        p2 += lock->pitch
    al_unlock_bitmap(self->a5)

int def platform_image_opengl_texture(LandImage *super):
    SELF
    return al_get_opengl_texture(self->a5)

def platform_image_crop(LandImage *super, int x, y, w, h):
    SELF
    ALLEGRO_STATE state
    al_store_state(&state, ALLEGRO_STATE_TARGET_BITMAP)
    ALLEGRO_BITMAP *cropped = al_create_bitmap(w, h)
    al_set_target_bitmap(cropped)
    if self->a5:
        al_draw_bitmap(self->a5, -x, -y, 0)
        al_destroy_bitmap(self->a5)
    self->a5 = cropped
    al_restore_state(&state)
