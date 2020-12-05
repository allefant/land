import land.land
import land.obj.obj
import land.glsl
import land.util2d
import land.util3d

class Kind:
    int kid
    LandArray *frames
    Kind *hd

class Object:
    Land4x4Matrix matrix
    Kind* kind

class Cell:
    LandArray* objects
    int x, y
    int tag

class SpatialHash:
    LandArray* cells # [Cell]
    float cell_size
    float min_pos
    int size

class Render:
    LandCamera *cam
    LandArray *cellstack
    int tag
    SpatialHash* spatial_hash
    LandVector light, campos
    Land4x4Matrix projection
    char* vertex_shader
    char* fragment_shader
    int stats_triangles
    bool more

Render render

LandArray *kinds
LandHash *kinds_by_name
LandArray *dynamic

def spatial_hash_new -> SpatialHash*:
    SpatialHash* h; land_alloc(h)
    h.cell_size = 500
    h.min_pos = -15000
    h.size = 60
    h.cells = land_array_new()
    for int y in range(h.size):
        for int x in range(h.size):
            Cell* cell; land_alloc(cell)
            cell.x = x
            cell.y = y
            cell.objects = land_array_new()
            land_array_add(h.cells, cell)
    return h

def hash_get_cell(SpatialHash* h, float x, y) -> Cell*:
    int cx = (x - h.min_pos) // h.cell_size
    int cy = (y - h.min_pos) // h.cell_size
    if cx < 0: cx = 0
    if cx > h.size - 1: cx = h.size - 1
    if cy < 0: cy = 0
    if cy > h.size - 1: cy = h.size - 1
    return land_array_get(h.cells, cx + cy * h.size)

def hash_static_object(SpatialHash* h, Object* o):
    LandVector v = land_4x4_matrix_get_position(&o.matrix)
    auto in_cell = hash_get_cell(h, v.x, v.y)
    land_array_add(in_cell.objects, o)

def add_kind(str name, str pattern) -> Kind*:
    Kind* k
    land_alloc(k)
    k.kid = land_array_count(kinds) + 1
    land_array_add(kinds, k)
    land_hash_insert(kinds_by_name, name, k)
    k.frames = land_array_new()

    bool star = land_contains(pattern, "*")

    int frame = 1
    while True:
        char *name = land_strdup(pattern)
        if star:
            char sframe[10]
            sprintf(sframe, "%04d", frame++)
            land_replace(&name, 0, "*", sframe)

        LandObjFile *of = land_objfile_new_from_filename(name)
        if of.error:
            land_free(name)
            break
        Land4x4Matrix matrix = land_4x4_matrix_rotate(1, 0, 0, pi / 2)
        land_obj_transform(of, &matrix, True)
        LandArray *tris = land_obj_triangles(of)
        
        for LandTriangles* t in LandArray* tris:
            land_triangles_shader(t, "elephant", render.vertex_shader,
                render.fragment_shader)
            printf("%s vertices: %d\n", name, t.n)

        land_array_add(k.frames, tris)

        land_free(name)

        if not star:
            break
   
    return k

def add_kind_hd(str name):
    char *path = land_strdup("flowers/")
    land_append(&path, "%s_*.obj", name)
    auto k = add_kind(name, path)
    land_free(path)

    path = land_strdup("flowers/hd/")
    land_append(&path, "%s_*.obj", name)
    auto khd = add_kind(name, path)
    land_free(path)

    k.hd = khd

def add_object(float x, y, z, scale, str kind)
    Object* o; land_alloc(o)
    Kind* k = land_hash_get(kinds_by_name, kind)
    o.matrix = land_4x4_matrix_translate(x, y, z)
    o.matrix = land_4x4_matrix_mul(o.matrix, land_4x4_matrix_scale(scale, scale, scale))
    o.kind = k
    if land_equals(kind, "elephant"):
        land_array_add(dynamic, o)
    else:
        hash_static_object(render.spatial_hash, o)

