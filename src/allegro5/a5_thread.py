import land.thread
static import global allegro5.allegro5

void *def proc(void *cb):
    void (*p)(void) = cb
    p()
    return NULL

def platform_thread_run(void (*cb)(void)):
    al_run_detached_thread(proc, cb)
