import land/land, base

enum LandWidgetThemeFlags:
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
    LandWidgetThemeFlags flags
    int bl, bt, br, bb # border to cut out of the image 
    int minw, minh
    LandWidget *anchor # for the ALIGNED modes 
    int ox, oy # extra offset into the anchor widget 
    float r, g, b, a # text color 
    LandFont *font
    unsigned int transparent : 1

    # Offset to contents - by default this is the same as the border, but it can
    # be smaller (contents are drawn over the border) or larger (there's some
    # additional padding of contents).
    int il, it, ir, ib
    int hgap, vgap # If there are child elements, space between them.
    
    LandWidgetThemeElement *selected
    LandWidgetTheme *theme

class LandWidgetTheme:
    char *name
    char *prefix
    char *suffix
    # TODO: instead of a list, use a mapping from the widget names. 
    LandList *elements

static LandWidgetTheme *default_theme

LandWidgetTheme *def land_widget_theme_default():
    return default_theme

def land_widget_theme_set_default(LandWidgetTheme *self):
    default_theme = self

# Given two sizes, return an offset <= 0, so when texturing the area of size1
# with a texture of size size2, the center will be aligned.
# 
static inline int def centered_offset (int size1, int size2):
    int center1, center2, o

    if !size1 || !size2:
        return 0
    center1 = size1 / 2
    center2 = size2 / 2
    o = (center1 - center2) % size2
    if o > 0:
        o -= size2
    return o

static inline def _masked_non_stretched_blit(LandImage *s, int sx, int sy, int w, int h,
                           int dx, int dy, int _, int __):
    land_image_clip(s, sx, sy, sx + w, sy + h)
    land_image_draw(s, dx - sx, dy - sy)

static inline def _masked_stretched_blit(LandImage *s, int sx, int sy, int w, int h,
                           int dx, int dy, int dw, int dh):
    land_image_clip(s, sx, sy, sx + w, sy + h)
    land_image_draw_scaled(s, dx - sx, dy - sy, (float)dw / w,
        (float)dh / h)

enum COLUMN_TYPE:
    COLUMN_CENTER = 1
    COLUMN_STRETCH
    COLUMN_LEFT
    COLUMN_MIDDLE
    COLUMN_RIGHT

