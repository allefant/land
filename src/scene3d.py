import land.util3d
import land.hash
import land.camera
import land.triangles
import land.obj.obj
import land.file
import land.obj.mesh

"""
This is meant to be a very simple, very unoptimized, 3D engine. It's
just a list of 3d objects which are all always drawn. Not useful in an
actual game, but the idea is to allow rapid prototyping by just placing
stuff and not having to think about it much.
"""

class LandScene3d:
    char *name

    LandArray *objects # [Object3d]
    LandHash *filenames # str->Triangles
    LandCamera *camera
    LandVector light
    Land4x4Matrix projection

    int stats_triangles
    bool draw_more
    char* vertex_shader
    char* fragment_shader

    LandFloat depth
    LandFloat zrange
    LandFloat fov_ro
    LandFloat view_size

    LandColor sky
    LandColor land

    bool draw_horizon
    LandObject3d *last_added

class LandModel3d:
    char *name
    LandArray *frames # [LandArray][LandTriangles]

class LandObject3d:
    Land4x4Matrix matrix
    LandModel3d *model
    int frame
    bool auto_animate

def land_scene3d_new(str name) -> LandScene3d*:
    LandScene3d *self; land_alloc(self)
    self.objects = land_array_new()
    self.filenames = land_hash_new()
    self.depth = 1
    self.zrange = 3000
    self.view_size = 1
    self.name = land_strdup(name)
    char *vert = land_format("%s.vert", name)
    if not land_data_file_exists(vert):
        land_exception("Cannot find %s", vert)
        return None
    char *frag = land_format("%s.frag", name)
    self.vertex_shader = land_read_text(vert)
    self.fragment_shader = land_read_text(frag)
    land_free(vert)
    land_free(frag)

    self.camera = land_camera_new()
    self.camera.z_is_up = True
    land_camera_translate(self.camera, land_vector(0, -60, 30))
    land_camera_change_freely(self.camera, -pi * 0.4, 0, 0)

    self.sky = land_color_name("skyblue")
    self.land = land_color_name("khaki")

    self.draw_horizon = True
    return self

def land_scene3d_add_object_from_filename(LandScene3d *self, str filename) -> LandObject3d*:
    LandModel3d *m = land_hash_get(self.filenames, filename)
    if not m:
        land_alloc(m)
        m.name = land_strdup(filename)
        char *name = land_strdup("")
        land_overwrite(&name, "%s_2.mesh", filename)
        if land_data_file_exists(name):
            auto frames = _read_mesh_frames(name)
            if not frames:
                return None
            m.frames = frames
        else:
            auto frames = _read_obj_frames(filename)
            if not frames:
                return None
            m.frames = frames
        print("have triangles")
        int frame = 1
        for LandArray *tris in LandArray *m.frames:
            int part = 1
            for LandTriangles* t in LandArray* tris:
                land_triangles_shader(t, "scene", self.vertex_shader,
                    self.fragment_shader)
                printf("%s (frame %d, part %d) vertices: %lu\n", filename, frame, part, t.n)
                part += 1
            frame += 1
        land_free(name)

    land_hash_insert(self.filenames, filename, m)

    LandObject3d *ob = land_object3d_new(m)
    land_array_add(self.objects, ob)
    self.last_added = ob
    ob.auto_animate = True
    return ob

def _read_mesh_frames(str filename) -> LandArray*:
    print("loading mesh %s", filename)
    LandFile *f = land_file_new(filename, "r")
    LandArray * meshframes = land_mesh_read_frames(f)
    if not meshframes:
        land_exception("Could not read %s", filename)
        return None
    print("%d frames", land_array_count(meshframes))
    LandArray *frames = land_array_new()
    for LandMeshFile *f in meshframes:
        LandArray *tris = land_mesh_triangles(f)
        land_array_add(frames, tris)
    return frames

