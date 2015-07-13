import allegro5.a5_opengl

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
