#ifdef _PROTOTYPE_
#include "../image.h"
#endif /* _PROTOTYPE_ */

#include <alleggl.h>
#include "display.h"
#include "allegrogl/image.h"

static LandImageInterface *vtable;

#define LAND_IMAGE_OPENGL(_x_) ((LandImageOpenGL *)_x_)

typedef struct LandImageOpenGL LandImageOpenGL;

struct LandImageOpenGL
{
    LandImage super;

    unsigned int gl_texture;
};

static void pad_pot(int w, int h, int *pad_w, int *pad_h)
{
    /* Pad to power of 2 for some older OpenGL drivers. Should actually
       query OpenGL if it is necessary.. */
    *pad_w = 1;
    while (*pad_w < w)
    {
        *pad_w *= 2;
    }
    *pad_w -= w;

    *pad_h = 1;
    while (*pad_h < h)
    {
        *pad_h *= 2;
    }
    *pad_h -= h;
}

LandImage *land_image_allegrogl_new(LandDisplay *super)
{
    LandImageOpenGL *self = calloc(1, sizeof *self);
    self->super.vt = vtable;
    return &self->super;
}

void land_image_allegrogl_del(LandDisplay *super, LandImage *self)
{
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self);
    if (sub->gl_texture)
    {
        glDeleteTextures(1, &sub->gl_texture);
    }
    land_free(self);
}

static void quad(LandImage *self)
{
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self);
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D, sub->gl_texture);

    GLfloat w, h;
    GLint i;
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &i);
    w = i;
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &i);
    h = i;

    GLfloat l = 0;
    GLfloat t = 0;
    GLfloat r = self->memory_cache->w;
    GLfloat b = self->memory_cache->h;

    GLfloat mx = l + self->x;
    GLfloat my = t + self->y;

    l += self->l;
    t += self->t;
    r -= self->r;
    b -= self->b;

    glBegin(GL_QUADS);

    glTexCoord2f(r / w, (h - b) / h);
    glVertex2d(r - mx, b - my);

    glTexCoord2f(l / w, (h - b) / h);
    glVertex2d(l - mx, b - my);

    glTexCoord2f(l / w, (h - t) / h);
    glVertex2d(l - mx, t - my);

    glTexCoord2f(r / w, (h - t) / h);
    glVertex2d(r - mx, t - my);

    glEnd();
}

void land_image_allegrogl_draw_scaled_rotated_tinted(LandImage *self, float x, float y,
    float sx, float sy, float angle, float r, float g, float b, float a)
{
    glColor4f(r, g, b, a);
    glPushMatrix();
    glTranslatef(x, y, 0);
    glScalef(sx, sy, 1);
    glRotatef(angle * 180 / AL_PI, 0, 0, -1);
    quad(self);
    glPopMatrix();
}

void land_image_allegrogl_grab(LandImage *self, int x, int y)
{
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self);

    if (!sub->gl_texture)
    {
        int w = self->memory_cache->w;
        int h = self->memory_cache->h;

        int pad_w, pad_h;
        pad_pot(w, h, &pad_w, &pad_h);

        glGenTextures(1, &sub->gl_texture);
    }

    glBindTexture(GL_TEXTURE_2D, sub->gl_texture);

    GLint format = GL_RGB8;
    GLint w, h;
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w);
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h);
    //glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_INTERNAL_FORMAT, &format);

    /* y position is bottom edge on screen to map to bottom edge of texture */
    glCopyTexImage2D(GL_TEXTURE_2D, 0, format, x, land_display_height() - y - h, w, h, 0);
}

void land_image_allegrogl_grab_into(LandImage *self, int x, int y, int tx, int ty, int tw, int th)
{
    int dh = land_display_height();
    int dw = land_display_width();
    if (x < 0)
    {
        tw += x;
        tx -= x;
        x = 0;
    }
    if (y < 0)
    {
        th += y;
        ty -= y;
        y = 0;
    }
    if (x + tw > dw)
    {
        tw -= x + tw - dw;
    }
    if (y + th > dh)
    {
        th -= y + th - dh;
    }
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self);
    glBindTexture(GL_TEXTURE_2D, sub->gl_texture);
    GLint w, h;
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w);
    glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h);

    if (tx < 0)
    {
        tw += tx;
        x -= tx;
        tx = 0;
    }
    if (ty < 0)
    {
        th += ty;
        y -= ty;
        ty = 0;
    }
    if (tx + tw > w)
    {
        tw -= tx + tw - w;
    }
    if (ty + th > h)
    {
        th -= ty + th - h;
    }

    glCopyTexSubImage2D(GL_TEXTURE_2D, 0, tx, h - ty - th, x, dh - y - th, tw, th);
}

void land_image_allegrogl_init(void)
{
    land_log_msg("land_image_allegrogl_init\n");
    land_alloc(vtable);
    vtable->prepare = land_image_allegrogl_prepare;
    vtable->draw_scaled_rotated_tinted = land_image_allegrogl_draw_scaled_rotated_tinted;
    vtable->grab = land_image_allegrogl_grab;
    vtable->grab_into = land_image_allegrogl_grab_into;
}

void land_image_allegrogl_prepare(LandImage *self)
{
    LandImageOpenGL *sub = LAND_IMAGE_OPENGL(self);
    if (sub->gl_texture)
    {
        glDeleteTextures(1, &sub->gl_texture);
    }

    int w = self->memory_cache->w;
    int h = self->memory_cache->h;

    int pad_w, pad_h;
    pad_pot(w, h, &pad_w, &pad_h);

    BITMAP *temp = create_bitmap_ex(32, w + pad_w, h + pad_h);
    blit(self->memory_cache, temp, 0, 0, 0, 0, w, h);

    /* Repeat border pixels across padding area of texture. */
    int i;
    for (i = w; i < w + pad_w; i++)
    {
        blit(self->memory_cache, temp, w - 1, 0, i, 0, 1, h);
    }
    for (i = h; i < h + pad_h; i++)
    {
        blit(self->memory_cache, temp, 0, h - 1, 0, i, w, 1);
    }
    int c = getpixel(self->memory_cache, w - 1, h - 1);
    rectfill(temp, w, h, w + pad_w - 1, h + pad_h - 1, c);

    sub->gl_texture = allegro_gl_make_texture_ex(AGL_TEXTURE_FLIP, temp, GL_RGBA8);

    destroy_bitmap(temp);

    land_log_msg(" texture %d: %d = %d + %d x %d = %d + %d\n", sub->gl_texture,
        w + pad_w, w, pad_w,
        h + pad_h, h, pad_h);

    glBindTexture(GL_TEXTURE_2D, sub->gl_texture);
    // TODO: Allow different modes
    // anti-aliased: use GL_NEAREST
    // tiled: use GL_REPEAT
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
}

