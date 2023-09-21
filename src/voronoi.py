import main
import noise
import external.delaunator
import land.util2d

class LandVoronoiNode:
    int x, y
    float cx, cy
    float v
    int b
    int neighbors_count
    int *neighbors
    LandFloat *edges
    bool is_edge # borders the outside, or with wrapping borders a wrapped cell
    int wrap_id # the cell id including wrapped cells, 0..n+en-1
    int id # the cell id from 0..n-1

class LandVoronoi:
    int *map # for each position the voronoi cell owner
    float *distance # for each position the distance to the cell center
    int *neighbor # for each position the owner of the closest neighbor cell center
    int n, en
    LandVoronoiNode *xy
    int w
    int h
    float max_distance
    float randomness
    LandRandom *seed
    bool wrap
    int center # 0=voronoi,1=centroid

    int voronoi_edges
    double voronoi_dist

    Delaunator *d
    LandBuffer *delaunay
    LandBuffer *extra # maps extra cells >=n to their real cell 0..n-1

    LandArray *polygons # LandVoronoiPolygon
    float border

class LandVoronoiPolygon:
    LandBuffer *xy

# static def wrap_distance(float x1, x2, wrap) -> float:
    # """
    # |x1    x2             |x1
    # |x1              x2   |x1
    # |x2              x1   |x2
    # """
    # float d = fabs(x2 - x1)
    # if d > wrap / 2:
        # d = wrap - d
    # return d

# def _wrap_diff(float x1, x2, wrap) -> float:
    # """
    # |x1    x2             |x1
    # |x1              x2   |x1
    # |x2              x1   |x2
    # """
    # float d = x2 - x1
    # if d > wrap / 2:
        # d = wrap - d
    # elif d < -wrap / 2:
        # d = wrap + d
    # return d

def _get_distance(LandVoronoi *self, int x, y, i) -> LandFloat:
    LandFloat dx = self.xy[i].x - x
    LandFloat dy = self.xy[i].y - y
    LandFloat d = sqrt(dx * dx + dy * dy)
    return d

def land_voronoi_new(LandRandom *seed, int w, h, n, bool wrap,
        int center, float randomness) -> LandVoronoi *:
    LandVoronoi *self; land_alloc(self)
    self.w = w
    self.h = h
    self.wrap = wrap
    self.center = center
    self.map = land_calloc(w * h * sizeof *self.map)
    self.distance = land_calloc(w * h * sizeof *self.distance)
    self.neighbor = land_calloc(w * h * sizeof *self.neighbor)
    self.n = n
    self.xy = land_calloc(n * sizeof *self.xy)
    self.max_distance = 0
    self.randomness = randomness
    self.seed = seed

    for int i in range(n):
        int x = land_random(seed, 0, w - 1)
        int y = land_random(seed, 0, h - 1)
        self.xy[i].x = x
        self.xy[i].y = y

    voronoi_recalculate_map(self)
    return self

# def _line_x(LandVoronoi *self, int c, x1, y1, x2, y2, n, xs, ys, float g):
    # """
    # 0/0 to 3/1
    # w = 3
    # xs = 1
    # g = 0.33
    # ys = 1
     # ________ ________ ________ ________ ________
    # |1       |        |        |        |        |
    # | f=0.5  | f=0.83 |        |        |        |
    # |        |        |        |        |        |
    # |________|________|________|________|________|
    # |        |        |        |2       |        |
    # |        |        | f=0.5  |        |        |
    # |        |        |        |        |        |
    # |________|________|________|________|________|
    # |        |        |        |        |        |
    # |        |        |        |        |        |
    # |        |        |        |        |        |
    # |________|________|________|________|________|
    # 0/0 to 4/2
    # w = 4
    # xs = 1
    # g = 0.5
    # ys = 1
     # ________ ________ ________ ________ ________
    # |1       |        |        |        |        |
    # |   f=0.5|        |        |        |        |
    # |        |        |        |        |        |
    # |________|________|________|________|________|
    # |        |        |        |        |        |
    # |        | f=0    | f=0.5  |        |        |
    # |        |        |        |        |        |
    # |________|________|________|________|________|
    # |        |        |        |        |2       |
    # |        |        |        | f=0    |        |
    # |        |        |        |        |        |
    # |________|________|________|________|________|
    # """
    # int x = x1
    # int y = y1
    # float f = 0.5
    # while n > 0:
        # if x >= 0 and y >= 0 and x < self.w and y < self.h:
            # self.map[x + self.w * y] = c
        # n -= 1
        # x += xs
        # f += g
        # if f > 1.0:
            # f -= 1.0
            # y += ys

