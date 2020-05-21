import land
import util3d

"""
# About world coordinates

There is no one best world coordinate system.

Classic 2D APIs usually use the x axis to go right and the y axis to go
down. This is the "natural" way the English writing system works and
also how video hardware internally used to represent pixel positions.

 0----x
 |
 |
 y

Mathematicians when plotting a graph usually put the origin in the lower
left corner instead, so the x axis still goes right but the y axis now
goes up.

 y
 |
 |
 0----x

A common 3D coordinate system uses x to point right and y to point up
(like in a math plot). The z axis then goes either into the screen or
towards the viewer. (The into the screen version is sometimes called
"left-handed", since the first three fingers of your left hand
at right angles would now represent the x, y, z axes - and the towards
the viewer one "right-handed").

 left-handed    right-handed
 y              y
 | z            |
 |/             |
 0----x         0----x
               /
              z
         
The coordinate system used by Land evolved from games that usually are
backed by a 2D map. This map uses x/y coordinates. When changing from
map coordinates to 3D world coordinates it was less error-prone to let
the x/y from the underlying terrain map keep their meaning. So a point
at x=123/y=456 on the map would be x=123/y=456/z=0 in 3D, at sea level.
So that means x still points to the right as always - but y now runs
along the ground (north/south) and z goes up.

 z
 | y
 |/
 0----x

Now, in the end this will not really matter except for some functions
which implicitly have some kind of "up" direcion, for example
land_camera_get_yaw.

# About camera coordinates

Also note that the world space and camera space are different things.
While the world axes define what a coordinate means, the three axes of
the camera (defined in that world coordinate system) are interpreted
relative to the viewer:

        world space    | camera space
x-axis  east ("right") | right
y-axis  north ("up")   | up
z-axis  up             | towards viewer

So while x/y coordinates are now less confusing betwen 2D and 3D for
a top-down-view map, we introduce some confusion about what is up. The
vector 0/0/1 points straight up. So if the z-axis of a LandCamera is
0/0/1 they look straight down. If the z-axis is 0/0/-1 they look
straight up. If the y-axis of LandCamera is 0/0/1 then the camera up
aligns with world up and we look straight ahead.

"""

class LandCamera:
    # position, right, back, up
    LandVector p, x, y, z
    LandFloat zoom

def land_camera_to_string(LandCamera *self) -> char *:
    """
    Free the returned string with land_free!
    """
    LandBuffer *b = land_buffer_new()
    LandVector *p = &self.p
    LandVector *x = &self.x
    LandVector *y = &self.y
    LandVector *z = &self.z
    land_buffer_addf(b, "%.3f %.3f %.3f ", p.x, p.y, p.z)
    land_buffer_addf(b, "%.3f %.3f %.3f ", x.x, x.y, x.z)
    land_buffer_addf(b, "%.3f %.3f %.3f ", y.x, y.y, y.z)
    land_buffer_addf(b, "%.3f %.3f %.3f ", z.x, z.y, z.z)
    land_buffer_addf(b, "%.3f", self.zoom)
    return land_buffer_finish(b)

def land_camera_from_string(LandCamera *self, char const *s):
    LandVector *p = &self.p
    LandVector *x = &self.x
    LandVector *y = &self.y
    LandVector *z = &self.z
    sscanf(s, "%lg %lg %lg "
        "%lg %lg %lg "
        "%lg %lg %lg "
        "%lg %lg %lg"
        "%lg",
        &p.x, &p.y, &p.z,
        &x.x, &x.y, &x.z,
        &y.x, &y.y, &y.z,
        &z.x, &z.y, &z.z,
        &self.zoom
        )

def land_camera_new -> LandCamera*:
    LandCamera* self
    land_alloc(self)
    land_camera_init(self)
    return self

def land_camera_init(LandCamera *c):
    memset(c, 0, sizeof *c)
    c.x.x = 1
    c.y.y = 1
    c.z.z = 1

LandCamera def land_camera_identity():
    LandCamera c
    land_camera_init(&c)
    return c

def land_camera_change_freely(LandCamera *self, float x, y, z):
    """
    Rotate the camera orientation by the given angles around its local
    x, y and z axes.
    """
    LandVector xaxis = self.x
    self.x = land_vector_rotate(self.x, xaxis, x)
    self.y = land_vector_rotate(self.y, xaxis, x)
    self.z = land_vector_rotate(self.z, xaxis, x)
    
    LandVector yaxis = self.y
    self.x = land_vector_rotate(self.x, yaxis, y)
    self.y = land_vector_rotate(self.y, yaxis, y)
    self.z = land_vector_rotate(self.z, yaxis, y)

    LandVector zaxis = self.z
    self.x = land_vector_rotate(self.x, zaxis, z)
    self.y = land_vector_rotate(self.y, zaxis, z)
    self.z = land_vector_rotate(self.z, zaxis, z)

