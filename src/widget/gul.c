#ifdef _PROTOTYPE_

typedef struct GUL_BOX GUL_BOX;
typedef enum GUL_GROW_TYPE GUL_GROW_TYPE;
typedef enum GUL_ALIGN_TYPE GUL_ALIGN_TYPE;

// 0000YYXX

//GUL_EXPAND_X 0
#define GUL_SHRINK_X 1
//GUL_LEFT 0
#define GUL_CENTER_X 2
#define GUL_RIGHT    4
#define GUL_EQUAL_X  8

#define GUL_LEAVE_X  16

//GUL_EXPAND_Y 0
#define GUL_SHRINK_Y 256
//GUL_TOP 0
#define GUL_CENTER_Y 512
#define GUL_BOTTOM   1024
#define GUL_EQUAL_Y  2048

#define GUL_LEAVE_Y  4096

/* EQUAL_X:
 * bottom-up: Try to use width of largest column, until parent->max_width / n
 * top-down: use parent->w / n
 * else: space is added to min_width for all expanding ones
 *
 * LEAVE_X:
 * top-down: never modify, no matter what
 */

#define GUL_HIDDEN 65536

struct GUL_BOX
{
    int x, y, w, h; /* outer box */

    int il, it, ir, ib; /* offsets to inner box */
    int hgap, vgap; /* space between children */

    GUL_BOX *parent;            /* Our parent. */

    GUL_BOX *sibling;           /* Sibling using the same space in front of us, like a layer. */

    /* Child boxes. */
    GUL_BOX *children;          /* Linked list head. */
    GUL_BOX *next;              /* Linked list pointer. */

    GUL_BOX **lookup_grid; /* to speed up locating a child. */

    int cols, rows;             /* How many children? */

    int col, row;               /* Where are we in the parent? */
    int extra_cols;             /* How many extra columns do we span? */
    int extra_rows;             /* How many extra rows? */

    int min_width;              /* Minimum outer width in pixels. */
    int min_height;             /* Minimum outer height in pixels. */

    // useful to restrain expanding caused by children during bottom up
    int max_width;              /* Maximum outer width in pixels. */
    int max_height;             /* Maximum outer height in pixels. */

    int current_min_width;
    int current_min_height;

    int flags;
};

#endif /* _PROTOTYPE_ */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <stdarg.h>
#include <allegro.h>

#include "log.h"
#include "memory.h"

#include "widget/gul.h"

//#define D(_) _
#define D(_) (void)0;

void ERR(char const *format, ...)
{
    va_list args;
    va_start(args, format);
    //vprintf(format, args);
    char str[1024];
    uvszprintf(str, sizeof str, format, args);
    ustrzcat(str, sizeof str, "\n");
    land_log_msg(str);
    va_end(args);
    
    //printf("\n");
}

void gul_box_initialize(GUL_BOX *self)
{
    memset(self, 0, sizeof *self);
    self->min_width = 3;
    self->min_height = 3;
}

GUL_BOX *gul_box_new(void)
{
    GUL_BOX *self = land_malloc(sizeof *self);

    gul_box_initialize(self);
    return self;
}

void gul_box_deinitialize(GUL_BOX *self)
{
    if (self->lookup_grid) land_free(self->lookup_grid);
}

void gul_box_del(GUL_BOX * self)
{
    gul_box_deinitialize(self);
    land_free(self);
}

/* Find box which contains the specified grid position. */
/*static GUL_BOX *find_box_in_grid(GUL_BOX *self, int col, int row)
{
    assert(col < self->cols && row < self->rows);
    GUL_BOX *c = self->children;

    while (c)
    {
        if (col >= c->col &&
            row >= c->row &&
            col <= c->col + c->extra_cols && row <= c->row + c->extra_rows)
            return c;
        c = c->next;
    }
    return NULL;
}*/

/* Same as find_box_in_grid, but O(c) instead of O(n). */
static GUL_BOX *lookup_box_in_grid(GUL_BOX *self, int col, int row)
{
    assert(col < self->cols && row < self->rows);

    return self->lookup_grid[row * self->cols + col];
}

static void update_lookup_grid(GUL_BOX *self)
{
    if (self->lookup_grid) land_free(self->lookup_grid);
    self->lookup_grid = land_calloc(self->cols * self->rows * sizeof *self->lookup_grid);
    
    /* The lookup grid initially is filled with 0. Now all non-hidden boxes
     * fill in which grid cells they occupy.
     */
    GUL_BOX *c = self->children;
    for (; c; c = c->next)
    {
        int i, j;
        if (c->flags & GUL_HIDDEN) continue;
        for (i = c->col; i <= c->col + c->extra_cols; i++)
        {
            for (j = c->row; j <= c->row + c->extra_rows; j++)
            {
                self->lookup_grid[i + j * self->cols] = c;
            }
        }
    }
}

