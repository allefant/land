static import allegro5/a5_thread
def land_thread_run(void (*cb)(void)):
    platform_thread_run(cb)
