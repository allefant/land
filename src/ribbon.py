import mem
import math
static import land.util2d
import land.color
static import global allegro5.allegro5
static import global allegro5.allegro_primitives

class LandRibbon:
    int n
    int subdiv
    float *xy

    int cn
    float *colors
    float *pos

    int wn
    float *w
    float *wpos

    bool loop
    bool filled
    bool fan
    float min_segment_distance

    bool calculated
    int vertex_count
    float *v
    float *vcol
    float *midxy # x/y coordinate of each segment start

    int segments
    # length[0] is always 0
    # length[1] is the length of the first segment
    # length[2] is the length of first and second segment
    # ...
    # length[segments] is the total length
    float *length

def land_ribbon_new(int n, subdiv, const float *xy) -> LandRibbon*:
    LandRibbon *self; land_alloc(self)
    self.n = n
    self.subdiv = subdiv
    self.xy = land_duplicate_bytes(xy, n * 2 * sizeof *xy)
    return self

def land_ribbon_new_empty(int subdiv) -> LandRibbon*:
    LandRibbon *self; land_alloc(self)
    self.n = 0
    self.subdiv = subdiv
    self.xy = None
    return self

def land_ribbon_add(LandRibbon *self, float x, y):
    int i = self.n
    self.n += 1
    self.xy = land_realloc(self.xy, self.n * 2 * sizeof *self.xy)
    self.xy[i * 2 + 0] = x
    self.xy[i * 2 + 1] = y

def land_ribbon_destroy(LandRibbon *self):
    if self.xy: land_free(self.xy)
    if self.v: land_free(self.v)
    if self.vcol: land_free(self.vcol)
    if self.length: land_free(self.length)
    if self.colors: land_free(self.colors)
    if self.pos: land_free(self.pos)
    if self.w: land_free(self.w)
    if self.wpos: land_free(self.wpos)
    land_free(self)

def land_ribbon_gradient(LandRibbon *self, int cn, const float *rgba, *pos):
    self.cn = cn
    self.colors = land_duplicate_bytes(rgba, cn * 4 * sizeof *rgba)
    if pos:
        self.pos = land_duplicate_bytes(pos, cn * sizeof *pos)
    else:
        self.pos = _even_positions(cn)

def land_ribbon_color(LandRibbon *self, LandColor c):
    land_ribbon_gradient(self, 2, (float[]){c.r, c.g, c.b, c.a, c.r,
        c.g, c.b, c.a}, (float[]){0, 1})

def land_ribbon_twocolor(LandRibbon *self, LandColor c1, c2):
    land_ribbon_gradient(self, 2, (float[]){c1.r, c1.g, c1.b, c1.a,
        c2.r, c2.g, c2.b, c2.a}, (float[]){0, 1})

def land_ribbon_color_names(LandRibbon *self, char const* names):
    self.cn = 1 + land_count(names, ",")
    land_alloc_array(self.colors, self.cn * 4)
    self.pos = _even_positions(self.cn)
    char const *s = names
    for int i in range(self.cn):
        int p = land_find(s, ",")
        if p == -1: p = strlen(s)
        char name[p + 1]
        land_copy_bytes(name, s, p)
        name[p] = 0
        LandColor c = land_color_name(name)
        self.colors[i * 4 + 0] = c.r
        self.colors[i * 4 + 1] = c.g
        self.colors[i * 4 + 2] = c.b
        self.colors[i * 4 + 3] = c.a
        s += p + 1

def land_ribbon_width(LandRibbon *self, float w):
    land_ribbon_thickness(self, 2, (float[]){w, w}, (float[]){0, 1})

def land_ribbon_width_from_to(LandRibbon *self, float w1, w2):
    land_ribbon_thickness(self, 2, (float[]){w1, w2}, (float[]){0, 1})

def land_ribbon_thickness(LandRibbon *self, int wn, const float *w, *p):
    self.wn = wn
    self.w = land_duplicate_bytes(w, wn * sizeof *w)
    if p:
        self.wpos = land_duplicate_bytes(p, wn * sizeof *p)
    else:
        self.wpos = _even_positions(wn)

