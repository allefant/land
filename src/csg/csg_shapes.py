import land.csg.csg
static import land.util
static import land.mem
import csg_octree
static macro pi LAND_PI

static def sphere_point(LandArray *vertices, LandFloat i, j):
    LandFloat theta = 2 * pi * i
    LandFloat phi = pi * j
    LandVector normal = land_vector(
      cos(theta) * sin(phi),
      cos(phi),
      sin(theta) * sin(phi))
    LandVector pos = normal

    land_array_add(vertices, land_csg_vertex_new(pos, normal))

def csg_sphere(int slices, rings, void *shared) -> LandCSG *:
    """
    Make a sphere with radius 1.0.
    It fits within a cube from -1/-1/-1 to 1/1/1.

    rings determines how many parts the latitude is divided into, a
    value of 3 means just south pole, equator and north pole.

    slices determins how many parts the longitude is divided into,
    a value of 3 means 0-meridian, +120° and -120°.
    """
    if slices < 3:
        return None
    if rings < 3:
        return None
    LandArray *polygons = land_array_new()
    for int i in range(slices): # longitude
        for int j in range(rings - 1): # latitude
            # for example if slices and rings are both 3
            # j = 0:
            # A=i/j B=-
            # D=i/j+1 C=i+1/j+1
            #
            # j = 1:
            # A[D]=i/j B[C]=i+1/j
            # D=i/j+1 C=-
            #
            LandArray *vertices = land_array_new()
            sphere_point(vertices, 1.0 * i / slices, 1.0 * j /
                (rings - 1))
            if j > 0: # not southpole
                sphere_point(vertices, 1.0 * (i + 1) / slices,
                    1.0 * j / (rings - 1))
            if j < rings - 2:
                sphere_point(vertices, 1.0 * (i + 1) / slices,
                    1.0 * (j + 1) / (rings - 1))
            sphere_point(vertices, 1.0 * i / slices,
                    1.0 * (j + 1) / (rings - 1))

            land_array_add(polygons, land_csg_polygon_new(vertices, shared))
            
    return land_csg_new_from_polygons(polygons)

def _sphere_point(LandVector a, b) -> LandVector:
    LandVector half = land_vector_mul(land_vector_add(a, b), 0.5)
    return land_vector_normalize(half)

def _sphere_tri(LandArray *polygons, LandVector a, b, c,
        int divisions, void *shared):
    """
          c
          .
         / \
       /     \
     X---------X
   /   \     /   \
 /       \ /       \
.---------I---------.
a                   b
    """
    if divisions == 0:
        LandArray *vertices = land_array_new()
        land_array_add(vertices, land_csg_vertex_new(a, a))
        land_array_add(vertices, land_csg_vertex_new(b, b))
        land_array_add(vertices, land_csg_vertex_new(c, c))
        land_array_add(polygons, land_csg_polygon_new(vertices, shared))
    else:
        LandVector ab2 = _sphere_point(a, b)
        LandVector bc2 = _sphere_point(b, c)
        LandVector ca2 = _sphere_point(c, a)
        _sphere_tri(polygons, a, ab2, ca2, divisions - 1, shared)
        _sphere_tri(polygons, b, bc2, ab2, divisions - 1, shared)
        _sphere_tri(polygons, c, ca2, bc2, divisions - 1, shared)
        _sphere_tri(polygons, ab2, bc2, ca2, divisions - 1, shared)

def csg_tetrasphere(int divisions, void *shared) -> LandCSG *:
    """
    Make a sphere out of a repeatedly subdivided tetrahedron.
    """
    LandArray *polygons = land_array_new()
    LandFloat r = 1 / sqrt(1.5)
    LandFloat t = 1 / sqrt(3)

    LandVector a = land_vector(-r, 0, -t)
    LandVector b = land_vector( r, 0, -t)
    LandVector c = land_vector( 0, -r, t)
    LandVector d = land_vector( 0,  r, t)
    _sphere_tri(polygons, a, d, b, divisions, shared)
    _sphere_tri(polygons, d, c, b, divisions, shared)
    _sphere_tri(polygons, c, d, a, divisions, shared)
    _sphere_tri(polygons, c, a, b, divisions, shared)
    return land_csg_new_from_polygons(polygons)

