import global allegro, alleggl, math
import ../array, ../display, ../log, ../exception
static import allegrogl/display, allegrogl/image, allegrogl/font

class LandDisplayAllegroGL:
    LandDisplay super

macro LAND_DISPLAY_ALLEGROGL(_x_) ((LandDisplayAllegroGL *)_x_)

static LandDisplayInterface *vtable

LandDisplayAllegroGL *def land_display_allegrogl_new(int w, h, bpp, hz, flags):
    land_log_message("land_display_allegrogl_new\n")
    LandDisplayAllegroGL *self
    land_alloc(self)
    LandDisplay *super = &self->super
    super->w = w
    super->h = h
    super->bpp = bpp
    super->hz = hz
    super->flags = flags
    super->vt = vtable

    super->clip_x1 = 0
    super->clip_y1 = 0
    super->clip_x2 = w
    super->clip_y2 = h

    super->color_r = 1
    super->color_g = 1
    super->color_b = 1
    super->color_a = 1

    return self

def land_display_allegrogl_set(LandDisplay *super):
    land_log_message("land_display_allegrogl_set\n")
    int mode = GFX_AUTODETECT

    int cd = desktop_color_depth()
    if super->bpp:
        cd = super->bpp

    static int once = 0
    if !once:
        if install_allegro_gl(): land_exception("install_allegro_gl")

        once++

    # We need to reset all references to textures *before* re-creating the
    # OpenGL context, else the texture ids reference wrong textures.
    land_font_allegrogl_unupload()

    allegro_gl_set(AGL_COLOR_DEPTH, cd)
    allegro_gl_set(AGL_SUGGEST, AGL_COLOR_DEPTH)

    allegro_gl_set(AGL_DOUBLEBUFFER, 1)
    allegro_gl_set(AGL_SUGGEST, AGL_DOUBLEBUFFER)

    allegro_gl_set(AGL_SAMPLE_BUFFERS, 0)
    allegro_gl_set(AGL_SUGGEST, AGL_SAMPLE_BUFFERS)

    allegro_gl_set(AGL_SAMPLES, 0)
    allegro_gl_set(AGL_SUGGEST, AGL_SAMPLES)

    allegro_gl_set(AGL_RENDERMETHOD, 1)
    allegro_gl_set(AGL_SUGGEST, AGL_RENDERMETHOD)

    mode = GFX_OPENGL
    if super->flags & LAND_WINDOWED:
        mode = GFX_OPENGL_WINDOWED
    #ifdef GFX_OPENGL_FULLSCREEN
    elif super->flags & LAND_FULLSCREEN:
        mode = GFX_OPENGL_FULLSCREEN
    #endif

    set_color_depth(cd)
    # TODO: seems to have bad effects on some windows machines
    # if super->hz:
    #    request_refresh_rate(super->hz)
    land_log_message(" %s %dx%dx%d %dHz\n",
        super->flags & LAND_FULLSCREEN ? "fullscreen" :
        super->flags & LAND_WINDOWED ? "windowed" : "auto",
        super->w, super->h, cd, super->hz)
    set_gfx_mode(mode, super->w, super->h, 0, 0)
    land_log_message(" gfx mode switch successfull.\n")

    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, SCREEN_W, SCREEN_H, 0, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glClearColor(0, 0, 0, 0)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    land_image_allegrogl_reupload()
    land_font_allegrogl_reupload()

def land_display_allegrogl_flip(LandDisplay *super):
    allegro_gl_flip()

def land_display_allegrogl_rectangle(LandDisplay *super,
    float x, float y, float x_, float y_):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x_, y)
    glVertex2f(x_, y_)
    glVertex2f(x, y_)
    glEnd()

def land_display_allegrogl_filled_rectangle(LandDisplay *super,
    float x, float y, float x_, float y_):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x_, y)
    glVertex2f(x_, y_)
    glVertex2f(x, y_)
    glEnd()

def land_display_allegrogl_filled_circle(LandDisplay *super,
    float x, float y, float x_, float y_):
    float min_side_length = 2
    float max_sides = 32
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_POLYGON)
    float xradius = (x_ - x) * 0.5
    float yradius = (y_ - y) * 0.5
    float xcenter = x + xradius
    float ycenter = y + yradius
    float n = AL_PI / (asin(min_side_length / (2 * xradius)))
    if n > max_sides:
        n = max_sides
    float a = 0
    float ai = AL_PI * 2 / n
    if ai > AL_PI / 4:
        ai = AL_PI / 4

    while a < AL_PI * 2:
        glVertex2f(xcenter + xradius * cos(a), ycenter - yradius * sin(a))
        a += ai

    glEnd(); 

def land_display_allegrogl_circle(LandDisplay *super,
    float x, float y, float x_, float y_):
    float min_side_length = 2
    float max_sides = 32
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINE_LOOP)
    float xradius = (x_ - x) * 0.5
    float yradius = (y_ - y) * 0.5
    float xcenter = x + xradius
    float ycenter = y + yradius
    float n = AL_PI / (asin(min_side_length / (2 * xradius)))
    if n > max_sides:
        n = max_sides
    float a = 0
    float ai = AL_PI * 2 / n
    if ai > AL_PI / 4:
        ai = AL_PI / 4
    while a < AL_PI * 2:
        glVertex2f(xcenter + xradius * cos(a), ycenter + yradius * sin(a))
        a += ai

    glEnd()

