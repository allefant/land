cdef extern from "land.h":
    cdef struct LandRunner:
        void *init
        void *enter
        void *tick
        void *draw
        void *leave
        void *destroy

    void land_runner_register(LandRunner *self)
    void land_runner_initialize(LandRunner *self, char *name,
        void *init, void *enter, void *tick, void *draw, void *leave, void *destroy)
    LandRunner *land_runner_new(char *name,
        void *init, void *enter, void *tick, void *draw, void *leave, void *destroy)
    void land_runner_init_all()
    void land_runner_switch_active(LandRunner *self)
    void land_runner_enter_active()
    void land_runner_tick_active()
    void land_runner_draw_active()
    void land_runner_leave_active()
    void land_runner_destroy_all()

cdef struct LandRunnerPyrex:
    LandRunner wrapped
    void *self

cdef class Runner:
    cdef LandRunnerPyrex wrapped
