import land/land, base

static enum LandWidgetThemeFlags:
    TILE_H = 0
    TILE_V = 0
    STRETCH_H = 1
    STRETCH_V = 2
    CENTER_H = 4
    CENTER_V = 8
    ALIGN_H = 16
    ALIGN_V = 32

# data for a single GUI bitmap
class LandWidgetThemeElement:
    char *name
    LandImage *bmp
    int flags
    int bl, bt, br, bb # border to cut out of the image
    int minw, minh
    LandWidget *anchor # for the ALIGNED modes 
    int ox, oy # extra offset into the anchor widget 
    float r, g, b, a # text color 
    LandFont *font
    bool transparent

    # Offset to contents - by default this is the same as the border, but it can
    # be smaller (contents are drawn over the border) or larger (there's some
    # additional padding of contents).
    int il, it, ir, ib
    int hgap, vgap # If there are child elements, space between them.
    
    LandWidgetThemeElement *selected
    LandWidgetThemeElement *disabled
    LandWidgetTheme *theme

class LandWidgetTheme:
    char *name
    char *prefix
    char *suffix
    # TODO: instead of a list, use a mapping from the widget names. 
    LandList *elements

    float border_scale

static LandWidgetTheme *default_theme

def land_widget_theme_default() -> LandWidgetTheme *:
    return default_theme

def land_widget_theme_set_default(LandWidgetTheme *self):
    default_theme = self

# Given two sizes, return an offset <= 0, so when texturing the area of size1
# with a texture of size size2, the center will be aligned.
# 
static inline def centered_offset (int size1, int size2) -> int:
    int center1, center2, o

    if not size1 or not size2:
        return 0
    center1 = size1 / 2
    center2 = size2 / 2
    o = (center1 - center2) % size2
    if o > 0:
        o -= size2
    return o

def _part(LandImage *image, float sx, sy, sw, sh, dx, dy, dw, dh):
    land_image_draw_partial_into(image, sx, sy, sw, sh, dx, dy, dw, dh)

# Draw the pattern pat into the specified rectangle, following the contained
# tiling, stretching, alignement and bordering constraints.
#
# Borders align depending on their type:
#
# NW N NE
# W  C  E
# SW S SW
#
# The remaining texture is aligned with its center to the center, except if the
# align flag is set. In this case, it will be aligned NW to the anchor.
#
# 
def _draw_bitmap(LandWidgetThemeElement *pat, int x, y, w, h,
        bool skip_middle):
    LandWidgetTheme *t = pat.theme

    int bl = pat.bl * t.border_scale
    int bt = pat.bt * t.border_scale
    int br = pat.br * t.border_scale
    int bb = pat.bb * t.border_scale
    int iw = land_image_width(pat.bmp)
    int ih = land_image_height(pat.bmp)

    #
    # |    bw     |
    # |.bl|bm |.br|
    #  ___ ___ ___
    # |   |   |   |
    # |___|___|___|
    # |   |   |   |
    # |___|___|___|
    # |   |   |   |
    # |___|___|___|
    #
    float imw = iw - pat.bl - pat.br
    float imh = ih - pat.bb - pat.bt
    float x2 = x + w - br
    float y2 = y + h - bb
    float w2 = w - bl - br
    float h2 = h - bb - bt

    _part(pat.bmp, 0, 0, pat.bl, pat.bt, x, y, bl, bt)
    _part(pat.bmp, pat.bl, 0, imw, pat.bt, x + bl, y, w2, bt)
    _part(pat.bmp, iw - pat.br, 0, pat.br, pat.bt, x2, y, br, bt)

    _part(pat.bmp, 0, pat.bt, pat.bl, imh, x, y + bt, bl, h2)
    if not skip_middle:
        _part(pat.bmp, pat.bl, pat.bt, imw, imh, x + bl, y + bt, w2, h2)
    _part(pat.bmp, iw - pat.br, pat.bt, pat.br, imh, x2, y + bt, br, h2)
    
    _part(pat.bmp, 0, ih - pat.bb, pat.bl, pat.bb, x, y2, bl, bb)
    _part(pat.bmp, pat.bl, ih - pat.bb, imw, pat.bb, x + bl, y2, w2, bb)
    _part(pat.bmp, iw - pat.br, ih - pat.bb, pat.br, pat.bb, x2, y2, br, bb)

