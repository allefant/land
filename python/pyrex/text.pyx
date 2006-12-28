cdef extern from "land.h":
    struct LandFont:
        pass
    LandFont *land_font_load(char *filename, float size)
    void land_font_set(LandFont *self)
    void land_font_destroy(LandFont *self)
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
    int land_text_get_char_offset(char *str, int nth)
    int land_text_get_width(char *str)
    int land_text_get_char_index(char *str, int x)

    void land_color(float r, float g, float b, float a)
    
    char *strdup(char *)

cdef class Font:
    cdef LandFont *wrapped
    cdef char *name
    cdef int size
    def __init__(self, *args):
        cdef char *s
        if len(args) == 2:
            self.wrapped = land_font_load(args[0], args[1])
            s = args[0]
            self.name = s
            self.name = strdup(self.name)
            self.size = args[1]
        else:
            raise land.LandException("Check parameters to Font().")

    def __del__(self):
        print "Reference count of font", self, "is 0."
        land_font_destroy(self.wrapped)

    def set_pos(self, x, y):
        land_text_pos(x, y)
    def get_x_pos(self): return land_text_x_pos()
    def get_y_pos(self):  return land_text_y_pos()
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
    def clear(self):
        land_font_destroy(self.wrapped)
        self.wrapped = NULL
    def reload(self):
        if self.wrapped: land_font_destroy(self.wrapped)
        self.wrapped = land_font_load(self.name, self.size)
    def calculate_string_width(self, str):
        land_font_set(self.wrapped)
        return land_text_get_width(str)
    def calculate_offset(self, str, n):
        land_font_set(self.wrapped)
        if type(str) == unicode:
            str = str.encode("utf8")
        return land_text_get_char_offset(str, n)
    def calculate_index(self, str, x):
        land_font_set(self.wrapped)
        if type(str) == unicode:
            str = str.encode("utf8")
        return land_text_get_char_index(str, x)

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

        land_font_set(self.wrapped)
        cdef char *s
        s = str
        if right:
            land_print_right("%s", s)
        elif centered:
            land_print_center("%s", s)
        else:
            land_print("%s", s)
