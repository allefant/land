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
    LandRandom *seed
    bool use_external_seed
    float randomness
    float power_modifier
    float amplitude
    int lerp
    bool warp
    float warp_x, warp_y, warp_sx, warp_sy
    bool blur
    float blur_size
    float minval, maxval
    bool wrap

    float z_scale, z_offset, z_ease

    float *cache

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

def land_noise_set_power_modifier(LandNoise *self, float power_modifier):
    self.power_modifier = power_modifier

def land_noise_set_randomness(LandNoise *self, float randomness):
    self.randomness = randomness

def land_noise_set_minmax(LandNoise *self, float minval, maxval):
    self.minval = minval
    self.maxval = maxval

def land_noise_set_warp(LandNoise *self, LandNoise *warp, float x, y, sx, sy):
    self.warp = True
    self.warp_x = x
    self.warp_y = y
    self.warp_sx = sx
    self.warp_sy = sy
    land_array_add(self.noise, warp)

def land_noise_set_blur(LandNoise *self, LandNoise *blur, int size):
    self.blur = True
    self.blur_size = size
    self.w = blur.w
    self.h = blur.h
    land_array_add(self.noise, blur)

def land_noise_set_wrap(LandNoise *self, bool wrap):
    self.wrap = wrap

def _smoothen(LandNoise *self):

    int w = self->w
    int h = self->h

    self.cache = land_malloc(w * h * sizeof *self.cache)

    for int y in range(self.h):
        for int x in range(self.w):
            self.cache[x + y *self.w] = land_noise_at(
                land_array_get_nth(self.noise, 0), x, y)

    _smoothen_temp(self.cache, w, h, self.blur_size, self.wrap)

def _smoothen_temp(float *noise, int w, h, blur_size, bool wrap):
    float *cache2 = land_malloc(w * h * sizeof *cache2)

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
            noise[x + w * y] = s / a

    land_free(cache2)

def _white(LandNoise *self) -> float*:
    float *noise = land_malloc(self.w * self.h * sizeof *noise)

    for int y in range(self.h):
        for int x in range(self.w):
            noise[x + self.w * y] = land_random_f(self.seed, -1, 1)

    return noise

def land_noise_prepare(LandNoise *self):
    if self.warp:
        land_noise_prepare(land_array_get_nth(self.noise, 0))
        return

    if self.blur:
        land_noise_prepare(land_array_get_nth(self.noise, 0))
        _smoothen(self)
        return

    if self.t == LandNoiseWhite:
        int w = self.w
        int h = self.h
        int n = self.levels
        int size = max(w, h) / 8
        for int i in range(n):
            float *noise = _white(self)
            _smoothen_temp(noise, w, h, size, self.wrap)
            land_array_add(self.noise, noise)
            size /= 2
            if size < 1: size = 1

        _multires_cache(self)
        
    if self.t == LandNoiseVoronoi:
        void *noise = land_voronoi_create(self.seed, self.w, self.h, self.count, self.randomness)
        land_array_add(self.noise, noise)
    if self.t == LandNoiseWaves:
        void *noise = _waves_create(self, self.w, self.h)
        land_array_add(self.noise, noise)
    if self.t == LandNoisePerlin:
        int n = self.levels
        int w = 1 << self.first_level
        int h = 1 << self.first_level
        # if n is 0, there is no noise at all
        # if n is 1, we do a 2x2 Perlin - a 1x1 Perlin usually is
        # mostly just 0.
        # if n is 2+, do the same as for n == 1 but in each additional
        # level double the frequency and half the amplitude.

        if self.h < self.w:
            w = h * self.w / self.h

        for int i in range(n):
            LandPerlin *noise = land_perlin_create(self.seed, w, h)
            land_perlin_set_lerp(noise, self.lerp)
            land_array_add(self.noise, noise)
            if w < self.w and h < self.h:
                w *= 2
                h *= 2

        _multires_cache(self)
        
    if self.t == LandNoisePlasma:
        void *noise = land_plasma_new(self.seed, self.w, self.h, self.power_modifier, self.amplitude)
        land_plasma_generate(noise)
        land_array_add(self.noise, noise)

    if self.t == LandNoiseValue:
        self.cache = land_calloc(self.w * self.h * sizeof *self.cache)

def _multires_cache(LandNoise *self):
    self.cache = land_malloc(self.w * self.h * sizeof *self.cache)
    for int y in range(self.h):
        for int x in range(self.w):
            float v = 0.0
            int i = 0
            for void *noise in LandArray *self.noise:
                float val = _get_resolution(self, noise, i, x, y)
                float s = pow(2 + self.power_modifier, -i + self.amplitude)
                if s < 1.0 / 128: break
                v += val * s
                i++
            self.cache[x + self.w * y] = v

def _get_resolution(LandNoise *self, void *sub, int i, x, y) -> float:
    if self.t == LandNoisePerlin:
        LandPerlin *sub2 = sub
        return land_perlin_at(
            sub2, (float)x * sub2.w / self.w, (float)y * sub2.h / self.h)
    if self.t == LandNoiseWhite:
        float *sub2 = sub
        float j = pow(self.w * self.h, 0.9) / pow(2, 10 + i)
        return sub2[x + self.w * y] * j
    return 0

def land_noise_callback(LandNoise *self, float (*cb)(float x)):
    for int y in range(self.h):
        for int x in range(self.w):
            self.cache[x + self.w * y] = cb(self.cache[x + self.w * y])

def land_noise_destroy(LandNoise *self):
    if self.seed and not self.use_external_seed:
        land_random_del(self.seed)
    land_free(self)

def land_noise_at(LandNoise *self, float x, y) -> float:
    float v = land_noise_at_raw(self, x, y)
    float v2 =  v * self.z_scale + self.z_offset
    if self.z_ease > 0.0000001:
        float v3 = 1 - cos(v2 * LAND_PI / 2)
        if v2 < 0: v3 = -v3
        v2 = v2 * (1 - self.z_ease) + v3 * self.z_ease
    if v2 < self.minval: v2 = self.minval
    if v2 > self.maxval: v2 = self.maxval
    return v2

def land_noise_at_raw(LandNoise *self, float x, y) -> float:

    if self.warp:
        LandNoise *warp = land_array_get_nth(self.noise, 0)
        float qx = land_noise_at(warp, x, y)
        float qy = land_noise_at(warp, x + self.warp_x, y + self.warp_y)
        float v = land_noise_at(warp, x + self.warp_sx * qx, y + self.warp_sy * qy)
        return v

    if self.blur or self.t == LandNoiseWhite or self.t == LandNoisePerlin or self.t == LandNoiseValue:
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
        return self.cache[ix + iy * self.w]

    if self.t == LandNoiseVoronoi:
        return land_voronoi_at(land_array_get_nth(self.noise, 0), x, y)
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
