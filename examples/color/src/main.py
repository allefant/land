import global land.land
import palette

static LandImage *zpics[4][12]
static enum Mode:
    XYY
    CIELAB
    OKLAB
    LIST
    CLOUD
    CUBE
    CUBE_LAB
    CUBE_OK
    
static Mode mode

class Color:
    LandColor rgb
    double l, a, b
    double ol, oa, ob
    LandArray *close
    double x, y, z, dx, dy
    bool fixed
    int marked

class Neighbor:
    Color *c
    double delta

class Xyz:
    int x, y, z
    
LandArray *colors # Color
LandFloat mindist
Color *maximum_grid_color
LandFloat maximum_grid_distance
int selected
bool show_marked

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

static def _init:
    mode = CIELAB

    test_ciede2000()

    land_find_data_prefix("data/")
    land_font_load("data/Muli-Regular.ttf", 14)

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
            land_color_to_oklab(c, &l, &a, &b)
            printf("                      = OkLab %.2f/%.2f/%.2f\n",
                l, a, b)

    # create XYZ and xyY and oklab pictures
    for int m in range(3):
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
                    if m == OKLAB:
                        c = land_color_oklab(l, a / 4, b / 4)
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

def _done:
    pass

def color_new(float r, g, b) -> Color*:
    Color *color; land_alloc(color)
    color.rgb.r = r
    color.rgb.g = g
    color.rgb.b = b
    land_color_to_cielab(color.rgb, &color.l, &color.a, &color.b)
    land_color_to_oklab(color.rgb, &color.ol, &color.oa, &color.ob)
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
LandLock *_lock
def find_grid_distances:
    if not _lock:
        _lock = land_thread_new_lock()
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

    land_thread_lock(_lock)
    int m = -1
    bool finished = True
    for int i in range(8):
        if not _data[i].maximum_grid_color:
            finished = False
            break
        if m < 0 or _data[i].maximum_grid_distance > _data[m].maximum_grid_distance:
            m = i

    if finished:
        maximum_grid_distance = _data[m].maximum_grid_distance
        maximum_grid_color = _data[m].maximum_grid_color
        printf("max distance: %.3f: #%02x%02x%02x\n", maximum_grid_distance,
            (int)(maximum_grid_color.rgb.r * 255), (int)(maximum_grid_color.rgb.g * 255), (int)(maximum_grid_color.rgb.b * 255))
    land_thread_unlock(_lock)

def print_colors:
    int i = 1
    for Color *c in colors:
        printf("color%03d #%02x%02x%02x\n", i, (int)(c.rgb.r * 255),
            (int)(c.rgb.g * 255), (int)(c.rgb.b * 255))
        i++

def arrange_fruits:
    arrange_prepare()
    int i = 0
    while fruits_palette[i]:
        LandColor c = land_color_name(fruits_palette[i])
        auto c2 = color_add(c.r, c.g, c.b)
        c2.fixed = True
        i++
    print("added %d colors", i)

def find_neighbors:
    double close = 0.3
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

    for Color *col in colors:
        land_array_sort(col.close, comp_delta)

    float mind = 1
    float maxd = 0
    Color *mindc = None, *mindc2
    Color *maxdc = None, *maxdc2
    for Color *col in colors:
        if land_array_count(col.close) == 0:
            continue
        Neighbor *a = land_array_get(col.close, 0)
        Neighbor *b = land_array_get(col.close, -1)
        if a.delta < mind:
            mind = a.delta
            mindc = col
            mindc2 = a.c
        if a.delta > maxd:
            maxd= a.delta
            maxdc = col
            maxdc2 = b.c

    print("Smallest delta: %.3f: %s <-> %s", mind, color_name(mindc), color_name(mindc2))
    print("Largest delta: %.3f: %s <-> %s", maxd, color_name(maxdc), color_name(maxdc2))

    for Color *col in colors:
        col.marked = 0
        if land_array_count(col.close) == 0:
            col.marked = 1
            continue
        Neighbor *a = land_array_get(col.close, 0)
        if a.delta >= 0.050:
            col.marked = 1
        if a.delta < 0.020:
            col.marked = 2

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