static def read_int_arg(int argc, LandArray *argv, int *a, int *val):
    (*a)++
    if *a < argc:
        LandBuffer *buf = land_array_get_nth(argv, *a)
        char *arg = land_buffer_finish(buf)
        *val = strtoul(arg, NULL, 0)
        land_free(arg)

def land_widget_theme_element_new(
    struct LandWidgetTheme *theme, char const *name, *argline) -> LandWidgetThemeElement *:
    LandWidgetThemeElement *self
    land_alloc(self)

    land_log_message("element %s\n", name)

    self.name = land_strdup(name)
    self.a = 1
    self.minw = 4
    self.minh = 4
    self.font = land_font_current()
    self.theme = theme

    LandBuffer *argbuf = land_buffer_new()
    land_buffer_cat(argbuf, argline)
    land_buffer_strip(argbuf, " ")
    LandArray *argv = land_buffer_split(argbuf, " ")
    land_buffer_del(argbuf)
    int argc = land_array_count(argv)
    land_log_message("%s has %d tokens\n", argline, argc)
    
    LandImage *img = NULL
    if argc:
        char iname[2048]
        LandBuffer *buf = land_array_get_nth(argv, 0)
        char *arg = land_buffer_finish(buf)
        snprintf(iname, sizeof iname, "%s%s%s", theme->prefix, arg, theme->suffix)
        land_free(arg)
        img = land_image_load_cached(iname)
        if img:
            for int a = 1 while a < argc with a++:
                buf = land_array_get_nth(argv, a)
                arg = land_buffer_finish(buf)
                if not strcmp (arg, "cut"):
                    int cx = 0, cy = 0, cw = 0, ch = 0
                    read_int_arg(argc, argv, &a, &cx)
                    read_int_arg(argc, argv, &a, &cy)
                    read_int_arg(argc, argv, &a, &cw)
                    read_int_arg(argc, argv, &a, &ch)
                    

                    if cw <= 0:
                        cw += land_image_width(img)
                    if ch <= 0:
                        ch += land_image_height(img)

                    self.bmp = land_image_new_from(img, cx, cy, cw, ch)
                    

                elif not strcmp (arg, "halign"):
                    self.flags |= ALIGN_H

                elif (not strcmp (arg, "valign")):
                    self.flags |= ALIGN_V

                elif (not strcmp (arg, "min")):
                    read_int_arg(argc, argv, &a, &self.minw)
                    read_int_arg(argc, argv, &a, &self.minh)

                elif (not strcmp (arg, "border")):
                    read_int_arg(argc, argv, &a, &self.bl)
                    read_int_arg(argc, argv, &a, &self.bt)
                    read_int_arg(argc, argv, &a, &self.br)
                    read_int_arg(argc, argv, &a, &self.bb)
                    # FIXME: should not overwrite a previous inner
                    self.il = self->bl
                    self.it = self->bt
                    self.ir = self->br
                    self.ib = self->bb
                
                elif (not strcmp (arg, "inner")):
                    read_int_arg(argc, argv, &a, &self.il)
                    read_int_arg(argc, argv, &a, &self.it)
                    read_int_arg(argc, argv, &a, &self.ir)
                    read_int_arg(argc, argv, &a, &self.ib)

                elif not strcmp (arg, "gap"):
                    read_int_arg(argc, argv, &a, &self.hgap)
                    read_int_arg(argc, argv, &a, &self.vgap)

                elif not strcmp(arg, "color"):
                    int c = 0
                    read_int_arg(argc, argv, &a, &c)
                    self.a = (c & 255) / 255.0; c >>= 8
                    self.b = (c & 255) / 255.0; c >>= 8
                    self.g = (c & 255) / 255.0; c >>= 8
                    self.r = (c & 255) / 255.0; c >>= 8

                elif (not strcmp(arg, "transparent")):
                    self.transparent = 1
                
                land_free(arg)

            if not self.bmp:
                self.bmp = land_image_new_from(img, 0, 0,
                    land_image_width(img), land_image_height(img))
            land_log_message("element %s: %d x %d, %d/%d/%d/%d %.1f/%.1f/%.1f/%.1f\n",
                name,
                land_image_width(self.bmp), land_image_height(self->bmp),
                self.bl, self->bt, self->br, self->bb,
                self.r, self->g, self->b, self->a)

        else:
            land_log_message("element: Error: %s not found!\n", name)

    land_array_destroy(argv)
    if img: land_image_destroy(img)

    return self

