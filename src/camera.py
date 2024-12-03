import land
import util3d

"""
# About world coordinates

There is no one best world coordinate system.

Classic 2D APIs usually use the x axis to go right and the y axis to go
down. This is the "natural" way the English writing system works and
also how old video hardware internally used to represent pixel positions.

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
land_camera_get_yaw. When you place a 3D model at 1/2/3 it will always
end up at 1/2/3 - the only time the coordinate system matters is when
you want to for example know what is "up" and what is "down".

# projection matrix

Camera coordinates work differently. In OpenGL, normalized camera space
is the x/y square from -1/-1 to 1/1 and the z coordinate is depth,
normally pointing towards the viewer.

The projection matrix is responsible for translating coordinates
of all the triangles into camera coordinates. In the most simple case
of orhthographic projection simply by projecting each vertex onto the
camera plane - defined by its position and right and up vectors.

land_projection() can be used to set the projection matrix

# modelview matrix

There is now one piece missing - if we have a world coordinate x/y/z
and we want to know the OpenGL camera space position of it - we need
an actual "camera". A position somewhere in world coordinates and a
direction we are looking at. Most often this is called the "modelview
matrix". land_camera_matrix() will convert a LandCamera into a 4x4
matrix to use for that.

# Local coordinates

There is one additional use case of cameras, which is for local object
coordinates. For example to store the position and orientation of an
airplane. This is the same as the modelview camera, just instead of
storing the position and direction the world is viewed from it stores
the position and orientation of an object. When rendering a 3D model
it can be useful to multiply its local camera with the view camera to
get a translated/rotated/scaled/etc. version of it.

# camera space variant A and B

For both the actual camera and object cameras there is multiple ways to
interpret the orientation axes.

We are mostly doing this in two different ways in Land, variant A and B:

        world space    | camera space A | camera space B
x-axis  east ("right") | right          | left (i.e. right from front)
y-axis  north ("up")   | up             | back
z-axis  up             | back           | up

viewed from front:

variant A:
        y   z                
        |  /
       ,,,
      (o o)
 x -- __|__
       / \

variant B:
        z   y                
        |  /
       ,,,
      (o o)
      __|__ -- x
       / \

to convert from B to A:
    x' = -x
    y' = z
    z' = y

## camera space variant A

Here we mimic OpenGL camera space. The camera can be both a render
camera and orientation, where the z axis now is a back vector. To move
forward in the direction the camera is looking, just add negative z.

The vector 0/0/1 still points straight up in world coordinates.
So if the z-axis of the player camera is 0/0/1 they look straight down.
If the z-axis is 0/0/-1 they look straight up. If the y-axis of
LandCamera is 0/0/1 then the camera up aligns with world up and we look
straight ahead.

The one confusion with this is that the local coordinate system now
seems rotated by 90°. For example an airplane standing on the ground. In
world coordinates the nose will point along an axis in the x/y plane
while z will go up.

## camera space variant B

In some games we use a local camera where the z axis goes up, so
x=1/0/0,y=0/1/0,z=0/0/1 means the player is standing upright and looking
south. This can be the least confusing since the up vector both times
is z=0/0/1.

To move the player forward we need to add negative y.

"""

class LandCamera:
    # position, right, back, up
    LandVector p, x, y, z
    LandFloat zoom
    bool z_is_up with 1 # "variant B"

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

def land_camera_rotate_axis(LandCamera *self, LandVector axis, float a):
    self.x = land_vector_rotate(self.x, axis, a)
    self.y = land_vector_rotate(self.y, axis, a)
    self.z = land_vector_rotate(self.z, axis, a)
    
