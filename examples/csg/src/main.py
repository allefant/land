import global stdlib
import global string
import global land.land
#import global land.csg.csg_test
import global land.csg.csg_shapes
import global land.util3d

static LandWidget *desktop
static LandWidgetTheme *theme

static LandFloat angle

class Triangles:
    LandFloat *v
    int n

Triangles t1, t2
static double icosahedron_coords[12][3]
static double dodecahedron_coords[20][3]
static bool coordinates_inited

static def init_coordinates:
    if coordinates_inited:
        return
    coordinates_inited = True

    double u = (1 + sqrt(5)) / 2.0
        
    double c1[][3] = {
        {0, 1, u},
        {0,-1, u},
        {0, 1, -u},
        {0, -1, -u},
        {1, u, 0},
        {-1, u, 0},
        {1, -u, 0},
        {-1, -u, 0},
        {u, 0, 1},
        {u, 0, -1},
        {-u, 0, 1},
        {-u, 0, -1},
    }

    memmove(icosahedron_coords, c1, sizeof(c1))

    double c2[][3] = {
        {-1, -1, -1},
        {-1, -1,  1},
        {-1,  1, -1},
        {-1,  1,  1},
        { 1, -1, -1},
        { 1, -1,  1},
        { 1,  1, -1},
        { 1,  1,  1},
        { 0, -1 / u, -u},
        { 0, -1 / u,  u},
        { 0,  1 / u, -u},
        { 0,  1 / u,  u},
        { -1 / u, -u, 0},
        { -1 / u,  u, 0},
        {  1 / u, -u, 0},
        {  1 / u,  u, 0},
        { -u, 0, -1 / u},
        {  u, 0, -1 / u},
        { -u, 0, 1 / u},
        {  u, 0, 1 / u},
    }

    memmove(dodecahedron_coords, c2, sizeof(c2))

def bubbles(void *material1, *material2) -> LandCSG *:
    init_coordinates()
    LandCSG *result = None
    for int i in range(12):
        double x = icosahedron_coords[i][0]
        double y = icosahedron_coords[i][1]
        double z = icosahedron_coords[i][2]
        
        LandCSG *s = csg_sphere(10, 10, material1)
        land_csg_transform(s, land_4x4_matrix_scale(0.75, 0.75, 0.75))
        land_csg_transform(s, land_4x4_matrix_translate(x, y, z))
        if not result:
            result = s
        else:
            LandCSG *n = land_csg_union(result, s)
            land_csg_destroy(result)
            land_csg_destroy(s)
            result = n

    for int i in range(20):
        double x = dodecahedron_coords[i][0]
        double y = dodecahedron_coords[i][1]
        double z = dodecahedron_coords[i][2]
        LandCSG *s = csg_sphere(10, 10, material2)
        land_csg_transform(s, land_4x4_matrix_translate(x, y, z))
        LandCSG *n = land_csg_union(result, s)
        land_csg_destroy(result)
        land_csg_destroy(s)
        result = n

    return result

#graphics.raspberry = function(t)
#    color("red")
#    push() size(0.8) make("sphere") pop()
#    size(1.0 / (math.sqrt(3) + 0.75))
#    bubbles(function()
#        size(0.75)
#        make("sphere")
#    end)
#end

static def triangles(LandCSG *model, Triangles *t):
    t.n = land_array_count(model->polygons) * 3
    int i = 0
    t.v = land_malloc(t.n * 6 * sizeof *t.v)
    LandCSGPolygon *poly
    for poly in LandArray *model.polygons:
        for int j in range(3):
            LandCSGVertex *vec = land_array_get_nth(poly.vertices, j)
            LandFloat *vt = t.v + 6 * i
            vt[0] = vec->pos.x
            vt[1] = vec->pos.y
            vt[2] = vec->pos.z
            LandColor c = land_color_name(poly.shared)
            vt[3] = c.r
            vt[4] = c.g
            vt[5] = c.b
            i++

def _init(LandRunner *self):
    land_find_data_prefix("data/")
    if False:
        LandCSG *cubeA = csg_cube(None)
        LandCSG *cubeB = csg_cube(None)
        land_csg_transform(cubeB, land_4x4_matrix_translate(4, 0, 0))
        LandCSG *AB = land_csg_union(cubeA, cubeB)
        printf("%d polygons", AB->polygons->count)
        land_csg_destroy(AB);
        land_csg_destroy(cubeA);
        land_csg_destroy(cubeB);

        land_quit()
        return
  
    land_font_load("galaxy.ttf", 12)

    theme = land_widget_theme_new("classic.cfg")
    land_widget_theme_set_default(theme)
    desktop = land_widget_panel_new(NULL, 0, 0, 640, 480)
    land_widget_reference(desktop)

    LandCSG *cubeA = csg_cube("red")
    #land_csg_transform(cubeA, land_4x4_matrix_translate(1, 1, 0))
    LandCSG *cubeB = csg_cube("blue")
    land_csg_transform(cubeB, land_4x4_matrix_translate(1, -1, 1))
    LandCSG *model = land_csg_subtract(cubeA, cubeB)
    land_csg_transform(model, land_4x4_matrix_translate(0, 2, 0))
    land_csg_triangles(model)
    triangles(model, &t1)

    LandCSG *raspberry = bubbles("yellow", "orange")
    land_csg_transform(raspberry, land_4x4_matrix_scale(0.5, 0.5, 0.5))
    land_csg_transform(raspberry, land_4x4_matrix_translate(0, -2, 0))
    land_csg_triangles(raspberry)
    triangles(raspberry, &t2)
    

def _tick(LandRunner *self):

    if land_key_pressed(LandKeyEscape) or land_closebutton():
        land_quit()

    land_widget_tick(desktop)

def _draw(LandRunner *self):
    land_clear(0, 0, 0, 1)
    land_clear_depth(1)

    land_render_state(LAND_DEPTH_TEST, False)
    glDisable(GL_CULL_FACE)
    
    land_reset_transform()
    land_widget_draw(desktop)

    #land_color(1, 0, 0, 1)
    #land_line(0, 0, 100, 0)

    land_render_state(LAND_DEPTH_TEST, True)
    glEnable(GL_CULL_FACE)

    angle += LAND_PI / 60

    Land4x4Matrix m = land_4x4_matrix_identity()
    m = land_4x4_matrix_mul(m, land_4x4_matrix_orthographic(-1, -1, -1000, 1, 1, 1000))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_translate(320, 240, 0))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_scale(50, 50, 50))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_rotate(1, 0, 0, LAND_PI / 4))
    m = land_4x4_matrix_mul(m, land_4x4_matrix_rotate(0, 1, 0, angle))
    land_display_transform_4x4(&m)

    land_3d_triangles(t1.n, t1.v)
    land_3d_triangles(t2.n, t2.v)

def _done(LandRunner *self):
    if theme:
        land_widget_theme_destroy(theme)
    if desktop:
        land_widget_unreference(desktop)
    if land_font_current():
        land_font_destroy(land_font_current())

land_standard_example()