def land_csg_icosphere(int divisions, void *shared) -> LandCSG *:
    LandArray *polygons = land_array_new()

    const LandFloat u = (1.0 + sqrt(5)) / 2.0
    const LandFloat r = sqrt(1 + u * u)
    const LandFloat icosahedron_coords[] = {
        0, 1, u, # top B 1
        0,-1, u, # top F 2
        0, 1, -u,
        0, -1, -u,
        1, u, 0, # R B 5
        -1, u, 0, # L B 6
        1, -u, 0, # R F 7
        -1, -u, 0, # L F 8
        u, 0, 1, # top R 9
        u, 0, -1,
        -u, 0, 1, # top L 11
        -u, 0, -1
        }
    const int icosahedron_triangles[] = {
        1, 11, 2,
        1, 6, 11,
        1, 5, 6,
        1, 9, 5,
        1, 2, 9, # top back
        2, 7, 9,
        2, 8, 7,
        2, 11, 8, # top front
        3, 10, 4,
        3, 5, 10,
        3, 6, 5,
        3, 12, 6,
        3, 4, 12, # bottom back
        4, 10, 7,
        4, 7, 8,
        4, 8, 12, # bottom front
        11, 12, 8,
        12, 11, 6, # left
        9, 7, 10,
        10, 5, 9 # right
        }
    for int i in range(20):
        int const *vi = icosahedron_triangles + i * 3
        LandFloat const *va = icosahedron_coords + vi[0] * 3 - 3
        LandFloat const *vb = icosahedron_coords + vi[1] * 3 - 3
        LandFloat const *vc = icosahedron_coords + vi[2] * 3 - 3
        LandVector a = land_vector(va[0] / r, va[1] / r, va[2] / r)
        LandVector b = land_vector(vb[0] / r, vb[1] / r, vb[2] / r)
        LandVector c = land_vector(vc[0] / r, vc[1] / r, vc[2] / r)
        _sphere_tri(polygons, a, b, c, divisions, shared)
    return land_csg_new_from_polygons(polygons)

def csg_cylinder(int slices, void *shared) -> LandCSG *:
    return csg_cylinder_open(slices, False, shared)

def csg_cut_cone_open(int slices, bool opened, float top_radius,
        void *shared) -> LandCSG *:
    """
    Make a cut cone along the z-axis with radius 1.0 at the botton
    and radius top_radius at the top at height 2.0.
    It fits within a cube from -1/-1/-1 to 1/1/1.
    """
    if slices < 3:
        return None

    LandVector up = land_vector(0, 0, 1)
    LandVector down = land_vector(0, 0, -1)
    
    LandArray *polygons = land_array_new()

    for int i in range(slices):
        
        LandCSGVertex *start = land_csg_vertex_new(down, down)
        LandCSGVertex *end = land_csg_vertex_new(up, up)

        LandFloat angle0 = i * 2 * pi / slices
        LandFloat angle1 = (i + 1) * 2 * pi / slices
        LandFloat c0 = cos(angle0), s0 = sin(angle0)
        LandFloat c1 = cos(angle1), s1 = sin(angle1)

        # the lower normals point straight out - so technically our
        # cone is weirdly bent towards the top
        LandVector side0 = land_vector(c0, -s0, 0)
        LandVector side1 = land_vector(c1, -s1, 0)
        LandVector v0d = land_vector(c0, -s0, -1)
        LandVector v1d = land_vector(c1, -s1, -1)
        LandVector v0u = land_vector(c0 * top_radius, -s0 * top_radius, 1)
        LandVector v1u = land_vector(c1 * top_radius, -s1 * top_radius, 1)

        LandArray *vertices

        if not opened:
            vertices = land_array_new()
            land_array_add(vertices, start)
            land_array_add(vertices, land_csg_vertex_new(v0d, down))
            land_array_add(vertices, land_csg_vertex_new(v1d, down))
            land_array_add(polygons, land_csg_polygon_new(vertices, shared))

        vertices = land_array_new()
        land_array_add(vertices, land_csg_vertex_new(v1d, side1))
        land_array_add(vertices, land_csg_vertex_new(v0d, side0))
        land_array_add(vertices, land_csg_vertex_new(v0u, side0))
        land_array_add(vertices, land_csg_vertex_new(v1u, side1))
        land_array_add(polygons, land_csg_polygon_new(vertices, shared))

        if not opened:
            vertices = land_array_new()
            land_array_add(vertices, end)
            land_array_add(vertices, land_csg_vertex_new(v1u, up))
            land_array_add(vertices, land_csg_vertex_new(v0u, up))
            land_array_add(polygons, land_csg_polygon_new(vertices, shared))

    return land_csg_new_from_polygons(polygons)

