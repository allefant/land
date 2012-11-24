import csg, csg_shapes

def test(char const *name, int want, got):
    if want == got:
        printf("OK   %s\n", name)
    else:
        printf("FAIL %s (want %d but got %d)\n", name, want, got)

def csg_test_shapes():
    LandCSG *cube = csg_cube(None)
    test("cube", 6, cube->polygons->count)
    land_csg_destroy(cube)

    LandCSG *sphere = csg_sphere(3, 3, None)
    test("sphere", 6, sphere->polygons->count)
    land_csg_destroy(sphere)

    LandCSG *sphere2 = csg_sphere(3, 4, None)
    test("sphere2", 9, sphere2->polygons->count)
    land_csg_destroy(sphere2)

    LandCSG *sphere3 = csg_sphere(4, 3, None)
    test("sphere3", 8, sphere3->polygons->count)
    land_csg_destroy(sphere3)

    LandCSG *cylinder = csg_cylinder(3, None)
    test("cylinder", 9, cylinder->polygons->count)
    land_csg_destroy(cylinder)

    LandCSG *cylinder2 = csg_cylinder(4, None)
    test("cylinder2", 12, cylinder2->polygons->count)
    land_csg_destroy(cylinder2)

def csg_test_union():
    LandCSG *cubeA = csg_cube(None)
    LandCSG *cubeB = csg_cube(None)
    land_csg_transform(cubeB, land_4x4_matrix_translate(4, 0, 0))

    LandCSG *AB = land_csg_union(cubeA, cubeB)
    test("AB", 12, AB->polygons->count)

    LandCSG *cubeC = csg_cube(None)
    land_csg_transform(cubeC, land_4x4_matrix_translate(2, 0, 0))

    LandCSG *AC = land_csg_union(cubeA, cubeC)
    test("AC", 10, AC->polygons->count)

    LandCSG *ABC1 = land_csg_union(AB, cubeC)
    test("ABC1", 14, ABC1->polygons->count)

    LandCSG *ABC2 = land_csg_union(cubeB, AC)
    test("ABC2", 14, ABC2->polygons->count)

    land_csg_destroy(cubeA)
    land_csg_destroy(cubeB)
    land_csg_destroy(cubeC)
    land_csg_destroy(AB)
    land_csg_destroy(AC)
    land_csg_destroy(ABC1)
    land_csg_destroy(ABC2)

def csg_test_subtract():
    LandCSG *cubeA = csg_cube(None)
    LandCSG *cubeB = csg_cube(None)
    land_csg_transform(cubeB, land_4x4_matrix_translate(1, 0, 0))
    LandCSG *A_B = land_csg_subtract(cubeA, cubeB)
    test("A-B", 6, A_B->polygons->count)

    LandCSG *cubeBi = land_csg_inverse(cubeB)
    test("Bi", 6, cubeBi->polygons->count)
    LandCSG *ABi = land_csg_union(cubeA, cubeBi)
    test("ABi", 6, ABi->polygons->count)

    land_csg_destroy(cubeA)
    land_csg_destroy(cubeB)
    land_csg_destroy(A_B)
    land_csg_destroy(cubeBi)
    land_csg_destroy(ABi)

def csg_test_intersect():
    LandCSG *cubeA = csg_cube(None)
    LandCSG *cubeB = csg_cube(None)
    land_csg_transform(cubeB, land_4x4_matrix_translate(1, 0, 0))
    LandCSG *A_B = land_csg_intersect(cubeA, cubeB)
    test("A/B", 6, A_B->polygons->count)
    land_csg_destroy(cubeA)
    land_csg_destroy(cubeB)
    land_csg_destroy(A_B)
    
def csg_test():
    csg_test_shapes()
    csg_test_union()
    csg_test_subtract()
    csg_test_intersect()
