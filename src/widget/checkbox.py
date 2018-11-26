import scrolling

class LandWidgetCheckBox:
    """
    This widget has two children. One is a button which changes text depending
    on if the checkbox is checked or not.
    """
    LandWidgetContainer super
    char *checkbox_selected
    char *checkbox_unselected

    bool *value
    
static import land/land

global LandWidgetInterface *land_widget_checkbox_interface
global LandWidgetInterface *land_widget_checkbox_button_interface
global LandWidgetInterface *land_widget_checkbox_description_interface

macro LAND_WIDGET_CHECKBOX(widget) ((LandWidgetCheckBox *)
    land_widget_check(widget, LAND_WIDGET_ID_CHECKBOX, __FILE__, __LINE__))

def _cb_clicked(LandWidget *widget):
    LandWidgetCheckBox *cb = LAND_WIDGET_CHECKBOX(widget->parent)
    if widget->selected:
        widget->selected = 0
        land_widget_button_replace_text(widget, cb->checkbox_unselected)
    else:
        widget->selected = 1
        land_widget_button_replace_text(widget, cb->checkbox_selected)
    if cb.value:
        *cb.value = widget.selected

def land_widget_checkbox_initialize(LandWidget *base,
    LandWidget *parent,
    char const *checkbox_selected,
    char const *checkbox_unselected,
    char const *text,
    bool *b,
    int x, int y, int w, int h):

    LandWidgetCheckBox *self = (void *)base
    self.checkbox_selected = land_strdup(checkbox_selected)
    self.checkbox_unselected = land_strdup(checkbox_unselected)
    self.value = b

    land_widget_checkbox_interface_initialize()

    land_widget_container_initialize(base, parent, x, y, w, h)
    base->vt = land_widget_checkbox_interface

    LandWidget *checkbox = land_widget_button_new(base, checkbox_selected,
        _cb_clicked, 0, 0, 8, 8)
    checkbox->vt = land_widget_checkbox_button_interface
    land_widget_theme_initialize(checkbox)
    land_widget_layout_set_shrinking(checkbox, 1, 0)
    LandWidget *description = land_widget_text_new(base, text, 0, 0, 0, 8, 8)
    description->vt = land_widget_checkbox_description_interface
    land_widget_theme_initialize(description)

    land_widget_layout_set_grid(base, 2, 1)
    land_widget_layout_set_grid_position(checkbox, 0, 0)
    land_widget_layout_set_grid_position(description, 1, 0)

    land_widget_theme_initialize(base)
    land_widget_layout_enable(base) # container disables it for some reason
    land_widget_layout(base)

    if b and *b:
        land_widget_button_replace_text(checkbox, checkbox_selected)
        checkbox.selected = True
    else:
        land_widget_button_replace_text(checkbox, checkbox_unselected)

def land_widget_checkbox_new(LandWidget *parent,
    char const *checkbox_selected,
    char const *checkbox_unselected,
    char const *text,
    int x, int y, int w, int h) -> LandWidget *:
    
    LandWidgetCheckBox *self; land_alloc(self)

    land_widget_checkbox_initialize((LandWidget *)self,
        parent, checkbox_selected, checkbox_unselected, text, None,
        x, y, w, h)

    return (LandWidget *)self

def land_widget_checkbox_new_boolean(LandWidget *parent,
    char const *checkbox_selected,
    char const *checkbox_unselected,
    char const *text,
    bool *b,
    int x, int y, int w, int h) -> LandWidget *:
    
    LandWidgetCheckBox *self; land_alloc(self)

    land_widget_checkbox_initialize((LandWidget *)self,
        parent, checkbox_selected, checkbox_unselected, text, b, x, y, w, h)

    return (LandWidget *)self


def land_widget_checkbox_is_checked(LandWidget *self) -> bool:
    return land_widget_container_child(self)->selected

def land_widget_checkbox_set(LandWidget *base, bool checked):
    LandWidget *box = land_widget_container_child((void *)LAND_WIDGET_CONTAINER(base))
    bool was = box.selected
    if was != checked:
        # _cb_clicked will change the state for us!
        _cb_clicked(box)
    
def land_widget_checkbox_interface_initialize():
    if land_widget_checkbox_interface: return
    land_widget_container_interface_initialize()
    land_widget_checkbox_interface = land_widget_copy_interface(
        land_widget_container_interface, "checkbox")
    land_widget_checkbox_interface->id |= LAND_WIDGET_ID_CHECKBOX
    land_widget_checkbox_interface->destroy = land_widget_checkbox_destroy

    land_widget_button_interface_initialize()
    land_widget_checkbox_button_interface = land_widget_copy_interface(
        land_widget_button_interface, "checkbox.box")
    land_widget_checkbox_description_interface = land_widget_copy_interface(
        land_widget_button_interface, "checkbox.description")

def land_widget_checkbox_destroy(LandWidget *base):
    LandWidgetCheckBox *self = LAND_WIDGET_CHECKBOX(base)
    if self.checkbox_selected: land_free(self->checkbox_selected)
    if self.checkbox_unselected: land_free(self->checkbox_unselected)
    land_widget_container_destroy(base)
