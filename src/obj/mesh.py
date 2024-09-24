import land.util2d
import land.glsl
import land.obj.obj

class LandMeshFile:
    int n # the number of vertices
    int stride # floats to the next vertex
    GLfloat *v
    LandArray *markers # LandObjMarker
    LandCSGAABB aabb

def land_mesh_new() -> LandMeshFile *:
    LandMeshFile *self; land_alloc(self)
    self.stride = 11
    self.aabb = land_csg_aabb_empty()
    return self

def land_mesh_find_marker(LandMeshFile *self, char const *name) -> LandObjMarker *:
    if not self.markers:
        return None
    for LandObjMarker *m in LandArray *self.markers:
        if land_equals(m.name, name):
            return m
    return None

def land_mesh_destroy(LandMeshFile *self):
    if self.v:
        land_free(self.v)
    land_free(self)

def land_mesh_set_origin(LandMeshFile *self, float x, y, z):
    for int i in range(self.n):
        GLfloat *vt = self.v + self.stride * i
        vt[0] -= x
        vt[1] -= y
        vt[2] -= z

static def vec(GLfloat *xyz) -> LandVector:
    return land_vector(xyz[0], xyz[1], xyz[2])

def land_mesh_recalculate_normals(LandMeshFile *self):
    int s = self.stride
    for int i in range(0, self.n, 3):
        LandVector t0 = vec(self.v + s * (i + 0))
        LandVector t1 = vec(self.v + s * (i + 1))
        LandVector t2 = vec(self.v + s * (i + 2))
        LandVector a = land_vector_sub(t0, t1)
        LandVector b = land_vector_sub(t1, t2)
        LandVector n = land_vector_normalize(land_vector_cross(a, b))
        for int j in range(3):
            GLfloat *v = self.v + s * (i + j)
            v[3] = n.x
            v[4] = n.y
            v[5] = n.z

def land_mesh_triangle_callback(LandMeshFile *self, void (*callback)(LandVector t0,
        LandVector t1, LandVector t2, void *data), void *data):
    int s = self.stride
    for int i in range(0, self.n, 3):
        LandVector t0 = vec(self.v + s * (i + 0))
        LandVector t1 = vec(self.v + s * (i + 1))
        LandVector t2 = vec(self.v + s * (i + 2))
        callback(t0, t1, t2, data)

def _write_int(LandFile *f, int x):
    land_file_write(f, (char*)&x, sizeof x)
    
def _read_int(LandFile *f) -> int:
    int x
    land_file_read(f, (char*)&x, sizeof x)
    return x

def _write_string(LandFile *f, str s):
    int n = strlen(s)
    _write_int(f, n)
    land_file_write(f, s, n)

def _read_string(LandFile *f) -> char*:
    int n = _read_int(f)
    char* s = land_malloc(n + 1)
    land_file_read(f, s, n)
    s[n] = 0
    return s

def _write_mesh(LandMeshFile *self, LandFile *f):
    land_file_write(f, "MESH", 4)
    _write_int(f, self.n)
    _write_int(f, self.stride)
    land_file_write(f, (char*)self.v, self.n * self.stride * sizeof *self.v)
    land_file_write(f, "MARK", 4)
    int n = self.markers ? land_array_count(self.markers) : 0
    _write_int(f, n)
    if n:
        for LandObjMarker *m in LandArray* self.markers:
            _write_string(f, m.name)
            land_file_write(f, (char *)&m.matrix, sizeof(Land4x4Matrix))
    land_file_write(f, "AABB", 4)
    land_file_write(f, (char *)&self.aabb.x1, sizeof(double))
    land_file_write(f, (char *)&self.aabb.y1, sizeof(double))
    land_file_write(f, (char *)&self.aabb.z1, sizeof(double))
    land_file_write(f, (char *)&self.aabb.x2, sizeof(double))
    land_file_write(f, (char *)&self.aabb.y2, sizeof(double))
    land_file_write(f, (char *)&self.aabb.z2, sizeof(double))