def csg_cylinder_open(int slices, bool opened, void *shared) -> LandCSG *:
    return csg_cut_cone_open(slices, opened, 1.0, shared)

def csg_cone(int slices, void *shared) -> LandCSG *:
    """
    Make a cone along the z-axis with radius 1.0 and height 2.0.
    The top of the cone is at 0/0/1.
    It fits within a cube from -1/-1/-1 to 1/1/1.
    """
    if slices < 3:
        return None

    LandVector down = land_vector(0, 0, -1)
    LandVector up = land_vector(0, 0, 1)
    
    LandArray *polygons = land_array_new()

    for int i in range(slices):
        
        LandCSGVertex *start = land_csg_vertex_new(down, down)

        LandFloat angle0 = i * 2 * pi / slices
        LandFloat angle1 = (i + 1) * 2 * pi / slices
        #Float anglem = (i + 0.5) * 2 * pi / slices
        LandFloat c0 = cos(angle0), s0 = sin(angle0)
        LandFloat c1 = cos(angle1), s1 = sin(angle1)
        #Float cm = cos(anglem), sm = sin(anglem)

        #LandVector sidem = land_vector_normalize(land_vector(cm, sm, 0.5))
        LandVector side0 = land_vector_normalize(land_vector(c0, -s0, 0.5))
        LandVector side1 = land_vector_normalize(land_vector(c1, -s1, 0.5))
        LandVector v0d = land_vector(c0, -s0, -1)
        LandVector v1d = land_vector(c1, -s1, -1)

        LandArray *vertices

        vertices = land_array_new()
        land_array_add(vertices, start)
        land_array_add(vertices, land_csg_vertex_new(v0d, down))
        land_array_add(vertices, land_csg_vertex_new(v1d, down))
        land_array_add(polygons, land_csg_polygon_new(vertices, shared))

        vertices = land_array_new()
        #land_array_add(vertices, land_csg_vertex_new(up, sidem))
        land_array_add(vertices, land_csg_vertex_new(up, up))
        land_array_add(vertices, land_csg_vertex_new(v1d, side1))
        land_array_add(vertices, land_csg_vertex_new(v0d, side0))
        land_array_add(polygons, land_csg_polygon_new(vertices, shared))

    return land_csg_new_from_polygons(polygons)

static def quad_vertices(LandVector a, b, c, d) -> LandArray*:
    LandArray *vertices = land_array_new()
    LandVector ab = land_vector_sub(b, a)
    LandVector bc = land_vector_sub(c, b)
    LandVector normal = land_vector_normalize(land_vector_cross(ab, bc))
    land_array_add(vertices, land_csg_vertex_new(a, normal))
    land_array_add(vertices, land_csg_vertex_new(b, normal))
    land_array_add(vertices, land_csg_vertex_new(c, normal))
    land_array_add(vertices, land_csg_vertex_new(d, normal))
    return vertices

static def add_quad(LandArray *polygons, LandVector a, b, c, d, void *shared):
    LandArray *vertices = quad_vertices(a, b, c, d)
    land_array_add(polygons, land_csg_polygon_new(vertices, shared))

static def triangle_vertices(LandVector a, b, c) -> LandArray*:
    LandArray *vertices = land_array_new()
    LandVector ab = land_vector_sub(b, a)
    LandVector bc = land_vector_sub(c, b)
    LandVector normal = land_vector_normalize(land_vector_cross(ab, bc))
    land_array_add(vertices, land_csg_vertex_new(a, normal))
    land_array_add(vertices, land_csg_vertex_new(b, normal))
    land_array_add(vertices, land_csg_vertex_new(c, normal))
    return vertices

static def add_tri(LandArray *polygons, LandVector a, b, c, void *shared):
    LandArray *vertices = triangle_vertices(a, b, c)
    land_array_add(polygons, land_csg_polygon_new(vertices, shared))

