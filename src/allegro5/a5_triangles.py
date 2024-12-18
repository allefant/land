import land.triangles
import land.util3d
static import global allegro5.allegro5
static import global allegro5.allegro_primitives
static import land.allegro5.a5_display

class LandVertexWithNormal:
    float x, y, z
    float u, v
    float nx, ny, nz
    float r, g, b, a
    float i

class LandVertexWithNormalNoTexture:
    float x, y, z
    float nx, ny, nz
    float r, g, b, a
    float i

class LandVertexAllegro:
    float x, y, z
    float u, v
    float r, g, b, a

class LandVertexNoTexture:
    float x, y, z
    float r, g, b, a

static class LandTrianglesPlatform:
    ALLEGRO_VERTEX_DECL *decl
    ALLEGRO_VERTEX_BUFFER *vb
    LandTrianglesShader *shader
    ALLEGRO_VERTEX_ELEMENT elem[10]

static class LandTrianglesShader:
    int light_tag
    ALLEGRO_SHADER *a5

LandVector _light_direction
float _light
int _light_tag
LandHash *_shader_cache # LandTrianglesShader

def platform_update_vertex_with_normals(LandTriangles *t, uint64_t i, float x, y, z, tu, tv, r, g, b, a):
    LandVertexWithNormal *v = land_triangles_get_vertex(t, i)
    v.x = x
    v.y = y
    v.z = z
    v.u = tu
    v.v = tv
    v.r = r
    v.g = g
    v.b = b
    v.a = a

def platform_update_vertex_with_normals_no_texture(LandTriangles *t, uint64_t i, float x, y, z, r, g, b, a):
    LandVertexWithNormalNoTexture *v = land_triangles_get_vertex(t, i)
    v.x = x
    v.y = y
    v.z = z
    v.r = r
    v.g = g
    v.b = b
    v.a = a

def platform_update_vertex_allegro(LandTriangles *t, uint64_t i, float x, y, z, tu, tv, r, g, b, a):
    LandVertexAllegro *v = land_triangles_get_vertex(t, i)
    v.x = x
    v.y = y
    v.z = z
    v.u = tu
    v.v = tv
    v.r = r
    v.g = g
    v.b = b
    v.a = a

def platform_update_vertex_no_texture(LandTriangles *t, uint64_t i, float x, y, z, r, g, b, a):
    LandVertexNoTexture *v = land_triangles_get_vertex(t, i)
    v.x = x
    v.y = y
    v.z = z
    v.r = r
    v.g = g
    v.b = b
    v.a = a

def platform_update_vertex(LandTriangles *t, uint64_t i, float x, y, z, tu, tv, r, g, b, a):
    if t.has_normals and t.has_texture:
        platform_update_vertex_with_normals(t, i, x, y, z, tu, tv, r, g, b, a)
    elif t.has_normals and not t.has_texture:
        platform_update_vertex_with_normals_no_texture(t, i, x, y, z, r, g, b, a)
    elif t.has_texture:
        platform_update_vertex_allegro(t, i, x, y, z, tu, tv, r, g, b, a)
    else:
        platform_update_vertex_no_texture(t, i, x, y, z, r, g, b, a)

def platform_set_vertex_normal(LandTriangles *t, float x, y, z):
    if t.has_normals and t.has_texture:
        LandVertexWithNormal* v = land_triangles_get_vertex(t, t.n - 1)
        v.nx = x
        v.ny = y
        v.nz = z
    elif t.has_normals:
        LandVertexWithNormalNoTexture* v = land_triangles_get_vertex(t, t.n - 1)
        v.nx = x
        v.ny = y
        v.nz = z

def platform_set_vertex_index(LandTriangles *t, float i):
    if t.has_normals:
        LandVertexWithNormal* v = land_triangles_get_vertex(t, t.n - 1)
        v.i = i

def platform_triangles_init(LandTriangles *self):
    LandTrianglesPlatform *platform
    land_alloc(platform)
    self.platform = platform

    if self.has_normals and self.has_texture:
        ALLEGRO_VERTEX_ELEMENT elem[] = {
            {ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0},
            {ALLEGRO_PRIM_TEX_COORD_PIXEL, ALLEGRO_PRIM_FLOAT_2, 12},
            {ALLEGRO_PRIM_USER_ATTR + 0, ALLEGRO_PRIM_FLOAT_3, 20},
            {ALLEGRO_PRIM_COLOR_ATTR, 0, 32},
            {ALLEGRO_PRIM_USER_ATTR + 1, ALLEGRO_PRIM_FLOAT_1, 48},
            {0, 0, 0}
        }
        self.size = 52
        land_copy_bytes(platform.elem, elem, sizeof(elem))
    elif self.has_normals and not self.has_texture:
        ALLEGRO_VERTEX_ELEMENT elem[] = {
            {ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0},
            {ALLEGRO_PRIM_USER_ATTR + 0, ALLEGRO_PRIM_FLOAT_3, 12},
            {ALLEGRO_PRIM_COLOR_ATTR, 0, 24},
            {ALLEGRO_PRIM_USER_ATTR + 1, ALLEGRO_PRIM_FLOAT_1, 40},
            {0, 0, 0}
        }
        self.size = 44
        land_copy_bytes(platform.elem, elem, sizeof(elem))
    elif self.has_texture:
        ALLEGRO_VERTEX_ELEMENT elem[] = {
            {ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0},
            {ALLEGRO_PRIM_TEX_COORD_PIXEL, ALLEGRO_PRIM_FLOAT_2, 12},
            {ALLEGRO_PRIM_COLOR_ATTR, 0, 20},
            {0, 0, 0}
        }
        self.size = 36
        land_copy_bytes(platform.elem, elem, sizeof(elem))
    else:
        ALLEGRO_VERTEX_ELEMENT elem[] = {
            {ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0},
            {ALLEGRO_PRIM_COLOR_ATTR, 0, 12},
            {0, 0, 0}
        }
        self.size = 28
        land_copy_bytes(platform.elem, elem, sizeof(elem))

    if not self.cpu_only:
        platform_triangles_upload(self)

