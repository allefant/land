import global land/land

LandImage *image
LandVoronoi *voronoi
bool use_dist
bool use_wrap = True
int selected
LandRandom *seed

def _cb(int x, y, unsigned char *rgba, void *user):
    float d = land_voronoi_at(voronoi, x, y)
    int o = land_voronoi_owner(voronoi, x, y)
    d = (d + 1) / 2
    LandColor rgb = land_color_rgba(d, 0, 0, 1)
    if o == 0: rgb = land_color_rgba(0, 0, d, 1)
    if o == 1 or o == 2 or o == 3: rgb = land_color_rgba(d, 0, d, 1)
    land_color_copy_to_bytes(rgb, rgba)

def _init:
    gen()
    apply()

def gen():
    int w = land_display_width()
    int h = land_display_height()
    image = land_image_new(w, h)
    uint64_t t = land_get_seconds()
    seed = land_random_new(t)
    print("seed: %lx", t)
    recreate()

def recreate:
    int w = land_display_width()
    int h = land_display_height()
    if voronoi:
        land_voronoi_destroy(voronoi)
    voronoi = land_voronoi_create(seed, w, h, 20, use_wrap, 0, 0, 0)
    land_voronoi_node(voronoi, 1)->b = 0
    land_voronoi_node(voronoi, 2)->b = 0
    land_voronoi_node(voronoi, 3)->b = 0

def apply:
    if use_dist:
        land_voronoi_set_distance(voronoi, 20)
    else:
        land_voronoi_set_distance(voronoi, 0)

    land_image_write_callback(image, _cb, None)

def _check_edge(LandVoronoi *self, int cell, neighbor,
        float px, py, cx, cy, x, y, distance,
        float *mind, int *mini):
    LandVoronoiNode *node = land_voronoi_node(self, cell)
    LandVoronoiNode *node2 = land_voronoi_node(self, neighbor)
    
    LandFloat pd = land_point_segment_distance(x, y, px, py, cx, cy)
    print("%.1f/%.1f to %d (%.1f/%.1f/%.1f/%.1f): %.1f", x, y, neighbor, px, py, cx, cy, pd)
    if node.b == node2.b: pd = distance
    if pd < *mind:
        *mind = pd
        *mini = neighbor

def _find_edge(int x, y, cell):
    LandVoronoiNode *node = land_voronoi_node(voronoi, cell)
    int pn = node.neighbors_count
    int mini = -1
    float d = 100
    voronoi.max_distance = 100
    for int i in range(pn):
        int j = (i + 1) % pn
        float x1 = node.edges[i * 2 + 0]
        float y1 = node.edges[i * 2 + 1]
        float x2 = node.edges[j * 2 + 0]
        float y2 = node.edges[j * 2 + 1]
        int neighbor = node.neighbors[j]

        _check_edge(voronoi, cell, neighbor, x1, y1, x2, y2, x, y,
            100, &d, &mini)
    print("cell %d: edge to %d: %d/%d %.1f", cell, mini, x, y, d)

def _tick:
    if land_key(LandKeyEscape):
        land_quit()
    if land_key_pressed('s'):
        gen()
        apply()
    if land_key_pressed('d'):
        use_dist = not use_dist
        apply()
    if land_key_pressed('w'):
        use_wrap = not use_wrap
        recreate()
        apply()

    if land_mouse_button_clicked(0):
        int prev = selected
        selected = land_voronoi_owner(voronoi, land_mouse_x(), land_mouse_y())
        print("%d/%d -> %d", land_mouse_x(), land_mouse_y(), selected)
        _find_edge(land_mouse_x(), land_mouse_y(), selected)
        if selected == prev:
            selected = -1

def _edge(float x1, y1, x2, y2, int cell):
    for int i in range(-1, 2):
        for int j in range(-1, 2):
            float x1_ = x1 + i * land_display_width()
            float y1_ = y1 + j * land_display_height()
            float x2_ = x2 + i * land_display_width()
            float y2_ = y2 + j * land_display_height()
            land_color(1, 1, 0, 1)
            land_line(x1_, y1_, x2_, y2_)
            land_text_pos((x1_ + x2_) / 2, (y1_ + y2_) / 2)
            land_text_background(land_color_premul(0, 0, 1, 0.5), 4)
            land_print_middle("%d", cell)
            land_text_background_off()

def _draw:
    land_clear(0, 0, 0, 1)
    land_image_draw(image, 0, 0)

    for int i in range(voronoi.n):
        auto xy = land_voronoi_node(voronoi, i)
        land_text_pos(xy.x, xy.y)
        land_color(1, 1, 0, 1)
        land_text_background(land_color_premul(0, 0, 1, .5), 8)
        land_print_middle("%d (%d)", i, xy.b)

    if selected != -1:
        auto node = land_voronoi_node(voronoi, selected)
        int ni0 = 0
        float x0 = 0, y0 = 0, px = 0, py = 0
        for int i in range(node.neighbors_count):
            int ni = node.neighbors[i]
            float x = node.edges[i * 2 + 0]
            float y = node.edges[i * 2 + 1]
            if i == 0:
                x0 = x
                y0 = y
                ni0 = ni
            else:
                _edge(px, py, x, y, ni)
            px = x
            py = y
        _edge(px, py, x0, y0, ni0)

def begin():
    land_init()
    land_set_display_percentage_aspect(0.5, 4.0 / 3, LAND_WINDOWED | LAND_OPENGL | LAND_RESIZE)
    land_callbacks(_init, _tick, _draw, None)
    land_mainloop()

land_use_main(begin)
