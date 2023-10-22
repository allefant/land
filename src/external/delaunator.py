import land.land

global int DEBUG_NODE = -1
LandFloat EPSILON = 0.00000000000000022204
int EDGE_STACK[512]
macro NoneInt INT_MAX
macro NoneFloat INFINITY

class IntArray:
    int *ints
    int n

class FloatArray:
    LandFloat *floats
    int n

class Point2D:
    LandFloat x, y

def int_array_del(IntArray *a):
    if a.ints: land_free(a.ints)
    land_free(a)

def float_array_del(FloatArray *a):
    if a.floats: land_free(a.floats)
    land_free(a)

def int_array_new_init(int n, int x) -> IntArray*:
    IntArray *a; land_alloc(a)
    a.ints = land_malloc(sizeof(int) * n)
    a.n = n
    for int i in range(n):
        a.ints[i] = x
    return a

def int_array_new(int n) -> IntArray*:
    return int_array_new_init(n, NoneInt)

def float_array_new(int n) -> FloatArray*:
    FloatArray *a; land_alloc(a)
    a.floats = land_malloc(sizeof(LandFloat) * n)
    a.n = n
    for int i in range(n):
        a.floats[i] = NoneFloat
    return a

def int_array_slice(IntArray *self, int n) -> IntArray *:
    self.n = n
    return self

class Delaunator:
    """
    a_________b
    |\        |
    |  \      |
    |    \    |
    |      \  |
    |________\|
    c         d

    coords = [a,b,c,d] - the 4 input points
    triangles = [0,2,3,0,3,1] - 2 triangles: 0/2/3=a/c/d and 0/3/1=a/d/b
    halfedges = [-,-,3,2,-,-]
    """
    FloatArray *coords # copy of the input coordinates
    IntArray *triangles # triplets a/b/c of triangle half-edges
    IntArray *halfedges # halfedges[x] has an index into triangles[] of
        # the edge in the other direction or -1 for an outer edge

    IntArray *hull

    IntArray *hullPrev
    IntArray *hullNext
    IntArray *hullTri
    IntArray *hullHash
    IntArray *_ids
    FloatArray *_dists

    IntArray *_triangles
    IntArray *_halfedges

    int hashSize
    int trianglesLen

    LandFloat _cx, _cy
    int _hullStart

    LandFloat bx1, by1, bx2, by2

def delaunator_del(Delaunator *self):
    float_array_del(self.coords)
    float_array_del(self._dists)
    int_array_del(self.triangles)
    int_array_del(self.halfedges)
    int_array_del(self.hull)
    int_array_del(self.hullPrev)
    int_array_del(self.hullNext)
    int_array_del(self.hullTri)
    int_array_del(self._ids)
    #int_array_del(self._triangles)
    #int_array_del(self._halfedges)