def _even_positions(int n) -> float*:
    float *pos = land_malloc(sizeof(float) * n)
    for int i in range(n):
        pos[i] = 1.0 * i / (n - 1)
    return pos

def land_ribbon_calculate(LandRibbon *ribbon):
    ribbon.calculated = True
    int n = ribbon.n
    int subdiv = ribbon.subdiv
    const float *xy = ribbon.xy
    int cn = ribbon.cn
    const float *rgba = ribbon.colors
    const float *pos = ribbon.pos

    # For n points we get to draw n-1 spline segments. For example if we
    # have 3 points there is 2 spline segments.
    # For each spline segment we add (q - 1) * 2 polygon points. For example if
    # q is 2 then we add 2 points for each segment. 
    # So in total: (n - 1) * (q - 1) * 2

    int n2 = n
    if ribbon.loop:
        n2 += 1
    int points = n2 * subdiv * 2
    ribbon.v = land_malloc(sizeof(float) * points * 2)
    ribbon.vcol = land_malloc(sizeof(float) * points * 4)

    int skip = 0
    int segments = (subdiv - 1) * (n2 - 1)
    ribbon.midxy = land_malloc(sizeof(float) * 2 * (segments + 1))
    int posmid = 0
    #int posrgba = 0
    for int i in range(0, n2 - 1):
        float xy8[8]
        #                         .c2
        #                        .
        #                   i+1 .___________ i+2
        #                      / c3
        #                     /
        #                    /
        #      ____________./ c0
        #     i-1         . i
        #                .
        #               c1
        #

        int i_n = (i + 1) % n

        xy8[0] = xy[i * 2 + 0]
        xy8[1] = xy[i * 2 + 1]
        xy8[2] = xy[i * 2 + 0]
        xy8[3] = xy[i * 2 + 1]
        xy8[4] = xy[i_n * 2 + 0]
        xy8[5] = xy[i_n * 2 + 1]
        xy8[6] = xy[i_n * 2 + 0]
        xy8[7] = xy[i_n * 2 + 1]

        float ex = xy8[0] - xy8[6]
        float ey = xy8[1] - xy8[7]
        float e = sqrt(ex * ex + ey * ey)
        
        e *= 0.33

        if i > 0 or ribbon.loop:
            int i1 = (i + n - 1) % n
            float dx = xy[i_n * 2 + 0] - xy[i1 * 2 + 0]
            float dy = xy[i_n * 2 + 1] - xy[i1 * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[2] += e * dx / d
            xy8[3] += e * dy / d
        
        if i < n2 - 2 or ribbon.loop:
            int i2 = (i_n + 1) % n
            float dx = xy[i * 2 + 0] - xy[i2 * 2 + 0]
            float dy = xy[i * 2 + 1] - xy[i2 * 2 + 1]
            float d = sqrt(dx * dx + dy * dy)
            xy8[4] += e * dx / d
            xy8[5] += e * dy / d

        float new_points[subdiv * 2]
        al_calculate_spline(new_points, 2 * sizeof(float), xy8, 0, subdiv)

        int j = 0
        ribbon.midxy[posmid + 0] = new_points[j * 2 + 0]
        ribbon.midxy[posmid + 1] = new_points[j * 2 + 1]
        posmid += 2
        for j in range(1, subdiv - 1):
            float x = new_points[j * 2 + 0]
            float y = new_points[j * 2 + 1]
            float dx = x - ribbon.midxy[posmid - 2 + 0]
            float dy = y - ribbon.midxy[posmid - 2 + 1]
            float d = sqrtf(dx * dx + dy * dy)
            if ribbon.min_segment_distance and d < ribbon.min_segment_distance:
                skip += 1
                continue
            ribbon.midxy[posmid + 0] = x
            ribbon.midxy[posmid + 1] = y
            posmid += 2

        j = subdiv - 1
        ribbon.midxy[posmid + 0] = new_points[j * 2 + 0]
        ribbon.midxy[posmid + 1] = new_points[j * 2 + 1]
        # posmid is not advanced for last one, so the next segment start
        # overwrites the previous end, except for the very last one

    segments -= skip
    ribbon.vertex_count = segments * 2 + 2
    ribbon.segments = segments
    ribbon.length = land_malloc(sizeof(float) * (segments + 1))
    float *length = ribbon.length
    length[0] = 0
    for int i in range(1, segments + 1):
        float x1, y1, x2, y2
        _get_mid_xy(ribbon, i - 1, &x1, &y1)
        _get_mid_xy(ribbon, i, &x2, &y2)
        double d = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))
        length[i] = length[i - 1] + d

    float rgba3[segments * 4 + 4]
    if rgba:
        _assign_gradient(cn, rgba, pos, segments + 1, length, rgba3)

    if ribbon.filled:
        if ribbon.fan: _apply_filled_fan(ribbon)
        else: _apply_filled_strip(ribbon)
    elif ribbon.w:
        _apply_thickness(ribbon)

    if not ribbon.filled:
        for int i in range(segments + 1):
            _copy4(ribbon.vcol + i * 2 * 4 + 0, rgba3 + i * 4)
            _copy4(ribbon.vcol + i * 2 * 4 + 4, rgba3 + i * 4)

