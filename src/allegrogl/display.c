#ifdef _PROTOTYPE_

#include <allegro.h>
#include <alleggl.h>
#include <math.h>

#include "array.h"
#include "../display.h"
#include "log.h"
#include "exception.h"

land_type(LandDisplayAllegroGL)
{
    LandDisplay super;
};

#endif /* _PROTOTYPE_ */

#include "allegrogl/display.h"
#include "allegrogl/image.h"

static LandDisplayInterface *vtable;

LandDisplayAllegroGL *land_display_allegrogl_new(int w, int h, int bpp, int hz,
    int flags)
{
    land_log_msg("land_display_allegrogl_new\n");
    LandDisplayAllegroGL *self = calloc(1, sizeof *self);
    LandDisplay *super = &self->super;
    super->w = w;
    super->h = h;
    super->bpp = bpp;
    super->hz = hz;
    super->flags = flags;
    super->vt = vtable;

    return self;
}

void land_display_allegrogl_set(LandDisplayAllegroGL *self)
{
    land_log_msg("land_display_allegrogl_set\n");
    LandDisplay *super = &self->super;
    int mode = GFX_AUTODETECT;

    int cd = desktop_color_depth();
    if (super->bpp)
        cd = super->bpp;

    if (install_allegro_gl())
    {
        land_exception("install_allegro_gl");
    }
    allegro_gl_set(AGL_COLOR_DEPTH, cd);
    allegro_gl_set(AGL_SUGGEST, AGL_COLOR_DEPTH);

    allegro_gl_set(AGL_DOUBLEBUFFER, 1);
    allegro_gl_set(AGL_SUGGEST, AGL_DOUBLEBUFFER);

    allegro_gl_set(AGL_SAMPLE_BUFFERS, 0);
    allegro_gl_set(AGL_SUGGEST, AGL_SAMPLE_BUFFERS);

    allegro_gl_set(AGL_SAMPLES, 0);
    allegro_gl_set(AGL_SUGGEST, AGL_SAMPLES);

    allegro_gl_set(AGL_RENDERMETHOD, 1);
    allegro_gl_set(AGL_SUGGEST, AGL_RENDERMETHOD);

    mode = GFX_OPENGL;
    if (super->flags & LAND_WINDOWED)
        mode = GFX_OPENGL_WINDOWED;
    else if (super->flags & LAND_FULLSCREEN)
        mode = GFX_OPENGL_FULLSCREEN;

    set_color_depth(cd);
    if (super->hz)
        request_refresh_rate(super->hz);
    set_gfx_mode(mode, super->w, super->h, 0, 0);

    glDisable(GL_CULL_FACE);
    glDisable(GL_DEPTH_TEST);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, SCREEN_W, SCREEN_H, 0, -1, 1);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    glClearColor(0, 0, 0, 0);

    glEnable(GL_TEXTURE_2D);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
}

void land_display_allegrogl_flip(LandDisplayAllegroGL *self)
{
    allegro_gl_flip();
}

void land_display_allegrogl_rectangle(LandDisplayAllegroGL *self,
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    glPushMatrix();
    glTranslatef(0.5, 0.5, 0); /* Center of pixel in GL. */
    glDisable(GL_TEXTURE_2D);
    glColor4f(r, g, b, 1);
    glBegin(GL_LINE_LOOP);
    glVertex2f(x, y);
    glVertex2f(x_, y);
    glVertex2f(x_, y_);
    glVertex2f(x, y_);
    glEnd();
    glPopMatrix();
}

void land_display_allegrogl_filled_circle(LandDisplayAllegroGL *self,
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    glPushMatrix();
    glTranslatef(0.5, 0.5, 0); /* Center of pixel in GL. */
    float min_side_length = 2;
    glDisable(GL_TEXTURE_2D);
    glColor4f(r, g, b, 1);
    glBegin(GL_POLYGON);
    float xradius = (x_ - x) * 0.5;
    float yradius = (y_ - y) * 0.5;
    float xcenter = x + xradius;
    float ycenter = y + yradius;
    float n = AL_PI / (asin(min_side_length / (2 * xradius)));
    float a = 0;
    float ai = AL_PI * 2 / n;
    if (ai > AL_PI / 4)
        ai = AL_PI / 4;

    while (a < AL_PI * 2)
    {
        glVertex2f(xcenter + xradius * cos(a), ycenter - yradius * sin(a));
        a += ai;
    }
    glEnd();
    glPopMatrix();
}

void land_display_allegrogl_circle(LandDisplayAllegroGL *self,
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    glPushMatrix();
    glTranslatef(0.5, 0.5, 0); /* Center of pixel in GL. */
    float min_side_length = 2;
    glColor4f(r, g, b, 1);
    glBegin(GL_LINE_LOOP);
    float xradius = (x_ - x) * 0.5;
    float yradius = (y_ - y) * 0.5;
    float xcenter = x + xradius;
    float ycenter = y + yradius;
    float n = AL_PI / (asin(min_side_length / (2 * xradius)));
    float a = 0;
    float ai = AL_PI * 2 / n;
    if (ai > AL_PI / 4)
        ai = AL_PI / 4;
    while (a < AL_PI * 2)
    {
        glVertex2f(xcenter + xradius * cos(a), ycenter + yradius * sin(a));
        a += ai;
    }
    glEnd();
    glPopMatrix();
}

void land_display_allegrogl_line(LandDisplayAllegroGL *self,
    float x, float y, float x_, float y_,
    float r, float g, float b)
{
    float dx = x_ - x;
    float dy = y_ - y;
    float d = sqrt(dx * dx + dy * dy);
    glPushMatrix();
    glTranslatef(0.5, 0.5, 0); /* Center of pixel in GL. */
    glDisable(GL_TEXTURE_2D);
    glColor4f(r, g, b, 1);
    glBegin(GL_LINES);
    glVertex2f(x, y);
    glVertex2f(x_ + dx / d, y_ + dy / d);
    glEnd();
    glPopMatrix();
}

void land_display_allegrogl_init(void)
{
    land_log_msg("land_display_allegrogl_init\n");
    land_alloc(vtable);

    vtable->set = (void *)land_display_allegrogl_set;
    vtable->flip = (void *)land_display_allegrogl_flip;
    vtable->rectangle = (void *)land_display_allegrogl_rectangle;
    vtable->line = (void *)land_display_allegrogl_line;
    vtable->new_image = (void *)land_image_allegrogl_new;
    vtable->filled_circle = (void *)land_display_allegrogl_filled_circle;
    vtable->circle = (void *)land_display_allegrogl_circle;
};
