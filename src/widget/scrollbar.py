import ../land, container

class LandWidgetScrollbar:
    """
    A horizontal or vertical bar, which can be moved inside its parent.
    """
    LandWidget super
    LandWidget *target
    int dragged
    int drag_x, drag_y
    int vertical : 1
    int autohide : 1
    void (*callback)(LandWidget *self, int set, int *min, int *max, int *range, int *pos)

macro LAND_WIDGET_SCROLLBAR(widget) ((LandWidgetScrollbar *)
    land_widget_check(widget, LAND_WIDGET_ID_SCROLLBAR, __FILE__, __LINE__))

static import widget/box

global LandWidgetInterface *land_widget_scrollbar_vertical_interface
global LandWidgetInterface *land_widget_scrollbar_horizontal_interface

static def scroll_vertical_cb(LandWidget *self, int set, *min, *max, *range,
    *pos):
    """
    If set is not 0, then the target window is scrolled according to the
    scrollbar position.
    If set is 0, then the min/max/range/pos parameters are updated.
    """
    LandWidgetScrollbar *bar = LAND_WIDGET_SCROLLBAR(self)
    LandWidget *target = bar->target
    if target:
        LandWidget *viewport = target->parent
        if set:
            int ty = viewport->box.y + viewport->element->it
            if (target->box.y > ty) ty = target->box.y
            ty -= *pos
            land_widget_move(target, 0, ty - target->box.y)

        else:
            *min = 0
            *max = target->box.h - 1
            *range = viewport->box.h - viewport->element->it - viewport->element->ib
            *pos = viewport->box.y + viewport->element->it - target->box.y
            if *pos < *min: *min = *pos
            if *pos + *range - 1 > *max: *max = *pos + *range - 1

static def scroll_horizontal_cb(LandWidget *self, int set, *min, *max, *range,
    *pos):
    LandWidgetScrollbar *bar = LAND_WIDGET_SCROLLBAR(self)
    LandWidget *target = bar->target
    if target:
        LandWidget *viewport = target->parent
        if set:
            int tx = viewport->box.x + viewport->element->il
            if (target->box.x > tx) tx = target->box.x
            tx -= *pos
            land_widget_move(target, tx - target->box.x, 0)

        else:
            *min = 0
            *max = target->box.w - 1
            *range = viewport->box.w - viewport->element->il - viewport->element->ir
            *pos = viewport->box.x + viewport->element->il - target->box.x
            if *pos < *min: *min = *pos
            if *pos + *range - 1 > *max: *max = *pos + *range - 1

static int def get_size(LandWidget *super):
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(super)
    if self->vertical:
        return super->box.h
    else:
        return super->box.w

def land_widget_scrollbar_update(LandWidget *super, int set):
    """
    If set is not 0, then the target is updated from the scrollbar. Else the
    scrollbar adjusts to the target's scrolled position.
    """
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(super)
    int minval, maxval, val, valrange
    int minpos, maxpos, pos, posrange, minlen

    self->callback(super, 0, &minval, &maxval, &valrange, &val)

    if self->vertical:
        minpos = super->parent->box.y + super->parent->element->it
        maxpos = super->parent->box.y + super->parent->box.h - super->parent->element->ib - 1
        pos = super->box.y
        posrange = super->box.h
        minlen = super->element->minh
    else:
        minpos = super->parent->box.x + super->parent->element->il
        maxpos = super->parent->box.x + super->parent->box.w - super->parent->element->ir - 1
        pos = super->box.x
        posrange = super->box.w
        minlen = super->element->minw
    if set:
        maxpos -= posrange - 1
        maxval -= valrange - 1

        if maxpos == minpos:
            val = minval
        else:
            # Always round up when setting, since we round down when querying. 
            int rounded = maxpos - 1 - minpos
            val = (minval + (pos - minpos) * (maxval - minval) + rounded) / (maxpos - minpos)

        self->callback(super, 1, &minval, &maxval, &valrange, &val)

    else:
        posrange = (1 + maxpos - minpos) * valrange / (1 + maxval - minval)
        if posrange < minlen: posrange = minlen
        maxpos -= posrange - 1
        maxval -= valrange - 1
        # Cannot allow updates in hide/unhide, since the hiding/unhiding of the
        # scrollbar will change the layout.
        int f = land_widget_layout_freeze(super->parent->parent)
        if maxval == minval:
            pos = minpos
            if not super->parent->hidden:
                land_widget_hide(super->parent)
        else:
            pos = minpos + (val - minval) * (maxpos - minpos) / (maxval - minval)
            if super->parent->hidden:
                land_widget_unhide(super->parent)
        if f: land_widget_layout_unfreeze(super->parent->parent)

        int dx = 0, dy = 0, dw = 0, dh = 0
        if self->vertical:
            dh = posrange - super->box.h
            dy = pos - super->box.y
        else:
            dw = posrange - super->box.w
            dx = pos - super->box.x
        land_widget_move(super, dx, dy)
        land_widget_size(super, dw, dh)

