import land.image, land.display
static import global allegro5.allegro5, allegro5.allegro_image, allegro5.allegro_opengl
static import land.allegro5.a5_display

static class LandImagePlatform:
    LandImage super
    ALLEGRO_BITMAP *a5

static LandDisplay *global_previous_display
static LandDisplayPlatform global_image_display
static ALLEGRO_BITMAP *previous

static macro SELF \
    LandImagePlatform *self = (void *)super;

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
    int f = al_get_bitmap_format(self->a5)
    ALLEGRO_LOCKED_REGION *lock = al_lock_bitmap(self->a5, f, ALLEGRO_LOCK_WRITEONLY)
    int rowbytes = al_get_pixel_size(f) * super->width
    for int i = 0 while i < super->height with i++:
        memset(lock->data + lock->pitch * i, 0, rowbytes)
    al_unlock_bitmap(self->a5)
    

LandImage *def platform_image_load(char const *filename, bool mem):
    LandImage *super = land_display_new_image()
    super->filename = land_strdup(filename)
    super->name = land_strdup(filename)
    ALLEGRO_STATE state
    if mem:
        al_store_state(&state, ALLEGRO_STATE_NEW_BITMAP_PARAMETERS)
        al_set_new_bitmap_flags(ALLEGRO_MEMORY_BITMAP)
    ALLEGRO_BITMAP *bmp
    if strchr(filename, '.'):
        bmp = al_load_bitmap(filename)
    else:
        bmp = al_load_bitmap(filename)
    if bmp:        
        LandImagePlatform *self = (void *)super
        self->a5 = bmp
        super->width = al_get_bitmap_width(bmp)
        super->height = al_get_bitmap_height(bmp)
        super->flags |= LAND_LOADED
    if mem:
        al_restore_state(&state)
    return super

LandImage *def platform_image_sub(LandImage *parent, float x, y, w, h):
    LandImage *super = land_display_new_image()
    super->flags |= LAND_SUBIMAGE
    super->filename = parent->filename
    super->name = parent->name

    LandImagePlatform *self = (void *)super
    LandImagePlatform *parentself = (void *)parent

    self->a5 = al_create_sub_bitmap(parentself->a5, x, y, w, h)
    super->width = al_get_bitmap_width(self->a5)
    super->height = al_get_bitmap_height(self->a5)
    return super

def platform_image_save(LandImage *super, char const *filename):
    LandImagePlatform *self = (void *)super
    al_save_bitmap(filename, self->a5)

def platform_image_prepare(LandImage *super):
    LandImagePlatform *self = (void *)super
    land_log_message("platform_image_prepare\n")
    al_remove_opengl_fbo(self->a5)

def platform_image_draw_scaled_rotated_tinted_flipped(LandImage *super, float x,
    float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha, int flip):
    SELF
    LandDisplay *d = _land_active_display
    ALLEGRO_STATE state
    bool restore = False
    if d->blend:
        if d->blend & LAND_BLEND_SOLID:
            al_store_state(&state, ALLEGRO_STATE_BLENDER)
            al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_ZERO)
            restore = True
        if d->blend & LAND_BLEND_ADD:
            al_store_state(&state, ALLEGRO_STATE_BLENDER)
            al_set_blender(ALLEGRO_ADD, ALLEGRO_ALPHA, ALLEGRO_ONE)
            restore = True
    elif r != 1 or g != 1 or b != 1 or alpha != 1:
        al_store_state(&state, ALLEGRO_STATE_BLENDER)
        al_set_blender(ALLEGRO_ADD, ALLEGRO_ALPHA, ALLEGRO_INVERSE_ALPHA)
        restore = True

    int flags = 0
    if flip == 1 or flags == 3: flags |= ALLEGRO_FLIP_HORIZONTAL
    if flip == 2 or flags == 3: flags |= ALLEGRO_FLIP_VERTICAL
    
    ALLEGRO_COLOR tint = al_map_rgba_f(r, g, b, alpha)

    if super->l or super->t or super->r or super->b:
        if angle != 0 or sx != 1 or sy != 1:
            ALLEGRO_BITMAP *sub = al_create_sub_bitmap(self->a5,
                super->l, super->t,
                super->width - super->l - super->r,
                super->height - super->t - super->b)
            float cx = super->x - super->l
            float cy = super->y - super->t
            al_draw_tinted_scaled_rotated_bitmap(sub, tint, cx, cy,
                x, y, sx, sy, -angle, flags)
            al_destroy_bitmap(sub)
        else:
            al_draw_tinted_bitmap_region(self->a5, tint,
                super->l, super->t,
                super->width - super->l - super->r,
                super->height - super->t - super->b,
                x + super->l,
                y + super->t, flags)
    else:
        al_draw_tinted_scaled_rotated_bitmap(self->a5, tint,
            super->x, super->y,
            x, y, sx, sy, -angle, flags)

    if restore:
        al_restore_state(&state)

def platform_set_image_display(LandImage *super):
    SELF
    global_previous_display = _land_active_display
    LandDisplayPlatform *prev = (void *)global_previous_display
    LandDisplay *d = (void *)&global_image_display
    _land_active_display = d

    global_image_display.a5 = prev->a5
    global_image_display.c = al_map_rgb_f(1, 1, 1)
    d->w = super->width
    d->h = super->height
    d->flags = 0
    d->color_r = 1
    d->color_g = 1
    d->color_b = 1
    d->color_a = 1
    d->blend = 0
    d->clip_off = False
    d->clip_x1 = 0
    d->clip_y1 = 0
    d->clip_x2 = super->width
    d->clip_y2 = super->height
    
    previous = al_get_target_bitmap()
    al_set_target_bitmap(self->a5)
    

def platform_unset_image_display():
    _land_active_display = global_previous_display
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
    for int y = 0 while y < h with y++:
        unsigned char *p3 = p2
        for int x = 0 while x < w with x++:
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
    for int y = 0 while y < h with y++:
        unsigned char *p3 = p2
        for int x = 0 while x < w with x++:
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