# Draw a column of pattern pat (at bx, width bw) into the given rectangle.
# 
static inline def blit_column(LandWidgetThemeElement *pat, int bx, int bw,
    int x, int y, int w, int h, int skip_middle):
    int oy
    int j
    int bh = land_image_height(pat->bmp)
    int bm = bh - pat->bt - pat->bb

    void (*bfunc)(LandImage *, int, int, int, int, int, int, int, int)
    bfunc = _masked_non_stretched_blit

    if bm < 1:
        return

    if pat->flags & ALIGN_V:
        # TODO: anchor
        oy = (y / bm) * bm - y

    else:
        oy = centered_offset (h, bm)

    if w != bw:
        bfunc = _masked_stretched_blit

    if pat->flags & CENTER_V:
        bfunc (pat->bmp, bx, 0, bw, land_image_height(pat->bmp), x,
               y + h / 2 - land_image_height(pat->bmp) / 2, w, land_image_height(pat->bmp))

    elif pat->flags & STRETCH_V:
        _masked_stretched_blit(pat->bmp, bx, 0, bw, land_image_height(pat->bmp), x, y, w, h)

    else: # pattern :
        # .....bx......
        #  ___ ___ ___
        # |   |   |   | .bt
        # |___|___|___|
        # |   |   |   | bm
        # |___|___|___|
        # |   |   |   | .bb
        # |___|___|___|
        #   
        int bt = pat->bt
        int bb = pat->bb
        if bt + bb > h:
            bt = h / 2
            bb = h - bt

        # top 
        if bt && y + bt >= _land_active_display->clip_y1:
            land_clip_push()
            land_clip_intersect(0, y, land_display_width(),  min(y + h, y + bt))
            bfunc(pat->bmp, bx, 0, bw, bt, x, y, w, bt)
            land_clip_pop()

        # middle 
        if h - pat->bt - pat->bb > 0 && !skip_middle:
            land_clip_push()
            land_clip_intersect(0, min(y + h, y + pat->bt), land_display_width(), max(y, y + h - pat->bb))
            int start = max(0, (_land_active_display->clip_y1 - (y + oy)) / bm)
            start = y + oy + start * bm
            int end = min(_land_active_display->clip_y2, y + h)
            for j = start; j < end; j += bm:
                bfunc(pat->bmp, bx, pat->bt, bw, bm, x, j, w, bm)

            land_clip_pop()

        # bottom 
        if bb && y + h - bb < _land_active_display->clip_y2:
            land_clip_push()
            land_clip_intersect(0, max(y, y + h - bb), land_display_width(), y + h)
            bfunc(pat->bmp, bx, land_image_height(pat->bmp) - bb, bw, bb, x,
                y + h - bb, w, bb)
            land_clip_pop()



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
static def draw_bitmap(LandWidgetThemeElement *pat, int x, int y, int w, int h,
    int skip_middle):
    int i

    int bw = land_image_width(pat->bmp)
    int bm = bw - pat->bl - pat->br

    if w < 1 || h < 1 || bm < 1:
        return

    land_clip_push()
    land_clip_intersect(x, y, x + w, y + h)
    
    if pat->flags & CENTER_H:
        blit_column(pat, 0, bw, x + w / 2 - bw / 2, y, bw, h, 0)

    elif pat->flags & STRETCH_H:
        blit_column(pat, 0, bw, x, y, w, h, 0)

    else: # pattern
        int ox
        if pat->flags & ALIGN_H:
            # TODO: anchor
            ox = (x / bm) * bm - x

        else:
            ox = centered_offset(w, bm)

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
         

        int bl = pat->bl
        int br = pat->br
        if bl + br > w:
            bl = w / 2
            br = w - bl

        # left 
        if bl && x + bl >= _land_active_display->clip_x1:
            land_clip_push()
            land_clip_intersect(x, 0, min(x + w, x + bl), land_display_height())
            blit_column(pat, 0, bl, x, y, bl, h, 0)
            land_clip_pop()
            
        # middle 
        if w - pat->bl - pat->br > 0:
            land_clip_push()
            land_clip_intersect(min(x + w, x + pat->bl), 0, max(x, x + w - pat->br),
                land_display_height())

            int start = max(0, (_land_active_display->clip_x1 - (x + ox)) / bm)
            start = x + ox + start * bm
            int end = min(_land_active_display->clip_x2, x + w - pat->br)
            for i = start; i < end; i += bm:
                blit_column(pat, pat->bl, bm, i, y, bm, h, skip_middle)

            land_clip_pop()

        # right 
        if br && x + w - br < _land_active_display->clip_x2:
            land_clip_push()
            land_clip_intersect(max(x, x + w - br), 0, x + w, land_display_height())
            blit_column(pat, bw - br, br, x + w - br, y, br, h, 0)
            land_clip_pop()


    land_clip_pop()

static def read_int_arg(int argc, LandArray *argv, int *a, int *val):
    (*a)++
    if *a < argc:
        LandBuffer *buf = land_array_get_nth(argv, *a)
        char *arg = land_buffer_finish(buf)
        *val = strtoul(arg, NULL, 0)

