import land.array
static import csg

class LandCSGAABB:
    double x1, y1, z1, x2, y2, z2

def land_csg_aabb_infinite() -> LandCSGAABB:
    LandCSGAABB a
    a.x1 = -INFINITY
    a.x2 = +INFINITY
    a.y1 = -INFINITY
    a.y2 = +INFINITY
    a.z1 = -INFINITY
    a.z2 = +INFINITY
    return a

def land_csg_aabb_empty() -> LandCSGAABB:
    LandCSGAABB a
    a.x1 = +INFINITY
    a.x2 = -INFINITY
    a.y1 = +INFINITY
    a.y2 = -INFINITY
    a.z1 = +INFINITY
    a.z2 = -INFINITY
    return a

def land_csg_aabb_update(LandCSGAABB *self, LandArray *polygons):
    # FIXME: This does not work for open shapes.
    # For example an inverse cube.
    *self = land_csg_aabb_empty()
    for LandCSGPolygon *p in LandArray *polygons:
        for LandCSGVertex *v in LandArray *p->vertices:
            if v->pos.x < self.x1: self->x1 = v->pos.x
            if v->pos.x > self.x2: self->x2 = v->pos.x
            if v->pos.y < self.y1: self->y1 = v->pos.y
            if v->pos.y > self.y2: self->y2 = v->pos.y
            if v->pos.z < self.z1: self->z1 = v->pos.z
            if v->pos.z > self.z2: self->z2 = v->pos.z

def land_csg_aabb_intersect(LandCSGAABB a, b) -> LandCSGAABB:
    LandCSGAABB c = a
    if b.x1 > c.x1: c.x1 = b.x1
    if b.x2 < c.x2: c.x2 = b.x2
    if b.y1 > c.y1: c.y1 = b.y1
    if b.y2 < c.y2: c.y2 = b.y2
    if b.z1 > c.z1: c.z1 = b.z1
    if b.z2 < c.z2: c.z2 = b.z2
    return c
