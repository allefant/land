import traceback, sys

cdef extern void land_quit()

cdef _init(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    try:
        self.init()
    except:
        traceback.print_exc()
        land_quit()

cdef _enter(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    try:
        self.enter()
    except:
        traceback.print_exc()
        land_quit()

cdef _tick(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    try:
        self.tick()
    except:
        traceback.print_exc()
        land_quit()

cdef _draw(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    try:
        self.draw()
    except:
        traceback.print_exc()
        land_quit()

cdef _leave(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    try:
        self.leave()
    except:
        traceback.print_exc()
        land_quit()

cdef _destroy(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    try:
        self.destroy()
    except:
        traceback.print_exc()
        land_quit()

cdef class Runner:
    def __new__(self, *args):
        land_runner_initialize(&self.wrapped.wrapped, "python runner",
            <void *>_init,
            <void *>_enter,
            <void *>_tick,
            <void *>_draw,
            <void *>_leave,
            <void *>_destroy,)
        self.wrapped.self = <void *>self
        land_runner_register(&self.wrapped.wrapped)

    def init(self):
        pass

    def enter(self):
        pass

    def tick(self):
        pass

    def draw(self):
        pass

    def leave(self):
        pass

    def destroy(self):
        pass

