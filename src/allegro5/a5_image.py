import land.image, land.display
static import global allegro5.allegro5, allegro5.allegro_image, allegro5.allegro_opengl
static import land.allegro5.a5_display

class LandImagePlatform:
    LandImage super
    ALLEGRO_BITMAP *a5
    ALLEGRO_BITMAP *memory

static LandDisplay *global_previous_display
static LandDisplayPlatform global_image_display
static ALLEGRO_BITMAP *previous

static macro SELF:
    LandImagePlatform *self = (void *)super

def platform_new_image() -> LandImage *:
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
        ALLEGRO_STATE state
        if super.flags & LAND_IMAGE_MEMORY:
            al_store_state(&state, ALLEGRO_STATE_NEW_BITMAP_PARAMETERS)
            al_set_new_bitmap_flags(ALLEGRO_MEMORY_BITMAP)
        if super.flags & LAND_IMAGE_DEPTH:
            al_set_new_bitmap_depth(16)
        if super.flags & LAND_IMAGE_DEPTH32:
            al_set_new_bitmap_depth(16)
        self->a5 = al_create_bitmap(super->width, super->height)
        if super.flags & LAND_IMAGE_DEPTH:
            al_set_new_bitmap_depth(0)
        if super.flags & LAND_IMAGE_DEPTH32:
            al_set_new_bitmap_depth(0)
        if super.flags & LAND_IMAGE_MEMORY:
            al_restore_state(&state)
    int f = al_get_bitmap_format(self->a5)
    ALLEGRO_LOCKED_REGION *lock = al_lock_bitmap(self->a5, f, ALLEGRO_LOCK_WRITEONLY)
    int rowbytes = al_get_pixel_size(f) * super->width
    for int i = 0 while i < super->height with i++:
        memset(lock->data + lock->pitch * i, 0, rowbytes)
    al_unlock_bitmap(self->a5)

def platform_image_load(char const *filename, bool mem) -> LandImage *:
    LandImage *super = land_display_new_image()
    super->filename = land_strdup(filename)
    if mem:
        super.flags |= LAND_IMAGE_MEMORY
    _platform_load(super)
    return super

def _platform_load(LandImage *super):
    super->name = land_strdup(super.filename)
    ALLEGRO_STATE state
    if super.flags & LAND_IMAGE_MEMORY:
        al_store_state(&state, ALLEGRO_STATE_NEW_BITMAP_PARAMETERS)
        al_set_new_bitmap_flags(ALLEGRO_MEMORY_BITMAP)
    *** "ifdef" ANDROID
    # FIXME: need to determine if we want APK or normal paths,
    # right now apk file interface is always active
    land_log_message("open %s", super.filename)
    *** "endif"
    int flags = 0
    if super.flags & LAND_NO_PREMUL:
        flags |= ALLEGRO_NO_PREMULTIPLIED_ALPHA
    ALLEGRO_BITMAP *bmp = al_load_bitmap_flags(super.filename, flags)
    if bmp:
        LandImagePlatform *self = (void *)super
        if super.flags & LAND_LOADING:
            self->memory = bmp
        else:
            self->a5 = bmp
        super->width = al_get_bitmap_width(bmp)
        super->height = al_get_bitmap_height(bmp)
        super->flags |= LAND_LOADED
    else:
        super->flags |= LAND_FAILED
    if super.flags & LAND_IMAGE_MEMORY:
        al_restore_state(&state)

def platform_image_preload_memory(LandImage* super):
    super.flags |= LAND_IMAGE_MEMORY
    _platform_load(super)
    super.flags &= ~LAND_IMAGE_MEMORY

def platform_image_exists(LandImage *super) -> bool:
    return al_filename_exists(super.filename)

def platform_image_load_on_demand(LandImage *super):
    LandImagePlatform *self = (void *)super
    if self.a5:
        return
    _platform_load(super)

def platform_image_sub(LandImage *parent, float x, y, w, h) -> LandImage *:
    LandImage *super = land_display_new_image()
    super.flags |= LAND_SUBIMAGE
    super.flags |= parent.flags & LAND_LOADED
    super.filename = parent->filename
    super.name = parent->name

    LandImagePlatform *self = (void *)super
    LandImagePlatform *parentself = (void *)parent

    self->a5 = al_create_sub_bitmap(parentself->a5, x, y, w, h)
    super->width = al_get_bitmap_width(self->a5)
    super->height = al_get_bitmap_height(self->a5)
    return super

def platform_image_save(LandImage *super, char const *filename):
    LandImagePlatform *self = (void *)super
    al_save_bitmap(filename, self->a5)
    land_log_message("Saved %dx%d bitmap to %s\n", super.width,
        super.height, filename)