/* TODO: provide functions for changing grid-size and cell-position, and to
 * optimized lookup of the lookup table in all cases.
 */
void gul_layout_changed(GUL_BOX *self)
{
    update_lookup_grid(self);
}

/* Get minimum height of the specified row. */
static int row_min_height(GUL_BOX * self, int row)
{
    int i;
    int v = 0;

    for (i = 0; i < self->cols; i++)
    {
        GUL_BOX *c = lookup_box_in_grid(self, i, row);

        if (c && c->current_min_height > v)
            v = c->current_min_height;
    }
    return v;
}

/* Get minimum width of the specified column. */
static int column_min_width(GUL_BOX * self, int col)
{
    int i;
    int v = 0;

    for (i = 0; i < self->rows; i++)
    {
        GUL_BOX *c = lookup_box_in_grid(self, col, i);
    
        if (c && c->current_min_width > v)
            v = c->current_min_width;
    }
    return v;
}

/* Check if a column is expanding (at least one cell). */
static int is_column_expanding(GUL_BOX * self, int col)
{
    int i;

    for (i = 0; i < self->rows; i++)
    {
        GUL_BOX *c = lookup_box_in_grid(self, col, i);

        if (c && !(c->flags & GUL_SHRINK_X))
            return 1;
    }
    return 0;
}

/* Check if a row is expanding (at least one cell). */
static int is_row_expanding(GUL_BOX * self, int row)
{
    int i;

    for (i = 0; i < self->cols; i++)
    {
        GUL_BOX *c = lookup_box_in_grid(self, i, row);

        if (c && !(c->flags & GUL_SHRINK_Y))
            return 1;
    }
    return 0;
}

/* Count number of expanding columns. */
static int expanding_columns(GUL_BOX * self)
{
    int i;
    int v = 0;

    for (i = 0; i < self->cols; i++)
    {
        if (is_column_expanding(self, i))
            v++;
    }
    return v;
}

/* Count number of expanding rows. */
static int expanding_rows(GUL_BOX * self)
{
    int i;
    int v = 0;

    for (i = 0; i < self->rows; i++)
    {
        if (is_row_expanding(self, i))
            v++;
    }
    return v;
}

/* Get minimum (outer) height so all children can possibly fit. */
static int min_height(GUL_BOX * self)
{
    int i;
    int v = 0;

    for (i = 0; i < self->rows; i++)
    {
        v += row_min_height(self, i);
    }

    v += self->vgap * (i - 1) + self->it + self->ib;

    return v;
}

/* Get minimum (outer) width so all children can possibly fit. */
static int min_width(GUL_BOX * self)
{
    int i;
    int v = 0;

    for (i = 0; i < self->cols; i++)
    {
        v += column_min_width(self, i);
    }

    v += self->hgap * (i - 1) + self->il + self->ir;

    return v;
}

void gul_attach_child(GUL_BOX *self, GUL_BOX *att, int update)
{
    GUL_BOX *c;

    for (c = self->children; c && c->next; c = c->next);
    if (c)
        c->next = att;
    else
        self->children = att;
    att->parent = self;

    if (update)
        update_lookup_grid(self);
}

void gul_remove_child(GUL_BOX * self, GUL_BOX * rem, int update)
{
    GUL_BOX *c, *p = NULL;

    for (c = self->children; c; c = c->next)
    {
        if (c == rem)
        {
            if (p)
            {
                p->next = c->next;
            }
            else
            {
                self->children = c->next;
            }
            if (update)
                update_lookup_grid(self);
            return;
        }
        p = c;
    }
}

void gul_box_replace_child(GUL_BOX * self, GUL_BOX * child, GUL_BOX * with)
{
    gul_remove_child(self, child, 0);
    with->col = child->col;
    with->row = child->row;
    with->extra_cols = child->extra_cols;
    with->extra_rows = child->extra_rows;
    gul_attach_child(self, with, 0);
    
    update_lookup_grid(self); /* could just replace relevant entries, but we
        don't bother */    
}


/*
 *
 */
static void gul_box_bottom_up(GUL_BOX * self)
{
    GUL_BOX *c;
    if (self->flags & GUL_HIDDEN) return;

    for (c = self->children; c; c = c->next)
    {
        gul_box_bottom_up(c);
    }

    if (self->children)
    {
        self->current_min_width = MAX(self->min_width, min_width(self));
        self->current_min_height = MAX(self->min_height, min_height(self));
    }
    else
    {
        self->current_min_width = self->min_width;
        self->current_min_height = self->min_height;
    }
}

/* Return value:
 *
 * 0 - ok
 * 1 - too small width
 * 2 - too small height
 * 3 - too small width as well as height
 */
