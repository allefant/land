#ifdef _PROTOTYPE_


#include "../land.h"

typedef struct WidgetTheme WidgetTheme;
typedef struct WidgetThemeElement WidgetThemeElement;
typedef enum WidgetThemeFlags WidgetThemeFlags;

#include "base.h"

enum WidgetThemeFlags
{
    TILE_H = 0,
    TILE_V = 0,
    STRETCH_H = 1,
    STRETCH_V = 2,
    CENTER_H = 4,
    CENTER_V = 8,
    ALIGN_H = 16,
    ALIGN_V = 32
};

/* data for a single GUI bitmap */
struct WidgetThemeElement
{
    char const *name;
    LandImage *bmp;
    WidgetThemeFlags flags;
    int bl, bt, br, bb; /* border to cut out of the image */
    Widget *anchor; /* for the ALIGNED modes */
    int ox, oy; /* extra offset into the anchor widget */
    int color;
    LandFont *font;
};

struct WidgetTheme
{
    char const *name;
    char const *prefix;
    char const *suffix;
    /* TODO: instead of a list, use a mapping from the widget names. */
    LandList *elements;
};

#endif /* _PROTOTYPE_ */

#include "widget/theme.h"

/* Given two sizes, return an offset <= 0, so when texturing the area of size1
 * with a texture of size size2, the center will be aligned.
 */
static inline int
centered_offset (int size1, int size2)
{
    int center1, center2, o;

    if (!size1 || !size2)
        return 0;
    center1 = size1 / 2;
    center2 = size2 / 2;
    o = (center1 - center2) % size2;
    if (o > 0)
        o -= size2;
    return o;
}

static inline void _masked_non_stretched_blit(LandImage *s, int sx, int sy, int w, int h,
                           int dx, int dy, int _, int __)
{
    (void) _;
    (void) __;
    land_image_clip(s, sx, sy, sx + w, sy + h);
    land_image_draw(s, dx - sx, dy - sy);
}

static inline void _masked_stretched_blit(LandImage *s, int sx, int sy, int w, int h,
                           int dx, int dy, int dw, int dh)
{
    land_image_clip(s, sx, sy, sx + w, sy + h);
    land_image_draw_scaled(s, dx - sx, dy - sy, (float)dw / w,
        (float)dh / h);
}

enum COLUMN_TYPE
{
    COLUMN_CENTER = 1,
    COLUMN_STRETCH,
    COLUMN_LEFT,
    COLUMN_MIDDLE,
    COLUMN_RIGHT
};
/* Draw a column of pattern pat (at bx, width bw) into the given rectangle.
 */
