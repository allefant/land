import land/land, container

class LandWidgetScrollbar:
    """
    A horizontal or vertical bar, which can be moved inside its parent.
    """
    LandWidget super
    LandWidget *target
    int dragged
    int drag_x, drag_y
    bool vertical
    void (*callback)(LandWidget *self, bool update_target, int *min, int *max, int *range,
        int *pos)

macro LAND_WIDGET_SCROLLBAR(widget) ((LandWidgetScrollbar *)
    land_widget_check(widget, LAND_WIDGET_ID_SCROLLBAR, __FILE__, __LINE__))

static import box

global LandWidgetInterface *land_widget_scrollbar_vertical_interface
global LandWidgetInterface *land_widget_scrollbar_horizontal_interface

static def scroll_vertical_cb(LandWidget *self, bool update_target,
        int *min, *max, *range, *pos):
    """
    If update_target is not 0, then the target window is scrolled according to the
    scrollbar position.
    If update_target is 0, then the min/max/range/pos parameters are updated.
    """
    LandWidgetScrollbar *bar = LAND_WIDGET_SCROLLBAR(self)
    LandWidget *target = bar->target
    if target:
        LandWidget *viewport = target->parent

        if update_target:
            int ty = viewport->box.y + viewport->element->it
            if target->box.y > ty: ty = target->box.y
            ty -= *pos
            land_widget_move(target, 0, ty - target->box.y)
        else:
            *min = 0
            *max = target->box.h - 1
            *range = viewport->box.h - viewport->element->it - viewport->element->ib
            *pos = viewport->box.y + viewport->element->it - target->box.y
            if *pos < *min: *min = *pos
            if *pos + *range - 1 > *max: *max = *pos + *range - 1
    else:
        if not update_target:
            *min = 0
            *max = 0
            *range = 1
            *pos = 0


#    range
# min ___    max
# |..|___|...|
#    pos

static def scroll_horizontal_cb(LandWidget *self, bool update_target,
        int *min, *max, *range, *pos):
    LandWidgetScrollbar *bar = LAND_WIDGET_SCROLLBAR(self)
    LandWidget *target = bar->target
    if target:
        LandWidget *viewport = target->parent
        if update_target:
            int tx = viewport->box.x + viewport->element->il
            if target->box.x > tx: tx = target->box.x
            tx -= *pos
            land_widget_move(target, tx - target->box.x, 0)

        else:
            *min = 0
            *max = target->box.w - 1
            *range = viewport->box.w - viewport->element->il - viewport->element->ir
            *pos = viewport->box.x + viewport->element->il - target->box.x
            if *pos < *min: *min = *pos
            if *pos + *range - 1 > *max: *max = *pos + *range - 1
    else:
        if not update_target:
            *min = 0
            *max = 0
            *range = 1
            *pos = 0

static def get_size(LandWidget *super) -> int:
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(super)
    if self.vertical:
        return super->box.h
    else:
        return super->box.w

