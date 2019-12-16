import land.buffer
import land.shader
static import land.mem
static import land.log
static import global allegro5.allegro5
static import global allegro5.allegro_primitives
static import global assert, math

class LandShaderPlatform:
    LandShader super
    ALLEGRO_SHADER *a5

def platform_shader_new(
        char const *name,
        char const *vertex_glsl,
        char const *fragment_glsl) -> LandShader*:

    LandShaderPlatform *self; land_alloc(self)
    self.super.name = land_strdup(name)
    self.a5 = al_create_shader(ALLEGRO_SHADER_GLSL)

    if vertex_glsl:
        al_attach_shader_source(self.a5, ALLEGRO_VERTEX_SHADER, vertex_glsl)

    if fragment_glsl:
        al_attach_shader_source(self.a5, ALLEGRO_PIXEL_SHADER, fragment_glsl)

    if not al_build_shader(self.a5):
        land_log_message("Shader build error: %s\n", name)

    if not al_use_shader(self.a5):
        land_log_message("Shader use error: %s\n", name)

    str error = al_get_shader_log(self.a5)
    if error and error[0]:
        land_log_message("Shader log:\n%s\n", error)

    return &self.super

def platform_shader_destroy(LandShader *super):
    land_free(super.name)
    LandShaderPlatform* self = (void *)super
    al_destroy_shader(self.a5)
    land_free(self)

