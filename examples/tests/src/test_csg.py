import land.land
import land.csg.csg, land.csg.csg_shapes
import test_util

def test_csg():
    test(shape_cube)
    test(shape_sphere)
    test(shape_sphere2)
    test(shape_sphere3)
    test(shape_cylinder)
    test(shape_cylinder2)

    test(shape_hemi1)
    test(shape_hemi2)

    test_before(_setup)
    test_after(_done)
    test(union1)
    test(union2)
    test(union3)
    test(union4)
    test(subtract1)
    test(intersect)

def _test_shape_cube:
    LandCSG *cube = csg_cube(None)
    assert_int(6, cube->polygons->count, "polygon count")
    land_csg_destroy(cube)

def _test_shape_sphere:
    LandCSG *sphere = csg_sphere(3, 3, None)
    assert_int(6, sphere->polygons->count, "polygon count")
    land_csg_destroy(sphere)

def _test_shape_sphere2:
    LandCSG *sphere2 = csg_sphere(3, 4, None)
    assert_int(9, sphere2->polygons->count, "polygon count")
    land_csg_destroy(sphere2)

def _test_shape_sphere3:
    LandCSG *sphere3 = csg_sphere(4, 3, None)
    assert_int(8, sphere3->polygons->count, "polygon count")
    land_csg_destroy(sphere3)

def _test_shape_cylinder:
    LandCSG *cylinder = csg_cylinder(3, None)
    assert_int(9, cylinder->polygons->count, "polygon count")
    land_csg_destroy(cylinder)

def _test_shape_cylinder2:
    LandCSG *cylinder2 = csg_cylinder(4, None)
    assert_int(12, cylinder2->polygons->count, "polygon count")
    land_csg_destroy(cylinder2)

LandCSG *cubeA, *cubeB, *AB, *cubeC, *AC, *ABC1, *ABC2, *A_D, *cubeD
def _setup:
    cubeA = csg_cube(None)
    cubeB = csg_cube(None)
    land_csg_transform(cubeB, land_4x4_matrix_translate(4, 0, 0))
    cubeC = csg_cube(None)
    land_csg_transform(cubeC, land_4x4_matrix_translate(2, 0, 0))
    cubeD = csg_cube(None)
    land_csg_transform(cubeD, land_4x4_matrix_translate(1, 0, 0))

    AB = land_csg_union(cubeA, cubeB)
    AC = land_csg_union(cubeA, cubeC)
    ABC1 = land_csg_union(AB, cubeC)
    ABC2 = land_csg_union(cubeB, AC)

    A_D = land_csg_subtract(cubeA, cubeD)

def _destroy(LandCSG **csg):
    if *csg:
        land_csg_destroy(*csg)
    *csg = None

def _done:
    _destroy(&cubeA)
    _destroy(&cubeB)
    _destroy(&cubeC)
    _destroy(&AB)
    _destroy(&AC)
    _destroy(&ABC1)
    _destroy(&ABC2)
    _destroy(&A_D)
    _destroy(&cubeD)

def _test_union1():
    assert_int(12, AB->polygons->count, "AB polygon count")

def _test_union2():
    assert_int(10, AC->polygons->count, "AC polygon count")

def _test_union3():
    assert_int(14, ABC1->polygons->count, "ABC1 polygon count")

def _test_union4:
    assert_int(14, ABC2->polygons->count, "ABC2 polygon count")

def _test_subtract1:
    assert_int(6, A_D->polygons->count, "A-D polygon count")

def _test_intersect:
    LandCSG *AintD = land_csg_intersect(cubeA, cubeD)
    assert_int(6, AintD->polygons->count,  "A/D polygons count")
    
def _test_shape_hemi1:
    LandCSG* a = land_csg_hemi(False, 3, 2, None)
    assert_int(a->polygons->count, 6, "hemi")

def _test_shape_hemi2:
    LandCSG* a = land_csg_hemi(False, 3, 3, None)
    assert_int(a->polygons->count, 9, "hemi")