def land_widget_theme_new(char const *filename) -> LandWidgetTheme *:
    """
    Load a new theme and make it the default theme.
    """
    LandWidgetTheme *self
    land_alloc(self)

    self.border_scale = 1

    LandIniFile *config = land_ini_read(filename)

    LandBuffer *prefix = land_buffer_new()
    land_buffer_cat(prefix, filename)
    int slash = land_buffer_rfind(prefix, '/')
    if slash >= 0:
        land_buffer_set_length(prefix, slash + 1)
    else:
        land_buffer_set_length(prefix, 0)
    
    land_buffer_cat(prefix, land_ini_get_string(config, "agup.cfg", "prefix", ""))

    self.name = land_strdup(land_ini_get_string(config, "agup.cfg", "name", ""))
    self.prefix = land_buffer_finish(prefix)
    self.suffix = land_strdup(land_ini_get_string(config, "agup.cfg", "suffix", ""))

    int n = land_ini_get_number_of_entries(config, "agup.cfg/elements")
    land_log_message("theme has %d elements\n", n)
    for int i = 0 while i < n with i++:
        char const *v = land_ini_get_nth_entry(config,
            "agup.cfg/elements", i)
        char const *k = land_ini_get_string(config, "agup.cfg/elements",
            v, "")
        LandWidgetThemeElement *elem = land_widget_theme_element_new(
            self, v, k)
        land_add_list_data(&self.elements, elem)

    land_ini_destroy(config)

    land_widget_theme_set_default(self)
    return self

def land_widget_theme_destroy(LandWidgetTheme *self):
    LandListItem *item
    if self.elements:
        for item = self.elements->first while item with item = item->next:
            LandWidgetThemeElement *elem = item->data
            land_free(elem->name)
            land_image_destroy(elem->bmp)
            land_free(elem)

        land_list_destroy(self.elements)
    land_free(self.name)
    land_free(self.prefix)
    land_free(self.suffix)
    land_free(self)

static def find_element(LandList *list, char const *name) -> LandWidgetThemeElement *:
    if not list:
        return None
    LandListItem *item = list->first
    while item:
        LandWidgetThemeElement *elem = item->data
        if not strcmp(elem->name, name):
            return elem
        item = item->next

    return None

def land_widget_theme_find_element(
    LandWidgetTheme *theme, LandWidget *widget) -> LandWidgetThemeElement *:
    if not theme:
        return None
    LandWidgetThemeElement *element
    
    element = find_element(theme->elements, widget->vt->name)
    if not element:
        element = find_element(theme->elements, "base")
    if not element:
        land_alloc(element)
        element->name = land_strdup("")
        element->theme = theme

    if not element->selected:
        char name[1024]
        # First, try to find "widget.selected"
        strncpy(name, widget->vt->name, sizeof name - 1)
        strncat(name, ".selected", sizeof name - strlen(name) - 1)
        element->selected = find_element(theme->elements, name)
        # If it doesn't exist, try "base.selected"
        if not element->selected:
            strncpy(name, element->name, sizeof name - 1)
            strncat(name, ".selected", sizeof name - strlen(name) - 1)
            element->selected = find_element(theme->elements, name)
        # If that doesn't exist as well, use the same as non-selected.
        if not element->selected:
            element->selected = element
    
    if not element->disabled:
        char name[1024]
        # First, try to find "widget.disabled"
        strncpy(name, widget->vt->name, sizeof name - 1)
        strncat(name, ".disabled", sizeof name - strlen(name) - 1)
        element->disabled = find_element(theme->elements, name)
        if not element->disabled:
            element->disabled = element

    return element

def land_widget_theme_element(LandWidget *self) -> LandWidgetThemeElement *:
    if self.selected: return self->element->selected
    if self.disabled: return self->element->disabled
    return self.element

def land_widget_theme_draw(LandWidget *self):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    if self.no_decoration: return
    if element->transparent: return

    #if land_completely_clipped():
    #    print("warning: widget clipped %s", land_widget_info_string(self))

    _draw_bitmap(element, self.box.x, self->box.y, self->box.w, self->box.h,
        self.only_border)

def land_widget_theme_color(LandWidget *self):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    land_color(element->r, element->g, element->b, element->a)

def land_widget_theme_font(LandWidget *self):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    land_font_set(element->font)

