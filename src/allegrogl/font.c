#ifdef _PROTOTYPE_

#include <allegro.h>
#include <fudgefont.h>
#include "../array.h"
#include "../font.h"
#include "../log.h"

land_type(LandFontAllegrogl)
{
    struct LandFont super;
    FONT *font;
    //LandImage *image;
    //int x[256], y[256], w[256], h[256];
};

#define LAND_FONT_ALLEGROGL(_x_) ((LandFontAllegrogl *)_x_)

#endif /* _PROTOTYPE_ */

#include "allegrogl/font.h"
#include <allegro/internal/aintern.h>

static LandFontInterface *vtable;

/* Simple font implementation bypassing AllegroGL. Probably we should switch
 * to using this one, and ditch the AllegroGL one, which is way too
 * complicated, and doesn't even support kerning.
 */
#if 0
//static void grab(LandFontAllegrogl *self)
{
    LandImage *image = self->image;
    BITMAP *bmp = image->memory_cache;
    int w = land_image_width(image);
    int h = land_image_height(image);
    int x, y;
    int b = getpixel(bmp, 0, 0);
    int i = 32;
    for (y = 1; y < h; y++)
    {
        for (x = 1; x < w; x++)
        {
            int c = getpixel(bmp, x, y);
            int c1 = getpixel(bmp, x - 1, y);
            int c2 = getpixel(bmp, x - 1, y - 1);
            int c3 = getpixel(bmp, x, y - 1);
            if (c1 == b && c2 == b && c3 == b && c != b)
            {
                self->x[i] = x;
                self->y[i] = y;
                self->w[i] = 0;
                self->h[i] = 0;
                while (getpixel(bmp, x + self->w[i], y) != b)
                {
                    self->w[i] += 1;
                }
                while (getpixel(bmp, x, y + self->h[i]) != b)
                {
                    self->h[i] += 1;
                }
                land_log_msg(" %d: %d / %d: %d x %d\n", i,
                    self->x[i], self->y[i],
                    self->w[i], self->h[i]);
                i++;
            }
        }
    }
    for (y = 0; y < h; y++)
    {
        for (x = 0; x < w; x++)
        {
            if (getpixel(bmp, x, y) == b)
                putpixel(bmp, x, y, 0);
        }
    }
    land_image_prepare(self->image);
}

//LandFont *land_font_allegrogl_load(char const *filename, float size)
{
    land_log_msg("land_font_allegrogl_load %s %.1f\n", filename, size);
    LandFontAllegrogl *self = calloc(1, sizeof *self);

    self->image = land_image_load(filename);
    
    grab(self);
    
    self->super.size = self->h[32];
    self->super.vt = vtable;
    if (self->image)
    {
        land_log_msg(" %d success\n", self->h[32]);
    }
    else
        land_log_msg(" failure\n");

    return &self->super;
}

//void land_font_allegrogl_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement)
{
    LandFontAllegrogl *self = LAND_FONT_ALLEGROGL(state->font);
    if (!self)
        return;

    int l = ustrlen(text);
    int i;
    int w = 0;
    for (i = 0; i < l; i++)
        w += self->w[(int)text[i]];

    int h = state->font->size;

    float x = state->x_pos;
    float y = state->y_pos;
    if (alignement == 1) /* right */
        x -= w;
    else if (alignement == 2) /* center */
        x -= w / 2.0;
    if (!state->off)
    {
        float ox = x;
        float r, g, b, a;
        land_get_color(&r, &g, &b, &a);
        for (i = 0; i < l; i++)
        {
            int glyph = text[i];
            land_image_clip(self->image, self->x[glyph] - 1, self->y[glyph] - 1,
                self->x[glyph] + self->w[glyph] + 1,
                self->y[glyph] + self->h[glyph] + 1);
            /* Attempt to make small text not get blurry - doesn't seem to
             * work reliably.
             */
            ox = (int)ox;
            y = (int)y;
            land_image_draw_tinted(self->image, ox - self->x[glyph],
                y - self->y[glyph], r, g, b, a);
            ox += self->w[glyph];
        }
    }
    state->x = x;
    state->y = y;
    state->w = w;
    state->h = h;
}
#endif

LandFont *land_font_allegrogl_load(char const *filename, float size)
{
    land_log_msg("land_font_allegrogl_load %s %.1f\n", filename, size);
    LandFontAllegrogl *self = calloc(1, sizeof *self);
    PALETTE pal;
    int data = size;
    FONT *temp = load_font(filename, pal, &data);
    int alpha = 0;
    int paletted = 0;
    if (is_color_font(temp))
    {
        FONT_COLOR_DATA *fcd = temp->data;
        if (bitmap_color_depth(fcd->bitmaps[0]) == 32)
            alpha = 1;
        else
        {
            paletted = 1;
            fudgefont_color_range(0, 0, 0, 255, 255, 255);
        }
    }
    else
    {
        select_palette(pal);
        paletted = 1;
    }
    
    if (alpha) make_trans_font(temp);
    
        land_log_msg(" using %salpha, using %spalette\n",
            alpha ? "" : "no ", paletted ? "" : "no ");

    self->font = allegro_gl_convert_allegro_font_ex(temp,
        AGL_FONT_TYPE_TEXTURED, -1, paletted ? GL_ALPHA : GL_RGBA8);
    self->super.size = text_height(self->font);
    self->super.vt = vtable;
    if (self->font)
    {
        land_log_msg_nostamp(" %d success\n", text_height(temp));
        GLuint ids[10];
        int n = allegro_gl_list_font_textures(self->font, ids, 10);
        int i;
        for (i = 0; i < n; i++)
        {
            int w, h, r, g, b, a;
            glBindTexture(GL_TEXTURE_2D, ids[i]);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &w);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &h);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_RED_SIZE, &r);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_GREEN_SIZE, &g);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_BLUE_SIZE, &b);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_ALPHA_SIZE, &a);
            land_log_msg(" texture %d: %d x %d x (%d%d%d%d)\n", ids[i], w, h, r, g, b, a);
        }
    }
    else
        land_log_msg_nostamp("failure\n");
    destroy_font(temp);
    return &self->super;
}

void land_font_allegrogl_print(LandFontState *state, LandDisplay *display,
    char const *text, int alignement)
{
    LandFontAllegrogl *self = LAND_FONT_ALLEGROGL(state->font);
    if (!self)
        return;

    int w = text_length(self->font, text);
    int h = state->font->size;

    float x = state->x_pos;
    float y = state->y_pos;
    if (alignement == 1) /* right */
        x -= w;
    else if (alignement == 2) /* center */
        x -= w / 2.0;
    /* To avoid extra anti-aliasing "smear" effect with default viewport. */
    x = (int)x;
    y = (int)y;
    if (!state->off)
    {
        glEnable(GL_BLEND);
        glEnable(GL_TEXTURE_2D);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        allegro_gl_printf_ex(self->font, x, y, 0, "%s", text);
    }
    state->x = x;
    state->y = y;
    state->w = w;
    state->h = h;
}

void land_font_allegrogl_init(void)
{
    land_log_msg("land_font_allegrogl_init\n");
    land_alloc(vtable);
    vtable->print = land_font_allegrogl_print;
}

