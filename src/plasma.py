import global stdlib, math, stdbool
import random
import mem
import common

class LandPlasma:
    int w, h
    float *cache
    float power_modifier
    float amplitude
    LandRandom *rndgen

# old crispness c:
# level n - 1: c
# level n - 2: 2c
# level n - 3: 4c
# ...
# level     0: w/2*c
#
# new power (2+p) and amplitude a:
# level 0    : p^a
# level 1    : p^(a-1)
# level 2    : p^(a-2)
# ...
# leven n - 1: p^(a-n+1)
#
# because 2^n = w, we can convert crispness to amplitude:
#
# a = log2(c * w / 2) = log2(c) + n - 1
# level 0    : c * w / 2
# ...
# level n - 2: 2^(a-n+2) = 2c
# level n - 1: 2^(a-n+1) = c
#
def _blend(LandPlasma *self, float c1, c2, level) -> float:
    float rnd = land_random_f(self.rndgen, -1, 1)

    float scale = pow(2 + self.power_modifier, -level + self.amplitude)
    float ret = (c1 + c2 + rnd * scale) / 2

    if ret < -1: ret = -1
    if ret > 1: ret = 1

    return ret

def land_plasma_new(LandRandom *rndgen, int w, h, float power_modifier, amplitude) -> LandPlasma*:
    LandPlasma *self
    land_alloc(self)

    self.w = w
    self.h = h
    self.power_modifier = power_modifier
    self.amplitude = amplitude
    self.rndgen = rndgen

    self.cache = land_calloc(w * h * sizeof *self.cache)

    return self

def _plasma_read(LandPlasma *self, int x, y) -> float:
    x = land_mod(x, self.w)
    y = land_mod(y, self.h)
    return self.cache[y * self.w + x]

def _plasma_write(LandPlasma *self, int x, y, float value):
    x = land_mod(x, self.w)
    y = land_mod(y, self.h)
    self.cache[y * self.w + x] = value

# example:
# i = 0, w = 16 # level 0 is full size
# i = 1, w = 8
# i = 2, w = 4
# i = 3, w = 2  # level log2(w)-1 is size 2
# there is no level 4 as a size of 1 would only overwrite pixels
def _fractal(LandPlasma *self, int x, y, w, h, i):
    # in the very first recursion level, all of them will be the same
    float c1 = _plasma_read(self, x, y)
    float c2 = _plasma_read(self, x + w, y)
    float c3 = _plasma_read(self, x + w, y + h)
    float c4 = _plasma_read(self, x, y + h)

    float n2 = _blend(self, c1, c2, i)
    float n4 = _blend(self, c1, c4, i)
    float n3 = _blend(self, (c1 + c2) / 2, (c3 + c4) / 2, i)

    w /= 2
    h /= 2

    _plasma_write(self, x + w, y, n2)
    _plasma_write(self, x + w, y + h, n3)
    _plasma_write(self, x, y + h, n4)

def _subdivide(LandPlasma *self):
    int dx = self.w
    int dy = self.h
    int x = 0
    int y = 0
    int i = 0

    while dx > 1 and dy > 1:
        while x < self.w:
            while y < self.h:
                _fractal(self, x, y, dx, dy, i)
                y += dy
            y = 0
            x += dx
        x = 0
        dx /= 2
        dy /= 2
        i++

def land_plasma_generate(LandPlasma *self):
    _plasma_write(self, 0, 0, 0)
    _subdivide(self)

def land_plasma_del(LandPlasma *self):
    land_free(self)

def land_plasma_at(LandPlasma *self, int x, y) -> float:
    x %= self.w
    if x < 0: x += self.w
    y %= self.h
    if y < 0: y += self.h
    float value = self.cache[x + self.w * y]
    return value
