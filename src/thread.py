static import allegro5/a5_thread

class LandThread:
    void *data
    void (*cb)(void *data)

class LandLock:
    void *lock

def land_thread_run(void (*cb)(void *data), void *data):
    platform_thread_run(cb, data)

def land_thread_new(void (*cb)(void *data), void *data) -> LandThread *:
    return platform_thread_new(cb, data)

def land_thread_destroy(LandThread *t):
    platform_thread_destroy(t)

def land_thread_wait_until_complete(LandThread *t):
    platform_thread_wait_until_complete(t)

def land_thread_new_lock() -> LandLock *:
    return platform_thread_new_lock()

def land_thread_delete_lock(LandLock *l):
    return platform_thread_delete_lock(l)

def land_thread_lock(LandLock *l):
    platform_thread_lock(l)

def land_thread_unlock(LandLock *l):
    platform_thread_unlock(l)

def land_thread_new_waitable_lock() -> LandLock*:
    return platform_thread_new_waitable_lock()

def land_thread_wait_lock(LandLock *self):
    """
    Wait for a lock to be triggered. This sleeps forever until another
    thread calls land_thread_trigger_lock on the lock.
    """
    platform_thread_wait_lock(self)

def land_thread_trigger_lock(LandLock *self):
    """
    Notifies all threads waiting on the lock to be triggered and wakes
    up exactly one of them.
    """
    platform_thread_trigger_lock(self)