static int gul_box_top_down(GUL_BOX * self)
{
    if (self->flags & GUL_HIDDEN) return 0;
    int r = 0;
    D(printf("Box: %d x %d\n", self->w, self->h);)
    if (self->cols == 0 || self->rows == 0)
    {
        D(printf("    empty.\n");)
        return 0;
    }
    int minw = min_width(self);
    int minh = min_height(self);

    if (minw > self->w)
    {
        ERR("Fatal: Minimum width of children (%d) "
            "exceeds available space (%d).", minw, self->w);
        r |= 1;
    }
    if (minh > self->h)
    {
        ERR("Fatal: Minimum height of children (%d) "
            "exceeds available space (%d).", minh, self->h);
        r |= 2;
    }

    /* Check if user specified min size is exceeded. */
    if (self->current_min_width > self->w) r |= 1;
    if (self->current_min_height > self->h) r |= 2;

    int available_width = self->w - minw;
    int available_height = self->h - minh;

    int want_width = expanding_columns(self);
    int want_height = expanding_rows(self);

    D(printf("    Children: %d (%d exp) x %d (%d exp)\n",
           self->cols, want_width, self->rows, want_height);
    printf("              %d x %d\n", minw, minh);)

    int i, j;

    D(printf("    Columns:");)
    /* Adjust column positions and widths. */
    int x = self->x + self->il;
    int share = 0;

    if (want_width)
        share = available_width / want_width;
    available_width -= share * want_width;
    for (i = 0; i < self->cols; i++)
    {
        int cw = column_min_width(self, i);
        int cx = x;

        if (is_column_expanding(self, i))
        {
            cw += share;
            /* The first columns may get an extra pixel, in case we can't
               evenly share. */
            if (available_width)
            {
                cw += 1;
                available_width -= 1;
            }
            D(printf(" <->%d", cw);)
        }
        else
            D(printf(" [-]%d", cw);)
        x += cw + self->hgap;

        /* Place all rows in the column accordingly */
        for (j = 0; j < self->rows; j++)
        {
            GUL_BOX *c = lookup_box_in_grid(self, i, j);

            if (c && c->row == j)
                /* Multi-row cells already were handled. */
            {
                if (c->col == i)
                {
                    c->x = cx;
                    c->w = cw;
                }
                else
                {
                    c->w += cw;
                }
            }
        }
    }
    D(printf("\n");)

    D(printf("    Rows:");)
    /* Adjust row positions and heights. */
    int y = self->y + self->it;

    share = 0;
    if (want_height)
        share = available_height / want_height;
    available_height -= share * want_height;
    for (j = 0; j < self->rows; j++)
    {
        int ch = row_min_height(self, j);
        int cy = y;

        if (is_row_expanding(self, j))
        {
            ch += share;
            /* The first rows may get an extra pixel, in case we can't
               evenly share. */
            if (available_height)
            {
                ch += 1;
                available_height -= 1;
            }
            D(printf(" <->%d", ch);)
        }
        else
            D(printf(" [-]%d", ch);)
        y += ch + self->vgap;

        /* Place all columns in the row accordingly. */
        for (i = 0; i < self->cols; i++)
        {
            GUL_BOX *c = lookup_box_in_grid(self, i, j);

            if (c && c->col == i)
                /* Multi-column cells already were handled. */
            {
                if (c->row == j)
                {
                    c->y = cy;
                    c->h = ch;
                }
                else
                {
                    c->h += ch;
                }
            }
        }
    }
    D(printf("\n");)

    GUL_BOX *c;

    for (c = self->children; c; c = c->next)
    {
        r |= gul_box_top_down(c);
    }
    return r;
}

/* Given a box, (recursively) fit its children into it. If adjust is 1, then
 * the box changes its size to the minimum size for the children to fit.
 */
int gul_box_fit_children(GUL_BOX * self, int adjustx, int adjusty)
{
    int r = 0;
    D(printf("gul_box_bottom_up\n");)
    gul_box_bottom_up(self);
    if (adjustx) self->w = self->current_min_width;
    if (adjusty) self->h = self->current_min_height;

    D(printf("gul_box_top_down\n");)
    r |= gul_box_top_down(self);
    return r;
}

/* Returns the box at a given location. */
GUL_BOX *gul_child_at(GUL_BOX * self, int x, int y)
{
    GUL_BOX *c = self->children;

    while (c)
    {
        if (x >= c->x && y >= c->y && x < c->x + c->w && y < c->y + c->h)
        {
            GUL_BOX *cc = gul_child_at(c, x, y);

            if (cc)
                return cc;
            return c;
        }
        c = c->next;
    }
    return NULL;
}

/* Calls a callback for a box and all its siblings. */
void
gul_cb(GUL_BOX * self, void (*cb) (GUL_BOX * self, void *data), void *data)
{
    GUL_BOX *c = self;

    while (c)
    {
        cb(c, data);
        c = c->next;
    }
}