def _apply_filled_strip(LandRibbon *self):
    #
    # 0   1   2   3   4
    #
    # 9   8   7   6   5
    #
    # 091 8 2 7 3 6 4 5
    float *v = self.v
    float *vcol = self.vcol
    float l = self.length[self.segments - 1]
    _get_mid_xy(self, self.segments - 1, v + 0, v + 1)
    _get_mid_xy(self, 0, v + 2, v + 3)
    float l1 = 0, l2 = self.length[self.segments - 1]
    land_ribbon_get_color(self, l2 / l,  vcol + 0)
    land_ribbon_get_color(self, l1 / l,  vcol + 4)
    int vc = 2
    v += 4
    vcol += 8
    for int i in range(1, self.segments - 1):
        if self.segments - 1 - i <= i - 1: break
        _get_mid_xy(self, self.segments - 1 - i, v + 0, v + 1)
        l2 = self.length[self.segments - 1 - i]
        land_ribbon_get_color(self, l2 / l, vcol)
        v += 2
        vc += 1
        vcol += 4
        if self.segments - 1 - i <= i: break
        _get_mid_xy(self, i, v + 0, v + 1)
        l1 = self.length[i]
        land_ribbon_get_color(self, l1 / l, vcol)
        v += 2
        vc += 1
        vcol += 4

    self.vertex_count = vc

def _apply_filled_fan(LandRibbon *self):
    # fixme
    pass

def _apply_thickness(LandRibbon *self):
    for int i in range(0, self.segments + 1):
        float lx, ly, rx, ry
        float w = land_ribbon_get_width(self, self.length[i] / self.length[self.segments])

        if i == 0:
            float x, y, nx, ny
            _get_mid_xy(self, i, &x, &y)
            _get_mid_norm(self, i, &nx, &ny)
            rx = x + nx * w
            ry = y + ny * w
            lx = x - nx * w
            ly = y - ny * w
        elif i == self.segments:
            float x, y, nx, ny
            _get_mid_xy(self, i, &x, &y)
            _get_mid_norm(self, self.segments, &nx, &ny)
            rx = x + nx * w
            ry = y + ny * w
            lx = x - nx * w
            ly = y - ny * w
        else:
            _get_intersection(self, i, -w, &lx, &ly)
            _get_intersection(self, i, +w, &rx, &ry)

        self.v[i * 4 + 0] = rx
        self.v[i * 4 + 1] = ry
        self.v[i * 4 + 2] = lx
        self.v[i * 4 + 3] = ly