def land_widget_theme_set_minimum_size_for_contents(LandWidget *self,
    int w, int h):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    self.inner_w = w
    self.inner_h = h
    w += element->il + element->ir
    h += element->it + element->ib
    if w < element.minw: w = element.minw
    if h < element.minh: h = element.minh
    land_widget_layout_set_minimum_size(self, w, h)

    # TODO: not sure this is the right place
    if self.box.w < w: self.box.w = w
    if self.box.h < h: self.box.h = h

def land_widget_theme_set_minimum_size_for_text(LandWidget *self,
    char const *text):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    land_font_set(element->font)
    (float w, h) = land_text_get_extents(text) # not line height (or we would cut off over/under parts)
    land_widget_theme_set_minimum_size_for_contents(self, (int)w, (int)h)

def land_widget_theme_set_minimum_width_for_text(LandWidget *self, str text):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    land_font_set(element->font)
    int w = land_text_get_width(text)
    self.inner_w = w
    w += element->il + element->ir
    if w < element.minw: w = element.minw
    land_widget_layout_set_minimum_width(self, w)

def land_widget_theme_set_minimum_size_for_image(LandWidget *self,
    LandImage *image):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    int w = land_image_width(image)
    int h = land_image_height(image)
    land_widget_theme_set_minimum_size_for_contents(self, w, h)

def land_widget_theme_initialize(LandWidget *self):
    """
    Initialize theming of an item. Must only called once at item creation,
    as it also calculates the minimum size.
    """
    if not self.element: return
    self.element = land_widget_theme_find_element(self->element->theme, self)
    int w = self.box.min_width - self->element->il - self->element->ir
    int h = self.box.min_height - self->element->it - self->element->ib
    land_widget_theme_set_minimum_size_for_contents(self, w, h)

def land_widget_theme_update(LandWidget *self):
    """
    Adjust the widget's theme to its class (widgets all start off as "base"
    otherwise).
    """
    if not self.element: return
    self.element = land_widget_theme_find_element(self->element->theme, self)
    land_widget_theme_set_minimum_size_for_contents(self,
        self.inner_w, self->inner_h)

static def _theme_recurse(LandWidget *self, LandWidgetTheme *theme):
    if not self.element: return
    self.element = land_widget_theme_find_element(theme, self)

    land_widget_theme_set_minimum_size_for_contents(self,
        self.inner_w, self->inner_h)

    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *c = (void *)self
        LandListItem *i = c->children ? c->children->first : None
        while i:
            LandWidget *w = i->data
            _theme_recurse(w, theme)
            i = i->next

static def _layout_recurse(LandWidget *self, LandWidgetTheme *theme):
    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *c = (void *)self
        LandListItem *i = c->children ? c->children->first : None
        while i:
            LandWidget *w = i->data
            _layout_recurse(w, theme)
            i = i->next

        # TODO: what is this for?
        if self.parent and (self->parent->box.flags & GUL_NO_LAYOUT):
            land_widget_layout(self)

def land_widget_theme_apply(LandWidget *self, LandWidgetTheme *theme):
    """
    Applies the given theme to the widget and all its children.
    """
    _theme_recurse(self, theme)
    _layout_recurse(self, theme)
    land_widget_layout(self)

def land_widget_theme_change_font(LandWidgetTheme *theme):
    for LandWidgetThemeElement *element in LandList *theme.elements:
        element.font = land_font_current()
        if element.selected:
            element.selected.font = land_font_current()
        if element.disabled:
            element.disabled.font = land_font_current()

def land_widget_debug_theme(LandWidget *w, int indentation):
    LandWidgetThemeElement *e = w.element

    for int i in range(indentation):
        printf("  ");
    if e.transparent:
        print("%s transparent", e.name)
    else:
        print("%s %dx%d", e.name, land_image_width(e.bmp), land_image_height(e.bmp))

    if land_widget_is(w, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *c = LAND_WIDGET_CONTAINER(w)
        if c.children:
            for LandWidget *child in LandList *c.children:
                land_widget_debug_theme(child, indentation + 1)
    
def land_widget_theme_set_stretch(LandWidgetTheme *self, bool hor, ver):
    for LandWidgetThemeElement *element in LandList *self.elements:
        if hor: element.flags |= STRETCH_H
        else: element.flags &= ~STRETCH_H
        if ver: element.flags |= STRETCH_V
        else: element.flags &= ~STRETCH_V
