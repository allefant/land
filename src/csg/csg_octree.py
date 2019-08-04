import land.array
import land.common
import land.mem
import csg_aabb

class LandOctree:
    LandArray** data
    int xs, ys, zs
    int xo, yo, zo
    int cx, cy, cz

def land_octree_new(int xs, ys, zs, xo, yo, zo, cx, cy, cz) -> LandOctree*:
    LandOctree *self; land_alloc(self)
    self.data = land_calloc(xs * ys * zs * sizeof *self.data)
    self.xs = xs
    self.ys = ys
    self.zs = zs
    self.xo = xo
    self.yo = yo
    self.zo = zo
    self.cx = cx
    self.cy = cy
    self.cz = cz
    return self

def land_octree_new_from_aabb(LandCSGAABB *aabb, int count) -> LandOctree*:
    return land_octree_new(count, count, count,
        aabb.x1, aabb.y1, aabb.z1,
        (aabb.x2 - aabb.x1) / count,
        (aabb.y2 - aabb.y1) / count,
        (aabb.z2 - aabb.z1) / count)

def land_octree_del(LandOctree *self):
    int n = self.xs * self.ys * self.zs
    for int i in range(n):
        if self.data[i]: land_array_destroy(self.data[i])
    land_free(self.data)
    land_free(self)

def between(int x, a, b) -> int:
    if x < a: return a
    if x > b: return b
    return x

def _getx(LandOctree *self, LandFloat x) -> int:
    return between((x - self.xo) / self.cx, 0, self.xs - 1)

def _gety(LandOctree *self, LandFloat y) -> int:
    return between((y - self.yo) / self.cy, 0, self.ys - 1)

def _getz(LandOctree *self, LandFloat z) -> int:
    return between((z - self.zo) / self.cz, 0, self.zs - 1)

def _get_i(LandOctree *self, LandFloat x, y, z) -> int:
    int xi = _getx(self, x)
    int yi = _getx(self, y)
    int zi = _getx(self, z)
    return xi + yi * self.xs + zi * self.xs * self.ys

def land_octree_insert(LandOctree *self, LandFloat x, y, z, void *data):
    int i = _get_i(self, x, y, z)
    LandArray *array = self.data[i]
    if not array:
        array = self.data[i] = land_array_new()
    land_array_add(array, data)

def land_octree_get(LandOctree *self, LandFloat x, y, z) -> LandArray*:
    int i = _get_i(self, x, y, z)
    return self.data[i]

def land_octree_callback_in_cube(LandOctree *self, LandFloat x1, y1, z1,
        x2, y2, z2, void (*callback)(LandArray *array, void *data), void *data):
    int ix1 = _getx(self, x1)
    int ix2 = _getx(self, x2)
    int iy1 = _gety(self, y1)
    int iy2 = _gety(self, y2)
    int iz1 = _getz(self, z1)
    int iz2 = _getz(self, z2)
    for int ix in range(ix1, ix2 + 1):
        for int iy in range(iy1, iy2 + 1):
            for int iz in range(iz1, iz2 + 1):
                callback(self.data[ix + iy * self.xs + iz * self.xs * self.ys], data)
