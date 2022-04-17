import main
import noise

class LandVoronoiNode:
    int x, y

class LandVoronoi:
    int *map
    float *distance
    int *neighbor
    int n
    LandVoronoiNode *xy
    int w
    int h
    float max_distance
    float randomness
    int modulo
    LandRandom *seed

static def wrap_distance(float x1, x2, wrap) -> float:
    """
    |x1    x2             |x1
    |x1              x2   |x1
    |x2              x1   |x2
    """
    float d = fabs(x2 - x1)
    if d > wrap / 2:
        d = wrap - d
    return d

def _get_distance(LandVoronoi *self, int x, y, i) -> LandFloat:
    LandFloat dx = wrap_distance(self.xy[i].x, x, self.w)
    LandFloat dy = wrap_distance(self.xy[i].y, y, self.h)
    LandFloat d = sqrt(dx * dx + dy * dy)
    return d

def _get_closest_two(LandVoronoi *self, int x, y, *c1, *c2):
    int mi = -1
    int mj = -1
    LandFloat md = 1e20
    LandFloat md2 = 1e20
    for int i in range(self.n):
        LandFloat d = _get_distance(self, x, y, i)
        if d < md:
            mi = i
            md = d

    for int i in range(self.n):
        LandFloat d = _get_distance(self, x, y, i)
        if d < md2:
            if self.modulo:
                if i % self.modulo != mi % self.modulo:
                    mj = i
                    md2 = d
            else:
                if i != mi:
                    mj = i
                    md2 = d
    *c1 = mi
    *c2 = mj

def land_voronoi_new(LandRandom *seed, int w, h, n, modulo, float randomness) -> LandVoronoi *:
    LandVoronoi *self; land_alloc(self)
    self.w = w
    self.h = h
    self.map = land_calloc(w * h * sizeof *self.map)
    self.distance = land_calloc(w * h * sizeof *self.distance)
    self.neighbor = land_calloc(w * h * sizeof *self.neighbor)
    self.n = n
    self.xy = land_calloc(n * sizeof *self.xy)
    self.max_distance = 0
    self.modulo = modulo
    self.randomness = randomness
    self.seed = seed

    for int i in range(n):
        int x = land_random(seed, 0, w - 1)
        int y = land_random(seed, 0, h - 1)
        self.xy[i].x = x
        self.xy[i].y = y

    for int y in range(h):
        for int x in range(w):
            int i, j
            _get_closest_two(self, x, y, &i, &j)
            self.map[x + w * y] = i
            self.neighbor[x + w * y] = j

    return self

def land_voronoi_create(LandRandom *seed, int w, h, n, modulo, float randomness, distance) -> LandVoronoi*:
    auto self = land_voronoi_new(seed, w, h, n, modulo, randomness)

    #if randomness > 0:
    #    land_voronoi_distort_with_perlin(self, seed, randomness)

    if distance > 0:
        land_voronoi_calculate_border_distance(self, distance)
    else:
        land_voronoi_calculate_distance(self)

    return self

def land_voronoi_calculate_distance(LandVoronoi *self):
    int w = self.w
    int h = self.h
    for int y in range(h):
        for int x in range(w):
            int i = self.map[x + self.w * y]
            float d = _get_distance(self, x, y, i)
            self.distance[x + self.w * y] = d
            if d > self.max_distance:
                self.max_distance = d

def land_voronoi_calculate_border_distance(LandVoronoi *self, float distance):
    if self.n < 2: return
    self.max_distance = distance
    int w = self.w
    int h = self.h
    for int y in range(h):
        for int x in range(w):
            int i = self.map[x + self.w * y]
            int j = self.neighbor[x + self.w * y]
            float d1 = _get_distance(self, x, y, i)
            float d2 = _get_distance(self, x, y, j)
            float d = d2 - d1
            if d > distance: d = distance
            self.distance[x + self.w * y] = d

def land_voronoi_distort_with_perlin(LandVoronoi *self, LandRandom *seed, float randomness):
    int w = self.w
    int h = self.h
    int *map2 = land_calloc(w * h * sizeof *map2)

    # distort distances to closest cell
    float rs = randomness
    if rs < 1: rs = 1
    LandPerlin *perlin = land_perlin_create(seed, w / rs, h / rs)
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

def land_voronoi_owner(LandVoronoi *self, int x, y) -> int:
    return self.map[x + self.w * y]

def land_voronoi_neighbor(LandVoronoi *self, int x, y) -> int:
    return self.neighbor[x + self.w * y]