LandWidgetThemeElement *def land_widget_theme_element_new(
    struct LandWidgetTheme *theme, char const *name, *argline):
    LandWidgetThemeElement *self
    land_alloc(self)
    land_log_message("New theme element %s: %s\n", name, argline)

    self->name = land_strdup(name)
    self->a = 1
    self->minw = 4
    self->minh = 4
    self->font = land_font_current()
    self->theme = theme

    LandBuffer *argbuf = land_buffer_new()
    land_buffer_cat(argbuf, argline)
    land_buffer_strip(argbuf, " ")
    LandArray *argv = land_buffer_split(argbuf, ' ')
    land_buffer_del(argbuf)
    int argc = land_array_count(argv)
    LandImage *img = NULL
    if argc:
        char name[2048]
        LandBuffer *buf = land_array_get_nth(argv, 0)
        char *arg = land_buffer_finish(buf)
        uszprintf(name, sizeof name, "%s%s%s", theme->prefix, arg, theme->suffix)
        land_free(arg)
        img = land_image_load(name)
        if img:
            for int a = 1; a < argc; a++:
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
                    self->bmp = land_image_new_from(img, cx, cy, cw, ch)

                elif not strcmp (arg, "halign"):
                    self->flags |= ALIGN_H

                elif (!strcmp (arg, "valign")):
                    self->flags |= ALIGN_V

                elif (!strcmp (arg, "min")):
                    read_int_arg(argc, argv, &a, &self->minw)
                    read_int_arg(argc, argv, &a, &self->minh)

                elif (!strcmp (arg, "border")):
                    read_int_arg(argc, argv, &a, &self->bl)
                    read_int_arg(argc, argv, &a, &self->bt)
                    read_int_arg(argc, argv, &a, &self->br)
                    read_int_arg(argc, argv, &a, &self->bb)
                    # FIXME: should not overwrite a previous inner
                    self->il = self->bl
                    self->it = self->bt
                    self->ir = self->br
                    self->ib = self->bb
                
                elif (!strcmp (arg, "inner")):
                    read_int_arg(argc, argv, &a, &self->il)
                    read_int_arg(argc, argv, &a, &self->it)
                    read_int_arg(argc, argv, &a, &self->ir)
                    read_int_arg(argc, argv, &a, &self->ib)

                elif (!strcmp (arg, "gap")):
                    read_int_arg(argc, argv, &a, &self->hgap)
                    read_int_arg(argc, argv, &a, &self->vgap)

                elif (!ustrcmp(arg, "color")):
                    int c = 0
                    read_int_arg(argc, argv, &a, &c)
                    self->a = (c & 255) / 255.0; c >>= 8
                    self->b = (c & 255) / 255.0; c >>= 8
                    self->g = (c & 255) / 255.0; c >>= 8
                    self->r = (c & 255) / 255.0; c >>= 8

                elif (!ustrcmp(arg, "transparent")):
                    self->transparent = 1
                
                land_free(arg)

            if !self->bmp:
                self->bmp = land_image_new_from(img, 0, 0,
                    land_image_width(img), land_image_height(img))
            land_log_message("element: %d x %d, %d/%d/%d/%d %.1f/%.1f/%.1f/%.1f\n",
                land_image_width(self->bmp), land_image_height(self->bmp),
                self->bl, self->bt, self->br, self->bb,
                self->r, self->g, self->b, self->a)

        else:
            land_log_message("element: Error: %s not found!\n", name)

    land_array_destroy(argv)
    if img: land_image_destroy(img)

    return self

LandWidgetTheme *def land_widget_theme_new(char const *filename):
    LandWidgetTheme *self
    land_alloc(self)

    LandIniFile *config = land_ini_read(filename)

    LandBuffer *prefix = land_buffer_new()
    land_buffer_cat(prefix, filename)
    int slash = land_buffer_rfind(prefix, '/')
    if slash >= 0:
        land_buffer_set_length(prefix, slash + 1)
    else:
        land_buffer_set_length(prefix, 0)
    
    land_buffer_cat(prefix, land_ini_get_string(config, "agup.cfg", "prefix", ""))

    self->name = land_strdup(land_ini_get_string(config, "agup.cfg", "name", ""))
    self->prefix = land_buffer_finish(prefix)
    self->suffix = land_strdup(land_ini_get_string(config, "agup.cfg", "suffix", ""))

    int n = land_ini_get_number_of_entries(config, "agup.cfg/elements")
    for int i = 0; i < n; i++:
        char const *v = land_init_get_nth_entry(config,
            "agup.cfg/elements", i)
        char const *k = land_ini_get_string(config, "agup.cfg/elements",
            v, "")
        LandWidgetThemeElement *elem = land_widget_theme_element_new(
            self, v, k)
        land_add_list_data(&self->elements, elem)

    land_ini_destroy(config)

    return self

def land_widget_theme_destroy(LandWidgetTheme *self):
    LandListItem *item
    for item = self->elements->first; item; item = item->next:
        LandWidgetThemeElement *elem = item->data
        land_free(elem->name)
        land_image_destroy(elem->bmp)
        land_free(elem)

    land_list_destroy(self->elements)
    land_free(self->name)
    land_free(self->prefix)
    land_free(self->suffix)
    land_free(self)