def land_camera_change_freely(LandCamera *self, float x, y, z):
    """
    Rotate the camera orientation by the given angles around its local
    x, y and z axes.
    """
    land_camera_rotate_axis(self, self.x, x)
    land_camera_rotate_axis(self, self.y, y)
    land_camera_rotate_axis(self, self.z, z)

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
    0 means the camera is level.
         Z
     \z.z|     y
      \  |    /
       \ |  /  y.z
        \|/________Y
        X
    """
    # self.z is the "back" vector
    # self.z.z is how much up it goes, from -1 to 0 to 1
    # if z.z==0 we are at a horizontal level and pitch is 0 (sin(0) == 0°)
    # (or 180° if we are upside down)
    # the identity matrix means we look straight down (back vector is 0/0/1)
    if self.z_is_up: return -atan2(self.y.z, self.z.z)
    else: return atan2(self.z.z, self.y.z)

def land_camera_get_roll(LandCamera *self) -> LandFloat:
    """
    get rotation around z (back)
       X
       |
       |    x  z.x
       |  / .
       |/___.____Z
      Y
    """
    # self.x is the "right" vector
    # self.x.z is how far the right vector goes up, if it is 0 roll is
    # 0 (or 180° if rolled all around)
    if self.z_is_up: return atan2(self.x.z, self.z.z)
    else: return atan2(self.x.z, self.y.z)

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
    if self.z_is_up: return atan2(self.y.x, self.y.y)
    else: return atan2(self.z.x, self.z.y)

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

def land_camera_scroll(LandCamera *self, float x, y):
    #              /
    #        U.   /
    #       /   °/
    #      /    /    V
    #     /α   /    /
    #----A----/----B-----
    #
    # When the mouse moves U the camera needs to move A.
    # U/A=sin(α)
    LandVector xv = land_vector_normalize(land_vector(self.x.x, self.x.y, 0))
    LandVector yv = land_vector_normalize(land_vector(self.y.x, self.y.y, 0))
    LandFloat alphasin = self.z.z
    yv = land_vector_mul(yv, 1 / alphasin)
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

def land_camera_look_to(LandCamera *self, float x, y, z):
    float dx = x - self.p.x
    float dy = y - self.p.y
    float dz = z - self.p.z
    double d = sqrt(dx * dx + dy * dy + dz * dz)
    if d < 0.0001:
        return
    if self.z_is_up:
        self.y = land_vector(dx / -d, dy / -d, dz / -d)
        self.z = land_vector(0, 0, 1)
        self.x = land_vector_normalize(land_vector_cross(self.y, self.z))
        self.z = land_vector_cross(self.x, self.y)
    else:
        self.y = land_vector(dx / -d, dy / -d, dz / -d)
        self.z = land_vector(0, 0, 1)
        self.x = land_vector_normalize(land_vector_cross(self.y, self.z))
        self.z = land_vector_cross(self.x, self.y)

def land_camera_look_to_vector(LandCamera *self, LandVector p):
    land_camera_look_to(self, p.x, p.y, p.z)

def land_camera_warp_vector(LandCamera *self, LandVector v):
    self.p = v
    
def land_camera_warp(LandCamera *self, float x, y, z):
    self.p.x = x
    self.p.y = y
    self.p.z = z

def land_camera_matrix(LandCamera *camera) -> Land4x4Matrix:
    Land4x4Matrix m

    if camera.z_is_up:
        LandVector x = land_vector_mul(camera.x, -1)
        m = land_4x4_matrix_inverse_from_vectors(&camera.p, &x, &camera.z, &camera.y)
    else:
        m = land_4x4_matrix_inverse_from_vectors(&camera.p, &camera.x, &camera.y, &camera.z)

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

def land_debug_camera(LandCamera *cam) -> char*:
    char *s = land_strdup("")
    land_appendln(&s, "pitch %.0f", land_camera_get_pitch(cam) * 180 / pi)
    land_appendln(&s, "yaw %.0f", land_camera_get_yaw(cam) * 180 / pi)
    land_appendln(&s, "roll %.0f", land_camera_get_roll(cam) * 180 / pi)
    land_appendln(&s, "scale %.2f", land_camera_get_scale(cam))
    land_appendln(&s, "p % .2f,% .2f,% .2f", cam.p.x, cam.p.y, cam.p.z)
    land_appendln(&s, "x % .2f,% .2f,% .2f", cam.x.x, cam.x.y, cam.x.z)
    land_appendln(&s, "y % .2f,% .2f,% .2f", cam.y.x, cam.y.y, cam.y.z)
    land_append(&s, "z % .2f,% .2f,% .2f", cam.z.x, cam.z.y, cam.z.z)
    return s

def land_camera_flip(LandCamera *cam):
    cam.x = land_vector_flip(cam.x)
    cam.z = land_vector_flip(cam.z)
