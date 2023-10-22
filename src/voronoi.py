import main
import noise
import external.delaunator
import land.util2d
import land.bitset

class LandVoronoiNode:
    int x, y
    float cx, cy
    float v
    int b
    int neighbors_count
    int *neighbors
    LandFloat *edges
    bool clipped # invalid node that was clipped
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
    int max_distance_i
    #float randomness
    LandRandom *seed
    bool wrap
    #int center # 0=voronoi,1=centroid

    int voronoi_edges
    double voronoi_dist

    Delaunator *d
    LandBuffer *delaunay
    LandBuffer *extra # maps extra cells >=n to their real cell 0..n-1

    float overlap # how much the voronoi cells overlap
    int clip_border

    LandBitSet *not_threadsafe_bitset

    bool debug

def _get_distance(LandVoronoi *self, int x, y, i) -> LandFloat:
    LandFloat dx = self.xy[i].x - x
    LandFloat dy = self.xy[i].y - y
    LandFloat d = sqrt(dx * dx + dy * dy)
    return d

def land_voronoi_new(LandRandom *seed, int w, h, n, bool wrap,
        int clip_border) -> LandVoronoi *:
    LandVoronoi *self; land_alloc(self)
    self.w = w
    self.h = h
    self.wrap = wrap
    self.map = land_calloc(w * h * sizeof *self.map)
    self.distance = land_calloc(w * h * sizeof *self.distance)
    self.neighbor = land_calloc(w * h * sizeof *self.neighbor)
    self.n = n
    self.xy = land_calloc(n * sizeof *self.xy)
    self.max_distance = 0
    self.seed = seed
    self.clip_border = clip_border

    for int i in range(n):
        int x = land_random(seed, 0, w - 1)
        int y = land_random(seed, 0, h - 1)
        self.xy[i].x = x
        self.xy[i].y = y

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

# def _rot(int *x1, *y1, *x2, *y2, *x3, *y3)
    # int tx = *x1
    # int ty = *y1
    # *x1 = *x2
    # *y1 = *y2
    # *x2 = *x3
    # *y2 = *y3
    # *x3 = tx
    # *y3 = ty

# def _swap(int *x1, *y1, *x2, *y2)
    # int tx = *x1
    # int ty = *y1
    # *x1 = *x2
    # *y1 = *y2
    # *x2 = tx
    # *y2 = ty

# def _hline(LandVoronoi *self, int c, x1, y, x2):
    # for int x = x1 while x < x2 with x += 1:
        # if x >= 0 and y >= 0 and x < self.w and y < self.h:
            # self.map[x + self.w * y] = c

# static class Leg:
    # float f
    # float g
    # int w, h
    # int step
    # int x
    # int y2

# def _leg(int x1, y1, x2, y2) -> Leg:
    # Leg l
    # l.f = 0.5
    # l.w = x2 - x1
    # l.h = y2 - y1
    # l.step = 1
    # if l.w < 0:
        # l.w = -l.w
        # l.step = -1
    # l.g = l.w if l.h == 0 else 1.0 * l.w / l.h
    # l.x = x1
    # l.y2 = y2
    # return l

# def _leg_step(Leg *leg):
    # leg.f += leg.g
    # LandFloat a = floor(leg.f)
    # leg.x += leg.step * (int)a
    # leg.f -= a

# def _triangle(LandVoronoi *self, int c, x1, y1, x2, y2, x3, y3):
    # if y1 < y2:
        # if y1 < y3: # 1 < 2,3
            # pass
        # else: # 3 < 1 < 2
            # _rot(&x1, &y1, &x3, &y3, &x2, &y2)
    # else:
        # if y2 < y3: # 2 < 1, 3 
            # _rot(&x1, &y1, &x2, &y2, &x3, &y3)
        # else: # 3 < 2 < 1
            # _rot(&x1, &y1, &x3, &y3, &x2, &y2)
    
    # int y = y1
    # if 1.0 * (x3 - x1) / (y3 - y1) < 1.0 * (x2 - x1) / (y2 - y1): _swap(&x2, &y2, &x3, &y3)
    # Leg left = _leg(x1, y1, x2, y2)
    # Leg right = _leg(x1, y1, x3, y3)
    # int h = max(y2 - y1, y3 - y1)
    # while h > 0:
        # _leg_step(&left)
        # _leg_step(&right)
        # _hline(self, c, left.x, y, right.x)
        # y += 1
        # if y >= left.y2:
            # left = _leg(x2, y2, x3, y3)
        # elif y >= right.y2:
            # right = _leg(x3, y3, x2, y2)
        # h -= 1

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

