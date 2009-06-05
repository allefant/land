import base, layout

class LandWidgetSizer:
    LandWidget super
    # 0 = top, 1 = top right, 2 = right, 3 = bottom right
    # 4 = bottom, 5 = bottom left, 6 = left, 7 = top left
    int position
    LandWidget *target

    int dragged
    int drag_x, drag_y

macro LAND_WIDGET_SIZER(widget) ((LandWidgetSizer *)widget)

LandWidgetInterface *land_widget_sizer_interface[8]

def land_widget_sizer_draw(LandWidget *widget):
    land_widget_theme_draw(widget)

def land_widget_sizer_mouse_tick(LandWidget *super):
    LandWidgetSizer *self = LAND_WIDGET_SIZER(super)
    if (land_mouse_delta_b()):
        if (land_mouse_b() & 1):
            self->dragged = 1
            self->drag_x = land_mouse_x() - self->target->box.x
            self->drag_y = land_mouse_y() - self->target->box.y
        else:
            self->dragged = 0

    if ((land_mouse_b() & 1) && self->dragged):
        float mx = 0, my = 0, sx = 0, sy = 0
        float dx = land_mouse_x() - self->target->box.x - self->drag_x
        float dy = land_mouse_y() - self->target->box.y - self->drag_y
        if self->position == 0: sy = -dy; my = 1
        elif self->position == 1: sx = dx; sy = -dy; my = 1
        elif self->position == 2: sx = dx
        elif self->position == 3: sx = dx; sy = dy
        elif self->position == 4: sy = dy
        elif self->position == 5: sx = -dx; sy = dy; mx = 1
        elif self->position == 6: sx = -dx; mx = 1
        elif self->position == 7: sx = -dx; sy = -dy; mx = 1; my = 1
        float pw = self->target->box.w
        float ph = self->target->box.h

        self->target->box.flags |= GUL_RESIZE

        land_widget_resize(self->target, sx, sy)
        sx = self->target->box.w - pw
        sy = self->target->box.h - ph
        land_widget_move(self->target, mx * -sx, my * -sy)
        self->drag_x += sx - mx * sx
        self->drag_y += sy - my * sy

        # TODO: do we really want that? What if the parent doesn't use layout?
        # if self->target->parent:
        #    land_widget_layout(self->target->parent)
        self->target->box.flags &= ~GUL_RESIZE

LandWidget *def land_widget_sizer_new(LandWidget *parent, int position,
    x, y, w, h):
    """
    Create a new sizer widget. By default it will use its parent as target,
    and shrink depending on the position parameter.
    """
    LandWidgetSizer *self
    
    land_widget_sizer_interface_initialize()

    # FIXME: inhibit layout changes until our own vt is set

    land_alloc(self)
    LandWidget *super = &self->super
    land_widget_base_initialize(super, parent, x, y, w, h)
    super->vt = land_widget_sizer_interface[position]

    if position == 0 or position == 4:
        land_widget_layout_set_shrinking(super, 0, 1)
    if position == 2 or position == 6:
        land_widget_layout_set_shrinking(super, 1, 0)
    else:
        land_widget_layout_set_shrinking(super, 1, 1)

    land_widget_theme_initialize(super)
    if parent: land_widget_layout(parent)

    # by default, size the parent. 
    self->target = parent
    self->position = position
    self->dragged = 0

    return super

def land_widget_sizer_set_target(LandWidget *self, LandWidget *target):
    """
    This does not set any references, as it is assumed the sizer is a descendant
    of the target anyway.
    """
    LAND_WIDGET_SIZER(self)->target = target

def land_widget_sizer_interface_initialize():
    if land_widget_sizer_interface[0]: return
    char const *dir[8] = {"t", "rt", "r", "rb", "b", "lb", "l", "lt"}
    for int i = 0 while i < 8 with i++:
        char str[256]
        snprintf(str, sizeof str, "sizer.%s", dir[i])
        land_widget_sizer_interface[i] = land_widget_copy_interface(
            land_widget_base_interface, str)
        land_widget_sizer_interface[i]->draw = land_widget_sizer_draw
        land_widget_sizer_interface[i]->mouse_tick = land_widget_sizer_mouse_tick
