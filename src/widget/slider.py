import base, container
static import land/land

class LandWidgetSlider:
    """
    A slider widget has a handle which can be dragged around to change a
    value.
    """
    LandWidgetContainer super

class LandWidgetHandle:
    """A handle widget is a widget which can move around inside its parent."""
    LandWidget super
    bool vertical
    float minval, maxval, value
    void (*update)(LandWidget *);
    int dragged
    int drag_x, drag_y

macro LAND_WIDGET_SLIDER(widget) ((LandWidgetSlider *) land_widget_check(widget,
    LAND_WIDGET_ID_SLIDER, __FILE__, __LINE__))
macro LAND_WIDGET_HANDLE(widget) ((LandWidgetHandle *) land_widget_check(widget,
    LAND_WIDGET_ID_HANDLE, __FILE__, __LINE__))

LandWidgetInterface *land_widget_slider_interface
LandWidgetInterface *land_widget_handle_horizontal_interface

LandWidget *def land_widget_handle_new(LandWidget *parent, float minval, maxval,
    bool vertical, void (*update)(LandWidget *), int x, y, w, h):
    LandWidgetHandle *self
    land_alloc(self)
    LandWidget *super = (void *)self
    land_widget_handle_interface_initialize()
    land_widget_base_initialize(super, parent, x, y, w, h)

    super->vt = land_widget_handle_horizontal_interface
    land_widget_theme_initialize(super)
    self->vertical = vertical
    self->minval = minval
    self->maxval = maxval
    self->update = update
    self->value = minval
    super->no_clip_check = 1
    
    self->super.box.w = self->super.box.min_width
    self->super.box.h = self->super.box.min_height

    return super

LandWidget *def land_widget_slider_new(LandWidget *parent, float minval, maxval,
        bool vertical, void (*update)(LandWidget *), int x, y, w, h):
    """
    vertical - whether the slider is vertical
    """
    LandWidgetSlider *self
    land_widget_slider_interface_initialize()
    land_alloc(self)
    LandWidget *super = (void *)self
    land_widget_container_initialize(super, parent, x, y, w, h)
    super->vt = land_widget_slider_interface
    land_widget_theme_initialize(super)

    LandWidget *handle = land_widget_handle_new(super, minval, maxval, vertical,
        update, x + super->element->il, y + super->element->it, 0, 0)

    land_widget_layout_set_minimum_size(super,
        handle->box.min_width + super->element->il + super->element->it,
        handle->box.min_height + super->element->il + super->element->it)

    return super

def land_widget_slider_size(LandWidget *widget, float dx, float dy):
    if not (dx or dy): return
    # Get handle
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(widget)
    LandListItem *item = container->children->first
    LandWidget *handle = LAND_WIDGET(item->data)
    
    land_widget_handle_update(handle, 0)

def land_widget_handle_update(LandWidget *super, int set):
    """
    Either set the value from the slider position, or else update the slider
    position from the value.
    """
    LandWidgetHandle *self = LAND_WIDGET_HANDLE(super)
    float minpos, maxpos
    float n, i
    n = self->maxval - self->minval
    i = self->value - self->minval
    minpos = super->parent->box.x + super->parent->element->il
    maxpos = super->parent->box.x + super->parent->box.w - super->parent->element->ir
    maxpos -= super->box.w

    if set:
        self->value = self->minval + (super->box.x - minpos) * n /\
            (maxpos - minpos)
        if self->update: self->update(super)
    else:
        super->box.x = minpos + i * (maxpos - minpos) / n
        super->box.y = super->parent->box.y + super->parent->element->it

def land_widget_handle_draw(LandWidget *super):
    land_widget_handle_update(super, 0)
    land_widget_theme_draw(super)

def land_widget_handle_mouse_tick(LandWidget *super):
    LandWidgetHandle *self = LAND_WIDGET_HANDLE(super)
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
        
        # sliders can only be moved horizontally right now...
        newy = t
        
        int dx = newx - super->box.x
        int dy = newy - super->box.y
        land_widget_move(super, dx, dy)
        land_widget_handle_update(super, 1)

def land_widget_slider_set_value(LandWidget *super, float value):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(super)
    LandListItem *item = container->children->first
    LandWidgetHandle *handle = LAND_WIDGET_HANDLE(item->data)
    handle->value = value
    land_widget_handle_update(LAND_WIDGET(handle), 0)

float def land_widget_slider_get_value(LandWidget *super):
    LandWidgetContainer *container = LAND_WIDGET_CONTAINER(super)
    LandListItem *item = container->children->first
    LandWidgetHandle *handle = LAND_WIDGET_HANDLE(item->data)
    return handle->value

def land_widget_slider_interface_initialize():
    if land_widget_slider_interface: return

    land_widget_container_interface_initialize()

    land_widget_slider_interface = land_widget_copy_interface(
        land_widget_container_interface, "slider.horizontal")
    land_widget_slider_interface->id |= LAND_WIDGET_ID_SLIDER
    land_widget_slider_interface->size = land_widget_slider_size

def land_widget_handle_interface_initialize():
    if land_widget_handle_horizontal_interface: return

    land_widget_base_interface_initialize()

    land_widget_handle_horizontal_interface = land_widget_copy_interface(
        land_widget_base_interface, "handle.horizontal")
    land_widget_handle_horizontal_interface->id |= LAND_WIDGET_ID_HANDLE
    land_widget_handle_horizontal_interface->draw =\
        land_widget_handle_draw
    land_widget_handle_horizontal_interface->mouse_tick =\
        land_widget_handle_mouse_tick