LandFloat _EPSILON = 0.00000000000000022204
def _cell_callback(int cell, LandFloat *xy, int *neighbors, int n, void *user):
    LandVoronoi *self = user
    LandVoronoiNode *node

    node = self.xy + cell
    if n < 3: n = 0

    for int i in range(n):
        int j = (i + 1) % n
        int k = (j + 1) % n
        LandFloat x1 = xy[i * 2 + 0]
        LandFloat y1 = xy[i * 2 + 1]
        LandFloat x2 = xy[j * 2 + 0]
        LandFloat y2 = xy[j * 2 + 1]
        LandFloat x3 = xy[k * 2 + 0]
        LandFloat y3 = xy[k * 2 + 1]
        LandFloat c = land_cross2d(x2 - x1, y2 - y1, x3 - x2, y3 - y2)
        LandFloat d = land_dot2d(x2 - x1, y2 - y1, x3 - x2, y3 - y2)

        if cell == DEBUG_NODE:
            print("%d: %.2f,%.2f", i, x1, y1)
            print("%d: %.8f %.8f (%.2f,%.2f x %.2f,%.2f)", i, c, d,
                x2 - x1, y2 - y1, x3 - x2, y3 - y2)
        if c < _EPSILON and d < -1 + _EPSILON:
            print("degenerated %d", cell)
            n = 0
            break

    node.clipped = n < 3
    node.neighbors_count = n
    node.neighbors = land_malloc(n * sizeof(int))
    node.edges = land_malloc(n * 2 * sizeof(LandFloat))
    node.wrap_id = cell
    if cell < self.n:
        node.id = cell
    else:
        node.id = land_buffer_get_uint32_by_index(self.extra, cell - self.n)

    for int i in range(n):
        LandFloat x1 = xy[i * 2 + 0]
        LandFloat y1 = xy[i * 2 + 1]
        
        int nid = neighbors[i]
        if nid == -1: # special edge node we construct for edge cells
            pass
        node.neighbors[i] = nid
        node.edges[i * 2 + 0] = x1
        node.edges[i * 2 + 1] = y1

# def _draw_fill(LandVoronoi *self, LandVoronoiNode *node):
    # LandFloat *xy = node.edges
    # int n = node.neighbors_count
    # int x0 = node.x
    # int y0 = node.y
    # for int i in range(n):
        # int j = (i + 1) % n
        # int x1 = xy[i * 2 + 0]
        # int y1 = xy[i * 2 + 1]
        # int x2 = xy[j * 2 + 0]
        # int y2 = xy[j * 2 + 1]
        # _triangle(self, node.wrap_id, x0, y0, x1, y1, x2, y2)

# def _draw_outline(LandVoronoi *self, LandVoronoiNode *node):
    # LandFloat *xy = node.edges
    # int n = node.neighbors_count
    # for int i in range(node.neighbors_count):
        # int j = (i + 1) % n
        # int x1 = xy[i * 2 + 0]
        # int y1 = xy[i * 2 + 1]
        # int x2 = xy[j * 2 + 0]
        # int y2 = xy[j * 2 + 1]
        # _line(self, -1, x1, y1, x2, y2)
        # _line(self, -1, x1, y1 - 1, x2, y2 - 1)
        # _line(self, -1, x1 - 1, y1, x2 - 1, y2)

def _edge_callback(LandFloat *xy, void *user):
    LandVoronoi *self = user
    LandFloat x1 = xy[0]
    LandFloat y1 = xy[1]
    LandFloat x2 = xy[2]
    LandFloat y2 = xy[3]
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

def land_voronoi_recalculate_map(LandVoronoi *self, bool update_map):
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
            land_zero(node, sizeof *node)
            node.x = land_buffer_get_land_float_by_index(self.delaunay, (self.n + i) * 2 + 0)
            node.y = land_buffer_get_land_float_by_index(self.delaunay, (self.n + i) * 2 + 1)

    if self.not_threadsafe_bitset:
        land_bitset_del(self.not_threadsafe_bitset)
    self.not_threadsafe_bitset = land_bitset_new(self.n + self.en)

    for int i in range(self.n + self.en):
        int j = i
        if j >= self.n:
            j = land_buffer_get_uint32_by_index(self.extra, j - self.n)
        self.xy[i].b = j

    #print("extra %d", self.extra.n // 4)
    int n = self.delaunay.n // sizeof(LandFloat) // 2
    int b = self.clip_border
    delaunator_init(self.d, (void *)self.delaunay.buffer, n,
        -b, -b, self.w + b, self.h + b)

    if update_map:
        _update_map(self)

