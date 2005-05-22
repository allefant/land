#include <stdlib.h>
#include <string.h>

#ifdef _PROTOTYPE_

#include "array.h"

land_type(LandRunner)
{
    char *name;
    void (*init)(void);
    void (*enter)(void);
    void (*tick)(void);
    void (*draw)(void);
    void (*leave)(void);
    void (*destroy)(void);
};

#endif /* _PROTOTYPE_ */

#include "runner.h"

land_array(LandRunner)

static LandRunner *active_runner;

LandRunner *land_runner_register(char const *name, void (*init)(void),
        void (*enter)(void), void (*tick)(void),
        void (*draw)(void), void (*leave)(void), void (*destroy)(void))
{
    land_new(LandRunner, self);
    self->name = strdup(name);
    self->init = init;
    self->enter = enter;
    self->tick = tick;
    self->draw = draw;
    self->leave = leave;
    self->destroy = destroy;
    return self;
}

void land_runner_init(void)
{
    int i;
    land_foreach(LandRunner, i)
    {
        LandRunner *self = land_pointer(LandRunner, i);
        if (self->init)
            self->init();
    }
}

void land_runner_switch(LandRunner *self)
{
    land_runner_leave();
    active_runner = self;
    land_runner_enter();
}

void land_runner_enter(void)
{
    LandRunner *self = active_runner;
    if (self && self->enter)
        self->enter();
}

void land_runner_tick(void)
{
    LandRunner *self = active_runner;
    if (self)
        self->tick();
}

void land_runner_draw(void)
{
    LandRunner *self = active_runner;
    if (self && self->draw)
        self->draw();
}

void land_runner_leave(void)
{
    LandRunner *self = active_runner;
    if (self && self->leave)
        self->leave();
}


void land_runner_destroy(void)
{
   int i;
    land_foreach(LandRunner, i)
    {
        LandRunner *self = land_pointer(LandRunner, i);
        if (self->destroy)
            self->destroy();
    }
}

