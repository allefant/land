# 0000YYXX

#GUL_EXPAND_X 0
macro GUL_SHRINK_X 1
#GUL_LEFT 0
macro GUL_CENTER_X 2
macro GUL_RIGHT    4
macro GUL_EQUAL_X  8

macro GUL_LEAVE_X  16

#GUL_EXPAND_Y 0
macro GUL_SHRINK_Y (1 * 256)
#GUL_TOP 0
macro GUL_CENTER_Y (2 * 256)
macro GUL_BOTTOM   (4 * 256)
macro GUL_EQUAL_Y  (8 * 256)

macro GUL_LEAVE_Y  (16 * 256)

macro GUL_HIDDEN (1 * 65536)
macro GUL_NO_LAYOUT (2 * 65536)

# EQUAL_X:
# bottom-up: Try to use width of largest column, until parent->max_width / n
# top-down: use parent->w / n
# else: space is added to min_width for all expanding ones
#
# LEAVE_X:
# top-down: never modify, no matter what
#
# NO_LAYOUT:
# The widget's children are not to be affected by the layout. The widget itself
# is affected though. (Use LEAVE_X to make the widget itself not be affected.)
#



class LandLayoutBox:
    int x, y, w, h # outer box 

    # to speed up locating a child (think of a list with 100000 items)
    struct LandWidget **lookup_grid

    int cols, rows             # How many children? 

    int col, row               # Where are we in the parent? 
    int extra_cols             # How many extra columns do we span? 
    int extra_rows             # How many extra rows? 

    int min_width              # Minimum outer width in pixels. 
    int min_height             # Minimum outer height in pixels. 

    # useful to restrain expanding caused by children during bottom up
    int max_width              # Maximum outer width in pixels (0 for no limit). 
    int max_height             # Maximum outer height in pixels (0 for no limit). 

    int current_min_width
    int current_min_height

    int flags

import base
static import widget/container, widget/theme
static import global stdio, stdlib, assert, string, stdarg, allegro
static import log, memory

#static macro D(_); _
static macro D(_); (void)0;

static def ERR(char const *format, ...):
    va_list args
    va_start(args, format)
    #vprintf(format, args)
    char str[1024]
    uvszprintf(str, sizeof str, format, args)
    ustrzcat(str, sizeof str, "\n")
    land_log_message(str)
    va_end(args)
    
    #printf("\n")

def gul_box_initialize(LandLayoutBox *self):
    memset(self, 0, sizeof *self)
    self->min_width = 3
    self->min_height = 3

LandLayoutBox *def gul_box_new():
    LandLayoutBox *self = land_malloc(sizeof *self)

    gul_box_initialize(self)
    return self

def gul_box_deinitialize(LandLayoutBox *self):
    if self->lookup_grid:
        land_free(self->lookup_grid)
        self->lookup_grid = None

def gul_box_del(LandLayoutBox * self):
    gul_box_deinitialize(self)
    land_free(self)

# Find box which contains the specified grid position. 
#static LandLayoutBox *find_box_in_grid(LandLayoutBox *self, int col, int row)
#{
#    assert(col < self->cols && row < self->rows)
#    LandLayoutBox *c = self->children
#
#    while c:
#    {
#        if col >= c->col &&
#            row >= c->row &&
#            col <= c->col + c->extra_cols && row <= c->row + c->extra_rows:
#            return c
#        c = c->next
#    }
#    return NULL
#}

static def update_lookup_grid(LandWidget *self):
    if self->box.lookup_grid: land_free(self->box.lookup_grid)
    self->box.lookup_grid = None
    
    if self->box.flags & (GUL_NO_LAYOUT | GUL_HIDDEN): return
    
    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)

        if not container->children: return

        self->box.lookup_grid = land_calloc(self->box.cols * self->box.rows *
            sizeof *self->box.lookup_grid)

        # The lookup grid initially is filled with 0. Now all non-hidden boxes
        # fill in which grid cells they occupy.
        LandListItem *li = container->children->first
        for ; li; li = li->next:
            LandWidget *c = li->data
            int i, j
            # NO_LAYOUT children are handled like normal, since it only affects
            # layout inside themselves, not themselves.
            if c->box.flags & GUL_HIDDEN: continue
            for i = c->box.col; i <= c->box.col + c->box.extra_cols; i++:
                for j = c->box.row; j <= c->box.row + c->box.extra_rows; j++:
                    self->box.lookup_grid[i + j * self->box.cols] = c


# Same as find_box_in_grid, but O(c) instead of O(n). 
static LandWidget *def lookup_box_in_grid(LandWidget *self,
    int col, row):
    if not self->box.lookup_grid: update_lookup_grid(self)
    if not self->box.lookup_grid: return None
    assert(col < self->box.cols && row < self->box.rows)

    return self->box.lookup_grid[row * self->box.cols + col]