def _update_map(LandVoronoi *self):

    for int y in range(self.h):
        for int x in range(self.w):
            self.map[x + self.w * y] = -1

    self.voronoi_edges = 0
    self.voronoi_dist = 0.0
    if self.n + self.en >= 2:
        #for_each_triangle(self.d, _tri_callback, self)
        if self.n + self.en >= 3: for_each_voronoi_edge(self.d, _edge_callback, self)
        if self.voronoi_edges:
            self.voronoi_dist /= self.voronoi_edges
        land_delaunator_for_each_voronoi_cell(self.d, _cell_callback, self)
    else:
        return

    #for int i in range(n):
    #    _draw_fill(self, self.xy + i)

    #for int i in range(n):
    #    _draw_outline(self, self.xy + i)

    assign_map(self)
    fixup_map_holes(self)

def _point_in_cell(int x, y, LandVoronoiNode *cell) -> bool:
    if cell.neighbors_count < 3 or cell.clipped: return False
    for int i in range(cell.neighbors_count):
        int j = (i + 1) % cell.neighbors_count
        LandFloat x1 = cell.edges[i * 2 + 0]
        LandFloat y1 = cell.edges[i * 2 + 1]
        LandFloat x2 = cell.edges[j * 2 + 0]
        LandFloat y2 = cell.edges[j * 2 + 1]
        if land_cross2d(x2 - x1, y2 - y1, x - x1, y - y1) < 0:
            return False
    return True

def land_voronoi_node_contains(LandVoronoi *v, int i, x, y) -> bool:
    auto node = land_voronoi_node(v, i)
    return _point_in_cell(x, y, node)

def _find_cell(LandVoronoi *self, int x, y) -> LandVoronoiNode *:
    for int i in range(self.n + self.en):
        LandVoronoiNode *node = self.xy + i
        if _point_in_cell(x, y, node):
            return node
    return None

def _check_cells_around(LandVoronoi *self, LandVoronoiNode *initial, int x, y) -> LandVoronoiNode *:
    if _point_in_cell(x, y, initial):
        return initial
    LandBitSet *bitset = self.not_threadsafe_bitset
    land_bitset_clear(bitset)
    land_bit_set(bitset, initial.wrap_id)
    LandArray *stack = land_array_new()
    land_array_add(stack, initial)
    int pos = 0
    LandVoronoiNode *found = None
    while pos < land_array_count(stack):
        LandVoronoiNode *check = land_array_get(stack, pos)
        pos += 1
        for int i in range(check.neighbors_count):
            int nid = check.neighbors[i]
            if nid == -1: continue
            if land_bit_check_or_set(bitset, nid):
                continue
            auto node_i = land_voronoi_node(self, nid)
            if _point_in_cell(x, y, node_i):
                found = node_i
                goto done
            land_array_add(stack, node_i)
    label done
    land_array_destroy(stack)
    return found

def assign_map(LandVoronoi *self):
    LandVoronoiNode *node = None
    int holes = 0
    int slow = 0
    for int y in range(self.h):
        LandVoronoiNode *row = node
        for int x in range(self.w):
            if node:
                node = _check_cells_around(self, node, x, y)
                if not node: slow += 1
            else:
                node = _find_cell(self, x, y)
                slow += 1
            if node:
                self.map[x + self.w * y] = node.wrap_id
                if x == 0: row = node
            else:
                holes += 1
        node = row
    print("%.3f%% slow checks (%d holes)",
        100.0 * slow / self.w / self.h, holes)

def fixup_map_holes(LandVoronoi *self):
    # just uses 4 neighbors with no polygon check, sometimes we have
    # pixels which fail the polygon check (due to floating point inaccuracy
    # after clipping)
    int holes = 0
    int fixed = 0
    for int grid in range(4):
        for int gy in range(0, self.h, 2):
            for int gx in range(0, self.w, 2):
                int x = gx + grid % 2
                int y = gy + grid // 2
                if self.map[x + self.w * y] != -1:
                    continue
                int dxy[] = {-1, 0, 1, 0, -1}
                for int d in range(4):
                    int nx = x + dxy[d]
                    int ny = y + dxy[d + 1]
                    if nx < 0 or nx >= self.w: continue
                    if ny < 0 or ny >= self.h: continue
                    int i = self.map[nx + self.w * ny]
                    if i == -1: continue
                    self.map[x + self.w * y] = i
                    fixed += 1
                    goto label_fixed
                holes += 1
                label label_fixed
    print("%s%d%s holes (%d fixed)", land_color_bash("red" if holes > 0 else "green"),
        holes, land_color_bash("end"), fixed)

