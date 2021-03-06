import global land.land

static LandImage *zpics[3][12]
static enum Mode:
    XYY
    CIELAB
    LIST
    CLOUD
    CUBE
    CUBE2
    
static Mode mode

class Color:
    LandColor rgb
    double l, a, b
    LandArray *close
    double x, y, z, dx, dy
    bool fixed

class Neighbor:
    Color *c
    double delta

class Xyz:
    int x, y, z
    
LandArray *colors # Color
LandFloat mindist
Color *maximum_grid_color
LandFloat maximum_grid_distance

def hex(Color *c, char *out):
    sprintf(out, "#%02x%02x%02x",
        (int)(255 * c.rgb.r),
        (int)(255 * c.rgb.g),
        (int)(255 * c.rgb.b))

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

    # color cube
    arrange_cube()

def color_new(float r, g, b) -> Color*:
    Color *color; land_alloc(color)
    color.rgb.r = r
    color.rgb.g = g
    color.rgb.b = b
    land_color_to_cielab(color.rgb, &color.l, &color.a, &color.b)
    return color

def color_add(float r, g, b) -> Color*:
    auto color = color_new(r, g, b)
    land_array_add(colors, color)
    return color

def color_addf(float r, g, b):
    color_add(r, g, b)->fixed = True

def arrange_prepare:
    if colors:
        land_array_destroy(colors)
    colors = land_array_new()

def add8:
    color_addf(0, 0, 0)
    color_addf(1, 0, 0)
    color_addf(0, 1, 0)
    color_addf(0, 0, 1)
    color_addf(0, 1, 1)
    color_addf(1, 0, 1)
    color_addf(1, 1, 0)
    color_addf(1, 1, 1)

def arrange_cube:
    arrange_prepare()
    for int x in range(5):
        for int y in range(6):
            for int z in range(5):
                Color * c = color_add(x / 4.0, y / 5.0, z / 4.0)
                if x == 0 or x == 4:
                    if y == 0 or y == 5:
                        if z == 0 or z == 4:
                            c.fixed = True

def arrange_center:
    arrange_prepare()
    add8()
    for int i in range(154 - 8):
        color_add(.5, .5, .5)

def arrange_random:
    arrange_prepare()
    add8()
    for int i in range(154 - 8):
        color_add(land_rand(0, 255) / 255.0,
            land_rand(0, 255) / 255.0,
            land_rand(0, 255) / 255.0)

class ThreadData:
    int xoffset, xcount
    Color *maximum_grid_color
    LandFloat maximum_grid_distance

ThreadData _data[8]
def find_grid_distances:
    for int i in range(8):
        ThreadData *d = _data + i
        d.xoffset = i * 8
        d.xcount = 8
        d.maximum_grid_color = None
        land_thread_run(find_grid_distances_thread, d)

def find_grid_distances_thread(void *v):
    ThreadData *data = v
    LandColor maximum = {0}
    double maximum_distance = 0
    int xn = 64, yn = 64, zn = 64

    for int x in range(data.xoffset, data.xoffset + data.xcount):
        for int y in range(yn):
            for int z in range(zn):
                double minimum = -1
                LandColor gc = land_color_rgba(x / (xn - 1.0),
                    y / (yn - 1.0),
                    z / (zn - 1.0),
                    1.0)
                for Color *c in colors:
                    double d = land_color_distance_ciede2000(gc, c.rgb)
                    if minimum < 0 or d < minimum:
                        minimum = d

                if minimum > maximum_distance:
                    maximum = gc
                    maximum_distance = minimum

    data.maximum_grid_distance = maximum_distance
    data.maximum_grid_color = color_new(maximum.r, maximum.g, maximum.b)
    int m = -1
    for int i in range(8):
        if not _data[i].maximum_grid_color: return
        if m < 0 or _data[i].maximum_grid_distance > _data[m].maximum_grid_distance:
            m = i

    maximum_grid_distance = _data[m].maximum_grid_distance
    maximum_grid_color = _data[m].maximum_grid_color

