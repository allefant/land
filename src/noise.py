import perlin
import voronoi
import plasma

enum LandNoiseType:
    LandNoiseNone
    LandNoiseWhite
    LandNoisePerlin
    LandNoiseVoronoi
    LandNoisePerlinMulti
    LandNoisePlasma

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
    float randomness
    float power_modifier
    float amplitude
    int lerp
    bool warp
    float warp_x, warp_y, warp_sx, warp_sy
    bool blur
    float blur_size

    float z_scale, z_offset, z_ease

    float *cache

def land_noise_new(LandNoiseType t) -> LandNoise*:
    LandNoise *self; land_alloc(self)

    self.t = t
    self.noise = land_array_new()

    self.count = 1
    self.levels = 1
    self.lerp = LandPerlinLerpCosine

    self.z_scale = 1

    return self

def land_noise_set_size(LandNoise *self, int w, h):
    self.w = w
    self.h = h

def land_noise_set_lerp(LandNoise *self, LandPerlinLerp lerp):
    self.lerp = lerp
    
def land_noise_set_count(LandNoise *self, int n):
    self.count = n

def land_noise_set_levels(LandNoise *self, int n):
    self.levels = n

def land_noise_set_amplitude(LandNoise *self, float amplitude):
    self.amplitude = amplitude

def land_noise_set_power_modifier(LandNoise *self, float power_modifier):
    self.power_modifier = power_modifier

def land_noise_set_randomness(LandNoise *self, float randomness):
    self.randomness = randomness

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

def _smoothen(LandNoise *self):

    int w = self->w
    int h = self->h

    float *temp = land_malloc(w * h * sizeof *temp)
    self.cache = land_malloc(w * h * sizeof *self.cache)

    for int y in range(self.h):
        for int x in range(self.w):
            temp[x + y *self.w] = land_noise_at(
                land_array_get_nth(self.noise, 0), x, y)
                    
    double sigma = self.blur_size
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
                ty %= h
                if ty < 0: ty += h
                s += temp[ty * w + tx] * b
            self.cache[x + w * y] = s / a

    for int y in range(h):
        for int x in range(w):
            double s = 0, a = 0
            for int u in range(fs):
                int tx = x + u - fs / 2
                int ty = y
                double b = filteri[u]
                a += b
                tx %= w
                if tx < 0: tx += w
                s += self.cache[ty * w + tx] * b
            temp[x + w * y] = s / a

    float *swap = self.cache
    self.cache = temp
    land_free(swap)

def _white(LandNoise *self):
    self.cache = land_malloc(self.w * self.h * sizeof *self.cache)

    for int y in range(self.h):
        for int x in range(self.w):
            self.cache[x + self.w * y] = land_rnd(-1, 1)

def land_noise_prepare(LandNoise *self):
    if self.warp:
        land_noise_prepare(land_array_get_nth(self.noise, 0))
        return

    if self.blur:
        land_noise_prepare(land_array_get_nth(self.noise, 0))
        _smoothen(self)
                
        return

    if self.t == LandNoiseWhite:
        _white(self)
        
    if self.t == LandNoiseVoronoi:
        void *noise = land_voronoi_create(self.w, self.h, self.count, self.randomness)
        land_array_add(self.noise, noise)
    if self.t == LandNoisePerlinMulti:
        int n = self.levels
        int w = 2
        int h = 2
        # if n is 0, there is no noise at all
        # if n is 1, we do a 2x2 Perlin - a 1x1 Perlin usually is
        # mostly just 0.
        # if n is 2+, do the same as for n == 1 but in each additional
        # level double the frequency and half the amplitude.
        
        for int i in range(0, n):
            LandPerlin *noise = land_perlin_create(w, h)
            land_perlin_set_lerp(noise, self.lerp)
            land_array_add(self.noise, noise)
            if w < self.w:
                w *= 2
            if h < self.h:
                h *= 2

        float fw = self.w
        float fh = self.h
        self.cache = land_malloc(self.w * self.h * sizeof *self.cache)
        for int y in range(fh):
            for int x in range(fw):
                float v = 0.0
                int i = 0
                for LandPerlin *noise in LandArray *self.noise:
                    int nw = noise.w
                    int nh = noise.h
                    float s = pow(2 + self.power_modifier, -i + self.amplitude)
                    if s < 1.0 / 128: break
                    v += land_perlin_at(noise, x * nw / fw, y * nh / fh) * s
                    i++
                self.cache[x + self.w * y] = v
        
    if self.t == LandNoisePlasma:
        void *noise = land_plasma_new(self.w, self.h, self.power_modifier, self.amplitude)
        land_plasma_generate(noise)
        land_array_add(self.noise, noise)

def land_noise_destroy(LandNoise *self):
    land_free(self)

def land_noise_at(LandNoise *self, float x, y) -> float:
    float v = land_noise_at_raw(self, x, y)
    float v2 =  v * self.z_scale + self.z_offset
    if self.z_ease > 0.0000001:
        float v3 = 1 - cos(v2 * LAND_PI / 2)
        if v2 < 0: v3 = -v3
        v2 = v2 * (1 - self.z_ease) + v3 * self.z_ease
    return v2

def land_noise_at_raw(LandNoise *self, float x, y) -> float:

    if self.warp:
        LandNoise *warp = land_array_get_nth(self.noise, 0)
        float qx = land_noise_at(warp, x, y)
        float qy = land_noise_at(warp, x + self.warp_x, y + self.warp_y)
        float v = land_noise_at(warp, x + self.warp_sx * qx, y + self.warp_sy * qy)
        return v

    if self.blur or self.t == LandNoiseWhite or self.t == LandNoisePerlinMulti:
        int ix = floor(x)
        int iy = floor(y)
        ix %= self.w
        if ix < 0: ix += self.w
        iy %= self.h
        if iy < 0: iy += self.h
        return self.cache[ix + iy * self.w]

    if self.t == LandNoiseVoronoi:
        return land_voronoi_at(land_array_get_nth(self.noise, 0), x, y)
    if self.t == LandNoisePlasma:
        return land_plasma_at(land_array_get_nth(self.noise, 0), x, y)
    return 0

def land_noise_z_transform(LandNoise *self, float scale, offset):
    self.z_scale = scale
    self.z_offset = offset

def land_noise_z_ease(LandNoise *self, float x):
    self.z_ease = x
