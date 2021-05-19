import land.land
import global ctype

class LandObjMaterial:
    char *name
    float r, g, b, a
    LandImage *texture

class LandObjVertex:
    int xyz, normal, uv

class LandObjObject:
    char *name
    bool smooth
    int tv_count
    LandObjVertex *triangle_vertices
    LandObjMaterial *mat

class LandObjMarker:
    char *name
    Land4x4Matrix matrix

class LandObjFile:
    char *filename

    int vn
    GLfloat *xyz

    int normal_count
    GLfloat *normal

    int uv_count
    GLfloat *uv

    LandArray *objects # LandObjObject
    LandObjObject *obj

    LandHash *materials # LandObjMaterial
    LandObjMaterial *mat

    LandArray *markers # LandObjMarker

    bool error

def _add_m(LandObjFile *self, char const *name):
    if not self.materials:
        self.materials = land_hash_new()

    LandObjMaterial *mat; land_alloc(mat)
    mat.name = land_strdup(name)
    land_hash_insert(self.materials, name, mat)
    self.mat = mat
    mat.a = 1
    #printf("material %s\n", name)

def _add_v(LandObjFile *self, float x, y, z):
    int i = self.vn
    self.vn++
    self.xyz = land_realloc(self.xyz, self.vn * sizeof(float) * 3)
    self.xyz[i * 3 + 0] = x
    self.xyz[i * 3 + 1] = y
    self.xyz[i * 3 + 2] = z

def _add_vn(LandObjFile *self, float x, y, z):
    int i = self.normal_count
    self.normal_count++
    self.normal = land_realloc(self.normal, self.normal_count * sizeof(float) * 3)
    self.normal[i * 3 + 0] = x
    self.normal[i * 3 + 1] = y
    self.normal[i * 3 + 2] = z

def _add_vt(LandObjFile *self, float x, y):
    int i = self.uv_count
    self.uv_count++
    self.uv = land_realloc(self.uv, self.uv_count * sizeof(float) * 2)
    self.uv[i * 2 + 0] = x
    self.uv[i * 2 + 1] = y

def _add_f(LandObjFile *self, LandObjVertex v):
    if v.xyz < 0: v.xyz += self.vn
    if v.uv < 0: v.uv += self.uv_count
    if v.normal < 0: v.normal += self.normal_count
    LandObjObject *o = self.obj
    int i = o.tv_count
    o.tv_count++
    o.triangle_vertices = land_realloc(o.triangle_vertices,
        o.tv_count * sizeof(*o.triangle_vertices))
    o.triangle_vertices[i] = v

def _add_o(LandObjFile *self, char const *name):
    LandObjObject *o = self.obj
    if self.objects == None:
        self.objects = land_array_new()
    if not self.obj or self.obj.tv_count > 1:
        land_alloc(o)
        o.mat = land_hash_get(self.materials, "")
        land_array_add(self.objects, o)
        self.obj = o
    if not o.name and name:
        o.name = land_strdup(name)
        #print("object %s", name)

def _read_vertex(LandObjFile *self, str row):
    # example: f -5814/-3659/-3696 -2205/-536/-606 -2218/-3661/-3698
    # example: f 8208 8207 8270 9812
    # example: f 1//1 2//2 3//3

    str s = row + 2
    char *ep
    for int i in range(4):
        LandObjVertex v = {0, 0, 0}
        for int j in range(3):
            int value = strtol(s, &ep, 0)
            if j == 0: v.xyz = value
            if j == 1: v.uv = value
            if j == 2: v.normal = value
            if *ep != '/':
                break
            s = ep + 1

        if i == 3: # quad instead of triangle, duplicate other two
            LandObjObject* o = self.obj
            LandObjVertex v0 = o.triangle_vertices[o.tv_count - 3]
            LandObjVertex v1 = o.triangle_vertices[o.tv_count - 1]
            _add_f(self, v0)
            _add_f(self, v1)
        _add_f(self, v)

        while *ep == ' ':
            ep++
        if *ep == 0:
            break
        s = ep