# def _line_y(LandVoronoi *self, int c, x1, y1, x2, y2, n, xs, ys, float g):
    # int x = x1
    # int y = y1
    # float f = 0.5
    # while n > 0:
        # if x >= 0 and y >= 0 and x < self.w and y < self.h:
            # self.map[x + self.w * y] = c
        # n -= 1
        # y += ys
        # f += g
        # if f > 1.0:
            # f -= 1.0
            # x += xs

# def _line(LandVoronoi *self, int c, x1, y1, x2, y2):
    # int xs = 1
    # int ys = 1
    # int w = x2 - x1
    # int h = y2 - y1
    # if w < 0:
        # w = -w
        # xs = -1
    # if h < 0:
        # h = -h
        # ys = -1
    # if w > h:
        # _line_x(self, c, x1, y1, x2, y2, w, xs, ys, 1.0 * h / w)
    # else:
        # _line_y(self, c, x1, y1, x2, y2, h, xs, ys, 1.0 * w / h)

def _rot(int *x1, *y1, *x2, *y2, *x3, *y3)
    int tx = *x1
    int ty = *y1
    *x1 = *x2
    *y1 = *y2
    *x2 = *x3
    *y2 = *y3
    *x3 = tx
    *y3 = ty

def _swap(int *x1, *y1, *x2, *y2)
    int tx = *x1
    int ty = *y1
    *x1 = *x2
    *y1 = *y2
    *x2 = tx
    *y2 = ty

def _hline(LandVoronoi *self, int c, x1, y, x2):
    for int x = x1 while x < x2 with x += 1:
        if x >= 0 and y >= 0 and x < self.w and y < self.h:
            self.map[x + self.w * y] = c

static class Leg:
    float f
    float g
    int w, h
    int step
    int x
    int y2

def _leg(int x1, y1, x2, y2) -> Leg:
    Leg l
    l.f = 0.5
    l.w = x2 - x1
    l.h = y2 - y1
    l.step = 1
    if l.w < 0:
        l.w = -l.w
        l.step = -1
    l.g = l.w if l.h == 0 else 1.0 * l.w / l.h
    l.x = x1
    l.y2 = y2
    return l

def _leg_step(Leg *leg):
    leg.f += leg.g
    LandFloat a = floor(leg.f)
    leg.x += leg.step * (int)a
    leg.f -= a

def _triangle(LandVoronoi *self, int c, x1, y1, x2, y2, x3, y3):
    if y1 < y2:
        if y1 < y3: # 1 < 2,3
            pass
        else: # 3 < 1 < 2
            _rot(&x1, &y1, &x3, &y3, &x2, &y2)
    else:
        if y2 < y3: # 2 < 1, 3 
            _rot(&x1, &y1, &x2, &y2, &x3, &y3)
        else: # 3 < 2 < 1
            _rot(&x1, &y1, &x3, &y3, &x2, &y2)
    
    int y = y1
    if 1.0 * (x3 - x1) / (y3 - y1) < 1.0 * (x2 - x1) / (y2 - y1): _swap(&x2, &y2, &x3, &y3)
    Leg left = _leg(x1, y1, x2, y2)
    Leg right = _leg(x1, y1, x3, y3)
    int h = max(y2 - y1, y3 - y1)
    while h > 0:
        _leg_step(&left)
        _leg_step(&right)
        _hline(self, c, left.x, y, right.x)
        y += 1
        if y >= left.y2:
            left = _leg(x2, y2, x3, y3)
        elif y >= right.y2:
            right = _leg(x3, y3, x2, y2)
        h -= 1

