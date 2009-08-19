import global land/land

LandImage *image
LandImage *colored[33]

global int COLORKEY_MAGENTA[20 * 3] = {
    244,154,193,
    63,0,22,
    85,0,42,
    105,0,57,
    123,0,69,
    140,0,81,
    158,0,93,
    177,0,105,
    195,0,116,
    214,0,127,
    236,0,140,
    238,61,150,
    239,91,161,
    241,114,172,
    242,135,182,
    246,173,205,
    248,193,217,
    250,213,229,
    253,233,241}

global float colorkey_colors[33 * 3]

static def read_colors():
    FILE *f = fopen("../../data/playercolors.txt", "rb")
    char str[256]
    int i = 3
    while i < 33 * 3:
        if not fgets(str, sizeof str, f): break
        char *s = str
        colorkey_colors[i++] = strtol(s, &s, 10) / 255.0
        colorkey_colors[i++] = strtol(s, &s, 10) / 255.0
        colorkey_colors[i++] = strtol(s, &s, 10) / 255.0
    fclose(f)

static def init(LandRunner *self):
    read_colors()
    image = land_image_load("../../data/sylph.png")
    int w = land_image_width(image)
    int h = land_image_height(image)
    for int i = 1 while i < 33 with i++:
        colored[i] = land_image_new_from(image, 0, 0, w, h)
        float *rgb = colorkey_colors + i * 3
        land_color(rgb[0], rgb[1], rgb[2], 1)
        land_image_colorize_replace(colored[i], 19, COLORKEY_MAGENTA)

static def tick(LandRunner *self):
    if land_key(LandKeyEscape):
        land_quit()

static def draw(LandRunner *self):
    land_clear(0, 0, 0, 0)
    for int i = 1 while i < 33 with i++:
        float *rgb = colorkey_colors + i * 3
        land_color(rgb[0], rgb[1], rgb[2], 1)
        int x = (i - 1) & 7;
        int y = (i - 1) >> 3;
        land_rectangle(80 * x + 0.5, 80 * y + 0.5,
            80 * x + 80 - 0.5, 80 * y + 80 - 0.5)
        land_image_draw(colored[i], 80 * x + 4, 80 * y + 4)

land_begin_shortcut(80 * 8, 80 * 4, 60, LAND_WINDOWED | LAND_OPENGL,
    init, None, tick, draw, None, None)
