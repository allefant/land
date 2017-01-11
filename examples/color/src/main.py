import global land.land

static LandImage *zpics[3][12]
static enum Mode:
    XYY
    CIELAB
    LIST
    CLOUD
    CUBE
    
static Mode mode

class Color:
    LandColor rgb
    double l, a, b
    LandArray *close
    double x, y, dx, dy

class Neighbor:
    Color *c
    double delta

class Xyz:
    int x, y, z
    
LandArray *colors

static def get_Y(int i) -> float:
    if i == 0: return 0.01
    return i * 0.07

static def get_x(int i) -> float:
    return 0.1 + (i / 255.0) * 0.6

static def get_y(int i) -> float:
    return 0.0 + (1 - i / 255.0) * 0.6

static def get_L(int i) -> float:
    if i == 0: return 0.16
    if i < 10:
        i -= 1
        return 0.32 + 0.07 * i
    i -= 10
    return 0.91 + 0.06 * i

static def get_a(int i) -> float:
    return (i - 127.5) / 240.0 * 2

static def get_b(int i) -> float:
    return (120 - i) / 240.0 * 2

static def get_ai(float x) -> int:
    return x * 240.0 / 2 + 127.5

static def get_bi(float x) -> int:
    return 120 - x * 240.0 / 2

static def get_xi(float x) -> int:
    return (x - 0.1) / 0.6 * 255.0

static def get_yi(float y) -> int:
    return 255 - (y - 0.0) / 0.6 * 255.0

static def xyz_new(int x, y, z) -> Xyz*:
    Xyz *xyz
    land_alloc(xyz)
    xyz.x = x
    xyz.y = y
    xyz.z = z
    return xyz

static def remove_neighbor(int n, LandColor *cube, double r,
        LandColor c, int x, y, z):
    LandArray *pos = land_array_new()
    land_array_add(pos, xyz_new(x, y, z))
    while True:
        Xyz *xyz = land_array_pop(pos)
        if not xyz:
            break
        x = xyz.x
        y = xyz.y
        z = xyz.z
        land_free(xyz)
        if x < 0: continue
        if y < 0: continue
        if z < 0: continue
        if x >= n: continue
        if y >= n: continue
        if z >= n: continue
        LandColor *o = &cube[x + y * n + z * n * n]
        if o.a < 1: continue
        double d = land_color_distance_ciede2000(c, *o)
        if d < r:
            o.a = 0
            land_array_add(pos, xyz_new(x + 1, y, z))
            land_array_add(pos, xyz_new(x - 1, y, z))
            land_array_add(pos, xyz_new(x, y + 1, z))
            land_array_add(pos, xyz_new(x, y - 1, z))
            land_array_add(pos, xyz_new(x, y, z + 1))
            land_array_add(pos, xyz_new(x, y, z - 1))
    land_array_destroy(pos)

static def remove_close(int n, LandColor *cube, double r, int x, y, z):
    LandColor *c = &cube[x + y * n + z * n * n]
    if c.a < 1:
        return
    remove_neighbor(n, cube, r, *c, x, y, z)