def _get_mid_xy(LandRibbon *self, int segment, float *x, *y):
    if segment > self.segments:
        print("wrong segment %d > %d", segment, self.segments)
        return
    *x = self.midxy[segment * 2 + 0]
    *y = self.midxy[segment * 2 + 1]

def _get_intersection(LandRibbon *self, int segment, float offset, float *x, *y):
    float xn, yn, xp, yp, xi, yi, nx1, ny1, nx2, ny2, dx1, dy1, dx2, dy2
    int i = segment
    int p = i - 1
    int n = i + 1
    #if i == 0: p = i
    #if i == self.segments: n = i
    _get_mid_xy(self, p, &xp, &yp)
    _get_mid_xy(self, i, &xi, &yi)
    _get_mid_xy(self, n, &xn, &yn)
    land_diffnormal2d(xp, yp, xi, yi, &dx1, &dy1)
    land_diffnormal2d(xi, yi, xn, yn, &dx2, &dy2)
    land_orthonormal2d(xi - xp, yi - yp, &nx1, &ny1)
    land_orthonormal2d(xn - xi, yn - yi, &nx2, &ny2)
    xp += nx1 * offset
    yp += ny1 * offset
    xi += nx2 * offset
    yi += ny2 * offset

    #x = xp + dx1 * u = xi + dx2 * v
    #y = yp + dy1 * u = yi + dy2 * v
    #1) u = (xi + dx2 * v - xp) / dx1
    #2) yp + dy1 * (xi + dx2 * v - xp) / dx1 = yi + dy2 * v
    # ) yp * dx1 + dy1 * (xi + dx2 * v - xp) = yi * dx1 + dy2 * v * dx1
    # ) yp * dx1 + dy1 * xi + dy1 * dx2 * v - dy1 * xp = yi * dx1 + dy2 * v * dx1
    # ) dy1 * dx2 * v - dy2 * v * dx1 = yi * dx1 - yp * dx1 - dy1 * xi + dy1 * xp
    # ) v = (yi * dx1 - yp * dx1 - xi * dy1 + xp * dy1) / (dy1 * dx2 - dy2 * dx1)

    LandFloat c = land_cross2d(dx2, dy2, dx1, dy1)
    if c * c < 0.0001: # parallel
        *x = xi
        *y = yi
        return
    *x = xi + dx2 * (yi * dx1 - yp * dx1 - xi * dy1 + xp * dy1) / c
    *y = yi + dy2 * (yi * dx1 - yp * dx1 - xi * dy1 + xp * dy1) / c

def _get_mid_norm(LandRibbon *self, int segment, float *nx, *ny):
    float xn, yn, xp, yp
    int c = self.segments
    int i = segment
    int ipr = i - 1
    int ine = i + 1
    if self.loop:
        if i == 0: ipr = (ipr + c) % c
        if i == self.segments: ine = ine % c
    else:
        if i == 0: ipr = i
        if i == c: ine = i
    _get_mid_xy(self, ipr, &xp, &yp)
    _get_mid_xy(self, ine, &xn, &yn)
    land_orthonormal2d(xn - xp, yn - yp, nx, ny)

def land_ribbon_get_subdivision_pos(LandRibbon *self, int sd, float *x, *y):
    if not self.calculated:
        land_ribbon_calculate(self)
    _get_mid_xy(self, sd, x, y)
    
def land_ribbon_get_subdivision_normal(LandRibbon *self, int sd, float *nx, *ny):
    if not self.calculated:
        land_ribbon_calculate(self)
    _get_mid_norm(self, sd, nx, ny)

def land_ribbon_length(LandRibbon *self) -> float:
    if not self.calculated:
        land_ribbon_calculate(self)
    return self.length[self.segments]