static def add_tri_flip(LandArray *polygons, LandVector a, b, c,
        void *shared, bool flip):
    add_tri(polygons, a, b, c, shared)
    if flip:
        land_csg_polygon_flip(land_array_get_last(polygons))

static def add_quad_flip(LandArray *polygons, LandVector a, b, c, d,
        void *shared, bool flip):
    add_quad(polygons, a, b, c, d, shared)
    if flip:
        land_csg_polygon_flip(land_array_get_last(polygons))

def csg_pyramid(void *shared) -> LandCSG *:
    """
    Make a 4-sided pyramid with a side-length of 1 and a height of 2.
    The top is at 0/0/1.
    It fits within a cube from -1/-1/-1 to 1/1/1.
    """
    LandArray *polygons = land_array_new()
    LandVector a = land_vector(-1, -1, -1)
    LandVector b = land_vector( 1, -1, -1)
    LandVector c = land_vector( 1,  1, -1)
    LandVector d = land_vector(-1,  1, -1)
    LandVector e = land_vector( 0,  0,  1)
    add_quad(polygons, a, d, c, b, shared)
    add_tri(polygons, a, b, e, shared)
    add_tri(polygons, b, c, e, shared)
    add_tri(polygons, c, d, e, shared)
    add_tri(polygons, d, a, e, shared)
    return land_csg_new_from_polygons(polygons)

def csg_cut_pyramid_open(bool opened, LandFloat top_x, top_y, void *shared) -> LandCSG *:
    """
    Make a 4-sided pyramid with a side-length of 1 at the base and a
    height of 2. The side-length at the top is top_x times top_y.
    """
    LandFloat x = top_x
    LandFloat y = top_y
    LandArray *polygons = land_array_new()
    LandVector a = land_vector(-1, -1, -1)
    LandVector b = land_vector( 1, -1, -1)
    LandVector c = land_vector( 1,  1, -1)
    LandVector d = land_vector(-1,  1, -1)
    LandVector e = land_vector(-x, -y,  1)
    LandVector f = land_vector( x, -y,  1)
    LandVector g = land_vector( x,  y,  1)
    LandVector h = land_vector(-x,  y,  1)
    if not opened: add_quad(polygons, a, d, c, b, shared) # bottom
    if not opened: add_quad(polygons, e, f, g, h, shared) # top
    add_quad(polygons, h, g, c, d, shared) # front
    add_quad(polygons, g, f, b, c, shared) # right
    add_quad(polygons, f, e, a, b, shared) # back
    add_quad(polygons, e, h, d, a, shared) # left
    return land_csg_new_from_polygons(polygons)

def csg_tetrahedron(void *shared) -> LandCSG *:
    """
    Make a tetrahedron.
    """
    LandArray *polygons = land_array_new()
    LandFloat s = 1 / sqrt(2)
    LandVector a = land_vector(-1, 0, -s)
    LandVector b = land_vector( 1, 0, -s)
    LandVector c = land_vector( 0, -1, s)
    LandVector d = land_vector( 0,  1, s)
    add_tri(polygons, a, d, b, shared)
    add_tri(polygons, d, c, b, shared)
    add_tri(polygons, c, d, a, shared)
    add_tri(polygons, c, a, b, shared)
    return land_csg_new_from_polygons(polygons)

def csg_cube(void *shared) -> LandCSG *:
    """
    Make a cube from -1/-1/-1 to 1/1/1.
    """
    return csg_trapezoid(-1, 1, shared);

