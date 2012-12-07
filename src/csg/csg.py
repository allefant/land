# Code here follows https://github.com/evanw/csg.js/blob/master/csg.js

# Constructive Solid Geometry

import land.array
import land.util3d
static import land.mem
import land.pool

class LandCSG:
    LandArray *polygons # LandCSGPolygon
    LandMemoryPool *pool

class LandCSGVertex:
    LandVector pos
    LandVector normal

class LandCSGPlane:
    LandVector normal
    LandFloat w

class LandCSGPolygon:
    LandArray *vertices # LandCSGVertex
    void *shared
    LandCSGPlane plane

class LandCSGNode:
    """
    A simple BSP tree.
    """
    LandCSGPlane plane
    LandCSGNode *front
    LandCSGNode *back
    LandArray *polygons # LandCSGPolygon

LandCSGVertex *def land_csg_vertex_new(LandVector pos, normal):
    LandCSGVertex *self; land_alloc(self)
    self->pos = pos
    self->normal = normal
    return self

def land_csg_vertex_destroy(LandCSGVertex *self):
    land_free(self)

LandCSGVertex *def csg_vertex_clone(LandCSG *csg, LandCSGVertex *self):
    #return land_csg_vertex_new(self->pos, self->normal)
    LandCSGVertex *v = land_pool_alloc(csg->pool, sizeof *v)
    v->pos = self->pos
    v->normal = self->normal
    return v

static LandArray *def clone_vertices(LandCSG *csg, LandArray *vertices):
    LandArray *clone = land_array_copy(vertices)
    for int i in range(land_array_count(clone)):
        clone->data[i] = csg_vertex_clone(csg, clone->data[i])
    return clone

static def clear_vertices(LandArray *vertices):
    #for int i in range(vertices->count):
    #    land_csg_vertex_destroy(vertices->data[i])
    land_array_clear(vertices)

static def csg_vertex_flip(LandCSGVertex *self):
    self->normal = land_vector_mul(self->normal, -1)

static LandCSGVertex *def csg_vertex_interpolate(LandCSG *csg,
        LandCSGVertex *self, *other, LandFloat t):
    #return land_csg_vertex_new(
    LandCSGVertex *v = land_pool_alloc(csg->pool, sizeof *v)
    v->pos = land_vector_lerp(self->pos, other->pos, t)
    v->normal = land_vector_lerp(self->normal, other->normal, t)
    return v

static LandCSGPlane def csg_plane(LandVector normal, LandFloat w):
    LandCSGPlane self
    self.normal = normal
    self.w = w
    return self

static const LandFloat LandCSGPlaneEPSILON = 0.00001

static LandCSGPlane def csg_plane_from_points(LandVector a, b, c):
    LandVector ac = land_vector_sub(c, a)
    LandVector ab = land_vector_sub(b, a)
    LandVector n = land_vector_cross(ab, ac)
    n = land_vector_normalize(n)
    return csg_plane(n, land_vector_dot(n, a))

def csg_plane_flip(LandCSGPlane *self):
    self->normal = land_vector_mul(self->normal, -1)
    self->w *= -1

