import land.land

class Render:
    LandObject3d *elephant
    LandScene3d *scene

Render *render

def _init(LandRunner* _):
    land_alloc(render)
    land_find_data_prefix("data/")

    render.scene = land_scene3d_new("simple3d")
    land_camera_warp(render.scene.camera, 0, 0, 2)
    land_camera_look_to(render.scene.camera, 0, 100, 20)

    render.elephant = land_scene3d_add_object_from_filename(render.scene, "obj/elephant")
    land_scene3d_place_last(render.scene, 0, 10, 0, scale=1, angle=0)
    land_scene3d_add_object_from_filename(render.scene, "obj/giraffe")
    land_scene3d_place_last(render.scene, 100, 0, 0, scale=1, angle=pi * 1.5)
    land_scene3d_add_object_from_filename(render.scene, "obj/zebra")
    land_scene3d_place_last(render.scene, 0, 100, 0, scale=1, angle=0)
    land_scene3d_add_object_from_filename(render.scene, "obj/rhinocerus")
    land_scene3d_place_last(render.scene, -100, 0, 0, scale=1, angle=pi * 0.5)
    land_scene3d_add_object_from_filename(render.scene, "obj/lion_male")
    land_scene3d_place_last(render.scene, 0, -100, 0, scale=1, angle=pi)
    for int y in range(5):
        for int x in range(5):
            land_scene3d_add_object_from_filename(render.scene, "obj/spiranthes_spiralis")
            land_scene3d_place_last(render.scene, (x - 2) * 10, (y - 2) * 10, 0, scale=.33, angle=land_rnd(0, 2 * pi))
    
def _draw(LandRunner* _):
    LandScene3d *scene = render.scene
    land_scene3d_render(render.scene)
    land_scene3d_reset()

    land_color_name("yellow")
    land_text_pos(4, 4)
    land_text_background(land_color_rgba(.0, 0, 0, .5), 4)

    char *st = land_debug_camera(scene.camera)
    land_append(&st, "\nFoV %.1f°", scene.fov_ro * 180 / pi)
    land_print_multiline(st)
    land_free(st)

    land_text_pos(land_display_width(), 0)
    land_print_right("triangles: %dk", scene.stats_triangles // 1000)

    LandVector v = land_vector(100, 0, 0)

    LandFloat scale = land_camera_get_scale(scene.camera)
    LandFloat s = scene.view_size
    LandFloat ratio = 1.0 * land_display_width() / land_display_height()
    LandFloat depth = scene.depth * scale
    LandFloat zrange = scene.zrange
    Land4x4Matrix pm = land_4x4_matrix_perspective(-s, -s / ratio, depth, s, s / ratio, depth + zrange)
    pm = land_4x4_matrix_mul(pm, land_camera_matrix(scene.camera))
    v = land_vector_matmul(v, &pm)
    float dx = land_display_width() / 2 + v.x * 15
    float dy = land_display_height() / 2 - v.y / 15
    land_text_pos(dx, dy)
    land_print_middle("giraffe")

def get_xy():
    LandScene3d *scene = render.scene
    float w = land_display_width()
    float h = land_display_height()
    float mx = land_mouse_x()
    float my = land_mouse_y()
    LandCamera *c = scene.camera

    LandVector t
    t.x = mx - w / 2
    t.y = -my + h / 2
    t.z = 0

    LandFloat s = pow(2, c.zoom)
    t.x /= s
    t.y /= s
    t.z /= s

    t = land_vector_backtransform(t, c.p, c.x, c.y, c.z)

    #print("%.2f %.2f %.2f", t.x, t.y, t.z)

def _tick(LandRunner* _):
    LandScene3d *scene = render.scene
    if land_key_pressed(LandKeyEscape): land_quit()
    if land_closebutton(): land_quit()

    if land_mouse_button(0):
        float rotx = -land_mouse_delta_y() * LandPi / 180
        float roty = land_mouse_delta_x() * LandPi / 180
        land_camera_change_locked_constrained(scene.camera, rotx, roty, pi * -.33, pi * 0.55)

    get_xy()

    float kx = 0, ky = 0, kz = 0
    if land_key(LandKeyLeft): kx = -1
    if land_key(LandKeyRight): kx = 1
    if land_key(LandKeyUp): ky = -1
    if land_key(LandKeyDown): ky = 1
    if land_key(LandKeyPageUp): kz = 1
    if land_key(LandKeyPageDown): kz = -1

    if land_key(LandKeyShift):
        LandObject3d *ele = render.elephant
        if kx:
            ele.matrix = land_4x4_matrix_mul(ele.matrix,
                land_4x4_matrix_rotate(0, 0, 1, 0.02 * -kx))
        if ky:
            LandVector backward = land_4x4_matrix_get_up(&ele.matrix)
            backward = land_vector_mul(backward, ky)
            ele.matrix = land_4x4_matrix_mul(land_4x4_matrix_translate(
                backward.x, backward.y, backward.z), ele.matrix)
    else:
        float s = .33
        land_camera_move(scene.camera, -kx * s, ky * s, kz * s)

    scene.camera->zoom += land_mouse_delta_z() * 0.01

def _config():
    land_set_display_parameters(2048, 1024, LAND_WINDOWED | LAND_RESIZE | LAND_OPENGL | LAND_DEPTH)
    land_default_display()
land_example(_config, _init, _tick, _draw, None)
