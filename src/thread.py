static import allegro5/a5_thread

class LandThread:
    void *data
    void (*cb)(void *data)

class LandLock:
    void *lock

def land_thread_run(void (*cb)(void *data), void *data):
    platform_thread_run(cb, data)

LandThread *def land_thread_new(void (*cb)(void *data), void *data):
    return platform_thread_new(cb, data)

def land_thread_destroy(LandThread *t):
    platform_thread_destroy(t)

LandLock *def land_thread_new_lock():
    return platform_thread_new_lock()

def land_thread_delete_lock(LandLock *l):
    return platform_thread_delete_lock(l)

def land_thread_lock(LandLock *l):
    platform_thread_lock(l)

def land_thread_unlock(LandLock *l):
    platform_thread_unlock(l)