# TODO: provide functions for changing grid-size and cell-position, and do
# optimized lookup of the lookup table in all cases.
def gul_layout_updated(LandWidget *self):
    # If the parent has NO_LAYOUT set, then our own layout change also does
    # not trigger propagation of the layout change over this barrier. For
    # example, a button inside a window changes its size. Its parent uses
    # layout, so we recurse upwards to the window. The window sees that its
    # parent is a desktop with NO_LAYOUT, so now we call gul_box_fit_children
    # on the window, not propagating anything to the desktop.
    # TODO: The window's size may change though, so maybe the desktop would like
    # to know nevertheless? This has to be done outside the layout algorithm
    # though.
    update_lookup_grid(self)
    if self->parent and not (self->parent->box.flags & GUL_NO_LAYOUT):
        gul_layout_updated(self->parent)
    else:
        gul_box_fit_children(self)

# Get minimum height of the specified row. 
static int def row_min_height(LandWidget *self, int row):
    int i
    int v = 0

    for i = 0; i < self->box.cols; i++:
        LandWidget *c = lookup_box_in_grid(self, i, row)

        if c && c->box.current_min_height > v:
            v = c->box.current_min_height

    return v

# Get minimum width of the specified column. 
static int def column_min_width(LandWidget *self, int col):
    int i
    int v = 0

    for i = 0; i < self->box.rows; i++:
        LandWidget *c = lookup_box_in_grid(self, col, i)
    
        if c and c->box.current_min_width > v:
            v = c->box.current_min_width

    return v

# Check if a column is expanding (at least one cell). 
static int def is_column_expanding(LandWidget *self, int col):
    int i

    for i = 0; i < self->box.rows; i++:
        LandWidget *c = lookup_box_in_grid(self, col, i)

        if c and not (c->box.flags & GUL_SHRINK_X):
            return 1

    return 0

# Check if a row is expanding (at least one cell). 
static int def is_row_expanding(LandWidget *self, int row):
    int i

    for i = 0; i < self->box.cols; i++:
        LandWidget *c = lookup_box_in_grid(self, i, row)

        if c and not (c->box.flags & GUL_SHRINK_Y):
            return 1

    return 0

# Count number of expanding columns. 
static int def expanding_columns(LandWidget * self):
    int i
    int v = 0

    for i = 0; i < self->box.cols; i++:
        if is_column_expanding(self, i):
            v++

    return v

# Count number of expanding rows. 
static int def expanding_rows(LandWidget * self):
    int i
    int v = 0

    for i = 0; i < self->box.rows; i++:
        if is_row_expanding(self, i):
            v++

    return v

# Get minimum (outer) height so all children can possibly fit. 
static int def min_height(LandWidget *self):
    int i
    int v = 0

    for i = 0; i < self->box.rows; i++:
        v += row_min_height(self, i)
        
    v += self->element->vgap * (i - 1) + self->element->it + self->element->ib

    return v

# Get minimum (outer) width so all children can possibly fit. 
static int def min_width(LandWidget *self):
    int i
    int v = 0

    for i = 0; i < self->box.cols; i++:
        v += column_min_width(self, i)

    v += self->element->hgap * (i - 1) + self->element->il + self->element->ir

    return v

# Recursively calculate the minimum size of all children of the given widget,
# starting with the children. Basically, current_min_width/height is calculated
# for each box, based on the min_width/height of the bottom-most boxes.
static def gul_box_bottom_up(LandWidget *self):

    # A hidden box does not take up any space, ever.
    if self->box.flags & GUL_HIDDEN:
        self->box.current_min_width = 0
        self->box.current_min_height = 0
        return
    
    # A box with NO_LAYOUT is like a box without children.
    if not (self->box.flags & GUL_NO_LAYOUT):
        if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
            LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)
            if container->children:
                LandListItem *i = container->children->first
                for ; i; i = i->next:
                    LandWidget *c = i->data
                    gul_box_bottom_up(LAND_WIDGET(c))

                self->box.current_min_width = MAX(self->box.min_width,
                    min_width(self))
                self->box.current_min_height = MAX(self->box.min_height,
                    min_height(self))
                return

    self->box.current_min_width = self->box.min_width
    self->box.current_min_height = self->box.min_height

