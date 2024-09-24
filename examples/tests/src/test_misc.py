import global land.land
import test_util

def test_misc:
    test(bitset0)
    test(bitset1)
    test(bitset100)

def _test_bitset0:
    LandBitSet *bitset = land_bitset_new(0)
    assert_bool(land_is_bit_set(bitset, 0), False, "empty")

def _test_bitset1:
    LandBitSet *bitset = land_bitset_new(1)
    assert_bool(land_is_bit_set(bitset, 0), False, "1")
    land_bit_set(bitset, 0)
    assert_bool(land_is_bit_set(bitset, 0), True, "1")

def _test_bitset100:
    LandBitSet *bitset = land_bitset_new(100)
    land_bit_set(bitset, 63)
    assert_bool(land_is_bit_set(bitset, 31), False, "set(31)")
    assert_bool(land_is_bit_set(bitset, 63), True, "set(63)")
