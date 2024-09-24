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
