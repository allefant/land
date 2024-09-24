import global land/land

LandImage *c
int start_tick
bool need_cover

def _init:
    (int w, h) = land_display_size()
    c = land_image_new(w, h)
    start_tick = land_get_ticks()
    need_cover = True

def _redraw_cover:
    land_set_image_display(c)
    (int w, h) = land_display_size()
    land_clear(0, 0, 0, 1)
    auto r = land_ribbon_new_empty(subdiv=8)
    land_ribbon_add(r, 0, h / 2)
    land_ribbon_add(r, w, h / 2)
    land_ribbon_width(r, h / 2)
    land_ribbon_twocolor(r, land_color_name("citron"), land_color_name("midnightblue"))
    land_ribbon_draw(r)
    land_ribbon_destroy(r)
    land_unset_image_display()

def _tick:
    if land_key(LandKeyEscape):
        land_quit()
    if land_closebutton():
        land_quit()

def _draw:
    land_clear(1, 1, 1, 1)
    land_scale_to_fit(800, 450, 0)

    if need_cover:
        need_cover = False
        _redraw_cover()

    auto r = land_ribbon_new_empty(subdiv=8)
    land_ribbon_add(r, 0, 225)
    land_ribbon_add(r, 800, 225)
    land_ribbon_width(r, 225)
    land_ribbon_twocolor(r, land_color_name("purple"), land_color_name("banana"))
    land_ribbon_draw(r)
    land_ribbon_destroy(r)

    float p = (land_get_ticks() - start_tick) / 300.0
    if p > 1.25:
        p = 0
        start_tick = land_get_ticks()
        need_cover = True
    land_spiral_reveal(c, 30, 30, p)
    land_image_draw_into(c, 0, 0, 800, 450)

def _config(): land_default_display()
land_example(_config, _init, _tick, _draw, None)
