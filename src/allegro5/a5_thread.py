import land.thread
import land.mem
static import global allegro5.allegro5

static class PlatformThread:
    LandThread super
    ALLEGRO_THREAD *a5

static void *def proc(void *data):
    LandThread *t = data
    t->cb(t->data)
    land_free(t)
    return NULL

def platform_thread_run(void (*cb)(void *), void *data):
    LandThread *t; land_alloc(t)
    t->cb = cb
    t->data = data
    al_run_detached_thread(proc, t)

static void *def aproc(ALLEGRO_THREAD *thread, void *arg):
    LandThread *t = arg
    t->cb(t->data)
    return NULL

LandThread *def platform_thread_new(void (*cb)(void *data), void *data):
    PlatformThread *t; land_alloc(t)
    t->super.cb = cb
    t->super.data = data
    t->a5 = al_create_thread(aproc, t)
    al_start_thread(t->a5)
    return &t->super

def platform_thread_destroy(LandThread *self):
    PlatformThread *t = (void *)self
    al_destroy_thread(t->a5)
    land_free(self)
