import base, hbox, button

# A spin control is a container, who contains and edit box and two buttons,
# with which the value of the edit box can be increased/decreased.
# 
class LandWidgetSpin:
    LandWidgetHBox super
    double min, max, step

class LandWidgetSpinButton:
    LandWidgetButton button
    LandWidget *spin
    double initial_delay # How many seconds to wait before auto-spinning. 
    double rate # How much time to wait between spins. 
    double dir

    double seconds
    double delay
    int count
    double step

macro LAND_WIDGET_SPIN(widget) ((LandWidgetSpin *) land_widget_check(widget,
    LAND_WIDGET_ID_SPIN, __FILE__, __LINE__))
macro LAND_WIDGET_SPINBUTTON(widget) ((LandWidgetSpinButton *)
    land_widget_check(widget, LAND_WIDGET_ID_SPINBUTTON, __FILE__, __LINE__))

static import land/land

LandWidgetInterface *land_widget_spin_interface
LandWidgetInterface *land_widget_spinbutton_interface

# FIXME: should come from theme
static LandImage *image_up
static LandImage *image_down

static def updated(LandWidget *base):
    LandListItem *item = LAND_WIDGET_CONTAINER(base)->children->first
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(item->data)
    if edit->modified:
        edit->modified(LAND_WIDGET(edit))

LandWidget *def land_widget_spinbutton_new(LandWidget *parent, LandImage *image,
    void (*clicked)(LandWidget *self),  int x, int y, int w, int h):
    LandWidgetSpinButton *spinbutton
    land_alloc(spinbutton)
    LandWidget *self = (LandWidget *)spinbutton
    land_widget_button_initialize(self, parent, NULL, image, clicked, x, y, w, h)
    land_widget_spinbutton_interface_initialize()
    self->vt = land_widget_spinbutton_interface

    land_widget_theme_initialize(self)
    land_widget_theme_set_minimum_size_for_image(self, image)

    return self

def land_widget_spin_initialize(LandWidget *base,
    LandWidget *parent, float val, float min, float max, float step,
    void (*modified)(LandWidget *self), int x, int y, int w, int h):
    land_widget_spin_interface_initialize()

    land_widget_hbox_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_spin_interface
    
    LandWidgetSpin *spin = LAND_WIDGET_SPIN(base)
    spin->min = min
    spin->max = max
    spin->step = step

    LandWidget *edit = land_widget_edit_new(base, "", modified, 0, 0, 1, 1)
    land_widget_edit_align_right(edit, true)
    LandWidget *spinner = land_widget_vbox_new(base, 0, 0, 1, 1)
    LandWidgetSpinButton *buttonup = LAND_WIDGET_SPINBUTTON(
        land_widget_spinbutton_new(spinner, image_up, NULL, 0, 0, 1, 1))
    buttonup->initial_delay = 0.25
    buttonup->rate = 0.1
    buttonup->spin = base
    buttonup->dir = 1

    LandWidgetSpinButton *buttondown = LAND_WIDGET_SPINBUTTON(
        land_widget_spinbutton_new(spinner, image_down, NULL, 0, 0, 1, 1))
    buttondown->initial_delay = 0.25
    buttondown->rate = 0.1
    buttondown->spin = base
    buttondown->dir = -1

    land_widget_layout_set_shrinking(LAND_WIDGET(buttonup), 1, 0)
    land_widget_layout_set_shrinking(LAND_WIDGET(buttondown), 1, 0)
    land_widget_layout_set_shrinking(spinner, 1, 0)

    land_widget_layout_set_expanding(edit, 1, 0)
    land_widget_spin_set_value(base, val)
    
    land_widget_layout_set_expanding(base, 1, 0)

    land_widget_theme_initialize(base)
    if parent: land_widget_layout(parent)