def csg_block2(int x, y, z, bool outside, void *shared) -> LandCSG *:
    bool all = not outside
    LandArray *polygons = land_array_new()
    LandFloat xs = 1.0 / x
    LandFloat ys = 1.0 / y
    LandFloat zs = 1.0 / z
    for int i in range(x):
        for int j in range(y):
            for int k in range(z):
                LandFloat xp = -1 + xs + i * xs * 2
                LandFloat yp = -1 + ys + j * ys * 2
                LandFloat zp = -1 + zs + k * zs * 2

                LandVector a = land_vector(xp + xs * -1, yp + ys * -1, zp + zs * -1)
                LandVector b = land_vector(xp + xs *  1, yp + ys * -1, zp + zs * -1)
                LandVector c = land_vector(xp + xs *  1, yp + ys *  1, zp + zs * -1)
                LandVector d = land_vector(xp + xs * -1, yp + ys *  1, zp + zs * -1)
                LandVector e = land_vector(xp + xs * -1, yp + ys * -1, zp + zs *  1)
                LandVector f = land_vector(xp + xs *  1, yp + ys * -1, zp + zs *  1)
                LandVector g = land_vector(xp + xs *  1, yp + ys *  1, zp + zs *  1)
                LandVector h = land_vector(xp + xs * -1, yp + ys *  1, zp + zs *  1)

                if all or k == z - 1:
                    add_quad(polygons, e, f, g, h, shared) # top
                if all or k == 0:
                    add_quad(polygons, a, d, c, b, shared) # bottom
                if all or j == y - 1:
                    add_quad(polygons, h, g, c, d, shared) # front
                if all or i == x - 1:
                    add_quad(polygons, g, f, b, c, shared) # right
                if all or j == 0:
                    add_quad(polygons, f, e, a, b, shared) # back
                if all or i == 0;
                    add_quad(polygons, e, h, d, a, shared) # left
    return land_csg_new_from_polygons(polygons)

def csg_block(int x, y, z, bool outside, void *shared) -> LandCSG *:
    return csg_block2(x, y, z, outside, shared)

def csg_grid(int x, y, void *shared) -> LandCSG *:
    LandArray *polygons = land_array_new()
    LandFloat xs = 1.0 / x
    LandFloat ys = 1.0 / y
    for int j in range(y):
        for int i in range(x):
            LandFloat xp = -1 + xs + i * xs * 2
            LandFloat yp = -1 + ys + j * ys * 2
            LandVector e = land_vector(xp + xs * -1, yp + ys * -1, 0)
            LandVector f = land_vector(xp + xs *  1, yp + ys * -1, 0)
            LandVector g = land_vector(xp + xs *  1, yp + ys *  1, 0)
            LandVector h = land_vector(xp + xs * -1, yp + ys *  1, 0)
            add_tri(polygons, e, f, g, shared)
            add_tri(polygons, g, h, e, shared)
            
    return land_csg_new_from_polygons(polygons)

def csg_prism(int n, void *shared) -> LandCSG *:
    """
    n is the shape - 3 for triangle, 4 for square, 5 for pentagon...
    The prism extrudes along the z axis from -1 to 1.
    The first edge is at y = 1 the others are on a circle around 0/0
    with radius 1 in the x/y plane.
    """
    LandArray *polygons = land_array_new()
    LandVector a = land_vector(0, 1, 1) # top front
    LandVector b = land_vector(0, 1, -1) # top back
    LandVector a0 = a
    LandVector b0 = b
    for int i in range(1, n + 1):
        LandFloat angle = i * 2 * pi / n
        LandVector c = land_vector(sin(angle), cos(angle), +1)
        LandVector d = land_vector(sin(angle), cos(angle), -1)
        add_quad(polygons, a, c, d, b, shared)
        if i >= 2 and i < n:
            add_tri(polygons, a0, c, a, shared)
            add_tri(polygons, b0, b, d, shared)
        a = c
        b = d
    return land_csg_new_from_polygons(polygons)

def csg_trapezoid(LandFloat x1, x2, void *shared) -> LandCSG*:
    """
    This is a prism, from one shape at z=-1 to another at z=1. The shape
    is assymetrical, at y=-1 the length is 2, from x=-1 to x=1. At y=1
    it goes from x1 to x2.
    If x1=-1 and x2=1 this is identical to csg_cube.
    y
    1
     x1__.__x2
      |     \
    0 |      \
     |        \
     |____.____\
    -1    0    1 x
    """
    LandArray *polygons = land_array_new()
    LandVector a = land_vector(-1, -1, -1)
    LandVector b = land_vector( 1, -1, -1)
    LandVector c = land_vector(x2,  1, -1)
    LandVector d = land_vector(x1,  1, -1)
    LandVector e = land_vector(-1, -1,  1)
    LandVector f = land_vector( 1, -1,  1)
    LandVector g = land_vector(x2,  1,  1)
    LandVector h = land_vector(x1,  1,  1)
    add_quad(polygons, a, d, c, b, shared) # bottom
    add_quad(polygons, e, f, g, h, shared) # top
    add_quad(polygons, h, g, c, d, shared) # front
    add_quad(polygons, g, f, b, c, shared) # right
    add_quad(polygons, f, e, a, b, shared) # back
    add_quad(polygons, e, h, d, a, shared) # left
    return land_csg_new_from_polygons(polygons)

