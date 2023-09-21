import perlin
import voronoi
import plasma

enum LandNoiseType:
    LandNoiseNone
    LandNoiseWhite
    LandNoisePerlin
    LandNoiseVoronoi
    LandNoisePlasma
    LandNoiseWaves
    LandNoiseValue

enum LandNoiseShape:
    LandNoiseShapeNone
    LandNoiseShapeDistance
    LandNoiseShapeSquared
    LandNoiseShapeCos
    LandNoiseShapeDiamond

class LandNoiseI2:
    int x, y

class LandNoiseF2:
    float x, y

class LandNoise:
    LandNoiseType t
    LandArray *noise
    int w, h
    int count
    int levels
    int first_level
    int modulo
    int passes
    LandRandom *seed
    bool use_external_seed
    float randomness
    float power_modifier
    float amplitude
    float distance
    int lerp
    bool warp
    float warp_x, warp_y, warp_sx, warp_sy
    bool blur
    float blur_size
    float minval, maxval
    bool wrap
    void *user
    LandNoiseShape shape
    float shape_amount

    float z_scale, z_offset, z_ease
    float (*transfer_cb)(float x)
    float (*value_cb)(LandNoise *self, int x, int y, void* user)
    void (*external_blur)(LandNoise *self, LandFloat *noise, int w, int h,
        LandFloat blur_size, LandFloat compensate, bool wrap)

    LandFloat *cache

static class Waves:
    int count
    float *xy

def land_noise_new(LandNoiseType t, int seed) -> LandNoise*:
    LandNoise *self; land_alloc(self)

    self.t = t
    self.noise = land_array_new()

    self.count = 1
    self.levels = 1
    self.first_level = 1
    self.lerp = LandPerlinLerpCosine

    self.z_scale = 1
    self.minval = -1e9
    self.maxval = +1e9

    self.wrap = True
    self.seed = land_random_new(seed)

    return self

def land_noise_set_random(LandNoise *self, LandRandom *random):
    """
    Note: Ownership of the LandRandom object remains at the caller who
    must make sure it lives as long as the noise is being used.
    """
    if self.seed and not self.use_external_seed:
        land_random_del(self.seed)
    self.seed = random
    self.use_external_seed = True

def land_noise_set_size(LandNoise *self, int w, h):
    self.w = w
    self.h = h

def land_noise_set_lerp(LandNoise *self, LandPerlinLerp lerp):
    self.lerp = lerp
    
def land_noise_set_count(LandNoise *self, int n):
    self.count = n

def land_noise_set_levels(LandNoise *self, int n):
    self.levels = n

def land_noise_set_first_level(LandNoise *self, int n):
    self.first_level = n

def land_noise_set_amplitude(LandNoise *self, float amplitude):
    self.amplitude = amplitude

def land_noise_set_distance(LandNoise *self, float distance):
    self.distance = distance

def land_noise_set_passes(LandNoise *self, int passes):
    self.passes = passes

def land_noise_set_power_modifier(LandNoise *self, float power_modifier):
    self.power_modifier = power_modifier

def land_noise_set_randomness(LandNoise *self, float randomness):
    self.randomness = randomness

def land_noise_set_minmax(LandNoise *self, float minval, maxval):
    self.minval = minval
    self.maxval = maxval

def land_noise_set_value(LandNoise *self, int x, y, float val):
    if self.cache:
        if x >= 0 and y >=  0 and x < self.w and y < self.h:
            self.cache[x + y *self.w] = val

def land_noise_set_warp(LandNoise *self, LandNoise *warp, float x, y, sx, sy):
    self.warp = True
    self.warp_x = x
    self.warp_y = y
    self.warp_sx = sx
    self.warp_sy = sy
    land_array_add(self.noise, warp)

def land_noise_set_blur(LandNoise *self, LandNoise *blur, LandFloat size):
    self.blur = True
    self.blur_size = size
    self.w = blur.w
    self.h = blur.h
    land_array_add(self.noise, blur)

def land_noise_set_wrap(LandNoise *self, bool wrap):
    self.wrap = wrap

