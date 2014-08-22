"""
Simple helper object for maintaining a vertex/fragment shader combination
with GLSL.
"""
static import log
static import mem
import allegro5.a5_opengl

class LandGLSLShader:
    GLuint vertex_shader
    GLuint fragment_shader
    GLuint program_object

static def shader_setup(LandGLSLShader *self,
        char const *name,
        char const *vertex_glsl,
        char const *fragment_glsl):

    self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(self.vertex_shader, 1, &vertex_glsl, NULL)
    glShaderSource(self.fragment_shader, 1, &fragment_glsl, NULL)

    glCompileShader(self.vertex_shader)
    glCompileShader(self.fragment_shader)

    GLint success
    glGetShaderiv(self.vertex_shader, GL_COMPILE_STATUS, &success);
    if True:
        int size
        glGetShaderiv(self.vertex_shader, GL_INFO_LOG_LENGTH, &size);
        char error[size]
        glGetShaderInfoLog(self.vertex_shader, size, &size, error);
        if size:
            land_log_message("%s: Vertex Shader %s:\n%s\n", name,
                success ? "Warning" : "Error", error)

    glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS, &success);
    if True:
        int size
        glGetShaderiv(self.fragment_shader, GL_INFO_LOG_LENGTH, &size);
        char error[size]
        glGetShaderInfoLog(self.fragment_shader, size, &size, error);
        if size:
            land_log_message("%s: Fragment Shader %s:\n%s\n", name,
                success ? "Warning" : "Error", error)

    self.program_object = glCreateProgram()
    glAttachShader(self.program_object, self->fragment_shader)
    glAttachShader(self.program_object, self->vertex_shader)

    glLinkProgram(self.program_object)

    glGetProgramiv(self.program_object, GL_LINK_STATUS, &success);
    if True:
        int size
        glGetProgramiv(self.program_object, GL_INFO_LOG_LENGTH, &size)
        char error[size]
        glGetProgramInfoLog(self.program_object, size, &size, error)
        if size:
            land_log_message("%s: Shader Link Error:\n%s\n", name, error)

static def shader_cleanup(LandGLSLShader *self):
    if self.program_object:
        glDeleteProgram(self.program_object)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

LandGLSLShader *def land_glsl_shader_new(char const *name,
        char const *vertex_glsl,
        char const *fragment_glsl):
    LandGLSLShader *self; land_alloc(self)
    shader_setup(self, name, vertex_glsl, fragment_glsl)
    return self

def land_glsl_shader_destroy(LandGLSLShader *self):
    shader_cleanup(self)
    land_free(self)

