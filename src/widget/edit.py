import global stdbool
import base

# A simple, one-line edit box. 
class LandWidgetEdit:
    LandWidget super
    char *text
    int bytes # How many bytes are reserved for text.
    int scroll
    int cursor
    int last_key
    int last_char
    bool align_right
    void (*modified)(LandWidget *self)

macro LAND_WIDGET_EDIT(widget) ((LandWidgetEdit *) land_widget_check(widget,
    LAND_WIDGET_ID_EDIT, __FILE__, __LINE__))

static import land/land

# FIXME: should come from theme
# How fast the cursor changes between visible and invisible.
# 0 = blink never
# 1 = blink every second
# 2 = blink twice a second
# 
static double land_widget_cursor_blink_rate = 2

LandWidgetInterface *land_widget_edit_interface

static int def get_x_offset(LandWidget *base):
    int x = base->box.x + base->element->il
    LandWidgetEdit *self = LAND_WIDGET_EDIT(base)
    if self->align_right:
        int w = land_text_get_width(self->text)
        x = base->box.x + base->box.w - base->element->r - w
    return x

def land_widget_edit_draw(LandWidget *base):
    LandWidgetEdit *self = LAND_WIDGET_EDIT(base)
    if !base->no_decoration:
        land_widget_box_draw(base)

    if !base->dont_clip:
        int l = base->box.x + base->element->il
        int t = base->box.y + base->element->it
        int r = base->box.x + base->box.w - base->element->r
        int b = base->box.y + base->box.h - base->element->ib
        land_clip_push()
        land_clip_intersect(l, t, r, b)

    if self->text:
        int x = get_x_offset(base)
        int y = base->box.y + base->element->it
        land_widget_theme_color(base)

        land_text_pos(x, y)
        land_print(self->text)

        if base->got_keyboard:
            double pos = land_get_time() * land_widget_cursor_blink_rate
            pos -= floor(pos)
            if pos < 0.5:
                int cx = land_text_get_char_offset(self->text, self->cursor)
                land_line(x + cx, y, x + cx, base->box.y + base->box.h -
                    base->element->ib)

    if !base->dont_clip:
        land_clip_pop()

def land_widget_edit_mouse_tick(LandWidget *base):
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(base)

    if (land_mouse_delta_b() & 1):
        if (land_mouse_b() & 1):
            base->want_focus = 1
            int x = land_mouse_x() - get_x_offset(base)
            edit->cursor = land_text_get_char_index(edit->text, x)

static macro M if (edit->modified) edit->modified(base)
def land_widget_edit_keyboard_tick(LandWidget *base):
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(base)
    while not land_keybuffer_empty():
        int k, u
        land_keybuffer_next(&k, &u)
        edit->last_key = k
        edit->last_char = u
        if u && u > 31 && u != 127:
            edit->bytes += ucwidth(u)
            edit->text = land_realloc(edit->text, edit->bytes)
            uinsert(edit->text, edit->cursor, u)
            edit->cursor++
            M
        else:
            int l = ustrlen(edit->text)
            if k == LandKeyLeft:
                edit->cursor--
                if (edit->cursor < 0) edit->cursor = 0

            elif k == LandKeyRight:
                edit->cursor++
                if (edit->cursor > l) edit->cursor = l

            elif k == LandKeyDelete:
                if edit->cursor < l:
                    uremove(edit->text, edit->cursor)
                    edit->bytes = ustrsizez(edit->text)
                    edit->text = land_realloc(edit->text, edit->bytes)
                    M
            elif k == LandKeyBackspace:
                if edit->cursor > 0:
                    edit->cursor--
                    uremove(edit->text, edit->cursor)
                    edit->bytes = ustrsizez(edit->text)
                    edit->text = land_realloc(edit->text, edit->bytes)
                    M
            elif k == LandKeyHome:
                edit->cursor = 0

            elif k == LandKeyEnd:
                edit->cursor = l

def land_widget_edit_destroy(LandWidget *base):
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(base)
    if (edit->text) land_free(edit->text)
    land_widget_base_destroy(base)

def land_widget_edit_initialize(LandWidget *base,
    LandWidget *parent, char const *text,
    void (*modified)(LandWidget *self), int x, int y, int w, int h):
    land_widget_base_initialize(base, parent, x, y, w, h)
    land_widget_edit_interface_initialize()
    base->vt = land_widget_edit_interface
    LandWidgetEdit *self = LAND_WIDGET_EDIT(base)
    if text:
        self->text = land_strdup(text)
        self->bytes = ustrsizez(self->text)
        land_widget_theme_set_minimum_size_for_text(base, text)
        if (base->box.min_width < w) base->box.min_width = w

    self->modified = modified

LandWidget *def land_widget_edit_new(LandWidget *parent, char const *text,
    void (*modified)(LandWidget *self), int x, int y, int w, int h):
    LandWidgetEdit *edit
    land_alloc(edit)
    LandWidget *self = (LandWidget *)edit

    land_widget_edit_initialize(self,
        parent, text, modified, x, y, w, h)

    land_widget_theme_initialize(self)
    land_widget_layout(parent)

    return self

def land_widget_edit_set_text(LandWidget *base, char const *text):
    """
    Changes the text of the edit widget to a copy of the given string. The
    string itself is not touched nor referenced - if you allocated it, you
    can immediately free it after this function returns.
    """
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(base)
    land_free(edit->text)
    edit->text = land_strdup(text)
    edit->bytes = ustrsizez(edit->text)
    land_widget_theme_set_minimum_size_for_text(base, text)
    if edit->cursor > ustrlen(text):
        edit->cursor = ustrlen(text)

def land_widget_edit_align_right(LandWidget *base, bool yes):
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(base)
    edit->align_right = yes

char const *def land_widget_edit_get_text(LandWidget *base):
    LandWidgetEdit *edit = LAND_WIDGET_EDIT(base)
    return edit->text

def land_widget_edit_interface_initialize():
    if land_widget_edit_interface: return

    land_widget_edit_interface = land_widget_copy_interface(
        land_widget_base_interface, "edit")
    land_widget_edit_interface->id |= LAND_WIDGET_ID_EDIT
    land_widget_edit_interface->destroy = land_widget_edit_destroy
    land_widget_edit_interface->draw = land_widget_edit_draw
    land_widget_edit_interface->mouse_tick = land_widget_edit_mouse_tick
    land_widget_edit_interface->keyboard_tick = land_widget_edit_keyboard_tick