def land_noise_set_shape(LandNoise *self, LandNoiseShape shape, float amount):
    self.shape = shape
    self.shape_amount = amount

def land_noise_smoothen(LandNoise *self):

    int w = self->w
    int h = self->h

    self.cache = land_malloc(w * h * sizeof *self.cache)

    for int y in range(self.h):
        for int x in range(self.w):
            self.cache[x + y *self.w] = land_noise_at(
                land_array_get_nth(self.noise, 0), x, y)

    _smoothen_temp(self, self.cache, w, h, self.blur_size, 1.0, self.wrap)

def _smoothen_temp(LandNoise *self, LandFloat *noise, int w, h,
        LandFloat blur_size, LandFloat compensate, bool wrap):
    if self.external_blur:
        self.external_blur(self, noise, w, h, blur_size, compensate, wrap)
        return
    LandFloat *cache2 = land_malloc(w * h * sizeof *cache2)

    double sigma = blur_size
    int fs = sigma * 6 + 1
    double filteri[fs]
    double sigma2 = sigma * sigma
    double f = 1.0 / sqrt(2 * LAND_PI * sigma2)
    for int y in range(fs):
        int y2 = y - fs / 2
        filteri[y] = f * exp(y2 * y2 / sigma2 / -2)

    for int y in range(h):
        for int x in range(w):
            double s = 0, a = 0
            for int v in range(fs):
                int tx = x
                int ty = y + v - fs / 2
                double b = filteri[v]
                a += b
                if ty < 0:
                    if wrap: ty += h
                    else: ty = 0
                if ty > h - 1:
                    if wrap: ty -= h
                    else: ty = h - 1
                s += noise[ty * w + tx] * b
            cache2[x + w * y] = s / a

    for int y in range(h):
        for int x in range(w):
            double s = 0, a = 0
            for int u in range(fs):
                int tx = x + u - fs / 2
                int ty = y
                double b = filteri[u]
                a += b
                if tx < 0:
                    if wrap: tx += w
                    else: tx = 0
                if tx > w - 1:
                    if wrap: tx -= w
                    else: tx = w - 1
                s += cache2[ty * w + tx] * b
            noise[x + w * y] = s * compensate / a

    land_free(cache2)

def _white(LandNoise *self) -> LandFloat*:
    LandFloat *noise = land_malloc(self.w * self.h * sizeof *noise)

    for int y in range(self.h):
        for int x in range(self.w):
            noise[x + self.w * y] = land_random_f(self.seed, -1, 1)

    return noise

def land_noise_replace_heightmap(LandNoise *self, LandFloat *cache):
    """
    Convert the noise to a fixed value noise - but keep the coloring
    info.
    """
    if not self.cache:
        self.cache = land_malloc(self.w * self.h * sizeof *self.cache)
    memcpy(self.cache, cache, self.w * self.h * sizeof *cache)
    self.t = LandNoiseValue
    self.z_scale = 1
    self.z_offset = 0
    self.z_ease = 0
    self.warp = False
    self.blur = False
    self.transfer_cb = None

