import global land/land

macro TYPES 6

LandImage *image[TYPES][16]
int ticks
int map[32]

class Slot:
    float rgb[3]
    LandImage *frames[16]
    bool flipped
    int anim_start
    int next_time
    int offset

    bool moving
    int pos
    double x, y, tx, ty

global int COLORKEY_MAGENTA[19 * 3] = {
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

Slot slots[33] # 0 is reserved

static def read_colors():
    FILE *f = fopen("../../data/playercolors.txt", "rb")
    char str[256]
    for int i = 1 while i <= 32 with i++:
        if not fgets(str, sizeof str, f): break
        Slot *s = slots + i
        char *sp = str
        s->rgb[0] = strtol(sp, &sp, 10) / 255.0
        s->rgb[1] = strtol(sp, &sp, 10) / 255.0
        s->rgb[2] = strtol(sp, &sp, 10) / 255.0
        s->offset = land_rand(0, 29)
        s->flipped = land_rand(0, 1)
        int xi = (i - 1) & 7
        int yi = (i - 1) >> 3
        s->x = xi * 80
        s->y = yi * 80
        s->pos = i - 1
        map[i - 1] = i
    fclose(f)

static def init(LandRunner *self):
    read_colors()
    image[0][0] = land_image_load("../../data/wesnoth/sylph.png")
    image[0][1] = land_image_load("../../data/wesnoth/sylph-magic.png")
    image[0][2] = image[0][1]
    image[1][0] = land_image_load("../../data/wesnoth/druid.png")
    image[1][1] = land_image_load("../../data/wesnoth/druid-magic-1.png")
    image[1][2] = land_image_load("../../data/wesnoth/druid-magic-2.png")
    image[1][3] = land_image_load("../../data/wesnoth/druid-magic-3.png")
    image[1][4] = land_image_load("../../data/wesnoth/druid-magic-4.png")
    image[1][5] = image[1][3]
    image[1][6] = image[1][2]
    image[1][7] = image[1][1]
    image[2][0] = land_image_load("../../data/wesnoth/shaman.png")
    image[2][1] = land_image_load("../../data/wesnoth/shaman-heal1.png")
    image[2][2] = land_image_load("../../data/wesnoth/shaman-heal2.png")
    image[2][3] = land_image_load("../../data/wesnoth/shaman-heal3.png")
    image[2][4] = land_image_load("../../data/wesnoth/shaman-heal4.png")
    image[2][5] = land_image_load("../../data/wesnoth/shaman-heal5.png")
    image[2][6] = land_image_load("../../data/wesnoth/shaman-heal6.png")
    image[2][7] = land_image_load("../../data/wesnoth/shaman-heal7.png")
    image[2][8] = land_image_load("../../data/wesnoth/shaman-heal8.png")
    image[2][9] = land_image_load("../../data/wesnoth/shaman-heal9.png")
    image[3][0] = land_image_load("../../data/wesnoth/shyde.png")
    image[3][1] = land_image_load("../../data/wesnoth/shyde-healing1.png")
    image[3][2] = land_image_load("../../data/wesnoth/shyde-healing2.png")
    image[3][3] = land_image_load("../../data/wesnoth/shyde-healing3.png")
    image[3][4] = land_image_load("../../data/wesnoth/shyde-healing4.png")
    image[3][5] = land_image_load("../../data/wesnoth/shyde-healing5.png")
    image[3][6] = land_image_load("../../data/wesnoth/shyde-healing6.png")
    image[3][7] = land_image_load("../../data/wesnoth/shyde-healing7.png")
    image[3][8] = land_image_load("../../data/wesnoth/shyde-healing8.png")
    image[3][9] = land_image_load("../../data/wesnoth/shyde-healing9.png")
    image[3][10] = land_image_load("../../data/wesnoth/shyde-healing10.png")
    image[3][11] = land_image_load("../../data/wesnoth/shyde-healing11.png")
    image[3][12] = land_image_load("../../data/wesnoth/shyde-healing12.png")
    image[4][0] = land_image_load("../../data/wesnoth/sorceress.png")
    image[4][1] = land_image_load("../../data/wesnoth/sorceress-melee-attack-1.png")
    image[4][2] = land_image_load("../../data/wesnoth/sorceress-melee-attack-2.png")
    image[4][3] = land_image_load("../../data/wesnoth/sorceress-melee-attack-3.png")
    image[4][4] = land_image_load("../../data/wesnoth/sorceress-melee-attack-4.png")
    image[4][5] = land_image_load("../../data/wesnoth/sorceress-melee-attack-5.png")
    image[4][6] = land_image_load("../../data/wesnoth/sorceress-melee-attack-6.png")
    image[4][7] = land_image_load("../../data/wesnoth/sorceress-melee-attack-7.png")
    image[4][8] = land_image_load("../../data/wesnoth/sorceress-melee-attack-8.png")
    image[4][9] = land_image_load("../../data/wesnoth/sorceress-melee-attack-9.png")
    image[4][10] = land_image_load("../../data/wesnoth/sorceress-melee-attack-10.png")
    image[5][0] = land_image_load("../../data/wesnoth/enchantress.png")
    image[5][1] = land_image_load("../../data/wesnoth/enchantress-melee-1.png")
    image[5][2] = land_image_load("../../data/wesnoth/enchantress-melee-2.png")
    image[5][3] = land_image_load("../../data/wesnoth/enchantress-melee-3.png")
    image[5][4] = land_image_load("../../data/wesnoth/enchantress-melee-4.png")
    image[5][5] = land_image_load("../../data/wesnoth/enchantress-melee-5.png")
    image[5][6] = land_image_load("../../data/wesnoth/enchantress-melee-6.png")

    for int i = 1 while i <= 32 with i++:
        int j = i % TYPES
        for int k = 0 while image[j][k] with k++:
            int w = land_image_width(image[j][k])
            int h = land_image_height(image[j][k])
            slots[i].frames[k] = land_image_new_from(image[j][k], 0, 0, w, h)
            float *rgb = slots[i].rgb
            land_color(rgb[0], rgb[1], rgb[2], 1)
            land_image_colorize_replace(slots[i].frames[k], 19, COLORKEY_MAGENTA)

static def move_to(int who, to):
    Slot *s = slots + who
    int xi = to & 7
    int yi = to >> 3
    float x = xi * 80
    float y = yi * 80
    s->tx = x
    s->ty = y
    s->moving = True
    s->pos = to
    map[to] = who

static def tick(LandRunner *self):
    ticks++

    if land_key(LandKeyEscape):
        land_quit()

    for int i = 1 while i <= 32 with i++:
        Slot *s = slots + i
        if s->moving:
            double dx = s->tx - s->x
            double dy = s->ty - s->y
            double d = sqrt(dx * dx + dy * dy)
            if d > 4:
                s->x += dx / d * 4
                s->y += dy / d * 4
            else:
                s->moving = False
                # Help with multisampling.
                s->x = (int)(s->x)
                s->y = (int)(s->y)
        elif ticks >= s->next_time:
            s->next_time += land_rand(60 * 2, 60 * 5)
            int what = land_rand(0, 5):
            if what == 0:
                s->flipped ^= 1
                s->offset += 1
            elif what == 1:
                int t = land_rand(1, 32)
                Slot *swap_with = slots + t
                int pos = s->pos
                move_to(i, swap_with->pos)
                move_to(t, pos)
            else:
                s->anim_start = ticks

static def draw_corners(float x, y, s):
    land_filled_polygon(3, (float []){x, y, x + s, y, x, y + s})
    land_filled_polygon(3, (float []){x + 80 - s, y, x + 80, y, x + 80, y + s})
    land_filled_polygon(3, (float []){x, y + 80, x + s, y + 80, x, y + 80 - s})
    land_filled_polygon(3, (float []){x + 80 - s, y + 80, x + 80, y + 80, x + 80, y + 80 - s})

static def draw_target(float x, y, x_, y_, s, r, g, b):
    float dx = x_ - x, dy = y_ - y
    float d = sqrtf(dx * dx + dy * dy)
    dx /= d; dy /= d
    float nx = dy * s, ny = -dx * s
    x += 40; y += 40
    x_ += 40; y_ += 40
    float v[] = {x_, y_, x + nx, y + ny, x, y, x - nx, y - ny};
    float c[] = {0, 0, 0, 0, 0, 0, 0, 0, r, g, b, 1, 0, 0, 0, 0};
    land_filled_colored_polygon(4, v, c)

static def draw(LandRunner *self):
    land_clear(0.25, 0.2, 0.15, 1)

    for int pos = 0 while pos < 32 with pos++:
        int i = map[pos]
        Slot *s = slots + i
        float *rgb = s->rgb
        if s->moving:
            draw_target(s->x, s->y, s->tx, s->ty, 4, rgb[0], rgb[1], rgb[2])

    for int pos = 0 while pos < 32 with pos++:
        int i = map[pos]
        Slot *s = slots + i
        float *rgb = s->rgb
        land_color(rgb[0], rgb[1], rgb[2], 1)

        int xi = pos & 7
        int yi = pos >> 3
        draw_corners(xi * 80, yi * 80, 9)

        int at = ticks - slots[i].anim_start
        int k = at >> 2
        if k > 15 or not slots[i].frames[k]: k = 0
        float ox = 4 + (72 - land_image_width(slots[i].frames[k])) * 0.5
        float oy = 4 + (72 - land_image_height(slots[i].frames[k])) * 0.5
        (s->flipped ? land_image_draw_flipped : land_image_draw)(
            slots[i].frames[k], s->x + ox,
            s->y + oy + 1 * sin((ticks + s->offset) * LAND_PI * 2 / 30))

land_begin_shortcut(80 * 8, 80 * 4, 60,
    LAND_WINDOWED | LAND_OPENGL | LAND_MULTISAMPLE,
    init, None, tick, draw, None, None)
