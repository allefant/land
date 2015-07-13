import list

class LandRunner:
    char *name
    int inited
    bool allocated
    void (*init)(LandRunner *self)
    void (*enter)(LandRunner *self)
    void (*tick)(LandRunner *self)
    void (*draw)(LandRunner *self)
    void (*leave)(LandRunner *self)
    void (*destroy)(LandRunner *self)

static import log, mem, global stdlib, string

static LandList *runners

static LandRunner *active_runner

def land_runner_register(LandRunner *self):
    land_log_message("land_runner_register \"%s\"\n", self.name)
    land_add_list_data(&runners, self)

def land_runner_initialize(LandRunner *self, char const *name, void (*init)(LandRunner *self),
    void (*enter)(LandRunner *self), void (*tick)(LandRunner *self),
    void (*draw)(LandRunner *self), void (*leave)(LandRunner *self), void (*destroy)(LandRunner *self)):
    self.name = land_strdup(name)
    self.init = init
    self.enter = enter
    self.tick = tick
    self.draw = draw
    self.leave = leave
    self.destroy = destroy

def land_runner_new(char const *name, void (*init)(LandRunner *self),
    void (*enter)(LandRunner *self), void (*tick)(LandRunner *self),
    void (*draw)(LandRunner *self), void (*leave)(LandRunner *self), void (*destroy)(LandRunner *self)) -> LandRunner *:
    LandRunner *self
    land_alloc(self)
    self.allocated = 1
    land_runner_initialize(self, name, init, enter, tick, draw, leave, destroy)
    return self

def land_runner_switch_active(LandRunner *self):
    land_runner_leave_active()
    active_runner = self
    if active_runner and not active_runner->inited:
        active_runner->inited = 1
        if active_runner->init: active_runner->init(active_runner)
    land_runner_enter_active()

def land_runner_enter_active():
    LandRunner *self = active_runner
    if self and self.enter:
        self.enter(self)

def land_runner_tick_active():
    LandRunner *self = active_runner
    if self and self.tick:
        self.tick(self)

def land_runner_draw_active():
    LandRunner *self = active_runner
    if self and self.draw:
        self.draw(self)

def land_runner_leave_active():
    LandRunner *self = active_runner
    if self and self.leave:
        self.leave(self)

def land_runner_destroy_all():
    land_log_message("land_runner_destroy_all\n")
    LandListItem *i
    if not runners:
        return
    for i = runners->first while i with i = i->next:
        LandRunner *self = (LandRunner *)i->data
        if self.destroy:
            self.destroy(self)
        land_log_message("destroyed %s\n", self.name)
        land_free(self.name)
        if self.allocated: land_free(self)

    land_list_destroy(runners)