str custom = """
#400000#800000#452209#5c4305#808000#2a3517#003200#004040#172727#0c0c38#000080#250041#400040#000000
#5e4747#8b0000#8b4513#7f725a#daa520#006400#008000#008080#2f4f4f#005f7f#191970#4b0082#630a42#343434
#a52a2a#b22222#cd853f#b8860b#bdb76b#556b2f#228b22#3cb371#008b8b#4682b4#0000cd#663399#800080#696969
#dc143c#a0522d#ff8c00#d2b48c#f5deb3#6b8e23#2e8b57#20b2aa#5f9ea0#708090#483d8b#9400d3#8b008b#808080
#cd5c5c#ff0000#f4a460#ffd700#f0e68c#9acd32#8fbc8f#66cdaa#00ced1#778899#0000ff#6c5f6c#c71585#a9a9a9
#bc8f8f#d2691e#ffa500#ffdead#eee8aa#32cd32#48d1cc#87ceeb#1e90ff#6a5acd#8a2be2#ff1493#c0c0c0
#f08080#ff4500#deb887#ffe4b5#ffefd5#7fff00#90ee90#40e0d0#add8e6#6495ed#4169e1#9932cc#ff00ff#d3d3d3
#fa8072#ff6347#ffdab9#faebd7#ffff00#adff2f#00ff00#00fa9a#b0e0e6#00bfff#7b68ee#ba55d3#db7093#dcdcdc
#ffb6c1#ff7f50#ffe4c4#ffebcd#fff8dc#f5f5dc#00ff7f#00ffff#afeeee#b0c4de#9370db#ee82ee#da70d6#f5f5f5
#ffc0cb#e9967a#faf0e6#fdf5e6#fffacd#fafad2#98fb98#7fffd4#e0ffff#87cefa#e6e6fa#dda0dd#ff69b4#fffafa
#ffe4e1#ffa07a#fff5ee#fffaf0#ffffe0#fffff0#f0fff0#f5fffa#f0ffff#f0f8ff#f8f8ff#d8bfd8#fff0f5#ffffff
#9585a5
"""



str custom2 = """
#400000#8b4513#452209#5c4305#808000#008000#003200#004040#172727#0c0c38
#250041#400040#630a42#000000#800000#ff0000#a0522d#7f725a#6b8e23#228b22
#2a3517#2f4f4f#708090#483d8b#005f7f#000080#800080#5e4747#343434#8b0000
#d2691e
#e9967a#daa520#bdb76b#32cd32#006400#008080#778899#4169e1#191970#8b008b
#c71585#696969#a52a2a#ff4500#d2b48c#ffd700#f0e68c#9acd32#556b2f#008b8b
#b0c4de#4682b4#4b0082#9400d3#ff1493#808080#b22222#b8860b#deb887#f5deb3
#eee8aa#00fa9a#2e8b57#20b2aa#add8e6#1e90ff#0000cd#6c5f6c#ff00ff#a9a9a9
#dc143c#cd853f#ffdab9#ffe4b5#f5f5dc#00ff00#3cb371#00ced1#b0e0e6#5f9ea0
#0000ff#9932cc#db7093#c0c0c0#cd5c5c#ff7f50#ffdead#ffebcd#fafad2#00ff7f
#8fbc8f#48d1cc#e6e6fa#6495ed#663399#ba55d3#bc8f8f#d3d3d3#ff6347#ff8c00
#ffe4c4#ffefd5#fff8dc#7cfc00#66cdaa#40e0d0#f0f8ff#00bfff#8a2be2#da70d6
#ff69b4#dcdcdc#f08080#f4a460#faebd7#fdf5e6#fffacd#7fff00#90ee90#afeeee
#f8f8ff#87ceeb#6a5acd#ee82ee#ffb6c1#f5f5f5#fa8072#ffa07a#faf0e6#ffff00
#ffffe0#98fb98#f0fff0#00ffff#e0ffff#87cefa#7b68ee#dda0dd#ffc0cb#fffafa
#ffe4e1#ffa500#fff5ee#fffaf0#fffff0#adff2f#f5fffa#7fffd4#f0ffff#9370db
#d8bfd8#fff0f5#ffffff
"""