def land_camera_change_locked(LandCamera *self, float x, z):
    """
    Rotate the camera around its local x axis by the given x angle and
    around world z by the given z angle.
    """
    LandVector xaxis = self.x
    self.x = land_vector_rotate(self.x, xaxis, x)
    self.y = land_vector_rotate(self.y, xaxis, x)
    self.z = land_vector_rotate(self.z, xaxis, x)
    
    LandVector zaxis = land_vector(0, 0, 1)
    self.x = land_vector_rotate(self.x, zaxis, z)
    self.y = land_vector_rotate(self.y, zaxis, z)
    self.z = land_vector_rotate(self.z, zaxis, z)

def land_camera_change_locked_constrained(LandCamera *self, float x, z, min_x, max_x):
    """
    Like land_camera_change_locked but limit the maximum x angle
    against the global z axis.
    """
    LandVector zaxis = land_vector(0, 0, 1)
    
    double angle = land_camera_get_pitch(self)

    if angle + x < min_x: x = min_x - angle
    if angle + x > max_x: x = max_x - angle

    LandVector xaxis = self.x
    self.x = land_vector_rotate(self.x, xaxis, x)
    self.y = land_vector_rotate(self.y, xaxis, x)
    self.z = land_vector_rotate(self.z, xaxis, x)
    
    self.x = land_vector_rotate(self.x, zaxis, z)
    self.y = land_vector_rotate(self.y, zaxis, z)
    self.z = land_vector_rotate(self.z, zaxis, z)

def land_camera_get_pitch(LandCamera *self) -> LandFloat:
    """
    Get "how much the camera points up", any roll or yaw is ignored.
         Z
     \z.z|     y
      \  |    /
       \ |  /  y.z
        \|/________Y
        X
    """
    return -atan2(self.y.z, self.z.z)

def land_camera_get_roll(LandCamera *self) -> LandFloat:
    """
    get rotation around y (back)
       X
       |
       |    x  z.x
       |  / .
       |/___.____Z
      Y
    """
    #LandFloat xz = sqrt(self.x.x * self.x.x + self.x.z * self.x.z)
    #return asin(self.x.z / xz)
    return -atan2(self.z.x, self.z.z)

def land_camera_get_yaw(LandCamera *self) -> LandFloat:
    """
    Get rotation around world 0/0/1 (up) - we ignore any roll completey,
    our yaw is derived from just the back (z) vector.
       Y
       |   y
       |  /
       | /
       |/________X
      Z

    A return of 0 means looking along 0/1/0. A return of pi/2 means
    looking along 1/0/0.
    """
    return atan2(self.z.x, self.z.y)

def land_camera_get_up_down(LandCamera *self) -> LandFloat:
    """
    Get rotation around world 0/1/0 (north).
    """
    return atan2(self.y.x, self.y.y)

def land_camera_set_yaw(LandCamera *self, LandFloat a):
    self.x = land_vector(cos(-a), sin(-a), 0)
    self.z = land_vector(0, 0, 1)
    # z = x × y
    # x = y × z
    # y = z × x
    self.y = land_vector_cross(self.z, self.x)

def land_camera_translate(LandCamera *self, LandVector v):
    self.p = land_vector_add(self.p, v)

def land_camera_move(LandCamera *self, float x, y, z):
    land_vector_iadd(&self.p, land_vector_mul(self.x, x))
    LandVector up = land_vector(0, 0, 1)
    LandVector back = land_vector_cross(self.x, up)
    back = land_vector_normalize(back)
    land_vector_iadd(&self.p, land_vector_mul(back, -y))
    land_vector_iadd(&self.p, land_vector_mul(up, z))

def land_camera_shift(LandCamera *self, float x, y):
    LandVector xv = land_vector_normalize(land_vector(self.x.x, self.x.y, 0))
    LandVector yv = land_vector_normalize(land_vector(self.y.x, self.y.y, 0))
    yv = land_vector_mul(yv, 1 + sin(fabs(self.y.z)))
    land_vector_iadd(&self.p, land_vector_mul(xv, x))
    land_vector_iadd(&self.p, land_vector_mul(yv, y))

def land_camera_look_into(LandCamera *self, float dx, dy):
    """
    Change the camera to look into the given dx/dy direction, with
    z going straight up.
    """
    double d = sqrt(dx * dx + dy * dy)
    if d < 0.0001:
        return
    self.y = land_vector(dx / -d, dy / -d, 0)
    self.z = land_vector(0, 0, 1)
    self.x = land_vector_cross(self.y, self.z)

