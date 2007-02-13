import base, ../image, ../animation

# TODO: It's time to split this up into simple buttons, image buttons, and
# text widgets.
class LandWidgetButton:
    """
    A button.
    """
    LandWidget super
    unsigned int xalign : 2 # 0 = left, 1 = right, 2 = center
    unsigned int yalign : 2 # 0 = top, 1 = bottom, 2 = center
    int xshift
    int yshift
    # 0 = single line
    # 1 = multi line
    # 2 = multi line with word wrapping
    int multiline : 2
    LandAnimation *animation
    LandImage *image
    char *text
    LandArray *lines
    void (*clicked)(LandWidget *self)
    void (*rclicked)(LandWidget *self)

macro LAND_WIDGET_BUTTON(widget) ((LandWidgetButton *)
    land_widget_check(widget, LAND_WIDGET_ID_BUTTON, __FILE__, __LINE__))

static import land

global LandWidgetInterface *land_widget_button_interface

def land_widget_button_draw(LandWidget *base):
    LandWidgetButton *self = LAND_WIDGET_BUTTON(base)
    land_widget_box_draw(base)

    if not base->dont_clip:
        float l, t, r, b
        land_widget_inner_extents(base, &l, &t, &r, &b)
        land_clip_push()
        land_clip_intersect(l, t, r, b)

    if self->image:
        int w = land_image_width(self->image)
        int h = land_image_height(self->image)

        float x = base->box.x + base->element->il
        switch self->xalign:
            case 1: x = base->box.x + base->box.w - base->element->ir - w; break
            case 2: x = base->box.x + (base->box.w -
                base->element->il - base->element->ir - w) * 0.5; break

        float y = base->box.y + base->element->it
        switch self->yalign:
            case 1: y = base->box.y + base->box.h - base->element->ib - h; break
            case 2: y = base->box.y + (base->box.h - base->element->it -
                base->element->ib - h) * 0.5; break

        x += self->xshift
        y += self->yshift
        land_image_draw(self->image, x + self->image->x, y + self->image->y)

    if self->animation:
        float fps = self->animation->fps
        int i = (int)(land_get_time() * fps) % self->animation->frames->count
        LandImage *image = land_animation_get_frame(self->animation, i)
        int w = land_image_width(image)
        int h = land_image_height(image)
        float x = base->box.x + base->element->il
        switch self->xalign:
            case 1: x = base->box.x + base->box.w - base->element->ir - w; break
            case 2: x = base->box.x + (base->box.w -
                base->element->il - base->element->ir - w) * 0.5; break

        float y = base->box.y + base->element->it
        switch self->yalign:
            case 1: y = base->box.y + base->box.h - base->element->ib - h; break
            case 2: y = base->box.y + (base->box.h -
                base->element->it - base->element->ib - h) * 0.5; break

        x += self->xshift
        y += self->yshift
        land_image_draw(image, x + image->x, y + image->y)

    if self->text:
        int x, y = base->box.y + base->element->it
        land_widget_theme_color(base)
        land_widget_theme_font(base)
        int th = land_font_height(land_font_current())
        switch self->yalign:
            case 1: y = base->box.y + base->box.h - base->element->ib - th; break
            case 2: y = base->box.y + (base->box.h - base->element->it +
                base->element->ib - th) / 2; break

        y += self->yshift
        switch self->xalign:
            case 0:
                x = base->box.x + base->element->il
                x += self->xshift
                land_text_pos(x, y)
                if self->multiline:
                    land_print_lines(self->lines, 0)
                else:
                    land_print("%s", self->text)
                break
            case 1:
                x = base->box.x + base->box.w - base->element->ir
                x += self->xshift
                land_text_pos(x, y)
                if self->multiline:
                    land_print_lines(self->lines, 1)
                else:
                    land_print_right("%s", self->text)
                break
            case 2:
                x = base->box.x + (base->box.w - base->element->il +
                    base->element->ir) / 2
                x += self->xshift
                land_text_pos(x, y)
                if self->multiline:
                    land_print_lines(self->lines, 2)
                else:
                    land_print_center("%s", self->text)
                break

    if !base->dont_clip:
        land_clip_pop()

def land_widget_button_size(LandWidget *base, float dx, dy):
    if not (dx or dy): return
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base)
    land_widget_button_multiline(base, button->multiline)

def land_widget_button_mouse_tick(LandWidget *base):
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base)
    if button->clicked:
        if land_mouse_delta_b() & 1:
            if land_mouse_b() & 1:
                button->clicked(base)
    if button->rclicked:
        if land_mouse_delta_b() & 2:
            if land_mouse_b() & 2:
                button->rclicked(base)


def land_widget_button_initialize(LandWidget *base,
    LandWidget *parent, char const *text,
    LandImage *image,
    void (*clicked)(LandWidget *self), int x, int y, int w, int h):
    
    #FIXME: Inhibit layout changes of parent, they make no sense before we
    # set the layout below

    land_widget_base_initialize(base, parent, x, y, w, h)
    land_widget_button_interface_initialize()
    base->vt = land_widget_button_interface
    land_widget_theme_initialize(base)
    LandWidgetButton *self = LAND_WIDGET_BUTTON(base)
    if text:
        self->text = land_strdup(text)
        land_widget_theme_set_minimum_size_for_text(base, text)
        w = MAX(w, base->box.min_width)
        h = MAX(h, base->box.min_height)
        land_widget_layout_set_minimum_size(base, w, h)

    if image:
        self->image = image
        land_widget_theme_set_minimum_size_for_image(base, image)

    self->clicked = clicked
    
    if parent: land_widget_layout(parent)

