import global land/land

LandImage *image
LandVoronoi *voronoi
float use_distance = 0
bool use_wrap = True
int use_passes = 1
int use_edge_display = 0
int use_count = 1000
bool show_delaunay = False
bool show_voronoi = True
bool show_numbers = False
int selected = 0
uint64_t seed
int fixed_seed
int use_clip_border = 0
int use_w = 1000
int use_h = 1000

def _cell_rgb(int c) -> LandColor:
    LandVoronoiNode *node = land_voronoi_node(voronoi, c)
    if node.b == 0: return land_color_rgba(0, 0, 1, 1)
    if node.b == 1: return land_color_rgba(0, 1, 0, 1)
    if node.b == 2: return land_color_rgba(1, 0, 0, 1)
    if node.b == 3: return land_color_rgba(1, .66, .33, 1)
    return land_color_rgba(.5, .5, .5, 1)

def _cell_rgb2(int c) -> LandColor:
    LandVoronoiNode *node = land_voronoi_node(voronoi, c)
    if node.b == 0: return land_color_rgba(1, 1, 1, 1)
    return land_color_rgba(0, 0, 0, 1)

class CBI:
    LandColor c
    float a
    LandColor (*cell_rgb)(int c)

"""

8   4   0   4   8
        |
        |
  A     |     B
        |

"""
def _cb_dist_raw_cb(int owner, neighbor, float distance, void *user):
    CBI *cbi = user
    float f = distance
    if use_distance > 0:
        f = 1 - distance / use_distance
    LandColor rgb = cbi.cell_rgb(owner)
    cbi.c.r += rgb.r * f
    cbi.c.g += rgb.g * f
    cbi.c.b += rgb.b * f
    cbi.a += f
    
def _cb_dist_raw(int x, y, unsigned char *rgba, void *user):
    CBI cbi
    cbi.c = land_color_rgba(0, 0, 0, 1)
    cbi.a = 0
    cbi.cell_rgb = _cell_rgb
    land_voronoi_cell_callback_at(voronoi, None, x, y, use_distance,
            _cb_dist_raw_cb, &cbi)
    if cbi.a > 0:
        cbi.c.r /= cbi.a
        cbi.c.g /= cbi.a
        cbi.c.b /= cbi.a
    land_color_copy_to_bytes(cbi.c, rgba)

def _cb_dist(int x, y, unsigned char *rgba, void *user):
    CBI cbi
    cbi.c = land_color_rgba(0, 0, 0, 1)
    cbi.a = 0
    cbi.cell_rgb = _cell_rgb2
    land_voronoi_cell_callback_at(voronoi, None, x, y, use_distance,
            _cb_dist_raw_cb, &cbi)
    if cbi.a > 0:
        cbi.c.r /= cbi.a
        cbi.c.g /= cbi.a
        cbi.c.b /= cbi.a
    land_color_copy_to_bytes(cbi.c, rgba)

def _cb_diff(int x, y, unsigned char *rgba, void *user):
    uint8_t n[16]
    _cb_dist(x + 1, y, n + 0, user)
    _cb_dist(x - 1, y, n + 4, user)
    rgba[0] = 127 + (n[0] - n[4]) * 8
    rgba[1] = 127 + (n[1] - n[5]) * 8
    rgba[2] = 127 + (n[2] - n[6]) * 8
    rgba[3] = 255

def _cb(int x, y, unsigned char *rgba, void *user):
    float d = land_voronoi_at(voronoi, x, y)
    d = (d + 1) / 2
    int o = land_voronoi_owner(voronoi, x, y)
    if o == -1:
        land_color_copy_to_bytes(land_color_rgba(0, 0, 0, 1), rgba)
        return
    LandColor co = _cell_rgb(o)
    co.r *= d
    co.g *= d
    co.b *= d
    land_color_copy_to_bytes(co, rgba)

def _init:
    gen(new=True, only_dist=False)

def gen(bool new, bool only_dist):
    int w = use_w
    int h = use_h
    if not image:
        image = land_image_new(w, h)
    if new:
        seed = land_get_seconds() + land_rand(0, 10000)
        if fixed_seed:
            seed = fixed_seed
            fixed_seed = 0
    print("seed: 0x%lx", seed)
    LandRandom *random = land_random_new(seed)

    if not only_dist:
        if voronoi:
            land_voronoi_destroy(voronoi)
        print("count: %d w: %d h: %d wrap: %d", use_count, w, h, use_wrap)
        voronoi = land_voronoi_new(random, w, h, use_count, use_wrap, use_clip_border)
        land_voronoi_recalculate_map(voronoi, use_passes == 0)
        for int i in range(use_passes):
            land_voronoi_centroid(voronoi, i == use_passes - 1)
        for int i in range(voronoi.n):
            auto node = land_voronoi_node(voronoi, i)
            node.b = land_random(random, 0, 4)
        for int i in range(voronoi.n, voronoi.n + voronoi.en):
            auto node = land_voronoi_node(voronoi, i)
            auto real = land_voronoi_node(voronoi, node.id)
            node.b = real.b
        land_random_del(random)

    land_voronoi_set_overlap(voronoi, use_distance)
    if use_edge_display == 0:
        land_image_write_callback(image, _cb, None)
    elif use_edge_display == 1:
        land_image_write_callback(image, _cb_dist_raw, None)
    elif use_edge_display == 2:
        land_image_write_callback(image, _cb_dist, None)
    else:
        land_image_write_callback(image, _cb_diff, None)