def select_color(float mx, my) -> int:
    int x = mx / 60
    if x < 0: x = 0
    if x > 19: x = 19
    int y = my / 60
    if y < 0: y = 0
    if y > 14: y = 14
    int i = y * 20 + x
    if i >= 0 and i < len(colors):
        return i
    return -1

def select_color_rgb(float r, g, b) -> int:
    int i = 0
    float e = 0.001
    print("colors: %d", land_array_count(colors))
    for Color *c in colors:
        print("%d: %f %f %f", i, fabs(c.rgb.r - r), fabs(c.rgb.g - g), fabs(c.rgb.b - b))
        if fabs(c.rgb.r - r) < e and fabs(c.rgb.g - g) < e and fabs(c.rgb.b - b) < e:
            return i
        i += 1
    return -1

char _cns[10][100]
int _cnsi
def color_name(Color *c) -> str:
    char h[8], h2[8]
    land_color_to_html(c.rgb, h)
    str name = "-"
    for int i = 0 while fruits_palette[i] with i++:
        LandColor lc = land_color_name(fruits_palette[i])
        land_color_to_html(lc, h2)
        if land_equals(h, h2):
            name = fruits_palette[i]
    int i = _cnsi++
    _cnsi %= 10
    sprintf(_cns[i], "%s (%s)", h, name)
    return _cns[i]