def print_colors:
    int i = 1
    for Color *c in colors:
        printf("color%03d #%02x%02x%02x\n", i, (int)(c.rgb.r * 255),
            (int)(c.rgb.g * 255), (int)(c.rgb.b * 255))
        i++

def arrange_custom:
    arrange_prepare()
    str p = custom
    while *p:
        if *p == '#':
            LandColor c = land_color_name(p)
            p += 7
            auto c2 = color_add(c.r, c.g, c.b)
            c2.fixed = True
        else:
            p++

def find_neighbors:
    double close = 0.3
    double min_close = close
    Color *min_a = None
    Color *min_b = None
    
    land_array_sort(colors, comp_l)

    int cn = land_array_count(colors)
    for int i in range(cn):
        Color *c = land_array_get_nth(colors, i)
        if c.close:
            land_array_destroy(c.close)
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
            if d < min_close:
                min_close = d
                min_a = c
                min_b = o

    for Color *col in colors:
        land_array_sort(col.close, comp_delta)

    if min_a:
        char ha[100], hb[100]
        hex(min_a, ha)
        hex(min_b, hb)
        printf("Closest pair: %.2f: %s <-> %s\n", min_close, ha, hb)

static def comp_delta(void const *a, void const *b) -> int:
    Neighbor * const *ap = a
    Neighbor * const *bp = b
    Neighbor *ac = *ap
    Neighbor *bc = *bp
    if ac.delta < bc.delta: return -1
    if ac.delta > bc.delta: return 1
    return 0

static def comp_l(void const *a, void const *b) -> int:
    Color * const *ap = a
    Color * const *bp = b
    Color *ac = *ap
    Color *bc = *bp
    if ac.l < bc.l: return -1
    if ac.l > bc.l: return 1
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

def clip(double x) -> double:
    if x < 0: return 0
    if x > 1: return 1
    return x