# def _check_edge(LandVoronoi *self, int cell, neighbor,
        # float px, py, cx, cy, x, y, distance,
        # float *mind, int *mini):
    # LandVoronoiNode *node = land_voronoi_node(self, cell)
    # LandVoronoiNode *node2 = land_voronoi_node(self, neighbor)
    
    # LandFloat pd = land_point_segment_distance(x, y, px, py, cx, cy)
    # #print("%.1f/%.1f to %d (%.1f/%.1f/%.1f/%.1f): %.1f", x, y, neighbor, px, py, cx, cy, pd)
    # if node.b == node2.b: pd = distance
    # if pd < *mind:
        # *mind = pd
        # *mini = neighbor

# def _find_edge(int x, y, cell):
    # LandVoronoiNode *node = land_voronoi_node(voronoi, cell)
    # int pn = node.neighbors_count
    # int mini = -1
    # float d = 100
    # voronoi.max_distance = 100
    # for int i in range(pn):
        # int j = (i + 1) % pn
        # float x1 = node.edges[i * 2 + 0]
        # float y1 = node.edges[i * 2 + 1]
        # float x2 = node.edges[j * 2 + 0]
        # float y2 = node.edges[j * 2 + 1]
        # int neighbor = node.neighbors[j]

        # _check_edge(voronoi, cell, neighbor, x1, y1, x2, y2, x, y,
            # 100, &d, &mini)
    # if use_wrap:
        # print("cell %d[%d] (%d): edge to %d: %d/%d %.1f", node.id, cell, node.b, mini, x, y, d)
    # else:
        # print("cell %d (%d): edge to %d: %d/%d %.1f", cell, node.b, mini, x, y, d)

def _select_cb(int owner, neighbor, float distance, void *_):
    print("edge %d->%d: %.1f", owner, neighbor, distance)

def _tick:
    float dh = land_display_height()
    float zoom = dh * 0.8 / use_h
    int ox = (land_display_width() - voronoi.w * zoom) / 2
    int oy = (land_display_height() - voronoi.h * zoom) / 2

    if land_key(LandKeyEscape) or land_closebutton():
        land_quit()
    if land_key_pressed('s'): gen(True, False)
    if land_key_pressed('h'): land_voronoi_self_check(voronoi)
    if land_key_pressed('d'):
        if use_distance == 0: use_distance = 1
        elif use_distance == 1: use_distance = 5
        elif use_distance == 5: use_distance = 10
        elif use_distance == 10: use_distance = 50
        else: use_distance = 0
        gen(False, True)
    if land_key_pressed('w'): use_wrap = not use_wrap; gen(False, False)
    if land_key_pressed('f'): use_edge_display = (use_edge_display + 1) % 4; gen(False, True)
    if land_shift_pressed('C'): use_count += 1; gen(False, False)
    if land_shift_pressed('c'): use_count -= 1; gen(False, False)
    if land_key_pressed('i'): print_all()
    if land_shift_pressed('P'):
        use_passes += 1
        gen(False, False)
    if land_shift_pressed('p'):
        use_passes -= 1
        if use_passes < 0: use_passes = 0
        gen(False, False)
    if land_shift_pressed('l'): use_clip_border--; gen(False, False)
    if land_shift_pressed('L'): use_clip_border++; gen(False, False)
    if land_key_pressed(LandKeyF1): show_delaunay = not show_delaunay
    if land_key_pressed(LandKeyF2): show_voronoi = not show_voronoi
    if land_key_pressed(LandKeyF3): show_numbers = not show_numbers

    if land_mouse_button_clicked(0):
        int prev = selected
        int mx = (land_mouse_x() - ox) / zoom
        int my = (land_mouse_y() - oy) / zoom
        selected = land_voronoi_owner(voronoi, mx, my)
        print("selected %d at %d/%d", selected, mx, my)
        if selected != -1:
            LandVoronoiNode *node = land_voronoi_node(voronoi, selected)
            printf("all %d edges:", node.neighbors_count)
            for int i in range(node.neighbors_count):
                printf(" %d", node.neighbors[i])
            print("")
            print("within %.1f:", use_distance)
            #voronoi.debug = True
            land_voronoi_cell_callback_at(voronoi, None, mx, my, 30,
                _select_cb, None)
            #voronoi.debug = False
        if selected == prev:
            selected = -1

