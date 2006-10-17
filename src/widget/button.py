import base, ../image, ../animation

class LandWidgetButton:
    LandWidget super
    unsigned int xalign : 2 # 0 = left, 1 = right, 2 = center
    unsigned int yalign : 2 # 0 = top, 1 = bottom, 2 = center
    int xshift
    int yshift
    LandAnimation *animation
    LandImage *image
    char *text
    void (*clicked)(LandWidget *self)
    void (*rclicked)(LandWidget *self)

macro LAND_WIDGET_BUTTON(widget) ((LandWidgetButton *)
    land_widget_check(widget, LAND_WIDGET_ID_BUTTON, __FILE__, __LINE__))

static import land

global LandWidgetInterface *land_widget_button_interface

def land_widget_button_draw(LandWidget *base):
    LandWidgetButton *self = LAND_WIDGET_BUTTON(base)
    if !base->no_decoration:
        land_widget_box_draw(base)

    if !base->dont_clip:
        int l = base->box.x + base->box.il
        int t = base->box.y + base->box.it
        int r = base->box.x + base->box.w - base->box.ir
        int b = base->box.y + base->box.h - base->box.ib
        land_clip_push()
        land_clip_intersect(l, t, r, b)

    if self->image:
        int w = land_image_width(self->image)
        int h = land_image_height(self->image)
        float x = base->box.x + base->box.il
        switch self->xalign:
            case 1: x = base->box.x + base->box.w - base->box.ir - w; break
            case 2: x = base->box.x + (base->box.w -
                base->box.il - base->box.ir - w) * 0.5; break

        float y = base->box.y + base->box.it
        switch self->yalign:
            case 1: y = base->box.y + base->box.h - base->box.ib - h; break
            case 2: y = base->box.y + (base->box.h - base->box.it -
                base->box.ib - h) * 0.5; break

        x += self->xshift
        y += self->yshift
        land_image_draw(self->image, x + self->image->x, y + self->image->y)

    if self->animation:
        float fps = self->animation->fps
        int i = (int)(land_get_time() * fps) % self->animation->frames->count
        LandImage *image = land_animation_get_frame(self->animation, i)
        int w = land_image_width(image)
        int h = land_image_height(image)
        float x = base->box.x + base->box.il
        switch self->xalign:
            case 1: x = base->box.x + base->box.w - base->box.ir - w; break
            case 2: x = base->box.x + (base->box.w -
                base->box.il - base->box.ir - w) * 0.5; break

        float y = base->box.y + base->box.it
        switch self->yalign:
            case 1: y = base->box.y + base->box.h - base->box.ib - h; break
            case 2: y = base->box.y + (base->box.h -
                base->box.it - base->box.ib - h) * 0.5; break

        x += self->xshift
        y += self->yshift
        land_image_draw(image, x + image->x, y + image->y)

    if self->text:
        int x, y = base->box.y + base->box.it
        land_widget_theme_color(base)
        land_widget_theme_font(base)
        int th = land_font_height(land_font_current())
        switch self->yalign:
            case 1: y = base->box.y + base->box.h - base->box.ib - th; break
            case 2: y = base->box.y + (base->box.h - base->box.it +
                base->box.ib - th) / 2; break

        y += self->yshift
        switch self->xalign:
            case 0:
                x = base->box.x + base->box.il
                x += self->xshift
                land_text_pos(x, y)
                land_print(self->text)
                break
            case 1:
                x = base->box.x + base->box.w - base->box.ir
                x += self->xshift
                land_text_pos(x, y)
                land_print_right(self->text)
                break
            case 2:
                x = base->box.x + (base->box.w - base->box.il +
                    base->box.ir) / 2
                x += self->xshift
                land_text_pos(x, y)
                land_print_center(self->text)
                break


    if !base->dont_clip:
        land_clip_pop()

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

def land_widget_button_destroy(LandWidget *base):
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base)
    land_free(button->text)
    land_widget_base_destroy(base)

def land_widget_button_initialize(LandWidget *base,
    LandWidget *parent, char const *text,
    LandImage *image,
    void (*clicked)(LandWidget *self), int x, int y, int w, int h):
    
    #FIXME: Inhibit layout changes of parent, they make no sense before we
    # set the layout below

    land_widget_base_initialize(base, parent, x, y, w, h)
    land_widget_button_interface_initialize()
    base->vt = land_widget_button_interface
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
    
    land_widget_theme_layout_border(base)
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

LandWidget *def land_widget_text_new(LandWidget *parent, char const *text,
    int x, int y, int w, int h):
    LandWidgetButton *button
    land_alloc(button)
    LandWidget *self = (LandWidget *)button

    land_widget_button_initialize(self,
        parent, text, NULL, NULL, x, y, w, h)
    self->no_decoration = 1
    land_widget_theme_layout_border(self)
    land_widget_layout(parent)

    return self

def land_widget_button_set_text(LandWidget *base, char const *text):
    LandWidgetButton *button = LAND_WIDGET_BUTTON(base)
    land_free(button->text)
    button->text = land_strdup(text)
    land_widget_theme_set_minimum_size_for_text(base, text)

def land_widget_button_align(LandWidget *self, int x, int y):
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
    if (land_widget_button_interface) return

    land_widget_button_interface = land_widget_copy_interface(
        land_widget_base_interface, "button")
    land_widget_button_interface->id |= LAND_WIDGET_ID_BUTTON
    land_widget_button_interface->destroy = land_widget_button_destroy
    land_widget_button_interface->draw = land_widget_button_draw
    land_widget_button_interface->mouse_tick = land_widget_button_mouse_tick
    land_widget_button_interface->get_inner_size =\
        land_widget_button_get_inner_size