LandWidget *def land_widget_spin_new(LandWidget *parent,
    float val, float min, float max, float step,
    void (*modified)(LandWidget *self), int x, int y, int w, int h):
    LandWidgetSpin *spin
    land_alloc(spin)
    LandWidget *self = (LandWidget *)spin

    land_widget_spin_initialize(self,
        parent, val, min, max, step, modified, x, y, w, h)
    return self

def land_widget_spin_set_value(LandWidget *base, float val):
    LandWidgetSpin *spin = LAND_WIDGET_SPIN(base)
    if (val < spin->min) val = spin->min
    if (val > spin->max && spin->max > spin->min) val = spin->max
    LandListItem *item = LAND_WIDGET_CONTAINER(base)->children->first
    LandWidget *edit = LAND_WIDGET(item->data)
    char text[256]
    char format[256]
    if spin->step > 0 && spin->step < 1:
        uszprintf(format, sizeof format, "%%.%df", (int)(0.9 - log10(spin->step)))
    else:
        ustrzcpy(format, sizeof format, "%.0f")
    uszprintf(text, sizeof text, format, val)
    land_widget_edit_set_text(edit, text)

def land_widget_spin_set_minimum_text(LandWidget *base, char const *text):
    LandListItem *item = LAND_WIDGET_CONTAINER(base)->children->first
    LandWidget *edit = LAND_WIDGET(item->data)
    land_widget_theme_set_minimum_size_for_text(edit, text)

float def land_widget_spin_get_value(LandWidget *base):
    LandWidgetSpin *spin = LAND_WIDGET_SPIN(base)
    LandListItem *item = LAND_WIDGET_CONTAINER(base)->children->first
    LandWidget *edit = LAND_WIDGET(item->data)
    char const *text = land_widget_edit_get_text(edit)
    float val = strtod(text, NULL)
    if val < spin->min: val = spin->min
    if val > spin->max and spin->max > spin->min: val = spin->max
    return val

static def spinning(LandWidget *widget, float amount):
    LandWidget *super = widget->parent->parent
    float val = land_widget_spin_get_value(super)
    LandWidgetSpin *spin = LAND_WIDGET_SPIN(super)
    val += amount
    land_widget_spin_set_value(LAND_WIDGET(spin), val)
    updated(super)

def land_widget_spinbutton_mouse_tick(LandWidget *base):
    LandWidgetSpinButton *spinbutton = LAND_WIDGET_SPINBUTTON(base)
    LandWidgetSpin *spin = LAND_WIDGET_SPIN(spinbutton->spin)
    if (land_mouse_delta_b() & 1):
        if (land_mouse_b() & 1):
            spinbutton->seconds = land_get_time()
            spinbutton->delay = spinbutton->initial_delay
            spinbutton->count = 0
            spinbutton->step = spin->step * spinbutton->dir
            spinning(base, spinbutton->step)
    else:
        if (land_mouse_b() & 1):
            double seconds = land_get_time()
            if seconds > spinbutton->seconds + spinbutton->delay:
                spinbutton->seconds = seconds
                spinbutton->delay = spinbutton->rate
                spinbutton->count++
                if spinbutton->count >= 20:
                    spinbutton->step *= 10
                    spinbutton->count = 0

                spinning(base, spinbutton->step)

def land_widget_spinbutton_interface_initialize():
    if land_widget_spinbutton_interface: return

    land_widget_button_interface_initialize()
    land_widget_spinbutton_interface = land_widget_copy_interface(
        land_widget_button_interface, "spinbutton")
    land_widget_spinbutton_interface->id |= LAND_WIDGET_ID_SPINBUTTON
    land_widget_spinbutton_interface->mouse_tick = land_widget_spinbutton_mouse_tick

def land_widget_spin_interface_initialize():
    if land_widget_spin_interface: return
    land_widget_hbox_interface_initialize()
    land_widget_spin_interface = land_widget_copy_interface(
        land_widget_hbox_interface, "spin")
    land_widget_spin_interface->id |= LAND_WIDGET_ID_SPIN
    
    image_up = land_image_create(2, 2)
    image_down = land_image_create(2, 2)
