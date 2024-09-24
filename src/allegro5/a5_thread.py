import land.thread
import land.mem
static import global allegro5.allegro5

static class PlatformThread:
    LandThread super
    ALLEGRO_THREAD *a5

static class PlatformLock:
    LandLock super
    ALLEGRO_MUTEX *a5
    ALLEGRO_COND *cond
    bool triggered

static def proc(void *data) -> void *:
    LandThread *t = data
    t->cb(t->data)
    land_free(t)
    return NULL

def platform_thread_run(void (*cb)(void *), void *data):
    LandThread *t; land_alloc(t)
    t->cb = cb
    t->data = data
    al_run_detached_thread(proc, t)

static def aproc(ALLEGRO_THREAD *thread, void *arg) -> void *:
    LandThread *t = arg
    t->cb(t->data)
    if t->done_cb:
        t->done_cb(t->data)
    return NULL

def platform_thread_new_state(void (*cb)(void *data), void *data, bool running) -> LandThread *:
    PlatformThread *t; land_alloc(t)
    t->super.cb = cb
    t->super.data = data
    t->a5 = al_create_thread(aproc, t)
    t->super.running = running
    if running:
        al_start_thread(t->a5)
    return &t->super

def platform_thread_new(void (*cb)(void *data), void *data) -> LandThread *:
    return platform_thread_new_state(cb, data, True)
    
def platform_thread_new_stopped(void (*cb)(void *data), void *data) -> LandThread *:
    return platform_thread_new_state(cb, data, False)

def platform_thread_start_stopped(LandThread *self):
    PlatformThread *t = (void *)self
    t->super.running = True
    al_start_thread(t.a5)

def platform_thread_wait_until_complete(LandThread* self):
    PlatformThread *t = (void *)self
    al_join_thread(t.a5, None)
    t->super.running = False

def platform_thread_destroy(LandThread *self):
    PlatformThread *t = (void *)self
    al_destroy_thread(t->a5)
    land_free(self)

def platform_thread_new_lock() -> LandLock *:
    PlatformLock *l; land_alloc(l)
    l.a5 = al_create_mutex_recursive()
    return (void *)l

def platform_thread_new_waitable_lock() -> LandLock *:
    PlatformLock *l; land_alloc(l)
    l.a5 = al_create_mutex() # not recursive, condition variables don't work that way
    l.cond = al_create_cond()
    return (void *)l

def platform_thread_delete_lock(LandLock *lock):
    PlatformLock *l = (void *)lock
    al_destroy_mutex(l.a5)
    if l.cond:
        al_destroy_cond(l.cond)
    land_free(l)

def platform_thread_lock(LandLock *lock):
    PlatformLock *l = (void *)lock
    al_lock_mutex(l.a5)

def platform_thread_unlock(LandLock *lock):
    PlatformLock *l = (void *)lock
    al_unlock_mutex(l.a5)
 
def platform_thread_wait_lock(LandLock *lockp, bool already_locked):
    PlatformLock* lock = (void*)lockp
    if not already_locked:
        al_lock_mutex(lock.a5)
    while not lock.triggered:
        al_wait_cond(lock.cond, lock.a5)
    lock.triggered = False
    if not already_locked:
        al_unlock_mutex(lock.a5)

def platform_thread_trigger_lock(LandLock *lockp, bool already_locked):
    PlatformLock* lock = (void*)lockp
    if not already_locked:
        al_lock_mutex(lock.a5)
    lock.triggered = True
    al_broadcast_cond(lock.cond)
    if not already_locked:
        al_unlock_mutex(lock.a5)