def land_display_allegrogl_plot(LandDisplay *super, float x, y):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_POINTS)
    glVertex2f(x + 0.5, y + 0.5)
    glEnd()

def land_display_allegrogl_pick_color(LandDisplay *super, float x, y):
    # could use glReadPixels or somesuch, followed by glColor
    pass

def land_display_allegrogl_filled_polygon(LandDisplay *super, int n,
    float *x, float *y):
    int i
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_POLYGON)
    for i = 0; i < n; i++:
        glVertex2f(x[i], y[i])
    glEnd()

def land_display_allegrogl_line(LandDisplay *super,
    float x, float y, float x_, float y_):
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINES)
    glVertex2f(x, y)
    if super->flags & LAND_CLOSE_LINES:
        # Draw line by one pixel longer, since OpenGL never draws the last pixel.
        float dx = x_ - x
        float dy = y_ - y
        float d = sqrt(dx * dx + dy * dy)
        glVertex2f(x_ + dx / d, y_ + dy / d)

    else:
        glVertex2f(x_, y_)

    glEnd()

def land_display_allegrogl_polygon(LandDisplay *super, int n,
    float *x, float *y):
    int i
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINE_LOOP)
    for i = 0; i < n; i++:
        glVertex2f(x[i], y[i])

    glEnd()

def land_display_allegrogl_color(LandDisplay *super):
    glColor4f(super->color_r, super->color_g, super->color_b, super->color_a)

def land_display_allegrogl_clip(LandDisplay *super):
    if super->clip_off:
        glDisable(GL_SCISSOR_TEST)
    else:
        glEnable(GL_SCISSOR_TEST)

    # If display is split into two columns, like this:
    #
    # clip(0, 0, 5.5, 10)
    # clip(5.5, 0, 10, 10)
    #
    # Then if we just pass this to OpenGL with integer clipping:
    #
    # x = int(0) = 0, w = int(5.5 - 0) = 5
    # x = int(5.5) = 5, w = int(10 - 5.5) = 4
    #
    # Now this means, we get a blank stripe:
    #
    # 00 01 02 03 04 05 06 07 08 09
    # xx xx xx xx xx yy yy yy yy ?? 
    #
    # If we convert to integer and add 1 to the width:
    #
    # x = int(0) = 0, w = 1 + int(5.5) - int(0) = 5
    # x = int(5.5) = 5, w = 1 + int(10) - int(5.5) = 6
    #
    # But, this results in an extra pixel:
    #
    # 00 01 02 03 04 05 06 07 08 09 10
    # xx xx xx xx xx yy yy yy yy yy yy
    #
    # The below seems to be the best compromise:
    #
    # x = int(0) = 0, w = int(5.5) - int(0)) = 5
    # x = int(5.5) = 5, w = int(10) - int(5.5) = 5
    #
    # 00 01 02 03 04 05 06 07 08 09
    # xx xx xx xx xx yy yy yy yy yy 
    #
    # This means, any clipping area not having at least one integer crossing
    # inside will be reduced to nothign.
      
    int x_1 = super->clip_x1
    int y_1 = super->clip_y1
    int x_2 = super->clip_x2
    int y_2 = super->clip_y2

    glScissor(x_1, super->h - y_2, x_2 - x_1, y_2 - y_1)

def land_display_allegrogl_clear(LandDisplay *super, float r, float g, float b, float a):
    glClearColor(r, g, b, a)
    glClear(GL_COLOR_BUFFER_BIT)

def land_display_allegrogl_init(void):
    land_log_message("land_display_allegrogl_init\n")
    land_alloc(vtable)

    vtable->set = land_display_allegrogl_set
    vtable->flip = land_display_allegrogl_flip
    vtable->rectangle = land_display_allegrogl_rectangle
    vtable->filled_rectangle = land_display_allegrogl_filled_rectangle
    vtable->line = land_display_allegrogl_line
    vtable->new_image = land_image_allegrogl_new
    vtable->del_image = land_image_allegrogl_del
    vtable->new_font = land_font_allegrogl_new
    vtable->del_font = land_font_allegrogl_del
    vtable->filled_circle = land_display_allegrogl_filled_circle
    vtable->circle = land_display_allegrogl_circle
    vtable->color = land_display_allegrogl_color
    vtable->clip = land_display_allegrogl_clip
    vtable->clear = land_display_allegrogl_clear
    vtable->plot = land_display_allegrogl_plot
    vtable->polygon = land_display_allegrogl_polygon
    vtable->filled_polygon = land_display_allegrogl_filled_polygon
    vtable->pick_color = land_display_allegrogl_pick_color

def land_display_allegrogl_exit(void):
    land_log_message("land_display_allegrogl_exit\n")
    land_free(vtable)
