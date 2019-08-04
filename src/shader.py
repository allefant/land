class LandShader:
    char* name

static import allegro5.a5_shader

global char const * land_sample_vertex_shader = """
attribute vec4 al_pos;
attribute vec4 al_color;
attribute vec2 al_texcoord;
uniform mat4 al_projview_matrix;
uniform bool al_use_tex_matrix;
uniform mat4 al_tex_matrix;
varying vec4 varying_color;
varying vec2 varying_texcoord;
void main()
{
  varying_color = al_color;
  if (al_use_tex_matrix) {
    vec4 uv = al_tex_matrix * vec4(al_texcoord, 0, 1);
    varying_texcoord = vec2(uv.x, uv.y);
  }
  else
    varying_texcoord = al_texcoord;
  gl_Position = al_projview_matrix * al_pos;
}
"""

global char const * land_sample_fragment_shader = """
#ifdef GL_ES
precision lowp float;
#endif
uniform sampler2D al_tex;
uniform bool al_use_tex;
varying vec4 varying_color;
varying vec2 varying_texcoord;
void main()
{
  vec4 c;
  if (al_use_tex)
    c = varying_color * texture2D(al_tex, varying_texcoord);
  else
    c = varying_color;
  if (c.a < 0.01) discard;
  else gl_FragColor = c;
}
"""

def land_shader_new(char const *name,
        char const *vertex_glsl,
        char const *fragment_glsl) -> LandShader *:
    LandShader *self
    self = platform_shader_new(name, vertex_glsl, fragment_glsl)
    return self

def land_shader_destroy(LandShader *self):
    platform_shader_destroy(self)
   

