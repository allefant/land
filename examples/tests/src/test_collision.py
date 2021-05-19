import global land.land
import global land.util2d
import test_util

class Line:
    float x1, y1, x2, y2
class Circle:
    float x, y, r

Line l[10]
Circle c[10]

def line(float x1, y1, x2, y2) -> Line:
    Line l = {x1, y1, x2, y2}
    return l

def reverse(Line l) -> Line:
    Line l2 = {l.x2, l.y2, l.x1, l.y1}
    return l2

def circle(float x, y, r) -> Circle:
    Circle c = {x, y, r}
    return c

def llc(Line l1, Line l2) -> bool:
    return land_line_line_collision2d(l1.x1, l1.y1, l1.x2, l1.y2,
        l2.x1, l2.y1, l2.x2, l2.y2)

def lcc(Line l, Circle c) -> bool:
    return land_line_circle_collision2d(l.x1, l.y1, l.x2, l.y2,
        c.x, c.y, c.r)

def _setup:
    l[0] = line(1, 1, 2, 1)
    l[1] = line(1.5, 1.5, 1.5, 0.5)
    l[2] = line(1, 2, 2, 0.5)
    l[3] = line(0.5, 0.75, 1.5, 0.75)
    l[4] = line(1.5, 1, 1.5, 1.25)
    l[5] = reverse(l[0])
    l[6] = reverse(l[1])
    l[7] = reverse(l[2])
    l[8] = reverse(l[3])
    l[9] = reverse(l[4])
    #   |
    # 2-|         2
    #   |          22
    #   |            2 1
    #   |             24
    # 1-|         00000400000
    #   |    33333333331  22
    #   |              1    2
    #   |
    # 0-|---------|---------|-
    #   0         1         2

    c[0] = circle(0, 0, 1)
    c[1] = circle(1, 0, 1)
    c[2] = circle(2, 0, 1)
    c[3] = circle(0, 1, 1)
    c[4] = circle(0, 1, 1.5)
    c[5] = circle(0.5, 1.5, sqrt(0.501))

def test_collision:
    test_before(_setup)
    test(line_line)
    test(line_circle)

def _test_line_line:
    
    for int i in range(10):
        for int j in range(10):
            bool result = llc(l[i], l[j])
            int i2 = i % 5
            int j2 = j % 5
            bool expect = i2 == j2 # every line collides with itself
            if i2 > j2:
                i2 = j % 5
                j2 = i % 5
            if i2 == 0:
                if j2 == 1 or j2 == 2 or j2 == 4: expect = True
            if i2 == 1:
                expect = True
            if i2 == 2:
                if j2 == 4: expect = True
            if i2 == 3:
                pass
            char expl[100]
            sprintf(expl, "line-line collision %d and %d", i, j)
            assert_bool(result, expect, expl)

def _test_line_circle:  
    for int i in range(6):
        for int j in range(10):
            bool result = lcc(l[j], c[i])
            int j2 = j % 5
            bool expect = False
            if i == 0:
                expect = j2 == 3
            if i == 1:
                expect = j2 == 0 or j2 == 1 or j2 == 3
            if i == 2:
                expect = j2 == 0 or j2 == 1 or j2 == 2 or j2 == 3
            if i == 3:
                expect = j2 == 0 or j2 == 3
            if i == 4:
                expect = True
            if i == 5:
                expect = j2 == 0 or j2 == 2
            char expl[100]
            sprintf(expl, "line-circle collision %d and %d", j, i)
            assert_bool(result, expect, expl)

