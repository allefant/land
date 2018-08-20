import land/land, base

# Returns 1 if layout is now inhibited, 0 if it already was.
def land_widget_layout_freeze(LandWidget *self) -> int:
    int nl = self.no_layout
    self.no_layout = 1
    return not nl

# Returns 1 if layout is now enabled, 0 if it already was.
def land_widget_layout_unfreeze(LandWidget *self) -> int:
    int nl = self.no_layout
    self.no_layout = 0
    return nl

def land_widget_layout_set_grid(LandWidget *self, int columns, rows):
    self.box.rows = rows
    self.box.cols = columns
    land_widget_layout(self)

def land_widget_layout_disable(LandWidget *self):
    self.box.flags |= GUL_NO_LAYOUT

def land_widget_layout_enable(LandWidget *self):
    self.box.flags &= ~GUL_NO_LAYOUT

def land_widget_layout_set_grid_position(LandWidget *self, int column, row):
    self.box.col = column
    self.box.row = row
    if self.parent:
        land_widget_layout(self.parent)

def land_widget_layout_set_grid_extra(LandWidget *self, int columns, rows):
    self.box.extra_cols = columns
    self.box.extra_rows = rows
    if self.parent:
        land_widget_layout(self.parent)

def land_widget_layout_set_minimum_size(LandWidget *self, int w, h):
    self.box.min_width = w
    self.box.min_height = h

def land_widget_layout_set_maximum_size(LandWidget *self, int w, h):
    self.box.max_width = w
    self.box.max_height = h

def land_widget_layout_set_shrinking(LandWidget *self, int x, int y):
    if x:
        self.box.flags |= GUL_SHRINK_X
    if y:
        self.box.flags |= GUL_SHRINK_Y
        
    if self.parent and not self->parent->no_layout:
        land_widget_layout(self)

def land_widget_layout_set_expanding(LandWidget *self, int x, int y):
    if x:
        self.box.flags &= ~GUL_SHRINK_X
    if y:
        self.box.flags &= ~GUL_SHRINK_Y

    if self.parent:
        land_widget_layout(self)

def land_widget_layout(LandWidget *self):
    if not self.no_layout:
        land_internal_gul_layout_updated(self)

def land_widget_layout_initialize(LandWidget *self, int x, y, w, h):
    land_internal_land_gul_box_initialize(&self.box)
    self.box.x = x
    self.box.y = y
    self.box.w = w
    self.box.h = h