def csg_extrude_triangle(LandVector a, b, LandFloat d, void *shared) -> LandCSG*:
    """
    This extrudes a triangle with points 0/a/b along a distance of d.
    """
    LandArray *polygons = land_array_new()
    LandVector z = land_vector(0, 0, 0)
    LandVector n = land_vector_cross(a, b)
    n = land_vector_normalize(n)
    LandVector z_ = land_vector_add(z, land_vector_mul(n, d))
    LandVector a_ = land_vector_add(a, land_vector_mul(n, d))
    LandVector b_ = land_vector_add(b, land_vector_mul(n, d))
    add_tri_flip(polygons, z, a, b, shared, d > 0)
    add_tri_flip(polygons, z_, b_, a_, shared, d > 0)
    add_quad_flip(polygons, a, z, z_, a_, shared, d > 0)
    add_quad_flip(polygons, z, b, b_, z_, shared, d > 0)
    add_quad_flip(polygons, b, a, a_, b_, shared, d > 0)
    return land_csg_new_from_polygons(polygons)

def csg_irregular_tetrahedron(LandVector a, b, c, d, void *shared) -> LandCSG*:
    LandArray *polygons = land_array_new()
    add_tri(polygons, a, b, c, shared)
    add_tri(polygons, a, d, b, shared)
    add_tri(polygons, b, d, c, shared)
    add_tri(polygons, c, d, a, shared)
    return land_csg_new_from_polygons(polygons)

static def torus_point(LandArray *vertices, LandFloat i, j, r):
    LandFloat theta = 2 * pi * i
    LandFloat phi = 2 * pi * j
    LandFloat cx = cos(theta)
    LandFloat cy = sin(theta)
    LandVector pos = land_vector(cx + cx * r * cos(phi),
        cy + cy * cos(phi) * r, sin(phi) * r)
    LandVector normal = land_vector(cx * cos(phi), cy * cos(phi),
        sin(phi))
    land_array_add(vertices, land_csg_vertex_new(pos, normal))

def csg_torus(int slices, segments, LandFloat diameter,
        void *shared) -> LandCSG *:
    """
    slices is the longitude subdivisions, or how many "disks" the torus
    is cut into along its outer circle

    segments is the "latitude" subdivisions, i.e. how many segments each
    individual disk has

    diameter is the size of the tube and must be greater than 0 (thin)
    and less than 1 (thick).

    The torus has radius of 1 around the origin and lies in the
    X/Y plane. The outer radius therefore is 1 + diameter / 2.
    """
    LandArray *polygons = land_array_new()
    for int i in range(slices): # latitude
        for int j in range(segments): # "longitude"
            LandArray *vertices = land_array_new()
            torus_point(vertices, 1.0 * i / slices, 1.0 * j / segments,
                diameter / 2)
            torus_point(vertices, 1.0 * (i + 1) / slices,
                1.0 * j / segments, diameter / 2)
            torus_point(vertices, 1.0 * (i + 1) / slices,
                1.0 * (j + 1) / segments, diameter / 2)
            torus_point(vertices, 1.0 * i / slices,
                1.0 * (j + 1) / segments, diameter / 2)
            land_array_add(polygons, land_csg_polygon_new(vertices, shared))
    return land_csg_new_from_polygons(polygons)

def land_csg_polygon_recalculate_normal(LandCSGPolygon *p):
    LandCSGVertex *v0 = land_array_get(p.vertices, 0)
    LandCSGVertex *v1 = land_array_get(p.vertices, 1)
    LandCSGVertex *v2 = land_array_get(p.vertices, 2)

    LandVector a = land_vector_sub(v0.pos, v1.pos)
    LandVector b = land_vector_sub(v1.pos, v2.pos)
    LandVector n = land_vector_normalize(land_vector_cross(a, b))

    p.plane = land_csg_plane_from_points(v0.pos, v1.pos, v2.pos)

    for LandCSGVertex *v in LandArray *p.vertices:
        v.normal = n

static class CallbackData:
    void (*callback)(LandCSGPolygon *p, void *data)
    void *data
    LandVector pos
    LandFloat r