float global_zoom = 1

def _edge(float x1, y1, x2, y2, int cell):
    float z = global_zoom
    for int i in range(-1, 2):
        for int j in range(-1, 2):
            if not use_wrap:
                if i != 0 or j != 0:
                    continue
            float x1_ = x1 + i * voronoi.w * z
            float y1_ = y1 + j * voronoi.h * z
            float x2_ = x2 + i * voronoi.w * z
            float y2_ = y2 + j * voronoi.h * z
            land_color(1, 1, 0, 1)
            land_line(x1_, y1_, x2_, y2_)
            land_text_pos((x1_ + x2_) / 2, (y1_ + y2_) / 2)
            land_text_background(land_color_premul(0, 0, 1, 0.5), 4)
            land_print_middle("%d", cell)
            land_text_background_off()

def _delaunay_cb(int a, int b, int c, void *_):
    float z = global_zoom
    auto va = land_voronoi_node(voronoi, a)
    auto vb = land_voronoi_node(voronoi, b)
    auto vc = land_voronoi_node(voronoi, c)
    land_line(va.x * z, va.y * z, vb.x * z, vb.y * z)
    land_line(vb.x * z, vb.y * z, vc.x * z, vc.y * z)
    land_line(vc.x * z, vc.y * z, va.x * z, va.y * z)

def _draw:
    float dh = land_display_height()
    float zoom = dh * 0.8 / use_h
    float z = zoom
    global_zoom = zoom
    land_reset_transform()
    land_clear(0, 0, 0, 1)
    int ox = (land_display_width() - voronoi.w * zoom) / 2
    int oy = (land_display_height() - voronoi.h * zoom) / 2
    land_translate(ox, oy)
    land_image_draw_scaled(image, 0, 0, zoom, zoom)

    for int i in range(voronoi.n + voronoi.en):
        auto xy = land_voronoi_node(voronoi, i)
        if show_numbers:
            land_text_pos(xy.x * zoom, xy.y * zoom)
            land_color(1, 1, 0, 1)
            land_text_background(land_color_premul(0, 0, 1, .5), 8)
            land_print_middle("%d (%d)", i, xy.b)
        if show_voronoi:
            land_premul(1, .5, 0, .5)
            int nc = xy.neighbors_count
            if nc > 0:
                land_move_to(xy.edges[nc * 2 - 2] * z, xy.edges[nc * 2 - 1] * z)
            for int j in range(nc):
                land_line_to(xy.edges[j * 2 + 0] * z, xy.edges[j * 2 + 1] * z)

    land_premul(0, 1, 0, 0.33)
    if show_delaunay:
        Delaunator *d = voronoi.d
        for_each_triangle(d, _delaunay_cb, None)

    if selected != -1:
        auto node = land_voronoi_node(voronoi, selected)
        int ni0 = 0
        float x0 = 0, y0 = 0, px = 0, py = 0
        for int i in range(node.neighbors_count):
            int ni = node.neighbors[i]
            float x = node.edges[i * 2 + 0] * zoom
            float y = node.edges[i * 2 + 1] * zoom
            if i == 0:
                x0 = x
                y0 = y
                ni0 = ni
            else:
                _edge(px, py, x, y, ni)
            px = x
            py = y
        _edge(px, py, x0, y0, ni0)

def print_all:
    print("coordinates")
    printf("[")
    for int i in range(voronoi.n + voronoi.en):
        auto xy = land_voronoi_node(voronoi, i)
        printf("[%d, %d], ", xy.x, -xy.y)
    print("]")
    for int i in range(voronoi.n + voronoi.en):
        auto xy = land_voronoi_node(voronoi, i)
        for int j in range(xy.neighbors_count):
            float x = xy.edges[j * 2 + 0]
            float y = xy.edges[j * 2 + 1]
            print("%10f, %10f", x, y)
    for int i in range(voronoi.n + voronoi.en):
        auto xy = land_voronoi_node(voronoi, i)
        if i == voronoi.n: print("--")
        printf("%d: neighbors=", i)
        for int e in range(xy.neighbors_count):
            if e > 0: printf(",")
            printf("%d", xy.neighbors[e])
        print("")

def begin():
    land_init()
    land_set_display_percentage_aspect(0.5, 4.0 / 3, LAND_WINDOWED | LAND_OPENGL | LAND_RESIZE)
    land_callbacks(_init, _tick, _draw, None)
    land_mainloop()

land_use_main(begin)