def _centroid(int i, LandFloat *xy, int *neighbors, int n, void *user):
    LandVoronoi *self = user
    # extra nodes are discarded and re-added so no need to care about them
    if i < self.n and n >= 3:
        LandVoronoiNode *v = self.xy + i
        LandFloat cx = 0
        LandFloat cy = 0
        for int j in range(n):
            cx += xy[j * 2 + 0]
            cy += xy[j * 2 + 1]
        v.x = cx / n
        v.y = cy / n

def land_voronoi_centroid(LandVoronoi *self, bool recalculate_map):
    Delaunator *d = self.d
    land_delaunator_for_each_voronoi_cell(d, _centroid, self)
    land_voronoi_recalculate_map(self, recalculate_map)

def land_voronoi_calculate_distance(LandVoronoi *self):
    if self.overlap > 0:
        _calculate_border_distance(self, self.overlap)
    else:
        _calculate_distance(self)

def _calculate_distance(LandVoronoi *self):
    int w = self.w
    int h = self.h
    int mx, my
    self.max_distance = 0
    for int y in range(h):
        for int x in range(w):
            int i = self.map[x + self.w * y]
            LandFloat d = 0
            if i != -1:
                d = _get_distance(self, x, y, i)
            self.distance[x + self.w * y] = d
            self.neighbor[x + self.w * y] = -1
            if d > self.max_distance:
                self.max_distance = d
                self.max_distance_i = i
                mx = x
                my = y
    print("size: %d/%d", w, h)
    print("max distance: %.1f for %d (at %d/%d)", self.max_distance, self.max_distance_i, mx, my)

def _check_edge(LandVoronoi *self, int cell, neighbor,
        LandFloat px, py, cx, cy, x, y, distance,
        LandFloat *mind, int *mini):
    if neighbor == -1:
        return
    LandVoronoiNode *node = land_voronoi_node(self, cell)
    LandVoronoiNode *node2 = land_voronoi_node(self, neighbor)
    if node.b == node2.b:
        return
    
    LandFloat pd = land_point_segment_distance(x, y, px, py, cx, cy)
    
    if pd < *mind:
        *mind = pd
        *mini = neighbor

def _calculate_border_distance(LandVoronoi *self, float distance):
    if self.n < 2: return

    self.max_distance = distance

    for int y in range(self.h):
        for int x in range(self.w):
            int cell = self.map[x + self.w * y]
            if cell == -1:
                # there shouldn't be holes but if there is one just
                # ignore
                continue
            LandVoronoiNode *node = land_voronoi_node(self, cell)
            LandFloat d = distance
            int pn = node.neighbors_count
            int mini = -1
            for int i in range(pn):
                int j = (i + 1) % pn
                LandFloat x1 = node.edges[i * 2 + 0]
                LandFloat y1 = node.edges[i * 2 + 1]
                LandFloat x2 = node.edges[j * 2 + 0]
                LandFloat y2 = node.edges[j * 2 + 1]

                int neighbor = node.neighbors[j]
                _check_edge(self, cell, neighbor, x1, y1, x2, y2, x, y,
                    distance, &d, &mini)

            self.distance[x + self.w * y] = d
            self.neighbor[x + self.w * y] = mini

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

def land_voronoi_cell_callback_at(LandVoronoi *self, LandBitSet *bitset, int x, y, radius,
        void (*cb)(int owner, int neighbor, float distance, void *user), void *user):
    if not bitset:
        bitset = self.not_threadsafe_bitset
    land_bitset_clear(bitset)
    if self.debug:
        char *bits = land_bitset_string(bitset)
        print(bits)
        land_free(bits)
    int owner = land_voronoi_owner(self, x, y)
    if owner == -1:
        # theoretically not possible as a voronoi diagram is infinite -
        # in our case, just don't pass coordinates outside the clip rect
        return
    if radius == 0:
        cb(owner, -1, 1, user)
        return
    _check_cell(self, bitset, owner, owner, x, y, radius, cb, user)
    if self.debug:
        char *bits = land_bitset_string(bitset)
        print(bits)
        land_free(bits)

