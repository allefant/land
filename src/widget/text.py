import scrolling
import land.font

class LandWidgetScrollingText:
    """
    A scrolling text widget. You can also put text into normal scrolling widget
    to get the same effect, but this widget already handles some extra stuff
    like word wrapping. (For non-wrapped text it is exactly the same as a
    normal scrolling widget with a text child.)
    """
    LandWidgetScrolling super

static import land/land

global LandWidgetInterface *land_widget_scrolling_text_interface

def land_widget_scrolling_text_initialize(LandWidget *base,
    LandWidget *parent, char const *text, int wordwrap,
    int x, int y, int w, int h):
    
    #FIXME: Inhibit layout changes of parent, they make no sense before we
    # set the layout below

    land_widget_scrolling_initialize(base, parent, x, y, w, h)

    land_widget_scrolling_text_interface_initialize()

    base->vt = land_widget_scrolling_text_interface

    land_widget_theme_initialize(base)

    LandWidget *container = land_widget_scrolling_get_container(base)
    float cx, cy, cw, ch
    land_widget_inner(container, &cx, &cy, &cw, &ch)
    land_widget_text_new(base, text, wordwrap, cx, cy, cw, ch)

def land_widget_scrolling_text_new(LandWidget *parent,
    char const *text, int wordwrap, int x, int y, int w, int h) -> LandWidget *:
    LandWidgetScrollingText *self
    land_alloc(self)
    LandWidget *widget = (LandWidget *)self

    land_widget_scrolling_text_initialize(widget,
        parent, text, wordwrap, x, y, w, h)

    return widget

def land_widget_scrolling_text_size(LandWidget *widget, float dx, float dy):
    if not (dx or dy): return
    LandWidget *container = land_widget_scrolling_get_container(widget)
    float cx, cy, cw, ch
    land_widget_layout(widget)
    land_widget_inner(container, &cx, &cy, &cw, &ch)
    LandWidget *button = land_widget_container_child(container)
    land_widget_size(button, cw - button->box.w, ch - button->box.h)
    land_widget_scrolling_size(widget, dx, dy)

def land_widget_scrolling_text_layout_changed(LandWidget *widget):
    if widget->box.w != widget->box.ow or widget->box.h != widget->box.oh:
        land_widget_scrolling_layout_changed(widget)
        LandWidget *container = land_widget_scrolling_get_container(widget)
        LandWidget *button = land_widget_container_child(container)
        float cx, cy, cw, ch
        land_widget_inner(container, &cx, &cy, &cw, &ch)
        land_widget_move_to(button, cx, cy)
        land_widget_set_size_permanent(button, cw, ch)

def land_widget_scrolling_text_interface_initialize():
    if land_widget_scrolling_text_interface: return
    land_widget_scrolling_interface_initialize()
    land_widget_scrolling_text_interface = land_widget_copy_interface(
        land_widget_scrolling_interface, "scrolling")
    land_widget_scrolling_text_interface->id |= LAND_WIDGET_ID_SCROLLING_TEXT
    land_widget_scrolling_text_interface->size = land_widget_scrolling_text_size
    land_widget_scrolling_text_interface->layout_changed = land_widget_scrolling_text_layout_changed

def land_widget_scrolling_text_get_text_widget(LandWidget *widget) -> LandWidget*:
    return land_widget_scrolling_get_child(widget)

def land_widget_scrolling_text_add(LandWidget *widget, str text, LandColor color, LandFont *font):
    """
    Call to add text spans to the scrolling text.
    Note: when done, call land_widget_scrolling_text_update.
    """
    auto button = land_widget_scrolling_text_get_text_widget(widget)
    land_widget_button_span(button, text, color, font)
    
def land_widget_scrolling_text_update(LandWidget *widget):
    """
    Call this after adding text spans to update line breaks and scroll
    bars of the text.
    """
    auto text = land_widget_scrolling_text_get_text_widget(widget)
    land_widget_button_update_multiline(text, 2)
    land_widget_scrolling_update(widget)
