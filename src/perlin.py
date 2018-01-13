import global math
import mem
import util
import random
import noise

class LandPerlin:
    LandNoiseF2 *xy
    int w
    int h
    float (*lerp)(float a, float b, float p)

enum LandPerlinLerp:
    LandPerlinLerpNone
    LandPerlinLerpLinear
    LandPerlinLerpCosine
    LandPerlinLerpSmoothStep
    LandPerlinLerpSmootherStep
    LandPerlinLerpSmoothestStep

def _no_lerp(float a0, a1, w) -> float:
    return a0

def _linear_lerp(float a0, a1, w) -> float:
    return  a0 + (a1 - a0) * w

def _cosine_lerp(float a0, a1, w) -> float:
    float ft = w * LAND_PI
    float f = (1 - cos(ft)) * 0.5
    return  a0 * (1 - f) + a1 * f

def _smooth_step_lerp(float a0, a1, w) -> float:
    float f = w * w * (3 - 2 * w)
    return  a0 * (1 - f) + a1 * f

def _smoother_step_lerp(float a0, a1, w) -> float:
    float f = 6 * pow(w, 5) - 15 * pow(w, 4) + 10 * pow(w, 3)
    return  a0 * (1 - f) + a1 * f

def _smoothest_step_lerp(float a0, a1, w) -> float:
    float f = -20 * pow(w, 7) + 70 * pow(w, 6) - 84 * pow(w, 5) + 35 * pow(w, 4)
    return  a0 * (1 - f) + a1 * f

def land_perlin_create(int w, h) -> LandPerlin*:
    """
    Create a Perlin noise of the given resolution.

    The noise at any integer coordinate is always 0. Other coordinates
    return a random value in the range -1..1.

    If w and h are 1, each noise sample will have the identical vector
    at each corner.
    
    For point 0.5/0.5 this means:

    a = 0.5 * u + 0.5 * v
    b = -0.5 * u + 0.5 * v
    c = 0.5 * u + -0.5 * v
    d = -0.5 * u + -0.5 * v
    a + b + c + d = 0
    result = 0

    Also any other point:

    a = x * u + y * v
    b = -X * u + y * v
    c = x * u + -Y * v
    d = -X * u + -Y * v
    e = X * a + x * b = xX * u + yX * v + -xX * u + xy * v
    f = X * c + x * d = xX * u + -XY * v + -xX * u + -xY * v
    result = Y * e + y * f =
             xXY * u + yXY * v + -xXY * u + xyY * v + xXy * u + -XYy * v + -xXy * u + -xYy * v
             u * (xXY - xXY + xXy - xXy) + v * (yXY + xyY - XYy - xYy)
             u * 0 + v * 0
             0

    Note that this is not necessarily true for non-linear interpolation.
    """
    #printf("land_perlin_create %dx%d\n", w, h)
    LandPerlin *self; land_alloc(self)
    self.w = w
    self.h = h
    self.xy = land_calloc(w * h * sizeof *self.xy)
    for int j in range(h):
        for int i in range(w):
            float a = land_rnd(0, LAND_PI * 2)
            self.xy[i + j * w].x = cos(a)
            self.xy[i + j * w].y = sin(a)
    self.lerp = _cosine_lerp
    return self

def land_perlin_set_lerp_callback(LandPerlin *self, float (*lerp)(
        float a, float b, float p)):
    self.lerp = lerp

def land_perlin_set_lerp(LandPerlin *self, LandPerlinLerp lerp):
    if lerp == LandPerlinLerpNone: self.lerp = _no_lerp
    if lerp == LandPerlinLerpLinear: self.lerp = _linear_lerp
    if lerp == LandPerlinLerpCosine: self.lerp = _cosine_lerp
    if lerp == LandPerlinLerpSmoothStep: self.lerp = _smooth_step_lerp
    if lerp == LandPerlinLerpSmootherStep: self.lerp = _smoother_step_lerp
    if lerp == LandPerlinLerpSmoothestStep: self.lerp = _smoothest_step_lerp

def land_perlin_destroy(LandPerlin *self):
    land_free(self.xy)
    land_free(self)

def _gradient(LandPerlin *self, int x, y) -> LandNoiseF2*:
    x %= self.w
    if x < 0: x += self.w
    y %= self.h
    if y < 0: y += self.h
    return self.xy + x + y * self.w

def _dot(LandPerlin *self, int ix, iy, float x, y) -> float:
    float dx = x - ix
    float dy = y - iy

    auto g = _gradient(self, ix, iy)
    return dx * g.x + dy * g.y

def land_perlin_at(LandPerlin *self, float x, y) -> float:
    """
    Get a noise value from a Perlin noise. If x/y are not from inside
    the resolution of the noise they will wrap around.
    """
    int x0 = floor(x)
    int x1 = x0 + 1
    int y0 = floor(y)
    int y1 = y0 + 1
    float sx = x - x0
    float sy = y - y0

    float (*lerp)(float, float, float) = self.lerp

    float n0 = _dot(self, x0, y0, x, y)
    float n1 = _dot(self, x1, y0, x, y)
    float v0 = lerp(n0, n1, sx)
    float n2 = _dot(self, x0, y1, x, y)
    float n3 = _dot(self, x1, y1, x, y)
    float v1 = lerp(n2, n3, sx)
    float value = lerp(v0, v1, sy)

    return value

def land_perlin_displace(LandPerlin *self, float x, y, *xd, *yd):
    """
    Instead of getting the result of the Perlin noise at x/y, directly
    get the random displacement vector xd/yd.
    """
    int x0 = floor(x)
    int x1 = x0 + 1
    int y0 = floor(y)
    int y1 = y0 + 1
    float sx = x - x0
    float sy = y - y0

    float (*lerp)(float, float, float) = self.lerp

    auto g00 = _gradient(self, x0, y0)
    auto g10 = _gradient(self, x1, y0)
    auto g01 = _gradient(self, x0, y1)
    auto g11 = _gradient(self, x1, y1)

    float ix0, ix1
    ix0 = lerp(g00.x, g10.x, sx)
    ix1 = lerp(g01.x, g11.x, sx)
    *xd = lerp(ix0, ix1, sy)

    ix0 = lerp(g00.y, g10.y, sx)
    ix1 = lerp(g01.y, g11.y, sx)
    *yd = lerp(ix0, ix1, sy)