def platform_image_draw_scaled_rotated_tinted_flipped(LandImage *super, float x,
    float y, float sx, float sy,
    float angle, float r, float g, float b, float alpha, int flip):
    SELF
    LandDisplay *d = _land_active_display
    ALLEGRO_STATE state

    if d.debug_frame:
        printf("image %s %dx%d %.1f/%.1f",
            super.filename if super.filename else super.name,
            super.width, super.height,
            x, y)
        if sx != 1 or sy != 1: printf(" (scale %.1fx%.1f)", sx, sy)
        if angle != 0: printf(" (rotate %.1f)", angle)
        if r != 1 or g != 1 or b != 1 or alpha != 1:
            printf(" (tint %.1f/%.1f/%.1f/%.1f)", r, g, b, alpha)

    if super.flags & LAND_LOADING:
        if d.debug_frame:
            print(" LOADING")
        return

    if super.flags & LAND_LOADING_COMPLETE:
        # attempt to draw an image that has completed loading asynchronously
        # - we may as well transfer it here during drawing
        if d.debug_frame:
            printf(" LOADING_COMPLETE")
        land_image_load_async(super)

    if not self->a5:
        if d.debug_frame:
            print("MISSING")
        return

    land_a5_display_check_transform()

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

    int flags = 0
    if flip == 1 or flip == 3: flags |= ALLEGRO_FLIP_HORIZONTAL
    if flip == 2 or flip == 3: flags |= ALLEGRO_FLIP_VERTICAL

    ALLEGRO_COLOR tint = al_map_rgba_f(r, g, b, alpha)

    al_draw_tinted_scaled_rotated_bitmap_region(self->a5,
        super->l, super->t,
        super->width - super->l - super->r,
        super->height - super->t - super->b,
        tint, super->x - super->l, super->y - super->t,
        x, y, sx, sy, -angle, flags)

    if restore:
        al_restore_state(&state)

    if d.debug_frame:
        float dx = x - (super.x - super.l)
        float dy = y - (super.y - super.t)
        float dw = super->width - super->l - super->r
        float dh = super->height - super->t - super->b
        if land_is_clipped_away(dx, dy, dx + dw, dy + dh):
            print(" clipped")
        else:
            print(" drawn (%.1f/%.1f/%.1f/%.1f)", dx, dy, dw, dh)

def platform_set_image_display(LandImage *super):
    SELF
    global_previous_display = _land_active_display
    LandDisplayPlatform *prev = (void *)global_previous_display
    LandDisplay *d = (void *)&global_image_display
    _land_active_display = d

    if prev:
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
    ALLEGRO_BITMAP* a5 = self->a5
    if self->memory:
        a5 = self->memory
    unsigned char *p = rgba
    ALLEGRO_LOCKED_REGION *lock
    lock = al_lock_bitmap(a5, ALLEGRO_PIXEL_FORMAT_ABGR_8888_LE,
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
    al_unlock_bitmap(a5)

def platform_image_set_rgba_data(LandImage *super,
    unsigned char const *rgba):
    SELF
    int w = super->width
    int h = super->height
    unsigned char const *p = rgba
    ALLEGRO_LOCKED_REGION *lock
    lock = al_lock_bitmap(self->a5, ALLEGRO_PIXEL_FORMAT_ABGR_8888_LE,
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

def platform_image_opengl_texture(LandImage *super) -> int:
    SELF
    return al_get_opengl_texture(self->a5)

def platform_image_crop(LandImage *super, int x, y, w, h):
    SELF
    ALLEGRO_STATE state
    if x == 0 and y == 0 and w == super.width and h == super.height:
        return
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    if x + w > super.width:
        w = super.width - x
    if y + h > super.height:
        h = super.height - y
    al_store_state(&state, ALLEGRO_STATE_TARGET_BITMAP |
        ALLEGRO_STATE_BLENDER)
    ALLEGRO_BITMAP *cropped = al_create_bitmap(w, h)
    #al_set_target_bitmap(cropped)
    #al_set_blender(ALLEGRO_ADD, ALLEGRO_ONE, ALLEGRO_ZERO);
    if self->a5:
        # FIXME: this fails with GL ES
        #al_draw_bitmap(self->a5, -x, -y, 0)

        ALLEGRO_LOCKED_REGION *rfrom = al_lock_bitmap_region(self->a5, x, y, w, h,
            ALLEGRO_PIXEL_FORMAT_ABGR_8888_LE, ALLEGRO_LOCK_READONLY)
        ALLEGRO_LOCKED_REGION *rto = al_lock_bitmap(cropped, ALLEGRO_PIXEL_FORMAT_ABGR_8888_LE,
            ALLEGRO_LOCK_WRITEONLY)

        for int i in range(h):
            uint8_t *pfrom = rfrom.data, *pto = rto.data
            pfrom += rfrom.pitch * i
            pto += rto.pitch * i
            memcpy(pto, pfrom, 4 * w)

        al_unlock_bitmap(self->a5)
        al_unlock_bitmap(cropped)

        al_destroy_bitmap(self->a5)
    self->a5 = cropped
    al_restore_state(&state)
    super.width = w
    super.height = h

def platform_image_merge(LandImage *super, LandImage *replacement_image):
    SELF
    LandImagePlatform *replacement = (void*)replacement_image
    al_destroy_bitmap(self->a5)
    self->a5 = replacement.a5
    replacement.a5 = None
    super.width = replacement_image.width
    super.height = replacement_image.height
    super.l = 0
    super.t = 0
    super.r = 0
    super.b = 0
    land_image_destroy(replacement_image)

def platform_image_transfer_from_memory(LandImage* super):
    SELF
    if not self->memory:
        return
    self->a5 = al_clone_bitmap(self->memory)
    land_log_message("platform_image_transfer %s: %s -> %s\n",
        super.name,
        "mem" if al_get_bitmap_flags(self->memory) & ALLEGRO_MEMORY_BITMAP else "vid",
        "mem" if al_get_bitmap_flags(self->a5) & ALLEGRO_MEMORY_BITMAP else "vid")
    al_destroy_bitmap(self->memory)
    self->memory = None
