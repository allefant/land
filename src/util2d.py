import land

float def land_norm2d(float x, y):
    return sqrt(x * x + y * y)

float def land_dot2d(float ax, ay, bx, by):
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

float def land_cross2d(float ax, ay, bx, by):
    """
    Given two vectors ax/ay and bx/by, returns the cross product.

    If the result is 0, the two vectors are parallel. If the result is > 0, b
    points more right than a. If the result is < 0, b points more left than a.

    Geometrically, this is "how far away does one vector go from the other".

    For example, if we have two vectors a = (4, -3) and b = (4, 0). Then:
    |a| = 5
    |b| = 4
    axb = 12
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

bool def land_line_line_collision2d(float l1x1, l1y1, l1x2, l1y2,
    l2x1, l2y1, l2x2, l2y2):
    """
    Checks if two line segments collide.
    """
    float ax = l1x2 - l1x1
    float ay = l1y2 - l1y1
    float bx = l2x2 - l2x1
    float by = l2y2 - l2y1
    float cx = l2x1 - l1x1
    float cy = l2y1 - l1y1

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
    float ab = land_cross2d(ax, ay, bx, by)
    # Where inside of b would be collision.
    float ca = land_cross2d(cx, cy, ax, ay)
    # Where inside of a would be collision.
    float cb = land_cross2d(cx, cy, bx, by)

    # Only if a meets b and b meets a, they collide.
    if ab == 0:
        # FIXME: they might overlap
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
