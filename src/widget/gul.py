# 0000YYXX

#GUL_EXPAND_X 0
macro GUL_SHRINK_X 1
#GUL_LEFT 0
macro GUL_CENTER_X 2
macro GUL_RIGHT    4
macro GUL_EQUAL_X  8

#GUL_EXPAND_Y 0
macro GUL_SHRINK_Y  (16)
#GUL_TOP 0
macro GUL_CENTER_Y  (32)
macro GUL_BOTTOM    (64)
macro GUL_EQUAL_Y   (128)

macro GUL_HIDDEN    (256)

macro GUL_NO_LAYOUT (512) # for containers only
macro GUL_STEADFAST (1024) # for containers only

macro GUL_RESIZE    (2048)

# EQUAL_X:
# bottom-up: Try to use width of largest column, until parent->max_width / n
# top-down: use parent->w / n
# else: space is added to min_width for all expanding ones
#
# NO_LAYOUT:
# The widget's children are not to be affected by the layout. The widget
# itself is affected though. This affects the top-down pass only.
#
# GUL_RESIZE:
# The widget is being resized - if not enough space, go ahead and modify its
# minimum dimensions to fit.
#
# GUL_STEADFAST:
# The widget will not adjust its size to the size of its children.

class LandLayoutBox:
    int x, y, w, h # outer box
    int ow, oh # temporary dimensions

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

    int current_min_width      # when recalculating layout resets to min_width
    int current_min_height

    int flags

import base
static import container, theme
static import global stdio, stdlib, assert, string, stdarg
static import land/log, land/mem

static int gul_debug

static macro D(_):
    if gul_debug: _
#static macro D(_) (void)0;

static def ERR(char const *format, ...):
    va_list args
    va_start(args, format)
    #vprintf(format, args)
    char str[1024]
    vsnprintf(str, sizeof str, format, args)
    strcat(str, "\n")
    land_log_message(str)
    va_end(args)

    #printf("\n")

def land_internal_land_gul_box_initialize(LandLayoutBox *self):
    memset(self, 0, sizeof *self)

def land_internal_land_gul_box_deinitialize(LandLayoutBox *self):
    if self.lookup_grid:
        land_free(self.lookup_grid)
        self.lookup_grid = None

# Find box which contains the specified grid position. 
#static LandLayoutBox *find_box_in_grid(LandLayoutBox *self, int col, int row)
#{
#    assert(col < self.cols && row < self->rows)
#    LandLayoutBox *c = self.children
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
    if self.box.lookup_grid: land_free(self->box.lookup_grid)
    self.box.lookup_grid = None
    
    if self.box.flags & (GUL_NO_LAYOUT | GUL_HIDDEN): return
    
    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)

        if not container->children: return
        if self.box.cols * self->box.rows == 0: return

        self.box.lookup_grid = land_calloc(self->box.cols * self->box.rows *
            sizeof *self.box.lookup_grid)

        # The lookup grid initially is filled with 0. Now all non-hidden boxes
        # fill in which grid cells they occupy.
        LandListItem *li = container->children->first
        for  while li with li = li->next:
            LandWidget *c = li->data
            int i, j
            # NO_LAYOUT children are handled like normal, since it only affects
            # layout inside themselves, not themselves.
            if c->box.flags & GUL_HIDDEN: continue
            for i = c->box.col while i <= c->box.col + c->box.extra_cols with i++:
                for j = c->box.row while j <= c->box.row + c->box.extra_rows with j++:
                    if i >= self.box.cols or j >= self.box.rows:
                        error("ui layout error, %d/%d outside grid of %d/%d",
                            i, j, self.box.cols, self.box.rows)
                        print("widget: %s", land_widget_info_string(c))
                        print("container: %s", land_widget_info_string(self))
                    else:
                        self.box.lookup_grid[i + j * self->box.cols] = c