static def init:
    mode = CIELAB

    test_ciede2000()

    land_font_load("../../data/Muli-Regular.ttf", 14)

    if True:
        double x, y, z
        double l, a, b
        LandColor cols[8] = {
            {0, 0, 0, 1},
            {1, 0, 0, 1},
            {0, 1, 0, 1},
            {0, 0, 1, 1},
            {1, 1, 0, 1},
            {0, 1, 1, 1},
            {1, 0, 1, 1},
            {1, 1, 1, 1}}
        for int i in range(8):
            LandColor c = cols[i]
            land_color_to_xyy(c, &x, &y, &z)
            printf("rgb %5.1f/%5.1f/%5.1f = xyY %.2f/%.2f/%.2f\n",
                c.r, c.g, c.b, x, y, z)
            land_color_to_cielab(c, &l, &a, &b)
            printf("                      = Lab %.2f/%.2f/%.2f\n",
                l, a, b)

    # create XYZ and xyY pictures
    for int m in range(2):
        for int zi in range(12):
            double Y = get_Y(zi)
            double l = get_L(zi)
            
            zpics[m][zi] = land_image_new(256, 256)
            uint8_t rgba[256 * 256 * 4]
            for int yi in range(256):
                double y = get_y(yi)
                double b = get_b(yi)
                for int xi in range(256):
                    double x = get_x(xi)
                    double a = get_a(xi)
                    uint8_t cr, cg, cb, ca

                    LandColor c = {0, 0, 0, 0}
                    if m == XYY: c = land_color_xyy(x, y, Y)
                    if m == CIELAB: c = land_color_cielab(l, a, b)
                    if c.r < 0 or c.g < 0 or c.b < 0 or c.r > 1 or c.g > 1 or c.b > 1:
                        c.r = c.g = c.b = 0
                    cr = c.r * 255
                    cg = c.g * 255
                    cb = c.b * 255
                    ca = 255
                    rgba[yi * 256 * 4 + xi * 4 + 0] = cr
                    rgba[yi * 256 * 4 + xi * 4 + 1] = cg
                    rgba[yi * 256 * 4 + xi * 4 + 2] = cb
                    rgba[yi * 256 * 4 + xi * 4 + 3] = ca
            land_image_set_rgba_data(zpics[m][zi], rgba)

    # create a fixed color lattice
    int n = 64
    LandColor cube[n * n * n]
    for int ri in range(n):
        for int gi in range(n):
            for int bi in range(n):
                int i = ri + gi * n + bi * n * n
                LandColor c
                c.a = 1
                c.r = ri / (n - 1.0)
                c.g = gi / (n - 1.0)
                c.b = bi / (n - 1.0)
                cube[i] = c

    colors = land_array_new()

    double r = 0.16

    int s = n
    while s > 0:
        for int x_ in range(0, n + 1, s):
            int x = x_ < n ? x_ : n - 1
            for int y_ in range(0, n + 1, s):
                int y = y_ < n ? y_ : n - 1
                for int z_ in range(0, n + 1, s):
                    int z = z_ < n ? z_ : n - 1

                    LandColor *c = &cube[x + y * n + z * n * n]
                    if c.a == 1:
                        Color *color
                        land_alloc(color)
                        color.rgb.r = c.r
                        color.rgb.g = c.g
                        color.rgb.b = c.b
                        land_color_to_cielab(*c, &color.l, &color.a, &color.b)
                        land_array_add(colors, color)
                        printf("%d %d %d: %.1f %.1f %.1f\n", x, y, z, c.r, c.g, c.b)
                    remove_close(n, cube, r, x, y, z)
        s /= 2

    printf("%d / %d colors with distance %f\n", land_array_count(colors),
        n * n * n, r)

    double close = 0.3

    int cn = land_array_count(colors)
    for int i in range(cn):
        Color *c = land_array_get_nth(colors, i)
        c.close = land_array_new()
        for int j in range(cn):
            if j == i: continue
            Color *o = land_array_get_nth(colors, j)
            double d = land_color_distance_ciede2000(c.rgb, o.rgb)
            if d < close:
                Neighbor *ne
                land_alloc(ne)
                ne.c = o
                ne.delta = d
                land_array_add(c.close, ne)

    for Color *col in colors:
        land_array_sort(col.close, comp)

static def comp(void const *a, void const *b) -> int:
    Neighbor * const *ap = a
    Neighbor * const *bp = b
    Neighbor *ac = *ap
    Neighbor *bc = *bp
    if ac.delta < bc.delta: return -1
    if ac.delta > bc.delta: return 1
    return 0

static def xdist(double x1, x2) -> double:
    #   A          B # +10 or -4
    #   B      A     # -6 or +8 
    #   A       B    # +7 or -7
    #   A B          # +1 or -13
    #   B          A # -10 or +4
    double dx = x1 - x2
    if fabs(dx) < 600: return dx
    if dx > 0: return dx - 1200
    return dx + 1200

static def tick:
    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

    if land_key_pressed(LandKeyFunction + 1): mode = XYY
    if land_key_pressed(LandKeyFunction + 2): mode = CIELAB
    if land_key_pressed(LandKeyFunction + 3): mode = LIST
    if land_key_pressed(LandKeyFunction + 4):
        int id = 0
        for Color *col in colors:
            col.x = 600
            col.y = 450
            if id == 0: col.y = 900 - 90
            if id == 7: col.y = 90
            id++
        mode = CLOUD
    if land_key_pressed(LandKeyFunction + 5): mode = CUBE

    if mode == CLOUD:
        int id = 0
        for Color *c in colors:
            for Color *o in colors:
                if o == c: continue
                double dx = xdist(o.x, c.x)
                double dy = o.y - c.y
                double d = sqrt(dx * dx + dy * dy)
                if d < 90:
                    if d < 1:
                        c.dx += land_rnd(-1, 1)
                        c.dy += land_rnd(-1, 1)
                    else:
                        c.dx -= dx / d * (90 - d) / 90
                        c.dy -= dy / d * (90 - d) / 90

            int ci = 0
            for Neighbor *n in LandArray *c.close:
                Color *o = n.c
                double dx = xdist(o.x, c.x)
                double dy = o.y - c.y
                double d = sqrt(dx * dx + dy * dy)
                double e = n.delta
                if d > 90:
                    e -= 0.25
                    if e < 0.05:
                        double f = d - 90
                        if f > 200: f = 200
                        f /= 10000
                        if f < 0: f = 0
                        e = 0.05 - e
                        e /= 0.05
                        c.dx += dx * e * f
                        c.dy += dy * e * f
                ci++
                if ci == 6: break

            #c.dy -= (c.l - 0.5) / 100000

            if fabs(c.dx) > 5:
                c.dx /= fabs(c.dx) / 5
            if fabs(c.dy) > 5:
                c.dy /= fabs(c.dy) / 5
                        
            if c.y < 30: c.dy += 1
            if c.y > 900 - 30: c.dy -= 1
            if id != 0 and id != 7:
                c.x += c.dx
                c.y += c.dy
            c.dx *= 0.9
            c.dy *= 0.9
            if c.x > 1200 - 30: c.x -= 1200
            if c.x < -30: c.x += 1200
            if c.y < 0: c.y = 0
            if c.y > 900: c.y = 900
            id++