def _read_marker(LandObjFile *self, char *row):
    float_t px, py, pz, rx, ry, rz, ux, uy, uz, bx, by, bz
    char name[100]
    sscanf(row, "m %s %f %f %f %f %f %f %f %f %f %f %f %f",
        name, &px, &py, &pz, &rx, &ry, &rz, &ux, &uy, &uz, &bx, &by, &bz)
    LandObjMarker *m; land_alloc(m)
    m.name = land_strdup(name)
    LandVector p = land_vector(px, py, pz)
    LandVector r = land_vector(rx, ry, rz)
    LandVector u = land_vector(bx, by, bz)
    LandVector b = land_vector(-ux, -uy, -uz)
    m.matrix = land_4x4_matrix_from_vectors(&p, &r, &u, &b)
    land_array_add(self.markers, m)

def _handle_row(LandObjFile *self, char *row):
    char name[1024]
    if row[0] == '#': return
    if land_starts_with(row, "mtllib "):
        sscanf(row, "mtllib %1023s", name)
        _read_mtl(self, name)
    if land_starts_with(row, "v "):
        float_t x, y, z
        sscanf(row, "v %f %f %f", &x, &y, &z)
        _add_v(self, x, y, z)
    if land_starts_with(row, "vn "):
        float_t x, y, z
        sscanf(row, "vn %f %f %f", &x, &y, &z)
        _add_vn(self, x, y, z)
    if land_starts_with(row, "vt "):
        float_t x, y, z
        sscanf(row, "vt %f %f %f", &x, &y, &z)
        # if z does not exist x and y still get read
        _add_vt(self, x, y)
    if land_starts_with(row, "g "):
        sscanf(row, "g %1023s", name)
        _add_o(self, name)
    if land_starts_with(row, "f "):
        _read_vertex(self, row)

    if land_starts_with(row, "usemtl "):
        sscanf(row, "usemtl %1023s", name)
        LandObjMaterial *m = land_hash_get(self.materials, name)
        _add_o(self, None)
        self.obj.mat = m
        if not self.obj.name:
            self.obj.name = land_strdup(name)

    if land_starts_with(row, "m "):
        _read_marker(self, row)

def _handle_mtl_row(LandObjFile *self, char *row):
    char name[1024]
    if row[0] == '#': return
    land_strip(&row)
    if land_starts_with(row, "newmtl "):
        sscanf(row, "newmtl %1023s", name)
        _add_m(self, name)

    if land_starts_with(row, "Kd "):
        float_t r, g, b
        sscanf(row, "Kd %f %f %f", &r, &g, &b)

        # if the .obj was generated by Blender, all colors are written
        # out in linear color space and we have to convert back to
        # sRGB (this is just an approximation for now)
        self.mat.r = pow(r / 0.8, 1 / 2.2)
        self.mat.g = pow(g / 0.8, 1 / 2.2)
        self.mat.b = pow(b / 0.8, 1 / 2.2)

    if land_starts_with(row, "map_Kd "):
        sscanf(row, "map_Kd %1023s", name)
        char *path = land_replace_filename(self.filename, name)
        self.mat.texture = land_image_load(path)
        land_free(path)

def _read_mtl(LandObjFile *self, char const *filename):
    char *filename2 = land_replace_filename(self.filename, filename)
    LandBuffer *fb = land_buffer_read_from_file(filename2)
    LandArray *a = land_buffer_split(fb, "\n")
    for LandBuffer *b in LandArray *a:
        char *row = land_buffer_finish(b)
        _handle_mtl_row(self, row)
    land_array_destroy(a)
    land_free(filename2)

