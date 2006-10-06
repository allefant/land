# 0000YYXX

#GUL_EXPAND_X 0
macro GUL_SHRINK_X 1
#GUL_LEFT 0
macro GUL_CENTER_X 2
macro GUL_RIGHT    4
macro GUL_EQUAL_X  8

macro GUL_LEAVE_X  16

#GUL_EXPAND_Y 0
macro GUL_SHRINK_Y 256
#GUL_TOP 0
macro GUL_CENTER_Y 512
macro GUL_BOTTOM   1024
macro GUL_EQUAL_Y  2048

macro GUL_LEAVE_Y  4096

# EQUAL_X:
# bottom-up: Try to use width of largest column, until parent->max_width / n
# top-down: use parent->w / n
# else: space is added to min_width for all expanding ones
#
# LEAVE_X:
# top-down: never modify, no matter what
# 

macro GUL_HIDDEN 65536

class LandLayoutBox:
    int x, y, w, h # outer box 

    int il, it, ir, ib # offsets to inner box 
    int hgap, vgap # space between children 

    LandLayoutBox *parent            # Our parent. 

    LandLayoutBox *sibling           # Sibling using the same space in front of us, like a layer. 

    # Child boxes. 
    LandLayoutBox *children          # Linked list head. 
    LandLayoutBox *next              # Linked list pointer. 

    LandLayoutBox **lookup_grid # to speed up locating a child. 

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
    if (self->lookup_grid) land_free(self->lookup_grid)

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

# Same as find_box_in_grid, but O(c) instead of O(n). 
static LandLayoutBox *def lookup_box_in_grid(LandLayoutBox *self, int col, row):
    assert(col < self->cols && row < self->rows)

    return self->lookup_grid[row * self->cols + col]

static def update_lookup_grid(LandLayoutBox *self):
    if (self->lookup_grid) land_free(self->lookup_grid)
    self->lookup_grid = land_calloc(self->cols * self->rows *
        sizeof *self->lookup_grid)
    
    # The lookup grid initially is filled with 0. Now all non-hidden boxes
    # fill in which grid cells they occupy.
    LandLayoutBox *c = self->children
    for ; c; c = c->next:
        int i, j
        if (c->flags & GUL_HIDDEN) continue
        for i = c->col; i <= c->col + c->extra_cols; i++:
            for j = c->row; j <= c->row + c->extra_rows; j++:
                self->lookup_grid[i + j * self->cols] = c


# TODO: provide functions for changing grid-size and cell-position, and do
# optimized lookup of the lookup table in all cases.
def gul_layout_updated(LandLayoutBox *self):
    update_lookup_grid(self)
    if self->parent:
        gul_layout_updated(self->parent)
    else:
        gul_box_fit_children(self)

# Get minimum height of the specified row. 
static int def row_min_height(LandLayoutBox * self, int row):
    int i
    int v = 0

    for i = 0; i < self->cols; i++:
        LandLayoutBox *c = lookup_box_in_grid(self, i, row)

        if c && c->current_min_height > v:
            v = c->current_min_height

    return v

# Get minimum width of the specified column. 
static int def column_min_width(LandLayoutBox * self, int col):
    int i
    int v = 0

    for i = 0; i < self->rows; i++:
        LandLayoutBox *c = lookup_box_in_grid(self, col, i)
    
        if c and c->current_min_width > v:
            v = c->current_min_width

    return v

# Check if a column is expanding (at least one cell). 
static int def is_column_expanding(LandLayoutBox * self, int col):
    int i

    for i = 0; i < self->rows; i++:
        LandLayoutBox *c = lookup_box_in_grid(self, col, i)

        if c and not (c->flags & GUL_SHRINK_X):
            return 1

    return 0

# Check if a row is expanding (at least one cell). 
static int def is_row_expanding(LandLayoutBox * self, int row):
    int i

    for i = 0; i < self->cols; i++:
        LandLayoutBox *c = lookup_box_in_grid(self, i, row)

        if c and not (c->flags & GUL_SHRINK_Y):
            return 1

    return 0

# Count number of expanding columns. 
static int def expanding_columns(LandLayoutBox * self):
    int i
    int v = 0

    for i = 0; i < self->cols; i++:
        if is_column_expanding(self, i):
            v++

    return v

# Count number of expanding rows. 
static int def expanding_rows(LandLayoutBox * self):
    int i
    int v = 0

    for i = 0; i < self->rows; i++:
        if is_row_expanding(self, i):
            v++

    return v

# Get minimum (outer) height so all children can possibly fit. 
static int def min_height(LandLayoutBox * self):
    int i
    int v = 0

    for i = 0; i < self->rows; i++:
        v += row_min_height(self, i)

    v += self->vgap * (i - 1) + self->it + self->ib

    return v

# Get minimum (outer) width so all children can possibly fit. 
static int def min_width(LandLayoutBox * self):
    int i
    int v = 0

    for i = 0; i < self->cols; i++:
        v += column_min_width(self, i)

    v += self->hgap * (i - 1) + self->il + self->ir

    return v