static def _tick:
    land_scale_to_fit(1200, 900, 256)
    LandFloat mx = land_mouse_x()
    LandFloat my = land_mouse_y()
    LandFloat mz = 0
    land_transform(&mx, &my, &mz)

    if land_key_pressed(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

    if land_key_pressed('1'): arrange_cube(); find_neighbors()
    if land_key_pressed('2'): arrange_center(); find_neighbors()
    if land_key_pressed('3'): arrange_random(); find_neighbors()
    if land_key_pressed('4'): arrange_fruits(); find_neighbors()

    if land_key_pressed('s'): print_colors()
    if land_key_pressed('m'): show_marked = not show_marked
    if land_key_pressed('d'): find_grid_distances()
    if land_key_pressed('a'):
        if maximum_grid_color:
            LandColor rgb = maximum_grid_color.rgb
            printf("adding #%02x%02x%02x\n",
                (int)(rgb.r * 255), (int)(rgb.g * 255), (int)(rgb.b * 255))
                
            color_add(rgb.r, rgb.g, rgb.b)
            find_neighbors()
            selected = select_color_rgb(rgb.r, rgb.g, rgb.b)
    if land_key_pressed('n'):
        int j = select_color(mx, my)
        if j > 0 and j != selected:
            Color* c1 = land_array_get(colors, selected)
            Color* c2 = land_array_get(colors, j)
            double l1, a1, b1, l2, a2, b2
            land_color_to_oklab(c1.rgb, &l1, &a1, &b1)
            land_color_to_oklab(c2.rgb, &l2, &a2, &b2)
            float l3 = (l1 + l2) / 2
            float a3 = (a1 + a2) / 2
            float b3 = (b1 + b2) / 2
            LandColor rgb = land_color_oklab(l3, a3, b3)
            printf("adding #%02x%02x%02x\n",
                (int)(rgb.r * 255), (int)(rgb.g * 255), (int)(rgb.b * 255))
            color_add(rgb.r, rgb.g, rgb.b)

    if land_key_pressed(LandKeyFunction + 1):
        if mode == CIELAB: mode = OKLAB
        elif mode == OKLAB: mode = XYY
        else: mode = CIELAB
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
        mode = CUBE_LAB
    if land_key_pressed(LandKeyFunction + 7):
        mode = CUBE_OK

    if mode == LIST:
        if land_mouse_button_clicked(LandButtonLeft):
            int i = select_color(mx, my)
            if i >= 0:
                selected = i
                Color* c = land_array_get(colors, i)
                print("%s", color_name(c))
                int n = land_array_count(c.close)
                if n > 6: n = 6
                for int i in range(n):
                    Neighbor *ne = land_array_get_nth(c.close, i)
                    Color *o = ne.c
                    print("%d: %s: %.3f", i, color_name(o), land_color_distance_ciede2000(c.rgb, o.rgb))

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

    if mode == CUBE or mode == CUBE_LAB or mode == CUBE_OK:
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
                    land_color_to_oklab(col.rgb, &col.ol, &col.oa, &col.ob)
                mindist = mindist * 0.99 + md2 * 0.01

static def marker(float x, y):
    land_circle(x - 10, y - 10, x + 10, y + 10)

static def draw_color(Color *c, float x, y):
    land_color(c.rgb.r, c.rgb.g, c.rgb.b, 1)
    land_filled_rectangle(x - 30, y - 30, x + 30, y + 30)

    if not show_marked:
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

    int a = 28
    int b = 29
    if show_marked:
        if c.marked == 1:
            land_color(0, 0, 0, 1)
            land_rectangle(x - a, y - a, x + b, y + b)
            land_color(0, 1, 0, 1)
            land_rectangle(x - b, y - b, x + a, y + a)
        if c.marked == 2:
            land_color(0, 0, 0, 1)
            land_rectangle(x - a, y - a, x + b, y + b)
            land_color(1, 0, 0, 1)
            land_rectangle(x - b, y - b, x + a, y + a)

def _show_selected:
    int i = selected
    int x = (i % 20) * 60
    int y = (i // 20) * 60
    land_color(0, 0, 0, 1)
    land_thickness(1)
    land_rectangle(x + 2, y + 2, x + 62, y + 62)
    land_color(1, 1, 1, 1)
    land_thickness(2)
    land_rectangle(x, y, x + 60, y + 60)

static def _draw:
    land_scale_to_fit(1200, 900, 0)

    if mode == LIST:
        land_clear(0.5, 0.5, 0.5, 1)
        int i = 0
        for int yi in range(15):
            for int xi in range(20):
                int x = xi * 60
                int y = yi * 60
                if i >= land_array_count(colors):
                    break
                Color *c = land_array_get_nth(colors, i)
                draw_color(c, x + 30, y + 30)
                i++
        _show_selected()

    elif mode == CLOUD:
        land_clear(0.5, 0.5, 0.5, 1)
        for  Color *c in colors:
            land_color(c.rgb.r, c.rgb.g, c.rgb.b, 1)
            float x = c.x
            float y = c.y
            land_filled_circle(x - 30, y - 30, x + 30, y + 30)
            land_filled_circle(1200 + x - 30, y - 30, 1200 + x + 30, y + 30)

    elif mode == CUBE or mode == CUBE_LAB or mode == CUBE_OK:
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
            if mode == CUBE_LAB:
                p = (LandVector){(1 + col.a) / 2, col.l, (1 + col.b) / 2}
            if mode == CUBE_OK:
                p = (LandVector){0.5 + col.oa  * 2, col.ol, 0.5 + col.ob * 2}
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

    elif mode == XYY or mode == CIELAB or mode == OKLAB:

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
                if mode == OKLAB: land_print("L = %.2f", get_L(i))
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

    land_text_pos(0, 900 - 12)
    land_color(1, 1, 1, 1)
    land_print("F3=list F4=cloud F5=cube F6=lab F7=ok 1=565 2=gray 3=random 4=fruits")

static def comp_z(void const *a, void const *b) -> int:
    Color const * const *as = a
    Color const * const *bs = b
    Color const *ac = *as
    Color const *bc = *bs
    if ac.z < bc.z: return -1
    if ac.z > bc.z: return 1
    return 0

def _config:
    land_set_display_parameters(2400, 64+1800, LAND_WINDOWED)
land_example(_config, _init, _tick, _draw, _done)