# Same as find_box_in_grid, but O(c) instead of O(n). 
static def lookup_box_in_grid(LandWidget *self,
    int col, row) -> LandWidget *:
    if not self.box.lookup_grid: update_lookup_grid(self)
    if not self.box.lookup_grid: return None
    assert(col < self.box.cols and row < self->box.rows)

    return self.box.lookup_grid[row * self->box.cols + col]

# Get minimum height of the specified row. 
static def row_min_height(LandWidget *self, int row) -> int:
    int v = 0
    for int i in range(self.box.cols):
        LandWidget *c = lookup_box_in_grid(self, i, row)
        if c and c->box.current_min_height > v:
            v = c->box.current_min_height
    return v

# Get minimum width of the specified column. 
static def column_min_width(LandWidget *self, int col) -> int:
    int v = 0
    for int i in range(self.box.rows):
        LandWidget *c = lookup_box_in_grid(self, col, i)
        if c and c->box.current_min_width > v:
            v = c->box.current_min_width
    return v

# Check if a column is expanding (at least one cell). 
static def is_column_expanding(LandWidget *self, int col) -> int:
    int i

    for i = 0 while i < self.box.rows with i++:
        LandWidget *c = lookup_box_in_grid(self, col, i)

        if c and c->box.col == col and not (c->box.flags & GUL_SHRINK_X):
            return 1

    return 0

# Check if a row is expanding (at least one cell). 
static def is_row_expanding(LandWidget *self, int row) -> int:
    int i

    for i = 0 while i < self.box.cols with i++:
        LandWidget *c = lookup_box_in_grid(self, i, row)

        if c and c->box.row == row and not (c->box.flags & GUL_SHRINK_Y):
            return 1

    return 0

# Count number of expanding columns. 
static def expanding_columns(LandWidget * self) -> int:
    int i
    int v = 0

    for i = 0 while i < self.box.cols with i++:
        if is_column_expanding(self, i):
            v++

    return v

# Count number of expanding rows. 
static def expanding_rows(LandWidget * self) -> int:
    int i
    int v = 0

    for i = 0 while i < self.box.rows with i++:
        if is_row_expanding(self, i):
            v++

    return v

# Get minimum (outer) height so all children can possibly fit. 
static def min_height(LandWidget *self) -> int:
    int v = 0
    for int i in range(self.box.rows):
        v += row_min_height(self, i)

    if self.element:
        v += self.element->vgap * (self.box.rows - 1)
        v += self->element->it + self->element->ib
    return v

# Get minimum (outer) width so all children can possibly fit. 
static def min_width(LandWidget *self) -> int:
    int v = 0
    for int i in range(self.box.cols):
        v += column_min_width(self, i)
    if self.element:
        v += self.element->hgap * (self.box.cols - 1)
        v += self->element->il + self->element->ir
    return v

static def adjust_resize_width(LandWidget *self, int dx) -> int:
    for int i in range(self.box.cols):
        int j
        for j = 0 while j < self.box.rows with j++:
            LandWidget *c = lookup_box_in_grid(self, i, j)
            if c and c->box.flags & GUL_RESIZE:
                c.box.current_min_width += dx
                return 1
    return 0

static def adjust_resize_height(LandWidget *self, int dx) -> int:
    int j
    for j = 0 while j < self.box.rows with j++:
        int i
        for i = 0 while i < self.box.cols with i++:
            LandWidget *c = lookup_box_in_grid(self, i, j)
            if c and c->box.flags & GUL_RESIZE:
                c->box.current_min_height += dx
                return 1
    return 0

