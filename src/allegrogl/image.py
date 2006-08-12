import ../image, ../display
static import global alleggl
static import allegrogl/image, memory, log

static LandImageInterface *vtable
static LandList *images

macro LAND_IMAGE_OPENGL(_x_) ((LandImageOpenGL *)_x_)

class LandImageOpenGL:
    LandImage super

    unsigned int gl_texture

static def pad_pot(int w, int h, int *pad_w, int *pad_h):
    # Pad to power of 2 for some older OpenGL drivers. Should actually
    #   query OpenGL if it is necessary..
    *pad_w = 1
    while *pad_w < w:
        *pad_w *= 2

    *pad_w -= w

    *pad_h = 1
    while *pad_h < h:
        *pad_h *= 2

    *pad_h -= h

def land_image_allegrogl_reupload(void):
    if not images: return
    int size = 0
    LandListItem *i
    land_log_message("Re-uploading all textures..\n")
    for i = images->first; i; i = i->next:
        LandImageOpenGL *image = i->data
        image->gl_texture = 0

    for i = images->first; i; i = i->next:
        LandImage *image = i->data
        land_image_allegrogl_prepare(image)
        size += image->memory_cache->w * image->memory_cache->h * 4

    land_log_message(" %.1f MB of texture data uploaded.\n", size / 1048576.0)

LandImage *def land_image_allegrogl_new(LandDisplay *super):
    LandImageOpenGL *self
    land_alloc(self)
    self->super.vt = vtable
    land_add_list_data(&images, self)
    return &self->super

def land_image_allegrogl_sub(LandImage *self, LandImage *parent):
    LAND_IMAGE_OPENGL(self)->gl_texture = LAND_IMAGE_OPENGL(parent)->gl_texture

def land_image_allegrogl_del(LandDisplay *super, LandImage *self):
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self)
    if (sub->gl_texture && !(self->flags & LAND_SUBIMAGE)):
        glDeleteTextures(1, &sub->gl_texture)

    land_remove_list_data(&images, self)
    land_free(self)

static def quad(LandImage *self):
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, sub->gl_texture)

    GLfloat w, h
    GLint i
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &i)
    w = i
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &i)
    h = i

    GLfloat l = 0
    GLfloat t = 0
    GLfloat r = self->memory_cache->w
    GLfloat b = self->memory_cache->h

    GLfloat mx = l + self->x
    GLfloat my = t + self->y

    l += self->l
    t += self->t
    r -= self->r
    b -= self->b

    glBegin(GL_QUADS)

    glTexCoord2f(r / w, (h - b) / h)
    glVertex2d(r - mx, b - my)

    glTexCoord2f(l / w, (h - b) / h)
    glVertex2d(l - mx, b - my)

    glTexCoord2f(l / w, (h - t) / h)
    glVertex2d(l - mx, t - my)

    glTexCoord2f(r / w, (h - t) / h)
    glVertex2d(r - mx, t - my)

    glEnd()

def land_image_allegrogl_draw_scaled_rotated_tinted(LandImage *self, float x, float y,
    float sx, float sy, float angle, float r, float g, float b, float a):
    glColor4f(r, g, b, a)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(sx, sy, 1)
    glRotatef(angle * 180 / AL_PI, 0, 0, -1)
    quad(self)
    glPopMatrix()

def land_image_allegrogl_grab(LandImage *self, int x, int y):
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self)

    if !sub->gl_texture:
        int w = self->memory_cache->w
        int h = self->memory_cache->h

        int pad_w, pad_h
        pad_pot(w, h, &pad_w, &pad_h)

        glGenTextures(1, &sub->gl_texture)

    glBindTexture(GL_TEXTURE_2D, sub->gl_texture)

    GLint format = GL_RGB8
    GLint w, h
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w)
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h)
    #glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_INTERNAL_FORMAT, &format)

    # y position is bottom edge on screen to map to bottom edge of texture 
    glCopyTexImage2D(GL_TEXTURE_2D, 0, format, x, land_display_height() - y - h, w, h, 0)

