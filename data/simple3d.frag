#version 100
#ifdef GL_ES
precision lowp float;
#endif

uniform sampler2D al_tex;
uniform bool al_use_tex;
uniform bool al_alpha_test;
uniform int al_alpha_func;
uniform float al_alpha_test_val;
varying vec4 varying_color;
varying vec2 varying_texcoord;
varying float shade;
varying float fog;

bool alpha_test_func(float x, int op, float compare);

void main() {
    vec4 c;
    if (al_use_tex)
        c = varying_color * texture2D(al_tex, varying_texcoord);
    else
        c = varying_color;
    c.r *= shade;
    c.g *= shade;
    c.b *= shade;
    c.r = 0.7f * fog + c.r * (1.f - fog);
    c.g = 0.8f * fog + c.g * (1.f - fog);
    c.b = 0.9f * fog + c.b * (1.f - fog);
    if (!al_alpha_test || alpha_test_func(c.a, al_alpha_func, al_alpha_test_val))
        gl_FragColor = c;
    else
        discard;
}

bool alpha_test_func(float x, int op, float compare) {
   // Note: These must be aligned with the ALLEGRO_RENDER_FUNCTION enum values.
  if (op == 0) return false; // ALLEGRO_RENDER_NEVER
  else if (op == 1) return true; // ALLEGRO_RENDER_ALWAYS
  else if (op == 2) return x < compare; // ALLEGRO_RENDER_LESS
  else if (op == 3) return x == compare; // ALLEGRO_RENDER_EQUAL
  else if (op == 4) return x <= compare; // ALLEGRO_RENDER_LESS_EQUAL
  else if (op == 5) return x > compare; // ALLEGRO_RENDER_GREATER
  else if (op == 6) return x != compare; // ALLEGRO_RENDER_NOT_EQUAL
  else if (op == 7) return x >= compare; // ALLEGRO_RENDER_GREATER_EQUAL
  return false;
}
