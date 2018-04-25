import land

def land_norm2d(float x, y) -> float:
    return sqrt(x * x + y * y)

def land_dot2d(float ax, ay, bx, by) -> float:
    """
    Given two vectors ax/ay and bx/by, returns the dot product.

    If the result is 0, the two vectors are orthogonal. If the result is
    > 0, they point into the same general direction. If the result is < 0,
    they point into opposite directions.

    This can be geometrically interpreted as "how far one vector goes along the
    direction of the other vector".

    For example, if we have two vectors a = (4, -3) and b = (4, 0). Then:
    |a| = 5
    |b| = 4
    a.b = 16
    cos = a.b / |a| / |b| = 0.8 (36.87°)
    length of a projected onto b: a.b / |b| = 4
    length of b projected onto a: a.b / |a| = 3.2

    """
    return ax * bx + ay * by

def land_cross2d(float ax, ay, bx, by) -> float:
    """
    Given two vectors ax/ay and bx/by, returns the cross product.

    If the result is 0, the two vectors are parallel. If the result
    is > 0, b points more to the left than a (if y goes up). If the
    result is < 0, b points more to the right than a (if y goes up).

    Geometrically, this is "how far away does one vector go from the other".

    For example, if we have two vectors a = (4, -3) and b = (4, 0). Then:
    |a| = 5
    |b| = 4
    axb = 4 * 0 - -3 * 4 = 12
    sin = axb / |a| / |b| = 0.6 (36.87°)
    distance of a from b: axb / |b| = 3
    distance of b from a: axb / |a| = 2.4
    """
    return ax * by - ay * bx

def land_ortho2d(float ax, ay, *bx, *by):
    """
    Returns a vector orthogonal to ax/ay. More specifically, returns a
    vector rotated 90 degree to the right (with y axis going down).
    """
    *bx = -ay;
    *by = ax;

def land_line_line_collision2d(LandFloat l1x1, l1y1, l1x2, l1y2,
        l2x1, l2y1, l2x2, l2y2) -> bool:
    """
    Checks if two line segments collide.
    """
    LandFloat ax = l1x2 - l1x1
    LandFloat ay = l1y2 - l1y1
    LandFloat bx = l2x2 - l2x1
    LandFloat by = l2y2 - l2y1
    LandFloat cx = l2x1 - l1x1
    LandFloat cy = l2y1 - l1y1

    # They collide if:
    # cx + B bx = A ax (1)
    # cy + B by = A ay (2)
    # A/B both from [0;1]
    #
    # Solving for A:
    # (from 1) B = (A ax - cx) / bx
    # (in 2) cy + (A ax - cx) / bx * by = A ay
    # cy bx + A ax by - cx by = A ay bx
    # A = (cx by - cy bx) / (ax by - ay bx) = cxb / axb
    #
    # Solving for B:
    # (from 1) A = (cx + B bx) / ax
    # (in 2) cy + B by = (cx + B bx) / ax * ay
    # cy ax + B ax by = cx ay + B ay bx
    # B = (cx ay - cy ay) / (ax by - ay bx) = cxa / axb
    #
    # We have a collision if both A and B are within [0;1].
    
    # 0 -> parallel, >0 -> right, <0 -> left.
    LandFloat ab = land_cross2d(ax, ay, bx, by)
    # Where inside of b would be collision.
    LandFloat ca = land_cross2d(cx, cy, ax, ay)
    # Where inside of a would be collision.
    LandFloat cb = land_cross2d(cx, cy, bx, by)

    # Only if a meets b and b meets a, they collide.
    if ab == 0:
        if ca == 0:
            # lines coincide
            LandFloat dac = land_dot2d(ax, ay, cx, cy)
            LandFloat dx = l2x2 - l1x1
            LandFloat dy = l2y2 - l1y1
            LandFloat dad = land_dot2d(ax, ay, dx, dy)
            
            if dac < 0:
                if dad < 0: return False
                return True
            if dad < 0: return True

            LandFloat daa = land_dot2d(ax, ay, ax, ay)

            if dac * dac > daa * daa and dad * dad > daa * daa: return False 
            
            return True
        return False
    if ab < 0:
        if ca > 0 or cb > 0: return False
        if ca < ab or cb < ab: return False
    else:
        if ca < 0 or cb < 0: return False
        if ca > ab or cb > ab: return False

    # A = cb / ab
    # B = ca / ab
    # x = l1x1 + A * ax = l2x1 + B * bx
    # y = l1y1 + A * ay = l2y1 + B * by

    return True

def circle_circle_collision2d(LandFloat c1x1, c1y1, c1r,
        c2x1, c2y1, c2r) -> bool:
    LandFloat ax = c2x1 - c1x1
    LandFloat ay = c2y1 - c1y1
    LandFloat r = c1r + c2r
    return ax * ax + ay * ay <= r * r

def land_line_circle_collision2d(LandFloat lx1, ly1, lx2, ly2,
        cx1, cy1, cr) -> bool:

    LandFloat ax = lx2 - lx1
    LandFloat ay = ly2 - ly1
    LandFloat bx = cx1 - lx1
    LandFloat by = cy1 - ly1
    LandFloat cx = cx1 - lx2
    LandFloat cy = cy1 - ly2
    LandFloat c = land_cross2d(ax, ay, bx, by)
    LandFloat a = ax * ax + ay * ay
    
    if a == 0: # line is just a point
        if bx * bx + by * by <= cr * cr: return True
        return False

    # circle is outside of the thick line
    if c * c / a > cr * cr: return False

    LandFloat ab = land_dot2d(ax, ay, bx, by)
    LandFloat ac = land_dot2d(ax, ay, cx, cy)

    # circle center is within line start and end
    if ab >= 0 and ac <= 0: return True

    # check distance to the two end-points
    if bx * bx + by * by <= cr * cr: return True
    if cx * cx + cy * cy <= cr * cr: return True
    
    return False
