import scrolling

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

LandWidget *def land_widget_scrolling_text_new(LandWidget *parent,
    char const *text, int wordwrap, int x, int y, int w, int h):
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
    # FIXME: isn't this by the button itself?
    #land_widget_button_multiline(button, LAND_WIDGET_BUTTON(button)->multiline)

    land_widget_scrolling_size(widget, dx, dy)

def land_widget_scrolling_text_interface_initialize():
    if land_widget_scrolling_text_interface: return
    land_widget_scrolling_interface_initialize()
    land_widget_scrolling_text_interface = land_widget_copy_interface(
        land_widget_scrolling_interface, "scrolling")
    land_widget_scrolling_text_interface->id |= LAND_WIDGET_ID_SCROLLING_TEXT
    land_widget_scrolling_text_interface->size = land_widget_scrolling_text_size