# Starting with the given box, recursively fit in all children.
static def gul_box_top_down(LandWidget *self):
    # A hidden box needs no layout since it gets assigned no space. A box
    # without layout is fully affected by the layout of its parent - but does
    # not allow the layout algorithm to run on its children.
    if self->box.flags & (GUL_HIDDEN | GUL_NO_LAYOUT): return

    D(printf("Box (%s[%p]): %d[%d] x %d[%d] at %d/%d\n", self->vt->name, self,
        self->box.w, self->box.cols, self->box.h, self->box.rows, self->box.x,
        self->box.y);)
    if self->box.cols == 0 or self->box.rows == 0:
        D(printf("    empty.\n");)
        return

    int minw = min_width(self)
    int minh = min_height(self)

    if self->box.max_width and minw > self->box.max_width:
        ERR("Fatal: Minimum width of children (%d) "
            "exceeds available space (%d).", minw, self->box.max_width)

    if self->box.max_height and minh > self->box.max_height:
        ERR("Fatal: Minimum height of children (%d) "
            "exceeds available space (%d).", minh, self->box.max_height)

    LandWidgetThemeElement *element = self->element

    int available_width = self->box.w - minw
    int available_height = self->box.h - minh

    int want_width = expanding_columns(self)
    int want_height = expanding_rows(self)

    D(printf("    Children: %d (%d exp) x %d (%d exp)\n",
        self->box.cols, want_width, self->box.rows, want_height);
        printf("              %d x %d\n", minw, minh);)

    int i, j

    # Adjust column positions and widths. 
    int x = self->box.x + element->il
    int share = 0

    if want_width:
        share = available_width / want_width
    available_width -= share * want_width
    D(printf("    Columns:");)
    for i = 0; i < self->box.cols; i++:
        int cw = column_min_width(self, i)
        int cx = x

        if is_column_expanding(self, i):
            cw += share
            # The first columns may get an extra pixel, in case we can't
            # evenly share. 
            if available_width:
                cw += 1
                available_width -= 1

            D(printf(" <->%d", cw);)

        else:
            D(printf(" [-]%d", cw);)
        x += cw + element->hgap

        # Place all rows in the column accordingly 
        for j = 0; j < self->box.rows; j++:
            LandWidget *c = lookup_box_in_grid(self, i, j)

            if c and c->box.row == j:
                # Prevent recursive layout updates. The layout algorithm itself
                # is recursive already. Maybe this needs to be re-thought (i.e.
                # make child widgets update their layout in resize handlers
                # independently, and this function gets non-recursive instead).
                int f = land_widget_layout_freeze(c)

                # Multi-row cells already were handled.
                if c->box.col == i:
                    int dx = cx - c->box.x
                    int dw = cw - c->box.w
                    land_widget_move(c, dx, 0)
                    land_widget_size(c, dw, 0)
                else:
                    int dw = cw - c->box.w
                    land_widget_size(c, dw, 0)
                    
                if f: land_widget_layout_unfreeze(c)

    D(printf("\n");)

    D(printf("    Rows:");)
    # Adjust row positions and heights. 
    int y = self->box.y + element->it

    share = 0
    if want_height:
        share = available_height / want_height
    available_height -= share * want_height
    for j = 0; j < self->box.rows; j++:
        int ch = row_min_height(self, j)
        int cy = y

        if (is_row_expanding(self, j)):
            ch += share
            # The first rows may get an extra pixel, in case we can't
            # evenly share. 
            if available_height:
                ch += 1
                available_height -= 1

            D(printf(" <->%d", ch);)

        else:
            D(printf(" [-]%d", ch);)
        y += ch + element->vgap

        # Place all columns in the row accordingly. 
        for i = 0; i < self->box.cols; i++:
            LandWidget *c = lookup_box_in_grid(self, i, j)

            if c and c->box.col == i:
                int f = land_widget_layout_freeze(c)
                # Multi-column cells already were handled.
                if c->box.row == j:
                    int dy = cy - c->box.y
                    int dh = ch - c->box.h
                    land_widget_move(c, 0, dy)
                    land_widget_size(c, 0, dh)
                else:
                    int dh = ch - c->box.h
                    land_widget_size(c, 0, dh)
                    
                if f: land_widget_layout_unfreeze(c)

    D(printf("\n");)

    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)
        if container->children:
            LandListItem *li = container->children->first
            for ; li; li = li->next:
                LandWidget *c = li->data
                gul_box_top_down(c)

# Given a box, (recursively) fit its children into it.
def gul_box_fit_children(LandWidget *self):
    D(printf("gul_box_fit_children %s[%p]\n", self->vt->name, self);)

    gul_box_bottom_up(self)
    int dw = self->box.current_min_width - self->box.w
    int dh = self->box.current_min_height - self->box.h
    self->box.w = self->box.current_min_width 
    self->box.h = self->box.current_min_height
    land_call_method(self, size, (self, dw, dh))

    gul_box_top_down(self)
