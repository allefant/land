import global stdlib
import global string
import global land.land
import global land.csg.csg_test
import global land.util3d

static LandWidget *desktop
static LandWidgetTheme *theme

static LandCSG *model
static LandFloat *v
static int n
static LandFloat angle

static def init(LandRunner *self):

    if False:
        LandCSG *cubeA = csg_cube(None)
        LandCSG *cubeB = csg_cube(None)
        land_csg_transform(cubeB, land_4x4_matrix_translate(4, 0, 0))
        LandCSG *AB = land_csg_union(cubeA, cubeB)
        printf("%d polygons", AB->polygons->count)
        land_quit()
        return
    
    csg_test()

    land_font_load("../../data/galaxy.ttf", 12)

    theme = land_widget_theme_new("../../data/classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandCSG *cubeA = csg_cube("red")
    #land_csg_transform(cubeA, land_4x4_matrix_translate(1, 1, 0))
    LandCSG *cubeB = csg_cube("blue")
    land_csg_transform(cubeB, land_4x4_matrix_translate(1, -1, 1))
    model = land_csg_subtract(cubeA, cubeB)
    land_csg_triangles(model)

    n = land_array_count(model->polygons) * 3
    int i = 0
    v = land_malloc(n * 6 * sizeof *v)
    for LandCSGPolygon *t in LandArray *model->polygons:
        for int j in range(3):
            LandCSGVertex *vec = land_array_get_nth(t->vertices, j)
            LandFloat *vt = v + 6 * i
            vt[0] = vec->pos.x
            vt[1] = vec->pos.y
            vt[2] = vec->pos.z
            LandColor c = land_color_name(t->shared)
            vt[3] = c.r
            vt[4] = c.g
            vt[5] = c.b
            i++

static def tick(LandRunner *self):
    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

static def draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_clear_depth(1)

    land_render_state(LAND_DEPTH_TEST, False)
    
    land_reset_transform()
    land_widget_draw(desktop)

    #land_color(1, 0, 0, 1)
    #land_line(0, 0, 100, 0)

    land_render_state(LAND_DEPTH_TEST, True)

    angle += LAND_PI / 60

    Land4x4Matrix m = land_4x4_matrix_identity()
    m = land_4x4_matrix_mul(m, land_4x4_matrix_orthographic(-1, -1, -1000, 1, 1, 1000))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_translate(320, 240, 0))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_scale(50, 50, 50))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_rotate(1, 0, 0, LAND_PI / 4))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_rotate(0, 1, 0, angle))
    land_display_transform_4x4(&m)

    land_3d_triangles(n, v)

static def done(LandRunner *self):
    if theme:
        land_widget_theme_destroy(theme)
    if desktop:
        land_widget_unreference(desktop)
    if land_font_current():
        land_font_destroy(land_font_current())

land_begin_shortcut(640, 480, 60, LAND_WINDOWED | LAND_OPENGL | LAND_DEPTH,
    init, NULL, tick, draw, NULL, done)