# Recursively calculate the minimum size of all children of the given widget,
# starting with the children. Basically, current_min_width/height is calculated
# for each box, based on the min_width/height of the bottom-most boxes.
static def gul_box_bottom_up(LandWidget *self):

    # A hidden box does not take up any space, ever.
    if self.box.flags & GUL_HIDDEN:
        self.box.current_min_width = 0
        self.box.current_min_height = 0
        return

    LandWidgetContainer *container = None
    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
         container = LAND_WIDGET_CONTAINER(self)

    # A box with NO_LAYOUT is like a box without children.
    if (self.box.flags & GUL_NO_LAYOUT) or not container or not container.children:
        self.box.current_min_width = self.box.min_width
        self.box.current_min_height = self.box.min_height
        return

    for LandWidget *c in LandList* container.children:
        gul_box_bottom_up(LAND_WIDGET(c))

    int min_w = min_width(self)
    int min_h = min_height(self)
    self.box.current_min_width = max(self.box.min_width, min_w)
    self.box.current_min_height = max(self.box.min_height, min_h)

static def gul_box_top_down(LandWidget *self):
    """
    Recursively fit in all child widgets into the given widget.
    """

    D(printf("Box (%s[%p]): %d[%d] x %d[%d] at %d/%d\n", self.vt->name, self,
        self.box.w, self->box.cols, self->box.h, self->box.rows, self->box.x,
        self.box.y))
        
    # A hidden box needs no layout since it gets assigned no space. A box
    # without layout is fully affected by the layout of its parent - but does
    # not allow the layout algorithm to run on its children.
    if self.box.flags & GUL_HIDDEN:
        D(printf("    hidden.\n"))
        return
    if self.box.flags & GUL_NO_LAYOUT:
        D(printf("    no layout.\n"))
        return

    if self.box.cols == 0 or self->box.rows == 0:
        D(printf("    empty.\n"))
        return

    int minw = min_width(self)
    int minh = min_height(self)

    # If we go over the max width find a column which we can shrink.
    if self.box.max_width and minw > self->box.max_width:
        if not adjust_resize_width(self, self.box.max_width - minw):
            ERR("Fatal: Minimum width of children (%d) "
                "exceeds available space (%d).", minw, self.box.max_width)

    if self.box.max_height and minh > self->box.max_height:
        if not adjust_resize_height(self, self.box.max_height - minh):
            ERR("Fatal: Minimum height of children (%d) "
                "exceeds available space (%d).", minh, self.box.max_height)

    LandWidgetThemeElement *element = self.element

    int available_width = self.box.w - minw
    int available_height = self.box.h - minh

    int want_width = expanding_columns(self)
    int want_height = expanding_rows(self)

    D(printf("    Children: %d (%d exp) x %d (%d exp)\n",
        self.box.cols, want_width, self->box.rows, want_height))
    D(printf("              %d x %d min\n", minw, minh))

    int i, j

    # Adjust column positions and widths. 
    int x = self.box.x
    if self.element: x += element->il
    int share = 0

    if want_width:
        share = available_width / want_width
    available_width -= share * want_width
    D(printf("    Columns:"))
    int hgap = self.element ? element->hgap : 0
    for i = 0 while i < self.box.cols with i++:
        int cw = column_min_width(self, i)
        int cx = x

        if is_column_expanding(self, i):
            cw += share
            # The first columns may get an extra pixel, in case we can't
            # evenly share. 
            if available_width:
                cw += 1
                available_width -= 1

            D(printf(" <->%d", cw))

        else:
            D(printf(" [-]%d", cw))
        x += cw + hgap

        # Place all rows in the column accordingly 
        for j = 0 while j < self.box.rows with j++:
            LandWidget *c = lookup_box_in_grid(self, i, j)
            # Multi-row cells already were handled.
            if c and c->box.row == j:
                if c->box.col == i:
                    c->box.w = cw
                    land_widget_move(c, cx - c->box.x, 0)
                else: # Multi-column cell.
                    c->box.w += cw + hgap

    D(printf("\n"))

    D(printf("    Rows:"))
    # Adjust row positions and heights. 
    int y = self.box.y
    if self.element:
        y += element->it

    share = 0
    if want_height:
        share = available_height / want_height
    available_height -= share * want_height
    int vgap = self.element ? element->vgap : 0
    for j = 0 while j < self.box.rows with j++:
        int ch = row_min_height(self, j)
        int cy = y

        if is_row_expanding(self, j):
            ch += share
            # The first rows may get an extra pixel, in case we can't
            # evenly share. 
            if available_height:
                ch += 1
                available_height -= 1

            D(printf(" <->%d", ch))

        else:
            D(printf(" [-]%d", ch))
        y += ch
        y += vgap

        # Place all columns in the row accordingly. 
        for i = 0 while i < self.box.cols with i++:
            LandWidget *c = lookup_box_in_grid(self, i, j)
            # Multi-column cells already were handled.
            if c and c->box.col == i:
                if c->box.row == j:
                    c->box.h = ch
                    land_widget_move(c, 0, cy - c->box.y)
                else: # Multi-row cell.
                    c->box.h += ch + vgap

    D(printf("\n"))

    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *container = LAND_WIDGET_CONTAINER(self)
        if container->children:
            LandListItem *li = container->children->first
            for while li with li = li->next:
                LandWidget *c = li->data

                if c->box.w != c->box.ow or c->box.h != c->box.oh:
                    land_call_method(c, layout_changing, (c))

                gul_box_top_down(c)

                if c->box.w != c->box.ow or c->box.h != c->box.oh:
                    land_call_method(c, layout_changed, (c))
                    c->box.ow = c->box.w
                    c->box.oh = c->box.h

                if c->layout_hack:
                    # In case the size change induced a layout change, for example
                    # scrollbars appearing or disappearing, we repeat the
                    # calculations.
                    c->layout_hack = 0
                    gul_box_top_down(c)