# def _tri_callback(int a, b, c, void *user):
    # LandVoronoi *self = user
    # LandFloat *xy = self.d->coords->floats
    # int p[] = {a, b, c}
    # for int i in range(3):
        # int j = (i + 1) % 3
        # int x1 = xy[p[i] * 2 + 0]
        # int y1 = xy[p[i] * 2 + 1]
        # int x2 = xy[p[j] * 2 + 0]
        # int y2 = xy[p[j] * 2 + 1]
        # _line(self, 1, x1, y1, x2, y2)

def _cell_callback(int cell, LandFloat *xy, int *neighbors, int n,
        bool is_edge, void *user):
    LandVoronoi *self = user
    int x0 = self.d->coords->floats[cell * 2 + 0]
    int y0 = self.d->coords->floats[cell * 2 + 1]
    LandVoronoiNode *node = None
    
    node = self.xy + cell
    node.neighbors_count = n
    node.neighbors = land_malloc(n * sizeof(int))
    node.edges = land_malloc(n * 2 * sizeof(LandFloat))
    node.is_edge = is_edge
    node.wrap_id = cell
    if cell < self.n:
        node.id = cell
    else:
        node.id = land_buffer_get_uint32_by_index(self.extra, cell - self.n)

    for int i in range(n):
        int j = (i + 1) % n
        int x1 = xy[i * 2 + 0]
        int y1 = xy[i * 2 + 1]
        int x2 = xy[j * 2 + 0]
        int y2 = xy[j * 2 + 1]
        _triangle(self, cell, x0, y0, x1, y1, x2, y2)
        #_line(self, 2, x1, y1, x2, y2)
        if node:
            int nid = neighbors[i]
            if nid == -1: # cannot actually happen
                print("cell %d: no neighbor %d", cell, nid)
                continue
            else:
                node.neighbors[i] = nid
                node.edges[i * 2 + 0] = x1
                node.edges[i * 2 + 1] = y1

def _edge_callback(LandFloat *xy, void *user):
    LandVoronoi *self = user
    int x1 = xy[0]
    int y1 = xy[1]
    int x2 = xy[2]
    int y2 = xy[3]
    self.voronoi_edges += 1
    self.voronoi_dist += sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))

def _add_extra(LandVoronoi *self, int i, LandFloat x, y):
    land_buffer_add_uint32_t(self.extra, i)
    land_buffer_add_land_float(self.delaunay, x)
    land_buffer_add_land_float(self.delaunay, y)

def _add_duplicates(LandVoronoi *self):
    print("add duplicates")
    LandFloat w = self.w
    LandFloat h = self.h
    LandFloat estimate = w * h / self.n
    LandFloat grid_x = 2 * sqrt(estimate * w / h)
    LandFloat grid_y = 2 * sqrt(estimate * h / w)

    for int i in range(self.n):
        LandFloat x = self.xy[i].x
        LandFloat y = self.xy[i].y

        if x > self.w - grid_x:
            _add_extra(self, i, x - self.w, y)
            if y > self.h - grid_y: _add_extra(self, i, x - self.w, y - self.h)
            if y < grid_y: _add_extra(self, i, x - self.w, y + self.h)
        if x < grid_x:
            _add_extra(self, i, x + self.w, y)
            if y > self.h - grid_y: _add_extra(self, i, x + self.w, y - self.h)
            if y < grid_y: _add_extra(self, i, x + self.w, y + self.h)
        if y > self.h - grid_y: _add_extra(self, i, x, y - self.h)
        if y < grid_y: _add_extra(self, i, x, y + self.h)