def game_init(LandRunner* _):
    kinds = land_array_new()
    land_array_add(kinds, None)
    dynamic = land_array_new()
    land_array_add(dynamic, None)
    kinds_by_name = land_hash_new()

    land_find_data_prefix("data/")

    render.vertex_shader = land_read_text("elephant.vert")
    render.fragment_shader = land_read_text("elephant.frag")

    add_kind("elephant", "elephant.obj")
    add_kind_hd("hepatica")
    add_kind_hd("primrose")
    add_kind_hd("bluebells")

    render.spatial_hash = spatial_hash_new()
    render.cellstack = land_array_new()

    str flowers[] = {"hepatica", "primrose", "bluebells"}

    add_object(0, 0, 0, 0.5, "elephant")
    for int v in range(250):
        for int u in range(250):
            float x = u * 100 - 12500
            float y = v * 100 - 12500
            float z = 0
            int r = land_rand(0, 2)
            x += land_rnd(0, 100)
            y += land_rnd(0, 100)
            add_object(x, y, z, 30, flowers[r])

    render.cam = land_camera_new()
    land_camera_translate(render.cam, land_vector(0, 0, 100))
    land_camera_change_freely(render.cam, -pi * 0.4, 0, 0)

def draw_object(Object* ob):
    if not ob: return
    Land4x4Matrix tm = ob.matrix
    land_display_transform_4x4(&tm)
    land_color(1, 1, 1, 1)
    Kind* k = ob.kind

    LandVector pos = land_4x4_matrix_get_position(&tm)
    LandVector rel = land_vector_sub(pos, render.campos)
    LandFloat dot = land_vector_dot(rel, render.cam->z)
    if dot > 0: return

    float dx = rel.x
    float dy = rel.y
    if dx * dx + dy * dy < 300 * 300:
        if k.hd:
            k = k.hd
    
    int n = land_array_count(k.frames)
    int t = 0
    if n == 5:
        t = (land_get_ticks() // 4) % 8
        if t >= 5:
            t = t - 5 # 0, 1, 2
            t = 3 - t
        
    LandArray*f = land_array_get(k.frames, t)
    for LandTriangles* t in f:
        land_triangles_draw_more(t, render.more)
        render.stats_triangles += t.n // 3
        render.more = True

def draw_cell(SpatialHash* h, Cell *cell) -> bool:
    if cell.tag == render.tag: return False
    cell.tag = render.tag
    LandFloat cs = h.cell_size
    LandFloat vx = cell.x * cs + h.min_pos
    LandFloat vy = cell.y * cs + h.min_pos
    LandVector p1 = land_vector_project(land_vector(vx, vy, 0), &render.projection)
    LandVector p2 = land_vector_project(land_vector(vx + cs, vy, 0), &render.projection)
    LandVector p3 = land_vector_project(land_vector(vx + cs, vy + cs, 0), &render.projection)
    LandVector p4 = land_vector_project(land_vector(vx, vy + cs, 0), &render.projection)
    bool out1 = p1.x < -1 or p1.x > 1 or p1.z < -1 or p1.z > 1
    bool out2 = p2.x < -1 or p2.x > 1 or p2.z < -1 or p2.z > 1
    bool out3 = p3.x < -1 or p3.x > 1 or p3.z < -1 or p3.z > 1
    bool out4 = p4.x < -1 or p4.x > 1 or p4.z < -1 or p4.z > 1
    if out1 and out2 and out3 and out4: return False
    for Object* ob in LandArray* cell.objects:
        draw_object(ob)
    return True

def draw_cells(SpatialHash* h):
    render.tag++
    land_array_clear(render.cellstack)
    LandCamera* cam = render.cam
    auto f = hash_get_cell(h, cam.p.x, cam.p.y)
    land_array_add(render.cellstack, f)
    while not land_array_is_empty(render.cellstack):
        Cell* cell = land_array_pop(render.cellstack)
        if draw_cell(render.spatial_hash, cell):
            if cell.x > 0:
                land_array_add(render.cellstack,
                    land_array_get(h.cells, cell.x - 1 + cell.y * h.size))
            if cell.y > 0:
                land_array_add(render.cellstack,
                    land_array_get(h.cells, cell.x + (cell.y - 1) * h.size))
            if cell.x < h.size - 1:
                land_array_add(render.cellstack,
                    land_array_get(h.cells, cell.x + 1 + cell.y * h.size))
            if cell.y < h.size - 1:
                land_array_add(render.cellstack,
                    land_array_get(h.cells, cell.x + (cell.y + 1) * h.size))

def game_draw(LandRunner* _):
    render.stats_triangles = 0

    land_render_state(LAND_DEPTH_TEST, True)
    land_clear_depth(1)
    land_clear(0.7, .8, .9, 1)

    LandFloat scale = land_camera_get_scale(render.cam)
    LandFloat ratio = 1.0 * land_display_width() / land_display_height()
    LandFloat depth = 100 * scale
    LandFloat zrange = 3000
    Land4x4Matrix pm = land_4x4_matrix_perspective(-100, -100 / ratio, depth, 100, 100 / ratio, depth + zrange)
    pm = land_4x4_matrix_mul(pm, land_4x4_matrix_translate(0, 0, -600 * scale))
    pm = land_4x4_matrix_mul(pm, land_camera_matrix(render.cam))
    land_projection(pm)
    render.projection = pm

    land_color(.5, .8, .1, 1)
    land_filled_rectangle(-10000, -10000, 10000, 10000)

    land_color(.7, 1, .3, 1)
    land_push_transform()
    LandCamera* cam = render.cam
    Land4x4Matrix tm = land_4x4_matrix_translate(cam.p.x, cam.p.y, 1)
    land_display_transform_4x4(&tm)
    land_thickness(20)
    for int i in range(0, 6, 2):
        land_line(cam.x.x * 100 * i, cam.x.y * 100 * i, cam.x.x * 100 * (i + 1), cam.x.y * 100 * (i + 1))
        land_line(cam.z.x * 100 * i, cam.z.y * 100 * i, cam.z.x * 100 * (i + 1), cam.z.y * 100 * (i + 1))
    land_pop_transform()

    land_color(1, 0, .3, 1)
    land_push_transform()
    tm = land_4x4_matrix_rotate(1, 0, 0, pi / 2)
    land_display_transform_4x4(&tm)
    land_thickness(10)
    land_line(0, 0, 0, 100)
    land_pop_transform()
    
    render.light = land_vector_normalize(land_vector(1, 0, 1))
    render.campos = land_vector_add(cam.p, land_vector_mul(cam.z, 500 * scale))

    land_triangles_set_light_direction(render.light)

    render.more = False
    draw_cells(render.spatial_hash)

    for Object* ob in dynamic:
        draw_object(ob)

    land_reset_projection()
    land_reset_transform()
    land_display_set_default_shaders()
    land_color_name("yellow")
    land_text_pos(0, 0)

    land_print("pitch %.0f", land_camera_get_pitch(cam) * 180 / pi)
    land_print("yaw %.0f", land_camera_get_yaw(cam) * 180 / pi)

    land_print("triangles: %dk", render.stats_triangles // 1000)

def game_tick(LandRunner* _):
    if land_key_pressed(LandKeyEscape): land_quit()

    if land_mouse_button(0):
        float rotx = land_mouse_delta_y() * LandPi / 180
        float roty = land_mouse_delta_x() * LandPi / 180

        land_camera_change_locked_constrained(render.cam, rotx, roty, -pi * 0.53, pi * 0.05)

    float kx = 0, ky = 0
    if land_key(LandKeyLeft): kx = -1
    if land_key(LandKeyRight): kx = 1
    if land_key(LandKeyUp): ky = -1
    if land_key(LandKeyDown): ky = 1

    Object* ele = land_array_get(dynamic, 1)
    if kx:
        ele.matrix = land_4x4_matrix_mul(ele.matrix,
            land_4x4_matrix_rotate(0, 0, 1, 0.01 * -kx))
    if ky:
        LandVector backward = land_4x4_matrix_get_up(&ele.matrix)
        backward = land_vector_mul(backward, ky * 4)
        ele.matrix = land_4x4_matrix_mul(land_4x4_matrix_translate(backward.x, backward.y, backward.z), ele.matrix)
        land_camera_translate(render.cam, backward)

    render.cam->zoom += land_mouse_delta_z() * 0.01

def begin():
    land_init()
    land_set_display_parameters(2048, 1024, LAND_WINDOWED | LAND_RESIZE | LAND_OPENGL | LAND_DEPTH)
    LandRunner *game_runner = land_runner_new("game",
        game_init, NULL, game_tick, game_draw, NULL, NULL)
    land_runner_register(game_runner)
    land_set_initial_runner(game_runner)
    land_mainloop()

land_use_main(begin)

