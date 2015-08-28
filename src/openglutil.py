import allegro5.a5_opengl
import util3d

def land_opengl_error() -> char const *:
    GLenum e = glGetError()
***scramble
for e in ["GL_NO_ERROR",
    "GL_INVALID_ENUM",
    "GL_INVALID_VALUE",
    "GL_INVALID_OPERATION",
    "GL_INVALID_FRAMEBUFFER_OPERATION",
    "GL_OUT_OF_MEMORY"]:
        parse("""
    if e == {e}: return "{e}"
""".format(e = e))
***
    return "unknown"

def land_4x4_matrix_to_gl_float(Land4x4Matrix m, GLfloat *gl):
    gl[0x0] = m.v[0x0]
    gl[0x1] = m.v[0x4]
    gl[0x2] = m.v[0x8]
    gl[0x3] = m.v[0xc]
    gl[0x4] = m.v[0x1]
    gl[0x5] = m.v[0x5]
    gl[0x6] = m.v[0x9]
    gl[0x7] = m.v[0xd]
    gl[0x8] = m.v[0x2]
    gl[0x9] = m.v[0x6]
    gl[0xa] = m.v[0xa]
    gl[0xb] = m.v[0xe]
    gl[0xc] = m.v[0x3]
    gl[0xd] = m.v[0x7]
    gl[0xe] = m.v[0xb]
    gl[0xf] = m.v[0xf]