def land_noise_prepare(LandNoise *self):
    if self.warp:
        land_noise_prepare(land_array_get_nth(self.noise, 0))
        return

    if self.blur:
        land_noise_prepare(land_array_get_nth(self.noise, 0))
        land_noise_smoothen(self)
        return

    if self.t == LandNoiseWhite:
        int w = self.w
        int h = self.h
        int n = 1 + self.levels
        #int size = 4 + self.first_level
        #int wh = min(w, h)
        for int i in range(n):
            LandFloat *noise = _white(self)
            float blur_radius = 0
            int level = self.first_level - i
            if level > 0:
                blur_radius = pow(2, (level - 1) / 2.0) #(float)wh / size
                # standard deviation decreases by about 2 * sqrt(pi) * sigma
                float compensate = 2 * sqrt(pi) * blur_radius
                _smoothen_temp(self, noise, w, h, blur_radius,
                    compensate, self.wrap)
            land_array_add(self.noise, noise)

        LandFloat scale = 1.0
        LandFloat mod = 0.5 + 0.25 * self.power_modifier
        #LandFloat total = 0
        #for int i in range(n):
        #    total += scale
        #    scale *= 0.75
        self.cache = land_malloc(self.w * self.h * sizeof *self.cache)
        for int y in range(self.h):
            for int x in range(self.w):
                LandFloat v = 0.0
                scale = 1.0
                for LandFloat *noise in LandArray *self.noise:
                    LandFloat val = noise[y * self.w + x]
                    LandFloat s = pow(2, self.amplitude)
                    v += val * scale * s
                    scale *= mod
                self.cache[x + self.w * y] = v
        
    if self.t == LandNoiseVoronoi:
        void *noise = land_voronoi_create(self.seed, self.w, self.h,
            self.count, self.wrap, self.randomness, 0, self.distance)
        land_array_add(self.noise, noise)
    if self.t == LandNoiseWaves:
        void *noise = _waves_create(self, self.w, self.h)
        land_array_add(self.noise, noise)
    if self.t == LandNoisePerlin:
        int n = self.levels + 1
        int first = self.first_level
        int w = self.w >> (1 + first)
        int h = self.h >> (1 + first)

        if w == 0: w = 1
        if h == 0: h = 1

        # if n is 0, there is no noise at all
        # if n is 1, we do a 2x2 Perlin - a 1x1 Perlin usually is
        # mostly just 0.
        # if n is 2+, do the same as for n == 1 but in each additional
        # level double the frequency and half the amplitude.

        # instead of stretching, for non-square adjust initial h level -
        # assuming the level is set for w
        #if self.w != self.h:
        #    h = h * self.h / self.w
        
        for int i in range(n):
            LandPerlin *noise = land_perlin_create(self.seed, w, h)
            land_perlin_set_lerp(noise, self.lerp)
            land_array_add(self.noise, noise)
            if w < self.w and h < self.h:
                w <<= 1
                h <<= 1

        _multires_cache(self)
        
    if self.t == LandNoisePlasma:
        void *noise = land_plasma_new(self.seed, self.w, self.h, self.power_modifier, self.amplitude)
        land_plasma_generate(noise)
        land_array_add(self.noise, noise)

    if self.t == LandNoiseValue:
        self.cache = land_calloc(self.w * self.h * sizeof *self.cache)
        if self.value_cb:
            for int y in range(self.h):
                for int x in range(self.w):
                    self.cache[x + self.w * y] = self.value_cb(self, x, y, self.user)

    if self.shape:
        for int y in range(self.h):
            for int x in range(self.w):
                float p = self.cache[x + self.w * y]
                float dx = (x * 2.0 - self.w) / self.w
                float dy = (y * 2.0 - self.h) / self.h
                float d = 1
                if self.shape == LandNoiseShapeDistance:
                    d -= 2 * sqrt(dx * dx + dy * dy)
                elif self.shape == LandNoiseShapeSquared:
                    d -= 2 * (dx * dx + dy * dy)
                elif self.shape == LandNoiseShapeDiamond:
                    d -= max(fabs(dx), fabs(dy))
                elif self.shape == LandNoiseShapeCos:
                    d -= 2 * sin(sqrt(dx * dx + dy * dy) * pi / 2)
                float v = d * self.shape_amount + p * (1 - self.shape_amount)
                if v < 0: v = -1
                self.cache[x + self.w * y] = v

def _multires_cache(LandNoise *self):
    self.cache = land_malloc(self.w * self.h * sizeof *self.cache)
    for int y in range(self.h):
        for int x in range(self.w):
            float v = 0.0
            int i = 0
            for void *noise in LandArray *self.noise:
                float val = _get_resolution(self, noise, i, x, y)
                float s = pow(2 + self.power_modifier, self.amplitude - i)
                if s < 1.0 / 128: break
                v += val * s
                i++
            self.cache[x + self.w * y] = v