def platform_triangles_upload(LandTriangles *self):
    LandTrianglesPlatform *platform = self.platform
    platform.decl = al_create_vertex_decl(platform.elem, self.size)

def platform_triangles_deinit(LandTriangles *self):
    LandTrianglesPlatform* platform = self.platform
    al_destroy_vertex_decl(platform.decl)
    if platform.vb:
        al_destroy_vertex_buffer(platform.vb)
    land_free(platform)

def platform_triangles_prepare_draw(LandTriangles *t, bool more):
    LandTrianglesPlatform* platform = t.platform
    if t.can_cache and not platform.vb:
        platform.vb = al_create_vertex_buffer(platform.decl,
            t.buf->buffer, t.n, 0)
        if not platform.vb:
            error("Could not create vertex buffer with %d vertices!", t.n)
    LandImagePlatform *pim = (void *)t.image
    platform_check_blending_and_transform()

    if platform.shader:
        if not more:
            if not al_use_shader(platform.shader.a5):
                print("could not use shader")
        if platform.shader.light_tag != _light_tag:
            platform.shader.light_tag = _light_tag
            float f2[3] = {_light_direction.x, _light_direction.y, _light_direction.z}
            if not al_set_shader_float_vector("light_direction", 3, f2, 1):
                print("could not set light direction")
            if not al_set_shader_float("light", _light):
                print("could not set light")

        if pim:
            al_set_shader_sampler("al_tex", pim.a5, 0)

def platform_triangles_perform_draw(LandTriangles *t):
    LandTrianglesPlatform* platform = t.platform
    LandImagePlatform *pim = (void *)t.image
    if platform.vb:
        al_draw_vertex_buffer(platform.vb, pim ? pim.a5 : None,
            0, t.n, ALLEGRO_PRIM_TRIANGLE_LIST)
    else:
        al_draw_prim(t.buf->buffer, platform.decl, pim ? pim.a5 : None,
            0, t.n, ALLEGRO_PRIM_TRIANGLE_LIST)
    platform_uncheck_blending()

def platform_triangles_draw(LandTriangles *t, bool more):
    platform_triangles_prepare_draw(t, more)
    platform_triangles_perform_draw(t)

def platform_set_shader_vector(str name, int n, float *f):
    if not al_set_shader_float_vector(name, 1, f, n):
        print("could not set %s", name)


def platform_set_shader_int(str name, int i):
    if not al_set_shader_int(name, i):
        print("could not set %s", name)



def platform_triangles_get_xyz(LandTriangles* t, int i, float *x, *y, *z):
    LandVertexAllegro *v = land_triangles_get_vertex(t, i)
    *x = v.x
    *y = v.y
    *z = v.z

def platform_triangles_refresh(LandTriangles* t):
    LandTrianglesPlatform* platform = t.platform
    if platform.vb
        
        #void* data = al_lock_vertex_buffer(platform.vb, 0, t.n, ALLEGRO_LOCK_WRITEONLY)
        #al_unlock_vertex_buffer(platform.vb)

        # have to copy the data with the above so maybe better to just recreate?
        al_destroy_vertex_buffer(platform.vb)
        platform.vb = al_create_vertex_buffer(platform.decl,
            t.buf->buffer, t.n, 0)

def platform_triangles_shader(LandTriangles* self, str id, vertex, fragment):
    LandTrianglesPlatform* platform = self.platform

    if not _shader_cache:
        _shader_cache = land_hash_new()

    LandTrianglesShader* cached = land_hash_get(_shader_cache, id)
    if cached:
        platform.shader = cached
    else:
        land_alloc(cached)
        cached.a5 = al_create_shader(ALLEGRO_SHADER_GLSL)
        al_attach_shader_source(cached.a5, ALLEGRO_VERTEX_SHADER, vertex)
        al_attach_shader_source(cached.a5, ALLEGRO_PIXEL_SHADER, fragment)
        bool r = al_build_shader(cached.a5)
        if r:
            land_log_message("shader \"%s\" compiled successfully\n", id)
        else:
            land_log_message("%s\n", al_get_shader_log(cached.a5))
        land_hash_insert(_shader_cache, id, cached)
        platform.shader = cached

def platform_triangles_set_light_direction(LandVector light):
    #Land4x4Matrix m = land_get_transform()
    #m.v[3] = 0
    #m.v[7] = 0
    #m.v[11] = 0
    #_light = land_vector_matmul(light, &m)
    #_light = land_vector_normalize(_light)
    _light_direction = light
    _light_tag++

def platform_triangles_set_light(float light):
    _light = light
    _light_tag++
