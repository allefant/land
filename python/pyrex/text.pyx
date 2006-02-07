cdef extern from "land.h":
    struct LandFont:
        pass
    LandFont *land_font_load(char *filename, float size)
    void land_set_font(LandFont *self)
    void land_text_pos(float x, float y)
    float land_text_x_pos()
    float land_text_y_pos()
    float land_text_x()
    float land_text_y()
    float land_text_width()
    float land_text_height()
    int land_text_state()
    int land_font_height(LandFont *self)
    void land_text_off()
    void land_text_on()
    void land_print(char *text, ...)
    void land_print_right(char *text, ...)
    void land_print_center(char *text, ...)
    void land_write(char *text, ...)
    void land_write_right(char *text, ...)
    void land_write_center(char *text, ...)

    void land_color(float r, float g, float b, float a)
    void land_set_glyphkeeper(int onoff)

cdef class Font:
    cdef LandFont *wrapped
    def __init__(self, *args):
        if len(args) == 2:
            text = args[0]
            self.wrapped = land_font_load(text, args[1])
        else:
            raise land.LandException("Check parameters to Font().")

    def set_pos(self, x, y):
        land_text_pos(x, y)
    def get_x(self): return land_text_x()
    def get_y(self):  return land_text_y()
    def x(self): return land_text_x()
    def y(self):  return land_text_y()
    def get_width(self): return land_text_width()
    def get_height(self): return land_text_height()
    def width(self): return land_text_width()
    def height(self): return land_text_height()
    def get_state(self): return land_text_state()
    def off(self): land_text_off()
    def on(self): land_text_on()
    def get_font_height(self): return land_font_height(self.wrapped)
    def write(self, str, right = False, centered = False, color = None,
        pos = None, x = None, y = None):

        if type(str) == unicode:
            str = str.encode("utf8")

        if color:
            land_color(color[0], color[1], color[2], color[3])

        if pos or (x != None) or (y != None):
            if pos: x, y = pos
            if x == None: x = land_text_x_pos()
            if y == None: y = land_text_y_pos()
            land_text_pos(x, y)

        land_set_font(self.wrapped)
        cdef char *s
        s = str
        if right:
            land_print_right("%s", s)
        elif centered:
            land_print_center("%s", s)
        else:
            land_print("%s", s)
def glyphkeeper(onoff):
    land_set_glyphkeeper(onoff)
