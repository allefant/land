#ifdef _PROTOTYPE_
#include "../image.h"
#endif /* _PROTOTYPE_ */

#include <alleggl.h>
#include "display.h"
#include "allegrogl/image.h"

static LandImageInterface *vtable;

LandImage *land_image_allegrogl_new(LandDisplay *super)
{
    LandImage *self;
    land_alloc(self);
    self->vt = vtable;
    return self;
}

static void quad(LandImage *self)
{
    glBindTexture(GL_TEXTURE_2D, self->gl_texture);
    glBegin(GL_TRIANGLE_FAN);

    GLfloat w = self->bitmap->w;
    GLfloat h = self->bitmap->h;

    GLfloat l = 0;
    GLfloat t = 0;
    GLfloat r = self->bitmap->w;
    GLfloat b = self->bitmap->h;

    GLfloat mx = l + self->x;
    GLfloat my = t + self->y;

    l += 0;
    t += 0;
    r -= 0;
    b -= 0;

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
    float sx, float sy, float a, float r, float g, float b)
{
    glColor3f(r, g, b);
    glPushMatrix();
    glTranslatef(x, y, 0);
    glScalef(sx, sy, 1);
    glRotatef(a * 180 / AL_PI, 0, 0, 1);
    quad(self);
    glPopMatrix();
}

void land_image_allegrogl_init(void)
{
    land_log_msg("land_image_allegrogl_init\n");
    land_alloc(vtable);
    vtable->prepare = land_image_allegrogl_prepare;
    vtable->draw_scaled_rotated_tinted = land_image_allegrogl_draw_scaled_rotated_tinted;
}

void land_image_allegrogl_prepare(LandImage *self)
{
    allegro_gl_set_texture_format(GL_RGBA8);
    self->gl_texture = allegro_gl_make_texture(self->memory_cache);
}