def _read_mesh(LandMeshFile *self, LandFile *f, char* section):
    self.n = _read_int(f)
    self.stride = _read_int(f)
    int bytes_count = self.n * self.stride * sizeof *self.v
    self.v = land_malloc(bytes_count)
    if not self.v:
        return
    land_file_read(f, (char*)self.v, bytes_count)

    land_file_read(f, section, 4)
    if land_equals(section, "MARK"):
        int n = _read_int(f)
        if n:
            self.markers = land_array_new()
            for int i in range(n):
                LandObjMarker *m = land_calloc(sizeof *m)
                m.name = _read_string(f)
                land_file_read(f, (char *)&m.matrix, sizeof(Land4x4Matrix))
                land_array_add(self.markers, m)
        land_file_read(f, section, 4)

    if land_equals(section, "AABB"):
        land_file_read(f, (char *)&self.aabb.x1, sizeof(double))
        land_file_read(f, (char *)&self.aabb.y1, sizeof(double))
        land_file_read(f, (char *)&self.aabb.z1, sizeof(double))
        land_file_read(f, (char *)&self.aabb.x2, sizeof(double))
        land_file_read(f, (char *)&self.aabb.y2, sizeof(double))
        land_file_read(f, (char *)&self.aabb.z2, sizeof(double))
        land_file_read(f, section, 4)

def land_mesh_write_frames(LandFile *f, LandArray *frames) -> int:
    int wrote = 0
    int n = land_array_count(frames)
    land_file_write(f, "FRUT", 4)
    land_file_put32le(f, n)
    for int i in range(n):
        LandMeshFile *mesh = land_array_get(frames, i)
        if mesh:
            _write_mesh(mesh, f)
            wrote++
    return wrote

def land_mesh_read_frames(LandFile *f) -> LandArray*: # [Mesh*]
    LandArray* frames = None
    char section[5]
    if land_file_read(f, section, 4) != 4:
        return None
    section[4] = 0
    if not land_equals(section, "FRUT"): return None
    int n = land_file_get32le(f)
    land_file_read(f, section, 4)
    for int i in range(n):
        if not land_equals(section, "MESH"): return None
        auto mesh = land_mesh_new()
        _read_mesh(mesh, f, section)
        if not frames:
            frames = land_array_new()
        land_array_add(frames, mesh)
    return frames

def _trans(GLfloat *xyz, Land4x4Matrix* matrix):
    LandVector v = land_vector(xyz[0], xyz[1], xyz[2])
    LandVector v_ = land_vector_matmul(v, matrix)
    xyz[0] = v_.x
    xyz[1] = v_.y
    xyz[2] = v_.z

def land_mesh_transform_positions(LandMeshFile *self, Land4x4Matrix *matrix):
    """Transform positions (not normals)."""
    int s = self.stride
    for int i in range(0, self.n):
        _trans(self.v + s * i, matrix)

def land_mesh_transform_normals(LandMeshFile *self, Land4x4Matrix *matrix):
    """Transform normals."""
    int s = self.stride
    for int i in range(0, self.n):
        _trans(self.v + s * i + 3, matrix)

def land_mesh_transform(LandMeshFile *self, Land4x4Matrix *matrix):
    """
    Transform mesh vertex positions with the matrix, and mesh
    normals with the orientation part of the matrix only.
    """
    land_mesh_transform_positions(self, matrix)
    Land4x4Matrix matrix2 = *matrix
    land_4x4_matrix_set_position(&matrix2, land_vector(0, 0, 0))
    land_mesh_transform_normals(self, &matrix2)

def land_mesh_triangles(LandMeshFile *self) -> LandArray*:
    LandArray *a = land_array_new()
    LandTriangles *t = land_triangles_new_with_normals()
    print("reading vertex data %d (stride %d)", self.n, self.stride)
    for int i in range(self.n):
        float *v = self.v + i * self.stride
        float x = v[0]
        float y = v[1]
        float z = v[2]
        float nx = v[3]
        float ny = v[4]
        float nz = v[5]
        float tu = 0
        float tv = 0
        float cr = v[6]
        float cg = v[7]
        float cb = v[8]
        float ca = v[9]
        land_add_vertex(t, x, y, z, tu, tv, cr, cg, cb, ca)
        land_set_vertex_normal(t, nx, ny, nz)
    land_array_add(a, t)
    return a
