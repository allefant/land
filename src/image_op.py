import common
import land.image
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