def _merge_callback_callback(LandArray *array, void *data):
    CallbackData *data2 = data

    if not array: return
    for LandCSGPolygon *p in array:
        bool touches = False
        for LandCSGVertex *v in LandArray* p.vertices:
            LandVector sub = land_vector_sub(data2.pos, v.pos)
            LandFloat d = land_vector_dot(sub, sub)
            if d <= data2.r * data2.r:
                touches = True
                break
        if touches:
            data2.callback(p, data2.data)

def _lookup_close_polygons(LandCSG *csg, LandVector pos, LandFloat r,
        void (*callback)(LandCSGPolygon *p, void *data), void *data):

    CallbackData data2 = {callback, data, pos, r}
    
    # for LandCSGPolygon *p in LandArray *csg.polygons:
        # bool touches = False
        # for LandCSGVertex *v in LandArray* p.vertices:
            # LandVector sub = land_vector_sub(pos, v.pos)
            # LandFloat d = land_vector_dot(sub, sub)
    land_octree_callback_in_cube(csg.octree,
        pos.x - r, pos.y - r, pos.z - r,
        pos.x + r, pos.y + r, pos.z + r,
        _merge_callback_callback, &data2)

static class Data:
    LandVector normal

def _merge_callback(LandCSGPolygon *p, void *v):
    Data *data = v
    data.normal.x += p.plane.normal.x
    data.normal.y += p.plane.normal.y
    data.normal.z += p.plane.normal.z

def land_csg_recalculate_smooth_normals(LandCSG* csg):
    csg.octree = land_octree_new_from_aabb(&csg.bbox, 10)
    # do the face normals which we will use as base
    for LandCSGPolygon *p in LandArray *csg.polygons:
        land_csg_polygon_recalculate_normal(p)
        LandFloat x = 0, y = 0, z = 0
        int i = 0
        for LandCSGVertex *v in LandArray *p.vertices:
            i++
            x += v.pos.x
            y += v.pos.y
            z += v.pos.z
        if i > 0:
            land_octree_insert(csg.octree, x / i, y / i, z / i, p)
        
    for LandCSGPolygon *p in LandArray *csg.polygons:
        for LandCSGVertex *v in LandArray *p.vertices:
            Data data
            data.normal.x = 0
            data.normal.y = 0
            data.normal.z = 0
            _lookup_close_polygons(csg, v.pos, 0.001, _merge_callback,
                &data)
            v.normal = land_vector_normalize(data.normal)

    land_octree_del(csg.octree)
    csg.octree = None

# land_csg_subdivide
# ideas:
# - verson which just splits each edge in half
# - version which only splits edges longer than some treshold
# - version which uses some kind of spline interpolation to split into
#   something more rounded...

def land_csg_voxelize(LandCSG* csg, double radius) -> LandCSG*:
    """
    FIXME: implement!
    The idea is to create a mesh from another mesh which is a voxelized
    version. Everything is cubes.
    """
    # .-2   .-1   .0    .1    .2
    #     -1.5              1.5
    #     ------------------
    #     |                |
    #     ------------------
    #
    int x0 = floor(csg.bbox.x1 / radius)
    int y0 = floor(csg.bbox.y1 / radius)
    int z0 = floor(csg.bbox.z1 / radius)
    int xn = ceil(csg.bbox.x2 / radius) - x0
    int yn = ceil(csg.bbox.y2 / radius) - y0
    int zn = ceil(csg.bbox.z2 / radius) - z0

    char* voxels = land_calloc(xn * yn * zn)
    for LandCSGPolygon *p in LandArray *csg.polygons:
        for LandCSGVertex *v in LandArray *p.vertices:
            int x = floor(v.pos.x / radius) - x0
            int y = floor(v.pos.y / radius) - y0
            int z = floor(v.pos.z / radius) - z0
            voxels[x + y * xn + z * xn * yn] = 1
        # FIXME: we don't need just the vertices but the entire polygon
        # idea: What if we subdivide each polygon first small enough to
        # cover each cube with at least one vertex
        # Maybe something like, as long as any edge is longer than 1,
        # subdivide.

    LandArray *polygons = land_array_new()

    LandCSG *csg2 = land_csg_new_from_polygons(polygons)
    
    land_free(voxels)

    return csg2
