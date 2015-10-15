import land.csg.csg
static import land.util

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

def csg_cylinder(int slices, void *shared) -> LandCSG *:
    return csg_cylinder_open(slices, False, shared)

def csg_cylinder_open(int slices, bool opened, void *shared) -> LandCSG *:
    """
    Make a cylinder along the z-axis with radius 1.0 and height 2.0.
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

        LandVector side0 = land_vector(c0, -s0, 0)
        LandVector side1 = land_vector(c1, -s1, 0)
        LandVector v0d = land_vector(c0, -s0, -1)
        LandVector v1d = land_vector(c1, -s1, -1)
        LandVector v0u = land_vector(c0, -s0, 1)
        LandVector v1u = land_vector(c1, -s1, 1)

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

def csg_prism(int slices, void *shared) -> LandCSG *:
    return None

static def add_quad(LandArray *polygons, LandVector a, b, c, d, void *shared):
    LandArray *vertices = land_array_new()
    LandVector ab = land_vector_sub(b, a)
    LandVector bc = land_vector_sub(c, b)
    LandVector normal = land_vector_normalize(land_vector_cross(ab, bc))
    land_array_add(vertices, land_csg_vertex_new(a, normal))
    land_array_add(vertices, land_csg_vertex_new(b, normal))
    land_array_add(vertices, land_csg_vertex_new(c, normal))
    land_array_add(vertices, land_csg_vertex_new(d, normal))
    land_array_add(polygons, land_csg_polygon_new(vertices, shared))

static def add_tri(LandArray *polygons, LandVector a, b, c, void *shared):
    LandArray *vertices = land_array_new()
    LandVector ab = land_vector_sub(b, a)
    LandVector bc = land_vector_sub(c, b)
    LandVector normal = land_vector_normalize(land_vector_cross(ab, bc))
    land_array_add(vertices, land_csg_vertex_new(a, normal))
    land_array_add(vertices, land_csg_vertex_new(b, normal))
    land_array_add(vertices, land_csg_vertex_new(c, normal))
    land_array_add(polygons, land_csg_polygon_new(vertices, shared))

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
    LandArray *polygons = land_array_new()
    LandVector a = land_vector(-1, -1, -1)
    LandVector b = land_vector( 1, -1, -1)
    LandVector c = land_vector( 1,  1, -1)
    LandVector d = land_vector(-1,  1, -1)
    LandVector e = land_vector(-1, -1,  1)
    LandVector f = land_vector( 1, -1,  1)
    LandVector g = land_vector( 1,  1,  1)
    LandVector h = land_vector(-1,  1,  1)
    add_quad(polygons, a, d, c, b, shared) # bottom
    add_quad(polygons, e, f, g, h, shared) # top
    add_quad(polygons, h, g, c, d, shared) # front
    add_quad(polygons, g, f, b, c, shared) # right
    add_quad(polygons, f, e, a, b, shared) # back
    add_quad(polygons, e, h, d, a, shared) # left
    return land_csg_new_from_polygons(polygons)

def csg_block(int x, y, z, bool outside, void *shared) -> LandCSG *:
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

                if all or k == 0:
                    add_quad(polygons, a, d, c, b, shared) # bottom
                if all or k == z - 1:
                    add_quad(polygons, e, f, g, h, shared) # top
                if all or j == y - 1:
                    add_quad(polygons, h, g, c, d, shared) # front
                if all or i == x - 1:
                    add_quad(polygons, g, f, b, c, shared) # right
                if all or j == 0:
                    add_quad(polygons, f, e, a, b, shared) # back
                if all or i == 0;
                    add_quad(polygons, e, h, d, a, shared) # left
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
