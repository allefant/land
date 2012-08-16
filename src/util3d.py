import math

typedef double LandFloat

class LandVector:
    """
    A simple 3D vector, with some extra useful methods for quaternions,
    transformations and rotation.
    """
    LandFloat x, y, z

class Land4x4Matrix:
    LandFloat v[16]

class LandQuaternion:
    """
    A quaternion can be useful to hold rotations, as it is much easier to use
    for physics code. For example a 3x3 matrix has too much redundancy (9 values
    instead of 3), and so usually will be hard to deal with or lead to wrong
    results. A quaternion instead will hold not much more than just the
    orientation (4 values instead of 3).

    Orientation basically is a direction, with an additional rotation. For
    example, a 3d vector plus an angle would describe it. Since the length of
    the 3d vector does not matter, just 3 angles also are enough (pitch, yaw,
    roll). Obviously, we can convert from any form to each other, quaternions
    just have properties which make them easy to use in physics code.
    """
    LandFloat w, x, y, z

static macro SQRT sqrt
static macro COS cos
static macro SIN sin

LandVector def land_vector(LandFloat x, y, z):
    LandVector v = {x, y, z}
    return v

LandVector def land_vector_from_array(LandFloat *a):
    LandVector v = {a[0], a[1], a[2]}
    return v

def land_vector_iadd(LandVector *v, LandVector w):
    v->x += w.x
    v->y += w.y
    v->z += w.z

def land_vector_isub(LandVector *v, LandVector w):
    v->x -= w.x
    v->y -= w.y
    v->z -= w.z

def land_vector_imul(LandVector *v, LandFloat s):
    v->x *= s
    v->y *= s
    v->z *= s

def land_vector_idiv(LandVector *v, LandFloat s):
    v->x /= s
    v->y /= s
    v->z /= s

LandVector def land_vector_neg(LandVector v):
    LandVector r = {-v.x, -v.y, -v.z}
    return r

LandVector def land_vector_mul(LandVector v, LandFloat s):
    LandVector r = {v.x * s, v.y * s, v.z * s}
    return r

LandVector def land_vector_div(LandVector v, LandFloat s):
    LandVector r  = {v.x / s, v.y / s, v.z / s}
    return r

LandVector def land_vector_add(LandVector v, w):
    LandVector r = {v.x + w.x, v.y + w.y, v.z + w.z}
    return r

LandVector def land_vector_sub(LandVector v, w):
    LandVector r = {v.x - w.x, v.y - w.y, v.z - w.z}
    return r

LandFloat def land_vector_dot(LandVector v, w):
    """
    The dot product is a number. The number corresponds to the cosine
    between the two vectors times their lengths. So the angle between the
    vectors would be: angle = acos(v . w / (|v| * |w|)). If the dot product
    is 0, the two vectors conversely are orthogonal. The sign can be used to
    determine which side of a plane a point is on.
    """
    return v.x * w.x + v.y * w.y + v.z * w.z

LandVector def land_vector_cross(LandVector v, w):
    """
    The cross product results in a vector orthogonal to both v and w. The
    length of the resulting vector corresponds to the sine of the angle
    between the two vectors and their lengths. So the angle between the
    vectors would be: angle = asin(|v x w| / (|v| * |w|)). If the cross
    product is the 0 vector, the two input vectors are parallel.
    """
    LandVector r = {
        v.y * w.z - w.y * v.z,
        v.z * w.x - w.z * v.x,
        v.x * w.y - w.x * v.y}
    return r

LandFloat def land_vector_norm(LandVector v):
    """
    Return the norm of the vector.
    """
    return SQRT(land_vector_dot(v, v))

LandVector def land_vector_normalize(LandVector v):
    """
    Return a normalized version of the vector.
    """
    return land_vector_div(v, land_vector_norm(v))

LandQuaternion def land_vector_quatmul(LandVector v, LandQuaternion q):
    """
    Multiply the vector with a quaternion. The result is a quaternion. For
    example if your vector is a rotation, the resulting quaternion will be a
    quaternion who rotates whatever it did plus this additional rotation.
    """
    LandQuaternion r = {
        - v.x * q.x - v.y * q.y - v.z * q.z,
          v.x * q.w + v.y * q.z - v.z * q.y,
          v.y * q.w + v.z * q.x - v.x * q.z,
          v.z * q.w + v.x * q.y - v.y * q.x}
    return r