static inline void blit_column(WidgetThemeElement *pat, int bx, int bw, int x, int y, int w, int h)
{
    int oy;
    int j;
    int bh = land_image_height(pat->bmp);
    int bm = bh - pat->bt - pat->bb;

    void (*bfunc)(LandImage *, int, int, int, int, int, int, int, int) =
        _masked_non_stretched_blit;

    if (bm < 1)
        return;

    if (pat->flags & ALIGN_V)
    {
        // TODO: anchor
        oy = (y / bm) * bm - y;
    }
    else
        oy = centered_offset (h, bm);

    if (w != bw)
    {
        bfunc = _masked_stretched_blit;
    }

    if (pat->flags & CENTER_V)
    {
        bfunc (pat->bmp, bx, 0, bw, land_image_height(pat->bmp), x,
               y + h / 2 - land_image_height(pat->bmp) / 2, w, land_image_height(pat->bmp));
    }
    else if (pat->flags & STRETCH_V)
    {
        _masked_stretched_blit(pat->bmp, bx, 0, bw, land_image_height(pat->bmp), x, y, w, h);
    }
    else /* pattern */
    {
        /* .....bx......
         *  ___ ___ ___
         * |   |   |   | .bt
         * |___|___|___|
         * |   |   |   | bm
         * |___|___|___|
         * |   |   |   | .bb
         * |___|___|___|
         *
         */

        int bt = pat->bt;
        int bb = pat->bb;
        if (bt + bb > h)
        {
            bt = h / 2;
            bb = h - bt;
        }

        /* top */
        if (bt)
        {
            land_clip_push();
            land_clip_intersect(0, y, land_display_width(),  MIN(y + h, y + bt));
            bfunc(pat->bmp, bx, 0, bw, bt, x, y, w, bt);
            land_clip_pop();
        }
        /* middle */
        if (h - pat->bt - pat->bb > 0)
        {
            land_clip_push();
            land_clip_intersect(0, MIN(y + h, y + pat->bt), land_display_width(), MAX(y, y + h - pat->bb));
            for (j = oy + y; j < y + h; j += bm)
            {
                bfunc(pat->bmp, bx, pat->bt, bw, bm, x, j, w, bm);
            }
            land_clip_pop();
        }
        /* bottom */
        if (bb)
        {
            land_clip_push();
            land_clip_intersect(0, MAX(y, y + h - bb), land_display_width(), y + h);
            bfunc(pat->bmp, bx, land_image_height(pat->bmp) - bb, bw, bb, x,
                y + h - bb, w, bb);
            land_clip_pop();
        }
    }
}

/* Draw the pattern pat into the specified rectangle, following the contained
 * tiling, stretching, alignement and bordering constraints.
 *
 * Borders align depending on their type:
 *
 * NW N NE
 * W  C  E
 * SW S SW
 *
 * The remaining texture is aligned with its center to the center, except if the
 * align flag is set. In this case, it will be aligned NW to the anchor.
 *
 */
static void draw_bitmap(WidgetThemeElement *pat, int x, int y, int w, int h)
{
    int i;

    int bw = land_image_width(pat->bmp);
    int bm = bw - pat->bl - pat->br;

    if (w < 1 || h < 1 || bm < 1)
        return;

    land_clip_push();
    land_clip_intersect(x, y, x + w, y + h);

    if (pat->flags & CENTER_H)
    {
        blit_column(pat, 0, bw, x + w / 2 - bw / 2, y, bw, h);
    }
    else if (pat->flags & STRETCH_H)
    {
        blit_column(pat, 0, bw, x, y, w, h);
    }
    else /* pattern */
    {
        int ox;
        if (pat->flags & ALIGN_H)
        {
            // TODO: anchor
            ox = (x / bm) * bm - x;
        }
        else
            ox = centered_offset(w, bm);

        /*
         * |    bw     |
         * |.bl|bm |.br|
         *  ___ ___ ___
         * |   |   |   |
         * |___|___|___|
         * |   |   |   |
         * |___|___|___|
         * |   |   |   |
         * |___|___|___|
         *
         */

        int bl = pat->bl;
        int br = pat->br;
        if (bl + br > w)
        {
            bl = w / 2;
            br = w - bl;
        }

        /* left */
        if (bl)
        {
            land_clip_push();
            land_clip_intersect(x, 0, MIN(x + w, x + bl), land_display_height());
            blit_column(pat, 0, bl, x, y, bl, h);
            land_clip_pop();
        }
        /* middle */
        if (w - pat->bl - pat->br > 0)
        {
            land_clip_push();
            land_clip_intersect(MIN(x + w, x + pat->bl), 0, MAX(x, x + w - pat->br),
                land_display_height());
            for (i = x + ox; i < x + w - pat->br; i += bm)
            {
                blit_column(pat, pat->bl, bm, i, y, bm, h);
            }
            land_clip_pop();
        }
        /* right */
        if (br)
        {
            land_clip_push();
            land_clip_intersect(MAX(x, x + w - br), 0, x + w, land_display_height());
            blit_column(pat, bw - br, br, x + w - br, y, br, h);
            land_clip_pop();
        }
    }

    land_clip_pop();
}

