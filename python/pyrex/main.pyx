cimport runner

cdef extern from "land.h":
    void land_init()
    void land_quit()
    void land_set_frequency(int f)
    void land_set_display_parameters(int w, int h, int bpp, int hz, int flags)
    void land_set_initial_runner(runner.LandRunner *runner)
    int land_main()
    double land_get_time()
    int land_closebutton()

def init():
    land_init()

def quit():
    land_quit()

def set_frequency(f):
    land_set_frequency(f)

def set_display_parameters(w, h, bpp, hz, flags):
    land_set_display_parameters(w, h, bpp, hz, flags)

def set_initial_runner(runner.Runner runner):
    land_set_initial_runner(&runner.wrapped.wrapped)

def main():
    land_main()

def get_time():
    return land_get_time()

def closebutton():
    return land_closebutton()
