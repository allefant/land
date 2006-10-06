import ../land, base

# Returns 1 if layout is now inhibited, 0 if it already was.
int def land_widget_layout_inhibit(LandWidget *self):
    int nl = self->no_layout
    self->no_layout = 1
    return !nl

# Returns 1 if layout is now enabled, 0 if it already was.
int def land_widget_layout_enable(LandWidget *self):
    int nl = self->no_layout
    self->no_layout = 0
    return nl

def land_widget_layout_set_grid(LandWidget *self, int columns, int rows):
    self->box.rows = rows
    self->box.cols = columns
    if !self->no_layout:
        land_layout_update(self)

def land_layout_update(LandWidget *self):
    if not self->no_layout:
        gul_layout_updated(&self->box)

def land_widget_layout_set_grid_position(LandWidget *self, int column, int row):
    self->box.col = column
    self->box.row = row
    if self->parent and not self->parent->no_layout:
        land_layout_update(self->parent)

def land_widget_layout_set_grid_extra(LandWidget *self, int columns, int rows):
    self->box.extra_cols = columns
    self->box.extra_rows = rows
    if self->parent and not self->parent->no_layout:
        land_layout_update(self->parent)

def land_widget_layout_set_minimum_size(LandWidget *self, int w, int h):
    self->box.min_width = w
    self->box.min_height = h
    if self->box.current_min_width < w:
        self->box.current_min_width = w
    if self->box.current_min_height < h:
        self->box.current_min_height = h
    if self->box.w < w:
        self->box.w = w
    if self->box.h < h:
        self->box.h = h

def land_widget_layout_set_shrinking(LandWidget *self, int x, int y):
    if x:
        self->box.flags |= GUL_SHRINK_X
    if y:
        self->box.flags |= GUL_SHRINK_Y
        
    if self->parent and not self->parent->no_layout:
        land_layout_update(self)

def land_widget_layout_set_expanding(LandWidget *self, int x, int y):
    if x:
        self->box.flags &= ~GUL_SHRINK_X
    if y:
        self->box.flags &= ~GUL_SHRINK_Y

    if self->parent and not self->parent->no_layout:
        land_layout_update(self)

def land_widget_layout_set_border(LandWidget *self, int l, int t, int r, int b, int hgap, int vgap):
    self->box.il = l
    self->box.it = t
    self->box.ir = r
    self->box.ib = b
    self->box.hgap = hgap
    self->box.vgap = vgap

def land_widget_layout_add(LandWidget *parent, LandWidget *child):
    #gul_remove_child(&parent->box, &child->box, !parent->no_layout)
    #TODO: Clarify that having multiple children on the same spot is
    #allowed. E.g. LandBook does this for its pages.

    gul_attach_child(&parent->box, &child->box, !parent->no_layout)

def land_widget_layout_remove(LandWidget *parent, LandWidget *child):
    gul_remove_child(&parent->box, &child->box, !parent->no_layout)

def land_widget_layout_replace(LandWidget *parent, LandWidget *old,
    LandWidget *with):
    gul_box_replace_child(&parent->box, &old->box, &with->box)

def land_widget_layout(LandWidget *self):
    if !self->no_layout:
        gul_layout_updated(&self->box)
