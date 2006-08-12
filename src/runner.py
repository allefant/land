import list

class LandRunner:
    char *name
    int inited
    void (*init)(LandRunner *self)
    void (*enter)(LandRunner *self)
    void (*tick)(LandRunner *self)
    void (*draw)(LandRunner *self)
    void (*leave)(LandRunner *self)
    void (*destroy)(LandRunner *self)

static import log, memory, global stdlib, string

static LandList *runners

static LandRunner *active_runner

def land_runner_register(LandRunner *self):
    land_log_message("land_runner_register \"%s\"\n", self->name)
    land_add_list_data(&runners, self)

def land_runner_initialize(LandRunner *self, char const *name, void (*init)(LandRunner *self),
    void (*enter)(LandRunner *self), void (*tick)(LandRunner *self),
    void (*draw)(LandRunner *self), void (*leave)(LandRunner *self), void (*destroy)(LandRunner *self)):
    self->name = land_strdup(name)
    self->init = init
    self->enter = enter
    self->tick = tick
    self->draw = draw
    self->leave = leave
    self->destroy = destroy

LandRunner *def land_runner_new(char const *name, void (*init)(LandRunner *self),
    void (*enter)(LandRunner *self), void (*tick)(LandRunner *self),
    void (*draw)(LandRunner *self), void (*leave)(LandRunner *self), void (*destroy)(LandRunner *self)):
    LandRunner *self
    land_alloc(self)
    land_runner_initialize(self, name, init, enter, tick, draw, leave, destroy)
    return self

def land_runner_switch_active(LandRunner *self):
    land_runner_leave_active()
    active_runner = self
    if active_runner && !active_runner->inited:
        active_runner->inited = 1
        if active_runner->init: active_runner->init(active_runner)
    land_runner_enter_active()

def land_runner_enter_active(void):
    LandRunner *self = active_runner
    if self && self->enter:
        self->enter(self)

def land_runner_tick_active(void):
    LandRunner *self = active_runner
    if self && self->tick:
        self->tick(self)

def land_runner_draw_active(void):
    LandRunner *self = active_runner
    if self && self->draw:
        self->draw(self)

def land_runner_leave_active(void):
    LandRunner *self = active_runner
    if self && self->leave:
        self->leave(self)

def land_runner_destroy_all(void):
    land_log_message("land_runner_destroy_all\n")
    LandListItem *i
    if !runners:
        return
    for i = runners->first; i; i = i->next:
        LandRunner *self = (LandRunner *)i->data
        if self->destroy:
            self->destroy(self)
        land_free(self->name)
        land_free(self)

    land_list_destroy(runners)
