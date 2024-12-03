"""
translation matrix to translate by xt/yt/zt

    T = 1 0 0 xt
        0 1 0 yt
        0 0 1 zt
        0 0 0 1

rotation matrix into coordinate system given by 3 vectors
                    x=xx/yx/zx, y=xy/yy/zy, z=xz/yz/zz

    R = xx xy xz 0
        yx yy yz 0
        zx zy zz 0
        0  0  0  1

scaling matrix to scale by xs/ys/zs

    S = xs 0  0  0
        0  ys 0  0
        0  0  zs 0
        0  0  0  1

    inv(T) = 1 0 0 -xt
             0 1 0 -yt
             0 0 1 -zt
             0 0 0 1

    inv(R) = xx yx zx 0
             xy yy zy 0
             xz yz zz 0
             0  0  0  1

    T x = x + xt
      y = y + yt
      z = z + zt
      1 = 1

    R x = xx x + xy y + xz z
      y = yx x + yy y + yz z
      z = zx x + zy y + zz z
      1 = 1

rotate first then translate

    T R = xx xy xz xt
          yx yy yz yt
          zx zy zz zt
          0  0  0  1

    T R x = xx x + xy y + xz z + xt
        y   yx x + yy y + yz z + yt
        z   zx x + zy y + zz z + zt
        1   1

translate first then rotate

    R T = xx xy xz xx xt + xy yt + xz zt
          yx yy yz yx xt + yy yt + yz zt
          zx zy zz zx xt + zy yt + zz zt
          0  0  0  1

scale first then translate

    T S = 1 0 0 xt   xs 0  0  0   xs 0  0  xt
          0 1 0 yt * 0  ys 0  0 = 0  ys 0  yt
          0 0 1 zt   0  0  zs 0   0  0  zs zt
          0 0 0 1    0  0  0  1   0  0  0  1

    T S x = xs * x + xt
        y   ys * y + yt
        z   zs * z + zt
        1   1

translate first then scale

    S T = xs 0  0  0   1 0 0 xt   xs 0  0  xs*xt
          0  ys 0  0 * 0 1 0 yt = 0  ys 0  ys*yt
          0  0  zs 0   0 0 1 zt   0  0  zs zs*zt
          0  0  0  1   0 0 0 1    0  0  0  1

    S T x = xs * x + xs * xt
        y   ys * y + ys * yt
        z   zs * z + zs * zt
        1   1

translate first then arbitrary affine matrix

    A T = A0 A1 A2 A3   1 0 0 xt    A0 A1 A2 A0*xt+A1*yt+A2*zt+A3
          A4 A5 A6 A7 * 0 1 0 yt =  A4 A5 A6 A4*xt+A5*yt+A7*zt+A7
          A8 A9 Aa Ab   0 0 1 zt    A8 A9 Aa A8*xt+A9*yt+Aa*zt+Ab
          0  0  0  1    0 0 0 1     0  0  0  1

scale first then arbitrary affine matrix

    A S = A0 A1 A2 A3   xs 0  0  0   A0*xs A1*ys A2*zs A3
          A4 A5 A6 A7 * 0  ys 0  0 = A4*xs A5*ys A6*zs A7
          A8 A9 Aa Ab   0  0  zs 0   A8*xs A9*ys Aa*zs Ab
          0  0  0  1    0  0  0  1   0     0     0     1 

rotate by an angle around vector 0/0/1

    Ra = +cos -sin 0 0
         +sin +cos 0 0
         0    0    1 0
         0    0    0 1

same but arbitrary affine matrix afterwards

    A Ra = A0*c+A1*s -A0*s+A1*c A2 A3
           A4*c+A5*s -A4*s+A5*c A6 A7
           A8*c+A9*s -A8*s+A9*c Aa Ab
           0         0          0  1

"""
import math
import land.main
import land.buffer

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
    roll). Obviously, we can convert from any form to any other, quaternions
    just have properties which make them easy to use in physics code.
    """
    LandFloat w, x, y, z

static macro SQRT sqrt
static macro COS cos
static macro SIN sin

def land_vector(LandFloat x, y, z) -> LandVector:
    LandVector v = {x, y, z}
    return v

def land_vector_from_array(LandFloat *a) -> LandVector:
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

def land_vector_neg(LandVector v) -> LandVector:
    LandVector r = {-v.x, -v.y, -v.z}
    return r

def land_vector_mul(LandVector v, LandFloat s) -> LandVector:
    LandVector r = {v.x * s, v.y * s, v.z * s}
    return r

def land_vector_flip(LandVector v) -> LandVector:
    return land_vector(-v.x, -v.y, -v.z)

def land_vector_div(LandVector v, LandFloat s) -> LandVector:
    LandVector r  = {v.x / s, v.y / s, v.z / s}
    return r

def land_vector_add(LandVector v, w) -> LandVector:
    LandVector r = {v.x + w.x, v.y + w.y, v.z + w.z}
    return r

def land_vector_add4(LandVector v, w, a, b) -> LandVector:
    LandVector r = {v.x + w.x + a.x + b.x, v.y + w.y + a.y + b.y,
        v.z + w.z + a.z + b.z}
    return r

def land_vector_add8(LandVector v, w, a, b, c, d, e, f) -> LandVector:
    LandVector r = {
        v.x + w.x + a.x + b.x + c.x + d.x + e.x + f.x,
        v.y + w.y + a.y + b.y + c.y + d.y + e.y + f.y,
        v.z + w.z + a.z + b.z + c.z + d.z + e.z + f.z}
    return r

def land_vector_sub(LandVector v, w) -> LandVector:
    LandVector r = {v.x - w.x, v.y - w.y, v.z - w.z}
    return r

def land_vector_lerp(LandVector v, w, LandFloat t) -> LandVector:
    return land_vector_add(v, land_vector_mul(land_vector_sub(w, v), t))

def land_vector_dot(LandVector v, w) -> LandFloat:
    """
    The dot product is a number. The number corresponds to the cosine
    between the two vectors times their lengths. So the angle between the
    vectors would be: angle = acos(v . w / (|v| * |w|)). If the dot product
    is 0, the two vectors conversely are orthogonal. The sign can be used to
    determine which side of a plane a point is on.
    """
    return v.x * w.x + v.y * w.y + v.z * w.z

def land_vector_cross(LandVector v, w) -> LandVector:
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

def land_vector_norm(LandVector v) -> LandFloat:
    """
    Return the norm of the vector.
    """
    return SQRT(land_vector_dot(v, v))

def land_vector_normalize(LandVector v) -> LandVector:
    """
    Return a normalized version of the vector.
    """
    return land_vector_div(v, land_vector_norm(v))

def land_vector_distance(LandVector v1, LandVector v2) -> LandFloat:
    return land_vector_norm(land_vector_sub(v2, v1))

def land_vector_quatmul(LandVector v, LandQuaternion q) -> LandQuaternion:
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

def land_vector_transform(LandVector v, p, r, u, b) -> LandVector:
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

def land_vector_matmul(LandVector v, Land4x4Matrix *m) -> LandVector:
    LandFloat x = m->v[0] * v.x + m->v[1] * v.y + m->v[2] * v.z + m->v[3]
    LandFloat y = m->v[4] * v.x + m->v[5] * v.y + m->v[6] * v.z + m->v[7]
    LandFloat z = m->v[8] * v.x + m->v[9] * v.y + m->v[10] * v.z + m->v[11]
    return land_vector(x, y, z)

def land_vector_backmul3x3(LandVector v, Land4x4Matrix *m) -> LandVector:
    """
    Multiplies with the transpose of the 3x3 portion of the matrix.
    """
    LandFloat x = m->v[0] * v.x + m->v[4] * v.y + m->v[8] * v.z
    LandFloat y = m->v[1] * v.x + m->v[5] * v.y + m->v[9] * v.z
    LandFloat z = m->v[2] * v.x + m->v[6] * v.y + m->v[10] * v.z
    return land_vector(x, y, z)


def land_vector_project(LandVector v, Land4x4Matrix *m) -> LandVector:
    LandFloat x = m->v[0] * v.x + m->v[1] * v.y + m->v[2] * v.z + m->v[3]
    LandFloat y = m->v[4] * v.x + m->v[5] * v.y + m->v[6] * v.z + m->v[7]
    LandFloat z = m->v[8] * v.x + m->v[9] * v.y + m->v[10] * v.z + m->v[11]
    LandFloat w = m->v[12] * v.x + m->v[13] * v.y + m->v[14] * v.z + m->v[15]
    return land_vector(x / w, y / w, z / w)

def land_vector_backtransform(LandVector v, p, r, u, b) -> LandVector:
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

def land_vector_rotate(LandVector v, a, double angle) -> LandVector:
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

def land_vector_reflect(LandVector v, n) -> LandVector:
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

def land_quaternion(LandFloat w, x, y, z) -> LandQuaternion:
    LandQuaternion q = {w, x, y, z}
    return q

def land_quaternion_from_array(LandFloat *f) -> LandQuaternion:
    LandQuaternion q = {f[0], f[1], f[2], f[3]}
    return q

def land_quaternion_to_array(LandQuaternion *q, LandFloat *f):
    f[0] = q->w
    f[1] = q->x
    f[2] = q->y
    f[3] = q->z

def _copy_sign(double x, double y) -> double:
    if x > 0:
        if y > 0: return x
        return -x
    if y > 0:
        return -x
    return x

def land_quaternion_from_vectors(LandVector x, y, z) -> LandQuaternion:
    double m00 = x.x
    double m01 = y.x
    double m02 = z.x
    double m10 = x.y
    double m11 = y.y
    double m12 = z.y
    double m20 = x.z
    double m21 = y.z
    double m22 = z.z

    LandQuaternion q
    q.w = sqrt( max( 0, 1 + m00 + m11 + m22 ) ) / 2
    q.x = sqrt( max( 0, 1 + m00 - m11 - m22 ) ) / 2
    q.y = sqrt( max( 0, 1 - m00 + m11 - m22 ) ) / 2
    q.z = sqrt( max( 0, 1 - m00 - m11 + m22 ) ) / 2
    q.x = _copy_sign( q.x, m21 - m12 )
    q.y = _copy_sign( q.y, m02 - m20 )
    q.z = _copy_sign( q.z, m10 - m01 )

    return q

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

def land_quaternion_combine(LandQuaternion qa, LandQuaternion qb) -> LandQuaternion:

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

def land_quaternion_4x4_matrix(LandQuaternion q) -> Land4x4Matrix:
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

def land_4x4_matrix_mul(Land4x4Matrix a, Land4x4Matrix b) -> Land4x4Matrix:
    """
    This multiplies two matrices:

    result = a b

    When used with 3D transformations, the result has the same effect as first
    applying b, then a. For example:

    v = land_vector(1, 0, 0)
    a = land_4x4_matrix_scale(10, 1, 1)
    b = land_4x4_matrix_translate(10, 0, 0)

    # This means first b then a, so v is first translated to 1+10=11, then
    # scaled to 110.
    land_vector_matmul(v, land_4x4_matrix_mul(a, b))

    # This means v is first scaled to 1*10=10, then translated to 20.
    land_vector_matmul(v, land_4x4_matrix_mul(b, a))

    In words, result[row,column] = a[row,...] * b[...,column].
    
    """
    Land4x4Matrix m
    for int i in range(4):
        for int j in range(4):
            LandFloat x = 0
            for int k in range(4):
                x += a.v[i * 4 + k] * b.v[k * 4 + j]
            m.v[i * 4 + j] = x
    return m

def land_4x4_matrix_scale(LandFloat x, y, z) -> Land4x4Matrix:
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

def land_4x4_matrix_skew(LandFloat xy, xz, yx, yz, zx, zy) -> Land4x4Matrix:
    Land4x4Matrix m
    m.v[0] = 1
    m.v[1] = xy
    m.v[2] = xz
    m.v[3] = 0
    m.v[4] = yx
    m.v[5] = 1
    m.v[6] = yz
    m.v[7] = 0
    m.v[8] = zx
    m.v[9] = zy
    m.v[10] = 1
    m.v[11] = 0
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

def land_4x4_matrix_rotate(LandFloat x, y, z, angle) -> Land4x4Matrix:
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

def land_4x4_matrix_identity() -> Land4x4Matrix:
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

def land_4x4_matrix_translate(LandFloat x, y, z) -> Land4x4Matrix:
    """
    T = 1 0 0 xt
        0 1 0 yt
        0 0 1 zt
        0 0 0 1
    """
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

def land_4x4_matrix_perspective(LandFloat left, bottom, nearz,
        right, top, farz) -> Land4x4Matrix:
    Land4x4Matrix m
    LandFloat w = right - left
    LandFloat h = top - bottom
    LandFloat depth = farz - nearz
    LandFloat cx = (right + left) / 2
    LandFloat cy = (bottom + top) / 2
    LandFloat cz = (farz + nearz) / 2

    m.v[0] = 2 * nearz / w
    m.v[1] = 0
    m.v[2] = 2 * cx / w
    m.v[3] = 0
    m.v[4] = 0
    m.v[5] = 2 * nearz / h
    m.v[6] = 0
    m.v[7] = 2 * cy / h
    m.v[8] = 0
    m.v[9] = 0
    m.v[10] = -2 * cz / depth
    m.v[11] = farz * nearz * -2 / depth
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = -1
    m.v[15] = 0
    return m

# note: "near" and "far" are keywords in certain windows compilers
def land_4x4_matrix_orthographic(LandFloat left, top, nearz,
        right, bottom, farz) -> Land4x4Matrix:
    """
    Orthographic means no projection so this would be just an identity matrix.
    But as convenience this scales and translates to fit into the
    left/top/right/bottom rectangle and also scales depth.

    The point at (left, top, near) will end up at (-1, -1, -1) and the point
    at (right, bottom, far) will end up at (1, 1, 1).

    O = S(2/w, 2/h, 2/d) T(-cx, -cy, -cz)

    O = 2/w 0   0   2/w*-cx
        0   2/h 0   2/h*-cy
        0   0   2/d 2/d*-cz
        0   0   0   1

    O x = 2/w*(x-cx)
      y   2/h*(y-cy)
      z   2/d*(z-cz)
      1   1

    inv(O) = inv(T) inv(S) = w/2 0   0   cx
                             0   h/2 0   cy
                             0   0   d/2 cz
                             0   0   0   1

    O inv(O) = 1 0 0 0
               0 1 0 0
               0 0 1 0
               0 0 0 1
        
    """
    Land4x4Matrix m
    LandFloat w = right - left
    LandFloat h = bottom - top
    LandFloat depth = farz - nearz
    LandFloat cx = (right + left) / 2
    LandFloat cy = (bottom + top) / 2
    LandFloat cz = (farz + nearz) / 2
    
    m.v[0] = 2 / w
    m.v[1] = 0
    m.v[2] = 0
    m.v[3] = 2 / w * -cx
    m.v[4] = 0
    m.v[5] = 2 / h
    m.v[6] = 0
    m.v[7] = 2 / h * -cy
    m.v[8] = 0
    m.v[9] = 0
    m.v[10] = 2 / depth
    m.v[11] = 2 / depth * -cz
    m.v[12] = 0
    m.v[13] = 0
    m.v[14] = 0
    m.v[15] = 1
    return m

def land_4x4_matrix_from_vectors(LandVector *p, *r, *u, *b) -> Land4x4Matrix:
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

def land_4x4_matrix_inverse_from_vectors(LandVector *p, *r, *u, *b) -> Land4x4Matrix:
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

def land_4x4_matrix_get_right(Land4x4Matrix *m) -> LandVector:
    return land_vector(m.v[0], m.v[4], m.v[8])

def land_4x4_matrix_get_up(Land4x4Matrix *m) -> LandVector:
    return land_vector(m.v[1], m.v[5], m.v[9])

def land_4x4_matrix_get_back(Land4x4Matrix *m) -> LandVector:
    return land_vector(m.v[2], m.v[6], m.v[10])

def land_4x4_matrix_get_position(Land4x4Matrix *m) -> LandVector:
    return land_vector(m.v[3], m.v[7], m.v[11])

def land_4x4_matrix_set_position(Land4x4Matrix *m, LandVector p):
    m.v[3] = p.x
    m.v[7] = p.y
    m.v[11] = p.z

def land_quaternion_normalize(LandQuaternion *q) -> double:
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
    return n

def land_quaternion_slerp(LandQuaternion qa, qb, double t) -> LandQuaternion:
    """
    Given two quaternions, interpolate a quaternion in between. If t is 0
    this will return qa, if t is 1 it will return qb.

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

    double theta = acos(c)

    double s = sin(theta)

    double fs = sin((1 - t) * theta) / s
    double ts = sin(t * theta) / s

    q.w = qa.w * fs + qb.w * ts
    q.x = qa.x * fs + qb.x * ts
    q.y = qa.y * fs + qb.y * ts
    q.z = qa.z * fs + qb.z * ts

    return q

def land_quaternion_towards(LandQuaternion qa, qb, double av) -> LandQuaternion:
    LandQuaternion q
    double c = qa.w * qb.w + qa.x * qb.x + qa.y * qb.y + qa.z * qb.z

    if c < 0:
        c = -c
        qb.w = -qb.w
        qb.x = -qb.x
        qb.y = -qb.y
        qb.z = -qb.z

    double theta = acos(c)

    double s = sin(theta)

    double t = 0.01
    if theta > av and theta > t:
        t = av / theta

    double fs = sin((1 - t) * theta) / s
    double ts = sin(t * theta) / s

    q.w = qa.w * fs + qb.w * ts
    q.x = qa.x * fs + qb.x * ts
    q.y = qa.y * fs + qb.y * ts
    q.z = qa.z * fs + qb.z * ts

    return q

def land_4x4_matrix_to_string(Land4x4Matrix *m) -> LandBuffer *:
    LandBuffer *b = land_buffer_new()
    for int i in range(16):
        land_buffer_addf(b, "%-5.2f%s", m.v[i],
            i % 4 == 3 ? "\n" : " ")
    return b
