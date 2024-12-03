import common
import land.image
import land.display
import global math

def land_image_blur_rgba(uint8_t *rgba, int w, h, double blur_size) -> uint8_t*:
    
    float *cache = land_malloc(w * h * sizeof(float) * 4)

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
            for int c in range(4):
                double s = 0, a = 0
                for int v in range(fs):
                    int tx = x
                    int ty = y + v - fs / 2
                    double b = filteri[v]
                    a += b
                    if ty < 0: ty = 0
                    if ty > h - 1: ty = h - 1
                    s += rgba[ty * w * 4 + tx * 4 + c] / 255.0 * b
                cache[x * 4 + w * y * 4 + c] = s / a

    for int y in range(h):
        for int x in range(w):
            for int c in range(4):
                double s = 0, a = 0
                for int u in range(fs):
                    int tx = x + u - fs / 2
                    int ty = y
                    double b = filteri[u]
                    a += b
                    if tx < 0: tx = 0
                    if tx > w - 1: tx = w - 1
                    s += cache[ty * w * 4 + tx * 4 + c] * b
                rgba[x * 4 + w * y * 4 + c] = s / a * 255

    land_free(cache)
    return rgba

def land_image_blur(LandImage *image, double blur_size):
    int w = land_image_width(image)
    int h = land_image_height(image)
    uint8_t *rgba = land_malloc(w * h * 4)
    land_image_get_rgba_data(image, rgba)
    land_image_blur_rgba(rgba, w, h, blur_size)
    land_image_set_rgba_data(image, rgba)
    land_free(rgba)

def land_spiral_reveal(LandImage *cover, float rw, rh, float p):
    if p > 1: p = 1
    (int w, h) = land_image_size(cover)
    int cx = w // 2
    int cy = h // 2
    land_set_image_display(cover)
    land_blend(LAND_BLEND_SOLID)
    int total = 0
    int n = h / rh * 1.3
    int first = 1
    int counter = 0
    for int i in range(1, n):
        float circum = i * rh * 2 * pi
        int n2 = circum / rw
        total += n2

    total *= p

    int c2 = 0
    for int i in range(1, n):
        float circum = i * rh * 2 * pi
        int n2 = circum / rw
        c2 += n2
        if i > 1 and c2 < total:
            first = i - 1
            counter = c2 - n2

    land_set_transparent()
    n = w / rw
    for int i in range(first, n):
        float circum = i * rh * 2 * pi
        int n2 = circum / rw
        for int j in range(n2):
            if counter >= total:
                break
            float a0 = j * 2 * pi / n2
            float a1 = (j + 1) * 2 * pi / n2
            float rh0 = i * rh + rh * j / n2
            float rh1 = i * rh + rh * (j + 1) / n2
            float x1 = cx + cos(a0) * rh0
            float y1 = cy + sin(a0) * rh0 * h / w
            float x2 = cx + cos(a1) * rh1
            float y2 = cy + sin(a1) * rh1 * h / w
            land_filled_triangle(cx, cy, x1, y1, x2, y2)
            counter += 1
    land_unset_image_display()

def _gradient_step(LandFloat x) -> LandFloat:
    if x < 0.5: return 0
    return 1

def _gradient_circular(LandFloat x) -> LandFloat:
    return 1 - sqrt(1 - x * x)

def _gradient_square(LandFloat x) -> LandFloat:
    return x * x

def _gradient_linear(LandFloat x) -> LandFloat:
    return x

def _gradient_root(LandFloat x) -> LandFloat:
    return sqrt(x)

def _gradient_circular_inv(LandFloat x) -> LandFloat:
    return sqrt(1 - (1 - x) * (1 - x))

enum LandGradientType:
    LandGradientStep
    LandGradientCircular # slower than square
    LandGradientSquare # slower than linear
    LandGradientLinear
    LandGradientRoot # faster than linear
    LandGradientCircularInv # faster than root

LandFloat (*_funcs[])(LandFloat) = {
    _gradient_step,
    _gradient_circular,
    _gradient_square,
    _gradient_linear,
    _gradient_root,
    _gradient_circular_inv
}

def land_image_brush(LandColor color, float radius, LandGradientType lgt) -> LandImage*:
    int ri = ceil(radius)
    int w = ri + 1 + ri
    int h = w
    LandImage *image = land_image_new(w, h)
    byte *rgba = land_image_allocate_rgba_data(image)
    for int yi in range(h):
        int y = yi - ri
        for int xi in range(w):
            int x = xi - ri
            LandFloat d = sqrt(x * x + y * y) / radius
            LandFloat a = 1 - _funcs[lgt](d)
            if a < 0: a = 0
            byte *p = rgba + 4 * (yi * w + xi)
            p[0] = color.r * 255 * a
            p[1] = color.g * 255 * a
            p[2] = color.b * 255 * a
            p[3] = color.a * 255 * a
    land_image_set_rgba_data(image, rgba)
    land_free(rgba)
    return image

def land_image_blend_into(LandImage *a, *b, float left_x, left_p, right_x, right_p):
    """
    Draw image b over image a, with a blending gradient.
    """
    byte *rgba_a = land_image_allocate_rgba_data(a)
    byte *rgba_b = land_image_allocate_rgba_data(b)
    (int w, h) = land_image_size(a)
    int sx = w * left_x
    int ex = w * right_x
    for int yi in range(h):
        for int xi in range(w):
            float a = (xi - sx) * 1.0 / (ex - sx)
            if a < 0: a = 0
            if a > 1: a = 1
            float p = left_p * (1 - a) + right_p * a
            byte *pa = rgba_a + 4 * (yi * w + xi)
            byte *pb = rgba_b + 4 * (yi * w + xi)
            pa[0] = pa[0] * (1 - p) + pb[0] * p
            pa[1] = pa[1] * (1 - p) + pb[1] * p
            pa[2] = pa[2] * (1 - p) + pb[2] * p
            pa[3] = pa[3] * (1 - p) + pb[3] * p
    land_image_set_rgba_data(a, rgba_a)
    land_free(rgba_a)
    land_free(rgba_b)