static void read_int_arg(int argc, char **argv, int *a, int *val)
{
    (*a)++;
    if (*a < argc)
    {
        *val = strtol (argv[*a], NULL, 10);
    }
}

WidgetThemeElement *widget_theme_element_new(struct WidgetTheme *theme, char const *element, int argc, char **argv)
{
    WidgetThemeElement *self;
    land_alloc(self);
    self->name = strdup(element);

    LandImage *img = NULL;
    if (argc)
    {
        char name[2048];
        uszprintf(name, sizeof name, "%s%s%s", theme->prefix, argv[0], theme->suffix);
        img = land_image_load(name);
        if (img)
        {
            int a;
            for (a = 1; a < argc; a++)
            {
                if (!strcmp (argv[a], "cut"))
                {
                    int cx = 0, cy = 0, cw = 0, ch = 0;
                    read_int_arg(argc, argv, &a, &cx);
                    read_int_arg(argc, argv, &a, &cy);
                    read_int_arg(argc, argv, &a, &cw);
                    read_int_arg(argc, argv, &a, &ch);

                    if (cw <= 0)
                        cw += land_image_width(img);
                    if (ch <= 0)
                        ch += land_image_height(img);
                    self->bmp = land_image_new_from(img, cx, cy, cw, ch);
                }
                else if (!strcmp (argv[a], "border"))
                {
                    read_int_arg(argc, argv, &a, &self->bl);
                    read_int_arg(argc, argv, &a, &self->br);
                    read_int_arg(argc, argv, &a, &self->bt);
                    read_int_arg(argc, argv, &a, &self->bb);
                }
            }
        }
    }

    land_log_msg("element: %d x %d, %d/%d/%d/%d\n", land_image_width(self->bmp),
        land_image_height(self->bmp), self->bl, self->bt, self->br, self->bb);

    return self;
}

WidgetTheme *widget_theme_new(char const *filename)
{
    WidgetTheme *self;
    land_alloc(self);

    push_config_state();
    set_config_file(filename);

    self->name = strdup(get_config_string("agup.cfg", "name", ""));
    self->prefix = strdup(get_config_string("agup.cfg", "prefix", ""));
    self->suffix = strdup(get_config_string("agup.cfg", "suffix", ""));

    char const **entries = NULL;
    int n = list_config_entries("agup.cfg/elements", &entries);
    int i;
    for (i = 0; i < n; i++)
    {
        int argc;
        char **argv = get_config_argv("agup.cfg/elements", entries[i], &argc);
        WidgetThemeElement *elem = widget_theme_element_new(self, entries[i], argc, argv);
        land_add_list_data(&self->elements, elem);
    }

    pop_config_state();

    return self;
}

static WidgetThemeElement *find_element(LandList *list, char const *name)
{
    LandListItem *item = list->first;
    while (item)
    {
        WidgetThemeElement *elem = item->data;
        if (!ustrcmp(elem->name, name))
            return elem;
        item = item->next;
    }
    return NULL;
}

void widget_theme_draw(Widget *self)
{
    struct WidgetTheme *theme = self->theme;

    if (!theme)
    {
        //land_color(1, 0, 0, 1);
        //land_rectangle(self->box.x + 0.5, self->box.y + 0.5, self->box.x + self->box.w - 0.5,
        //    self->box.y + self->box.h - 0.5);
        return;
    }

    WidgetThemeElement *element = find_element(theme->elements, self->vt->name);

    if (!element)
        element = find_element(theme->elements, "base");

    if (!element)
    {
        land_color(1, 1, 0, 1);
        land_rectangle(self->box.x + 0.5, self->box.y + 0.5, self->box.x + self->box.w - 0.5,
            self->box.y + self->box.h - 0.5);
        return;
    }

    draw_bitmap(element, self->box.x, self->box.y, self->box.w, self->box.h);
}
