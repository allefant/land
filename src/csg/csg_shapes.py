import land.csg.csg
static import land.util

static macro Float LandFloat
static macro pi LAND_PI

static def sphere_point(LandArray *vertices, Float i, j):
    Float theta = 2 * pi * i
    Float phi = pi * j
    LandVector normal = land_vector(
      cos(theta) * sin(phi),
      cos(phi),
      sin(theta) * sin(phi))
    LandVector pos = normal

    land_array_add(vertices, land_csg_vertex_new(pos, normal))

LandCSG *def csg_sphere(int slices, rings, void *shared):
    """
    Make a sphere with radius 1.0.
    It fits within a cube from -1/-1/-1 to 1/1/1.
    """
    if slices < 3:
        return None
    if rings < 3:
        return None
    rings--
    LandArray *polygons = land_array_new()
    for int i in range(slices):
        for int j in range(rings):
            
            LandArray *vertices = land_array_new()
            sphere_point(vertices, 1.0 * i / slices, 1.0 * j / rings)
            if j > 0:
                sphere_point(vertices, 1.0 * (i + 1) / slices,
                    1.0 * j / rings)
            if j < rings - 1:
                sphere_point(vertices, 1.0 * (i + 1) / slices,
                    1.0 * (j + 1) / rings)
            sphere_point(vertices, 1.0 * i / slices,
                    1.0 * (j + 1) / rings)

            land_array_add(polygons, land_csg_polygon_new(vertices, shared))
            
    return land_csg_new_from_polygons(polygons)

LandCSG *def csg_cylinder(int slices, void *shared):
    return csg_cylinder_open(slices, False, shared)

LandCSG *def csg_cylinder_open(int slices, bool opened, void *shared):
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

        Float angle0 = i * 2 * pi / slices
        Float angle1 = (i + 1) * 2 * pi / slices
        Float c0 = cos(angle0), s0 = sin(angle0)
        Float c1 = cos(angle1), s1 = sin(angle1)

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

LandCSG *def csg_cone(int slices, void *shared):
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

        Float angle0 = i * 2 * pi / slices
        Float angle1 = (i + 1) * 2 * pi / slices
        #Float anglem = (i + 0.5) * 2 * pi / slices
        Float c0 = cos(angle0), s0 = sin(angle0)
        Float c1 = cos(angle1), s1 = sin(angle1)
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

LandCSG *def csg_prism(int slices, void *shared):
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

LandCSG *def csg_pyramid(void *shared):
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

LandCSG *def csg_tetrahedron(void *shared):
    """
    Make a tetrahedron.
    """
    LandArray *polygons = land_array_new()
    Float s = 1 / sqrt(2)
    LandVector a = land_vector(-1, 0, -s)
    LandVector b = land_vector( 1, 0, -s)
    LandVector c = land_vector( 0, -1, s)
    LandVector d = land_vector( 0,  1, s)
    add_tri(polygons, a, d, b, shared)
    add_tri(polygons, d, c, b, shared)
    add_tri(polygons, c, d, a, shared)
    add_tri(polygons, c, a, b, shared)
    return land_csg_new_from_polygons(polygons)

LandCSG *def csg_cube(void *shared):
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