def land_camera_warp(LandCamera *self, float x, y, z):
    self.p.x = x
    self.p.y = y
    self.p.z = z

def land_camera_matrix(LandCamera *camera) -> Land4x4Matrix:
    Land4x4Matrix m = land_4x4_matrix_inverse_from_vectors(
        &camera.p, &camera.x, &camera.y, &camera.z)

    # apply zoom
    LandFloat s = pow(2, camera.zoom)
    for int i in range(8):
        m.v[i] *= s

    return m

def land_camera_get_scale(LandCamera *camera) -> LandFloat:
    return pow(2, camera.zoom)

def land_camera_scale(LandCamera *camera, float scale):
    camera.zoom = log2(scale)

def land_camera_forward_matrix(LandCamera *camera) -> Land4x4Matrix:
    Land4x4Matrix m = land_4x4_matrix_from_vectors(
        &camera.p, &camera.x, &camera.y, &camera.z)
    return m

def land_camera_forward_matrix_replace_position(LandCamera *camera, LandVector *pos) -> Land4x4Matrix:
    Land4x4Matrix m = land_4x4_matrix_from_vectors(
        pos, &camera.x, &camera.y, &camera.z)
    return m

def land_camera_init_from_matrix(LandCamera *camera, Land4x4Matrix matrix):
    LandFloat *v = matrix.v
    camera.x = land_vector_normalize(land_vector(v[0], v[1], v[2]))
    camera.y = land_vector_normalize(land_vector(v[4], v[5], v[6]))
    camera.z = land_vector_normalize(land_vector(v[8], v[9], v[10]))
    camera.p = land_vector(v[3], v[7], v[11])

def land_camera_get_on_screen_position(LandCamera* cam, LandVector pos) -> LandVector:
    LandFloat s = pow(2, cam.zoom)
    LandVector t = land_vector_transform(pos, cam.p, cam.x, cam.y, cam.z)
    return land_vector(t.x * s, t.y * s, 0)

def _test(str name, LandCamera cam, double result, expected):
    double epsilon = 0.000001
    double differ = fabs(result - expected)
    if differ < epsilon:
        print("OK %s", name)
    else:
        print("FAIL %s", name)
        print("expected %f but got %f", expected, result)
        print("p: % .3f % .3f % .3f", cam.p.x, cam.p.y, cam.p.z)
        print("x: % .3f % .3f % .3f", cam.x.x, cam.x.y, cam.x.z)
        print("y: % .3f % .3f % .3f", cam.y.x, cam.y.y, cam.y.z)
        print("z: % .3f % .3f % .3f", cam.z.x, cam.z.y, cam.z.z)

def land_camera_tests:
    LandCamera cam

    cam = land_camera_identity()
    _test("pitch", cam, land_camera_get_pitch(&cam), 0)
    land_camera_change_freely(&cam, pi / 2, 0, 0)
    _test("pitch2", cam, land_camera_get_pitch(&cam), pi / 2)
    land_camera_change_freely(&cam, pi, 0, 0)
    _test("pitch3", cam, land_camera_get_pitch(&cam), -pi / 2)

    cam = land_camera_identity()
    land_camera_change_freely(&cam, pi * 3 / 4, 0, 0)
    _test("pitch4", cam, land_camera_get_pitch(&cam), pi * 3 / 4)

    cam = land_camera_identity()
    _test("roll", cam, land_camera_get_roll(&cam), 0)
    land_camera_change_freely(&cam, 0, pi / 2, 0)
    _test("roll2", cam, land_camera_get_roll(&cam), pi / 2)
    land_camera_change_freely(&cam, 0, pi, 0)
    _test("roll3", cam, land_camera_get_roll(&cam), -pi / 2)
    land_camera_change_freely(&cam, 0, -pi / 4, 0)
    _test("roll4", cam, land_camera_get_roll(&cam), -pi * 3 / 4)

    cam = land_camera_identity()
    _test("yaw0", cam, land_camera_get_yaw(&cam), 0)
    for int i in range(8):
        char yaw[10]
        sprintf(yaw, "yaw%d", 1 + i)
        float exp = 2 * pi * i / 8 - pi
        if exp < -pi: exp += 2 * pi
        cam = land_camera_identity()
        land_camera_change_freely(&cam, -pi / 2, i * 2 * pi / 8, 0)
        _test(yaw, cam, land_camera_get_yaw(&cam), exp)
    