def _check_cell(LandVoronoi *self, LandBitSet *bitset, int start, cell, x, y, radius,
        void (*cb)(int owner, int neighbor, float distance, void *user), void *user):
    if land_bit_check_or_set(bitset, cell):
        if self.debug:
            print("[%d]", cell)
        return
    auto node = land_voronoi_node(self, cell)
    if self.debug:
        print("_check_cell %d", cell)
    int pn = node.neighbors_count
    float mind = radius
    int minn = -1
    for int i in range(pn):
        int j = (i + 1) % pn
        int neigh = node.neighbors[j]
        if neigh == -1: continue
        float x1 = node.edges[i * 2 + 0]
        float y1 = node.edges[i * 2 + 1]
        float x2 = node.edges[j * 2 + 0]
        float y2 = node.edges[j * 2 + 1]
        LandFloat pd = land_point_segment_distance(x, y, x1, y1, x2, y2)
        if self.debug:
            print("  edge %d: %.1f (<%d)", neigh, pd, radius)
        if pd < radius:
            if pd < mind:
                mind = pd
                minn = neigh
            _check_cell(self, bitset, start, neigh, x, y, radius, cb, user)
    if minn != -1:
        if self.debug:
            print("* %d->%d", cell, minn)
        cb(cell, minn, -mind if cell == start else mind, user)
    elif cell == start:
        cb(cell, -1, 0.1, user)

def land_voronoi_owner(LandVoronoi *self, int x, y) -> int:
    if x < 0 or x >= self.w: return -1
    if y < 0 or y >= self.h: return -1
    return self.map[x + self.w * y]

def land_voronoi_neighbor(LandVoronoi *self, int x, y) -> int:
    return self.neighbor[x + self.w * y]

def land_voronoi_is_neighbor(LandVoronoi *self, int i, j) -> bool:
    auto i_node = land_voronoi_node(self, i)
    auto j_node = land_voronoi_node(self, j)
    if not i_node: return False
    if not j_node: return False
    for int ni in range(i_node.neighbors_count):
        if i_node.neighbors[ni] == j:
            for int nj in range(j_node.neighbors_count):
                if j_node.neighbors[nj] == i:
                    return True
    return False

def land_voronoi_node(LandVoronoi *self, int i) -> LandVoronoiNode*:
    if i == -1: return None
    return self.xy + i

def land_voronoi_set_overlap(LandVoronoi *self, float overlap):
    self.overlap = overlap
    land_voronoi_calculate_distance(self)

def _print_cell(LandVoronoi *self, int id):
    auto node = land_voronoi_node(self, id)
    printf("%d:", id)
    if not node: return
    LandFloat *f = node.edges
    for int i in range(node.neighbors_count):
        printf(" %.2f,%.2f", f[i * 2 + 0], f[i * 2 + 1])
    print("")

def land_voronoi_self_check(LandVoronoi *self):
    for int y in range(self.h):
        for int x in range(self.w):
            int owner = land_voronoi_owner(self, x, y)
            if owner == -1:
                error("hole at %d/%d", x, y)
                continue
            int in_cell = 0
            int all_cells[10]
            bool found_map = False
            for int i in range(self.n + self.en):
                LandVoronoiNode *node = self.xy + i
                if _point_in_cell(x + 0.5, y + 0.5, node):
                    if in_cell < 10:
                        all_cells[in_cell] = i
                    in_cell += 1
                    if owner == i:
                        found_map = True
            if in_cell == 1 and not found_map:
                error("at %d/%d could not find map owner %d", x, y, owner)
                for int i in range(in_cell):
                    if i == 10: break
                    _print_cell(self, all_cells[i])
            if in_cell == 0:
                auto on = land_voronoi_node(self, owner)
                if _point_in_cell(x + 1.5, y, on): continue
                if _point_in_cell(x - 0.5, y, on): continue
                if _point_in_cell(x, y + 1.5, on): continue
                if _point_in_cell(x, y - 0.5, on): continue
                error("no cell for %d/%d", x, y)
                error("owner is %d", owner)
            if in_cell > 1:
                bool all_neighbors = True
                for int i in range(in_cell):
                    if all_cells[i] == owner: continue
                    if land_voronoi_is_neighbor(self, owner, all_cells[i]):
                        continue
                    all_neighbors = False
                if not all_neighbors:
                    error("multiple cells for %d/%d", x, y)
                    error("owner is %d", owner)
                    for int i in range(in_cell):
                        if i == 10: break
                        _print_cell(self, all_cells[i])
            
