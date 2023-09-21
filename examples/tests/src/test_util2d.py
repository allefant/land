import global land.land
import test_util
import global land.util2d

def test_util2d:
    test(point_in_rect)
    test(point_rounded_rectangle_distance)
    test(point_segment_distance)

def _test_point_in_rect:
    for int t in range(4):
        float a = pi * 2 * t / 4
        assert_bool(land_point_in_rect(0, 0, 0, 0, a, 1, 1), True, "A")
        assert_bool(land_point_in_rect(0.499, 0, 0, 0, a, 1, 1), True, "B1")
        assert_bool(land_point_in_rect(0.501, 0, 0, 0, a, 1, 1), False, "B2")
        assert_bool(land_point_in_rect(-0.499, 0, 0, 0, a, 1, 1), True, "B1")
        assert_bool(land_point_in_rect(-0.501, 0, 0, 0, a, 1, 1), False, "B2")
        assert_bool(land_point_in_rect(0, 0.499, 0, 0, a, 1, 1), True, "B1")
        assert_bool(land_point_in_rect(0, 0.501, 0, 0, a, 1, 1), False, "B2")
        assert_bool(land_point_in_rect(0, -0.499, 0, 0, a, 1, 1), True, "B1")
        assert_bool(land_point_in_rect(0, -0.501, 0, 0, a, 1, 1), False, "B2")

    assert_bool(land_point_in_rect(0.49, 0.49, 0, 0, 0, 1, 1), True, "A45")
    assert_bool(land_point_in_rect(0.49, 0.49, 0, 0, pi / 4, 1, 1), False, "A45")

    assert_bool(land_point_in_rect(1.9, 0, 1, 0, 0, 2, 1), True, "2x1")
    assert_bool(land_point_in_rect(1.9, 0, 1, 0, pi / 2, 2, 1), False, "2x1")
    assert_bool(land_point_in_rect(1, 0.9, 1, 0, pi / 2, 2, 1), True, "2x1")
    assert_bool(land_point_in_rect(1, 0.9, 1, 0, 0, 2, 1), False, "2x1")

def _test_point_rounded_rectangle_distance:
    for int t in range(32):
        float a = pi * 2 * t / 32
        assert_float(land_point_rectangle_distance(0, 0, 0, 0, a, 1, 1), -0.5, 3, "A")

    float a = pi / 4
    assert_float(land_point_rectangle_distance(0, 0, 1, 1, a, 2, 2), sqrt(2) - 1, 3, "B")

    LandRectangle r = land_rotated_rectangle_aabb(0, 0, a, 10, 10)
    char *result = land_strdup("\n")
    assert_float(r.x, -7.07, 1, "r.x")
    assert_float(r.y, -7.07, 1, "r.y")
    assert_float(r.w, 14.14, 1, "r.w")
    assert_float(r.h, 14.14, 1, "r.h")
    for int y in range(r.h):
        for int x in range(r.w):
            float d = land_point_rectangle_distance(r.x + x, r.y + y, 0, 0, a, 10, 10)
            if d <= 0: land_append(&result, "%d", (int)(-d))
            else: land_append(&result, ".")
        land_append(&result, "\n")

    str expected = """
...............
.......00......
......0100.....
.....012100....
....01222100...
...0122322100..
..012234322100.
.01223444322100
.0012234322100.
..00122322100..
...001222100...
....0012100....
.....00100.....
......000......
.......0.......
"""
    assert_equals(result, expected)

def _assert_distance(LandFloat x, y, ax, ay, bx, by, expected, str text):
    assert_float(land_point_segment_distance(x, y, ax, ay, bx, by), expected, 5, text)

def _test_point_segment_distance:
    _assert_distance(0, 0, 0, 0, 1, 0, 0, "to A")
    _assert_distance(1, 0, 0, 0, 1, 0, 0, "to B")
    _assert_distance(0.5, 0, 0, 0, 1, 0, 0, "to center")
    _assert_distance(-1, 0, 0, 0, 1, 0, 1, "left")
    _assert_distance(2, 0, 0, 0, 1, 0, 1, "right")
    _assert_distance(0, 1, 0, 0, 1, 0, 1, "up")
    _assert_distance(1, 1, 0, 0, 1, 0, 1, "up")
    _assert_distance(0, -1, 0, 0, 1, 0, 1, "down")
    _assert_distance(1, -1, 0, 0, 1, 0, 1, "down")

    _assert_distance(0, 0, 1, 0, 0, 0, 0, "to A")
    _assert_distance(1, 0, 1, 0, 0, 0, 0, "to B")
    _assert_distance(0.5, 0, 1, 0, 0, 0, 0, "to center")
    _assert_distance(-1, 0, 1, 0, 0, 0, 1, "left")
    _assert_distance(2, 0, 1, 0, 0, 0, 1, "right")
    _assert_distance(0, 1, 1, 0, 0, 0, 1, "up")
    _assert_distance(1, 1, 1, 0, 0, 0, 1, "up")
    _assert_distance(0, -1, 1, 0, 0, 0, 1, "down")
    _assert_distance(1, -1, 1, 0, 0, 0, 1, "down")

    _assert_distance(100.0, 50.0, 110.0, 50.0, 90.0, 50.0, 0, "line")
