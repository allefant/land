import main
import noise

class LandVoronoi:
    int *map
    float *distance
    int n
    LandNoiseI2 *xy
    int w
    int h
    float max_distance

static def wrap_distance(float x1, x2, wrap) -> float:
    """
    |x1    x2             |x1
    |x1              x2   |x1
    |x2              x1   |x2
    """
    float d = fabs(x2 - x1)
    float d2 = fabs(x1 + wrap - x2)
    if d2 < d: d = d2
    d2 = fabs(x2 + wrap - x1)
    if d2 < d: d = d2
    return d

static def get_closest(LandVoronoi *self, int x, y) -> int:
    int mi = -1
    int md = INT_MAX
    for int i in range(self.n):
        int dx = wrap_distance(self.xy[i].x, x, self.w)
        int dy = wrap_distance(self.xy[i].y, y, self.h)
        if dx * dx + dy * dy < md:
            mi = i
            md = dx * dx + dy * dy
    return mi

def land_voronoi_new(int w, h, n) -> LandVoronoi *:
    LandVoronoi *self; land_alloc(self)
    self.w = w
    self.h = h
    self.map = land_calloc(w * h * sizeof *self.map)
    self.distance = land_calloc(w * h * sizeof *self.distance)
    self.n = n
    self.xy = land_calloc(n * sizeof *self.xy)
    self.max_distance = 0

    for int i in range(n):
        int x = land_rand(0, w - 1)
        int y = land_rand(0, h - 1)
        self.xy[i].x = x
        self.xy[i].y = y

    for int y in range(h):
        for int x in range(w):
            int i = get_closest(self, x, y)
            self.map[x + w * y] = i

    return self

def land_voronoi_create(int w, h, n, float randomness) -> LandVoronoi*:
    auto self = land_voronoi_new(w, h, n)

    land_voronoi_distort_with_perlin(self, randomness)

    land_voronoi_calculate_distance(self)

    return self

def land_voronoi_calculate_distance(LandVoronoi *self):
    int w = self.w
    int h = self.h
    for int y in range(h):
        for int x in range(w):
            int i = self.map[x + self.w * y]
            int dx = wrap_distance(self.xy[i].x, x, self.w)
            int dy = wrap_distance(self.xy[i].y, y, self.h)
            float d = sqrt(dx * dx + dy * dy)
            self.distance[x + self.w * y] = d
            if d > self.max_distance:
                self.max_distance = d

def land_voronoi_distort_with_perlin(LandVoronoi *self, float randomness):
    int w = self.w
    int h = self.h
    int *map2 = land_calloc(w * h * sizeof *map2)

    # distort distances to closest cell
    float rs = randomness
    if rs < 1: rs = 1
    LandPerlin *perlin = land_perlin_create(w / rs, h / rs)
    for int y in range(h):
        for int x in range(w):
            float xd, yd
            land_perlin_displace(perlin, x / rs, y / rs, &xd, &yd)
            int dx = land_mod(x + xd * randomness, self.w)
            int dy = land_mod(y + yd * randomness, self.h)
            int i = self.map[dx + w * dy]
            map2[y * w + x] = i
    land_perlin_destroy(perlin)

    land_free(self.map)
    self.map = map2

def land_voronoi_destroy(LandVoronoi *self):
    land_free(self.map)
    land_free(self.distance)
    land_free(self.xy)
    land_free(self)

def land_voronoi_at(LandVoronoi *self, int x, y) -> float:
    float value = self.distance[x + self.w * y] / self.max_distance
    return value * 2 - 1 # change range from 0..1 to -1..1