LandWidget *def land_widget_button_new(LandWidget *parent, char const *text,
    void (*clicked)(LandWidget *self), int x, int y, int w, int h):

    LandWidgetButton *button
    land_alloc(button)
    LandWidget *self = (LandWidget *)button

    land_widget_button_initialize(self,
        parent, text, NULL, clicked, x, y, w, h)

    return self

LandWidget *def land_widget_button_new_with_image(LandWidget *parent,
    char const *text, LandImage *image,
    void (*clicked)(LandWidget *self), int x, int y, int w, int h):
    LandWidgetButton *button
    land_alloc(button)
    LandWidget *self = (LandWidget *)button

    land_widget_button_initialize(self,
        parent, text, image, clicked, x, y, w, h)

    return self

LandWidget *def land_widget_button_new_with_animation(LandWidget *parent,
    char const *text, LandAnimation *animation,
    void (*clicked)(LandWidget *self), int x, int y, int w, int h):
    LandWidgetButton *button
    land_alloc(button)
    LandWidget *self = (LandWidget *)button

    land_widget_button_initialize(self,
        parent, text, NULL, clicked, x, y, w, h)
    button->animation = animation

    return self

LandWidget *def land_widget_text_initialize(LandWidget *self,
    LandWidget *parent, char const *text, int multiline, x, y, w, h):

    land_widget_button_initialize(self,
        parent, multiline ? None : text, NULL, NULL, x, y, w, h)
    self->no_decoration = 1

    land_widget_theme_initialize(self)

    if multiline:
        land_widget_button_multiline(self, multiline)
        land_widget_button_set_text(self, text)
    else:
        land_widget_layout(parent)

    return self

LandWidget *def land_widget_text_new(LandWidget *parent, char const *text,
    int multiline, x, y, w, h):
    LandWidgetButton *button
    land_alloc(button)
    LandWidget *self = (LandWidget *)button

    land_widget_text_initialize(self, parent, text, multiline, x, y, w, h)

    return self

static int def _linedelcb(void *item, void *data):
    land_free(item)
    return 0

def land_widget_button_set_text(LandWidget *base, char const *text):
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base)
    if button->text: land_free(button->text)
    button->text = None
    if text:
        button->text = land_strdup(text)
        if button->multiline:
            land_widget_button_multiline(base, button->multiline)
        else:
            land_widget_theme_set_minimum_size_for_text(base, text)
    if base->parent: land_widget_layout(base->parent)

def land_widget_button_multiline(LandWidget *self, int style):
    """
    If style is 0, the text of this widget is a single line. No newline
    characters are allowed.
    If style is 1, the text can have multiple lines.
    If style is 2, the text can have multiple lines, and long lines are
    word wrapped.
    """
    LandWidgetButton *button = LAND_WIDGET_BUTTON(self)
    button->multiline = style
    if button->lines:
        land_array_for_each(button->lines, _linedelcb, None)
        land_array_destroy(button->lines)
    if style and button->text:
        float x, y, w, h
        land_widget_inner(self, &x, &y, &w, &h)
        if style == 1:
            button->lines = land_text_splitlines(button->text)
        else:
            button->lines = land_wordwrap_text(w, 0, button->text)
        float ww, wh
        land_wordwrap_extents(&ww, &wh)
        if ww - w > 0.1:
            # We can not wrap up text shorter than the single longest word
            # (which can't be split). So if our first try of wrapping was not
            # sucessful because it was too narrow, we wrap it again with a
            # width guaranteed to succeed.
            land_array_for_each(button->lines, _linedelcb, None)
            land_array_destroy(button->lines)
            button->lines = land_wordwrap_text(ww, 0, button->text)
            land_wordwrap_extents(&ww, &wh)
        land_widget_theme_set_minimum_size_for_contents(self, ww, wh)

def land_widget_button_align(LandWidget *self, int x, int y):
    """
    0 = left/top
    1 = right/bottom
    2 = center
    """
    LandWidgetButton *button = LAND_WIDGET_BUTTON(self)
    button->xalign = x
    button->yalign = y
    
def land_widget_button_shift(LandWidget *self, int x, int y):
    LandWidgetButton *button = LAND_WIDGET_BUTTON(self)
    button->xshift = x
    button->yshift = y

def land_widget_button_get_inner_size(LandWidget *self, float *w, float *h):
    pass

def land_widget_button_interface_initialize():
    if land_widget_button_interface: return

    land_widget_button_interface = land_widget_copy_interface(
        land_widget_base_interface, "button")
    land_widget_button_interface->id |= LAND_WIDGET_ID_BUTTON
    land_widget_button_interface->destroy = land_widget_button_destroy
    land_widget_button_interface->draw = land_widget_button_draw
    land_widget_button_interface->mouse_tick = land_widget_button_mouse_tick
    land_widget_button_interface->get_inner_size =\
        land_widget_button_get_inner_size
    land_widget_button_interface->size = land_widget_button_size

def land_widget_button_destroy(LandWidget *base):
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base)
    if button->text: land_free(button->text)
    if button->lines:
        land_array_for_each(button->lines, _linedelcb, None)
        land_array_destroy(button->lines)
    land_widget_base_destroy(base)