def _read_obj_frames(str filename) -> LandArray*:
    LandArray *frames = land_array_new()
    int frame = 1
    char *name = land_strdup("")
    while True:
        land_overwrite(&name, "%s_%04d.obj", filename, frame)
        if not land_data_file_exists(name):
            if frame == 1:
                land_overwrite(&name, "%s.obj", filename)
                if not land_data_file_exists(name):
                    land_overwrite(&name, "%s", filename)
        LandObjFile *of = land_objfile_new_from_filename(name)
        if of.error:
            break

        # TODO: maybe only change orientation if some flag is set
        Land4x4Matrix matrix = land_4x4_matrix_rotate(1, 0, 0, pi / 2)
        land_obj_transform(of, &matrix, True)
        LandArray *tris = land_obj_triangles(of)
        land_array_add(frames, tris)

        frame += 1

    land_free(name)

    if frame == 1:
        land_exception("Could not load %s\n", filename)
        return None
    return frames

def land_scene3d_place_last(LandScene3d *self, float x, y, z, scale, angle):
    LandObject3d *ob = self.last_added
    ob.matrix = land_4x4_matrix_translate(x, y, z)
    ob.matrix = land_4x4_matrix_mul(ob.matrix, land_4x4_matrix_scale(scale, scale, scale))
    ob.matrix = land_4x4_matrix_mul(ob.matrix, land_4x4_matrix_rotate(0, 0, 1, angle))

def land_object3d_new(LandModel3d *t) -> LandObject3d*:
    LandObject3d *self; land_alloc(self)
    self.model = t
    self.matrix = land_4x4_matrix_identity()
    return self

def land_scene3d_render(LandScene3d *self):
    self.stats_triangles = 0
    self.draw_more = False

    LandFloat scale = land_camera_get_scale(self.camera)

    self.light = land_vector_normalize(land_vector(1, 0, 1))

    land_triangles_set_light_direction(self.light)

    land_color_set(self.sky)
    land_clear_color()
    land_render_state(LAND_DEPTH_TEST, True)
    land_clear_depth(1)
    LandFloat ratio = 1.0 * land_display_width() / land_display_height()
    LandFloat depth = self.depth * scale
    LandFloat s = self.view_size
    self.fov_ro = atan2(s, depth) * 2
    LandFloat zrange = self.zrange
    Land4x4Matrix pm = land_4x4_matrix_perspective(-s, -s / ratio, depth, s, s / ratio, depth + zrange)
    pm = land_4x4_matrix_mul(pm, land_camera_matrix(self.camera))
    land_projection(pm)

    if self.draw_horizon:
        land_color_set(self.land)
        land_filled_rectangle(-10000, -10000, 10000, 10000)

    for LandObject3d *ob in LandArray *self.objects:
        land_scene3d_render_object(self, ob)

def land_scene3d_render_object(LandScene3d *self, LandObject3d* ob):
    if not ob: return
    Land4x4Matrix tm = ob.matrix
    land_display_transform_4x4(&tm)
    land_color(1, 1, 1, 1)

    #LandVector pos = land_4x4_matrix_get_position(&tm)
    #LandVector rel = land_vector_sub(pos, self.camera_position)
    #LandFloat dot = land_vector_dot(rel, cam.z)
    #if dot > 0: return

    if ob.auto_animate:
        int n = land_array_count(ob.model.frames)
        ob.frame = land_get_ticks() // 4
        if n == 5:
            ob.frame %= 8
            if ob.frame >= 5: ob.frame = 8 - ob.frame
        else:
            ob.frame %= n

    LandArray *tris = land_array_get(ob.model.frames, ob.frame)
    for LandTriangles *t in tris:
        land_triangles_draw_more(t, self.draw_more)
        self.stats_triangles += t.n // 3
        self.draw_more = True

def land_scene3d_reset:
    land_render_state(LAND_DEPTH_TEST, False)
    land_reset_projection()
    land_reset_transform()
    land_display_set_default_shaders()
