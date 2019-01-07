import land.triangles
static import global allegro5.allegro5
static import global allegro5.allegro_primitives
static import land.allegro5.a5_display

class LandVertexWithNormal:
    float x, y, z
    float nx, ny, nz
    float r, g, b, a
    float i

class LandVertexAllegro:
    float x, y, z
    float u, v
    float r, g, b, a

static class LandTrianglesPlatform:
    ALLEGRO_VERTEX_DECL *decl
    ALLEGRO_VERTEX_BUFFER *vb

def platform_update_vertex_with_normals(LandTriangles *t, int i, float x, y, z, tu, tv, r, g, b, a):
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

def platform_update_vertex_allegro(LandTriangles *t, int i, float x, y, z, tu, tv, r, g, b, a):
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

def platform_update_vertex(LandTriangles *t, int i, float x, y, z, tu, tv, r, g, b, a):
    if t.has_normals:
        platform_update_vertex_with_normals(t, i, x, y, z, tu, tv, r, g, b, a)
    else:
        platform_update_vertex_allegro(t, i, x, y, z, tu, tv, r, g, b, a)

def platform_set_vertex_normal(LandTriangles *t, float x, y, z):
    if t.has_normals:
        LandVertexWithNormal* v = land_triangles_get_vertex(t, t.n - 1)
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

    if self.has_normals:
        ALLEGRO_VERTEX_ELEMENT elem[] = {
            {ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0},
            {ALLEGRO_PRIM_USER_ATTR + 0, ALLEGRO_PRIM_FLOAT_3, 12},
            {ALLEGRO_PRIM_COLOR_ATTR, 0, 24},
            {ALLEGRO_PRIM_USER_ATTR + 1, ALLEGRO_PRIM_FLOAT_1, 40},
            {0, 0, 0}
        }
        self.size = 44
        platform.decl = al_create_vertex_decl(elem, self.size)
    else:
        ALLEGRO_VERTEX_ELEMENT elem[] = {
            {ALLEGRO_PRIM_POSITION, ALLEGRO_PRIM_FLOAT_3, 0},
            {ALLEGRO_PRIM_TEX_COORD_PIXEL, ALLEGRO_PRIM_FLOAT_2, 12},
            {ALLEGRO_PRIM_COLOR_ATTR, 0, 20},
            {0, 0, 0}
        }
        self.size = 36
        platform.decl = al_create_vertex_decl(elem, self.size)

def platform_triangles_deinit(LandTriangles *self):
    LandTrianglesPlatform* platform = self.platform
    al_destroy_vertex_decl(platform.decl)
    if platform.vb:
        al_destroy_vertex_buffer(platform.vb)
    land_free(platform)

def platform_triangles_draw(LandTriangles *t):
    LandTrianglesPlatform* platform = t.platform
    if not platform.vb:
        platform.vb = al_create_vertex_buffer(platform.decl,
            t.buf->buffer, t.n, 0)
    LandImagePlatform *pim = (void *)t.image;
    platform_check_blending_and_transform()
    if platform.vb:
        al_draw_vertex_buffer(platform.vb, pim ? pim.a5 : None,
            0, t.n, ALLEGRO_PRIM_TRIANGLE_LIST)
    else:
        al_draw_prim(t.buf->buffer, platform.decl, pim ? pim.a5 : None,
        0, t.n, ALLEGRO_PRIM_TRIANGLE_LIST)
    platform_uncheck_blending()
