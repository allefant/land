static import allegro5/a5_thread
import land.array

class LandThread:
    void *data
    void (*cb)(void *data)
    void (*done_cb)(void *data)
    bool running

class LandLock:
    bool locked

class LandThreadPool:
    LandLock *lock
    LandArray *threads # [LandPoolThread]
    int max_count
    bool full
    bool done
    bool no_reuse
    double ts

class LandPoolThread:
    LandThreadPool *pool
    LandThread *thread
    bool idle
    LandLock *next
    int run_count
    double ts0, ts1

    LandFuture *future
    void (*cb)(void *data)
    void *data

class LandFuture:
    bool complete
    LandLock *lock

    void *data

def land_thread_pool_new(int max_count) -> LandThreadPool*:
    LandThreadPool *self; land_alloc(self)
    self.threads = land_array_new()
    self.max_count = max_count
    self.lock = land_thread_new_waitable_lock()
    self.ts = land_get_time()
    return self

def land_thread_pool_destroy(LandThreadPool *self):
    self.done = True
    for LandPoolThread *thread in LandArray *self.threads:
        _pool_thread_destroy(thread)
    land_array_destroy(self.threads)
    land_thread_delete_lock(self.lock)
    land_free(self)

def land_thread_pool_stats(LandThreadPool *self):
    int i = 0
    for LandPoolThread *thread in LandArray *self.threads:
        print("thread %d: called %d times (start %.3f, duration %.3f)",
            i, thread.run_count, thread.ts0 - self.ts, thread.ts1 - thread.ts0)
        i += 1

def _pool_thread_new(LandThreadPool *pool, void (*cb)(void *data), void *data) -> LandPoolThread*:
    LandPoolThread *self; land_alloc(self)
    self.pool = pool
    self.cb = cb
    self.data = data
    self.next = land_thread_new_waitable_lock()
    self.ts0 = land_get_time()
    return self

def _pool_thread_destroy(LandPoolThread *self):
    land_thread_trigger_lock(self.next)
    land_thread_wait_until_complete(self.thread)
    land_thread_destroy(self.thread)
    land_thread_delete_lock(self.next)
    land_free(self)

def land_future_destroy(LandFuture *self):
    land_thread_delete_lock(self.lock)
    land_free(self)

def land_thread_pool_submit(LandThreadPool *self, void (*cb)(void *data), void *data) -> LandFuture *:
    land_thread_lock(self.lock)

    # if we know we are full, wait until we are not
    if self.full:
        land_wait_for_lock(self.lock)

    LandFuture *future; land_alloc(future)
    future.lock = land_thread_new_waitable_lock()

    # find a free pool thread and re-use it immediately
    int count = 0
    LandPoolThread *submitted = None
    for LandPoolThread *t in LandArray *self.threads:
        # we are inside the pool lock, so we are safe to check and
        # modify the flag here
        if t.idle
            if submitted:
                break
            if self.no_reuse:
                land_thread_wait_until_complete(t.thread)
                land_thread_destroy(t.thread)
                t.thread = land_thread_new_stopped(_pool_thread, t)
            submitted = t
            t.idle = False
            t.future = future
            t.cb = cb
            t.data = data
        count += 1

    if count == self.max_count: # since we were not full, submitted must be set
        self.full = True

    if submitted:
        goto done

    # all existing threads were filled, but less than max_count, lets
    # add a new one
    auto t = _pool_thread_new(self, cb, data)
    t.future = future
    t.thread = land_thread_new_stopped(_pool_thread, t)
    land_array_add(self.threads, t)
    if land_array_count(self.threads) == self.max_count:
        self.full = True
    land_thread_start_stopped(t.thread)

    label done
    land_thread_unlock(self.lock)
    if submitted:
        if self.no_reuse:
            land_thread_start_stopped(submitted.thread)
        else:
            land_thread_trigger_lock(submitted.next)
    return future

def _pool_thread(void *data):
    LandPoolThread *t = data
    while not t.pool.done:
        t.run_count += 1
        t.cb(t.data)
        LandFuture *future = t.future
        t.future = None
        future.data = t.data
        t.cb = None
        t.data = None
        t.idle = True
        future.complete = True
        land_thread_lock(t.pool.lock)
        if t.pool.full:
            t.pool.full = False
            land_trigger_lock(t.pool.lock)
        land_thread_unlock(t.pool.lock)
        t.ts1 = land_get_time()
        land_thread_trigger_lock(future.lock)
        if t.pool.no_reuse:
            return
        land_thread_wait_lock(t.next) # version which locks

def land_future_wait(LandFuture *future):
    if future.complete:
        return
    land_thread_wait_lock(future.lock)

def land_thread_run(void (*cb)(void *data), void *data):
    platform_thread_run(cb, data)

def land_thread_new(void (*cb)(void *data), void *data) -> LandThread *:
    return platform_thread_new(cb, data)

def land_thread_new_stopped(void (*cb)(void *data), void *data) -> LandThread *:
    return platform_thread_new_stopped(cb, data)

def land_thread_start_stopped(LandThread *self):
    platform_thread_start_stopped(self)

def land_thread_set_done_callback(LandThread *self, void (*done_cb)(void *data)):
    self.done_cb = done_cb

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
    l.locked = True

def land_thread_unlock(LandLock *l):
    l.locked = False
    platform_thread_unlock(l)

def land_thread_new_waitable_lock() -> LandLock*:
    return platform_thread_new_waitable_lock()

def land_thread_wait_lock(LandLock *self):
    """
    Wait for a lock to be triggered. This sleeps forever until another
    thread calls land_thread_trigger_lock on the lock. The lock MUST NOT
    be locked already or this will deadlock immediately.
    """
    platform_thread_wait_lock(self, False)

def land_thread_trigger_lock(LandLock *self):
    """
    Notifies all threads waiting on the lock to be triggered and wakes
    up exactly one of them. The lock MUST NOT
    be locked already or this will deadlock immediately.
    """
    platform_thread_trigger_lock(self, False)

def land_wait_for_lock(LandLock *self):
    if not self.locked:
        land_exception("land_wait_for_lock: Thread was not locked")
    platform_thread_wait_lock(self, True)

def land_trigger_lock(LandLock *self):
    if not self.locked:
        land_exception("land_trigger_lock: Thread was not locked")
    platform_thread_trigger_lock(self, True)