# Split the polygon along this plane. Then put a copy of the polygon (or
# new polygon fragments) into the 4 lists.
# Ownership of the polygon remains at the caller.
# A polygon is put in at most one list.
static def csg_plane_split_polygon(LandCSG *csg,
        LandCSGPlane *self,
        #LandCSGPolygon const *polygon,
        LandCSGPolygon *polygon,
        LandArray *coplanar_front, *coplanar_back, *front, *back):
    
    const int COPLANAR = 0
    const int FRONT = 1
    const int BACK = 2
    const int SPANNING = 3

    int polygon_type = 0
    int n = land_array_count(polygon->vertices)
    int i = 0
    int types[n]
    for LandCSGVertex *v in LandArray *polygon->vertices:
        LandFloat t = land_vector_dot(self->normal, v->pos) - self->w
        int type = t < -LandCSGPlaneEPSILON ? BACK : t > LandCSGPlaneEPSILON ? FRONT : COPLANAR
        polygon_type |= type
        types[i++] = type
    assert(i == n)

    if polygon_type == COPLANAR:
        LandArray *a
        if land_vector_dot(self->normal, polygon->plane.normal) > 0:
            a = coplanar_front
        else:
            a = coplanar_back;
        #land_array_add(a, land_csg_polygon_clone(csg, polygon))
        land_array_add(a, polygon)
    elif polygon_type == FRONT:
        #land_array_add(front, land_csg_polygon_clone(csg, polygon))
        land_array_add(front, polygon)
    elif polygon_type == BACK:
        #land_array_add(back, land_csg_polygon_clone(csg, polygon))
        land_array_add(back, polygon)
    elif polygon_type == SPANNING:
        LandArray *f = land_array_new()
        LandArray *b = land_array_new()
        for i in range(n):
            int j = (i + 1) % n
            int ti = types[i]
            int tj = types[j]
            LandCSGVertex *vi = land_array_get_nth(polygon->vertices, i)
            LandCSGVertex *vj = land_array_get_nth(polygon->vertices, j)

            if ti == FRONT:
                land_array_add(f, csg_vertex_clone(csg, vi))
            elif ti == BACK:
                land_array_add(b, csg_vertex_clone(csg, vi))
            elif ti == COPLANAR:
                land_array_add(f, csg_vertex_clone(csg, vi))
                land_array_add(b, csg_vertex_clone(csg, vi))

            if (ti | tj) == SPANNING:
                LandFloat t = self->w - land_vector_dot(self->normal, vi->pos)
                t /= land_vector_dot(self->normal, land_vector_sub(vj->pos, vi->pos))
                LandCSGVertex *v = csg_vertex_interpolate(csg, vi, vj, t)
                land_array_add(f, v)
                land_array_add(b, csg_vertex_clone(csg, v))

        if land_array_count(f) >= 3:
            LandCSGPolygon *add = land_pool_alloc(csg->pool, sizeof *add)
            # land_csg_polygon_new
            land_csg_polygon_init(add, f, polygon->shared)
            land_array_add(front, add)
        else:
            clear_vertices(f)
            land_array_destroy(f)

        if land_array_count(b) >= 3:
            LandCSGPolygon *add = land_pool_alloc(csg->pool, sizeof *add)
            # land_csg_polygon_new
            land_csg_polygon_init(add, b, polygon->shared)
            land_array_add(back, add)
        else:
            clear_vertices(b)
            land_array_destroy(b)

# The array is owned by the polygon now.
def land_csg_polygon_init(LandCSGPolygon *self, LandArray *vertices,
        void *shared):
    self->vertices = vertices
    self->shared = shared
    LandCSGVertex *v0 = land_array_get_nth(vertices, 0)
    LandCSGVertex *v1 = land_array_get_nth(vertices, 1)
    LandCSGVertex *v2 = land_array_get_nth(vertices, 2)
    self->plane = csg_plane_from_points(v0->pos, v1->pos, v2->pos)

LandCSGPolygon *def land_csg_polygon_new(LandArray *vertices,
        void *shared):
    LandCSGPolygon *self; land_alloc(self)
    land_csg_polygon_init(self, vertices, shared)
    return self

def land_csg_polygon_destroy(LandCSGPolygon *self):
    clear_vertices(self->vertices)
    land_array_destroy(self->vertices)
    land_free(self)

LandCSGPolygon *def land_csg_polygon_clone(LandCSG *csg,
        LandCSGPolygon const *self):
    
    #LandCSGPolygon *clone = land_csg_polygon_new(
    LandCSGPolygon *clone = land_pool_alloc(csg->pool, sizeof *clone)
    land_csg_polygon_init(clone,
        clone_vertices(csg, self->vertices), self->shared)
    return clone

static def csg_polygon_flip(LandCSGPolygon *self):
    land_array_reverse(self->vertices)
    for LandCSGVertex *v in LandArray *self->vertices:
        csg_vertex_flip(v)

    csg_plane_flip(&self->plane)

static LandArray *def clone_polygons(LandCSG *csg, LandArray *polygons):
    LandArray *clone = land_array_copy(polygons)
    for int i in range(land_array_count(clone)):
        clone->data[i] = land_csg_polygon_clone(csg, clone->data[i])
    return clone

static def clear_polygons(LandArray *polygons):
    #for int i in range(polygons->count):
    #    land_csg_polygon_destroy(polygons->data[i])
    land_array_clear(polygons)

static def csg_node_destroy(LandCSGNode *self):
    if self->front:
        csg_node_destroy(self->front)
    if self->back:
        csg_node_destroy(self->back)
    clear_polygons(self->polygons)
    land_array_destroy(self->polygons)
    land_free(self)