def voronoi_recalculate_map(LandVoronoi *self):
    if self.d: delaunator_del(self.d)
    if self.extra: land_buffer_destroy(self.extra)
    if self.delaunay: land_buffer_destroy(self.delaunay)
    land_alloc(self.d)
    self.extra = land_buffer_new()
    self.delaunay = land_buffer_new()

    for int i in range(self.n):
        LandFloat x = self.xy[i].x
        LandFloat y = self.xy[i].y
        land_buffer_add_land_float(self.delaunay, x)
        land_buffer_add_land_float(self.delaunay, y)

    if self.wrap:
        _add_duplicates(self)
        self.en = self.extra.n // sizeof(uint32_t)
        self.xy = land_realloc(self.xy, (self.n + self.en) * sizeof *self.xy)
        for int i in range(self.en):
            LandVoronoiNode *node = self.xy + self.n + i
            node.x = land_buffer_get_land_float_by_index(self.delaunay, (self.n + i) * 2 + 0)
            node.y = land_buffer_get_land_float_by_index(self.delaunay, (self.n + i) * 2 + 1)

    for int i in range(self.n + self.en):
        int j = i
        if j >= self.n:
            j = land_buffer_get_uint32_by_index(self.extra, j - self.n)
        self.xy[i].b = j

    #print("extra %d", self.extra.n // 4)
    int n = self.delaunay.n // sizeof(LandFloat) // 2
    delaunator_init(self.d, (void *)self.delaunay.buffer, n)

    for int y in range(self.h):
        for int x in range(self.w):
            self.map[x + self.w * y] = -1

    self.voronoi_edges = 0
    self.voronoi_dist = 0.0
    if n >= 3:
        #for_each_triangle(self.d, _tri_callback, self)
        for_each_voronoi_edge(self.d, 1, _edge_callback, self)
        if self.voronoi_edges:
            self.voronoi_dist /= self.voronoi_edges
        land_delaunator_for_each_voronoi_cell(self.d, self.center, _cell_callback, self)
        fixup_map(self)

def fixup_map(LandVoronoi *self):
    int dx[] = {-1,  0, 1, 0}
    int dy[] = { 0, -1, 0, 1}
    for int t in range(100):
        int unassigned = 0
        for int steps in range(4):
            int oddx = steps % 2
            int oddy = steps // 2
            for int y in range(oddx, self.h, 2):
                for int x in range(oddy, self.w, 2):
                    int i = self.map[x + self.w * y]
                    if i == -1:
                        unassigned += 1
                        for int d in range(4):
                            if x + dx[d] < 0 or y + dy[d] < 0 or x + dx[d] >= self.w or y + dy[d] >= self.h:
                                continue
                            int j = self.map[x + dx[d] + self.w * (y + dy[d])]
                            if j != -1:
                                self.map[x + self.w * y] = j
                                break
        if unassigned == 0:
            break

def land_voronoi_create(LandRandom *seed, int w, h, n,
        bool wrap, int center, float randomness, border) -> LandVoronoi*:
    auto self = land_voronoi_new(seed, w, h, n, wrap, center, randomness)
    self.border = border

    #if randomness > 0:
    #    land_voronoi_distort_with_perlin(self, seed, randomness)

    if border > 0:
        land_voronoi_calculate_border_distance(self, border)
    else:
        land_voronoi_calculate_distance(self)

    return self

def _centroid(int i, LandFloat *xy, int *neighbors, int n,
        bool is_edge, void *user):
    LandVoronoi *self = user
    if i < self.n:
        LandVoronoiNode *v = self.xy + i
        float cx = 0
        float cy = 0
        for int j in range(n):
            cx += xy[j * 2 + 0]
            cy += xy[j * 2 + 1]
        v.x = cx / n
        v.y = cy / n

def land_voronoi_centroid(LandVoronoi *self, bool recalculate):
    Delaunator *d = self.d
    land_delaunator_for_each_voronoi_cell(d, 0, _centroid, self)

    voronoi_recalculate_map(self)

    if recalculate:
        land_voronoi_calculate_distance(self)