def land_widget_scrollbar_update(LandWidget *handle, bool update_target):
    """
    If update_target is set, then the target is updated from the scrollbar. Else the
    scrollbar adjusts to the target's scrolled position.
    """
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(handle)
    int minval, maxval, val, valrange
    int minpos, maxpos, pos, minlen

    LandWidget* bar_area = handle.parent

    self.callback(handle, 0, &minval, &maxval, &valrange, &val)

    if self.vertical:
        minpos = bar_area->box.y + bar_area->element->it
        maxpos = bar_area->box.y + bar_area->box.h - bar_area->element->ib - 1
        pos = handle->box.y
        minlen = handle->element->minh
    else:
        minpos = bar_area->box.x + bar_area->element->il
        maxpos = bar_area->box.x + bar_area->box.w - bar_area->element->ir - 1
        pos = handle->box.x
        minlen = handle->element->minw

    int posrange = 0
    if maxval > minval:
        posrange = (1 + maxpos - minpos) * valrange / (1 + maxval - minval)

    if posrange < minlen: posrange = minlen

    if update_target:
        maxpos -= posrange - 1
        maxval -= valrange - 1

        if maxpos <= minpos:
            return
        else:
            # Always round up when setting, since we round down when querying. 
            int rounded = maxpos - minpos - 1
            val = (minval + (pos - minpos) * (maxval - minval) + rounded) / (maxpos - minpos)

        self.callback(handle, 1, &minval, &maxval, &valrange, &val)

    else:
        # minpos/maxpos: pixel positions which can be covered in view
        # minval/maxval: pixel position which can be covered in scrollbar
        # valrage: length of viewed area in view
        # posrange: length of scrollbar
        maxpos -= posrange - 1
        maxval -= valrange - 1

        if maxval == minval:
            pos = minpos
        else:
            pos = minpos + (val - minval) * (maxpos - minpos) / (maxval - minval)

        int dx = 0, dy = 0
        if self.vertical:
            handle.box.w = bar_area->box.w - (
                bar_area->element->ir +
                bar_area->element->il)
            handle.box.h = posrange
            dx = bar_area->box.x + bar_area->element->il - handle->box.x
            dy = pos - handle->box.y
        else:
            handle.box.w = posrange
            handle.box.h = bar_area->box.h - (
                bar_area->element->ib +
                bar_area->element->it)
            dx = pos - handle->box.x
            dy = bar_area->box.y + bar_area->element->it - handle->box.y
        handle.box.min_width = handle.box.w
        handle.box.min_height = handle.box.h
        land_widget_move(handle, dx, dy)

def land_widget_scrollbar_draw(LandWidget *self):
    # land_widget_scrollbar_update(self, 0)
    land_widget_theme_draw(self)

def land_widget_scrollbar_mouse_tick(LandWidget *handle):
    LandWidgetScrollbar *self = LAND_WIDGET_SCROLLBAR(handle)
    if land_mouse_delta_b():
        if land_mouse_b() & 1:
            self.drag_x = land_mouse_x() - handle->box.x
            self.drag_y = land_mouse_y() - handle->box.y
            self.dragged = 1

        else:
            self.dragged = 0

    LandWidget* bar_area = handle.parent

    if (land_mouse_b() & 1) and self.dragged:
        int newx = land_mouse_x() - self.drag_x
        int newy = land_mouse_y() - self.drag_y
        int l = bar_area->box.x + bar_area->element->il
        int t = bar_area->box.y + bar_area->element->it
        int r = bar_area->box.x + bar_area->box.w - handle->box.w - bar_area->element->ir
        int b = bar_area->box.y + bar_area->box.h - handle->box.h - bar_area->element->ib
        if newx > r: newx = r
        if newy > b: newy = b
        if newx < l: newx = l
        if newy < t: newy = t
        int dx = newx - handle->box.x
        int dy = newy - handle->box.y
        land_widget_move(handle, dx, dy)
        int old_size = get_size(handle)
        land_widget_scrollbar_update(handle, 1)

        # layout of target may change by scrolling (e.g. when scrolled outside normal range) 
        land_widget_scrollbar_update(handle, 0)
        int new_size = get_size(handle)
        # If we scroll down or right and layout changed, anchor to bottom. 
        if new_size > old_size:
            if self.vertical and dy > 0: self->drag_y += new_size - old_size
            if not self.vertical and dx > 0: self->drag_x += new_size - old_size

def land_widget_scrollbar_new(LandWidget *parent, *target,
    int vertical, int x, y, w, h) -> LandWidget *:
    LandWidgetScrollbar *self

    land_widget_scrollbar_interface_initialize()

    land_alloc(self)
    LandWidget *super = &self.super
    land_widget_base_initialize(super, parent, x, y, w, h)

    self.target = target
    self.vertical = vertical
    if vertical:
        self.callback = scroll_vertical_cb
        super->vt = land_widget_scrollbar_vertical_interface
    else:
        self.callback = scroll_horizontal_cb
        super->vt = land_widget_scrollbar_horizontal_interface
    
    land_widget_theme_initialize(super)

    return super

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