static def csg_node_invert(LandCSGNode *self):
    for LandCSGPolygon *p in LandArray *self->polygons:
        csg_polygon_flip(p)
    csg_plane_flip(&self->plane)

    if self->front:
        csg_node_invert(self->front)

    if self->back:
        csg_node_invert(self->back)

    LandCSGNode *temp = self->front
    self->front = self->back
    self->back = temp

# Remove polygons inside this BSP from the passed array.
static def csg_node_clip_polygons(LandCSG *csg, LandCSGNode *self,
        LandArray *polygons):
    if not self->plane.normal.z and not self->plane.normal.y and\
            not self->plane.normal.x:
        return

    LandArray *front = land_array_new()
    LandArray *back = land_array_new()

    for LandCSGPolygon *p in LandArray *polygons:
        csg_plane_split_polygon(csg, &self->plane, p, front, back, front, back)

    # front/back now contain cloned and/or new polygons, so we can destroy
    # the original ones.
    clear_polygons(polygons)

    if self->front:
        csg_node_clip_polygons(csg, self->front, front)

    if self->back:
        csg_node_clip_polygons(csg, self->back, back)
    else:
        clear_polygons(back)

    # now add back the polygons which survived 
    land_array_concat(polygons, front)
    land_array_concat(polygons, back)

    land_array_destroy(front)
    land_array_destroy(back)

# Remove all polygons which are inside bsp.
static def csg_node_clip_to(LandCSG *csg, LandCSGNode *self, LandCSGNode *bsp):
    csg_node_clip_polygons(csg, bsp, self->polygons)
    if self->front:
        csg_node_clip_to(csg, self->front, bsp)
    if self->back:
        csg_node_clip_to(csg, self->back, bsp)

# Return a new list containing all the polygons in this BSP.
# The returned list (as well as all polygons in that list) are owned
# by the caller.
static LandArray *def csg_node_all_polygons(LandCSG *csg, LandCSGNode *self):
    LandArray *polygons = clone_polygons(csg, self->polygons)

    if self->front:
        land_array_merge(polygons, csg_node_all_polygons(csg, self->front))
    if self->back:
        land_array_merge(polygons, csg_node_all_polygons(csg, self->back))

    return polygons

#static def csg_node_debug_info(LandCSGNode *self, char const *info):
#    LandArray *temp = csg_node_all_polygons(self)
#    printf("%s%p: %d polygons\n", info, self, temp->count)
#    clear_polygons(temp)
#    land_array_destroy(temp)

static LandCSGNode *def csg_node_new(LandCSG *csg, LandArray *polygons)

# Build a BSP tree from (or merge with) a list of polygons.
# Ownership of the polygons array is transferred. The caller must not access
# the array anymore.
static def csg_node_build(LandCSG *csg, LandCSGNode *self, LandArray *polygons):
    if not land_array_count(polygons):
        return
    if not self->plane.normal.z and\
            not self->plane.normal.y and not self->plane.normal.x:
        LandCSGPolygon *p0 = land_array_get_nth(polygons, 0)
        self->plane = p0->plane

    LandArray *front = land_array_new()
    LandArray *back = land_array_new()

    for LandCSGPolygon *p in LandArray *(LandArray *)polygons:
        csg_plane_split_polygon(csg, &self->plane, p, self->polygons,
            self->polygons, front, back)

    if land_array_count(front):
        if not self->front:
            self->front = csg_node_new(csg, None)
        csg_node_build(csg, self->front, front)
    else:
        land_array_destroy(front)

    if land_array_count(back):
        if not self->back:
            self->back = csg_node_new(csg, None)
        csg_node_build(csg, self->back, back)
    else:
        land_array_destroy(back)

    clear_polygons(polygons)
    land_array_destroy(polygons)

# Ownership of the polygons array is transferred to the CSG Node. If the caller
# still needs any polygons make a copy first.
static LandCSGNode *def csg_node_new(LandCSG *csg, LandArray *polygons):
    LandCSGNode *self; land_alloc(self)
    self->polygons = land_array_new()
    if polygons:
        csg_node_build(csg, self, polygons)
    return self

def land_csg_transform(LandCSG *self, Land4x4Matrix matrix):
    Land4x4Matrix matrix2 = *(&matrix)
    # The normal should not be translated (nor scaled, but the scaling is
    # taken care of be re-normalizing it)
    matrix2.v[3] = 0
    matrix2.v[7] = 0
    matrix2.v[11] = 0
    for LandCSGPolygon *p in LandArray *self->polygons:
        for LandCSGVertex *v in LandArray *p->vertices:
            v->pos = land_vector_matmul(v->pos, &matrix)
            v->normal = land_vector_normalize(
                land_vector_matmul(v->normal, &matrix2))

