import global land.land
import test_util

def test_buffer:
    test(ring)
    test(ring2)

def _test_ring:
    LandRingBuffer *ring = land_ring_buffer_new()
    assert_equals_num(land_ring_len_uint32(ring), 0L, "%lu", "initial")
    for int i in range(1000):
        land_ring_add_uint32(ring, i)
    assert_equals_num(land_ring_len_uint32(ring), 1000L, "%lu", "length")
    assert_equals_num(ring.ring.size, 4096L, "%lu", "size")
    for uint32_t i in range(1000):
        uint32_t x = land_ring_pop_first_uint32(ring)
        assert_equals_num(x, i, "%u", "value")
    assert_equals_num(land_ring_len_uint32(ring), 0L, "%lu", "empty")
    assert_equals_num(ring.ring.size, 4096L, "%lu", "size 2")

def _test_ring2:
    LandRingBuffer *ring = land_ring_buffer_new()
    for int i in range(1000):
        land_ring_add_uint32(ring, i)
    for int i in range(500):
        land_ring_pop_first_uint32(ring)
    for int i in range(500):
        land_ring_add_uint32(ring, 1000 + i)
    for int i in range(500):
        land_ring_pop_first_uint32(ring)
    for int i in range(500):
        land_ring_add_uint32(ring, 1500 + i)
    for uint32_t i in range(1000):
        uint32_t x = land_ring_pop_first_uint32(ring)
        assert_equals_num(x, 1000 + i, "%u", "value")
    assert_equals_num(land_ring_len_uint32(ring), 0L, "%lu", "empty again")
    assert_equals_num(ring.ring.size, 4096L, "%lu", "allocation")