static def tick:
    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

    if land_key_pressed('1'): arrange_cube()
    if land_key_pressed('2'): arrange_center()
    if land_key_pressed('3'): arrange_random()
    if land_key_pressed('4'): arrange_custom()
    
    if land_key_pressed('s'): print_colors()
    if land_key_pressed('d'): find_grid_distances()
    if land_key_pressed('a'):
        if maximum_grid_color:
            LandColor rgb = maximum_grid_color.rgb
            printf("adding #%02x%02x%02x\n",
                (int)(rgb.r * 255), (int)(rgb.g * 255), (int)(rgb.b * 255))
                
            color_add(rgb.r, rgb.g, rgb.b)

    if land_key_pressed(LandKeyFunction + 1): mode = XYY
    if land_key_pressed(LandKeyFunction + 2): mode = CIELAB
    if land_key_pressed(LandKeyFunction + 3):
        mode = LIST
        find_neighbors()

    if land_key_pressed(LandKeyFunction + 4):
        find_neighbors()

        int id = 0
        for Color *col in colors:
            col.x = 600
            col.y = 450
            if id == 0: col.y = 900 - 90
            if id == land_array_count(colors) - 1: col.y = 90
            id++
        mode = CLOUD
    if land_key_pressed(LandKeyFunction + 5):
        mode = CUBE
    if land_key_pressed(LandKeyFunction + 6):
        mode = CUBE2

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

            if not c.close: continue

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
            if id != 0 and id != land_array_count(colors) - 1:
                c.x += c.dx
                c.y += c.dy
            c.dx *= 0.9
            c.dy *= 0.9
            if c.x > 1200 - 30: c.x -= 1200
            if c.x < -30: c.x += 1200
            if c.y < 0: c.y = 0
            if c.y > 900: c.y = 900
            id++

    if mode == CUBE or mode == CUBE2:
        # LLoyd's (but too slow as brute force)
        # 1. for each color, assign to it all the colors closer to it
        #    than to any other
        # 2. for each such voronoi cell, compute the centroid
        # 3. move the color closer to its centroid
        # 4. repeat

        double t = land_get_time()
        while land_get_time() < t + 1.0 / 100:
            int i = land_rand(0, land_array_count(colors) - 1)
            Color *col = land_array_get_nth(colors, i)
            
            double md = -1
            for Color *c in colors:
                if c == col: continue
                if fabs(c.l - col.l) > 0.2: continue
                double d = land_color_distance_ciede2000(col.rgb, c.rgb)
                if md < 0 or d < md:
                    md = d
            LandColor rgb2 = col.rgb
            rgb2.r = clip(rgb2.r + land_rnd(-0.01, 0.01))
            rgb2.g = clip(rgb2.g + land_rnd(-0.01, 0.01))
            rgb2.b = clip(rgb2.b + land_rnd(-0.01, 0.01))
            double md2 = -1
            for Color *c in colors:
                if c == col: continue
                if fabs(c.l - col.l) > 0.2: continue
                double d = land_color_distance_ciede2000(rgb2, c.rgb)
                if md2 < 0 or d < md2:
                    md2 = d
            if md2 > md:
                #printf("%f > %f\n", md2, md)
                if not col.fixed:
                    col.rgb = rgb2
                    land_color_to_cielab(col.rgb, &col.l, &col.a, &col.b)
                mindist = mindist * 0.99 + md2 * 0.01

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
        if c.l < 0.5:
            land_color(1, 1, 1, 1)
        else:
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

    if mode == CUBE or mode == CUBE2:
        land_clear(0.5, 0.5, 0.5, 1)
        land_color(0.8, 0.8, 0.8, 1)

        Land4x4Matrix m = land_4x4_matrix_identity()
        m = land_4x4_matrix_mul(m, land_4x4_matrix_translate(600, 450, 0))
        m = land_4x4_matrix_mul(m, land_4x4_matrix_rotate(1, 0, 0, LAND_PI / -4))
        m = land_4x4_matrix_mul(m, land_4x4_matrix_rotate(0, 1, 0, land_get_ticks() * 2 * LAND_PI / 600))
        m = land_4x4_matrix_mul(m, land_4x4_matrix_scale(400, -400, 400))
        m = land_4x4_matrix_mul(m, land_4x4_matrix_translate(-0.5, -0.5, -0.5))

        LandVector v[] = {
            {0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0},
            {0, 0, 1}, {1, 0, 1}, {1, 1, 1}, {0, 1, 1},
            }
        for int i in range(8):
            v[i] = land_vector_matmul(v[i], &m)
        int lines[] = {0, 1, 1, 2, 2, 3, 3, 0,
            4, 5, 5, 6, 6, 7, 7, 4,
            0, 4, 1, 5, 2, 6, 3, 7}
        for int i in range(0, 24, 2):
            int a = lines[i]
            int b = lines[i + 1]
            land_line(v[a].x, v[a].y, v[b].x, v[b].y)

        for Color *col in colors:
            LandColor c = col.rgb
            LandVector p = {c.r, c.g, c.b}
            if mode == CUBE2:
                p = (LandVector){col.a + 0.5, col.l, col.b + 0.5}
            LandVector v = land_vector_matmul(p, &m)
            col.x = v.x
            col.y = v.y
            col.z = v.z

        LandArray *a = land_array_copy(colors)
        land_array_sort(a, comp_z)

        for Color *col in a:
            LandColor c = col.rgb
            land_color(c.r, c.g, c.b, 1)
            float ra = 20
            if col.fixed: ra *= 1.5
            land_filled_circle(col.x - ra, col.y - ra, col.x + ra, col.y + ra)

        land_array_destroy(a)

        land_color(0, 0, 0, 1)
        land_text_pos(0, 0)
        land_print("Colors: %d", land_array_count(colors))
        land_print("Minimum distance: %f", mindist)
        if maximum_grid_color:
            land_print("Maximum distance: %f", maximum_grid_distance)
            draw_color(maximum_grid_color, 30, land_text_y() + 60)
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

static def comp_z(void const *a, void const *b) -> int:
    Color const * const *as = a
    Color const * const *bs = b
    Color const *ac = *as
    Color const *bc = *bs
    if ac.z < bc.z: return -1
    if ac.z > bc.z: return 1
    return 0

static def _main:
    land_init()
    land_set_display_parameters(1200, 900, LAND_WINDOWED)
    land_callbacks(init, tick, draw, None)
    land_mainloop()

land_use_main(_main)
