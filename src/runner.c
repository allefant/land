#include <stdlib.h>
#include <string.h>

#ifdef _PROTOTYPE_

#include "array.h"

typedef struct LandRunner LandRunner;
struct LandRunner
{
    char *name;
    int inited;
    void (*init)(LandRunner *self);
    void (*enter)(LandRunner *self);
    void (*tick)(LandRunner *self);
    void (*draw)(LandRunner *self);
    void (*leave)(LandRunner *self);
    void (*destroy)(LandRunner *self);
};

#endif /* _PROTOTYPE_ */

#include "runner.h"
#include "log.h"

static LandList *runners;

static LandRunner *active_runner;

void land_runner_register(LandRunner *self)
{
    land_log_msg("land_runner_register \"%s\"\n", self->name);
    land_add_list_data(&runners, self);
}

void land_runner_initialize(LandRunner *self, char const *name, void (*init)(LandRunner *self),
    void (*enter)(LandRunner *self), void (*tick)(LandRunner *self),
    void (*draw)(LandRunner *self), void (*leave)(LandRunner *self), void (*destroy)(LandRunner *self))
{
    self->name = strdup(name);
    self->init = init;
    self->enter = enter;
    self->tick = tick;
    self->draw = draw;
    self->leave = leave;
    self->destroy = destroy;
}

LandRunner *land_runner_new(char const *name, void (*init)(LandRunner *self),
    void (*enter)(LandRunner *self), void (*tick)(LandRunner *self),
    void (*draw)(LandRunner *self), void (*leave)(LandRunner *self), void (*destroy)(LandRunner *self))
{
    LandRunner *self = calloc(1, sizeof *self);
    land_runner_initialize(self, name, init, enter, tick, draw, leave, destroy);
    return self;
}

void land_runner_switch_active(LandRunner *self)
{
    land_runner_leave_active();
    active_runner = self;
    if (active_runner && !active_runner->inited)
    {
        active_runner->inited = 1;
        if (active_runner->init) active_runner->init(active_runner);
    }
    land_runner_enter_active();
}

void land_runner_enter_active(void)
{
    LandRunner *self = active_runner;
    if (self && self->enter)
        self->enter(self);
}

void land_runner_tick_active(void)
{
    LandRunner *self = active_runner;
    if (self && self->tick)
        self->tick(self);
}

void land_runner_draw_active(void)
{
    LandRunner *self = active_runner;
    if (self && self->draw)
        self->draw(self);
}

void land_runner_leave_active(void)
{
    LandRunner *self = active_runner;
    if (self && self->leave)
        self->leave(self);
}


void land_runner_destroy_all(void)
{
    LandListItem *i;
    if (!runners)
        return;
    for (i = runners->first; i; i = i->next)
    {
        LandRunner *self = (LandRunner *)i->data;
        if (self->destroy)
            self->destroy(self);
    }
}