def _get_resolution(LandNoise *self, void *sub, int i, x, y) -> float:
    if self.t == LandNoisePerlin:
        LandPerlin *sub2 = sub
        return land_perlin_at(
            sub2, (float)x * sub2.w / self.w, (float)y * sub2.h / self.h)
    return 0

def land_noise_transfer_callback(LandNoise *self, float (*cb)(float x)):
    self.transfer_cb = cb
    
def land_noise_value_callback(LandNoise *self, float (*cb)(
        LandNoise *noise, int x, int y, void *user), void *user):
    self.value_cb = cb
    self.user = user

def land_noise_destroy(LandNoise *self):
    if self.seed and not self.use_external_seed:
        land_random_del(self.seed)
    land_free(self)

def land_noise_at(LandNoise *self, float x, y) -> LandFloat:
    LandFloat v = land_noise_at_raw(self, x, y)
    if self.transfer_cb:
        v = self.transfer_cb(v)
    LandFloat v2 =  v * self.z_scale + self.z_offset
    if self.z_ease > 0.0000001:
        LandFloat v3 = 1 - cos(v2 * LAND_PI / 2)
        if v2 < 0: v3 = -v3
        v2 = v2 * (1 - self.z_ease) + v3 * self.z_ease
    if v2 < self.minval: v2 = self.minval
    if v2 > self.maxval: v2 = self.maxval
    return v2

def _get_int_pos(LandNoise *self, float x, y, int *x_out, *y_out):
    int ix = floor(x)
    int iy = floor(y)
    if self.wrap:
        ix %= self.w
        if ix < 0: ix += self.w
        iy %= self.h
        if iy < 0: iy += self.h
    else:
        if ix < 0: ix = 0
        if iy < 0: iy = 0
        if ix > self.w - 1: ix = self.w - 1
        if iy > self.h - 1: iy = self.h - 1
    *x_out = ix
    *y_out = iy

def land_noise_at_raw(LandNoise *self, float x, y) -> LandFloat:

    if self.warp:
        LandNoise *warp = land_array_get_nth(self.noise, 0)
        LandFloat qx = land_noise_at(warp, x, y)
        LandFloat qy = land_noise_at(warp, x + self.warp_x, y + self.warp_y)
        LandFloat v = land_noise_at(warp, x + self.warp_sx * qx, y + self.warp_sy * qy)
        return v

    if self.blur or self.t == LandNoiseWhite or self.t == LandNoisePerlin or self.t == LandNoiseValue:
        int ix, iy
        _get_int_pos(self, x, y, &ix, &iy)
        return self.cache[ix + iy * self.w]

    if self.t == LandNoiseVoronoi:
        int ix, iy
        _get_int_pos(self, x, y, &ix, &iy)
        return land_voronoi_at(land_array_get_nth(self.noise, 0), ix, iy)
    if self.t == LandNoisePlasma:
        return land_plasma_at(land_array_get_nth(self.noise, 0), x, y)
    if self.t == LandNoiseWaves:
        return _waves_at(land_array_get_nth(self.noise, 0), self.power_modifier, self.amplitude, x, y)
    return 0

def _waves_create(LandNoise *noise, int w, h) -> void*:
    Waves *waves; land_alloc(waves)
    waves.count = noise.count
    waves.xy = land_calloc(noise.count * 2 * sizeof*waves.xy)
    for int i in range(noise.count):
        waves.xy[i + i + 0] = land_random_f(noise.seed, 0, w)
        waves.xy[i + i + 1] = land_random_f(noise.seed, 0, h)
    return waves

def _waves_at(Waves *self, float power_modifier, amplitude, int x, y) -> float:
    float v = 0
    for int i in range(self.count):
        float dx = self.xy[i + i + 0] - x
        float dy = self.xy[i + i + 1] - y
        v += power_modifier * sin(amplitude * sqrt(dx * dx + dy * dy))
    return v

def land_noise_z_transform(LandNoise *self, float scale, offset):
    self.z_scale = scale
    self.z_offset = offset

def land_noise_z_ease(LandNoise *self, float x):
    self.z_ease = x