def land_voronoi_calculate_distance(LandVoronoi *self):
    int w = self.w
    int h = self.h
    for int y in range(h):
        for int x in range(w):
            int i = self.map[x + self.w * y]
            float d = 0
            if i != -1:
                d = _get_distance(self, x, y, i)
            self.distance[x + self.w * y] = d
            self.neighbor[x + self.w * y] = -1
            if d > self.max_distance:
                self.max_distance = d

def _check_edge(LandVoronoi *self, int cell, neighbor,
        float px, py, cx, cy, x, y, distance,
        float *mind, int *mini):
    LandVoronoiNode *node = land_voronoi_node(self, cell)
    LandVoronoiNode *node2 = land_voronoi_node(self, neighbor)
    
    LandFloat pd = land_point_segment_distance(x, y, px, py, cx, cy)
    if node.b == node2.b: pd = distance
    if pd < *mind:
        *mind = pd
        *mini = neighbor

def land_voronoi_calculate_border_distance(LandVoronoi *self, float distance):
    if self.n < 2: return

    self.max_distance = distance

    for int y in range(self.h):
        for int x in range(self.w):
            int cell = self.map[x + self.w * y]
            LandVoronoiNode *node = land_voronoi_node(self, cell)
            float d = distance
            int pn = node.neighbors_count
            int mini = -1
            for int i in range(pn):
                int j = (i + 1) % pn
                float x1 = node.edges[i * 2 + 0]
                float y1 = node.edges[i * 2 + 1]
                float x2 = node.edges[j * 2 + 0]
                float y2 = node.edges[j * 2 + 1]

                int neighbor = node.neighbors[j]
                _check_edge(self, cell, neighbor, x1, y1, x2, y2, x, y,
                    distance, &d, &mini)

            self.distance[x + self.w * y] = d
            self.neighbor[x + self.w * y] = mini
            #if cell == 5 and mini == 19:
            #    print("edge: %d/%d %.1f",
            #        x, y, d)

            # int mini = -1
            # float mindd = 0
            # LandVoronoiNode *xy = self.xy + cell
            # for int ni in range(xy.neighbors_count):
                # int n = xy.neighbors[ni]
                # LandVoronoiNode *neighbor = self.xy + n
                # float ndd = pow(neighbor.x - x, 2) + pow(neighbor.y - y, 2)
                # if mini == -1 or ndd < mindd:
                    # mindd = ndd
                    # mini = n
            # self.neighbor[x + self.w * y] = mini
            # float cd = sqrt(pow(xy.x - x, 2) + pow(xy.y - y, 2))
            # float d = fabs(sqrt(mindd) - cd) # crude heuristic, we really want the distance to the edge
            # d = distance - d
            # if d < 0: d = 0
            # self.distance[x + self.w * y] = d
            # if d > self.max_distance:
                # self.max_distance = d
    #land_voronoi_cells_free(polys)

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
    delaunator_del(self.d)
    land_free(self.map)
    land_free(self.neighbor)
    land_free(self.distance)
    for int i in range(self.n):
        auto node = land_voronoi_node(self, i)
        land_free(node.neighbors)
        land_free(node.edges)
    land_free(self.xy)
    land_free(self)

def land_voronoi_at(LandVoronoi *self, int x, y) -> float:
    float value = self.distance[x + self.w * y] / self.max_distance
    return value * 2 - 1 # change range from 0..1 to -1..1

def land_voronoi_owner(LandVoronoi *self, int x, y) -> int:
    return self.map[x + self.w * y]

def land_voronoi_neighbor(LandVoronoi *self, int x, y) -> int:
    return self.neighbor[x + self.w * y]

def land_voronoi_node(LandVoronoi *self, int i) -> LandVoronoiNode*:
    return self.xy + i

def land_voronoi_set_distance(LandVoronoi *self, float border):
    self.border = border
    if border:
        land_voronoi_calculate_border_distance(self, border)
    else:
        land_voronoi_calculate_distance(self)