static LandWidgetThemeElement *def find_element(LandList *list, char const *name):
    LandListItem *item = list->first
    while item:
        LandWidgetThemeElement *elem = item->data
        if not ustrcmp(elem->name, name):
            return elem
        item = item->next

    return None

LandWidgetThemeElement *def land_widget_theme_find_element(
    LandWidgetTheme *theme, LandWidget *widget):
    if not theme:
        return None
    LandWidgetThemeElement *element
    
    element = find_element(theme->elements, widget->vt->name)
    if not element:
        element = find_element(theme->elements, "base")

    if not element->selected:
        char name[1024]
        # First, try to find "widget.selected"
        ustrzcpy(name, sizeof name, widget->vt->name)
        ustrzcat(name, sizeof name, ".selected")
        element->selected = find_element(theme->elements, name)
        # If it doesn't exist, try "base.selected"
        if not element->selected:
            ustrzcpy(name, sizeof name, element->name)
            ustrzcat(name, sizeof name, ".selected")
            element->selected = find_element(theme->elements, name)
        # If that doesn't exist as well, use the same as non-selected.
        if not element->selected:
            element->selected = element

    return element

LandWidgetThemeElement *def land_widget_theme_element(LandWidget *self):
    if self->selected: return self->element->selected
    return self->element

def land_widget_theme_draw(LandWidget *self):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    if self->no_decoration: return
    if element->transparent: return

    draw_bitmap(element, self->box.x, self->box.y, self->box.w, self->box.h,
        self->only_border)

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
    self->inner_w = w
    self->inner_h = h
    w += element->il + element->ir
    h += element->it + element->ib
    if element->minw > w: w = element->minw
    if element->minh > h: h = element->minh
    if self->outer_w > w: w = self->outer_w
    if self->outer_h > h: h = self->outer_h
    land_widget_layout_set_minimum_size(self, w, h)

def land_widget_theme_set_minimum_size_for_text(LandWidget *self,
    char const *text):
    LandWidgetThemeElement *element = land_widget_theme_element(self)
    if not element: return
    land_font_set(element->font)
    int w = land_text_get_width(text)
    int h = land_font_height(land_font_current())
    land_widget_theme_set_minimum_size_for_contents(self, w, h)

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
    if not self->element: return
    self->element = land_widget_theme_find_element(self->element->theme, self)
    # FIXME: Do this in land_widget_base_initialize instead
    self->outer_w = self->box.min_width
    self->outer_h = self->box.min_height
    int w = self->box.min_width - self->element->il - self->element->ir
    int h = self->box.min_height - self->element->it - self->element->ib
    land_widget_theme_set_minimum_size_for_contents(self, w, h)

def land_widget_theme_update(LandWidget *self):
    """
    Adjust the widget's theme to its class (widgets all start off as "base"
    otherwise).
    """
    if not self->element: return
    self->element = land_widget_theme_find_element(self->element->theme, self)
    land_widget_theme_set_minimum_size_for_contents(self,
        self->inner_w, self->inner_h)

static def _theme_recurse(LandWidget *self, LandWidgetTheme *theme):
    if not self->element: return
    self->element = land_widget_theme_find_element(theme, self)
    land_widget_theme_set_minimum_size_for_contents(self,
        self->inner_w, self->inner_h)

    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *c = (void *)self
        LandListItem *i = c->children->first
        while i:
            LandWidget *w = i->data
            _theme_recurse(w, theme)
             i = i->next

static def _layout_recurse(LandWidget *self, LandWidgetTheme *theme):
    if land_widget_is(self, LAND_WIDGET_ID_CONTAINER):
        LandWidgetContainer *c = (void *)self
        LandListItem *i = c->children->first
        while i:
            LandWidget *w = i->data
            _layout_recurse(w, theme)
             i = i->next
        if self->parent and (self->parent->box.flags & GUL_NO_LAYOUT):
            land_widget_layout(self)

def land_widget_theme_apply(LandWidget *self, LandWidgetTheme *theme):
    """
    Applies the given theme to the widget and all its children.
    """
    _theme_recurse(self, theme)
    _layout_recurse(self, theme)
    land_widget_layout(self)