static def marker(float x, y):
    land_circle(x - 10, y - 10, x + 10, y + 10)

static def draw_color(Color *c, float x, y):
    land_color(c.rgb.r, c.rgb.g, c.rgb.b, 1)
    land_filled_rectangle(x - 30, y - 30, x + 30, y + 30)
    int n = land_array_count(c.close)
    for int i in range(n):
        if i >= 6: break
        Neighbor *ne = land_array_get_nth(c.close, i)
        Color *o = ne.c
        float dx = cos(LAND_PI * 2 * i / 6)
        float dy = sin(LAND_PI * 2 * i / 6)
        float ox = x + 20 * dx
        float oy = y + 20 * dy
        land_color(0, 0, 0, 1)
        land_line(x + 10 * dx, y + 10 * dy, x + 15 * dx, y + 15 * dy)
        land_color(o.rgb.r, o.rgb.g, o.rgb.b, 1)
        land_filled_circle(ox - 5, oy - 5, ox + 5, oy + 5)

static def draw:

    if mode == LIST:
        land_clear(0.5, 0.5, 0.5, 1)
        int i = 0
        for int yi in range(15):
            for int xi in range(20):
                int x = xi * 60
                int y = yi * 60
                if i >= land_array_count(colors):
                    break
                Color *c = land_array_get_nth(colors, i++)
                draw_color(c, x + 30, y + 30)
        return

    if mode == CLOUD:
        land_clear(0.5, 0.5, 0.5, 1)
        for  Color *c in colors:
            land_color(c.rgb.r, c.rgb.g, c.rgb.b, 1)
            float x = c.x
            float y = c.y
            land_filled_circle(x - 30, y - 30, x + 30, y + 30)
            land_filled_circle(1200 + x - 30, y - 30, 1200 + x + 30, y + 30)
        return

    if mode == XYY or mode == CIELAB:

        land_clear(0, 0, 0, 1)
        
        for int y in range(3):
            for int x in range(4):
                int x_ = 22 + x * 300
                int y_ = 22 + y * 300
                int i = x + y * 4
                land_image_draw(zpics[mode][i], x_, y_)
                land_color(1, 1, 1, 1)
                land_text_pos(x_, y_ - 20)
                if mode == XYY: land_print("Y = %.2f", get_Y(i))
                if mode == CIELAB: land_print("L = %.2f", get_L(i))
                land_rectangle(x_, y_, x_ + 256, y_ + 256)

                if mode == XYY:

                    if i == 1:
                        land_color(0, 0, 1, 1)
                        marker(x_ + get_xi(0.15), y_ + get_yi(0.06))

                    if i == 3:
                        land_color(1, 0, 0, 1)
                        marker(x_ + get_xi(0.64), y_ + get_yi(0.33))

                    if i == 4:
                        land_color(1, 0, 1, 1)
                        marker(x_ + get_xi(0.32), y_ + get_yi(0.15))

                    if i == 10:
                        land_color(0, 1, 0, 1)
                        marker(x_ + get_xi(0.30), y_ + get_yi(0.60))

                    if i == 11:
                        land_color(0, 1, 1, 1)
                        marker(x_ + get_xi(0.22), y_ + get_yi(0.33))

                    if i == 11:
                        land_color(1, 1, 0, 1)
                        marker(x_ + get_xi(0.42), y_ + get_yi(0.51))

                if mode == CIELAB:
                    if i == 1:
                        land_color(0, 0, 1, 1)
                        marker(x_ + get_ai(0.79), y_ + get_bi(-1.08))

                    if i == 4:
                        land_color(1, 0, 0, 1)
                        marker(x_ + get_ai(0.80), y_ + get_bi(0.67))

                    if i == 5:
                        land_color(1, 0, 1, 1)
                        marker(x_ + get_ai(0.98), y_ + get_bi(-0.61))

                    if i == 9:
                        land_color(0, 1, 0, 1)
                        marker(x_ + get_ai(-0.86), y_ + get_bi(0.83))

                    if i == 10:
                        land_color(0, 1, 1, 1)
                        marker(x_ + get_ai(-0.48), y_ + get_bi(-0.14))

                    if i == 11:
                        land_color(1, 1, 0, 1)
                        marker(x_ + get_ai(-0.22), y_ + get_bi(0.94))

static def _main:
    land_init()
    land_set_display_parameters(1200, 900, LAND_WINDOWED)
    land_callbacks(init, tick, draw, None)
    land_mainloop()

land_use_main(_main)