def land_objfile_new_from_filename(char const *filename) -> LandObjFile *:
    LandObjFile *self; land_alloc(self)

    self.markers = land_array_new()

    # 0 elements are reserved to mean missing
    _add_v(self, 0, 0, 0)
    _add_vn(self, 0, 0, 0)
    _add_vt(self, 0, 0)
    _add_m(self, "")
    
    self.filename = land_strdup(filename)
    LandBuffer *fb = land_buffer_read_from_file(self.filename)
    if not fb:
        land_log_message("Could not open %s\n", self.filename)
        self.error = True
        return self
    LandArray *a
    if land_ends_with(self.filename, ".b"):
        int i = 0
        int o = 1
        while i < fb.n:
            uint8_t b = land_buffer_get_byte(fb, i)
            if b == 'V':
                float x = land_buffer_get_float(fb, i + 1)
                float y = land_buffer_get_float(fb, i + 5)
                float z = land_buffer_get_float(fb, i + 9)
                i += 13
                _add_v(self, x, y, z)
            elif b == 'N':
                float x = land_buffer_get_float(fb, i + 1)
                float y = land_buffer_get_float(fb, i + 5)
                float z = land_buffer_get_float(fb, i + 9)
                i += 13
                _add_vn(self, x, y, z)
            elif b == 'T':
                float x = land_buffer_get_float(fb, i + 1)
                float y = land_buffer_get_float(fb, i + 5)
                i += 9
                _add_vt(self, x, y)
            elif b == 'F':
                int a = o
                int b = o + 1
                int c = o + 2
                o += 3
                i += 1

                LandObjVertex va, vb, vc
                va.xyz = a
                va.uv = a
                va.normal = a
                vb.xyz = b
                vb.uv = b
                vb.normal = b
                vc.xyz = c
                vc.uv = c
                vc.normal = c
                _add_f(self, va)
                _add_f(self, vb)
                _add_f(self, vc)
            else:
                int j = land_buffer_find(fb, i, "\n")
                fb.buffer[j] = 0
                _handle_row(self, fb.buffer + i)
                i = j + 1
    else:
        a = land_buffer_split(fb, "\n")
        for LandBuffer *b in LandArray *a:
            char *row = land_buffer_finish(b)
            land_strip(&row)
            _handle_row(self, row)
        land_array_destroy(a)
    #print("Vertices: %d", self.vn)
    return self

def land_obj_transform(LandObjFile *self, Land4x4Matrix *matrix,
        bool include_normals):

    for int i in range(self.vn):
        float x = self.xyz[i * 3 + 0]
        float y = self.xyz[i * 3 + 1]
        float z = self.xyz[i * 3 + 2]
        LandVector pos = land_vector(x, y, z)
        pos = land_vector_matmul(pos, matrix)
        self.xyz[i * 3 + 0] = pos.x
        self.xyz[i * 3 + 1] = pos.y
        self.xyz[i * 3 + 2] = pos.z

    if include_normals:
        for int i in range(self.normal_count):
            float nx = self.normal[i * 3 + 0]
            float ny = self.normal[i * 3 + 1]
            float nz = self.normal[i * 3 + 2]
            LandVector normal = land_vector(nx, ny, nz)
            normal = land_vector_matmul(normal, matrix)
            self.normal[i * 3 + 0] = normal.x
            self.normal[i * 3 + 1] = normal.y
            self.normal[i * 3 + 2] = normal.z
                

def land_obj_triangles(LandObjFile *self) -> LandArray*:
    LandArray *a = land_array_new()
    for LandObjObject *obj in LandArray* self.objects:
        LandTriangles *t = land_triangles_new_with_normals()
        LandObjMaterial *m = obj.mat
        land_triangles_texture(t, m.texture)
        float tw = 1, th = 1
        if m.texture:
            tw = land_image_width(m.texture)
            th = land_image_height(m.texture)
        for int i in range(obj.tv_count):
            LandObjVertex *v = obj.triangle_vertices + i
            float x = self.xyz[v.xyz * 3 + 0]
            float y = self.xyz[v.xyz * 3 + 1]
            float z = self.xyz[v.xyz * 3 + 2]
            float nx = self.normal[v.normal * 3 + 0]
            float ny = self.normal[v.normal * 3 + 1]
            float nz = self.normal[v.normal * 3 + 2]
            float tu = self.uv[v.uv * 2 + 0] * tw
            float tv = th - self.uv[v.uv * 2 + 1] * th
            land_add_vertex(t, x, y, z, tu, tv, 1, 1, 1, 1)
            land_set_vertex_normal(t, nx, ny, nz)
        land_array_add(a, t)
    return a

def land_obj_markers(LandObjFile *self) -> LandArray*:
    return self.markers
