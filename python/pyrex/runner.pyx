cdef _init(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    self.init()

cdef _enter(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    self.enter()

cdef _tick(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    self.tick()

cdef _draw(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    self.draw()

cdef _leave(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    self.leave()

cdef _destroy(LandRunnerPyrex *wrapped):
    self = <object>wrapped.self
    self.destroy()

cdef class Runner:
    def __new__(self):
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

