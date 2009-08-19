import math

macro LandFloat double

class LandVector:
    """
    A simple 3D vector, with some extra useful methods for quaternions,
    transformations and rotation.
    """
    LandFloat x, y, z

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

def land_vector_iadd(LandVector v, w):
    v.x += w.x
    v.y += w.y
    v.z += w.z

def land_vector_isub(LandVector v, w):
    v.x -= w.x
    v.y -= w.y
    v.z -= w.z

def land_vector_imul(LandVector v, LandFloat s):
    v.x *= s
    v.y *= s
    v.z *= s

def land_vector_idiv(LandVector v, LandFloat s):
    v.x /= s
    v.y /= s
    v.z /= s

LandVector def land_vector_neg(LandVector v):
    LandVector r = {-v.x, -v.y, -v.z}
    return r

LandVector def land_vector_mul(LandVector v, LandFloat s):
    LandVector r  = {v.x * s, v.y * s, v.z * s}
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

LandVector def land_vector_backtransform(LandVector v, p, r, u, b):
    """
    Do the inverse of transform, i.e. you can use it to transform from
    camera back to world coordinates.
    """
    LandVector x = land_vector_mul(r, v.x)
    LandVector y = land_vector_mul(u, v.y)
    LandVector z = land_vector_mul(b, v.z)
    LandVector a = p
    land_vector_iadd(a, x)
    land_vector_iadd(a, y)
    land_vector_iadd(a, z)
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
    land_vector_imul(r, -2 * d)
    land_vector_iadd(r, v)
    return r

LandQuaternion def land_quaternion(LandFloat w, x, y, z):
    LandQuaternion q = {w, x, y, z}
    return q

def land_quaternion_iadd(LandQuaternion q, p):
    q.w += p.w
    q.x += p.x
    q.y += p.y
    q.z += p.z

def land_quaternion_imul(LandQuaternion q, LandFloat s):
    q.w *= s
    q.x *= s
    q.y *= s
    q.z *= s

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

def land_quaternion_normalize(LandQuaternion q):
    """
    Normalize the quaternion. This may be useful to prevent deteriorating
    the quaternion if it is used for a long time, due to Fing point
    inaccuracies.
    """
    LandFloat n = SQRT(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z)
    q.w /= n
    q.x /= n
    q.y /= n
    q.z /= n

