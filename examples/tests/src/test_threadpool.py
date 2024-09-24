import global land.land
import test_util

def test_threadpool:
    test(empty)
    test(submit)
    test(submit1000)
    test(time)

def _test_empty:
    auto pool = land_thread_pool_new(0)
    land_thread_pool_destroy(pool)

class Sample:
    int x

def _test_submit:
    auto pool = land_thread_pool_new(1)
    Sample s
    s.x = 0
    assert_equals_num(s.x, 0, "%d", "value")
    auto future = land_thread_pool_submit(pool, _fast, &s)
    land_future_wait(future)
    assert_equals_num(s.x, 1, "%d", "value")
    land_thread_pool_destroy(pool)

def _test_submit1000:
    auto pool = land_thread_pool_new(2)
    Sample s[1000] = {}
    LandFuture *f[1000]
    assert_equals_num(s[0].x, 0, "%d", "value")
    for int i in range(1000):
        f[i] = land_thread_pool_submit(pool, _fast, s + i)
    for int i in range(1000):
        land_future_wait(f[i])
        assert_equals_num(s[i].x, 1, "%d", "value")
    land_thread_pool_destroy(pool)

def _test_time:
    for int c in range(16):
        int tnum = 16 - c
        auto t = land_timing_new()
        auto pool = land_thread_pool_new(tnum)
        #pool.no_reuse = True
        Sample s[400] = {}
        LandFuture *f[400]
        int j = 0
        for int i in range(400):
            s[i].x = 2000
            f[i] = land_thread_pool_submit(pool, _slow, s + i)
            if j == tnum - 1:
                for j in range(tnum):
                    land_future_wait(f[i - tnum + 1 + j])
                    # 4000: 37813
                    # 2000: 17389
                    assert_equals_num(s[i - tnum + 1 + j].x, 17389, "%d", "value")
                j = 0
            else:
                j += 1
                
        char *name = land_str("%d threads", 16 - c)
        land_thread_pool_stats(pool)
        land_thread_pool_destroy(pool)
        land_timing_add(t, name)
        land_timing_print(t)
        land_free(name)

def _fast(void *data):
    Sample *s = data
    s.x += 1

def _is_prime(int x, n, *primes) -> bool:
    for int i in range(n):
        if x % primes[i] == 0: return False
    return True

def _slow(void *data):
    Sample *s = data
    int n = s.x
    int primes[n]
    primes[0] = 2
    int pn = 1
    int x = 3
    while True:
        if _is_prime(x, pn, primes):
            primes[pn] = x
            pn += 1
            if pn == n:
                s.x = x
                return
        x += 1