LandVector def land_vector_transform(LandVector v, p, r, u, b):
    """
    Return a new vector obtained by transforming this vector by a coordinate
    system with the given origin and given right/up/back vectors. This is
    used if the vector is in world coordinates, and you want to transform it
    to camera coordinates, where p/r/u/b define camera position and
    orientation.
    """
    LandVector w = land_vector_sub(v, p)
    LandVector a = {
        land_vector_dot(w, r),
        land_vector_dot(w, u),
        land_vector_dot(w, b)}
    return a

LandVector def land_vector_matmul(LandVector v, Land4x4Matrix *m):
    LandFloat x = m->v[0] * v.x + m->v[1] * v.y + m->v[2] * v.z + m->v[3]
    LandFloat y = m->v[4] * v.x + m->v[5] * v.y + m->v[6] * v.z + m->v[7]
    LandFloat z = m->v[8] * v.x + m->v[9] * v.y + m->v[10] * v.z + m->v[11]
    return land_vector(x, y, z)

LandVector def land_vector_backtransform(LandVector v, p, r, u, b):
    """
    Do the inverse of transform, i.e. you can use it to transform from
    camera back to world coordinates.
    """
    LandVector x = land_vector_mul(r, v.x)
    LandVector y = land_vector_mul(u, v.y)
    LandVector z = land_vector_mul(b, v.z)
    LandVector a = p
    land_vector_iadd(&a, x)
    land_vector_iadd(&a, y)
    land_vector_iadd(&a, z)
    return a

LandVector def land_vector_rotate(LandVector v, a, double angle):
    """
    Rotate the vector around axis a by angle in counter clockwise direction.
    If this vector is a point in world space, then the axis of rotation is
    defined by the origin and the a vector.
    """
    LandFloat c = COS(angle)
    LandFloat s = SIN(angle)

    LandVector r = land_vector_mul(a, a.x * (1 - c))
    LandVector u = land_vector_mul(a, a.y * (1 - c))
    LandVector b = land_vector_mul(a, a.z * (1 - c))

    r.x += c
    r.y += a.z * s
    r.z -= a.y * s

    u.x -= a.z * s
    u.y += c
    u.z += a.x * s

    b.x += a.y * s
    b.y -= a.x * s
    b.z += c

    LandFloat x = land_vector_dot(v, r)
    LandFloat y = land_vector_dot(v, u)
    LandFloat z = land_vector_dot(v, b)

    LandVector ret = {x, y, z}

    return ret

LandVector def land_vector_reflect(LandVector v, n):
    """
    Given the normal of a plane, reflect the vector off the plane. If the
    vector is a point in 3D space, and the plane goes through the origin,
    the result is a point reflected by the plane.
    """
    LandFloat d = land_vector_dot(v, n)
    LandVector r = n
    land_vector_imul(&r, -2 * d)
    land_vector_iadd(&r, v)
    return r

LandQuaternion def land_quaternion(LandFloat w, x, y, z):
    LandQuaternion q = {w, x, y, z}
    return q

LandQuaternion def land_quaternion_from_array(LandFloat *f):
    LandQuaternion q = {f[0], f[1], f[2], f[3]}
    return q

def land_quaternion_to_array(LandQuaternion *q, LandFloat *f):
    f[0] = q->w
    f[1] = q->x
    f[2] = q->y
    f[3] = q->z

def land_quaternion_iadd(LandQuaternion *q, LandQuaternion p):
    q->w += p.w
    q->x += p.x
    q->y += p.y
    q->z += p.z

def land_quaternion_imul(LandQuaternion *q, LandFloat s):
    q->w *= s
    q->x *= s
    q->y *= s
    q->z *= s

LandQuaternion def land_quaternion_combine(LandQuaternion qa, LandQuaternion qb):

    # FIXME: what is this?

    LandVector qav = {qa.x, qa.y, qa.z}
    LandVector qbv = {qb.x, qb.y, qb.z}
    LandVector va = land_vector_cross(qav, qbv)
    LandVector vb = land_vector_mul(qav, qb.w)
    LandVector vc = land_vector_mul(qbv, qa.w)
    land_vector_iadd(&va, vb)
    LandVector qrv = land_vector_add(va, vc)
    
    double w = land_vector_dot(qav, qbv)
    LandQuaternion qr = {qrv.x, qrv.y, qrv.z, w}

    land_quaternion_normalize(&qr)
    return qr