def delaunator_init(Delaunator *self, LandFloat *points, int n,
        LandFloat bx1, by1, bx2, by2):
    self.bx1 = bx1
    self.by1 = by1
    self.bx2 = bx2
    self.by2 = by2
    for int i in range(512):
        EDGE_STACK[i] = NoneInt

    FloatArray *coords = float_array_new(n * 2)

    for int i in range(0, n):
        coords.floats[2 * i] = points[2 * i]
        coords.floats[2 * i+1] = points[2 * i + 1]
    delaunator_constructor(self, coords)
    print("coords: %d", self.coords.n // 2)
    print("triangles: %d", self.triangles.n // 3)
    print("edges: %d", self.halfedges.n)

def delaunator_constructor(Delaunator *self, FloatArray *coords):
    int n = coords.n >> 1

    self.coords = coords

    # arrays that will store the triangulation graph
    int maxTriangles = max(2 * n - 5, 0)
    if maxTriangles < 0: maxTriangles = 0
    self._triangles = int_array_new(maxTriangles * 3)
    self._halfedges = int_array_new(maxTriangles * 3)

    # temporary arrays for tracking the edges of the advancing convex hull
    self.hashSize = ceil(sqrt(n))
    self.hullPrev = int_array_new(n) # edge to prev edge
    self.hullNext = int_array_new(n) # edge to next edge
    self.hullTri = int_array_new(n) # edge to adjacent triangle
    self.hullHash = int_array_new_init(self.hashSize, -1) # angular edge hash

    # temporary arrays for sorting points
    self._ids =  int_array_new(n)
    self._dists = float_array_new(n)

    if n < 3:
        n = 3
        print("Need at least 3 points")
        self.triangles = int_array_new(n)
        self.halfedges = int_array_new(n)
        self.hull = int_array_new(n)
        return
    delaunator_update(self, coords)

def delaunator_update(Delaunator *self, FloatArray *coords):
    int n = coords.n >> 1

    # populate an array of point indices; calculate input data bbox
    LandFloat minX = INFINITY
    LandFloat minY = INFINITY
    LandFloat maxX = -INFINITY
    LandFloat maxY = -INFINITY

    for int i in range(n):
        LandFloat x = coords.floats[2 * i]
        LandFloat y = coords.floats[2 * i + 1]
        if isnan(x): print("x nan for %d", i)
        if isnan(y): print("y nan for %d", i)
        if (x < minX): minX = x
        if (y < minY): minY = y
        if (x > maxX): maxX = x
        if (y > maxY): maxY = y
        self._ids.ints[i] = i

    LandFloat cx = (minX + maxX) / 2
    LandFloat cy = (minY + maxY) / 2

    LandFloat minDist = INFINITY
    int i0 = 0
    int i1 = 0
    int i2 = 0

    # pick a seed point close to the center
    for int i in range(0,n):
        LandFloat d = _dist(cx, cy, coords.floats[2 * i], coords.floats[2 * i + 1])

        if (d < minDist):
            i0 = i
            minDist = d

    LandFloat i0x = coords.floats[2 * i0]
    LandFloat i0y = coords.floats[2 * i0 + 1]
    minDist = INFINITY

    # find the point closest to the seed
    for int i in range(0,n):
        if (i == i0): continue
        LandFloat d = _dist(i0x, i0y, coords.floats[2 * i], coords.floats[2 * i + 1])

        if (d < minDist and d > 0):
            i1 = i
            minDist = d

    LandFloat i1x = coords.floats[2 * i1]
    LandFloat i1y = coords.floats[2 * i1 + 1]

    LandFloat minRadius = INFINITY

    # find the third point which forms the smallest circumcircle with the first two
    for int i in range(0,n):
        if (i == i0 or i == i1): continue
        LandFloat r = circumradius(i0x, i0y, i1x, i1y, coords.floats[2 * i], coords.floats[2 * i + 1])

        if (r < minRadius):
            i2 = i
            minRadius = r

    LandFloat i2x = coords.floats[2 * i2]
    LandFloat i2y = coords.floats[2 * i2 + 1]

    if (minRadius == INFINITY):
        # order collinear points by dx (or dy if all x are identical)
        # and return the list as a hull
        for int i in range(0,n):
            self._dists.floats[i] = (coords.floats[2 * i] - coords.floats[0])
            if not self._dists.floats[i]:
                self._dists.floats[i] = (coords.floats[2 * i + 1] - coords.floats[1])

        quicksort(self._ids, self._dists, 0, n - 1)
        IntArray *hull = int_array_new(n)
        int j = 0
        LandFloat d0 = -INFINITY

        for int i in range(0,n):
            int id = self._ids.ints[i]

            if (self._dists.floats[id] > d0):
                hull.ints[j] = id
                j+=1
                d0 = self._dists.floats[id]

        self.hull = int_array_slice(hull, j)

    # swap the order of the seed points for counter-clockwise orientation
    if (orient(i0x, i0y, i1x, i1y, i2x, i2y)):
        int i = i1
        LandFloat x = i1x
        LandFloat y = i1y
        i1 = i2
        i1x = i2x
        i1y = i2y
        i2 = i
        i2x = x
        i2y = y

    Point2D center = circumcenter(i0x, i0y, i1x, i1y, i2x, i2y)
    self._cx = center.x
    self._cy = center.y

    for int i in range(0,n):
        self._dists.floats[i] = _dist(coords.floats[2 * i], coords.floats[2 * i + 1], center.x, center.y)

    # sort the points by distance from the seed triangle circumcenter
    quicksort(self._ids, self._dists, 0, n - 1)

    # set up the seed triangle as the starting hull
    self._hullStart = i0
    int hullSize = 3

    self.hullNext.ints[i0] = self.hullPrev.ints[i2] = i1
    self.hullNext.ints[i1] = self.hullPrev.ints[i0] = i2
    self.hullNext.ints[i2] = self.hullPrev.ints[i1] = i0

    self.hullTri.ints[i0] = 0
    self.hullTri.ints[i1] = 1
    self.hullTri.ints[i2] = 2

    self.hullHash.ints[delaunator_hashKey(self, i0x, i0y)] = i0
    self.hullHash.ints[delaunator_hashKey(self, i1x, i1y)] = i1
    self.hullHash.ints[delaunator_hashKey(self, i2x, i2y)] = i2

    self.trianglesLen = 0
    delaunator_addTriangle(self, i0, i1, i2, -1, -1, -1)

    LandFloat xp=0
    LandFloat yp=0

    for int k in range(0, self._ids.n):
        int i = self._ids.ints[k]
        LandFloat x = coords.floats[2 * i]
        LandFloat y = coords.floats[2 * i + 1]

        # skip near-duplicate points
        if (k > 0 and fabs(x - xp) <= EPSILON and fabs(y - yp) <= EPSILON): continue

        xp = x
        yp = y

        # skip seed triangle points
        if (i == i0 or i == i1 or i == i2): continue

        # find a visible edge on the convex hull using edge hash
        int start = 0
        int key = delaunator_hashKey(self, x, y)

        for int j in range(0,self.hashSize):
            start = self.hullHash.ints[(key + j) % self.hashSize]
            if (start != -1 and start != self.hullNext.ints[start]): break

        start = self.hullPrev.ints[start]
        int e = start

        while True:
            int q = self.hullNext.ints[e]
            if orient(x, y, coords.floats[2 * e], coords.floats[2 * e + 1], coords.floats[2 * q], coords.floats[2 * q + 1]): break
            e = q

            if (e == start):
                e = -1
                break

        if (e == -1): continue # likely a near-duplicate point; skip it

        # add the first triangle from the point
        int t = delaunator_addTriangle(self, e, i, self.hullNext.ints[e], -1, -1, self.hullTri.ints[e])

        # recursively flip triangles from the point until they satisfy the Delaunay condition
        self.hullTri.ints[i] = delaunator_legalize(self, t + 2,coords)
        self.hullTri.ints[e] = t # keep track of boundary triangles on the hull
        hullSize+=1

        # walk forward through the hull, adding more triangles and flipping recursively
        n = self.hullNext.ints[e]

        while True:
            int q = self.hullNext.ints[n]
            if not (orient(x, y, coords.floats[2 * n], coords.floats[2 * n + 1], coords.floats[2 * q], coords.floats[2 * q + 1])): break
            t = delaunator_addTriangle(self, n, i, q, self.hullTri.ints[i], -1, self.hullTri.ints[n])
            self.hullTri.ints[i] = delaunator_legalize(self, t + 2,coords)
            self.hullNext.ints[n] = n # mark as removed
            hullSize-=1
            n = q

        # walk backward from the other side, adding more triangles and flipping
        if (e == start):
            while True:
                int q = self.hullPrev.ints[e]
                if not (orient(x, y, coords.floats[2 * q], coords.floats[2 * q + 1], coords.floats[2 * e], coords.floats[2 * e + 1])): break
                t = delaunator_addTriangle(self, q, i, e, -1, self.hullTri.ints[e], self.hullTri.ints[q])
                delaunator_legalize(self,t + 2,coords)
                self.hullTri.ints[q] = t
                self.hullNext.ints[e] = e # mark as removed
                hullSize-=1
                e = q

        # update the hull indices
        self._hullStart = self.hullPrev.ints[i] = e
        self.hullNext.ints[e] = self.hullPrev.ints[n] = i
        self.hullNext.ints[i] = n

        # save the two new edges in the hash table
        self.hullHash.ints[delaunator_hashKey(self, x, y)] = i
        self.hullHash.ints[delaunator_hashKey(self, coords.floats[2 * e], coords.floats[2 * e + 1])] = e

    self.hull = int_array_new(hullSize)
    int e = self._hullStart
    for int i in range(0,hullSize):
        self.hull.ints[i] = e
        e = self.hullNext.ints[e]

    # trim typed triangle mesh arrays
    self.triangles = int_array_slice(self._triangles, self.trianglesLen)
    self.halfedges = int_array_slice(self._halfedges, self.trianglesLen)
    self._triangles = None
    self._halfedges = None

def delaunator_hashKey(Delaunator *self, LandFloat x, y) -> int:
    return (int)floor(pseudoAngle(x - self._cx, y - self._cy) * self.hashSize) % self.hashSize

def delaunator_legalize(Delaunator *self, int a, FloatArray *coords) -> int:
    int i = 0
    int ar = 0

    # recursion eliminated with a fixed-size stack
    while True:
        int b = self._halfedges.ints[a]
        """
          if the pair of triangles doesn't satisfy the Delaunay condition
          (p1 is inside the circumcircle of [p0, pl, pr]), flip them,
          then do the same check/flip recursively for the new pair of triangles
         
                    pl                    pl
                   /||\                  /  \
                al/ || \bl            al/    \a
                 /  ||  \              /      \
                /  a||b  \    flip    /___ar___\
              p0\   ||   /p1   =>   p0\---bl---/p1
                 \  ||  /              \      /
                ar\ || /br             b\    /br
                   \||/                  \  /
                    pr                    pr
         
        """
        int a0 = a - a % 3
        ar = a0 + (a + 2) % 3

        if (b == -1): # convex hull edge
            if (i == 0): break
            i-=1
            a = EDGE_STACK[i]
            continue

        int b0 = b - b % 3
        int al = a0 + (a + 1) % 3
        int bl = b0 + (b + 2) % 3

        int p0 = self._triangles.ints[ar]
        int pr = self._triangles.ints[a]
        int pl = self._triangles.ints[al]
        int p1 = self._triangles.ints[bl]

        bool illegal = inCircle(
            coords.floats[2 * p0], coords.floats[2 * p0 + 1],
            coords.floats[2 * pr], coords.floats[2 * pr + 1],
            coords.floats[2 * pl], coords.floats[2 * pl + 1],
            coords.floats[2 * p1], coords.floats[2 * p1 + 1])

        if (illegal):
            self._triangles.ints[a] = p1
            self._triangles.ints[b] = p0

            int hbl = self._halfedges.ints[bl]

            # edge swapped on the other side of the hull (rare); fix the halfedge reference
            if (hbl == -1):
                int e = self._hullStart
                
                while True:
                    if (self.hullTri.ints[e] == bl):
                        self.hullTri.ints[e] = a
                        break

                    e = self.hullPrev.ints[e]
                    if (e == self._hullStart): break

            delaunator_link(self, a, hbl)
            delaunator_link(self, b, self._halfedges.ints[ar])
            delaunator_link(self, ar, bl)

            int br = b0 + (b + 1) % 3

            # don't worry about hitting the cap: it can only happen on extremely degenerate input
            if (i < 512):
                EDGE_STACK[i] = br
                i+=1

        else:
            if (i == 0): break
            i-=1
            a = EDGE_STACK[i]

    return ar

def delaunator_link(Delaunator *self, int a, b):
    self._halfedges.ints[a] = b
    if (b != -1):
        self._halfedges.ints[b] = a

# add a new triangle given vertex indices and adjacent half-edge ids
def delaunator_addTriangle(Delaunator *self, int i0, i1, i2, a, b, c) -> int:
    int t = self.trianglesLen

    self._triangles.ints[t] = i0
    self._triangles.ints[t + 1] = i1
    self._triangles.ints[t + 2] = i2

    delaunator_link(self, t, a)
    delaunator_link(self, t + 1, b)
    delaunator_link(self, t + 2, c)

    self.trianglesLen += 3

    return t

# monotonically increases with real angle, but doesn't need expensive trigonometry
def pseudoAngle(LandFloat dx, dy) -> LandFloat:
    LandFloat p = dx / (fabs(dx) + fabs(dy))

    if (dy > 0):
        return (3 - p) / 4 # [0..1]
    else:
        return (1 + p) / 4 # [0..1]

def _dist(LandFloat ax, ay, bx, by) -> LandFloat:
    LandFloat dx = ax - bx
    LandFloat dy = ay - by
    return dx * dx + dy * dy

# return 2d orientation sign if we're confident in it through J. Shewchuk's error bound check
def orientIfSure(LandFloat px, py, rx, ry, qx, qy) -> LandFloat:
    LandFloat l = (ry - py) * (qx - px)
    LandFloat r = (rx - px) * (qy - py)

    if (fabs(l - r) >= 3.3306690738754716e-16 * fabs(l + r)):
        return l - r
    else:
        return 0.0

# a more robust orientation test that's stable in a given triangle (to fix robustness issues)
def orient(LandFloat rx, ry, qx, qy, px, py) -> bool:
    LandFloat x = orientIfSure(px, py, rx, ry, qx, qy)
    if x == 0.0:
        x = orientIfSure(rx, ry, qx, qy, px, py)
    if x == 0.0:
        x = orientIfSure(qx, qy, px, py, rx, ry)
    return x < 0

def inCircle(LandFloat ax, ay, bx, by, cx, cy, px, py) -> bool:
    LandFloat dx = ax - px
    LandFloat dy = ay - py
    LandFloat ex = bx - px
    LandFloat ey = by - py
    LandFloat fx = cx - px
    LandFloat fy = cy - py

    LandFloat ap = dx * dx + dy * dy
    LandFloat bp = ex * ex + ey * ey
    LandFloat cp = fx * fx + fy * fy

    return dx * (ey * cp - bp * fy) -\
           dy * (ex * cp - bp * fx) +\
           ap * (ex * fy - ey * fx) < 0

def circumradius(LandFloat ax, ay, bx, by, cx, cy) -> LandFloat:
    LandFloat dx = bx - ax
    LandFloat dy = by - ay
    LandFloat ex = cx - ax
    LandFloat ey = cy - ay

    LandFloat bl = dx * dx + dy * dy
    LandFloat cl = ex * ex + ey * ey

    LandFloat d = 0.5/(dx * ey - dy * ex)
   
    LandFloat x = (ey * bl - dy * cl) * d
    LandFloat y = (dx * cl - ex * bl) * d

    return x*x + y*y

def circumcenter(LandFloat ax, ay, bx, by, cx, cy) -> Point2D:
    LandFloat dx = bx - ax
    LandFloat dy = by - ay
    LandFloat ex = cx - ax
    LandFloat ey = cy - ay

    LandFloat bl = dx * dx + dy * dy
    LandFloat cl = ex * ex + ey * ey
    LandFloat d = 0.5/(dx * ey - dy * ex)

    Point2D p
    p.x = ax + (ey * bl - dy * cl) * d
    p.y = ay + (dx * cl - ex * bl) * d
    return p

def centroid(LandFloat ax, ay, bx, by, cx, cy) -> Point2D:
    Point2D p
    p.x = (ax + bx + cx) / 3
    p.y = (ay + by + cy) / 3
    return p

def quicksort(IntArray *ids, FloatArray *dists, int left, right):
    if (right - left <= 20):
        for int i in range(left + 1,right+1):
            int temp = ids.ints[i]
            LandFloat tempDist = dists.floats[temp]
            int j = i-1
            while (j >= left and dists.floats[ids.ints[j]] > tempDist):
                ids.ints[j + 1] = ids.ints[j]
                j-=1
            ids.ints[j + 1] = temp

    else:
        int median = (left + right) >> 1
        int i = left + 1
        int j = right
        swap(ids, median, i)

        if (dists.floats[ids.ints[left]] > dists.floats[ids.ints[right]]):
            swap(ids, left, right)

        if (dists.floats[ids.ints[i]] > dists.floats[ids.ints[right]]):
            swap(ids, i, right)

        if (dists.floats[ids.ints[left]] > dists.floats[ids.ints[i]]):
            swap(ids, left, i)

        int temp = ids.ints[i]
        LandFloat tempDist = dists.floats[temp]

        while True:
            while i < ids.n - 1:
                i+=1
                if (dists.floats[ids.ints[i]] >= tempDist): break

            while j > 0:
                j-=1
                if (dists.floats[ids.ints[j]] <= tempDist): break

            if (j < i): break
            swap(ids, i, j);

        ids.ints[left + 1] = ids.ints[j]
        ids.ints[j] = temp;

        if (right - i + 1 >= j - left):
            quicksort(ids, dists, i, right)
            quicksort(ids, dists, left, j - 1)

        else:
            quicksort(ids, dists, left, j - 1)
            quicksort(ids, dists, i, right)

def swap(IntArray *arr, int i, j):
    int tmp = arr.ints[i]
    arr.ints[i] = arr.ints[j]
    arr.ints[j] = tmp

def next_halfedge(int e) -> int: return e - 2 if e % 3 == 2 else e + 1
def triangle_of_edge(int e) -> int: return e // 3

def points_of_triangle(Delaunator *self, int t, int *p0, *p1, *p2):
    *p0 = self.triangles.ints[3 * t + 0]
    *p1 = self.triangles.ints[3 * t + 1]
    *p2 = self.triangles.ints[3 * t + 2]

def triangle_center(Delaunator *self, int t, center_type, LandFloat *result):
    int p0, p1, p2
    points_of_triangle(self, t, &p0, &p1, &p2)
    LandFloat *f = self.coords.floats
    Point2D center
    if center_type == 0:
        center = circumcenter(
            f[p0 * 2 + 0], f[p0 * 2 + 1],
            f[p1 * 2 + 0], f[p1 * 2 + 1],
            f[p2 * 2 + 0], f[p2 * 2 + 1])
    else:
        center = centroid(
            f[p0 * 2 + 0], f[p0 * 2 + 1],
            f[p1 * 2 + 0], f[p1 * 2 + 1],
            f[p2 * 2 + 0], f[p2 * 2 + 1])
    result[0] = center.x
    result[1] = center.y

def edges_around_point(Delaunator *self, int start, int *end) -> LandBuffer*:
    # start is an edge leading into the point
    LandBuffer *result = land_buffer_new()
    int incoming = start
    while True:
        land_buffer_add_uint32_t(result, incoming)
        int outgoing = next_halfedge(incoming)
        incoming = self.halfedges.ints[outgoing]
        if incoming == -1: break
        if incoming == start: break
    *end = incoming
    return result

def for_each_triangle(Delaunator *self, void (*callback)(int a, int b, int c, void *user), void *user):
    if self.coords.n // 2 < 3: return
    for int t in range(self.triangles.n // 3):
        int a, b, c
        points_of_triangle(self, t, &a, &b, &c)
        callback(a, b, c, user);

def for_each_voronoi_edge(Delaunator *self,
        void (*callback)(LandFloat *xy, void *user), void *user):
    for int e in range(self.triangles.n):
        if e < self.halfedges.ints[e]:
            int t1 = triangle_of_edge(e)
            int t2 = triangle_of_edge(self.halfedges.ints[e])
            LandFloat xy[4]
            triangle_center(self, t1, 0, xy + 0)
            triangle_center(self, t2, 0, xy + 2)
            callback(xy, user);

# def _is_concave(LandFloat ax, ay, bx, by, cx, cy) -> bool:
    # return land_cross2d(bx - ax, by - ay, cx - ax, cy - ay) < 0

def _construct_two(Delaunator *self, LandFloat *xy0, LandFloat *xy1):
    LandFloat *f = self.coords.floats
    LandFloat x0 = f[0]
    LandFloat y0 = f[1]
    LandFloat x1 = f[2]
    LandFloat y1 = f[3]
    LandFloat dx = x1 - x0
    LandFloat dy = y1 - y0
    LandFloat ux = -dy
    LandFloat uy = dx
    xy0[0] = x0 - dx * 10000
    xy0[1] = y0 - dy * 10000
    xy0[2] = x0 + dx / 2 - ux * 10000
    xy0[3] = y0 + dy / 2 - uy * 10000
    xy0[4] = x0 + dx / 2 + ux * 10000
    xy0[5] = y0 + dy / 2 + uy * 10000
    xy1[0] = x1 + dx * 10000
    xy1[1] = y1 + dy * 10000
    xy1[2] = x1 - dx / 2 + ux * 10000
    xy1[3] = y1 - dy / 2 + uy * 10000
    xy1[4] = x1 - dx / 2 - ux * 10000
    xy1[5] = y1 - dy / 2 - uy * 10000

#macro _NO_CLIP

def land_delaunator_for_each_voronoi_cell(Delaunator *self, #int center,
        void (*callback)(int i, LandFloat *xy, int *neighbors, int n,
        void *user), void *user):
    int n = self.coords.n // 2

    if n == 2:
        LandFloat xy0[3 * 2 * 2]
        LandFloat xy0_[6 * 2 * 2]
        LandFloat xy1[3 * 2 * 2]
        LandFloat xy1_[6 * 2 * 2]
        _construct_two(self, xy0, xy1)
        int n0[] = {1, -1, -1}
        int n1[] = {0, -1, -1}
        int n0_[6]
        int n1_[6]
        int en0 = _clip(self, 0, xy0, n0, 3, xy0_, n0_)
        int en1 = _clip(self, 1, xy1, n1, 3, xy1_, n1_)
        callback(0, xy0_, n0_, en0, user)
        callback(1, xy1_, n1_, en1, user)
        return

    # we find an incoming edge for each node (if incomplete, the left-most one)
    int index_incoming[n] # point-id to half-edge-id
    int index_outgoing[n]
    for int i in range(n):
        index_incoming[i] = -1
        index_outgoing[i] = -1
    for int e in range(self.triangles.n):
        int e2 = next_halfedge(e)
        int endpoint = self.triangles.ints[e2]
        int endpoint_out = self.triangles.ints[e]
        if index_incoming[endpoint] == -1 or self.halfedges.ints[e] == -1:
            index_incoming[endpoint] = e
        if index_outgoing[endpoint_out] == -1 or self.halfedges.ints[e] == -1:
            index_outgoing[endpoint_out] = e

    if False:
        printf("          ")
        for int e in range(self.triangles.n):
            printf(" %2d", e)
            if e % 3 == 2: printf(" | ")
        print("")
        printf("triangles:")
        for int e in range(self.triangles.n):
            printf(" %2d", self.triangles.ints[e])
            if e % 3 == 2: printf(" | ")
        print("")
        printf("halfedges:")
        for int e in range(self.halfedges.n):
            int h = self.halfedges.ints[e]
            if h == -1: printf(" --")
            else: printf(" %2d", h)
            if e % 3 == 2: printf(" | ")
        print("")
        for int i in range(n):
            print("index %d inc=%d out=%d", i, index_incoming[i], index_outgoing[i])

    for int p in range(n):
        int incoming = index_incoming[p]
        int outgoing = index_outgoing[p]
        if incoming == -1: continue
        int end = -1
        LandBuffer *edges = edges_around_point(self, incoming, &end)
        # we have all the incoming edges only, for points on the hull
        # we will be missing the last edge (outgoing only)
        int en = land_buffer_len_uint32(edges)
        LandFloat xy[2 * (3 + en)]
        int neighbors[3 + en]
        for int ei in range(en):
            int e = land_buffer_get_uint32_by_index(edges, ei)
            int t = triangle_of_edge(e)
            neighbors[ei] = self.triangles.ints[e]
            triangle_center(self, t, 0, xy + ei * 2)

        # for hull cells add some distant points
        if end == -1:
            int e1 = incoming
            int e2 = next_halfedge(outgoing)
            int p1 = self.triangles.ints[e1]
            int p2 = self.triangles.ints[e2]
            LandFloat *xyl = xy + en * 2
            _add_normal(self, p, p2, 10000.0, xyl - 2, xyl)
            _add_normal(self, p1, p, 10000.0, xy, xyl + 2)
            neighbors[en + 0] = p2
            neighbors[en + 1] = p1
            en += 2

        LandFloat xy2[2 * 2 * en]
        int neighbors2[2 * en]
        en = _clip(self, p, xy, neighbors, en, xy2, neighbors2)
        callback(p, xy2, neighbors2, en, user)
        land_buffer_destroy(edges)

def _add_normal(Delaunator *self, int p1, p2, LandFloat distance, *last, *add):
    LandFloat *f = self.coords.floats
    LandFloat ny = f[p2 * 2 + 0] - f[p1 * 2 + 0]
    LandFloat nx = f[p2 * 2 + 1] - f[p1 * 2 + 1]
    LandFloat n = sqrt(nx * nx + ny * ny)
    nx /= n
    ny /= n
    add[0] = last[0] - nx * distance
    add[1] = last[1] + ny * distance

def _move(LandFloat *a, *b, t, *out):
    out[0] = a[0] + t * (b[0] - a[0])
    out[1] = a[1] + t * (b[1] - a[1])
    
def _check_top(Delaunator *self, LandFloat *xy) -> bool: return xy[1] < self.by1
def _check_bot(Delaunator *self, LandFloat *xy) -> bool: return xy[1] > self.by2
def _check_lef(Delaunator *self, LandFloat *xy) -> bool: return xy[0] < self.bx1
def _check_rig(Delaunator *self, LandFloat *xy) -> bool: return xy[0] > self.bx2
def _clip_top(Delaunator *self, LandFloat *a, *b, *out): _move(a, b, (self.by1 - a[1]) / (b[1] - a[1]), out)
def _clip_bot(Delaunator *self, LandFloat *a, *b, *out): _move(a, b, (self.by2 - a[1]) / (b[1] - a[1]), out)
def _clip_lef(Delaunator *self, LandFloat *a, *b, *out): _move(a, b, (self.bx1 - a[0]) / (b[0] - a[0]), out)
def _clip_rig(Delaunator *self, LandFloat *a, *b, *out): _move(a, b, (self.bx2 - a[0]) / (b[0] - a[0]), out)

def _too_close(int cell, LandFloat *a, *b) -> bool:
    LandFloat dx = b[0] - a[0]
    LandFloat dy = b[1] - a[1]
    if cell == DEBUG_NODE:
        print("distance: %f/%f to %f/%f -> %f", a[0], a[1], b[0], b[1], dx * dx + dy * dy)
    if dx * dx + dy * dy < EPSILON:
        return True
    return False

def _add_point(int cell, int i, LandFloat *xy, int *neighbors, LandFloat *point, int neighbor) -> int:
    if i > 0:
        if _too_close(cell, xy + i * 2 - 2, point):
            if cell == DEBUG_NODE: print("cannot add close prev point")
            return i
        if i > 1:
            if _too_close(cell, xy , point):
                if cell == DEBUG_NODE: print("cannot add close initial point")
                return i
    xy[i * 2 + 0] = point[0]
    xy[i * 2 + 1] = point[1]
    neighbors[i] = neighbor
    if cell == DEBUG_NODE:
        print("insert point towards %d (%.1f/%.1f)",
            neighbors[i], xy[i * 2 + 0], xy[i * 2 + 1])
    return i + 1

def _clip_side(Delaunator *self, int cell, LandFloat *xy, int *neighbors, int n,
        LandFloat *xy2, int *neighbors2,
        bool (*check_out)(Delaunator *self, LandFloat *xy),
        void (*get_int)(Delaunator *self, LandFloat *a, LandFloat *b, LandFloat *out)) -> int:
    if n < 3:
        return 0
    int o = 0
    LandFloat p[2] = {xy[0], xy[1]}
    bool fout = check_out(self, xy)
    bool pout = fout
    if cell == DEBUG_NODE:
        printf("before clip:")
        for int i in range(n):
            printf(" %d", neighbors[i])
        print("")
    if not pout:
        xy2[0] = p[0]
        xy2[1] = p[1]
        neighbors2[0] = neighbors[0]
        o++
    elif cell == DEBUG_NODE:
        print("skipped %d (%.1f/%.1f)", neighbors[0], p[0], p[1])
    for int i in range(1, n):
        LandFloat a[2] = {xy[i * 2 + 0], xy[i * 2 + 1]}
        bool out = check_out(self, a)
        if out:
            if pout:
                # entire segment is out, just remove it
                if cell == DEBUG_NODE:
                    print("entire segment to %d is out (to %.1f/%.1f)",
                        neighbors[i], a[0], a[1])
            else:
                # we are out but previous is not, insert intersection point
                LandFloat ip[2]
                get_int(self, p, a, ip)
                o = _add_point(cell, o, xy2, neighbors2, ip, neighbors[i])
        else:
            if pout:
                # previous was out, we are not, add intersection point
                LandFloat ip[2]
                get_int(self, p, a, ip)
                o = _add_point(cell, o, xy2, neighbors2, ip, -1)
            o = _add_point(cell, o, xy2, neighbors2, a, neighbors[i])
        pout = out
        p[0] = a[0]
        p[1] = a[1]
    if fout:
        if not pout:
            LandFloat ip[2]
            get_int(self, p, xy, ip)
            o = _add_point(cell, o, xy2, neighbors2, ip, neighbors[0])
    else:
        if pout:
            LandFloat ip[2]
            get_int(self, p, xy, ip)
            o = _add_point(cell, o, xy2, neighbors2, ip, -1)
    if cell == DEBUG_NODE:
        printf("after clip:")
        for int i in range(o):
            printf(" %d", neighbors2[i])
        print("")
    return o

def _clip(Delaunator *self, int p, LandFloat *xy, int *neighbors, int n,
        LandFloat *xy_out, int *neighbors_out) -> int:
    *** "ifdef" _NO_CLIP
    for int i in range(n):
        neighbors_out[i] = neighbors[i]
        xy_out[i * 2 + 0] = xy[i * 2 + 0]
        xy_out[i * 2 + 1] = xy[i * 2 + 1]
    return n
    *** "endif"
    LandFloat xy2[n * 2 * 2]
    int neighbors2[n * 2]
    int n2 = _clip_side(self, p, xy, neighbors, n, xy2, neighbors2, _check_top, _clip_top)
    LandFloat xy3[n2 * 2 * 2]
    int neighbors3[n2 * 2]
    int n3 = _clip_side(self, p, xy2, neighbors2, n2, xy3, neighbors3, _check_bot, _clip_bot)
    LandFloat xy4[n3 * 2 * 2]
    int neighbors4[n3 * 2]
    int n4 = _clip_side(self, p, xy3, neighbors3, n3, xy4, neighbors4, _check_lef, _clip_lef)
    int n5 = _clip_side(self, p, xy4, neighbors4, n4, xy_out, neighbors_out, _check_rig, _clip_rig)
    return n5