def land_widget_scrollbar_draw(LandWidget *self):
    land_widget_scrollbar_update(self, 0)
    land_widget_theme_draw(self)

def land_widget_scrollbar_mouse_tick(LandWidget *super):
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(super)
    if land_mouse_delta_b():
        if land_mouse_b() & 1:
            self->drag_x = land_mouse_x() - super->box.x
            self->drag_y = land_mouse_y() - super->box.y
            self->dragged = 1

        else:
            self->dragged = 0

    if (land_mouse_b() & 1) and self->dragged:
        int newx = land_mouse_x() - self->drag_x
        int newy = land_mouse_y() - self->drag_y
        int l = super->parent->box.x + super->parent->element->il
        int t = super->parent->box.y + super->parent->element->it
        int r = super->parent->box.x + super->parent->box.w - super->box.w - super->parent->element->ir
        int b = super->parent->box.y + super->parent->box.h - super->box.h - super->parent->element->ib
        if newx > r: newx = r
        if newy > b: newy = b
        if newx < l: newx = l
        if newy < t: newy = t
        int dx = newx - super->box.x
        int dy = newy - super->box.y
        land_widget_move(super, dx, dy)
        int old_size = get_size(super)
        land_widget_scrollbar_update(super, 1)

        # layout of target may change by scrolling (e.g. when scrolled outside normal range) 
        land_widget_scrollbar_update(super, 0)
        int new_size = get_size(super)
        # If we scroll down, and layout changed, anchor to bottom. 
        if new_size > old_size:
            if self->vertical and dy > 0: self->drag_y += new_size - old_size
            if not self->vertical and dx > 0: self->drag_x += new_size - old_size

LandWidget *def land_widget_scrollbar_new(LandWidget *parent, *target,
    int vertical, int x, y, w, h):
    LandWidgetScrollbar *self
    
    land_widget_scrollbar_interface_initialize()

    land_alloc(self)
    LandWidget *super = &self->super
    land_widget_base_initialize(super, parent, x, y, w, h)

    self->target = target
    self->vertical = vertical
    if vertical:
        self->callback = scroll_vertical_cb
        super->vt = land_widget_scrollbar_vertical_interface
    else:
        self->callback = scroll_horizontal_cb
        super->vt = land_widget_scrollbar_horizontal_interface
    
    land_widget_theme_initialize(super)
    land_widget_theme_set_minimum_size(super)
    
    return super

def land_widget_scrollbar_autohide(LandWidget *self, int autohide):
    LAND_WIDGET_SCROLLBAR(self)->autohide = autohide

def land_widget_scrollbar_interface_initialize():
    if not land_widget_scrollbar_vertical_interface:
        LandWidgetInterface *i = land_widget_copy_interface(
            land_widget_base_interface, "scrollbar.vertical")
        i->id = LAND_WIDGET_ID_SCROLLBAR
        i->draw = land_widget_scrollbar_draw
        i->move = land_widget_base_move
        i->mouse_tick = land_widget_scrollbar_mouse_tick
        land_widget_scrollbar_vertical_interface = i

    if not land_widget_scrollbar_horizontal_interface:
        LandWidgetInterface *i = land_widget_copy_interface(
            land_widget_base_interface, "scrollbar.horizontal")
        i->id = LAND_WIDGET_ID_SCROLLBAR
        i->draw = land_widget_scrollbar_draw
        i->move = land_widget_base_move
        i->mouse_tick = land_widget_scrollbar_mouse_tick
        land_widget_scrollbar_horizontal_interface = i

