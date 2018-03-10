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
    char* name

static def shader_setup(LandGLSLShader *self,
        char const *name,
        char const *vertex_glsl,
        char const *fragment_glsl):

    if name:
        self.name = land_strdup(name)
    else:
        name = self.name

    if vertex_glsl:
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)

        glShaderSource(self.vertex_shader, 1, &vertex_glsl, NULL)
        glCompileShader(self.vertex_shader)
        
        GLint success
        glGetShaderiv(self.vertex_shader, GL_COMPILE_STATUS, &success);
        land_log_message("%s: Vertex Shader compilation %s.\n", name,
            success ? "succeeded" : "failed")
        if True:
            int size
            glGetShaderiv(self.vertex_shader, GL_INFO_LOG_LENGTH, &size);
            char error[size]
            glGetShaderInfoLog(self.vertex_shader, size, &size, error);
            if size:
                land_log_message("%s: Vertex Shader %s:\n%s\n", name,
                    success ? "Warning" : "Error", error)

    if fragment_glsl:
        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, 1, &fragment_glsl, NULL)
        glCompileShader(self.fragment_shader)

        GLint success
        glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS, &success);
        if True:
            int size
            glGetShaderiv(self.fragment_shader, GL_INFO_LOG_LENGTH, &size);
            char error[size]
            glGetShaderInfoLog(self.fragment_shader, size, &size, error);
            if size:
                land_log_message("%s: Fragment Shader %s:\n%s\n", name,
                    success ? "Warning" : "Error", error)

    if not self.program_object:
        self.program_object = glCreateProgram()

    if self.fragment_shader:
        glAttachShader(self.program_object, self->fragment_shader)
    if self.vertex_shader:
        glAttachShader(self.program_object, self->vertex_shader)

    if self.fragment_shader and self.vertex_shader:
        glLinkProgram(self.program_object)
        GLint success
        glGetProgramiv(self.program_object, GL_LINK_STATUS, &success);
        if True:
            int size
            glGetProgramiv(self.program_object, GL_INFO_LOG_LENGTH, &size)
            char error[size]
            glGetProgramInfoLog(self.program_object, size, &size, error)
            if size:
                land_log_message("%s: Shader Link Error:\n%s\n", name, error)

static def shader_cleanup(LandGLSLShader *self):
    land_free(self.name)
    if self.program_object:
        glDeleteProgram(self.program_object)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

def land_glsl_shader_new(char const *name,
        char const *vertex_glsl,
        char const *fragment_glsl) -> LandGLSLShader *:
    LandGLSLShader *self; land_alloc(self)
    shader_setup(self, name, vertex_glsl, fragment_glsl)
    return self

def land_glsl_shader_new_empty(char const *name) -> LandGLSLShader *:
    LandGLSLShader *self; land_alloc(self)
    shader_setup(self, name, None, None)
    return self

def land_glsl_shader_set_shaders(LandGLSLShader *self,
        char const *vertex_glsl, char const *fragment_glsl):
    shader_setup(self, None, vertex_glsl, fragment_glsl)

def land_glsl_shader_destroy(LandGLSLShader *self):
    shader_cleanup(self)
    land_free(self)