def land_csg_destroy(LandCSG *self):
    clear_polygons(self->polygons)
    land_array_destroy(self->polygons)
    land_pool_destroy(self->pool)
    land_free(self)

def land_csg_triangles(LandCSG *self):
    LandArray *triangles = None
    for LandCSGPolygon *p in LandArray *self->polygons:
        int n = land_array_count(p->vertices)
        if n == 3: continue

        if not triangles:
            triangles = land_array_new()

        # 0 1 2 remain in the existing polygon
        LandCSGVertex *a = land_array_get_nth(p->vertices, 0)
        LandCSGVertex *b = land_array_get_nth(p->vertices, 2)
        for int i in range(3, n):
            LandCSGVertex *c = land_array_get_nth(p->vertices, i)
            LandArray *v = land_array_new()
            land_array_add(v, csg_vertex_clone(self, a))
            land_array_add(v, csg_vertex_clone(self, b))
            land_array_add(v, c)
            LandCSGPolygon *triangle = land_csg_polygon_new(v, p->shared)
            land_array_add(triangles, triangle)
            b = c
        p->vertices->count = 3
    if triangles:
        land_array_merge(self->polygons, triangles)

LandCSG *def land_csg_new():
    LandCSG *self; land_alloc(self)
    self->pool = land_pool_new()
    return self

# The array is owned by the LandCSG now.
LandCSG *def land_csg_new_from_polygons(LandArray *polygons):
    LandCSG *self = land_csg_new()
    self->polygons = polygons
    return self

LandCSG *def land_csg_clone(LandCSG *self):
    LandCSG *csg = land_csg_new()
    csg->polygons = clone_polygons(self, self->polygons)
    return csg

LandCSG *def land_csg_union(LandCSG *self, *csg):
    LandCSG *c = land_csg_new()
    LandCSGNode *a = csg_node_new(c, clone_polygons(c, self->polygons))
    LandCSGNode *b = csg_node_new(c, clone_polygons(c, csg->polygons))

    csg_node_clip_to(c, a, b)
    csg_node_clip_to(c, b, a)
    csg_node_invert(b)
    csg_node_clip_to(c, b, a)
    csg_node_invert(b)

    csg_node_build(c, a, csg_node_all_polygons(c, b))

    c->polygons = csg_node_all_polygons(c, a)

    csg_node_destroy(a)
    csg_node_destroy(b)

    return c
    
LandCSG *def land_csg_subtract(LandCSG *self, *csg):
    LandCSG *c = land_csg_new()
    LandCSGNode *a = csg_node_new(c, clone_polygons(c, self->polygons))
    LandCSGNode *b = csg_node_new(c, clone_polygons(c, csg->polygons))

    csg_node_invert(a)
    csg_node_clip_to(c, a, b)
    csg_node_clip_to(c, b, a)
    csg_node_invert(b)
    csg_node_clip_to(c, b, a)
    csg_node_invert(b)
    csg_node_build(c, a, csg_node_all_polygons(c, b))
    csg_node_invert(a)

    c->polygons = csg_node_all_polygons(c, a)

    csg_node_destroy(a)
    csg_node_destroy(b)

    return c

LandCSG *def land_csg_intersect(LandCSG *self, *csg):
    LandCSG *c = land_csg_new()
    LandCSGNode *a = csg_node_new(c, clone_polygons(c, self->polygons))
    LandCSGNode *b = csg_node_new(c, clone_polygons(c, csg->polygons))

    csg_node_invert(a)
    csg_node_clip_to(c, b, a)
    csg_node_invert(b)
    csg_node_clip_to(c, a, b)
    csg_node_clip_to(c, b, a)
    csg_node_build(c, a, csg_node_all_polygons(c, b))
    csg_node_invert(a)

    c->polygons = csg_node_all_polygons(c, a)

    csg_node_destroy(a)
    csg_node_destroy(b)

    return c

LandCSG *def land_csg_inverse(LandCSG *self):
    LandCSG *csg = land_csg_clone(self)
    for LandCSGPolygon *p in LandArray *csg->polygons:
        csg_polygon_flip(p)
    return csg
