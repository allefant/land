import global land/land

LandImage *image
LandImage *image_parts[4]

static LandImage * def create_test_image():
    int w = 100
    int h = 100
    image = land_image_new(w, h)
    int i
    land_set_image_display(image)
    for i = 0 while i < w * h with i++:
        int x = i % w
        int y = i / w
        float red, green, blue
        red = max(0, 1 - (float)x / w - (float)y / h)
        green = max(0, (float)x / w - (float)y / h)
        blue = max(0, (float)y / h - (float)x / w)
        int b
        for b = 1 while b < 8 with b++:
            int mask = (1 << b) - 1
            if ((x & mask) == mask) && y < mask:
                blue = 0
                green = 1
                red = 1

            if ((y & mask) == mask) && x < mask:
                blue = 1
                green = 0
                red = 1


        if x >= w / 2 && y >= h / 2:
            int ix = w * 3 / 4 - x
            int iy = h * 3 / 4 - y
            if ix <= 0:
                ix--
            if iy <= 0:
                iy--
            int iz = max(abs(ix), abs(iy))
            if (iz & 3) == 0:
                blue = 1
                green = 1
                red = 0


        land_color(red, green, blue, 1)
        land_plot(x, y)

    land_unset_image_display()
    return image

static def init(LandRunner *self):
    image = create_test_image()
    image = land_image_load("../../data/land3.png")
    land_image_offset(image, 20, 12)

    int w = land_image_width(image)
    int h = land_image_height(image)

    image_parts[0] = land_image_new_from(image, 0, 0, w / 2, h / 2)
    image_parts[1] = land_image_new_from(image, w / 2, 0, w / 2, h / 2)
    image_parts[2] = land_image_new_from(image, w / 2, h / 2, w / 2, h / 2)
    image_parts[3] = land_image_new_from(image, 0, h / 2, w / 2, h / 2)

static def destroy(LandRunner *self):
    int i
    for i = 0 while i < 4 with i++:
        land_image_del(image_parts[i])
    land_image_del(image)

static def tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

static def draw(LandRunner *self):
    static float angle = 0
    int w = land_image_width(image)
    int h = land_image_height(image)

    static int clip_switch = 0
    clip_switch++

    if clip_switch % 60 == 0:
        if (clip_switch / 60) & 1:
            int cw = land_rand(w / 2, w)
            int ch = land_rand(h / 2, h)
            int cx = land_rand(0, w - cw)
            int cy = land_rand(0, h - ch)

            land_image_clip(image, cx, cy, cx + cw, cy + ch)
    
        else:
            land_image_unclip(image)

    land_clear(0.2, 0, 0, 0)
    land_color(1, 1, 1, 1)
    land_rectangle(10 - 0.5, 10 - 0.5, 10 + land_image_width(image) + 0.5,
        10 + land_image_height(image) + 0.5)
    land_rectangle(8 - 0.5, 8 - 0.5, 12 + land_image_width(image) + 0.5,
        12 + land_image_height(image) + 0.5)

    land_image_draw(image, 10 + 20, 10 + 12)

    land_image_draw_rotated(image, 480, 140, angle)
    land_color(0, 1, 0, 1)
    land_filled_circle(480 - 2, 140 - 2, 480 + 2, 140 + 2)

    float sx = cos(angle + LAND_PI / 4) * 1.5
    float sy = sin(angle + LAND_PI / 4) * 1.5
    land_image_draw_scaled_rotated(image, 480, 300, sx, sy, -sin(angle))
    land_color(0, 1, 0, 1)
    land_filled_circle(480 - 2, 300 - 2, 480 + 2, 300 + 2)

    float s = (cos(angle * 3) + 1) * 10
    land_image_draw(image_parts[0], 40 - s, 240 - s)
    land_image_draw(image_parts[1], 40 + w / 2 + s, 240 - s)
    land_image_draw(image_parts[2], 40 + w / 2 + s, 240 + h / 2 + s)
    land_image_draw(image_parts[3], 40 - s, 240 + h / 2 + s)
    
    #land_image_clip(image, 0, 0, w / 2, h / 2)
    #land_image_draw(image, 40 - s, 240 - s)
    #land_image_clip(image, w / 2, 0, w, h / 2)
    #land_image_draw(image, 40 + s, 240 - s)
    #land_image_clip(image, w / 2, h / 2, w, h)
    #land_image_draw(image, 40 + s, 240 + s)
    #land_image_clip(image, 0, h / 2, w / 2, h)
    #land_image_draw(image, 40 - s, 240 + s)
    #land_image_unclip(image)

    angle += 1.0 * LAND_PI / 180.0
    angle /= LAND_PI * 2
    angle -= floor(angle)
    angle *= LAND_PI * 2

    int x = 50
    int y = 50

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, land_image_opengl_texture(image))

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)

    GLfloat color[4] = { 1, 1, 1, 1 };
    glTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, color);

    glTexEnvf(GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_DOT3_RGB)
    int i
    for i = 0 while i < 2 with i++:
        glTexEnvf(GL_TEXTURE_ENV, GL_SOURCE0_RGB, GL_TEXTURE)
        glTexEnvf(GL_TEXTURE_ENV, GL_OPERAND0_RGB,
            i == 0 ? GL_SRC_COLOR : GL_ONE_MINUS_SRC_COLOR)

        glTexEnvf(GL_TEXTURE_ENV, GL_SOURCE1_RGB, GL_PRIMARY_COLOR)
        glTexEnvf(GL_TEXTURE_ENV, GL_OPERAND1_RGB,
            i == 0 ? GL_SRC_COLOR : GL_ONE_MINUS_SRC_COLOR)

        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(320 - x, 240 - y)
        glTexCoord2f(1, 0)
        glVertex2f(320 + x, 240 - y)
        glTexCoord2f(1, 1)
        glVertex2f(320 + x, 240 + y)
        glTexCoord2f(0, 1)
        glVertex2f(320 - x, 240 + y)
        glEnd()

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

land_begin_shortcut(640, 480, 60, LAND_WINDOWED | LAND_OPENGL,
    init, NULL, tick, draw, NULL, destroy)
