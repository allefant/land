import global land/land

int t

def _tick:
    if land_key(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

    if land_key_pressed(LandKeyLeft): t--
    if land_key_pressed(LandKeyRight): t++
    

def _draw:
    land_clear(0, 0, 0, 1)
    land_scale_to_fit(640, 480, 0)

    if t == 0: _test1()
    if t == 1: _test2()
    if t == 2: _test3()
    if t == 3: _test4(loop=False)
    if t == 4: _test4(loop=True)
    if t == 5: _test5()
    if t == 6: _test6(min_segment=0)
    if t == 7: _test6(min_segment=25)
    t = land_mod(t, 8)

def _test1:
    float xy[] = {80, 80, 160, 160, 160, 80}
    land_color_set_named("orange")
    land_filled_ribbon(3, xy)

    float xy2[] = {80, 80, 160, 160, 160, 80}
    for int i in range(3): xy2[i * 2 + 1] += 240
    auto r = land_ribbon_new(3, subdiv=8, xy2)
    land_ribbon_color_names(r, "citron,cadetblue,citron")
    r.loop = True
    r.filled = True
    land_ribbon_draw(r)
    land_ribbon_destroy(r)

    float xy3[] = {80, 80, 160, 160, 160, 80, 200, 80, 200, 200, 120, 200}
    for int i in range(6): xy3[i * 2 + 0] += 320
    r = land_ribbon_new(6, subdiv=8, xy3)
    land_ribbon_color_names(r, "chocolate, banana, chocolate")
    r.loop = True
    r.filled = True
    land_ribbon_draw(r)
    land_ribbon_destroy(r)

def _test2:
    for int i in range(4):
        float xy[] = {80, 80, 160, 80, 160, 160}
        if i == 1 or i == 2:
            xy[0] += 320
            xy[2] += 320
            xy[4] += 320
        if i == 2 or i == 3:
            xy[1] += 240
            xy[3] += 240
            xy[5] += 240
        auto r = land_ribbon_new(3, subdiv=8, xy)
        if i == 0:
            land_ribbon_color_names(r, "orchid, gold")
        else:
            r.loop = True
            land_ribbon_color_names(r, "orchid, gold, orchid")
        if i == 0 or i == 1:
            land_ribbon_thickness(r, 3, (float[]){5, 20, 5}, None)
        elif i == 2:
            land_ribbon_thickness(r, 4, (float[]){5, 20, 5, 5}, None)
        else:
            land_ribbon_thickness(r, 4, (float[]){5, 20, 5, 20}, None)
        land_ribbon_draw(r)
        _ribbon_debug(r)
        land_ribbon_destroy(r)

def _test3:
    for int i in range(9):
        float xy[] = {160, 50 + 40 * i, 480, 50 + 40 * i}
        auto r = land_ribbon_new(2, subdiv=2 + i, xy)
        land_ribbon_color(r, land_color_name("darkgoldenrod"))
        land_ribbon_width(r, 10)
        land_ribbon_draw(r)
        _ribbon_debug(r)
        land_ribbon_destroy(r)

def _test4(bool loop):
    float xy[] = {120, 80, 560, 80, 560, 400, 80, 400, 320, 240, 160, 400, 300, 220}
    float rgba[] = {
        0, 0, .5, .5,
        .5, 0, .5, .5,
        0.5, 0, 0, .5}
    float a = (1 + cos(land_get_time() * pi / 2)) / 2
    float pos[] = {
        0,
        a,
        1
        }
    LandRibbon *r = land_ribbon_new(7, subdiv=8, xy)
    r.loop = loop
    land_ribbon_gradient(r, 3, rgba, pos)
    float w_[] = {10, 10, 20, 10, 10}
    float p_[] = {0, a - 0.1, a, a + 0.1, 1}
    land_ribbon_thickness(r, 4, w_, p_)
    land_ribbon_draw(r)

    float x1, y1, x2, y2
    land_ribbon_get_pos(r, a, &x1, &y1)
    land_ribbon_get_pos(r, a + 0.05, &x2, &y2)
    float w = land_ribbon_get_width(r, a)
    float nx, ny
    land_orthonormal2d(x2 - x1, y2 - y1, &nx, &ny)
    land_color(1, 1, 0, 1)
    land_thickness(0)
    land_line(x1 + nx * w, y1 + ny * w, x2 + nx * w, y2 + ny * w)

    _ribbon_debug(r)
    
    land_ribbon_destroy(r)

    # int b = 160
    # float xy2[] = {b, b, 640 - b, b, 640 - b, 480 - b, b, 480 - b, b, b}
    # float rgba2[] = {
        # 0, 0, 0, 0,
        # 0, 0, 0, 0,
        # .8, .7, 0, 1,
        # 0, 0, 0, 0,
        # 0, 0, 0, 0}
    # float pos2[] = {
        # 0,
        # (1 + cos(land_get_time() * pi)) / 2 * 0.8,
        # (1 + cos(land_get_time() * pi)) / 2 * 0.8 + 0.1,
        # (1 + cos(land_get_time() * pi)) / 2 * 0.8 + 0.2,
        # 1
        # }
    # land_thickness(20)
    # land_colored_ribbon(5, subdiv=8, xy2, 5, rgba2, pos2)

def _test5:
    float xy[] = {120, 80, 560, 80, 560, 400, 80, 400, 320, 240, 160, 400, 300, 220}
    float rgba[] = {
        1, 1, 1, 1,
        1, 1, 1, 1,
        0, 0, 0, 0,
        0, 0, 0, 0}
    float a = (1 + cos(land_get_time() * pi / 2)) / 2
    float pos[] = {
        0,
        a,
        a + 0.01,
        1
        }
    LandRibbon *r = land_ribbon_new(7, subdiv=16, xy)
    land_ribbon_gradient(r, 4, rgba, pos)
    land_ribbon_draw(r)

    land_ribbon_destroy(r)

def _set(float *xy, int i, float x, y):
    xy[i * 2 + 0] = x
    xy[i * 2 + 1] = y

def _test6(float min_segment):
    float *xy = land_calloc(40 * 2 * sizeof(float))
    int x0 = 320
    int y0 = 240
    for int i in range(0, 40):
        float a = 2 * pi * i / 8
        float r = 25 + i * 50 / 8
        float x = x0 + cos(a) * r
        float y = y0 + sin(a) * r
        _set(xy, i, x, y)

    LandRibbon *r = land_ribbon_new(40, subdiv=16, xy)
    r.min_segment_distance = min_segment
    float rgba[] = {
        1, 1, 1, 1,
        1, 1, 1, 1,
        0, 0, 0, 0,
        0, 0, 0, 0}
    float a = (1 + cos(land_get_time() * pi / 2)) / 2
    float pos[] = {
        0,
        a,
        a + 0.01,
        1
        }
    land_ribbon_gradient(r, 4, rgba, pos)
    land_ribbon_draw(r)
    _ribbon_debug(r)
    land_ribbon_destroy(r)

def _ribbon_debug(LandRibbon *r):
    land_thickness(0)

    for int i in range(r.n):
        float x = r.xy[i * 2 + 0]
        float y = r.xy[i * 2 + 1]
        land_color(1, 0, 0, 1)
        land_circle_around(x, y, 5)

    for int i in range(r.segments + 1):
        float x, y, nx, ny
        land_ribbon_get_subdivision_pos(r, i, &x, &y)
        land_ribbon_get_subdivision_normal(r, i, &nx, &ny)
        land_color(1, 1, 0, 1)
        land_line(x, y, x + nx * 10, y + ny * 10)

def _config(): land_default_display()
land_example(_config, None, _tick, _draw, None)
