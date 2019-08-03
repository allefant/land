import land.buffer
import land.image
import allegro5.a5_display
import allegro5.a5_triangles
import land.csg.csg

class LandTriangles:
    int n # number of vertices (not triangles)
    int size # size of a single vertex, in bytes
    bool has_normals
    LandBuffer *buf
    LandImage *image
    void *platform
    
def land_triangles_new -> LandTriangles*:
    LandTriangles *self; land_alloc(self)
    platform_triangles_init(self)
    return self

def land_triangles_new_with_normals -> LandTriangles*:
    LandTriangles *self; land_alloc(self)
    self.has_normals = True
    platform_triangles_init(self)
    return self

def land_triangles_add_csg(LandTriangles* self, LandCSG *csg):
    """
    Note: All polygons contained in the CSG must be triangles.
    
    Note: No reference to the CSG is kept so you can safely destroy it
    after this function returns.
    """
    for LandCSGPolygon *p in LandArray *csg.polygons:
        for int j in range(3):
            LandCSGVertex *v = land_array_get_nth(p.vertices, j)
            land_add_vertex(self, v.pos.x, v.pos.y, v.pos.z, 0, 0,
                v.rgba.r, v.rgba.g, v.rgba.b, v.rgba.a)
            land_set_vertex_normal(self, v.normal.x, v.normal.y, v.normal.z)
            land_set_vertex_index(self, j)

def land_triangles_destroy(LandTriangles *self):
    return platform_triangles_deinit(self)

def land_triangles_clear(LandTriangles *self):
    self.n = 0

def land_triangles_texture(LandTriangles *self, LandImage *texture):
    self.image = texture

def land_add_vertex(LandTriangles *self, float x, y, z, u, v, r, g, b, a):
    self.n++
    if not self.buf:
        self.buf = land_buffer_new()
    land_buffer_grow(self.buf, self.size)
    land_update_vertex(self, self.n - 1, x, y, z, u, v, r, g, b, a)

def land_set_vertex_normal(LandTriangles *self, float x, y, z):
    platform_set_vertex_normal(self, x, y, z)

def land_set_vertex_index(LandTriangles *self, float i):
    platform_set_vertex_index(self, i)

def land_duplicate_vertex(LandTriangles *self, int i):
    self.n++
    land_buffer_grow(self.buf, self.size)
    land_buffer_move(self.buf, self.size * (-1 + i), -self.size, self.size)

def land_update_vertex(LandTriangles *self, int i, float x, y, z, u, v, r, g, b, a):
    platform_update_vertex(self, i, x, y, z, u, v, r, g, b, a)

def land_triangles_draw(LandTriangles *self):
    platform_triangles_draw(self)

def land_triangles_get_vertex(LandTriangles* self, int i) -> void*:
    char* pointer = self.buf.buffer
    pointer += i * self.size
    return pointer