def land_image_allegrogl_grab_into(LandImage *self, int x, int y, int tx, int ty, int tw, int th):
    int dh = land_display_height()
    int dw = land_display_width()
    if x < 0:
        tw += x
        tx -= x
        x = 0

    if y < 0:
        th += y
        ty -= y
        y = 0

    if x + tw > dw:
        tw -= x + tw - dw

    if y + th > dh:
        th -= y + th - dh

    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self)
    glBindTexture(GL_TEXTURE_2D, sub->gl_texture)
    GLint w, h
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w)
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h)

    if tx < 0:
        tw += tx
        x -= tx
        tx = 0

    if ty < 0:
        th += ty
        y -= ty
        ty = 0

    if tx + tw > w:
        tw -= tx + tw - w

    if ty + th > h:
        th -= ty + th - h

    glCopyTexSubImage2D(GL_TEXTURE_2D, 0, tx, h - ty - th, x, dh - y - th, tw, th)

def land_image_allegrogl_cache(LandImage *super):
    LandImageOpenGL *self = LAND_IMAGE_OPENGL(self)
    glBindTexture(GL_TEXTURE_2D, self->gl_texture)
    GLint w, h
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w)
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h)
    char *pixels = land_malloc(w * h * 4)
    glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV,
        pixels)
    int x, y
    for y = 0; y < super->memory_cache->h; y++:
        for x = 0; x < super->memory_cache->w; x++:
            ((int *)super->memory_cache->line[y])[x] = ((int *)(pixels + w * 4))[x]


    land_free(pixels)

def land_image_allegrogl_init(void):
    land_log_message("land_image_allegrogl_init\n")
    land_alloc(vtable)
    vtable->prepare = land_image_allegrogl_prepare
    vtable->draw_scaled_rotated_tinted = land_image_allegrogl_draw_scaled_rotated_tinted
    vtable->grab = land_image_allegrogl_grab
    vtable->grab_into = land_image_allegrogl_grab_into
    vtable->sub = land_image_allegrogl_sub
    images = land_list_new()

def land_image_allegrogl_exit(void):
    if images->count:
        land_log_message("Error: %d OpenGL images not destroyed.\n", images->count)
    land_list_destroy(images)
    land_free(vtable)

def land_image_allegrogl_prepare(LandImage *self):
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self)

    # FIXME: Sub-images don't work yet, they need a pointer to their parent,
    # e.g. right now, there's no way to get the right texture ID if the
    # parent texture changes
    # Assume that the parent is prepared.
    if self->flags & LAND_SUBIMAGE:
        return

    if sub->gl_texture:
        glDeleteTextures(1, &sub->gl_texture)

    int w = self->memory_cache->w
    int h = self->memory_cache->h

    int pad_w, pad_h
    pad_pot(w, h, &pad_w, &pad_h)

    BITMAP *temp = create_bitmap_ex(32, w + pad_w, h + pad_h)
    if self->palette: select_palette(self->palette)
    blit(self->memory_cache, temp, 0, 0, 0, 0, w, h)
    if (bitmap_color_depth(self->memory_cache) != 32):
        # Fix up empty alpha channel.
        int x, y
        for y = 0; y < h; y++:
            for x = 0; x < w; x++:
                ((unsigned char *)temp->line[y])[x * 4 + 3] = 255



    # Repeat border pixels across padding area of texture.
    int i
    for i = w; i < w + pad_w; i++:
        blit(self->memory_cache, temp, w - 1, 0, i, 0, 1, h)

    for i = h; i < h + pad_h; i++:
        blit(self->memory_cache, temp, 0, h - 1, 0, i, w, 1)

    int c = getpixel(self->memory_cache, w - 1, h - 1)
    rectfill(temp, w, h, w + pad_w, h + pad_h, c)

    sub->gl_texture = allegro_gl_make_texture_ex(AGL_TEXTURE_FLIP, temp, GL_RGBA8)
    destroy_bitmap(temp)

    glBindTexture(GL_TEXTURE_2D, sub->gl_texture)
    # FIXME:
    # For some reason, textures get some odd blur effect applied as returned
    # by AGL. The below command somehow fixes it???
    # Most probably a driver bug..
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, GL_RGBA,
        GL_UNSIGNED_INT_8_8_8_8_REV, NULL)

    land_log_message(" texture %d: %.1fMB %d = %d + %d x %d = %d + %d\n",
        sub->gl_texture,
        (w + pad_w) * (h + pad_h) * 4.0 / (1024 * 1024),
        w + pad_w, w, pad_w,
        h + pad_h, h, pad_h)

    # TODO: Allow different modes
    # anti-aliased: use GL_LINEAR
    # tiled: use GL_REPEAT
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