# Given a box, (recursively) fit its children into it.
static def gul_box_fit_children(LandWidget *self):
    D(printf("gul_box_fit_children %s[%p]\n", self.vt->name, self))

    gul_box_bottom_up(self)

    if not (self.box.flags & GUL_STEADFAST):
        # TODO: we also resize the box itself here? why?
        self.box.w = self->box.current_min_width
        self.box.h = self->box.current_min_height

    if self.no_layout_notify == 0:
        land_call_method(self, layout_changing, (self))

    gul_box_top_down(self)

    if self.no_layout_notify == 0:
        land_call_method(self, layout_changed, (self))

# TODO: provide functions for changing grid-size and cell-position, and do
# optimized lookup of the lookup table in all cases.
def land_internal_gul_layout_updated(LandWidget *self):
    """
    This is used if the size of a widget may have changed and therefore its own
    as well as its parent's layout needs updating.
    """
    D(printf("gul_layout_updated %s[%p]\n", self.vt->name, self))
    # If the parent has NO_LAYOUT set, then our own layout change also does
    # not trigger propagation of the layout change over this barrier. For
    # example, a button inside a window changes its size. That parent window uses
    # layout, so we recurse upwards to the window. The window sees that its
    # parent is a desktop with NO_LAYOUT, so now we call gul_box_fit_children
    # on the window, not propagating anything to the desktop.
    # TODO: The window's size may change though, so maybe the desktop would like
    # to know nevertheless? This has to be done outside the layout algorithm
    # though.
    update_lookup_grid(self)
    if self.parent and not (self->parent->box.flags & GUL_NO_LAYOUT):
        if self.no_layout_notify == 0:
            self.no_layout_notify = 1
            land_internal_gul_layout_updated(self.parent)
            self.no_layout_notify = 0
    else:
        gul_box_fit_children(self)

def land_internal_gul_layout_updated_during_layout(LandWidget *self):
    """
    FIXME: What the hell is this? Can't we do it the proper way?
    If widgets are added or removed in the middle of a layout algorithm run,
    this function should be called from within the layout_changed event.
    """
    update_lookup_grid(self)
    gul_box_bottom_up(self)