def gul_attach_child(LandLayoutBox *self, LandLayoutBox *att, int update):
    LandLayoutBox *c

    for c = self->children; c && c->next; c = c->next:
        pass
    if c:
        c->next = att
    else:
        self->children = att
    att->parent = self

    if update:
        update_lookup_grid(self)

def gul_remove_child(LandLayoutBox *self, LandLayoutBox *rem, int update):
    LandLayoutBox *c, *p = NULL

    for c = self->children; c; c = c->next:
        if c == rem:
            if p:
                p->next = c->next
            else:
                self->children = c->next

            if update:
                update_lookup_grid(self)
            return

        p = c

def gul_box_replace_child(LandLayoutBox *self, *child, *with):
    gul_remove_child(self, child, 0)
    with->col = child->col
    with->row = child->row
    with->extra_cols = child->extra_cols
    with->extra_rows = child->extra_rows
    gul_attach_child(self, with, 0)
    
    update_lookup_grid(self) # could just replace relevant entries, but we
        #  don't bother     

# Recursively calculate the minimum size of all children of the fiven box,
# starting with the children. Basically, current_min_width/height is calculated
# for each box, based on the min_width/height of the bottom-most boxes.
static def gul_box_bottom_up(LandLayoutBox *self):
    LandLayoutBox *c
    if (self->flags & GUL_HIDDEN) return

    for c = self->children; c; c = c->next:
        gul_box_bottom_up(c)

    if self->children:
        self->current_min_width = MAX(self->min_width, min_width(self))
        self->current_min_height = MAX(self->min_height, min_height(self))

    else:
        self->current_min_width = self->min_width
        self->current_min_height = self->min_height


# Starting with the given box, recursively fit in all children.
static def gul_box_top_down(LandLayoutBox * self):
    if (self->flags & GUL_HIDDEN) return

    D(printf("Box: %d x %d\n", self->w, self->h);)
    if self->cols == 0 or self->rows == 0:
        D(printf("    empty.\n");)
        return

    int minw = min_width(self)
    int minh = min_height(self)

    if self->max_width and minw > self->max_width:
        ERR("Fatal: Minimum width of children (%d) "
            "exceeds available space (%d).", minw, self->max_width)

    if self->max_height and minh > self->max_height:
        ERR("Fatal: Minimum height of children (%d) "
            "exceeds available space (%d).", minh, self->max_height)

    int available_width = self->w - minw
    int available_height = self->h - minh

    int want_width = expanding_columns(self)
    int want_height = expanding_rows(self)

    D(printf("    Children: %d (%d exp) x %d (%d exp)\n",
           self->cols, want_width, self->rows, want_height)
    printf("              %d x %d\n", minw, minh);)

    int i, j

    D(printf("    Columns:");)
    # Adjust column positions and widths. 
    int x = self->x + self->il
    int share = 0

    if want_width:
        share = available_width / want_width
    available_width -= share * want_width
    for i = 0; i < self->cols; i++:
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
        x += cw + self->hgap

        # Place all rows in the column accordingly 
        for j = 0; j < self->rows; j++:
            LandLayoutBox *c = lookup_box_in_grid(self, i, j)

            if c and c->row == j:
                # Multi-row cells already were handled.
                if c->col == i:
                    c->x = cx
                    c->w = cw

                else:
                    c->w += cw

    D(printf("\n");)

    D(printf("    Rows:");)
    # Adjust row positions and heights. 
    int y = self->y + self->it

    share = 0
    if want_height:
        share = available_height / want_height
    available_height -= share * want_height
    for j = 0; j < self->rows; j++:
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
        y += ch + self->vgap

        # Place all columns in the row accordingly. 
        for i = 0; i < self->cols; i++:
            LandLayoutBox *c = lookup_box_in_grid(self, i, j)

            if c and c->col == i:
                # Multi-column cells already were handled.
                if c->row == j:
                    c->y = cy
                    c->h = ch

                else:
                    c->h += ch

    D(printf("\n");)

    LandLayoutBox *c

    for c = self->children; c; c = c->next:
        gul_box_top_down(c)

# Given a box, (recursively) fit its children into it.
def gul_box_fit_children(LandLayoutBox * self):
    D(printf("gul_box_bottom_up\n");)
    gul_box_bottom_up(self)
    self->w = self->current_min_width 
    self->h = self->current_min_height

    D(printf("gul_box_top_down\n");)
    gul_box_top_down(self)

# Returns the box at a given location. 
LandLayoutBox *def gul_child_at(LandLayoutBox * self, int x, int y):
    LandLayoutBox *c = self->children

    while c:
        if x >= c->x && y >= c->y && x < c->x + c->w && y < c->y + c->h:
            LandLayoutBox *cc = gul_child_at(c, x, y)

            if cc:
                return cc
            return c

        c = c->next

    return NULL

# Calls a callback for a box and all its siblings. 
def gul_cb(LandLayoutBox * self,
    void (*cb) (LandLayoutBox * self, void *data), void *data):
    LandLayoutBox *c = self

    while c:
        cb(c, data)
        c = c->next

