static import allegro5/a5_thread

class LandThread:
    void *data
    void (*cb)(void *data)

def land_thread_run(void (*cb)(void *data), void *data):
    platform_thread_run(cb, data)

LandThread *def land_thread_new(void (*cb)(void *data), void *data):
    return platform_thread_new(cb, data)

def land_thread_destroy(LandThread *t):
    platform_thread_destroy(t)
