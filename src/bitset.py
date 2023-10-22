import common
import mem
import land.util

class LandBitSet:
    uint64_t *bits
    int bits_count
    int size_in_bytes

def land_bitset_new(int n) -> LandBitSet*:
    LandBitSet *self; land_alloc(self)
    self.bits_count = n
    int size = (n + 63) // 64
    self.size_in_bytes = size * 8
    self.bits = land_calloc(self.size_in_bytes)
    return self

def land_bitset_del(LandBitSet *self):
    land_free(self.bits)
    land_free(self)

def land_bitset_clear(LandBitSet *self):
    land_zero(self.bits, self.size_in_bytes)

def land_bit_set(LandBitSet *self, int x):
    int p = x // 64
    self.bits[p] |= 1L << (x & 63)

def land_is_bit_set(LandBitSet *self, int x) -> bool:
    int p = x // 64
    return (self.bits[p] & (1L << (x & 63))) != 0

def land_bit_check_or_set(LandBitSet *self, int x) -> bool:
    int p = x // 64
    uint64_t r = self.bits[p] & (1L << (x & 63))
    self.bits[p] |= 1L << (x & 63)
    return r != 0

def land_bitset_string(LandBitSet *self) -> char*:
    char *r = land_strdup("{")
    bool first = True
    for int i in range(self.bits_count):
        if land_is_bit_set(self, i):
            if first:
                first = False
            else:
                land_append(&r, ",")
            land_append(&r, "%d", i)
    land_append(&r, "}")
    return r