def land_ribbon_get_pos(LandRibbon *self, float pos, *x, *y):
    if not self.calculated:
        land_ribbon_calculate(self)
    if pos < 0:
        float rp = pos * self.length[self.segments]
        float x1, y1, x2, y2
        _get_mid_xy(self, 0, &x1, &y1)
        _get_mid_xy(self, 1, &x2, &y2)
        float dx = x2 - x1
        float dy = y2 - y1
        float d = sqrt(dx * dx + dy * dy)
        *x = x1 + rp * dx / d
        *y = y1 + rp * dy / d
        return
    float pp = 0
    for int i in range(1, self.segments + 1):
        float p = self.length[i] / self.length[self.segments]
        if pos <= p:
            float x1, y1, x2, y2
            _get_mid_xy(self, i - 1, &x1, &y1)
            _get_mid_xy(self, i, &x2, &y2)
            float pd = (pos - pp) / (p - pp)
            *x = x1 + (x2 - x1) * pd
            *y = y1 + (y2 - y1) * pd
            return
        pp = p
    # past last point
    float rp = (pos - 1) * self.length[self.segments]
    float x1, y1, x2, y2
    _get_mid_xy(self, self.segments - 1, &x1, &y1)
    _get_mid_xy(self, self.segments, &x2, &y2)
    float dx = x2 - x1
    float dy = y2 - y1
    float d = sqrt(dx * dx + dy * dy)
    *x = x2 + rp * dx / d
    *y = y2 + rp * dy / d

def land_ribbon_get_normal(LandRibbon *self, float pos, *nx, *ny):
    # fixme: calculate normals in the bezier function
    if not self.calculated:
        land_ribbon_calculate(self)
    if pos < 0:
        _get_mid_norm(self, 0, nx, ny)
        return
    for int i in range(1, self.segments + 1):
        float p = self.length[i] / self.length[self.segments]
        if pos <= p:
            _get_mid_norm(self, i - 1, nx, ny)
            return
    # past last point
    _get_mid_norm(self, self.segments, nx, ny)

def _copy4(float *a, const float *b):
    memcpy(a, b, sizeof(float) * 4)

def _get_gradient(float p, int cn, const float *rgba, *pos, float *to):
    if p < pos[0]: # first offset > 0 and we are before it
        _copy4(to, rgba)
        return
    int a = -1, b = -1
    for int i in range(1, cn):
        if p < pos[i]:
            a = i - 1
            b = i
            break
    if a < 0: # past last offset
        _copy4(to, rgba + (cn - 1) * 4)
        return
    float x = (p - pos[a]) / (pos[b] - pos[a])
  
    to[0] = rgba[a * 4 + 0] * (1 - x) + rgba[b * 4 + 0] * x
    to[1] = rgba[a * 4 + 1] * (1 - x) + rgba[b * 4 + 1] * x
    to[2] = rgba[a * 4 + 2] * (1 - x) + rgba[b * 4 + 2] * x
    to[3] = rgba[a * 4 + 3] * (1 - x) + rgba[b * 4 + 3] * x

def land_ribbon_get_color(LandRibbon *self, float p, *rgba):
    _get_gradient(p, self.cn, self.colors, self.pos, rgba)

def land_ribbon_get_width(LandRibbon *self, float p) -> float:
    if p < self.wpos[0]:
        return self.w[0]
    int a = -1, b = -1
    for int i in range(1, self.wn):
        if p < self.wpos[i]:
            a = i - 1
            b = i
            break
    if a < 0: # past last offset
        return self.w[self.wn - 1]
    float x = (p - self.wpos[a]) / (self.wpos[b] - self.wpos[a])
    # fixme: use quadratic interpolation not linear
    return self.w[a] * (1 - x) + self.w[b] * x

def _assign_gradient(int cn, const float *rgba, const float *pos, int segments, float *length, float *rgba3):
    # given cn rgba[cn*4] colors and pos[cn] offsets for a gradient,
    # apply it to another color array rgba3[segments*4] with (normally) more segments

    _copy4(rgba3 + 0, rgba + 0)
    for int i in range(1, segments):
        float p = length[i] / length[segments - 1] # fixme: should this be sements?
        _get_gradient(p, cn, rgba, pos, rgba3 + i * 4)
