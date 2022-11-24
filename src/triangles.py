import land.buffer
import land.image
import allegro5.a5_display
import allegro5.a5_triangles
import land.csg.csg

class LandTriangles:
    int n # number of vertices (not triangles)
    int size # size of a single vertex, in bytes
    bool has_normals
    bool has_texture
    LandBuffer *buf
    LandImage *image
    void *platform
    bool can_cache

def land_triangles_new -> LandTriangles*:
    LandTriangles *self; land_alloc(self)
    self.can_cache = True
    self.has_texture = True
    platform_triangles_init(self)
    return self

def land_triangles_new_with_normals -> LandTriangles*:
    LandTriangles *self; land_alloc(self)
    self.has_normals = True
    self.has_texture = True
    self.can_cache = True
    platform_triangles_init(self)
    return self

def land_triangles_new_with_normals_no_texture -> LandTriangles*:
    LandTriangles *self; land_alloc(self)
    self.has_normals = True
    self.can_cache = True
    platform_triangles_init(self)
    return self

def land_triangles_new_no_texture -> LandTriangles*:
    LandTriangles *self; land_alloc(self)
    self.can_cache = True
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

def land_triangles_destroy_with_image(LandTriangles *self):
    land_image_destroy(self.image)
    self.image = None
    return platform_triangles_deinit(self)

def land_triangles_clear(LandTriangles *self):
    self.n = 0
    if self.buf:
        land_buffer_clear(self.buf)

def land_triangles_refresh(LandTriangles* self):
    platform_triangles_refresh(self)

def land_triangles_texture(LandTriangles *self, LandImage *texture):
    """
    Ownership remains at the caller.
    """
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
    """
    -1 .. duplicate most recent
    -2 .. duplicate the second most recent
    ...
    """
    self.n++
    land_buffer_grow(self.buf, self.size)
    land_buffer_move(self.buf, self.size * (-1 + i), -self.size, self.size)

def land_update_vertex(LandTriangles *self, int i, float x, y, z, u, v, r, g, b, a):
    platform_update_vertex(self, i, x, y, z, u, v, r, g, b, a)

def land_triangles_draw(LandTriangles *self):
    if not self.n: return
    platform_triangles_draw(self, False)

def land_triangles_draw_more(LandTriangles *self, bool more):
    if not self.n: return
    platform_triangles_draw(self, more)

def land_triangles_prepare_draw(LandTriangles *self, bool more):
    if not self.n: return
    platform_triangles_prepare_draw(self, more)

def land_triangles_perform_draw(LandTriangles *self):
    if not self.n: return
    platform_triangles_perform_draw(self)

def land_triangles_get_vertex(LandTriangles* self, int i) -> void*:
    char* pointer = self.buf.buffer
    pointer += i * self.size
    return pointer

def land_triangles_draw_debug(LandTriangles *self):
    for int i in range(0, self.n, 3):
        float xy[6], z[1]
        platform_triangles_get_xyz(self, i + 0, xy + 0, xy + 1, z)
        platform_triangles_get_xyz(self, i + 1, xy + 2, xy + 3, z)
        platform_triangles_get_xyz(self, i + 2, xy + 4, xy + 5, z)
        land_polygon(3, xy)

def land_triangles_can_cache(LandTriangles* self, bool can_cache):
    self.can_cache = can_cache

def land_triangles_shader(LandTriangles* self, str id, vertex, fragment):
    platform_triangles_shader(self, id, vertex, fragment)

def land_triangles_set_light_direction(LandVector light):
    platform_triangles_set_light_direction(light)

def land_triangles_set_light(float light):
    platform_triangles_set_light(light)

def land_triangles_get_max_z(LandTriangles *self) -> LandFloat:
    float maxz = INT_MIN
    for int i in range(0, self.n):
        float x, y, z
        platform_triangles_get_xyz(self, i + 0, &x, &y, &z)
        if z > maxz: maxz = z
    return maxz

def land_triangles_get_max_y(LandTriangles *self) -> LandFloat:
    float maxy = INT_MIN
    for int i in range(0, self.n):
        float x, y, z
        platform_triangles_get_xyz(self, i + 0, &x, &y, &z)
        if y > maxy: maxy = y
    return maxy
