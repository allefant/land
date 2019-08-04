import land.land

class Rivers:
    LandNoise *noise
    LandNoise *count
    int w, h
    int *add
    int *end
    float snow_height
    float water_height

class End:
    int x, y
    int volume
    int length

def _get(Rivers* r, int *a, x, y) -> int:
    return a[((y + r.h) % r.h) * r.w + ((x + r.w) % r.w)]

def _move(Rivers *r, int *x, *y) -> bool:
    float v = land_noise_at(r.noise, *x, *y)
    if v <= r.water_height: return False
    float a = land_noise_at(r.noise, *x + 1, *y)
    float b = land_noise_at(r.noise, *x, *y + 1)
    float c = land_noise_at(r.noise, *x - 1, *y)
    float d = land_noise_at(r.noise, *x, *y - 1)

    float mab = min(a, b)
    float mcd = min(c, d)
    float m = min(mab, mcd)

    if m >= v: return False

    if a == m: (*x)++
    elif b == m: (*y)++
    elif c == m: (*x)--
    elif d == m: (*y)--
    else: return False
    return True

def _move_reverse(Rivers *r, int *x, *y) -> bool:
    #int av = _get(r, r.add, *x, *y)
    int aa = _get(r, r.add, *x + 1, *y)
    int ab = _get(r, r.add, *x, *y + 1)
    int ac = _get(r, r.add, *x - 1, *y)
    int ad = _get(r, r.add, *x, *y - 1)

    float v = land_noise_at(r.noise, *x, *y)
    float a = land_noise_at(r.noise, *x + 1, *y)
    float b = land_noise_at(r.noise, *x, *y + 1)
    float c = land_noise_at(r.noise, *x - 1, *y)
    float d = land_noise_at(r.noise, *x, *y - 1)

    if v >= r.snow_height: return False

    if a < v: aa = 0
    if b < v: ab = 0
    if c < v: ac = 0
    if d < v: ad = 0

    int maaab = max(aa, ab)
    int macad = max(ac, ad)
    int am = max(maaab, macad)
    if am == 0: return False

    if am == aa: (*x)++
    elif am == ab: (*y)++
    elif am == ac: (*x)--
    elif am == ad: (*y)--
    else: return True

    return True

def _endcomp(void const *a, void const *b) -> int:
    End* ae = *(End**)a
    End* be = *(End**)b
    if ae.volume > be.volume: return -1
    if ae.volume < be.volume: return 1
    return 0

def find_closest_under(LandNoise *noise, float h, int *x, *y) -> bool:
    """
      b
     bab       
    ba*1234      
     ba234
      b34
      c4
      d
    """
    int qx[] = {-1, -1, 1, 1}
    int qy[] = {1, -1, -1, 1}
    for int r in range(30):
        int rx = *x + r
        int ry = *y
        for int q in range(4):
            for int s in range(r):
                float v = land_noise_at(noise, rx, ry)
                if v < h:
                    *x = rx
                    *y = ry
                    return True
                rx += qx[q]
                ry += qy[q]
    return False

def rivers(LandNoise *noise, float water_height, snow_height) -> LandNoise*:
    int w = noise.w
    int h = noise.h

    Rivers r
    
    LandNoise *count = land_noise_new(LandNoiseValue, 0)
    land_noise_set_size(count, w, h)
    land_noise_prepare(count)

    r.noise = noise
    r.count = count
    r.add = land_calloc(w * h * sizeof*r.add)
    r.end = land_calloc(w * h * sizeof*r.end)
    r.w = w
    r.h = h
    r.snow_height = snow_height
    r.water_height = water_height
    
    for int y in range(h):
        for int x in range(w):
            int rx = x
            int ry = y
            float v = land_noise_at(noise, rx, ry)
            if v < snow_height: continue
            r.add[rx + w * ry]++
            int l = 0
            while True:
                while _move(&r, &rx, &ry):
                    rx = (rx + w) % w
                    ry = (ry + h) % h
                    r.add[rx + w * ry]++
                    l += 1
                r.end[rx + w * ry] += l
                v = land_noise_at(noise, rx, ry)
                if v <= water_height:
                    break
                int tx = rx
                int ty = ry
                if not find_closest_under(noise, v, &tx, &ty):
                    break
                rx = (tx + w) % w
                ry = (ty + h) % h

    LandArray *ends = land_array_new()
    for int y in range(h):
        for int x in range(w):
            if r.end[x + w * y] == 0: continue
            End *end; land_alloc(end)
            end.x = x
            end.y = y
            end.volume = r.end[x + w * y]
            land_array_add(ends, end)

    land_array_sort(ends, _endcomp)
    int e = 0
    #printf("rivers:\n")
    for End*end in LandArray *ends:
        if end.volume > 5000 or e < 5:
            int rx = end.x
            int ry = end.y
            while _move_reverse(&r, &rx, &ry):
                rx = (rx + w) % w
                ry = (ry + h) % h
                end.length++
        e++

    for End*end in LandArray *ends:
        if end.length < 10: continue
        #printf("%d %d %d %d\n", end.x, end.y, end.volume, end.length)
        int rx = end.x
        int ry = end.y
        while _move_reverse(&r, &rx, &ry):
            rx = (rx + w) % w
            ry = (ry + h) % h
            r.add[rx + w * ry] = 0
            _paint(count, rx, ry)

    return count

def _paint(LandNoise *noise, int x, y):
    int r = 5
    for int v in range(-r, r + 1):
        for int u in range(-r, r + 1):
            int dd = u * u + v * v
            if dd > r * r: continue
            int rx = (x + u + noise.w) % noise.w
            int ry = (y + v + noise.h) % noise.h
            float a = noise.cache[rx + ry * noise.w]
            float v = r - sqrt(dd)
            v /= r
            v = pow(v, 2) / 2
            a = max(a, v)
            noise.cache[rx + ry * noise.w] = a
                