def land_quaternion_vectors(LandQuaternion q, LandVector *r, *u, *b):
    """
    Output three orientation vectors for the quaternion. That is, if the
    quaternion is used as a 3D orientation, return right/up/back vectors
    representing the same orientation.
    """
    LandFloat ww = q.w * q.w
    LandFloat xx = q.x * q.x
    LandFloat yy = q.y * q.y
    LandFloat zz = q.z * q.z
    LandFloat wx = q.w * q.x * 2
    LandFloat wy = q.w * q.y * 2
    LandFloat wz = q.w * q.z * 2
    LandFloat xy = q.x * q.y * 2
    LandFloat xz = q.x * q.z * 2
    LandFloat yz = q.y * q.z * 2

    r->x = ww + xx - yy - zz
    u->x = xy - wz
    b->x = xz + wy

    r->y = xy + wz
    u->y = ww - xx + yy - zz
    b->y = yz - wx

    r->z = xz - wy
    u->z = yz + wx
    b->z = ww - xx - yy + zz

Land4x4Matrix def land_quaternion_4x4_matrix(LandQuaternion q):
    LandVector r, u, b
    land_quaternion_vectors(q, &r, &u, &b)
    Land4x4Matrix m
    m.v[0] = r.x
    m.v[1] = u.x
    m.v[2] = b.x
    m.v[3] = 0
    m.v[4] = r.y
    m.v[5] = u.y
    m.v[6] = b.y
    m.v[7] = 0
    m.v[8] = r.z
    m.v[9] = u.z
    m.v[10] = b.z
    m.v[11] = 0
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

Land4x4Matrix def land_4x4_matrix_mul(Land4x4Matrix a, Land4x4Matrix b):
    Land4x4Matrix m
    for int i in range(4):
        for int j in range(4):
            LandFloat x = 0
            for int k in range(4):
                x += a.v[i * 4 + k] * b.v[k * 4 + j]
            m.v[i * 4 + j] = x
    return m

Land4x4Matrix def land_4x4_matrix_scale(LandFloat x, y, z):
    Land4x4Matrix m
    m.v[0] = x
    m.v[1] = 0
    m.v[2] = 0
    m.v[3] = 0
    m.v[4] = 0
    m.v[5] = y
    m.v[6] = 0
    m.v[7] = 0
    m.v[8] = 0
    m.v[9] = 0
    m.v[10] = z
    m.v[11] = 0
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

Land4x4Matrix def land_4x4_matrix_rotate(LandFloat x, y, z, angle):
    Land4x4Matrix m

    double s = sin(angle);
    double c = cos(angle);
    double cc = 1 - c;

    m.v[0] = (cc * x * x) + c
    m.v[4] = (cc * x * y) + (z * s)
    m.v[8] = (cc * x * z) - (y * s)
    m.v[12] = 0
    m.v[1] = (cc * x * y) - (z * s)
    m.v[5] = (cc * y * y) + c
    m.v[9] = (cc * z * y) + (x * s)
    m.v[13] = 0
    m.v[2] = (cc * x * z) + (y * s)
    m.v[6] = (cc * y * z) - (x * s)
    m.v[10] = (cc * z * z) + c
    m.v[14] = 0
    m.v[3] = 0
    m.v[7] = 0
    m.v[11] = 0
    m.v[15] = 1

    return m

Land4x4Matrix def land_4x4_matrix_perspective(LandFloat z):
    Land4x4Matrix m
    m.v[0] = 1
    m.v[1] = 0
    m.v[2] = 0
    m.v[3] = 0
    m.v[4] = 0
    m.v[5] = 1
    m.v[6] = 0
    m.v[7] = 0
    m.v[8] = 0
    m.v[9] = 0
    m.v[10] = 1
    m.v[11] = 0
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 1 / z
    m.v[15] = 1
    return m

Land4x4Matrix def land_4x4_matrix_identity():
    Land4x4Matrix m
    m.v[0] = 1
    m.v[1] = 0
    m.v[2] = 0
    m.v[3] = 0
    m.v[4] = 0
    m.v[5] = 1
    m.v[6] = 0
    m.v[7] = 0
    m.v[8] = 0
    m.v[9] = 0
    m.v[10] = 1
    m.v[11] = 0
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

Land4x4Matrix def land_4x4_matrix_translate(LandFloat x, y, z):
    Land4x4Matrix m
    m.v[0] = 1
    m.v[1] = 0
    m.v[2] = 0
    m.v[3] = x
    m.v[4] = 0
    m.v[5] = 1
    m.v[6] = 0
    m.v[7] = y
    m.v[8] = 0
    m.v[9] = 0
    m.v[10] = 1
    m.v[11] = z
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

# note: "near" and "far" are keywords in certain windows compilers
Land4x4Matrix def land_4x4_matrix_orthographic(LandFloat left, top, nearz,
        right, bottom, farz):
    """
    Orthographic means no projection so this would be just an identity matrix.
    But as convenience this scales and translates to fit into the
    left/top/right/bottom rectangle and also scales depth.

    The point at (left, top, near) will end up at (-1, -1, -1) and the point
    at (right, bottom, far) will end up at (1, 1, 1).
    """
    Land4x4Matrix m
    LandFloat w = right - left
    LandFloat h = bottom - top
    LandFloat depth = farz - nearz
    LandFloat x = (right + left) / 2
    LandFloat y = (bottom + top) / 2
    LandFloat z = (farz + nearz) / 2
    
    m.v[0] = 2 / w
    m.v[1] = 0
    m.v[2] = 0
    m.v[3] = 0
    m.v[4] = 2 / w * -x
    m.v[5] = 2 / h
    m.v[6] = 0
    m.v[7] = 0
    m.v[8] = 0
    m.v[9] = 2 / h * -y
    m.v[10] = 2 / depth
    m.v[11] = 2 / depth * -z
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

Land4x4Matrix def land_4x4_matrix_from_vectors(LandVector *p, *r, *u, *b):
    Land4x4Matrix m
    m.v[0] = r->x
    m.v[1] = u->x
    m.v[2] = b->x
    m.v[3] = p->x
    m.v[4] = r->y
    m.v[5] = u->y
    m.v[6] = b->y
    m.v[7] = p->y
    m.v[8] = r->z
    m.v[9] = u->z
    m.v[10] = b->z
    m.v[11] = p->z
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

Land4x4Matrix def land_4x4_matrix_inverse_from_vectors(LandVector *p, *r, *u, *b):
    Land4x4Matrix m
    m.v[0] = r->x
    m.v[1] = r->y
    m.v[2] = r->z
    m.v[3] = r->x * -p->x + r->y * -p->y + r->z * -p->z
    m.v[4] = u->x
    m.v[5] = u->y
    m.v[6] = u->z
    m.v[7] = u->x * -p->x + u->y * -p->y + u->z * -p->z
    m.v[8] = b->x
    m.v[9] = b->y
    m.v[10] = b->z
    m.v[11] = b->x * -p->x + b->y * -p->y + b->z * -p->z
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

def land_quaternion_normalize(LandQuaternion *q):
    """
    Normalize the quaternion. This may be useful to prevent deteriorating
    the quaternion if it is used for a long time, due to floating point
    inaccuracies.
    """
    LandFloat n = SQRT(q->w * q->w + q->x * q->x + q->y * q->y + q->z * q->z)
    q->w /= n
    q->x /= n
    q->y /= n
    q->z /= n

LandQuaternion def land_quaternion_slerp(LandQuaternion qa, qb, double t):
    """
    Given two quaternions, interpolate a quaternion in between. If t is 0
    this will return, if t is 1 it will return qb.

    The rotation will be along the shortest path (not necessarily the shorter
    direction though) and the rotation angle will linearly correspond to t.
    """
    LandQuaternion q
    double c = qa.w * qb.w + qa.x * qb.x + qa.y * qb.y + qa.z * qb.z

    if c < 0:
        c = -c
        qb.w = -qb.w
        qb.x = -qb.x
        qb.y = -qb.y
        qb.z = -qb.z

    double theta = acos(c);

    double s = sin(theta)

    double fs = sin((1 - t) * theta) / s;
    double ts = sin(t * theta) / s;

    q.w = qa.w * fs + qb.w * ts;
    q.x = qa.x * fs + qb.x * ts;
    q.y = qa.y * fs + qb.y * ts;
    q.z = qa.z * fs + qb.z * ts;

    return q;
